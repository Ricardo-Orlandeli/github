import os
import sys
import json
import random
from datetime import datetime

# Adicionar diretório pai ao path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar módulos do sistema
try:
    from agentes.rag_system_pmbok import PMBOKRAGSystem
    from agentes.schedule_agent_updated import ScheduleAgent
    from agentes.cost_agent_updated import CostAgent
    from agentes.pmbok_guard_rails import PMBOKGuardRails
except ImportError:
    print("Erro ao importar módulos. Verificando diretório atual...")
    print(f"Diretório atual: {os.getcwd()}")
    print(f"Conteúdo do diretório: {os.listdir('.')}")
    print("Tentando importar de forma alternativa...")
    
    # Tentar importar de forma alternativa
    sys.path.append(os.path.abspath('.'))
    from rag_system_pmbok import PMBOKRAGSystem
    from schedule_agent_updated import ScheduleAgent
    from cost_agent_updated import CostAgent
    from pmbok_guard_rails import PMBOKGuardRails

# Classe para simular interface LLM para testes
class MockLLMInterface:
    """
    Interface LLM simulada para testes.
    """
    
    def __init__(self):
        """
        Inicializa a interface LLM simulada.
        """
        self.responses = {
            "cronograma": [
                "Com base na análise do cronograma do projeto, recomendo as seguintes ações:\n\n1. Revisar o caminho crítico para identificar oportunidades de fast-tracking\n2. Alocar recursos adicionais para as tarefas críticas\n3. Implementar monitoramento diário das tarefas críticas\n4. Considerar a revisão da linha de base do cronograma se o atraso persistir\n5. Comunicar o status aos stakeholders e discutir estratégias de recuperação",
                "Analisando o SPI de 0.85, é evidente que o projeto está levemente atrasado. Recomendo:\n\n1. Implementar horas extras para recuperar o atraso\n2. Revisar as dependências entre tarefas para otimização\n3. Focar nas tarefas atrasadas com maior prioridade\n4. Documentar as lições aprendidas para evitar atrasos similares no futuro",
                "Para melhorar o desempenho do cronograma com SPI de 0.75, recomendo:\n\n1. Realizar reunião de emergência com a equipe do projeto\n2. Aplicar técnicas de compressão do cronograma como fast-tracking\n3. Revisar a alocação de recursos para otimização\n4. Implementar um sistema de monitoramento mais rigoroso\n5. Considerar a revisão da linha de base se necessário"
            ],
            "custos": [
                "Com base na análise dos custos do projeto, recomendo as seguintes ações:\n\n1. Revisar as categorias de custo com maior desvio\n2. Implementar medidas de economia sem impactar a qualidade\n3. Renegociar contratos com fornecedores\n4. Monitorar de perto todas as despesas futuras\n5. Recalcular a Estimativa no Término (EAC) semanalmente",
                "Analisando o CPI de 0.92, é evidente que o projeto está levemente acima do orçamento. Recomendo:\n\n1. Implementar controles mais rigorosos para aprovação de despesas\n2. Revisar processos para identificar ineficiências\n3. Focar na redução de custos nas categorias com maior desvio\n4. Comunicar o status aos stakeholders e discutir estratégias de recuperação",
                "Para melhorar o desempenho dos custos com CPI de 0.78, recomendo:\n\n1. Realizar reunião de emergência com a equipe do projeto\n2. Implementar congelamento de despesas não essenciais\n3. Revisar o escopo para identificar possíveis reduções\n4. Renegociar contratos com fornecedores principais\n5. Considerar a revisão do orçamento base"
            ]
        }
    
    def generate_text(self, prompt):
        """
        Gera texto com base no prompt.
        
        Args:
            prompt: Prompt para geração de texto
            
        Returns:
            Texto gerado
        """
        # Determinar o domínio com base no prompt
        if "cronograma" in prompt.lower() or "spi" in prompt.lower():
            domain = "cronograma"
        elif "custo" in prompt.lower() or "cpi" in prompt.lower():
            domain = "custos"
        else:
            # Domínio desconhecido, retornar resposta genérica
            return "Recomendo analisar os dados do projeto e seguir as melhores práticas do PMBOK."
        
        # Retornar uma resposta aleatória para o domínio
        return random.choice(self.responses[domain])

# Função para criar arquivos de status de teste
def create_test_status_files(base_dir):
    """
    Cria arquivos de status de teste.
    
    Args:
        base_dir: Diretório base para os arquivos
    """
    # Criar diretório de status se não existir
    status_dir = os.path.join(base_dir, "status_files")
    os.makedirs(status_dir, exist_ok=True)
    
    # Arquivo de status de cronograma
    schedule_content = """RELATÓRIO DE STATUS DE CRONOGRAMA
Projeto: Sistema de Gerenciamento de Dados (PROJ-0001)
Data: 15/04/2025
Gerente: João Silva

Status atual: Atrasado
Percentual de conclusão: 65.0%
Data de início: 10/01/2025
Data de término planejada: 30/06/2025
Data de término real/prevista: 15/07/2025
Atraso atual: 15 dias
Motivo do atraso: Problemas técnicos inesperados
Índice de Desempenho de Cronograma (SPI): 0.85
Valor Planejado (PV): R$ 250000.00
Valor Agregado (EV): R$ 212500.00

Tarefas críticas:
- Desenvolvimento do módulo de autenticação
- Integração com sistema de pagamentos
- Implementação do módulo de relatórios
- Testes de segurança

Tarefas atrasadas:
- Integração com sistema de pagamentos
- Implementação do módulo de relatórios
"""
    
    # Arquivo de status de custos
    cost_content = """RELATÓRIO DE STATUS DE CUSTOS
Projeto: Sistema de Gerenciamento de Dados (PROJ-0001)
Data: 15/04/2025
Gerente: João Silva

Orçamento inicial: R$ 500000.00
Custo real atual: R$ 230000.00
Desvio orçamentário: 8.5%
Índice de Desempenho de Custo (CPI): 0.92
Valor Agregado (EV): R$ 212500.00
Estimativa para conclusão: R$ 312500.00
Estimativa no término (EAC): R$ 542500.00
Variação no término (VAC): R$ -42500.00

Detalhamento por categoria:
- Pessoal: R$ 115000.00 (50.0%)
- Equipamentos: R$ 34500.00 (15.0%)
- Software: R$ 23000.00 (10.0%)
- Serviços: R$ 46000.00 (20.0%)
- Outros: R$ 11500.00 (5.0%)
"""
    
    # Arquivo de status de escopo
    scope_content = """RELATÓRIO DE STATUS DE ESCOPO
Projeto: Sistema de Gerenciamento de Dados (PROJ-0001)
Data: 15/04/2025
Gerente: João Silva

Escopo original: Sistema para gerenciamento de dados com módulos de autenticação, processamento e relatórios
Houve mudança de escopo: Sim
Descrição das mudanças: Adição de novos requisitos de segurança
Impacto no cronograma: 15 dias
Impacto no custo: R$ 50000.00

Solicitações de mudança:
- SCM-01: Adição de funcionalidade de autenticação biométrica
- SCM-02: Integração com sistema legado
- SCM-03: Adição de relatórios gerenciais

Requisitos atuais:
- REQ-01: O sistema deve permitir autenticação de usuários
- REQ-02: O sistema deve processar transações em menos de 2 segundos
- REQ-03: O sistema deve ser compatível com navegadores modernos
- REQ-04: O sistema deve permitir exportação de dados em formato CSV
- REQ-05: O sistema deve implementar criptografia de dados sensíveis
- REQ-06: O sistema deve ter interface responsiva
- REQ-07: O sistema deve permitir integração com APIs externas
- REQ-08: O sistema deve ter backup automático diário
- REQ-09: O sistema deve ter controle de acesso baseado em perfis
- REQ-10: O sistema deve registrar logs de auditoria
"""
    
    # Arquivo de status de riscos
    risk_content = """RELATÓRIO DE STATUS DE RISCOS
Projeto: Sistema de Gerenciamento de Dados (PROJ-0001)
Data: 15/04/2025
Gerente: João Silva

Riscos identificados:
- R01: Atraso na entrega de componentes críticos
  Probabilidade: 3/5, Impacto: 4/5, Nível: Alto
  Mitigação: Planejar buffer de tempo no cronograma
  Contingência: Acionar fornecedores alternativos

- R02: Rotatividade de pessoal-chave
  Probabilidade: 2/5, Impacto: 4/5, Nível: Médio
  Mitigação: Implementar programa de retenção de talentos
  Contingência: Redistribuir tarefas entre a equipe

- R03: Problemas de integração com sistemas legados
  Probabilidade: 4/5, Impacto: 3/5, Nível: Alto
  Mitigação: Realizar testes de integração antecipados
  Contingência: Implementar soluções de contorno

- R04: Falhas de segurança
  Probabilidade: 2/5, Impacto: 5/5, Nível: Alto
  Mitigação: Implementar revisões de segurança periódicas
  Contingência: Ativar plano de recuperação de desastres

Riscos ocorridos:
- R03 (ocorrido em 05/04/2025)
  Impacto real: Atraso de 2 semanas no cronograma
  Ações tomadas: Implementação do plano de contingência
"""
    
    # Salvar arquivos
    with open(os.path.join(status_dir, "PROJ-0001_cronograma.txt"), 'w', encoding='utf-8') as f:
        f.write(schedule_content)
    
    with open(os.path.join(status_dir, "PROJ-0001_custos.txt"), 'w', encoding='utf-8') as f:
        f.write(cost_content)
    
    with open(os.path.join(status_dir, "PROJ-0001_escopo.txt"), 'w', encoding='utf-8') as f:
        f.write(scope_content)
    
    with open(os.path.join(status_dir, "PROJ-0001_riscos.txt"), 'w', encoding='utf-8') as f:
        f.write(risk_content)
    
    print(f"Arquivos de status de teste criados em {status_dir}")

# Função para testar o sistema RAG
def test_rag_system(base_dir):
    """
    Testa o sistema RAG.
    
    Args:
        base_dir: Diretório base para os arquivos
        
    Returns:
        Resultados do teste
    """
    print("\n=== Testando Sistema RAG ===")
    
    # Criar diretório de resultados se não existir
    results_dir = os.path.join(base_dir, "test_results")
    os.makedirs(results_dir, exist_ok=True)
    
    # Testar RAG para diferentes domínios
    domains = ["cronograma", "custos", "escopo", "riscos"]
    results = {}
    
    for domain in domains:
        print(f"\nTestando RAG para domínio: {domain}")
        
        # Criar sistema RAG
        rag_system = PMBOKRAGSystem(domain=domain)
        
        # Consulta de exemplo
        if domain == "cronograma":
            query = "O projeto está com SPI de 0.85, indicando atraso no cronograma. Quais ações devem ser tomadas?"
        elif domain == "custos":
            query = "O projeto está com CPI de 0.92, indicando desvio no orçamento. Quais ações devem ser tomadas?"
        elif domain == "escopo":
            query = "O projeto teve uma mudança de escopo que impacta o cronograma em 15 dias. Como gerenciar essa mudança?"
        else:  # riscos
            query = "O projeto tem 3 riscos de nível alto. Como priorizar as ações de mitigação?"
        
        # Buscar documentos relevantes
        relevant_docs = rag_system.query(query, top_k=3)
        
        # Gerar prompt aumentado
        augmented_prompt = rag_system.augment_prompt(query)
        
        # Salvar resultados
        domain_results = {
            "query": query,
            "relevant_docs": [{"id": doc["id"], "title": doc["title"]} for doc in relevant_docs],
            "augmented_prompt": augmented_prompt
        }
        
        results[domain] = domain_results
        
        print(f"Documentos relevantes encontrados: {len(relevant_docs)}")
        for doc in relevant_docs:
            print(f"- {doc['id']}: {doc['title']}")
    
    # Salvar resultados em arquivo JSON
    results_file = os.path.join(results_dir, "rag_test_results.json")
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\nResultados do teste RAG salvos em {results_file}")
    
    return results

# Função para testar os agentes
def test_agents(base_dir):
    """
    Testa os agentes.
    
    Args:
        base_dir: Diretório base para os arquivos
        
    Returns:
        Resultados do teste
    """
    print("\n=== Testando Agentes ===")
    
    # Criar diretório de resultados se não existir
    results_dir = os.path.join(base_dir, "test_results")
    os.makedirs(results_dir, exist_ok=True)
    
    # Criar diretório de status se não existir
    status_dir = os.path.join(base_dir, "status_files")
    if not os.path.exists(status_dir) or len(os.listdir(status_dir)) == 0:
        create_test_status_files(base_dir)
    
    # Inicializar interface LLM simulada
    llm = MockLLMInterface()
    
    # Testar agente de cronograma
    print("\nTestando Agente de Cronograma")
    schedule_agent = ScheduleAgent(llm_interface=llm)
    schedule_file = os.path.join(status_dir, "PROJ-0001_cronograma.txt")
    schedule_results = schedule_agent.analyze_schedule_file(schedule_file)
    schedule_report = schedule_agent.generate_report(schedule_results)
    
    # Testar agente de custos
    print("\nTestando Agente de Custos")
    cost_agent = CostAgent(llm_interface=llm)
    cost_file = os.path.join(status_dir, "PROJ-0001_custos.txt")
    cost_results = cost_agent.analyze_cost_file(cost_file)
    cost_report = cost_agent.generate_report(cost_results)
    
    # Salvar resultados
    results = {
        "schedule_agent": {
            "analysis_results": schedule_results,
            "report": schedule_report
        },
        "cost_agent": {
            "analysis_results": cost_results,
            "report": cost_report
        }
    }
    
    # Salvar resultados em arquivo JSON
    results_file = os.path.join(results_dir, "agents_test_results.json")
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    # Salvar relatórios em arquivos de texto
    schedule_report_file = os.path.join(results_dir, "schedule_agent_report.txt")
    with open(schedule_report_file, 'w', encoding='utf-8') as f:
        f.write(schedule_report)
    
    cost_report_file = os.path.join(results_dir, "cost_agent_report.txt")
    with open(cost_report_file, 'w', encoding='utf-8') as f:
        f.write(cost_report)
    
    print(f"\nResultados do teste dos agentes salvos em {results_file}")
    print(f"Relatório do agente de cronograma salvo em {schedule_report_file}")
    print(f"Relatório do agente de custos salvo em {cost_report_file}")
    
    return results

# Função para testar os guard rails
def test_guard_rails(base_dir):
    """
    Testa os guard rails.
    
    Args:
        base_dir: Diretório base para os arquivos
        
    Returns:
        Resultados do teste
    """
    print("\n=== Testando Guard Rails ===")
    
    # Criar diretório de resultados se não existir
    results_dir = os.path.join(base_dir, "test_results")
    os.makedirs(results_dir, exist_ok=True)
    
    # Inicializar guard rails
    guard_rails = PMBOKGuardRails()
    
    # Dados de teste para diferentes domínios
    test_data = {
        "cronograma": {
            "spi": 0.75,
            "atraso_dias": 15,
            "duracao_planejada": 100,
            "tarefas_criticas": ["Tarefa 1", "Tarefa 2"],
            "replanejamento": True
        },
        "custos": {
            "cpi": 0.85,
            "desvio_orcamento": 12.5,
            "realocacao_orcamento": 6.0
        },
        "escopo": {
            "mudanca_escopo": "Sim",
            "impacto_cronograma": 15,
            "impacto_custo_percentual": 10.0,
            "num_mudancas_escopo": 4
        },
        "riscos": {
            "riscos_altos": ["R01", "R03", "R04"],
            "riscos_criticos": ["R01", "R04"],
            "novos_riscos_altos": ["R05"],
            "riscos_alta_exposicao": ["R01", "R03", "R04"]
        }
    }
    
    # Recomendações de teste para diferentes domínios
    test_recommendations = {
        "cronograma": [
            "Revisar o caminho crítico e identificar oportunidades de fast-tracking",
            "Alocar recursos adicionais para as tarefas críticas",
            "Implementar horas extras para recuperar o atraso"
        ],
        "custos": [
            "Revisar as categorias de custo com maior desvio",
            "Implementar medidas de economia sem impactar a qualidade",
            "Monitorar de perto todas as despesas futuras"
        ],
        "escopo": [
            "Documentar formalmente a mudança de escopo",
            "Revisar a linha de base do cronograma",
            "Avaliar o impacto nos custos e recursos"
        ],
        "riscos": [
            "Implementar planos de mitigação para os riscos de alto nível",
            "Revisar o registro de riscos semanalmente",
            "Desenvolver planos de contingência para os riscos críticos"
        ]
    }
    
    # Testar guard rails para diferentes domínios
    results = {}
    
    for domain in test_data.keys():
        print(f"\nTestando Guard Rails para domínio: {domain}")
        
        # Validar dados
        validation_results = guard_rails.validate(domain, test_data[domain])
        
        # Validar recomendações
        recommendation_validation = guard_rails.validate_recommendations(
            domain, test_recommendations[domain], test_data[domain]
        )
        
        # Gerar relatório
        report = guard_rails.generate_report(recommendation_validation)
        
        # Salvar resultados
        domain_results = {
            "validation_results": validation_results,
            "recommendation_validation": recommendation_validation,
            "report": report
        }
        
        results[domain] = domain_results
        
        print(f"Validação: {'VÁLIDO' if validation_results['valid'] else 'INVÁLIDO'}")
        print(f"Mensagens de validação: {len(validation_results['messages'])}")
        print(f"Validação de recomendações: {'VÁLIDO' if recommendation_validation['valid'] else 'INVÁLIDO'}")
        if not recommendation_validation['valid']:
            print(f"Tópicos ausentes: {recommendation_validation['missing_topics']}")
    
    # Salvar resultados em arquivo JSON
    results_file = os.path.join(results_dir, "guard_rails_test_results.json")
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    # Salvar relatórios em arquivos de texto
    for domain, domain_results in results.items():
        report_file = os.path.join(results_dir, f"guard_rails_{domain}_report.txt")
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(domain_results["report"])
    
    print(f"\nResultados do teste dos guard rails salvos em {results_file}")
    
    return results

# Função principal
def main():
    """
    Função principal para testar o sistema.
    """
    print("=== Iniciando Testes do Sistema ===")
    print(f"Data e hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    # Determinar diretório base
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print(f"Diretório base: {base_dir}")
    
    # Criar diretório de resultados se não existir
    results_dir = os.path.join(base_dir, "test_results")
    os.makedirs(results_dir, exist_ok=True)
    
    # Testar sistema RAG
    rag_results = test_rag_system(base_dir)
    
    # Testar agentes
    agent_results = test_agents(base_dir)
    
    # Testar guard rails
    guard_rails_results = test_guard_rails(base_dir)
    
    # Compilar resultados
    results = {
        "rag_system": rag_results,
        "agents": agent_results,
        "guard_rails": guard_rails_results,
        "test_date": datetime.now().isoformat()
    }
    
    # Salvar resultados compilados
    results_file = os.path.join(results_dir, "system_test_results.json")
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n=== Testes Concluídos ===")
    print(f"Resultados compilados salvos em {results_file}")

if __name__ == "__main__":
    main()
