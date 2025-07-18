"""
risk_agent_updated.py: Risks Agent with RAG+LLM integration for project management.
"""
from rag_system_pmbok import PMBOKRAGSystem
from openai import OpenAI

class RisksAgent:
    def __init__(self, knowledge_base_path, llm_api_key):
        self.rag = PMBOKRAGSystem(knowledge_base_path)
        self.llm = OpenAI(api_key=llm_api_key)

    def analyze_risks(self, risks_status_file):
        # Retrieve relevant knowledge
        with open(risks_status_file, 'r', encoding='utf-8') as f:
            risks_data = f.read()
        context = self.rag.retrieve_relevant(risks_data, topic='risks')
        # Compose prompt for LLM
        prompt = f"""
You are a project management expert. Analyze the following project risks and responses. Use the provided PMBOK knowledge context to recommend mitigation strategies and control actions.

Risks Status:
{risks_data}

Relevant PMBOK Knowledge:
{context}

Provide a detailed analysis and actionable recommendations.
"""
        response = self.llm.chat_completion(prompt)
        return response

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 4:
        print("Usage: python risk_agent_updated.py <knowledge_base_path> <llm_api_key> <risks_status_file>")
        sys.exit(1)
    agent = RisksAgent(sys.argv[1], sys.argv[2])
    result = agent.analyze_risks(sys.argv[3])
    print(result)
