# ✦ Aurora Agent AI

**Aurora Agent AI** is a full-stack multi-agent intelligence system built with **FastAPI**, **Jinja2**, **Mistral AI (Free Tier)**, **Supabase + pgvector**, and **Vapi Voice**. It routes user queries through **Aurora Master** to specialized domain agents (**Aurora Finance**, **Aurora HR**, **Aurora Sales**, and **Aurora Operations**) with Retrieval-Augmented Generation (RAG), PDF knowledge ingestion, and unified Web + Voice conversation memory — all served from a single command.

---

## ✨ Key Capabilities

### 🧠 Neural Multi-Agent Orchestration
- **Aurora Master (`master`)**: Central orchestrator that analyzes intent and routes requests to the right specialist or handles general inquiries.
- **Aurora Finance (`finance`)**: Payroll schedules, vendor invoices, expense reimbursements, budgets, tax compliance, and financial reporting.
- **Aurora HR (`hr`)**: Talent acquisition, PTO & leave balances, attendance, onboarding checklists, benefits, and workplace policies.
- **Aurora Sales (`sales`)**: Lead qualification, CRM pipeline management, custom pricing quotes, proposals, follow-ups, and deal closing.
- **Aurora Operations (`operations`)**: Supply chain logistics, warehouse inventory, vendor SLAs, SOPs, and fulfillment workflows.

### ⚡ Free-Tier Mistral AI + Automatic Multi-Provider Failover
- **Mistral AI (Primary — Free Tier)**: Natively configured for `mistral-small-latest` (chat) and `mistral-embed` (vector embeddings) via Mistral's OpenAI-compatible API (`https://api.mistral.ai/v1`).
- **Automatic Dimension Alignment**: Pads/normalizes `mistral-embed` vectors to `1536` dimensions so your Supabase `pgvector` tables work identically whether you use Mistral AI or OpenAI.
- **Multi-Provider Failover**: Supports `MISTRAL_API_KEY` (first priority), `GROQ_API_KEY` (free tier `llama-3.3-70b-versatile`), and `OPENAI_API_KEY` (`gpt-4o-mini`).

### 📚 Retrieval-Augmented Generation (RAG)
- **Built-in UI & API PDF Upload**: Upload domain PDFs directly from each agent's sidebar in the Jinja2 UI (`POST /knowledge/upload/{agent_slug}`).
- **Smart Chunking & Embeddings**: Extracts PDF text, splits along natural paragraph/sentence boundaries, and generates vector embeddings.
- **Resilient Dual-Mode Storage**: Uses **Supabase Postgres + pgvector** when configured, and automatically falls back to an **in-memory vector & session store** for instant local development without external dependencies.

### 🎨 Unified Jinja2 Command Center (Zero Separate Frontend Server)
- Everything runs with **one command** (`uvicorn app.main:app --reload`).
- Modern Aurora dark glassmorphism UI with:
  - One-click **Agent Switcher** & **Starter Prompt Chips**
  - Live **Routing Telemetry Badges** & **RAG Chunk Counters**
  - Interactive **PDF Knowledge Base Uploader**
  - **Session Reset** (`POST /chat/reset`) & **Conversation History** (`GET /chat/history`)

---

## ⚡ Quick Start (Single Command)

### 1. Create and activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Get your Free Mistral AI Key & configure `.env`

1. Go to **[https://console.mistral.ai/api-keys/](https://console.mistral.ai/api-keys/)** and create a free API key under the free **Experiment** plan (no credit card needed).
2. Copy `.env.example` to `.env` and paste your key:

```bash
cp .env.example .env
```

```env
MISTRAL_API_KEY=your_mistral_api_key_here
MISTRAL_MODEL=mistral-small-latest
MISTRAL_EMBEDDING_MODEL=mistral-embed
```

### 3. Start Aurora Agent AI

```bash
uvicorn app.main:app --reload
```

Open **[http://127.0.0.1:8000](http://127.0.0.1:8000)** in your browser.

---

## 👨‍💻 Author

Designed & built by **Washifur Rahman**.
