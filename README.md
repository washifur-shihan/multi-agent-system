# 🧠 Multi-Agent System (Finance • HR • Sales • Operations)

A production-ready multi-agent AI system built with FastAPI, Supabase, OpenAI, and Vapi. It routes user queries to specialized department agents through a Master Agent and supports chat, voice, PDF knowledge ingestion, embeddings, and retrieval-augmented generation.

## 🚀 Features

### 🧠 Multi-Agent Architecture

- Master Agent routes user queries to the right department
- Finance Agent handles payroll, invoices, expenses, budgets, and reimbursements
- HR Agent handles hiring, leave, attendance, employee policies, and benefits
- Sales Agent handles leads, CRM, quotes, follow-ups, and deals
- Operations Agent handles logistics, SOPs, vendors, inventory, and daily operations

### 🔍 Retrieval-Augmented Generation (RAG)

- Upload PDFs per agent
- Automatic PDF text extraction, chunking, and embeddings
- Semantic search through Supabase Postgres + pgvector
- Grounded LLM responses using department-specific knowledge

### 🎙️ Voice Integration (Vapi)

- Real-time voice assistant support
- Vapi calls the backend `/chat/` endpoint
- Dynamic routing through the Master Agent
- Response mapping through the `reply` field

### 💬 Chat UI

- Clean Jinja2 frontend
- Agent-specific chat pages
- Session-based conversation memory
- Shared chat endpoint for web and voice channels

## 🏗️ Tech Stack

- Backend: FastAPI
- Database: Supabase Postgres + pgvector
- LLM: OpenAI GPT-4o-mini
- Voice: Vapi
- Frontend: Jinja2 + vanilla JavaScript
- Storage: Supabase Storage
- PDF Processing: pypdf

## 📂 Project Structure

```text
app/
├── api/
│   ├── chat.py          # Main chat endpoint for Vapi + UI
│   ├── knowledge.py     # PDF upload endpoint
│   ├── orders.py        # Orders route module
│   ├── vapi.py          # Vapi route module
│   └── vapi_dynamic.py  # Dynamic Vapi route module
│
├── services/
│   ├── agents.py        # Agent lookup, prompts, and Vapi widget config
│   ├── router.py        # Master routing logic
│   ├── retrieval.py     # Vector search + conversation retrieval
│   ├── llm_chat.py      # LLM response generation
│   ├── memory.py        # Customers, conversations, and messages
│   └── pdf_ingest.py    # PDF → chunks → embeddings
│
├── templates/
│   ├── base.html
│   ├── home.html
│   └── order.html       # Agent chat UI
│
├── static/
│   └── css/style.css
│
├── db/
│   └── supabase.py
│
├── config.py
└── main.py
```

## ⚙️ Setup

### 1. Clone and install

```bash
git clone <your-repo>
cd multi-agent-system
python -m venv venv
```

Activate the virtual environment.

Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

Windows CMD:

```bat
venv\Scripts\activate
```

macOS/Linux:

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### 2. Environment variables

Create a `.env` file in the project root:

```env
SUPABASE_URL=your_project_url
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
SUPABASE_BUCKET=knowledge-files

OPENAI_API_KEY=your_openai_key

VAPI_PUBLIC_KEY=your_public_key
VAPI_ASSISTANT_ID=your_assistant_id
```

Optional:

```env
VAPI_API_KEY=your_vapi_api_key
ELEVENLABS_API_KEY=your_elevenlabs_api_key
```

### 3. Run the server

```bash
uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

## 🗄️ Database Setup (Supabase)

The app expects Supabase tables for:

- `agents`
- `customers`
- `conversations`
- `messages`
- `knowledge_documents`
- `knowledge_chunks`

It also expects a vector search RPC function:

```text
match_knowledge_chunks(...)
```

Use a Supabase Storage bucket named:

```text
knowledge-files
```

## 🧠 How Routing Works

```text
User input
   ↓
Master Agent (router.py)
   ↓
Select department agent
   ↓
Retrieve relevant knowledge from Supabase vector search
   ↓
Generate response with OpenAI
   ↓
Save conversation memory
```

Available department routes:

| Query type | Routed agent |
| --- | --- |
| Payroll, invoices, expenses, reimbursements | Finance |
| Hiring, leave, attendance, policies, benefits | HR |
| Leads, CRM, pricing, follow-ups, deals | Sales |
| Logistics, SOPs, vendors, inventory | Operations |

## 🎙️ Vapi Integration

Configure a Vapi tool with:

```text
Method: POST
URL: https://your-domain.com/chat/
```

Request body:

```json
{
  "customer_key": "voice-user",
  "message": "{{transcript}}",
  "channel": "voice",
  "agent_slug": "master"
}
```

Response mapping:

```text
reply
```

## 📄 Knowledge Upload

Upload PDFs for an agent:

```text
POST /knowledge/upload/{agent_id}
```

Ingestion flow:

```text
PDF → text extraction → chunks → embeddings → Supabase vector storage
```

## 🌐 Main Routes

- `GET /` - agent selection page
- `GET /a/{slug}` - agent chat page
- `POST /chat/` - chat endpoint for UI and Vapi
- `POST /knowledge/upload/{agent_id}` - upload and ingest a PDF for an agent
- `GET /health` - health check
- `GET /docs` - FastAPI Swagger documentation

## 🧪 Example Queries

| Input | Expected agent |
| --- | --- |
| "I need help with payroll" | Finance |
| "How many leave days do I have?" | HR |
| "Follow up with this lead" | Sales |
| "Inventory is low" | Operations |


## 🔥 Future Improvements

- Multi-step agent workflows
- Agent-to-agent communication
- Long-term memory across sessions
- Streaming responses
- Authentication and user accounts
- Dashboard analytics

## 👨‍💻 Author

Built by Washifur Rahman.

## License

Copyright (c) 2026 Washifur Rahman. All rights reserved.
