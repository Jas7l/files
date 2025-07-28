import os

from config import settings
from services.database import SessionLocal
from services.file_manager import FileManager


def file_service() -> FileManager:
    storage_path = settings.STORAGE_PATH
    os.makedirs(storage_path, exist_ok=True)
    session = SessionLocal()
    return FileManager(session, storage_path)
