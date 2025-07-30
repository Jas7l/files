from services.files_service import FilesService
from . import connections


def file_service() -> FilesService:
    return FilesService(pg_connection=connections.pg.acquire_session())
