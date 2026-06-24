# tests/ui/selenium/test_login.py
import pytest
import allure
from tests.config.settings import settings
from tests.ui.pages.selenium.login_page import SeleniumLoginPage
from tests.ui.pages.selenium.storage_page import SeleniumStoragePage
from tests.ui.pages.selenium.register_page import SeleniumRegisterPage


@allure.epic("File Service")
@allure.feature("Authentication")
@pytest.mark.ui
@pytest.mark.selenium
class TestSeleniumLogin:

    @allure.story("User Login")
    @allure.title("Успешный вход с валидными данными (Selenium)")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("selenium", "ui", "smoke")
    def test_successful_login(self, webdriver):
        """Тест успешного входа через Selenium."""
        login_page = SeleniumLoginPage(webdriver, settings.base_url)
        storage_page = SeleniumStoragePage(webdriver, settings.base_url)

        login_page.navigate_to_login()
        login_page.login(settings.test_username, settings.test_password)

        # Проверки: после логина редирект на /app (StoragePage)
        storage_page.wait_for_url("/app", timeout=10)
        assert "/app" in storage_page.get_current_url()

        # Проверка, что страница загрузилась
        storage_page.wait_for_storage_page(timeout=10)
        assert storage_page.is_page_loaded()

    @allure.story("User Login")
    @allure.title("Неуспешный вход с неверным паролем (Selenium)")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("selenium", "ui", "negative")
    def test_failed_login_wrong_password(self, webdriver):
        """Тест входа с неверным паролем через Selenium."""
        login_page = SeleniumLoginPage(webdriver, settings.base_url)
        storage_page = SeleniumStoragePage(webdriver, settings.base_url)

        login_page.navigate_to_login()
        login_page.login(settings.test_username, "wrong_password")

        # Ждем появления ошибки на StoragePage (как в Playwright версии)
        storage_page.wait_for_element(*storage_page.ERROR_TEXT, timeout=5)

        # Проверки: после неудачного логина редирект на /app с ошибкой
        assert "/app" in storage_page.get_current_url()
        assert storage_page.is_file_error_visible()
        assert storage_page.is_stats_error_visible()

    @allure.story("User Login")
    @allure.title("Переход на страницу регистрации (Selenium)")
    @allure.severity(allure.severity_level.MINOR)
    @allure.tag("selenium", "ui", "navigation")
    def test_register_link(self, webdriver):
        """Тест перехода на страницу регистрации через Selenium."""
        login_page = SeleniumLoginPage(webdriver, settings.base_url)
        register_page = SeleniumRegisterPage(webdriver, settings.base_url)

        login_page.navigate_to_login()
        assert login_page.is_register_link_visible()

        login_page.click_register_link()

        # Проверки: перешли на /register
        register_page.wait_for_url("/register", timeout=5)
        assert "/register" in register_page.get_current_url()
        assert register_page.is_page_loaded()