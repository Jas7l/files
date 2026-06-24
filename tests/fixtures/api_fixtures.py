import pytest
from tests.clients.files_client import FilesClient
from tests.clients.auth_client import AuthClient
from tests.config.settings import settings
from tests.utils.logger import get_logger

logger = get_logger(__name__)

@pytest.fixture(scope="session")
def api_base_url() -> str:
    """Базовый url API"""

    return settings.api_url

@pytest.fixture(scope="function")
def api_client(api_base_url: str) -> FilesClient:
    """Фикстура api client"""

    client = FilesClient(api_base_url, timeout=settings.browser_timeout)
    yield client
    client.close()

@pytest.fixture(scope="function")
def auth_client(api_base_url: str) -> AuthClient:
    """Фикстура authh client"""

    client = AuthClient(api_base_url, timeout=settings.browser_timeout)
    yield client
    client.close()

@pytest.fixture(scope="function")
def authenticated_api_client(auth_client: AuthClient) -> FilesClient:
    """Фикстура авторризованного api client"""

    response = auth_client.login(
        settings.test_username, settings.test_password
    )

    if response.status_code != 200:
        logger.warning(f'Login failed: {response.text}')

    api_client = FilesClient(auth_client.base_url)
    if auth_client.auth_token:
        api_client.set_auth_token(auth_client.auth_token)

    yield api_client
    api_client.close()
