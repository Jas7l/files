import os
import shutil
import uuid
import datetime
import pytest
from sqlalchemy import create_engine
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy_utils import database_exists, create_database

from tests.config.settings import settings
from tests.utils.logger import get_logger
from tests.clients.files_client import FilesClient
from tests.clients.auth_client import AuthClient

from src.models.file import File
from src.models.user import User
from base_module.models import BaseOrmMappedModel

logger = get_logger(__name__)

TEST_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data/files")

def get_test_engine():
    """Создает подключение к тестовой БД"""

    engine = create_engine(
        f"postgresql+psycopg2://{settings.pg_user}:{settings.pg_password}"
        f"@{settings.pg_host}:{settings.pg_port}/{settings.pg_database}",
        echo=settings.debug
    )

    if not database_exists(engine.url):
        create_database(engine.url)

    return engine


def create_test_schema(engine):
    """Создает схему и таблицы в тестовой БД"""

    with engine.connect() as connection:
        with connection.begin():
            if not engine.dialect.has_schema(connection, "files"):
                connection.execute(sa.text(f'CREATE SCHEMA IF NOT EXISTS files'))

            BaseOrmMappedModel.REGISTRY.metadata.create_all(connection)

    logger.info("Test database schema created")


def drop_test_schema(engine):
    """Удаляет все данные из тестовой БД"""

    with engine.connect() as connection:
        with connection.begin():
            File.__table__.drop(connection, checkfirst=True)
            User.__table__.drop(connection, checkfirst=True)

    logger.info("Test database schema dropped")


def clear_test_storage():
    """Очищает тестовое хранилище файлов"""
    if os.path.exists(settings.local_storage_path):
        shutil.rmtree(settings.local_storage_path)
        logger.info(f"Cleared test storage: {settings.local_storage_path}")

    os.makedirs(settings.local_storage_path, exist_ok=True)
    logger.info(f"Created fresh test storage: {settings.local_storage_path}")


@pytest.fixture(scope="session")
def db_engine():
    """
    Фикстура для подключения к тестовой БД.
    Создает схему и таблицы один раз для всей сессии тестов.
    """

    logger.info("Setting up test database connection")

    engine = get_test_engine()
    create_test_schema(engine)

    yield engine

    drop_test_schema(engine)
    engine.dispose()
    logger.info("Test database cleaned up")


@pytest.fixture(scope="session")
def db_session(db_engine):
    """
    Фикстура для работы с сессией БД.
    Используется для прямого доступа к БД в тестах.
    """

    Session = sessionmaker(bind=db_engine, expire_on_commit=False)
    session = Session()

    yield session

    session.close()


@pytest.fixture(scope="session", autouse=True)
def setup_test_data(db_session: Session):
    """
    Подготавливает тестовые данные через API.
    Не создает пользователя напрямую в БД.
    """
    logger.info("=" * 50)
    logger.info("Preparing test data via API...")
    logger.info("=" * 50)

    # ============================================
    # 1. Создаем и авторизуем пользователя через API
    # ============================================
    auth_client = AuthClient(settings.api_url)

    # Пытаемся зарегистрировать
    register_response = auth_client.register({
        "username": settings.test_username,
        "password": settings.test_password
    })

    if register_response.status_code == 201:
        logger.info(f"✓ Registered test user: {settings.test_username}")
    elif register_response.status_code == 400:
        logger.info(f"✓ Test user already exists: {settings.test_username}")
    else:
        logger.warning(
            f"Registration response: {register_response.status_code} - {register_response.text}")

    # Логинимся
    login_response = auth_client.login(settings.test_username,
                                       settings.test_password)

    if login_response.status_code != 200:
        logger.error(f"Login failed: {login_response.text}")
        raise Exception("Cannot login test user")

    user_data = login_response.json()
    user_id = user_data.get("id")
    token = user_data.get("token")

    logger.info(
        f"✓ Authenticated as: {settings.test_username} (ID: {user_id})")

    # ============================================
    # 2. Загружаем тестовые файлы через API
    # ============================================
    files_client = FilesClient(settings.api_url)
    files_client.set_auth_token(token)

    test_files_config = [
        {"src_filename": "test_file_1.txt", "path": "test",
         "comment": "Base test file 1"},
        {"src_filename": "test_file_2.pdf", "path": "test",
         "comment": "Base test file 2"},
        {"src_filename": "document.docx", "path": "documents",
         "comment": "Document file"},
    ]

    created_files = []

    for file_config in test_files_config:
        src_path = os.path.join(TEST_DATA_DIR, file_config["src_filename"])

        if not os.path.exists(src_path):
            logger.warning(f"Test file not found: {src_path}, creating dummy")
            os.makedirs(TEST_DATA_DIR, exist_ok=True)
            with open(src_path, 'w') as f:
                f.write(f"Test content for {file_config['src_filename']}")

        with open(src_path, 'rb') as f:
            response = files_client.upload_file(
                file_path=src_path,
                path=file_config["path"],
                comment=file_config["comment"]
            )

        if response.status_code == 200:
            file_data = response.json()
            created_files.append(file_data)
            logger.info(
                f"✓ Uploaded: {file_config['src_filename']} → ID: {file_data['id']}")
        else:
            logger.error(
                f"Failed to upload {file_config['src_filename']}: {response.status_code} - {response.text}")

    files_client.close()
    auth_client.close()

    settings._test_user_id = user_id
    settings._test_file_ids = [f["id"] for f in created_files]
    settings._test_files_info = created_files

    logger.info("=" * 50)
    logger.info(f"✓ Test data prepared successfully!")
    logger.info(f"  User ID: {user_id}")
    logger.info(f"  Files uploaded: {len(created_files)}")
    logger.info("=" * 50)

    yield

    logger.info("Test data cleanup completed")