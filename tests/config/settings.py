import os
from typing import Optional
from dotenv import load_dotenv


class Settings:
    """Менеджер настроек фреймворка"""

    def __init__(self, env_file: Optional[str] = None):
        """Инициализация настроек из файла окружения"""

        if env_file is None:
            env_file = os.path.join(
                os.path.dirname(__file__), "dev.env"
            )

        if os.path.exists(env_file):
            load_dotenv(env_file)

    @property
    def base_url(self) -> str:
        """Базовый URL фронтенда"""

        return os.getenv("BASE_URL", "http://localhost:5173")

    @property
    def api_url(self) -> str:
        """Базовый url api"""

        return os.getenv("API_URL", "http://localhost:8020")

    @property
    def headless_mode(self) -> bool:
        """Параметр headless для отчётов"""

        return os.getenv("HEADLESS_MODE", "false").lower() == "true"

    @property
    def browser_timeout(self) -> int:
        """Таймаут браузера"""

        return int(os.getenv("BROWSER_TIMEOUT", "30"))

    @property
    def implicit_wait(self) -> int:
        """Время ожидание"""

        return int(os.getenv("IMPLICIT_WAIT", "10"))

    @property
    def log_level(self) -> str:
        """Уровень логирования"""

        return os.getenv("LOG_LEVEL", "INFO")

    @property
    def environment(self) -> str:
        """Текущий environment"""

        return os.getenv("ENVIRONMENT", "dev")

    @property
    def test_username(self) -> str:
        """Get test username."""
        return os.getenv("TEST_USERNAME", "testuser")

    @property
    def test_password(self) -> str:
        """Get test password."""
        return os.getenv("TEST_PASSWORD", "testpass123")

    @property
    def pg_host(self) -> str:
        """PostgreSQL host for tests"""
        return os.getenv("PG_HOST", "localhost")

    @property
    def pg_port(self) -> int:
        """PostgreSQL port for tests"""
        return int(os.getenv("PG_PORT", "5443"))

    @property
    def pg_user(self) -> str:
        """PostgreSQL user for tests"""
        return os.getenv("PG_USER", "test_user")

    @property
    def pg_password(self) -> str:
        """PostgreSQL password for tests"""
        return os.getenv("PG_PASSWORD", "test_password")

    @property
    def pg_database(self) -> str:
        """PostgreSQL database name for tests"""
        return os.getenv("PG_DATABASE", "test_db")

    @property
    def debug(self) -> bool:
        """Debug mode for tests"""
        return os.getenv("DEBUG", "false").lower() == "true"

    @property
    def local_storage_path(self) -> str:
        """Storage path on local machine for test fixtures"""

        tests_dir = os.path.dirname(os.path.dirname(__file__))
        return os.path.join(tests_dir, "storage")


def get_settings(env: Optional[str] = None) -> Settings:
    """Получить настройки из файла окружения"""

    if env is None:
        env = os.getenv("ENVIRONMENT", "dev")

    env_file = os.path.join(os.path.dirname(__file__), f"{env}.env")
    return Settings(env_file)

settings = get_settings()
