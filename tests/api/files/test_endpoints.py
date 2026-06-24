import pytest
from tests.clients.files_client import FilesClient
from tests.utils.assertions import Assert
from tests.utils.allure_helper import AllureReporting
import allure


@allure.epic("File Storage Service")
@allure.feature("Files API")
@pytest.mark.api
class TestFilesAPI:

    @allure.story("Get files list")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Получение списка файлов")
    def test_get_files(self, authenticated_api_client):
        """Тест получения списка файлов"""

        with AllureReporting.add_step("Подготовка запроса"):
            client = authenticated_api_client
            url = "/api/files"
            AllureReporting.attach_request("GET", url)

        with AllureReporting.add_step("Отправка запроса"):
            response = client.get_files()

        with AllureReporting.add_step("Проверка ответа"):
            AllureReporting.attach_response(
                response.status_code,response.json()
            )
            Assert.response_status(response.status_code, 200)
            data = response.json()
            Assert.is_not_none(data)
            AllureReporting.attach_log(
                f"Получено файлов: {len(data)}","files_count"
            )

        with AllureReporting.add_step("Завершение"):
            allure.attach(
                "Тест успешно выполнен", "result", allure.attachment_type.TEXT
            )


    @allure.story("Get filtred files list")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Получение отфильтрованного списка файлов")
    def test_get_files_filtred(self, authenticated_api_client):
        """Тест получения списка файлов"""

        filter_path = "test"

        with AllureReporting.add_step("Подготовка запроса"):
            client = authenticated_api_client
            url = "/api/files"
            AllureReporting.attach_request(
                "GET", url, params={"path": filter_path}
            )

        with AllureReporting.add_step("Отправка запроса"):
            response = client.get_files(filter_path)

        with AllureReporting.add_step("Проверка ответов"):
            AllureReporting.attach_response(response.status_code, response.json())
            Assert.response_status(response.status_code, 200)
            data = response.json()
            Assert.is_not_none(data)
            Assert.equal(data[0]["name"], "test_file_1")
            AllureReporting.attach_log(
                f"Получено файлов: {len(data)}", "files_count"
            )
