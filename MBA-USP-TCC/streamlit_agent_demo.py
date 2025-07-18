
import streamlit as st
import os
from workflow_updated import ProjectManagementWorkflow
from scope_agent_updated import ScopeAgent
from risk_agent_updated import RisksAgent

st.title('Single-Agent Project Management Demo')


AGENT_OPTIONS = {
    'Scope Agent (RAG+LLM)': 'scope',
    'Time (Schedule) Agent': 'schedule',
    'Costs Agent': 'cost',
    'Risks Agent (RAG+LLM)': 'risk'
}

agent_choice = st.selectbox('Select the agent to run:', list(AGENT_OPTIONS.keys()))

uploaded_file = st.file_uploader('Upload the corresponding status file (TXT)', type='txt')


if uploaded_file and st.button('Run Agent'):
    # Prepare status_files directory
    status_dir = os.path.join(os.path.dirname(__file__), 'dataset', 'status_files')
    os.makedirs(status_dir, exist_ok=True)
    agent_file_map = {
        'scope': 'PROJ-0001_escopo.txt',
        'schedule': 'PROJ-0001_cronograma.txt',
        'cost': 'PROJ-0001_custos.txt',
        'risk': 'PROJ-0001_riscos.txt'
    }
    agent_key = AGENT_OPTIONS[agent_choice]
    file_path = os.path.join(status_dir, agent_file_map[agent_key])
    with open(file_path, 'wb') as f:
        f.write(uploaded_file.read())

    # Use RAG+LLM agent for Scope and Risks
    if agent_key == 'scope':
        knowledge_base_path = os.path.join(os.path.dirname(__file__), '..', 'knowledge_base')
        api_key = os.environ.get('OPENAI_API_KEY', '')
        agent = ScopeAgent(knowledge_base_path, api_key)
        result = agent.analyze_scope(file_path)
    elif agent_key == 'risk':
        knowledge_base_path = os.path.join(os.path.dirname(__file__), '..', 'knowledge_base')
        api_key = os.environ.get('OPENAI_API_KEY', '')
        agent = RisksAgent(knowledge_base_path, api_key)
        result = agent.analyze_risks(file_path)
    else:
        # Use CrewAI workflow for schedule/cost
        workflow = ProjectManagementWorkflow(process_type='sequential')
        agent_task = workflow.tasks[agent_key]
        result = agent_task.run()

    st.subheader('Agent Output')
    st.code(result if isinstance(result, str) else '\n\n'.join(result))

st.markdown('---')
st.markdown('**How to run locally:**')
st.code('streamlit run streamlit_agent_demo.py')
st.markdown('**How to run on Google Colab:**')
st.markdown('1. Upload this script and your code files to Colab.')
st.markdown('2. Run `!pip install streamlit` in a Colab cell.')
st.markdown('3. Run `!streamlit run streamlit_agent_demo.py --server.enableCORS false --server.enableXsrfProtection false` and use the public URL provided by Colab.')
