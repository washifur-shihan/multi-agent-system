from fastapi import APIRouter
from app.models.schemas import KnowledgeSearchRequest, VapiEventRequest
from app.services.agents import get_agent_by_slug
from app.services.retrieval import search_knowledge

router = APIRouter()


@router.post("/knowledge/search")
async def knowledge_search(payload: KnowledgeSearchRequest):
    agent = get_agent_by_slug(payload.agent_slug) or get_agent_by_slug("master")
    results = search_knowledge(agent["id"], payload.query, match_count=payload.match_count)

    documents = [
        {
            "title": f"{agent['name']} Knowledge #{i + 1}",
            "content": row["content"],
            "similarity": row.get("similarity", 0.9),
        }
        for i, row in enumerate(results)
    ]

    return {"documents": documents}


@router.post("/events")
async def vapi_events(payload: VapiEventRequest):
    return {
        "ok": True,
        "received": payload.model_dump(),
    }
