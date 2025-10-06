import logging
import time

from config import config
from injectors import services

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


def sync_storages():
    """Вызов метода синхронизации сервиса files"""

    log.info('Starting sync')
    fs = services.files_service()
    try:
        fs.sync_storage_and_db()
        log.info('Sync completed')
    except Exception as e:
        log.error(f'Sync failed: {e}')
        raise


if __name__ == '__main__':
    """Запуск регулярной синхронизации хранилища и БД"""

    sync_storages()
    interval = config.sync_interval
    log.info('Running sync every hour.')
    while True:
        sync_storages()
        time.sleep(interval)
