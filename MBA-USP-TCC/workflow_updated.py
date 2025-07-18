
from crewai import Agent, Task, Crew, Process
import os
import json
from datetime import datetime
from cost_agent_updated import CostAgent
from schedule_agent_updated import ScheduleAgent
from scope_agent_updated import ScopeAgent
from risk_agent_updated import RisksAgent

class ProjectManagementWorkflow:
    """
    Workflow para gerenciamento de projetos usando CrewAI.
    
    Este workflow coordena os agentes especializados em cronograma, custos, escopo e riscos
    para analisar arquivos de status de projetos e gerar recomendações.
    """
    
    def __init__(self, llm_api_key=None, process_type="sequential"):
        """
        Inicializa o workflow.
        
        Args:
            llm_api_key: Chave de API para o LLM (opcional)
            process_type: Tipo de processo (sequential ou hierarchical)
        """
        self.llm_api_key = llm_api_key
        self.process_type = process_type
        
        # Configurar diretórios
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.status_dir = os.path.join(self.base_dir, "..", "..", "dataset", "status_files")
        self.results_dir = os.path.join(self.base_dir, "..", "results")
        
        # Criar diretório de resultados se não existir
        os.makedirs(self.results_dir, exist_ok=True)
        
        # Inicializar agentes e tarefas
        self.agents = self._create_agents()
        self.tasks = self._create_tasks()
        
        # Criar crew
        self.crew = self._create_crew()
    
    def _create_agents(self):
        """
        Cria os agentes especializados.
        
        Returns:
            Dicionário com os agentes
        """
        # Instantiate RAG+LLM agents
        knowledge_base_path = os.path.join(self.base_dir, "..", "..", "knowledge_base")
        schedule_agent = ScheduleAgent(llm_interface=self.llm_api_key)
        cost_agent = CostAgent(llm_interface=self.llm_api_key)
        scope_agent = ScopeAgent(knowledge_base_path, self.llm_api_key)
        risk_agent = RisksAgent(knowledge_base_path, self.llm_api_key)
        return {
            "schedule": schedule_agent,
            "cost": cost_agent,
            "scope": scope_agent,
            "risk": risk_agent
        }
    
    def _create_tasks(self):
        """
        Cria as tarefas para os agentes.
        
        Returns:
            Dicionário com as tarefas
        """
        # Tasks now use the RAG+LLM agent methods
        schedule_task = Task(
            description="Análise do cronograma do projeto usando RAG+LLM.",
            agent=self.agents["schedule"],
            expected_output="Relatório detalhado do cronograma.",
            run=lambda: self.agents["schedule"].analyze_schedule_file(os.path.join(self.status_dir, "PROJ-0001_cronograma.txt"))
        )
        cost_task = Task(
            description="Análise de custos do projeto usando RAG+LLM.",
            agent=self.agents["cost"],
            expected_output="Relatório detalhado de custos.",
            run=lambda: self.agents["cost"].analyze_cost_file(os.path.join(self.status_dir, "PROJ-0001_custos.txt"))
        )
        scope_task = Task(
            description="Análise de escopo do projeto usando RAG+LLM.",
            agent=self.agents["scope"],
            expected_output="Relatório detalhado de escopo.",
            run=lambda: self.agents["scope"].analyze_scope(os.path.join(self.status_dir, "PROJ-0001_escopo.txt"))
        )
        risk_task = Task(
            description="Análise de riscos do projeto usando RAG+LLM.",
            agent=self.agents["risk"],
            expected_output="Relatório detalhado de riscos.",
            run=lambda: self.agents["risk"].analyze_risks(os.path.join(self.status_dir, "PROJ-0001_riscos.txt"))
        )
        return {
            "schedule": schedule_task,
            "cost": cost_task,
            "scope": scope_task,
            "risk": risk_task
        }
    
    def _create_crew(self):
        """
        Cria a crew com os agentes e tarefas.
        
        Returns:
            Objeto Crew
        """
        if self.process_type == "hierarchical":
            # Modo hierárquico - o gerente de projeto coordena os especialistas
            crew = Crew(
                agents=[
                    self.agents["project_manager"],
                    self.agents["schedule"],
                    self.agents["cost"],
                    self.agents["scope"],
                    self.agents["risk"]
                ],
                tasks=[self.tasks["project_manager"]],
                process=Process.hierarchical,
                verbose=2
            )
        else:
            # Modo sequencial - os especialistas trabalham em sequência
            crew = Crew(
                agents=[
                    self.agents["schedule"],
                    self.agents["cost"],
                    self.agents["scope"],
                    self.agents["risk"]
                ],
                tasks=[
                    self.tasks["schedule"],
                    self.tasks["cost"],
                    self.tasks["scope"],
                    self.tasks["risk"]
                ],
                process=Process.sequential,
                verbose=2
            )
        return crew
    
    def run(self):
        """
        Executa o workflow.
        
        Returns:
            Resultados da execução
        """
        # Executar a crew
        results = self.crew.kickoff()
        
        # Salvar resultados
        self._save_results(results)
        
        return results
    
    def _save_results(self, results):
        """
        Salva os resultados da execução.
        
        Args:
            results: Resultados da execução
        """
        # Criar nome de arquivo com timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"results_{self.process_type}_{timestamp}.txt"
        filepath = os.path.join(self.results_dir, filename)
        
        # Salvar resultados
        with open(filepath, 'w', encoding='utf-8') as f:
            if isinstance(results, list):
                for i, result in enumerate(results):
                    f.write(f"=== RESULTADO {i+1} ===\n\n")
                    f.write(result)
                    f.write("\n\n")
            else:
                f.write(results)
        
        print(f"Resultados salvos em: {filepath}")

# Exemplo de uso
if __name__ == "__main__":
    import argparse
    
    # Configurar argumentos de linha de comando
    parser = argparse.ArgumentParser(description='Workflow de Gerenciamento de Projetos com CrewAI')
    parser.add_argument('--process', choices=['sequential', 'hierarchical'], default='sequential',
                        help='Tipo de processo (sequential ou hierarchical)')
    parser.add_argument('--api_key', type=str, help='Chave de API para o LLM')
    parser.add_argument('--mock', action='store_true', help='Usar modo de simulação (sem chamadas reais ao LLM)')
    
    args = parser.parse_args()
    
    # Criar e executar workflow
    workflow = ProjectManagementWorkflow(
        llm_api_key=args.api_key,
        process_type=args.process
    )
    
    if args.mock:
        print("Executando em modo de simulação...")
        # Simular resultados
        mock_results = [
            """
            # ANÁLISE DE CRONOGRAMA
            
            ## Status Atual
            O projeto está com SPI de 0.85, indicando um leve atraso no cronograma.
            
            ## Avaliação da Saúde
            O cronograma está em estado de ATENÇÃO devido ao SPI abaixo de 0.9.
            
            ## Recomendações
            1. Revisar o caminho crítico e identificar oportunidades de fast-tracking
            2. Implementar horas extras para recuperar o atraso
            3. Monitorar de perto as tarefas críticas
            
            ## Justificativa
            As recomendações visam recuperar o atraso sem impactar o escopo ou a qualidade.
            """,
            """
            # ANÁLISE DE CUSTOS
            
            ## Status Atual
            O projeto está com CPI de 0.92, indicando um leve desvio no orçamento.
            
            ## Avaliação da Saúde
            Os custos estão em estado de ATENÇÃO devido ao CPI abaixo de 0.95.
            
            ## Recomendações
            1. Revisar as categorias de custo com maior desvio
            2. Implementar medidas de economia sem impactar a qualidade
            3. Monitorar de perto todas as despesas futuras
            
            ## Justificativa
            As recomendações visam controlar os custos sem comprometer os objetivos do projeto.
            """,
            """
            # ANÁLISE DE ESCOPO
            
            ## Status Atual
            O projeto teve uma mudança de escopo que impacta o cronograma em 15 dias.
            
            ## Avaliação de Impacto
            O impacto da mudança de escopo é SIGNIFICATIVO e requer revisão da linha de base.
            
            ## Recomendações
            1. Documentar formalmente a mudança de escopo
            2. Revisar a linha de base do cronograma
            3. Avaliar o impacto nos custos e recursos
            
            ## Justificativa
            As recomendações visam garantir que a mudança de escopo seja gerenciada adequadamente.
            """,
            """
            # ANÁLISE DE RISCOS
            
            ## Status Atual
            O projeto tem 3 riscos de nível alto que requerem atenção imediata.
            
            ## Avaliação de Riscos
            Os riscos de alto nível representam uma AMEAÇA SIGNIFICATIVA para o sucesso do projeto.
            
            ## Recomendações
            1. Implementar planos de mitigação para os riscos de alto nível
            2. Revisar o registro de riscos semanalmente
            3. Desenvolver planos de contingência para os riscos críticos
            
            ## Justificativa
            As recomendações visam reduzir a exposição do projeto aos riscos identificados.
            """
        ]
        
        # Salvar resultados simulados
        workflow._save_results(mock_results)
        
        print("Simulação concluída!")
    else:
        # Executar workflow real
        results = workflow.run()
        
        print("Execução concluída!")
