from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import Settings
from app.services.agents import get_agent_by_slug, list_active_agents, build_widget_assistant_config
from app.api.knowledge import router as knowledge_router
from app.api.chat import router as chat_router
# from app.api.kb import router as kb_router
from app.config import settings

app = FastAPI(title="Multi Agent System")

templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/")
async def home(request: Request):
    agents = list_active_agents()

    return templates.TemplateResponse(
        request=request,
        name="home.html",
        context={
            "request": request,
            "agents": agents
        }
    )


@app.get("/a/{slug}")
async def agent_page(request: Request, slug: str):
    agent = get_agent_by_slug(slug)

    if not agent:
        return {"error": "Agent not found"}

    widget_assistant_json = build_widget_assistant_config(agent)

    return templates.TemplateResponse(
    request=request,
    name="order.html",
    context={
        "request": request,
        "agent": agent,
        "widget_assistant_json": widget_assistant_json,
        "vapi_public_key": settings.VAPI_PUBLIC_KEY,
        "vapi_assistant_id": settings.VAPI_ASSISTANT_ID,
    }
)


@app.get("/health")
async def health():
    return {"ok": True}


app.include_router(knowledge_router, prefix="/knowledge", tags=["knowledge"])
app.include_router(chat_router, prefix="/chat", tags=["chat"])
