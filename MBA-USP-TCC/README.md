
# MBA-USP-TCC: Multi-Agent AI System for Project Management

This project implements a multi-agent AI system for project management, leveraging CrewAI workflows to orchestrate specialized agents. The system provides actionable insights, recommendations, and consolidated reports to project managers, following PMBOK best practices.

---

## System Architecture

**Agents:**
- **Scope Agent:** Analyzes project scope, identifies changes, and recommends actions to control scope creep.
- **Time (Schedule) Agent:** Monitors project schedule, calculates SPI, and suggests actions to keep the project on track.
- **Costs Agent:** Monitors project costs, calculates CPI, and recommends actions to control budget deviations.
- **Risks Agent:** Identifies and analyzes project risks, evaluates responses, and suggests mitigation strategies.
- **Project Manager Agent:** Orchestrates the workflow, consolidates recommendations from all agents, and produces an executive report with prioritized actions.

**Workflow:**
- Agents analyze their respective status files and generate detailed reports.
- The Project Manager Agent (in hierarchical mode) consolidates all recommendations and produces an integrated action plan.
- CrewAI is used for agent orchestration and workflow management.

---

## Requirements

- Python 3.8+
- pip (Python package manager)
- CrewAI (`pip install crewai`)
- Other dependencies listed in `requirements.txt`

---

## Local Setup & Execution (Runbook)

### 1. Clone the Repository
```
git clone https://github.com/Ricardo-Orlandeli/AI-MultiAgents.git
cd AI-MultiAgents/tcc_multiagentes_prototipo
```

### 2. Install Dependencies
```
pip install -r requirements.txt
pip install crewai
```

### 3. Prepare Dataset
- Ensure the folder `dataset/status_files/` exists.
- Add status files for your project (e.g., `PROJ-0001_cronograma.txt`, `PROJ-0001_custos.txt`, `PROJ-0001_escopo.txt`, `PROJ-0001_riscos.txt`).
- You can generate synthetic files using the provided script:
```
python projeto_dataset_corrigido_manus.py
```

### 4. Run the Workflow
#### Mock Mode (for demo/testing):
```
python workflow_updated.py --mock
```
#### Real Data (Sequential or Hierarchical):
```
python workflow_updated.py --process sequential
python workflow_updated.py --process hierarchical
```

### 5. Output
- Results are saved in the `results/` folder as timestamped text files.

---

## Web Demo (Optional)

This system is designed for local execution. To demo via web, you can:

1. **Use Google Colab or Jupyter Notebook:**
   - Upload the code and dataset files.
   - Run the workflow in a notebook cell.
   - Display results directly in the notebook.

2. **Deploy a Simple Web App (Advanced):**
   - Use Flask or FastAPI to create a web interface.
   - Expose endpoints to upload status files and trigger the workflow.
   - Display results in the browser.
   - (This requires additional development; ask for a template if needed.)

---


## Agent Roles & Responsibilities (All RAG+LLM Enabled)

All agents now use Retrieval Augmented Generation (RAG) and interface with an LLM (e.g., OpenAI) for advanced recommendations:

| Agent              | Responsibility                                                      |
|--------------------|---------------------------------------------------------------------|
| Scope Agent        | Analyze scope status, changes, and recommend control actions (RAG+LLM) |
| Time Agent         | Analyze schedule, SPI, and recommend actions to stay on track (RAG+LLM) |
| Costs Agent        | Analyze costs, CPI, and recommend actions to control budget (RAG+LLM) |
| Risks Agent        | Analyze risks, responses, and recommend mitigation strategies (RAG+LLM) |
| Project Manager    | Orchestrate, consolidate, and prioritize all agent recommendations  |

---

### Example: Running a RAG+LLM Agent Directly

```python
from scope_agent_updated import ScopeAgent
agent = ScopeAgent('knowledge_base/', 'YOUR_OPENAI_API_KEY')
result = agent.analyze_scope('dataset/status_files/PROJ-0001_escopo.txt')
print(result)
```

---



## Step-by-Step: Run a Single-Agent Pilot in Google Colab with Streamlit

You can also demo any individual agent using Streamlit in Google Colab. Follow these steps:

### 1. Upload Your Project Files to Colab
- Upload `streamlit_agent_demo.py`, `workflow_updated.py`, and all required code files to your Colab environment.

### 2. Install All Requirements
In a Colab cell, run:
```
!pip install -r requirements.txt
!pip install streamlit
```

### 3. Start the Streamlit App
In a Colab cell, run:
```
!streamlit run streamlit_agent_demo.py --server.enableCORS false --server.enableXsrfProtection false & npx localtunnel --port 8501
```
- This will start Streamlit and provide a public URL (from localtunnel) to access the app in your browser.

### 4. Open the Web Interface
- Click the localtunnel URL shown in the Colab output to open the Streamlit app.

### 5. Select and Test an Agent
- Choose the agent you want to test (Scope, Time, Costs, or Risks).
- Upload the corresponding status file (e.g., `PROJ-0001_escopo.txt` for Scope Agent).
- Click "Run Agent" to see the agent's analysis and recommendations.

### 6. (Optional) Generate Example Status Files
- In a Colab cell, run:
```
!python projeto_dataset_corrigido_manus.py
```
- The files will be saved in `dataset/status_files/`.

---

This approach is ideal for sharing a live demo with others or running the pilot in the cloud.

---

You can quickly test any individual agent (Scope, Time, Costs, or Risks) using the provided Streamlit web app. Follow these steps:

### 1. Install All Requirements
```
pip install -r requirements.txt
```

### 2. Launch the Streamlit App
```
streamlit run streamlit_agent_demo.py
```

### 3. Open the Web Interface
- After running the above command, your browser will open automatically (or visit the URL shown in the terminal, usually http://localhost:8501).

### 4. Select and Test an Agent
- Choose the agent you want to test (Scope, Time, Costs, or Risks).
- Upload the corresponding status file (e.g., `PROJ-0001_escopo.txt` for Scope Agent).
- Click "Run Agent" to see the agent's analysis and recommendations.

### 5. (Optional) Generate Example Status Files
- Use the script below to generate synthetic status files for testing:
```
python projeto_dataset_corrigido_manus.py
```
- The files will be saved in `dataset/status_files/`.

---

This pilot is ideal for quick demos, validation, and experimentation with each agent individually.

---
## Troubleshooting

- **pip not recognized:** Ensure Python and pip are installed and added to PATH.
- **ModuleNotFoundError:** Run `pip install -r requirements.txt` and `pip install crewai`.
- **Missing status files:** Generate or add required files in `dataset/status_files/`.

---

## Contact

For questions or demo support, contact the project maintainer or open an issue on GitHub.
