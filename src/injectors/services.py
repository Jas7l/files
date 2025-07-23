import os
from flask_cors import CORS
from ..services.file_manager import FileManager
from ..database import SessionLocal
from ..config import settings


def file_service() -> FileManager:
    storage_path = settings.STORAGE_PATH
    os.makedirs(storage_path, exist_ok=True)
    session = SessionLocal()
    return FileManager(session, storage_path)


def cors_service(app) -> CORS:
    return CORS(
        app,
        origins=["http://localhost:5173"],
        supports_credentials=True,
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"]
    )