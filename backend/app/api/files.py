from fastapi import APIRouter, UploadFile, File, Form, BackgroundTasks, HTTPException, Query
from fastapi.responses import FileResponse
from typing import List, Optional
from app.schemas.file import FileUpdate, FileRead
from app.services.file_manager import FileManager
from app.database import context_db

# Create router
router = APIRouter()


# Route for syncing the database with the local storage
@router.post("/files/sync")
async def sync_files(background_tasks: BackgroundTasks):
    background_tasks.add_task(FileManager.sync_storage_and_db)
    return {"detail": "Sync started in background"}


# Route to get all files or filter files by path
# URL example: /files?path=my-path
@router.get("/files", response_model=List[FileRead])
def get_files(path: Optional[str] = Query(None)):
    files = FileManager.get_all_files(path)
    if not files:
        raise HTTPException(status_code=404, detail="No files found")
    return files


# Route to get file by ID
@router.get("/files/{file_id}", response_model=FileRead)
def get_file(file_id: int):
    return FileManager.get_file_by_id(file_id)


# Route to download a file
@router.get("/files/{file_id}/download")
def download_file(file_id: int):
    return FileManager.download_file(file_id)


# Route to upload a file
@router.post("/files", response_model=FileRead)
def upload_file(
    uploaded_file: UploadFile = File(...),
    path: Optional[str] = Form(""),
    comment: Optional[str] = Form(None),
):
    return FileManager.upload_file(uploaded_file, path, comment)


# Route to update a file
@router.patch("/files/{file_id}", response_model=FileRead)
def update_file(file_id: int, file_data: FileUpdate):
    return FileManager.update_file(file_id, file_data)


# Route to delete a file
@router.delete("/files/{file_id}", response_model=FileRead)
def delete_file(file_id: int):
    return FileManager.delete_file(file_id)
