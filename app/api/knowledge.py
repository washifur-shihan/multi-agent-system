from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException
from uuid import uuid4

from app.db.supabase import supabase
from app.config import settings
from app.services.pdf_ingest import ingest_knowledge_pdf

router = APIRouter()


@router.post("/upload/{agent_id}")
async def upload_knowledge(
    agent_id: str,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    content = await file.read()
    storage_path = f"knowledge/{agent_id}/{uuid4()}-{file.filename}"

    supabase.storage.from_(settings.SUPABASE_BUCKET).upload(
        path=storage_path,
        file=content,
        file_options={"content-type": "application/pdf"}
    )

    doc = (
        supabase.table("knowledge_documents")
        .insert({
            "agent_id": agent_id,
            "file_name": file.filename,
            "storage_path": storage_path
        })
        .execute()
    )

    document_id = doc.data[0]["id"]

    background_tasks.add_task(
        ingest_knowledge_pdf,
        agent_id,
        document_id,
        storage_path
    )

    return {
        "status": "uploaded",
        "document_id": document_id
    }