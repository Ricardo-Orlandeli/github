from crewai import Agent, Task, Crew
from dotenv import load_dotenv
import os



# Carregar variáveis de ambiente do arquivo .env
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Criar agente
agente = Agent(
    role="Analista de Teste",
    goal="Executar uma tarefa de demonstração",
    backstory="Especialista em testes automatizados para TCCs universitários.",
    verbose=True,
    llm=llm
)

# Criar tarefa
tarefa = Task(
    description="Analise este texto e retorne um resumo.",
    expected_output="Resumo gerado com sucesso.",
    agent=agente
)

# Criar Crew
crew = Crew(
    agents=[agente],
    tasks=[tarefa],
    verbose=True
)

# Executar
resultado = crew.kickoff()
print("Resultado:", resultado)
