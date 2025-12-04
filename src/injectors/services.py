from services.files_service import FilesService

from . import connections


def files_service() -> FilesService:
    """Глобальный сервис работы с файлами (scripts)"""

    return FilesService(pg_connection=connections.pg.acquire_session())

def user_files_service(user_id: int) -> FilesService:
    """Пользовательский сервис работы с файлами для API"""

    return FilesService(
        pg_connection=connections.pg.acquire_session(),
        user_id=user_id,
    )
