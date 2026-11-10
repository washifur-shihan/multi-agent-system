from datetime import datetime, timezone
from uuid import uuid4
from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException

from app.db.supabase import supabase
from app.config import settings
from app.services.agents import get_agent_by_id, get_agent_by_slug
from app.services.pdf_ingest import ingest_knowledge_pdf
from app.services.retrieval import list_knowledge_documents, register_local_document

router = APIRouter()


def _resolve_agent(agent_identifier: str) -> dict:
    agent = get_agent_by_id(agent_identifier) or get_agent_by_slug(agent_identifier)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_identifier}' not found")
    return agent


@router.get("/{agent_identifier}")
async def get_agent_knowledge(agent_identifier: str):
    agent = _resolve_agent(agent_identifier)
    documents = list_knowledge_documents(agent["id"])
    return {
        "agent_id": agent["id"],
        "agent_slug": agent["slug"],
        "documents": documents,
    }


@router.post("/upload/{agent_identifier}")
async def upload_knowledge(
    agent_identifier: str,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    agent = _resolve_agent(agent_identifier)
    agent_id = agent["id"]

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded PDF file is empty.")

    storage_path = f"knowledge/{agent_id}/{uuid4()}-{file.filename}"
    document_id = str(uuid4())

    if supabase is not None:
        try:
            supabase.storage.from_(settings.SUPABASE_BUCKET).upload(
                path=storage_path,
                file=content,
                file_options={"content-type": "application/pdf"},
            )
            doc_res = (
                supabase.table("knowledge_documents")
                .insert(
                    {
                        "agent_id": agent_id,
                        "file_name": file.filename,
                        "storage_path": storage_path,
                    }
                )
                .execute()
            )
            if doc_res.data:
                document_id = doc_res.data[0]["id"]
        except Exception as exc:
            print(f"⚠️ Supabase storage/table upload fallback to memory ({exc})")

    local_doc = {
        "id": document_id,
        "agent_id": agent_id,
        "file_name": file.filename,
        "storage_path": storage_path,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    register_local_document(local_doc)

    background_tasks.add_task(
        ingest_knowledge_pdf,
        agent_id,
        document_id,
        storage_path,
        content,
    )

    return {
        "status": "uploaded",
        "document_id": document_id,
        "file_name": file.filename,
        "agent_slug": agent["slug"],
    }
