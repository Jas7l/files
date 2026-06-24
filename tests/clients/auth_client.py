from typing import Dict, Any, Optional
import requests
from tests.clients.base_client import BaseApiClient
from tests.utils.logger import get_logger

logger = get_logger(__name__)


class AuthClient(BaseApiClient):
    """API клиент аунтификации"""

    def register(self, user_data: Dict[str, Any]) -> requests.Response:
        """Зарегестрировать нового пользователя"""

        logger.info(f"Registering user with username: {user_data.get('username')}")
        return self.post("/api/auth/register", json=user_data)

    def login(self, username: str, password: str) -> requests.Response:
        """Логин пользователя и установка токена"""

        logger.info(f"Logging in user: {username}")
        response = self.post(
            "/api/auth/login",
            json={"username": username, "password": password},
        )

        if response.status_code == 200:
            try:
                token = response.json().get("token")
                if token:
                    self.set_auth_token(token)
                    logger.info("Auth token set successfully")
            except Exception as e:
                logger.warning(f"Could not extract token: {e}")

        return response

    def logout(self) -> requests.Response:
        """Логаут и удаление токена"""

        logger.info("Logging out user")
        response = self.post("/api/auth/logout", json={})
        self.auth_token = None

        return response
