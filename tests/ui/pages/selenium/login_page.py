# tests/ui/pages/selenium_login_page.py
from selenium.webdriver.common.by import By
from tests.ui.pages.base.base_selenium_page import BaseSeleniumPage
from tests.utils.logger import get_logger

logger = get_logger(__name__)


class SeleniumLoginPage(BaseSeleniumPage):
    """Page Object для страницы логина (Selenium)."""

    # ============================================
    # ЛОКАТОРЫ (селекторы элементов)
    # ============================================

    # Поле ввода имени пользователя
    USERNAME_INPUT = (By.CSS_SELECTOR, "input[placeholder='Имя пользователя']")

    # Поле ввода пароля
    PASSWORD_INPUT = (By.CSS_SELECTOR, "input[type='password'][placeholder='Пароль']")

    # Кнопка "Войти" — используем XPath вместо :has-text()
    LOGIN_BUTTON = (By.XPATH, "//button[text()='Войти']")

    # Сообщение об ошибке
    ERROR_MESSAGE = (By.CSS_SELECTOR, "div[style*='color: red']")

    # Ссылка на страницу регистрации
    REGISTER_LINK = (By.CSS_SELECTOR, "a[href='/register']")

    # Заголовок страницы
    PAGE_TITLE = (By.XPATH, "//h2[text()='Вход']")

    # ============================================
    # МЕТОДЫ ДЛЯ ДЕЙСТВИЙ
    # ============================================

    def navigate_to_login(self):
        """Перейти на страницу логина."""
        logger.info("Navigating to login page")
        self.navigate("/login")

    def enter_username(self, username: str):
        """Ввести имя пользователя."""
        logger.info(f"Entering username: {username}")
        self.fill(*self.USERNAME_INPUT, username)

    def enter_password(self, password: str):
        """Ввести пароль."""
        logger.info("Entering password")
        self.fill(*self.PASSWORD_INPUT, password)

    def click_login(self):
        """Нажать кнопку 'Войти'."""
        logger.info("Clicking login button")
        self.click(*self.LOGIN_BUTTON)

    def login(self, username: str, password: str):
        """Выполнить полный логин (ввести данные + нажать кнопку)."""
        logger.info(f"Logging in as: {username}")
        self.enter_username(username)
        self.enter_password(password)
        self.click_login()

    # ============================================
    # МЕТОДЫ ДЛЯ ПРОВЕРОК
    # ============================================

    def is_page_loaded(self) -> bool:
        """Проверить, что страница логина загружена."""
        return self.is_visible(*self.PAGE_TITLE)

    def is_error_visible(self) -> bool:
        """Проверить, видно ли сообщение об ошибке."""
        return self.is_visible(*self.ERROR_MESSAGE)

    def get_error_message(self) -> str:
        """Получить текст сообщения об ошибке."""
        return self.get_text(*self.ERROR_MESSAGE)

    def is_register_link_visible(self) -> bool:
        """Проверить, видна ли ссылка на регистрацию."""
        return self.is_visible(*self.REGISTER_LINK)

    def click_register_link(self):
        """Перейти на страницу регистрации."""
        logger.info("Clicking register link")
        self.click(*self.REGISTER_LINK)