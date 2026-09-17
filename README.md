# 🖥️ AI IT Helpdesk Agent (Use Case #4)

> **Agent + RAG + Tool Calling Engine for IT Diagnostics & Support Automation**

The **AI IT Helpdesk Agent** is an autonomous assistant designed to diagnose common technical issues, retrieve troubleshooting procedures from a RAG knowledge base, run system health checks, manage support tickets, and perform automated password resets.

---

## 🌟 Key Features

1. **🧠 RAG Knowledge Base Engine (`src/rag_engine.py`)**
   - In-memory TF-IDF + Cosine Similarity vector search retriever.
   - Pre-loaded with Standard Operating Procedures (SOPs) for VPN disconnection, Windows BSOD, Wi-Fi errors, Outlook syncing, Account lockouts, RAM/CPU bottlenecks, Printer spooler reset, and Admin privileges.
   - Real-time article publishing & vector re-indexing.

2. **🛠️ IT Tool Execution Suite (`src/tools.py`)**
   - `search_knowledge_base`: Retrieves SOPs with relevance scores and citations.
   - `run_system_diagnostic`: Simulates live diagnostics for network latency, DNS resolution, physical RAM, and disk storage.
   - `create_it_ticket`: Generates tickets with Priority (Low/Medium/High/Critical), category, and tracking ID (`INC-xxxx`).
   - `get_ticket_status`: Queries existing ticket lifecycle status and technician notes.
   - `trigger_password_reset`: Initiates automated account unlock & verification token dispatch.

3. **🤖 Diagnostic Agent Core (`src/agent.py`)**
   - ReAct reasoning loop.
   - Formulates step-by-step diagnostic solution reports complete with root cause analysis, action plans, tool outputs, citations, and ticket dispatch notices.

4. **💬 Multi-Tab Streamlit Web App (`app.py`)**
   - **AI Diagnostic Chat**: Interactive chat interface displaying live tool execution traces.
   - **Knowledge Base Explorer**: Search, browse, and add new SOP articles.
   - **IT Ticket Center**: Monitor, filter, and update active tickets.
   - **Diagnostic Sandbox**: Run on-demand diagnostic scans.

5. **⚡ Command Line Interface (`cli.py`)**
   - Interactive terminal chat or single-shot command line queries.

---

## 📂 Project Structure

```
ai_it_helpdesk_agent/
├── app.py                   # Streamlit Web Application Interface
├── cli.py                   # Command Line Interface (CLI)
├── main.py                  # Application Entrypoint Launcher
├── run_tests.py             # Unit Test Runner
├── requirements.txt         # Python Dependencies
├── README.md                # Project Documentation
├── create_zip.py            # Automated Zip Archive Generator
├── data/
│   ├── kb_articles.json     # Knowledge Base Articles & SOP Database
│   └── tickets.json         # Support Ticket Database
├── src/
│   ├── __init__.py
│   ├── agent.py             # ReAct Agent Core Engine
│   ├── rag_engine.py        # RAG Knowledge Base Retriever
│   ├── tools.py             # Diagnostic & Ticketing Tools Suite
│   └── llm.py               # Flexible LLM Client (OpenAI/Gemini/Local Fallback)
└── tests/
    └── test_agent.py        # Unit Test Suite
```

---

## 🚀 Quick Start Guide

### 1. Installation
Clone or unpack the project folder and install dependencies:
```bash
pip install -r requirements.txt
```

### 2. Run Web Application
Launch the interactive Streamlit Dashboard:
```bash
python main.py
# OR
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

### 3. Run Command Line Interface (CLI)
For quick terminal queries:
```bash
python main.py cli --query "My VPN keeps dropping connection"
```
Or start interactive CLI:
```bash
python cli.py
```

### 4. Run Test Suite
Run the 5 automated unit tests:
```bash
python run_tests.py
```

---

## ⚙️ Configuration & LLM Providers

The agent operates seamlessly in **Smart Local Fallback Mode** without requiring any paid API key. 
To enable online OpenAI or Gemini LLM generation, set your environment variable:

```bash
# Optional: Set OpenAI API Key
export OPENAI_API_KEY="your-openai-key"

# Optional: Set Gemini API Key
export GEMINI_API_KEY="your-gemini-key"
```

---

## 📊 Evaluation & Capabilities Matrix

| Requirement | Implementation | Status |
| :--- | :--- | :--- |
| **Agent Logic** | ReAct reasoning loop with step-by-step diagnostic output | ✅ Implemented |
| **RAG Knowledge Base** | TF-IDF / Cosine Similarity semantic search & dynamic indexing | ✅ Implemented |
| **Tool Calling** | Auto-invocation of Ping/RAM/Disk tools, Ticket Manager, Password Reset | ✅ Implemented |
| **Web Interface** | Multi-tab Streamlit dashboard with chat history & trace logs | ✅ Implemented |
| **Packaging** | Zipped distribution package ready for submission | ✅ Implemented |
