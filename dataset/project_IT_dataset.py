import pandas as pd
import random
import uuid
from datetime import datetime, timedelta
import os

# Função para gerar uma data aleatória dentro de uma faixa de anos
def random_date(start_year=2020, end_year=2025):
    start_date = datetime(start_year, 1, 1)
    end_date = datetime(end_year, 12, 31)
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    random_date = start_date + timedelta(days=random_days)
    return random_date

# Função para gerar o dataset com 11 tipos de projeto
def generate_project_dataset(num_tuples=100, output_dir=".", file_name="project_dataset"):
    # Tipos de projetos
    project_types = [
        "Data Center", "Data Migration", "Cloud IaaS", "Cloud PaaS", "Cloud SaaS", 
        "Desenvolvimento de Software Personalizado", "Infraestrutura de TI", "Aplicativo Móvel", 
        "Migração de Sistema Legado", "Cibersegurança", "Big Data e Analytics"
    ]
    
    # Definições de risco e status
    risks = ["Falha de segurança", "Problema de integração", "Atraso na entrega de fornecedor", "Problema técnico inesperado", "Escalabilidade insuficiente"]
    impacts = ["Alto", "Médio", "Baixo"]
    probabilities = ["Alta", "Média", "Baixa"]
    
    # Listas para armazenar os dados
    project_data = []
    
    for _ in range(num_tuples):
        # Tipo de projeto aleatório
        project_type = random.choice(project_types)
        
        # Gerar dados aleatórios para cada projeto
        project_id = str(uuid.uuid4())
        start_date = random_date(2020, 2023)
        end_date_planned = start_date + timedelta(days=random.randint(90, 365))
        end_date_real = end_date_planned if random.choice([True, False]) else end_date_planned + timedelta(days=random.randint(0, 60))
        completion_percentage = random.randint(0, 100)
        delay = max(0, (end_date_real - end_date_planned).days)
        delay_reason = random.choice([None, "Problema de integração de dados", "Demora na entrega de hardware", "Falhas nos testes"])
        scope_change = random.choice([True, False])
        scope_change_reason = "Aumento de capacidade de armazenamento" if scope_change else None
        initial_budget = random.randint(100000, 1000000)
        real_cost = initial_budget + random.randint(-50000, 150000)
        budget_deviation = real_cost - initial_budget
        estimated_cost = real_cost + random.randint(-20000, 50000)
        
        risk_identified = random.choice(risks)
        risk_probability = random.choice(probabilities)
        risk_impact = random.choice(impacts)
        mitigation_plan = "Reforço na segurança de dados, testes intensivos" if risk_identified == "Falha de segurança" else "Ajuste na arquitetura"
        risk_occurred = random.choice([None, "Falha de segurança", "Atraso na entrega de fornecedor"])
        real_risk_impact = "Interrupção de serviços por 2 horas" if risk_occurred == "Falha de segurança" else None
        corrective_actions = "Reforço no firewall, ajuste na arquitetura" if risk_occurred else None

        # Adicionar a tupla ao dataset
        project_data.append({
            "ID do Projeto": project_id,
            "Nome do Projeto": f"Projeto_{project_type}_{random.choice(['TechCorp', 'InovaData', 'CloudShift', 'GlobalTech'])}",
            "Tipo de Projeto": project_type,
            "Data de Início": start_date.strftime("%Y-%m-%d"),
            "Data de Término Planejada": end_date_planned.strftime("%Y-%m-%d"),
            "Data de Término Real": end_date_real.strftime("%Y-%m-%d"),
            "Percentual de Conclusão": completion_percentage,
            "Atrasos": delay,
            "Motivo dos Atrasos": delay_reason,
            "Mudança de Escopo?": "Sim" if scope_change else "Não",
            "Mudanças de Escopo": scope_change_reason,
            "Orçamento Inicial": initial_budget,
            "Custo Real até o Momento": real_cost,
            "Desvios de Orçamento": budget_deviation,
            "Estimativa de Custo para Conclusão": estimated_cost,
            "Riscos Identificados": risk_identified,
            "Probabilidade de Ocorrência": risk_probability,
            "Impacto dos Riscos": risk_impact,
            "Plano de Mitigação": mitigation_plan,
            "Riscos Ocorridos": risk_occurred,
            "Impacto Real dos Riscos": real_risk_impact,
            "Ações Corretivas": corrective_actions,
        })

    # Converter para DataFrame
    df = pd.DataFrame(project_data)
    
    # Criar diretório de saída se não existir
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Salvar em arquivos .csv e .txt
    csv_file_path = os.path.join(output_dir, f"{file_name}.csv")
    txt_file_path = os.path.join(output_dir, f"{file_name}.txt")
    
    df.to_csv(csv_file_path, index=False, sep=";")
    df.to_csv(txt_file_path, index=False, sep="\t")
    
    return df, csv_file_path, txt_file_path

# Exemplo de uso
# Gerar o dataset com 100 tuplas e salvar em arquivos
generated_data, csv_path, txt_path = generate_project_dataset(num_tuples=100, output_dir=".", file_name="project_dataset")

print(f"Arquivo CSV salvo em: {csv_path}")
print(f"Arquivo TXT salvo em: {txt_path}")
