from typing import Any, Dict, Optional
import requests
import json
import os
from tests.clients.base_client import BaseApiClient
from tests.utils.logger import get_logger

logger = get_logger(__name__)

class FilesClient(BaseApiClient):
    """API клиент сервиса работы с файлами"""

    def health_check(self) -> requests.Response:
        """Check API health."""
        return self.get("/api/health")

    def get_files(self, path: str = None) -> requests.Response:
        """Получение списка файлов"""

        params = {}
        if path:
            params['path'] = path

        return self.get("/api/files", params=params)

    def upload_file(self, file_path: str, path: str = "",
                    comment: str = "") -> requests.Response:
        """
        Загружает файл на сервер.

        Args:
            file_path: путь к файлу на диске
            path: относительный путь для хранения (опционально)
            comment: комментарий к файлу (опционально)

        Returns:
            Response object
        """
        # Формируем fields как JSON строку
        fields = json.dumps({
            "path": path,
            "comment": comment
        })

        # Открываем файл в бинарном режиме
        with open(file_path, 'rb') as f:
            files = {
                "attachment": (os.path.basename(file_path), f,
                               "application/octet-stream")
            }
            data = {
                "fields": fields
            }

            return self.post("/api/files", files=files, data=data)
