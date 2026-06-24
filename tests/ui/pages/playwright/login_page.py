from tests.ui.pages.base.base_playwright_page import BasePlaywrightPage
from tests.utils.logger import get_logger

logger = get_logger(__name__)


class LoginPage(BasePlaywrightPage):
    """Page Object для страницы логина."""

    # ============================================
    # ЛОКАТОРЫ (селекторы элементов)
    # ============================================

    # Поле ввода имени пользователя
    USERNAME_INPUT = "input[placeholder='Имя пользователя']"

    # Поле ввода пароля
    PASSWORD_INPUT = "input[type='password'][placeholder='Пароль']"

    # Кнопка "Войти"
    LOGIN_BUTTON = "button:has-text('Войти')"

    # Сообщение об ошибке (попробуем разные варианты)
    ERROR_MESSAGE = "div[style*='color: red']"
    ERROR_MESSAGE_ALT = "div.error"  # альтернативный селектор

    # Ссылка на страницу регистрации
    REGISTER_LINK = "a[href='/register']"

    # Заголовок страницы
    PAGE_TITLE = "h2:has-text('Вход')"

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
        self.fill(self.USERNAME_INPUT, username)

    def enter_password(self, password: str):
        """Ввести пароль."""
        logger.info("Entering password")
        self.fill(self.PASSWORD_INPUT, password)

    def click_login(self):
        """Нажать кнопку 'Войти'."""
        logger.info("Clicking login button")
        self.click(self.LOGIN_BUTTON)

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
        return self.is_visible(self.PAGE_TITLE)

    def is_error_visible(self) -> bool:
        """Проверить, видно ли сообщение об ошибке."""
        # Проверяем основной селектор, если не работает — пробуем альтернативный
        if self.is_visible(self.ERROR_MESSAGE):
            return True
        return self.is_visible(self.ERROR_MESSAGE_ALT)

    def get_error_message(self) -> str:
        """Получить текст сообщения об ошибке."""
        if self.is_visible(self.ERROR_MESSAGE):
            return self.get_text(self.ERROR_MESSAGE)
        elif self.is_visible(self.ERROR_MESSAGE_ALT):
            return self.get_text(self.ERROR_MESSAGE_ALT)
        return ""

    def is_register_link_visible(self) -> bool:
        """Проверить, видна ли ссылка на регистрацию."""
        return self.is_visible(self.REGISTER_LINK)

    def click_register_link(self):
        """Перейти на страницу регистрации."""
        logger.info("Clicking register link")
        self.click(self.REGISTER_LINK)

    def wait_for_error(self, timeout: int = 5):
        """Дождаться появления ошибки."""
        self.wait_for_element(self.ERROR_MESSAGE, timeout=timeout)