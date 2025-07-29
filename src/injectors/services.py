from services.file_manager import FileManager
from . import connections


def file_service() -> FileManager:
    return FileManager(pg_connection=connections.pg.acquire_session())
