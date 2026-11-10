# ✦ Aurora Agent AI

**Aurora Agent AI** is a full-stack multi-agent intelligence system built with **FastAPI**, **Jinja2**, **OpenAI**, **Supabase + pgvector**, and **Vapi Voice**. It routes user queries through **Aurora Master** to specialized domain agents (**Aurora Finance**, **Aurora HR**, **Aurora Sales**, and **Aurora Operations**) with Retrieval-Augmented Generation (RAG), PDF knowledge ingestion, and unified Web + Voice conversation memory — all served from a single command.

---

## ✨ Key Capabilities

### 🧠 Neural Multi-Agent Orchestration
- **Aurora Master (`master`)**: Central orchestrator that analyzes intent and routes requests to the right specialist or handles general inquiries.
- **Aurora Finance (`finance`)**: Payroll schedules, vendor invoices, expense reimbursements, budgets, tax compliance, and financial reporting.
- **Aurora HR (`hr`)**: Talent acquisition, PTO & leave balances, attendance, onboarding checklists, benefits, and workplace policies.
- **Aurora Sales (`sales`)**: Lead qualification, CRM pipeline management, custom pricing quotes, proposals, follow-ups, and deal closing.
- **Aurora Operations (`operations`)**: Supply chain logistics, warehouse inventory, vendor SLAs, SOPs, and fulfillment workflows.

### 📚 Retrieval-Augmented Generation (RAG)
- **Built-in UI & API PDF Upload**: Upload domain PDFs directly from each agent's sidebar in the Jinja2 UI (`POST /knowledge/upload/{agent_slug}`).
- **Smart Chunking & Embeddings**: Extracts PDF text, splits along natural paragraph/sentence boundaries, and generates `text-embedding-3-small` vectors.
- **Resilient Dual-Mode Storage**: Uses **Supabase Postgres + pgvector** when configured, and automatically falls back to an **in-memory vector & session store** for instant local development without external dependencies.

### 🎨 Unified Jinja2 Command Center (Zero Separate Frontend Server)
- Everything runs with **one command** (`uvicorn app.main:app --reload`).
- Modern Aurora dark glassmorphism UI with:
  - One-click **Agent Switcher** & **Starter Prompt Chips**
  - Live **Routing Telemetry Badges** & **RAG Chunk Counters**
  - Interactive **PDF Knowledge Base Uploader**
  - **Session Reset** (`POST /chat/reset`) & **Conversation History** (`GET /chat/history`)

### 🎙️ Real-Time Voice Integration (Vapi)
- Shared `/chat/` endpoint handles both Web UI chat and Vapi voice transcripts.
- Embedded Vapi voice call button automatically activates when `VAPI_PUBLIC_KEY` and `VAPI_ASSISTANT_ID` are set in `.env`.

---

## 📂 Project Structure

```text
aurora-agent-ai/
├── app/
│   ├── api/
│   │   ├── chat.py          # Unified Web + Vapi chat, history, and session reset endpoints
│   │   ├── knowledge.py     # PDF knowledge upload and document listing endpoints
│   │   └── vapi.py          # Vapi knowledge search & webhook event endpoints
│   ├── db/
│   │   └── supabase.py      # Resilient Supabase client initialization
│   ├── models/
│   │   └── schemas.py       # Pydantic request/response schemas
│   ├── services/
│   │   ├── agents.py        # Aurora agent definitions, prompts, and Supabase lookup
│   │   ├── llm.py           # OpenAI embeddings with deterministic local fallback
│   │   ├── llm_chat.py      # Grounded LLM synthesis with RAG & routing context
│   │   ├── memory.py        # Customer, conversation & message persistence (Supabase + local fallback)
│   │   ├── pdf_ingest.py    # PDF extraction → smart chunking → vector embeddings
│   │   ├── retrieval.py     # pgvector RPC search + local cosine similarity fallback
│   │   └── router.py        # Word-boundary & phrase-weighted intent router
│   ├── static/
│   │   └── css/style.css    # Aurora dark glassmorphism stylesheet
│   ├── templates/
│   │   ├── base.html        # Master layout with live system status indicators
│   │   ├── home.html        # Command Center agent grid & architecture overview
│   │   └── agent.html       # Interactive Agent Workspace (Chat + RAG PDF Upload + Voice)
│   ├── utils/
│   │   └── text.py          # Text normalization and boundary-aware chunking
│   ├── config.py            # Environment settings and capability detection
│   └── main.py              # FastAPI application entrypoint
├── .env.example             # Sample environment configuration
├── schema.sql               # Complete Supabase Postgres + pgvector SQL setup & seed
├── requirements.txt         # Python dependencies
└── README.md
```

---

## ⚡ Quick Start (Single Command)

### 1. Create and activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure environment variables (optional for local demo)

```bash
cp .env.example .env
```

Edit `.env` with your keys:
- `OPENAI_API_KEY`: Enables live `gpt-4o-mini` completions and `text-embedding-3-small` vectors.
- `SUPABASE_URL` & `SUPABASE_SERVICE_ROLE_KEY`: Enables persistent Postgres + `pgvector` storage (run `schema.sql` in the Supabase SQL Editor).
- `VAPI_PUBLIC_KEY` & `VAPI_ASSISTANT_ID`: Enables the floating real-time voice widget.

*(Note: Aurora Agent AI also boots and runs cleanly in local memory mode even before `.env` is configured!)*

### 3. Start Aurora Agent AI

```bash
uvicorn app.main:app --reload
```

Open **[http://127.0.0.1:8000](http://127.0.0.1:8000)** in your browser.

---

## 🌐 Main Routes

| Route | Method | Description |
| :--- | :--- | :--- |
| `/` | `GET` | Aurora Command Center (agent overview & status) |
| `/a/{slug}` | `GET` | Agent Workspace (`master`, `finance`, `hr`, `sales`, `operations`) |
| `/chat/` | `POST` | Main chat & voice routing endpoint |
| `/chat/history` | `GET` | Fetch current session message history |
| `/chat/reset` | `POST` | Reset active conversation session |
| `/knowledge/{agent}` | `GET` | List indexed PDF documents for an agent |
| `/knowledge/upload/{agent}` | `POST` | Upload & embed a PDF into an agent's knowledge base |
| `/health` | `GET` | Health & integration status check |
| `/docs` | `GET` | Interactive FastAPI Swagger UI |

---

## 👨‍💻 Author

Designed & built by **Washifur Rahman**.
