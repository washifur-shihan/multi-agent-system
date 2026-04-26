from fastapi import APIRouter
from pydantic import BaseModel
from app.services.retrieval import search_menu

router = APIRouter()


class KnowledgeSearchRequest(BaseModel):
    query: str


@router.post("/knowledge/search")
async def knowledge_search(payload: KnowledgeSearchRequest):
    results = search_menu(payload.query, match_count=5)

    documents = [
        {
            "title": f"Menu chunk {i + 1}",
            "content": row["content"],
            "metadata": row.get("metadata", {})
        }
        for i, row in enumerate(results)
    ]

    return {"documents": documents}


class VapiEventRequest(BaseModel):
    type: str | None = None
    message: str | None = None


@router.post("/events")
async def vapi_events(payload: VapiEventRequest):
    return {
        "ok": True,
        "received": payload.model_dump()
    }