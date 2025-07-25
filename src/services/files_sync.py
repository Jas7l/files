import logging

from apscheduler.schedulers.blocking import BlockingScheduler

from injectors import services

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


def sync_storages():
    log.info("Starting sync")
    fs = services.file_service()
    try:
        fs.sync_storage_and_db()
        log.info("Sync completed")
    except Exception as e:
        log.error(f"Sync failed: {e}")
        raise


if __name__ == "__main__":
    sync_storages()
    scheduler = BlockingScheduler()
    scheduler.add_job(sync_storages, "interval", hours=1)
    log.info("Scheduler started. Running sync every hour.")
    scheduler.start()
