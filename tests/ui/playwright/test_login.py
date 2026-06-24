# tests/ui/playwright/test_login.py
import pytest
import allure
from tests.config.settings import settings
from tests.ui.pages.playwright.login_page import LoginPage
from tests.ui.pages.playwright.storage_page import StoragePage
from tests.ui.pages.playwright.register_page import RegisterPage


@allure.epic("File Service")
@allure.feature("Authentication")
@pytest.mark.ui
@pytest.mark.playwright
class TestLogin:

    @allure.story("User Login")
    @allure.title("Успешный вход с валидными данными")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("playwright", "ui", "smoke")
    def test_successful_login(self, page):
        """Тест успешного входа."""
        login_page = LoginPage(page, settings.base_url)
        storage_page = StoragePage(page, settings.base_url)

        # Действия
        login_page.navigate_to_login()
        login_page.login(settings.test_username, settings.test_password)

       # page.pause()

        # Проверки: после логина редирект на /app (StoragePage)
        # Увеличиваем таймаут для ожидания редиректа
        storage_page.wait_for_url("/app", timeout=10)
        assert "/app" in storage_page.get_current_url()

        # Проверка, что страница загрузилась
        storage_page.wait_for_storage_page(timeout=10)
        assert storage_page.is_page_loaded()


    @allure.story("User Login")
    @allure.title("Неуспешный вход с неверным паролем")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("playwright", "ui", "negative")
    def test_failed_login_wrong_password(self, page):
        """Тест входа с неверным паролем."""
        login_page = LoginPage(page, settings.base_url)
        storage_page = StoragePage(page, settings.base_url)

        login_page.navigate_to_login()
        login_page.login(settings.test_username, "wrong_password")

        # Ждем появления ошибки (увеличиваем таймаут)
        storage_page.wait_for_element(storage_page.ERROR_TEXT, timeout=5)

        # Проверки
        assert storage_page.is_file_error_visible()
        assert storage_page.is_stats_error_visible()
        assert "/app" in storage_page.get_current_url()

    @allure.story("User Login")
    @allure.title("Переход на страницу регистрации")
    @allure.severity(allure.severity_level.MINOR)
    @allure.tag("playwright", "ui", "navigation")
    def test_register_link(self, page):
        """Тест перехода на страницу регистрации."""
        login_page = LoginPage(page, settings.base_url)
        register_page = RegisterPage(page, settings.base_url)

        login_page.navigate_to_login()
        assert login_page.is_register_link_visible()

        login_page.click_register_link()

        # Проверки: перешли на /register
        register_page.wait_for_url("/register", timeout=5)
        assert "/register" in register_page.get_current_url()
        assert register_page.is_page_loaded()