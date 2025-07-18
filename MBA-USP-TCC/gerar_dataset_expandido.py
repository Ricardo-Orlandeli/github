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
    Gera um dataset sintético para treinamento dos agentes de IA.
    
    Args:
        num_projetos: Número de projetos a serem gerados
        output_dir: Diretório de saída para os arquivos
    """
    print(f"Gerando dataset com {num_projetos} projetos...")
    
    # Criar diretório de saída se não existir
    os.makedirs(output_dir, exist_ok=True)
    
    # Gerar projetos
    projetos = []
    for i in range(num_projetos):
        projeto_id = f"PROJ-{i+1:04d}"
        
        # Dados básicos do projeto
        data_inicio = fake.date_between(start_date='-2y', end_date='-6m')
        duracao_planejada = random.randint(30, 365)  # Entre 1 mês e 1 ano
        data_termino_planejada = data_inicio + timedelta(days=duracao_planejada)
        
        # Status do projeto (em andamento, concluído, atrasado, cancelado)
        status_opcoes = ['Em andamento', 'Concluído', 'Atrasado', 'Cancelado']
        status_pesos = [0.5, 0.2, 0.25, 0.05]  # Mais projetos em andamento e atrasados
        status = random.choices(status_opcoes, weights=status_pesos, k=1)[0]
        
        # Orçamento e gerente
        orcamento_inicial = random.randint(50000, 5000000)
        gerente = fake.name()
        
        # Percentual de conclusão
        if status == 'Concluído':
            percentual_conclusao = 100.0
        elif status == 'Cancelado':
            percentual_conclusao = random.uniform(10.0, 90.0)
        else:
            # Para projetos em andamento ou atrasados, o percentual depende do tempo decorrido
            dias_decorridos = (datetime.now().date() - data_inicio).days
            percentual_tempo = min(1.0, dias_decorridos / duracao_planejada)
            
            if status == 'Em andamento':
                # Projetos em andamento podem estar um pouco adiantados ou atrasados
                percentual_conclusao = percentual_tempo * random.uniform(0.8, 1.2)
            else:  # Atrasado
                # Projetos atrasados têm percentual de conclusão menor que o tempo decorrido
                percentual_conclusao = percentual_tempo * random.uniform(0.5, 0.9)
            
            percentual_conclusao = min(99.9, max(1.0, percentual_conclusao * 100))
        
        # Data de término real/prevista
        if status == 'Concluído':
            # Projetos concluídos podem ter terminado antes, no prazo ou com pequeno atraso
            variacao_dias = random.randint(-30, 30)
            data_termino_real = data_termino_planejada + timedelta(days=variacao_dias)
        elif status == 'Cancelado':
            # Projetos cancelados terminam antes do prazo
            data_termino_real = data_inicio + timedelta(days=int(duracao_planejada * percentual_conclusao / 100))
        elif status == 'Atrasado':
            # Projetos atrasados têm previsão de término após a data planejada
            atraso_dias = random.randint(10, 180)  # Entre 10 dias e 6 meses de atraso
            data_termino_real = data_termino_planejada + timedelta(days=atraso_dias)
        else:  # Em andamento
            # Projetos em andamento podem estar no prazo ou com pequeno atraso/adiantamento
            variacao_dias = random.randint(-15, 30)
            data_termino_real = data_termino_planejada + timedelta(days=variacao_dias)
        
        # Calcular atraso atual em dias
        if datetime.now().date() > data_termino_planejada:
            atraso_atual = (datetime.now().date() - data_termino_planejada).days
        else:
            atraso_atual = 0
        
        # Gerar métricas de valor agregado
        pv = orcamento_inicial * (percentual_tempo if percentual_tempo <= 1.0 else 1.0)  # Valor Planejado
        
        # Valor Agregado (EV) baseado no percentual de conclusão e orçamento
        ev = orcamento_inicial * (percentual_conclusao / 100)
        
        # Custo Real (AC) com variação
        if status == 'Em andamento' or status == 'Concluído':
            ac_variacao = random.uniform(0.8, 1.2)  # Variação de -20% a +20%
        else:  # Atrasado ou Cancelado
            ac_variacao = random.uniform(1.0, 1.5)  # Variação de 0% a +50% (mais custos)
        
        ac = ev * ac_variacao
        
        # Calcular SPI e CPI
        spi = ev / pv if pv > 0 else 1.0
        cpi = ev / ac if ac > 0 else 1.0
        
        # Ajustar SPI e CPI para status específicos
        if status == 'Atrasado':
            spi = min(spi, 0.9)  # Projetos atrasados têm SPI < 0.9
        elif status == 'Em andamento':
            spi = random.uniform(0.85, 1.15)  # Projetos em andamento têm SPI entre 0.85 e 1.15
        elif status == 'Concluído':
            spi = random.uniform(0.95, 1.1)  # Projetos concluídos têm SPI entre 0.95 e 1.1
        
        # Estimativas
        etc = (orcamento_inicial - ev) / cpi if cpi > 0 and percentual_conclusao < 100 else 0  # Estimativa para Conclusão
        eac = ac + etc  # Estimativa no Término
        vac = orcamento_inicial - eac  # Variação no Término
        
        # Desvio orçamentário em percentual
        desvio_orcamento = ((ac / (orcamento_inicial * percentual_tempo)) - 1) * 100 if percentual_tempo > 0 else 0
        
        # Gerar categorias de custos
        categorias_custos = {
            "Pessoal": ac * random.uniform(0.4, 0.6),
            "Equipamentos": ac * random.uniform(0.1, 0.2),
            "Software": ac * random.uniform(0.05, 0.15),
            "Serviços": ac * random.uniform(0.1, 0.2),
            "Outros": ac * random.uniform(0.05, 0.1)
        }
        
        # Ajustar para garantir que a soma seja igual ao AC
        soma_categorias = sum(categorias_custos.values())
        fator_ajuste = ac / soma_categorias
        categorias_custos = {k: v * fator_ajuste for k, v in categorias_custos.items()}
        
        # Gerar informações de escopo
        mudanca_escopo = random.choices(['Sim', 'Não'], weights=[0.3, 0.7], k=1)[0]
        
        if mudanca_escopo == 'Sim':
            descricao_mudancas = random.choice([
                "Adição de novos requisitos de segurança",
                "Expansão do escopo para incluir funcionalidades adicionais",
                "Redução do escopo devido a restrições orçamentárias",
                "Alteração nas especificações técnicas",
                "Mudança na plataforma de implementação"
            ])
            
            impacto_cronograma = random.randint(5, 60)  # Entre 5 e 60 dias
            impacto_custo = orcamento_inicial * random.uniform(0.05, 0.2)  # Entre 5% e 20% do orçamento
            
            # Gerar solicitações de mudança
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
        
        # Gerar requisitos
        num_requisitos = random.randint(5, 15)
        requisitos = []
        for j in range(num_requisitos):
            requisitos.append(f"REQ-{j+1:02d}: {random.choice([
                'O sistema deve permitir autenticação de usuários',
                'O sistema deve processar transações em menos de 2 segundos',
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
        
        # Gerar riscos
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
                "mitigacao": random.choice([
                    "Planejar buffer de tempo no cronograma",
                    "Implementar programa de retenção de talentos",
                    "Monitorar mudanças regulatórias",
                    "Realizar testes de integração antecipados",
                    "Implementar revisões de segurança periódicas",
                    "Contratar consultores externos",
                    "Realizar testes de carga e desempenho",
                    "Envolver usuários nos testes desde o início",
                    "Implementar programa de gestão de mudanças",
                    "Realizar testes de compatibilidade abrangentes",
                    "Implementar redundância de infraestrutura",
                    "Estabelecer acordos de nível de serviço",
                    "Utilizar técnicas de estimativa mais precisas",
                    "Implementar processo de validação de requisitos",
                    "Estabelecer plano de comunicação eficaz"
                ]),
                "contingencia": random.choice([
                    "Acionar fornecedores alternativos",
                    "Redistribuir tarefas entre a equipe",
                    "Contratar consultoria especializada",
                    "Implementar soluções de contorno",
                    "Ativar plano de recuperação de desastres",
                    "Terceirizar atividades específicas",
                    "Escalar infraestrutura",
                    "Revisar e ajustar requisitos",
                    "Intensificar treinamento dos usuários",
                    "Limitar funcionalidades em plataformas específicas",
                    "Ativar ambiente de contingência",
                    "Assumir controle interno das dependências",
                    "Revisar e ajustar cronograma e orçamento",
                    "Priorizar requisitos essenciais",
                    "Escalar problemas para a alta gestão"
                ])
            })
        
        # Gerar riscos ocorridos
        riscos_ocorridos = []
        if random.random() < 0.4:  # 40% de chance de ter riscos ocorridos
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
        
        # Gerar tarefas críticas e atrasadas
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
        
        # Motivo do atraso
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
        
        # Compilar informações do projeto
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
            "riscos_ocorridos": riscos_ocorridos
        }
        
        projetos.append(projeto)
    
    # Salvar dataset em formato JSON
    with open(os.path.join(output_dir, "projetos.json"), 'w', encoding='utf-8') as f:
        json.dump(projetos, f, ensure_ascii=False, indent=2)
    
    # Salvar dataset em formato CSV (apenas dados principais)
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
    
    # Gerar arquivos de status para cada projeto
    os.makedirs(os.path.join(output_dir, "status_files"), exist_ok=True)
    
    for projeto in projetos:
        # Arquivo de status de cronograma
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
        
        # Arquivo de status de custos
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
                percentual = valor / projeto['custo_real_atual'] * 100
                f.write(f"- {categoria}: R$ {valor:.2f} ({percentual:.1f}%)\n")
        
        # Arquivo de status de escopo
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
        
        # Arquivo de status de riscos
        with open(os.path.join(output_dir, "status_files", f"{projeto['id']}_riscos.txt"), 'w', encoding='utf-8') as f:
            f.write(f"RELATÓRIO DE STATUS DE RISCOS\n")
            f.write(f"Projeto: {projeto['nome']} ({projeto['id']})\n")
            f.write(f"Data: {datetime.now().strftime('%d/%m/%Y')}\n")
            f.write(f"Gerente: {projeto['gerente']}\n\n")
            
            f.write(f"Riscos identificados:\n")
            for risco in projeto['riscos']:
                f.write(f"- {risco['id']}: {risco['descricao']}\n")
                f.write(f"  Probabilidade: {risco['probabilidade']}/5, Impacto: {risco['impacto']}/5, Nível: {risco['nivel']}\n")
                f.write(f"  Mitigação: {risco['mitigacao']}\n")
                f.write(f"  Contingência: {risco['contingencia']}\n\n")
            
            f.write(f"Riscos ocorridos:\n")
            for risco in projeto['riscos_ocorridos']:
                f.write(f"- {risco['id']} (ocorrido em {risco['data']})\n")
                f.write(f"  Impacto real: {risco['impacto_real']}\n")
                f.write(f"  Ações tomadas: {risco['acoes_tomadas']}\n\n")
    
    print(f"Dataset gerado com sucesso! Arquivos salvos em {output_dir}")
    return projetos

if __name__ == "__main__":
    # Gerar dataset com 1000 projetos
    gerar_dataset(num_projetos=1000)
