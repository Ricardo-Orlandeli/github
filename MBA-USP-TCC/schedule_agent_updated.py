import json
import os
from datetime import datetime
from rag_system_pmbok import PMBOKRAGSystem

class ScheduleAgent:
    """
    Agente especializado em monitorar e controlar o cronograma do projeto.
    
    Este agente analisa o status do cronograma, calcula o SPI (Índice de Desempenho de Cronograma)
    e recomenda ações corretivas em caso de desvios.
    """
    
    def __init__(self, llm_interface=None):
        """
        Inicializa o agente de cronograma.
        
        Args:
            llm_interface: Interface para comunicação com o LLM
        """
        self.llm_interface = llm_interface
        self.rag_system = PMBOKRAGSystem(domain="cronograma")
        
    def analyze_schedule_file(self, file_path):
        """
        Analisa um arquivo de status de cronograma.
        
        Args:
            file_path: Caminho para o arquivo de status
            
        Returns:
            Dicionário com os resultados da análise
        """
        # Verificar se o arquivo existe
        if not os.path.exists(file_path):
            return {
                "error": f"Arquivo não encontrado: {file_path}",
                "status": "error"
            }
        
        # Ler o arquivo de status
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extrair informações relevantes
        project_info = self._extract_project_info(content)
        schedule_status = self._extract_schedule_status(content)
        
        # Calcular ou extrair SPI
        spi = schedule_status.get('spi', None)
        if spi is None and 'valor_agregado' in schedule_status and 'valor_planejado' in schedule_status:
            ev = schedule_status.get('valor_agregado', 0)
            pv = schedule_status.get('valor_planejado', 0)
            if pv > 0:
                spi = ev / pv
                schedule_status['spi'] = spi
        
        # Determinar status do cronograma com base no SPI
        schedule_health = self._evaluate_schedule_health(spi)
        
        # Gerar recomendações
        recommendations = self._generate_recommendations(schedule_status, project_info)
        
        # Compilar resultados
        results = {
            "project_info": project_info,
            "schedule_status": schedule_status,
            "schedule_health": schedule_health,
            "recommendations": recommendations,
            "analysis_date": datetime.now().isoformat(),
            "status": "success"
        }
        
        return results
    
    def _extract_project_info(self, content):
        """
        Extrai informações gerais do projeto do conteúdo do arquivo.
        
        Args:
            content: Conteúdo do arquivo de status
            
        Returns:
            Dicionário com informações do projeto
        """
        lines = content.split('\n')
        project_info = {}
        
        # Extrair informações básicas
        for line in lines[:10]:  # Verificar apenas as primeiras linhas
            if "Projeto:" in line:
                parts = line.split("Projeto:")[1].strip().split("(")
                if len(parts) > 1:
                    project_info["nome"] = parts[0].strip()
                    project_info["id"] = parts[1].replace(")", "").strip()
                else:
                    project_info["nome"] = parts[0].strip()
            elif "Data:" in line:
                project_info["data_relatorio"] = line.split("Data:")[1].strip()
            elif "Gerente:" in line:
                project_info["gerente"] = line.split("Gerente:")[1].strip()
        
        return project_info
    
    def _extract_schedule_status(self, content):
        """
        Extrai informações de status do cronograma do conteúdo do arquivo.
        
        Args:
            content: Conteúdo do arquivo de status
            
        Returns:
            Dicionário com status do cronograma
        """
        lines = content.split('\n')
        schedule_status = {}
        
        # Extrair informações de status
        for i, line in enumerate(lines):
            if "Status atual:" in line:
                schedule_status["status"] = line.split("Status atual:")[1].strip()
            elif "Percentual de conclusão:" in line:
                try:
                    percentual = line.split("Percentual de conclusão:")[1].strip()
                    schedule_status["percentual_conclusao"] = float(percentual.replace("%", ""))
                except:
                    pass
            elif "Data de início:" in line:
                schedule_status["data_inicio"] = line.split("Data de início:")[1].strip()
            elif "Data de término planejada:" in line:
                schedule_status["data_termino_planejada"] = line.split("Data de término planejada:")[1].strip()
            elif "Data de término real/prevista:" in line:
                schedule_status["data_termino_real"] = line.split("Data de término real/prevista:")[1].strip()
            elif "Atraso atual:" in line:
                try:
                    atraso = line.split("Atraso atual:")[1].strip()
                    schedule_status["atraso_dias"] = int(atraso.split(" dias")[0])
                except:
                    pass
            elif "Motivo do atraso:" in line:
                schedule_status["motivo_atraso"] = line.split("Motivo do atraso:")[1].strip()
            elif "Índice de Desempenho de Cronograma (SPI):" in line:
                try:
                    spi = line.split("Índice de Desempenho de Cronograma (SPI):")[1].strip()
                    schedule_status["spi"] = float(spi)
                except:
                    pass
            elif "Valor Planejado (PV):" in line:
                try:
                    pv = line.split("Valor Planejado (PV):")[1].strip()
                    schedule_status["valor_planejado"] = float(pv.replace("R$", "").strip())
                except:
                    pass
            elif "Valor Agregado (EV):" in line:
                try:
                    ev = line.split("Valor Agregado (EV):")[1].strip()
                    schedule_status["valor_agregado"] = float(ev.replace("R$", "").strip())
                except:
                    pass
        
        # Extrair tarefas críticas e atrasadas
        tarefas_criticas = []
        tarefas_atrasadas = []
        
        in_critical_section = False
        in_delayed_section = False
        
        for line in lines:
            if "Tarefas críticas:" in line:
                in_critical_section = True
                in_delayed_section = False
                continue
            elif "Tarefas atrasadas:" in line:
                in_critical_section = False
                in_delayed_section = True
                continue
            elif line.strip() == "" or line.startswith("RELATÓRIO"):
                in_critical_section = False
                in_delayed_section = False
                continue
            
            if in_critical_section and line.strip().startswith("-"):
                tarefas_criticas.append(line.strip()[2:].strip())
            elif in_delayed_section and line.strip().startswith("-"):
                tarefas_atrasadas.append(line.strip()[2:].strip())
        
        schedule_status["tarefas_criticas"] = tarefas_criticas
        schedule_status["tarefas_atrasadas"] = tarefas_atrasadas
        
        return schedule_status
    
    def _evaluate_schedule_health(self, spi):
        """
        Avalia a saúde do cronograma com base no SPI.
        
        Args:
            spi: Índice de Desempenho de Cronograma
            
        Returns:
            Dicionário com avaliação da saúde do cronograma
        """
        if spi is None:
            return {
                "status": "unknown",
                "description": "Não foi possível determinar o status do cronograma devido à falta de informações."
            }
        
        if spi >= 1.05:
            return {
                "status": "excellent",
                "description": f"O projeto está significativamente adiantado (SPI = {spi:.2f}). Verifique se a qualidade está sendo mantida e considere realocar recursos."
            }
        elif spi >= 0.95:
            return {
                "status": "good",
                "description": f"O projeto está no cronograma ou levemente adiantado (SPI = {spi:.2f}). Continue monitorando."
            }
        elif spi >= 0.85:
            return {
                "status": "warning",
                "description": f"O projeto está levemente atrasado (SPI = {spi:.2f}). Ações preventivas são recomendadas."
            }
        elif spi >= 0.7:
            return {
                "status": "critical",
                "description": f"O projeto está significativamente atrasado (SPI = {spi:.2f}). Ações corretivas são necessárias."
            }
        else:
            return {
                "status": "severe",
                "description": f"O projeto está severamente atrasado (SPI = {spi:.2f}). Ações corretivas urgentes são necessárias."
            }
    
    def _generate_recommendations(self, schedule_status, project_info):
        """
        Gera recomendações com base no status do cronograma.
        
        Args:
            schedule_status: Status do cronograma
            project_info: Informações do projeto
            
        Returns:
            Lista de recomendações
        """
        # Extrair SPI
        spi = schedule_status.get('spi')
        
        # Recomendações padrão baseadas no SPI
        if spi is None:
            recommendations = [
                "Estabelecer métricas de valor agregado (EV) e valor planejado (PV) para calcular o SPI",
                "Implementar um sistema de monitoramento de cronograma mais detalhado",
                "Revisar o plano de gerenciamento do cronograma"
            ]
        elif spi < 0.7:
            recommendations = [
                "Realizar reunião de emergência com a equipe do projeto e stakeholders",
                "Revisar o caminho crítico e identificar oportunidades de fast-tracking",
                "Alocar recursos adicionais para as tarefas críticas",
                "Considerar a revisão da linha de base do cronograma",
                "Implementar monitoramento diário das tarefas críticas",
                "Avaliar a possibilidade de redução de escopo (com aprovação dos stakeholders)"
            ]
        elif spi < 0.85:
            recommendations = [
                "Revisar o caminho crítico e identificar oportunidades de otimização",
                "Implementar horas extras para recuperar o atraso",
                "Monitorar de perto as tarefas críticas",
                "Revisar as dependências entre tarefas para otimização",
                "Comunicar o status aos stakeholders e discutir estratégias de recuperação"
            ]
        elif spi < 0.95:
            recommendations = [
                "Monitorar de perto as tarefas críticas",
                "Identificar potenciais riscos que possam causar mais atrasos",
                "Revisar a alocação de recursos para otimização",
                "Implementar reuniões de acompanhamento mais frequentes"
            ]
        elif spi < 1.05:
            recommendations = [
                "Manter o monitoramento regular do cronograma",
                "Continuar com as práticas atuais de gerenciamento",
                "Documentar lições aprendidas para projetos futuros"
            ]
        else:
            recommendations = [
                "Verificar se a qualidade está sendo mantida apesar do avanço rápido",
                "Considerar realocação de recursos para outros projetos prioritários",
                "Documentar as práticas bem-sucedidas para projetos futuros",
                "Revisar as estimativas para projetos futuros"
            ]
        
        # Adicionar recomendações específicas com base nas tarefas atrasadas
        if schedule_status.get('tarefas_atrasadas') and len(schedule_status['tarefas_atrasadas']) > 0:
            recommendations.append(f"Focar nas tarefas atrasadas: {', '.join(schedule_status['tarefas_atrasadas'])}")
        
        # Usar o RAG para enriquecer as recomendações com conhecimento do PMBOK
        if self.llm_interface and spi is not None:
            # Criar contexto para consulta
            context = f"""
            Projeto: {project_info.get('nome', 'Não especificado')}
            Status atual: {schedule_status.get('status', 'Não especificado')}
            SPI: {spi:.2f}
            Percentual de conclusão: {schedule_status.get('percentual_conclusao', 'Não especificado')}%
            Atraso: {schedule_status.get('atraso_dias', 'Não especificado')} dias
            Motivo do atraso: {schedule_status.get('motivo_atraso', 'Não especificado')}
            """
            
            # Aumentar o prompt com conhecimento do PMBOK
            augmented_prompt = self.rag_system.augment_prompt(
                query=context,
                template="""
                Com base nas melhores práticas do PMBOK para gerenciamento de cronograma, analise a seguinte situação:
                
                {query}
                
                Conhecimento relevante do PMBOK:
                {knowledge}
                
                Considerando as melhores práticas acima e o SPI de {spi:.2f}, forneça 3-5 recomendações específicas e acionáveis para melhorar o desempenho do cronograma:
                """
            )
            
            # Obter recomendações do LLM
            llm_response = self.llm_interface.generate_text(augmented_prompt)
            
            # Extrair recomendações da resposta do LLM
            llm_recommendations = self._extract_recommendations_from_llm(llm_response)
            
            # Adicionar recomendações do LLM
            if llm_recommendations:
                recommendations.extend(llm_recommendations)
        
        return recommendations
    
    def _extract_recommendations_from_llm(self, llm_response):
        """
        Extrai recomendações da resposta do LLM.
        
        Args:
            llm_response: Resposta do LLM
            
        Returns:
            Lista de recomendações
        """
        # Implementação simples - extrair linhas que começam com números ou hífens
        recommendations = []
        for line in llm_response.split('\n'):
            line = line.strip()
            if (line.startswith('1.') or line.startswith('2.') or 
                line.startswith('3.') or line.startswith('4.') or 
                line.startswith('5.') or line.startswith('-')):
                # Remover o prefixo numérico ou hífen
                clean_line = line[2:].strip() if line[1] == '.' else line[1:].strip()
                recommendations.append(clean_line)
        
        return recommendations
    
    def generate_report(self, analysis_results):
        """
        Gera um relatório com base nos resultados da análise.
        
        Args:
            analysis_results: Resultados da análise
            
        Returns:
            Relatório formatado
        """
        if analysis_results.get('status') == 'error':
            return f"ERRO: {analysis_results.get('error')}"
        
        project_info = analysis_results.get('project_info', {})
        schedule_status = analysis_results.get('schedule_status', {})
        schedule_health = analysis_results.get('schedule_health', {})
        recommendations = analysis_results.get('recommendations', [])
        
        report = f"""
        RELATÓRIO DE ANÁLISE DE CRONOGRAMA
        
        Projeto: {project_info.get('nome', 'Não especificado')} ({project_info.get('id', 'Não especificado')})
        Data da análise: {datetime.now().strftime('%d/%m/%Y %H:%M')}
        
        RESUMO DO STATUS:
        Status atual: {schedule_status.get('status', 'Não especificado')}
        Percentual de conclusão: {schedule_status.get('percentual_conclusao', 'Não especificado')}%
        SPI (Índice de Desempenho de Cronograma): {schedule_status.get('spi', 'Não calculado'):.2f if schedule_status.get('spi') is not None else 'Não calculado'}
        
        AVALIAÇÃO DA SAÚDE DO CRONOGRAMA:
        Status: {schedule_health.get('status', 'Não avaliado')}
        {schedule_health.get('description', '')}
        
        RECOMENDAÇÕES:
        """
        
        for i, recommendation in enumerate(recommendations, 1):
            report += f"{i}. {recommendation}\n"
        
        report += f"""
        DETALHES ADICIONAIS:
        Data de início: {schedule_status.get('data_inicio', 'Não especificado')}
        Data de término planejada: {schedule_status.get('data_termino_planejada', 'Não especificado')}
        Data de término real/prevista: {schedule_status.get('data_termino_real', 'Não especificado')}
        Atraso atual: {schedule_status.get('atraso_dias', 'Não especificado')} dias
        Motivo do atraso: {schedule_status.get('motivo_atraso', 'Não especificado')}
        
        Tarefas críticas:
        """
        
        for tarefa in schedule_status.get('tarefas_criticas', []):
            report += f"- {tarefa}\n"
        
        report += "\nTarefas atrasadas:\n"
        
        for tarefa in schedule_status.get('tarefas_atrasadas', []):
            report += f"- {tarefa}\n"
        
        return report

# Exemplo de uso
if __name__ == "__main__":
    from llm_interface import LLMInterface
    
    # Inicializar interface LLM
    llm = LLMInterface()
    
    # Criar agente de cronograma
    agent = ScheduleAgent(llm_interface=llm)
    
    # Analisar arquivo de status
    results = agent.analyze_schedule_file("../status_files/PROJ-0001_cronograma.txt")
    
    # Gerar relatório
    report = agent.generate_report(results)
    
    print(report)
