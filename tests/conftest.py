"""Global pytest configuration and fixtures."""

import pytest
import sys
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

SRC_PATH = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_PATH))

from tests.fixtures.api_fixtures import *
from tests.fixtures.ui_fixtures import *
from tests.fixtures.data_fixtures import *
from tests.fixtures.db_fixtures import *
from tests.utils.logger import get_logger
from tests.config.settings import settings

logger = get_logger(__name__)


def pytest_configure(config):
    """Вывод конфига"""

    logger.info("=" * 70)
    logger.info("Test Automation Framework Started")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Base URL: {settings.base_url}")
    logger.info(f"API URL: {settings.api_url}")
    logger.info(f"Headless Mode: {settings.headless_mode}")
    logger.info("=" * 70)


def pytest_sessionstart(session):
    """Хук начала сессии"""

    logger.info("Test session started")


def pytest_sessionfinish(session, exitstatus):
    """Хук окончания сессии"""

    logger.info(f"Test session finished with exit status: {exitstatus}")


@pytest.fixture(scope="session", autouse=True)
def configure_logging():
    """Конфигурация логгера для тестов"""

    logger.info("Logging configured")
    yield
    logger.info("Test session cleanup completed")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Составить отчёт"""

    outcome = yield

    rep = outcome.get_result()

    if rep.when == "call":
        if rep.passed:
            logger.info(f"✓ PASSED: {item.name}")
        elif rep.failed:
            logger.error(f"✗ FAILED: {item.name}")
        elif rep.skipped:
            logger.warning(f"⊘ SKIPPED: {item.name}")


@pytest.fixture(scope="function")
def test_logger():
    """Логгер для теста"""

    return logger
