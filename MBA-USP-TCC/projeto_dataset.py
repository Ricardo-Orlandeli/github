import pandas as pd
import numpy as np
import random
import os
import json
from datetime import datetime, timedelta
from faker import Faker

# Configurar o Faker para português do Brasil
fake = Faker('pt_BR')
Faker.seed(42)  # Para reprodutibilidade
np.random.seed(42)
random.seed(42)

def gerar_dataset(num_projetos=1000, output_dir="../dataset"):
    """
    Generates a synthetic dataset for training AI agents.

    Args:
        num_projetos: Number of projects to generate
        output_dir: Output directory for the files
    """
    print(f"Generating dataset with {num_projetos} projects...")

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Generate projects
    projetos = []
    for i in range(num_projetos):
        projeto_id = f"PROJ-{i+1:04d}"

        # Basic project data
        data_inicio = fake.date_between(start_date='-2y', end_date='-6m')
        duracao_planejada = random.randint(30, 365)  # Between 1 month and 1 year
        data_termino_planejada = data_inicio + timedelta(days=duracao_planejada)

        # Project status (in progress, completed, delayed, cancelled)
        status_opcoes = ['Em andamento', 'Concluído', 'Atrasado', 'Cancelado']
        status_pesos = [0.5, 0.2, 0.25, 0.05]  # More projects in progress and delayed
        status = random.choices(status_opcoes, weights=status_pesos, k=1)[0]

        # Budget and manager
        orcamento_inicial = random.randint(50000, 5000000)
        gerente = fake.name()

        # Calculate elapsed time percentage first
        dias_decorridos = (datetime.now().date() - data_inicio).days
        percentual_tempo = min(1.0, dias_decorridos / duracao_planejada)

        # Completion percentage
        if status == 'Concluído':
            percentual_conclusao = 100.0
        elif status == 'Cancelado':
            percentual_conclusao = random.uniform(10.0, 90.0)
        else:
            # For projects in progress or delayed, the percentage depends on elapsed time
            if status == 'Em andamento':
                # Projects in progress can be slightly ahead or behind schedule
                percentual_conclusao = percentual_tempo * random.uniform(0.8, 1.2)
            else:  # Delayed
                # Delayed projects have a completion percentage lower than elapsed time
                percentual_conclusao = percentual_tempo * random.uniform(0.5, 0.9)

            percentual_conclusao = min(99.9, max(1.0, percentual_conclusao * 100))

        # Actual/forecasted end date
        if status == 'Concluído':
            # Completed projects may have finished early, on time, or with a small delay
            variacao_dias = random.randint(-30, 30)
            data_termino_real = data_termino_planejada + timedelta(days=variacao_dias)
        elif status == 'Cancelado':
            # Cancelled projects end early
            data_termino_real = data_inicio + timedelta(days=int(duracao_planejada * percentual_conclusao / 100))
        elif status == 'Atrasado':
            # Delayed projects have a forecasted end date after the planned date
            atraso_dias = random.randint(10, 180)  # Between 10 days and 6 months of delay
            data_termino_real = data_termino_planejada + timedelta(days=atraso_dias)
        else:  # Em andamento
            # Projects in progress can be on time or with a small delay/ahead
            variacao_dias = random.randint(-15, 30)
            data_termino_real = data_termino_planejada + timedelta(days=variacao_dias)

        # Calculate current delay in days
        if datetime.now().date() > data_termino_planejada:
            atraso_atual = (datetime.now().date() - data_termino_planejada).days
        else:
            atraso_atual = 0

        # Generate earned value metrics
        pv = orcamento_inicial * (percentual_tempo if percentual_tempo <= 1.0 else 1.0)  # Planned Value

        # Earned Value (EV) based on completion percentage and budget
        ev = orcamento_inicial * (percentual_conclusao / 100)

        # Actual Cost (AC) with variation
        if status == 'Em andamento' or status == 'Concluído':
            ac_variacao = random.uniform(0.8, 1.2)  # Variation from -20% to +20%
        else:  # Delayed or Cancelled
            ac_variacao = random.uniform(1.0, 1.5)  # Variation from 0% to +50% (higher costs)

        ac = float(ev) * ac_variacao

        # Calculate SPI and CPI
        spi = ev / pv if pv > 0 else 1.0
        cpi = ev / ac if ac > 0 else 1.0

        # Adjust SPI and CPI for specific statuses
        if status == 'Atrasado':
            spi = min(spi, 0.9)  # Delayed projects have SPI < 0.9
        elif status == 'Em andamento':
            spi = random.uniform(0.85, 1.15)  # Projects in progress have SPI between 0.85 and 1.15
        elif status == 'Concluído':
            spi = random.uniform(0.95, 1.1)  # Completed projects have SPI between 0.95 and 1.1

        # Estimates
        etc = (float(orcamento_inicial) - float(ev)) / cpi if cpi > 0 and percentual_conclusao < 100 else 0  # Estimate to Complete
        eac = ac + etc  # Estimate at Completion
        vac = orcamento_inicial - eac  # Variance at Completion

        # Budget variance in percentage
        desvio_orcamento = ((ac / (float(orcamento_inicial) * percentual_tempo)) - 1) * 100 if percentual_tempo > 0 else 0

        # Generate cost categories
        categorias_custos = {
            "Pessoal": float(ac) * random.uniform(0.4, 0.6),
            "Equipamentos": float(ac) * random.uniform(0.1, 0.2),
            "Software": float(ac) * random.uniform(0.05, 0.15),
            "Serviços": float(ac) * random.uniform(0.1, 0.2),
            "Outros": float(ac) * random.uniform(0.05, 0.1)
        }

        # Adjust to ensure sum equals AC
        soma_categorias = sum(categorias_custos.values())
        fator_ajuste = float(ac) / float(soma_categorias)
        categorias_custos = {k: v * fator_ajuste for k, v in categorias_custos.items()}

        # Generate scope information
        mudanca_escopo = random.choices(['Sim', 'Não'], weights=[0.3, 0.7], k=1)[0]

        if mudanca_escopo == 'Sim':
            descricao_mudancas = random.choice([
                "Adição de novos requisitos de segurança",
                "Expansão do escopo para incluir funcionalidades adicionais",
                "Redução do escopo devido a restrições orçamentárias",
                "Alteração nas especificações técnicas",
                "Mudança na plataforma de implementação"
            ])

            impacto_cronograma = random.randint(5, 60)
            impacto_custo = round(float(orcamento_inicial) * random.uniform(0.05, 0.2), 2)

            num_solicitacoes = random.randint(1, 5)
            solicitacoes_mudanca = []
            for j in range(num_solicitacoes):
                solicitacoes_mudanca.append(f"SCM-{j+1:02d}: {random.choice([
                    'Adição de funcionalidade de autenticação biométrica',
                    'Alteração na interface do usuário',
                    'Integração com sistema legado',
                    'Mudança no banco de dados',
                    'Adição de relatórios gerenciais',
                    'Implementação de módulo de exportação de dados',
                    'Alteração nos requisitos de desempenho',
                    'Mudança na arquitetura do sistema'
                ])}")
        else:
            descricao_mudancas = "N/A"
            impacto_cronograma = 0
            impacto_custo = 0
            solicitacoes_mudanca = []

        # Generate requirements
        num_requisitos = random.randint(5, 15)
        requisitos = []
        for j in range(num_requisitos):
            requisitos.append(f"REQ-{j+1:02d}: {random.choice([
                'O sistema deve permitir autenticação de usuários',
                'O sistema deve processar transações em menos de 2 seconds',
                'O sistema deve ser compatível com navegadores modernos',
                'O sistema deve permitir exportação de dados em formato CSV',
                'O sistema deve implementar criptografia de dados sensíveis',
                'O sistema deve ter interface responsiva',
                'O sistema deve permitir integração com APIs externas',
                'O sistema deve ter backup automático diário',
                'O sistema deve ter controle de acesso baseado em perfis',
                'O sistema deve registrar logs de auditoria',
                'O sistema deve ter alta disponibilidade (99.9%)',
                'O sistema deve ser escalável para suportar até 10.000 usuários simultâneos',
                'O sistema deve ter documentação completa',
                'O sistema deve passar por testes de segurança',
                'O sistema deve ser compatível com dispositivos móveis'
            ])}")

        # Generate risks
        num_riscos = random.randint(3, 10)
        riscos = []
        for j in range(num_riscos):
            probabilidade = random.randint(1, 5)
            impacto = random.randint(1, 5)
            nivel = "Baixo" if probabilidade * impacto <= 6 else "Médio" if probabilidade * impacto <= 15 else "Alto"

            riscos.append({
                "id": f"R{j+1:02d}",
                "descricao": random.choice([
                    "Atraso na entrega de componentes críticos",
                    "Rotatividade de pessoal-chave",
                    "Mudanças regulatórias",
                    "Problemas de integração com sistemas legados",
                    "Falhas de segurança",
                    "Indisponibilidade de recursos especializados",
                    "Problemas de desempenho",
                    "Falhas em testes de aceitação",
                    "Resistência dos usuários à mudança",
                    "Problemas de compatibilidade",
                    "Falhas de infraestrutura",
                    "Dependências externas não cumpridas",
                    "Estimativas imprecisas",
                    "Requisitos mal definidos",
                    "Problemas de comunicação com stakeholders"
                ]),
                "probabilidade": probabilidade,
                "impacto": impacto,
                "nivel": nivel,
                "plano_mitigacao": random.choice([
                    "Implementar plano de contingência",
                    "Contratar pessoal adicional",
                    "Monitorar mudanças regulatórias",
                    "Realizar testes de integração antecipados",
                    "Fortalecer medidas de segurança",
                    "Buscar fornecedores alternativos",
                    "Otimizar código e infraestrutura",
                    "Realizar testes de aceitação com usuários-chave",
                    "Comunicar benefícios da mudança",
                    "Testar compatibilidade em diferentes ambientes",
                    "Implementar redundância de infraestrutura",
                    "Gerenciar dependências ativamente",
                    "Refinar estimativas com base em dados históricos",
                    "Melhorar a documentação de requisitos",
                    "Estabelecer canais de comunicação claros"
                ])
            })

        # Generate stakeholders
        num_stakeholders = random.randint(3, 8)
        stakeholders = []
        for j in range(num_stakeholders):
            stakeholders.append({
                "nome": fake.name(),
                "papel": random.choice([
                    "Patrocinador",
                    "Gerente de Área",
                    "Usuário Final",
                    "Equipe de Desenvolvimento",
                    "Fornecedor",
                    "Regulador",
                    "Consultor",
                    "Analista de Negócios"
                ]),
                "interesse": random.choice([
                    "Alto",
                    "Médio",
                    "Baixo"
                ]),
                "influencia": random.choice([
                    "Alto",
                    "Médio",
                    "Baixo"
                ])
            })

        # Generate communication plan
        num_comunicacoes = random.randint(2, 5)
        plano_comunicacao = []
        for j in range(num_comunicacoes):
            plano_comunicacao.append({
                "tipo": random.choice([
                    "Reunião de Status",
                    "Relatório Semanal",
                    "Email",
                    "Apresentação",
                    "Workshop"
                ]),
                "frequencia": random.choice([
                    "Diária",
                    "Semanal",
                    "Quinzenal",
                    "Mensal"
                ]),
                "audiencia": random.choice([
                    "Equipe do Projeto",
                    "Stakeholders Chave",
                    "Gerência",
                    "Todos os Envolvidos"
                ]),
                "responsavel": fake.name()
            })

        # Generate quality metrics
        num_metricas_qualidade = random.randint(3, 7)
        metricas_qualidade = []
        for j in range(num_metricas_qualidade):
            metricas_qualidade.append({
                "metrica": random.choice([
                    "Número de Defeitos por Iteração",
                    "Tempo Médio para Correção de Defeitos",
                    "Satisfação do Cliente",
                    "Cobertura de Testes",
                    "Número de Bugs Críticos",
                    "Tempo de Resposta do Sistema",
                    "Disponibilidade do Sistema"
                ]),
                "valor_atual": round(random.uniform(0.5, 100.0), 2),
                "meta": round(random.uniform(1.0, 95.0), 2)
            })

        # Generate resource allocation
        num_recursos = random.randint(5, 15)
        alocacao_recursos = []
        for j in range(num_recursos):
            alocacao_recursos.append({
                "recurso": fake.name() if random.random() > 0.3 else fake.job(),
                "tipo": random.choice([
                    "Pessoa",
                    "Equipamento",
                    "Software"
                ]),
                "alocacao_percentual": random.randint(20, 100),
                "custo_hora": round(random.uniform(20.0, 200.0), 2)
            })

        # Generate dependencies
        num_dependencias = random.randint(0, 5)
        dependencias = []
        if num_dependencias > 0 and i > 0: # Avoid dependencies on the first project
            for j in range(num_dependencias):
                dependencia_id = f"PROJ-{random.randint(1, i):04d}"
                dependencias.append({
                    "projeto_dependente_id": projeto_id,
                    "projeto_dependencia_id": dependencia_id,
                    "tipo": random.choice([
                        "Término para Início",
                        "Início para Início",
                        "Término para Término"
                    ]),
                    "descricao": random.choice([
                        f"Requer a conclusão do projeto {dependencia_id}",
                        f"Requer o início do projeto {dependencia_id}",
                        f"Requer a conclusão simultânea com o projeto {dependencia_id}"
                    ])
                })

        # Generate lessons learned
        num_licoes = random.randint(0, 3)
        licoes_aprendidas = []
        if num_licoes > 0:
            for j in range(num_licoes):
                licoes_aprendidas.append({
                    "licao": random.choice([
                        "A comunicação proativa com stakeholders é crucial.",
                        "A gestão de riscos deve ser contínua.",
                        "A definição clara do escopo evita retrabalho.",
                        "A alocação adequada de recursos impacta o cronograma.",
                        "Testes contínuos melhoram a qualidade.",
                        "A colaboração entre equipes é fundamental.",
                        "A documentação detalhada facilita a manutenção.",
                        "A adaptação a mudanças é necessária."
                    ]),
                    "categoria": random.choice([
                        "Processo",
                        "Pessoas",
                        "Técnico",
                        "Comunicação"
                    ])
                })

        # Generate occurred risks
        riscos_ocorridos = []
        if random.random() < 0.4:  # 40% chance of having occurred risks
            num_riscos_ocorridos = random.randint(1, min(3, len(riscos)))
            riscos_selecionados = random.sample(riscos, num_riscos_ocorridos)

            for risco in riscos_selecionados:
                data_ocorrencia = fake.date_between(start_date=data_inicio, end_date=datetime.now().date())

                riscos_ocorridos.append({
                    "id": risco["id"],
                    "data": data_ocorrencia.strftime("%d/%m/%Y"),
                    "impacto_real": random.choice([
                        "Atraso de 2 semanas no cronograma",
                        "Aumento de 10% nos custos",
                        "Redução de funcionalidades",
                        "Problemas de qualidade",
                        "Insatisfação dos stakeholders",
                        "Retrabalho significativo",
                        "Perda de dados",
                        "Indisponibilidade temporária",
                        "Falhas de segurança",
                        "Perda de recursos-chave"
                    ]),
                    "acoes_tomadas": random.choice([
                        "Implementação do plano de contingência",
                        "Realocação de recursos",
                        "Ajuste no cronograma",
                        "Revisão do orçamento",
                        "Contratação de recursos adicionais",
                        "Implementação de controles adicionais",
                        "Revisão de processos",
                        "Comunicação intensificada com stakeholders",
                        "Revisão de prioridades",
                        "Implementação de soluções alternativas"
                    ])
                })

        # Generate critical and delayed tasks
        num_tarefas_criticas = random.randint(3, 8)
        tarefas_criticas = []
        for j in range(num_tarefas_criticas):
            tarefas_criticas.append(random.choice([
                "Desenvolvimento do módulo de autenticação",
                "Integração com sistema de pagamentos",
                "Implementação do módulo de relatórios",
                "Migração de dados legados",
                "Testes de segurança",
                "Implementação da API REST",
                "Desenvolvimento da interface do usuário",
                "Configuração da infraestrutura",
                "Implementação do módulo de notificações",
                "Testes de aceitação do usuário",
                "Implementação do módulo de análise de dados",
                "Desenvolvimento do painel administrativo",
                "Implementação do sistema de backup",
                "Configuração do ambiente de produção",
                "Implementação do módulo de exportação de dados"
            ]))

        tarefas_atrasadas = []
        if status == 'Atrasado':
            num_tarefas_atrasadas = random.randint(1, min(3, len(tarefas_criticas)))
            tarefas_atrasadas = random.sample(tarefas_criticas, num_tarefas_atrasadas)

        # Reason for delay
        if status == 'Atrasado':
            motivo_atraso = random.choice([
                "Atraso na entrega de componentes por fornecedores",
                "Problemas técnicos inesperados",
                "Rotatividade de pessoal-chave",
                "Mudanças de requisitos não planejadas",
                "Estimativas imprecisas",
                "Dependências externas não cumpridas",
                "Problemas de integração com sistemas legados",
                "Falhas em testes de aceitação",
                "Recursos insuficientes",
                "Problemas de comunicação"
            ])
        else:
            motivo_atraso = "N/A"

        # Compile project information
        projeto = {
            "id": projeto_id,
            "nome": fake.catch_phrase(),
            "data_inicio": data_inicio.strftime("%d/%m/%Y"),
            "data_termino_planejada": data_termino_planejada.strftime("%d/%m/%Y"),
            "data_termino_real": data_termino_real.strftime("%d/%m/%Y"),
            "duracao_planejada": duracao_planejada,
            "orcamento_inicial": orcamento_inicial,
            "gerente": gerente,
            "status": status,
            "percentual_conclusao": percentual_conclusao,
            "atraso_atual": atraso_atual,
            "motivo_atraso": motivo_atraso,
            "valor_planejado": pv,
            "valor_agregado": ev,
            "custo_real_atual": ac,
            "spi": spi,
            "cpi": cpi,
            "estimativa_custo_conclusao": etc,
            "estimativa_final_projeto": eac,
            "variacao_final_projeto": vac,
            "desvio_orcamento": desvio_orcamento,
            "categorias_custos": categorias_custos,
            "mudanca_escopo": mudanca_escopo,
            "descricao_mudancas": descricao_mudancas,
            "impacto_cronograma": impacto_cronograma,
            "impacto_custo": impacto_custo,
            "solicitacoes_mudanca": solicitacoes_mudanca,
            "requisitos": requisitos,
            "tarefas_criticas": tarefas_criticas,
            "tarefas_atrasadas": tarefas_atrasadas,
            "riscos": riscos,
            "riscos_ocorridos": riscos_ocorridos,
            "stakeholders": stakeholders,
            "plano_comunicacao": plano_comunicacao,
            "metricas_qualidade": metricas_qualidade,
            "alocacao_recursos": alocacao_recursos,
            "dependencias": dependencias,
            "licoes_aprendidas": licoes_aprendidas
        }

        projetos.append(projeto)

    # Save dataset in JSON format
    with open(os.path.join(output_dir, "projetos.json"), 'w', encoding='utf-8') as f:
        json.dump(projetos, f, ensure_ascii=False, indent=2)

    # Save dataset in CSV format (main data only)
    df_projetos = pd.DataFrame([{
        "id": p["id"],
        "nome": p["nome"],
        "data_inicio": p["data_inicio"],
        "data_termino_planejada": p["data_termino_planejada"],
        "data_termino_real": p["data_termino_real"],
        "orcamento_inicial": p["orcamento_inicial"],
        "gerente": p["gerente"],
        "status": p["status"],
        "percentual_conclusao": p["percentual_conclusao"],
        "spi": p["spi"],
        "cpi": p["cpi"],
        "mudanca_escopo": p["mudanca_escopo"]
    } for p in projetos])

    df_projetos.to_csv(os.path.join(output_dir, "projetos.csv"), index=False)

    # Generate status files for each project
    os.makedirs(os.path.join(output_dir, "status_files"), exist_ok=True)

    for projeto in projetos:
        # Schedule status file
        with open(os.path.join(output_dir, "status_files", f"{projeto['id']}_cronograma.txt"), 'w', encoding='utf-8') as f:
            f.write(f"RELATÓRIO DE STATUS DE CRONOGRAMA\n")
            f.write(f"Projeto: {projeto['nome']} ({projeto['id']})\n")
            f.write(f"Data: {datetime.now().strftime('%d/%m/%Y')}\n")
            f.write(f"Gerente: {projeto['gerente']}\n\n")

            f.write(f"Status atual: {projeto['status']}\n")
            f.write(f"Percentual de conclusão: {projeto['percentual_conclusao']:.1f}%\n")
            f.write(f"Data de início: {projeto['data_inicio']}\n")
            f.write(f"Data de término planejada: {projeto['data_termino_planejada']}\n")
            f.write(f"Data de término real/prevista: {projeto['data_termino_real']}\n")
            f.write(f"Atraso atual: {projeto['atraso_atual']} dias\n")
            f.write(f"Motivo do atraso: {projeto['motivo_atraso']}\n")
            f.write(f"Índice de Desempenho de Cronograma (SPI): {projeto['spi']:.2f}\n")
            f.write(f"Valor Planejado (PV): R$ {projeto['valor_planejado']:.2f}\n")
            f.write(f"Valor Agregado (EV): R$ {projeto['valor_agregado']:.2f}\n\n")

            f.write(f"Tarefas críticas:\n")
            for tarefa in projeto['tarefas_criticas']:
                f.write(f"- {tarefa}\n")

            f.write(f"\nTarefas atrasadas:\n")
            for tarefa in projeto['tarefas_atrasadas']:
                f.write(f"- {tarefa}\n")

        # Cost status file
        with open(os.path.join(output_dir, "status_files", f"{projeto['id']}_custos.txt"), 'w', encoding='utf-8') as f:
            f.write(f"RELATÓRIO DE STATUS DE CUSTOS\n")
            f.write(f"Projeto: {projeto['nome']} ({projeto['id']})\n")
            f.write(f"Data: {datetime.now().strftime('%d/%m/%Y')}\n")
            f.write(f"Gerente: {projeto['gerente']}\n\n")

            f.write(f"Orçamento inicial: R$ {projeto['orcamento_inicial']:.2f}\n")
            f.write(f"Custo real atual: R$ {projeto['custo_real_atual']:.2f}\n")
            f.write(f"Desvio orçamentário: {projeto['desvio_orcamento']:.2f}%\n")
            f.write(f"Índice de Desempenho de Custo (CPI): {projeto['cpi']:.2f}\n")
            f.write(f"Valor Agregado (EV): R$ {projeto['valor_agregado']:.2f}\n")
            f.write(f"Estimativa para conclusão: R$ {projeto['estimativa_custo_conclusao']:.2f}\n")
            f.write(f"Estimativa no término (EAC): R$ {projeto['estimativa_final_projeto']:.2f}\n")
            f.write(f"Variação no término (VAC): R$ {projeto['variacao_final_projeto']:.2f}\n\n")

            f.write(f"Detalhamento por categoria:\n")
            for categoria, valor in projeto['categorias_custos'].items():
                percentual = valor / float(projeto['custo_real_atual']) * 100
                f.write(f"- {categoria}: R$ {valor:.2f} ({percentual:.1f}%)\n")

        # Scope status file
        with open(os.path.join(output_dir, "status_files", f"{projeto['id']}_escopo.txt"), 'w', encoding='utf-8') as f:
            f.write(f"RELATÓRIO DE STATUS DE ESCOPO\n")
            f.write(f"Projeto: {projeto['nome']} ({projeto['id']})\n")
            f.write(f"Data: {datetime.now().strftime('%d/%m/%Y')}\n")
            f.write(f"Gerente: {projeto['gerente']}\n\n")

            f.write(f"Escopo original: Sistema para {projeto['nome'].lower()}\n")
            f.write(f"Houve mudança de escopo: {projeto['mudanca_escopo']}\n")
            f.write(f"Descrição das mudanças: {projeto['descricao_mudancas']}\n")
            f.write(f"Impacto no cronograma: {projeto['impacto_cronograma']} dias\n")
            f.write(f"Impacto no custo: R$ {projeto['impacto_custo']:.2f}\n\n")

            f.write(f"Solicitações de mudança:\n")
            for solicitacao in projeto['solicitacoes_mudanca']:
                f.write(f"- {solicitacao}\n")

            f.write(f"\nRequisitos atuais:\n")
            for requisito in projeto['requisitos']:
                f.write(f"- {requisito}\n")

        # Risk status file
        with open(os.path.join(output_dir, "status_files", f"{projeto['id']}_riscos.txt"), 'w', encoding='utf-8') as f:
            f.write(f"RELATÓRIO DE STATUS DE RISCOS\n")
            f.write(f"Projeto: {projeto['nome']} ({projeto['id']})\n")
            f.write(f"Data: {datetime.now().strftime('%d/%m/%Y')}\n")
            f.write(f"Gerente: {projeto['gerente']}\n\n")

            f.write(f"Riscos identificados:\n")
            for risco in projeto['riscos']:
                f.write(f"- {risco['id']}: {risco['descricao']}\n")
                f.write(f"  Probabilidade: {risco['probabilidade']}/5, Impacto: {risco['impacto']}/5, Nível: {risco['nivel']}\n")
                f.write(f"  Mitigação: {risco['plano_mitigacao']}\n\n")

            f.write(f"Riscos ocorridos:\n")
            for risco in projeto['riscos_ocorridos']:
                f.write(f"- {risco['id']} (ocorrido em {risco['data']})\n")
                f.write(f"  Impacto real: {risco['impacto_real']}\n")
                f.write(f"  Ações tomadas: {risco['acoes_tomadas']}\n\n")

    print(f"Dataset generated successfully! Files saved in {output_dir}")
    return projetos

if __name__ == "__main__":
    # Generate dataset with 1000 projects
    gerar_dataset(num_projetos=1000)

# To generate a smaller dataset for testing:
# gerar_dataset(num_projetos=10, output_dir="../test_dataset")

# To generate the full dataset:
# gerar_dataset(num_projetos=1000)