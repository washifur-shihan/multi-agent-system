# AI Restaurant Ordering System

An AI-powered restaurant ordering system built with FastAPI, Supabase, OpenAI, and Vapi. Customers can choose a restaurant, chat with an AI ordering assistant, or use the Vapi voice widget to ask about menu items and place orders.

Live demo: https://order-system-vapi-fastapi.onrender.com/

## Features

- Multi-restaurant ordering flow
- Restaurant pages at `/r/{slug}`
- Chat-based ordering through a FastAPI endpoint
- Voice ordering through the embedded Vapi widget
- Restaurant-specific assistant prompts
- Menu retrieval with OpenAI embeddings and Supabase vector search
- PDF menu upload and background ingestion
- Conversation memory and draft order extraction

## Tech Stack

Backend:

- FastAPI
- Python
- Supabase
- OpenAI
- Vapi

Frontend:

- Jinja templates
- HTML
- CSS
- JavaScript Fetch API

Data and AI:

- OpenAI embeddings
- Supabase PostgreSQL and Storage
- pgvector search
- Retrieval-augmented generation
- PDF menu processing with `pypdf`

## Project Structure

```text
app/
  api/             FastAPI route modules
  db/              Supabase client setup
  models/          Request/response schemas
  services/        Business logic, retrieval, LLM, orders, PDF ingestion
  static/          CSS assets
  templates/       Jinja HTML templates
  config.py        Environment-based settings
  main.py          FastAPI application entry point
requirements.txt
README.md
```

## Local Setup

1. Clone the repository and enter the project directory.

```bash
git clone <repo-url>
cd order-system-vapi
```

2. Create and activate a virtual environment.

```bash
python -m venv venv
```

Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source venv/bin/activate
```

3. Install dependencies.

```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root.

```env
SUPABASE_URL=your-supabase-url
SUPABASE_SERVICE_ROLE_KEY=your-supabase-service-role-key
VAPI_API_KEY=your-vapi-api-key
ELEVENLABS_API_KEY=your-elevenlabs-api-key
OPENAI_API_KEY=your-openai-api-key
```

5. Run the development server.

```bash
uvicorn app.main:app --reload
```

Open the app at:

```text
http://127.0.0.1:8000
```

## Main Routes

- `GET /` - restaurant selection page
- `GET /r/{slug}` - restaurant ordering page
- `POST /chat/` - chat with the AI assistant
- `POST /menu/upload/{restaurant_id}` - upload and ingest a PDF menu
- `POST /kb/{restaurant_slug}/search` - retrieve menu knowledge for a restaurant
- `GET /orders/` - orders route health check
- `GET /health` - application health check
- `GET /docs` - FastAPI Swagger documentation

## Supabase Requirements

The application expects Supabase to provide:

- A `menu-files` storage bucket for uploaded PDF menus
- Tables for `restaurants`, `menu_documents`, `menu_chunks`, `customers`, `conversations`, `messages`, and `orders`
- A vector search RPC function named `match_menu_chunks`

Restaurant records should include fields used by the app, such as `id`, `name`, `slug`, `welcome_message`, `prompt_instructions`, `voice_provider`, `voice_id`, and `vapi_knowledge_base_id`.

## How It Works

1. A customer selects a restaurant from the home page.
2. The restaurant page loads a restaurant-specific chat and voice assistant.
3. Chat messages are sent to `/chat/`.
4. The backend retrieves matching menu chunks from Supabase.
5. OpenAI generates a grounded response using the retrieved menu context.
6. The conversation is saved, and draft order items are extracted when possible.

## Deployment

This project is currently hosted on Render and uses Supabase for database and file storage.

Production URL:

```text
https://order-system-vapi-fastapi.onrender.com/
```

## Future Improvements

- Full checkout flow with cart review and payment support
- Admin dashboard for restaurant owners
- Real-time voice call transcript UI
- Better speech-to-text normalization for order items
- Mobile-friendly refinements

## License

Copyright (c) 2026 Washifur Rahman. All rights reserved.
