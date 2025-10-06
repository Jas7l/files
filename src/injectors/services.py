from services.files_service import FilesService

from . import connections


def files_service() -> FilesService:
    """Сервис работы с файлами"""

    return FilesService(pg_connection=connections.pg.acquire_session())
