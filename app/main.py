from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import settings
from app.services.agents import (
    get_agent_by_slug,
    list_active_agents,
    build_widget_assistant_config,
)
from app.services.retrieval import list_knowledge_documents
from app.api.knowledge import router as knowledge_router
from app.api.chat import router as chat_router
from app.api.vapi import router as vapi_router

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Aurora Agent AI — Personal Multi-Agent Intelligence System with RAG, Smart Routing, and Voice.",
)

templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")


def _system_status() -> dict:
    return {
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "openai_connected": settings.has_openai,
        "supabase_connected": settings.has_supabase,
        "vapi_connected": settings.has_vapi,
        "model": settings.OPENAI_MODEL,
    }


@app.get("/")
async def home(request: Request):
    agents = list_active_agents()
    return templates.TemplateResponse(
        request=request,
        name="home.html",
        context={
            "request": request,
            "agents": agents,
            "system": _system_status(),
        },
    )


@app.get("/a/{slug}")
async def agent_page(request: Request, slug: str):
    agent = get_agent_by_slug(slug)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    all_agents = list_active_agents()
    documents = list_knowledge_documents(agent["id"])
    widget_assistant_json = build_widget_assistant_config(agent)

    return templates.TemplateResponse(
        request=request,
        name="agent.html",
        context={
            "request": request,
            "agent": agent,
            "all_agents": all_agents,
            "documents": documents,
            "widget_assistant_json": widget_assistant_json,
            "vapi_public_key": settings.VAPI_PUBLIC_KEY or "",
            "vapi_assistant_id": settings.VAPI_ASSISTANT_ID or "",
            "system": _system_status(),
        },
    )


@app.get("/health")
async def health():
    return {"ok": True, **_system_status()}


app.include_router(knowledge_router, prefix="/knowledge", tags=["knowledge"])
app.include_router(chat_router, prefix="/chat", tags=["chat"])
app.include_router(vapi_router, prefix="/vapi", tags=["vapi"])
