from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException
from uuid import uuid4
from app.db.supabase import supabase
from app.services.pdf_ingest import ingest_menu_pdf

router = APIRouter()

@router.post("/upload/{restaurant_id}")
async def upload_menu(
    restaurant_id: str,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    content = await file.read()
    storage_path = f"menus/{uuid4()}-{file.filename}"

    supabase.storage.from_("menu-files").upload(
        path=storage_path,
        file=content,
        file_options={"content-type": "application/pdf"}
    )

    doc = supabase.table("menu_documents").insert({
        "restaurant_id": restaurant_id,
        "name": file.filename,
        "storage_path": storage_path,
        "is_active": True
    }).execute()

    document_id = doc.data[0]["id"]

    background_tasks.add_task(
        ingest_menu_pdf,
        restaurant_id,
        document_id,
        storage_path
    )

    return {
        "status": "uploaded",
        "document_id": document_id
    }