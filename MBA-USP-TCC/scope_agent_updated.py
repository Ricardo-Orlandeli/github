"""
scope_agent_updated.py: Scope Agent with RAG+LLM integration for project management.
"""
from rag_system_pmbok import PMBOKRAGSystem
from openai import OpenAI

class ScopeAgent:
    def __init__(self, knowledge_base_path, llm_api_key):
        self.rag = PMBOKRAGSystem(knowledge_base_path)
        self.llm = OpenAI(api_key=llm_api_key)

    def analyze_scope(self, scope_status_file):
        # Retrieve relevant knowledge
        with open(scope_status_file, 'r', encoding='utf-8') as f:
            scope_data = f.read()
        context = self.rag.retrieve_relevant(scope_data, topic='scope')
        # Compose prompt for LLM
        prompt = f"""
You are a project management expert. Analyze the following project scope status and changes. Use the provided PMBOK knowledge context to recommend control actions to prevent or address scope creep.

Scope Status:
{scope_data}

Relevant PMBOK Knowledge:
{context}

Provide a detailed analysis and actionable recommendations.
"""
        response = self.llm.chat_completion(prompt)
        return response

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 4:
        print("Usage: python scope_agent_updated.py <knowledge_base_path> <llm_api_key> <scope_status_file>")
        sys.exit(1)
    agent = ScopeAgent(sys.argv[1], sys.argv[2])
    result = agent.analyze_scope(sys.argv[3])
    print(result)
