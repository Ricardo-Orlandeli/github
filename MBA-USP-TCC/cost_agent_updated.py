import json
import os
from datetime import datetime
from rag_system_pmbok import PMBOKRAGSystem

class CostAgent:
    """
    Agente especializado em monitorar e controlar os custos do projeto.
    
    Este agente analisa o status dos custos, calcula o CPI (Índice de Desempenho de Custo)
    e recomenda ações corretivas em caso de desvios orçamentários.
    """
    
    def __init__(self, llm_interface=None):
        """
        Inicializa o agente de custos.
        
        Args:
            llm_interface: Interface para comunicação com o LLM
        """
        self.llm_interface = llm_interface
        self.rag_system = PMBOKRAGSystem(domain="custos")
        
    def analyze_cost_file(self, file_path):
        """
        Analisa um arquivo de status de custos.
        
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
        cost_status = self._extract_cost_status(content)
        
        # Calcular ou extrair CPI
        cpi = cost_status.get('cpi', None)
        if cpi is None and 'valor_agregado' in cost_status and 'custo_real' in cost_status:
            ev = cost_status.get('valor_agregado', 0)
            ac = cost_status.get('custo_real', 0)
            if ac > 0:
                cpi = ev / ac
                cost_status['cpi'] = cpi
        
        # Determinar status dos custos com base no CPI
        cost_health = self._evaluate_cost_health(cpi)
        
        # Gerar recomendações
        recommendations = self._generate_recommendations(cost_status, project_info)
        
        # Compilar resultados
        results = {
            "project_info": project_info,
            "cost_status": cost_status,
            "cost_health": cost_health,
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
    
    def _extract_cost_status(self, content):
        """
        Extrai informações de status dos custos do conteúdo do arquivo.
        
        Args:
            content: Conteúdo do arquivo de status
            
        Returns:
            Dicionário com status dos custos
        """
        lines = content.split('\n')
        cost_status = {}
        
        # Extrair informações de status
        for i, line in enumerate(lines):
            if "Orçamento inicial:" in line:
                try:
                    orcamento = line.split("Orçamento inicial:")[1].strip()
                    cost_status["orcamento_inicial"] = float(orcamento.replace("R$", "").strip())
                except:
                    pass
            elif "Custo real atual:" in line:
                try:
                    custo = line.split("Custo real atual:")[1].strip()
                    cost_status["custo_real"] = float(custo.replace("R$", "").strip())
                except:
                    pass
            elif "Desvio orçamentário:" in line:
                try:
                    desvio = line.split("Desvio orçamentário:")[1].strip()
                    cost_status["desvio_orcamento"] = float(desvio.replace("%", "").strip())
                except:
                    pass
            elif "Índice de Desempenho de Custo (CPI):" in line:
                try:
                    cpi = line.split("Índice de Desempenho de Custo (CPI):")[1].strip()
                    cost_status["cpi"] = float(cpi)
                except:
                    pass
            elif "Valor Agregado (EV):" in line:
                try:
                    ev = line.split("Valor Agregado (EV):")[1].strip()
                    cost_status["valor_agregado"] = float(ev.replace("R$", "").strip())
                except:
                    pass
            elif "Estimativa para conclusão:" in line:
                try:
                    etc = line.split("Estimativa para conclusão:")[1].strip()
                    cost_status["estimativa_conclusao"] = float(etc.replace("R$", "").strip())
                except:
                    pass
            elif "Estimativa no término (EAC):" in line:
                try:
                    eac = line.split("Estimativa no término (EAC):")[1].strip()
                    cost_status["estimativa_termino"] = float(eac.replace("R$", "").strip())
                except:
                    pass
            elif "Variação no término (VAC):" in line:
                try:
                    vac = line.split("Variação no término (VAC):")[1].strip()
                    cost_status["variacao_termino"] = float(vac.replace("R$", "").strip())
                except:
                    pass
        
        # Extrair categorias de custos
        categorias_custos = {}
        in_categories_section = False
        
        for line in lines:
            if "Detalhamento por categoria:" in line:
                in_categories_section = True
                continue
            elif line.strip() == "" or line.startswith("RELATÓRIO"):
                in_categories_section = False
                continue
            
            if in_categories_section and line.strip().startswith("-"):
                try:
                    parts = line.strip()[2:].split(":")
                    if len(parts) >= 2:
                        categoria = parts[0].strip()
                        valor_parts = parts[1].strip().split("(")
                        valor = float(valor_parts[0].replace("R$", "").strip())
                        
                        if len(valor_parts) > 1:
                            percentual = float(valor_parts[1].replace("%)", "").strip())
                            categorias_custos[categoria] = {"valor": valor, "percentual": percentual}
                        else:
                            categorias_custos[categoria] = {"valor": valor}
                except:
                    pass
        
        cost_status["categorias_custos"] = categorias_custos
        
        return cost_status
    
    def _evaluate_cost_health(self, cpi):
        """
        Avalia a saúde dos custos com base no CPI.
        
        Args:
            cpi: Índice de Desempenho de Custo
            
        Returns:
            Dicionário com avaliação da saúde dos custos
        """
        if cpi is None:
            return {
                "status": "unknown",
                "description": "Não foi possível determinar o status dos custos devido à falta de informações."
            }
        
        if cpi >= 1.1:
            return {
                "status": "excellent",
                "description": f"O projeto está significativamente abaixo do orçamento (CPI = {cpi:.2f}). Verifique se a qualidade está sendo mantida e considere realocar recursos."
            }
        elif cpi >= 1.0:
            return {
                "status": "good",
                "description": f"O projeto está dentro do orçamento ou levemente abaixo (CPI = {cpi:.2f}). Continue monitorando."
            }
        elif cpi >= 0.9:
            return {
                "status": "warning",
                "description": f"O projeto está levemente acima do orçamento (CPI = {cpi:.2f}). Ações preventivas são recomendadas."
            }
        elif cpi >= 0.8:
            return {
                "status": "critical",
                "description": f"O projeto está significativamente acima do orçamento (CPI = {cpi:.2f}). Ações corretivas são necessárias."
            }
        else:
            return {
                "status": "severe",
                "description": f"O projeto está severamente acima do orçamento (CPI = {cpi:.2f}). Ações corretivas urgentes são necessárias."
            }
    
    def _generate_recommendations(self, cost_status, project_info):
        """
        Gera recomendações com base no status dos custos.
        
        Args:
            cost_status: Status dos custos
            project_info: Informações do projeto
            
        Returns:
            Lista de recomendações
        """
        # Extrair CPI
        cpi = cost_status.get('cpi')
        
        # Recomendações padrão baseadas no CPI
        if cpi is None:
            recommendations = [
                "Estabelecer métricas de valor agregado (EV) e custo real (AC) para calcular o CPI",
                "Implementar um sistema de monitoramento de custos mais detalhado",
                "Revisar o plano de gerenciamento dos custos"
            ]
        elif cpi < 0.7:
            recommendations = [
                "Realizar reunião de emergência com a equipe do projeto e stakeholders",
                "Revisar todas as categorias de custo para identificar áreas de maior desvio",
                "Implementar controles mais rigorosos para aprovação de despesas",
                "Considerar a revisão do orçamento base",
                "Avaliar a possibilidade de redução de escopo (com aprovação dos stakeholders)",
                "Renegociar contratos com fornecedores"
            ]
        elif cpi < 0.8:
            recommendations = [
                "Revisar as categorias de custo com maior desvio",
                "Implementar medidas de economia sem impactar a qualidade",
                "Monitorar de perto todas as despesas futuras",
                "Revisar processos para identificar ineficiências",
                "Comunicar o status aos stakeholders e discutir estratégias de recuperação"
            ]
        elif cpi < 0.9:
            recommendations = [
                "Monitorar de perto as categorias de custo com maior desvio",
                "Identificar potenciais riscos que possam causar mais desvios",
                "Revisar a alocação de recursos para otimização",
                "Implementar reuniões de acompanhamento de custos mais frequentes"
            ]
        elif cpi < 1.0:
            recommendations = [
                "Manter o monitoramento regular dos custos",
                "Implementar pequenas medidas de economia",
                "Revisar estimativas para atividades futuras"
            ]
        elif cpi < 1.1:
            recommendations = [
                "Manter o monitoramento regular dos custos",
                "Continuar com as práticas atuais de gerenciamento",
                "Documentar lições aprendidas para projetos futuros"
            ]
        else:
            recommendations = [
                "Verificar se a qualidade está sendo mantida apesar dos custos reduzidos",
                "Considerar realocação de recursos para outros projetos prioritários",
                "Documentar as práticas bem-sucedidas para projetos futuros",
                "Revisar as estimativas para projetos futuros"
            ]
        
        # Adicionar recomendações específicas com base nas categorias de custo
        if cost_status.get('categorias_custos'):
            # Identificar categoria com maior desvio
            maior_categoria = None
            maior_valor = 0
            
            for categoria, info in cost_status['categorias_custos'].items():
                if info.get('valor', 0) > maior_valor:
                    maior_valor = info.get('valor', 0)
                    maior_categoria = categoria
            
            if maior_categoria and cpi < 0.9:
                recommendations.append(f"Focar na redução de custos na categoria: {maior_categoria}")
        
        # Usar o RAG para enriquecer as recomendações com conhecimento do PMBOK
        if self.llm_interface and cpi is not None:
            # Criar contexto para consulta
            context = f"""
            Projeto: {project_info.get('nome', 'Não especificado')}
            CPI: {cpi:.2f}
            Orçamento inicial: R$ {cost_status.get('orcamento_inicial', 'Não especificado')}
            Custo real atual: R$ {cost_status.get('custo_real', 'Não especificado')}
            Desvio orçamentário: {cost_status.get('desvio_orcamento', 'Não especificado')}%
            """
            
            # Aumentar o prompt com conhecimento do PMBOK
            augmented_prompt = self.rag_system.augment_prompt(
                query=context,
                template="""
                Com base nas melhores práticas do PMBOK para gerenciamento de custos, analise a seguinte situação:
                
                {query}
                
                Conhecimento relevante do PMBOK:
                {knowledge}
                
                Considerando as melhores práticas acima e o CPI de {cpi:.2f}, forneça 3-5 recomendações específicas e acionáveis para melhorar o desempenho dos custos:
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
        cost_status = analysis_results.get('cost_status', {})
        cost_health = analysis_results.get('cost_health', {})
        recommendations = analysis_results.get('recommendations', [])
        
        report = f"""
        RELATÓRIO DE ANÁLISE DE CUSTOS
        
        Projeto: {project_info.get('nome', 'Não especificado')} ({project_info.get('id', 'Não especificado')})
        Data da análise: {datetime.now().strftime('%d/%m/%Y %H:%M')}
        
        RESUMO DO STATUS:
        Orçamento inicial: R$ {cost_status.get('orcamento_inicial', 'Não especificado'):.2f if cost_status.get('orcamento_inicial') is not None else 'Não especificado'}
        Custo real atual: R$ {cost_status.get('custo_real', 'Não especificado'):.2f if cost_status.get('custo_real') is not None else 'Não especificado'}
        Desvio orçamentário: {cost_status.get('desvio_orcamento', 'Não especificado'):.2f if cost_status.get('desvio_orcamento') is not None else 'Não especificado'}%
        CPI (Índice de Desempenho de Custo): {cost_status.get('cpi', 'Não calculado'):.2f if cost_status.get('cpi') is not None else 'Não calculado'}
        
        AVALIAÇÃO DA SAÚDE DOS CUSTOS:
        Status: {cost_health.get('status', 'Não avaliado')}
        {cost_health.get('description', '')}
        
        RECOMENDAÇÕES:
        """
        
        for i, recommendation in enumerate(recommendations, 1):
            report += f"{i}. {recommendation}\n"
        
        report += f"""
        DETALHES ADICIONAIS:
        Valor Agregado (EV): R$ {cost_status.get('valor_agregado', 'Não especificado'):.2f if cost_status.get('valor_agregado') is not None else 'Não especificado'}
        Estimativa para conclusão: R$ {cost_status.get('estimativa_conclusao', 'Não especificado'):.2f if cost_status.get('estimativa_conclusao') is not None else 'Não especificado'}
        Estimativa no término (EAC): R$ {cost_status.get('estimativa_termino', 'Não especificado'):.2f if cost_status.get('estimativa_termino') is not None else 'Não especificado'}
        Variação no término (VAC): R$ {cost_status.get('variacao_termino', 'Não especificado'):.2f if cost_status.get('variacao_termino') is not None else 'Não especificado'}
        
        DETALHAMENTO POR CATEGORIA:
        """
        
        for categoria, info in cost_status.get('categorias_custos', {}).items():
            valor = info.get('valor', 0)
            percentual = info.get('percentual', 0)
            report += f"- {categoria}: R$ {valor:.2f} ({percentual:.1f}%)\n"
        
        return report

# Exemplo de uso
if __name__ == "__main__":
    from llm_interface import LLMInterface
    
    # Inicializar interface LLM
    llm = LLMInterface()
    
    # Criar agente de custos
    agent = CostAgent(llm_interface=llm)
    
    # Analisar arquivo de status
    results = agent.analyze_cost_file("../status_files/PROJ-0001_custos.txt")
    
    # Gerar relatório
    report = agent.generate_report(results)
    
    print(report)
