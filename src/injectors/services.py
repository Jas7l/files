import os

from config import settings
from . import connections
from services.file_manager import FileManager


def file_service() -> FileManager:
    return FileManager(pg_connection=connections.pg.acquire_session())
