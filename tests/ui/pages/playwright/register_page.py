from tests.ui.pages.base.base_playwright_page import BasePlaywrightPage
from tests.utils.logger import get_logger

logger = get_logger(__name__)

class RegisterPage(BasePlaywrightPage):
    """Page Object для страницы регистрации"""

    # Локаторы
    USERNAME_INPUT = "input[placeholder='Имя пользователя']"
    PASSWORD_INPUT = "input[type='password'][placeholder='Пароль']"
    PASSWORD2_INPUT = "input[type='password'][placeholder='Повторите пароль']"
    SUBMIT_BUTTON = "button:has-text('Создать аккаунт')"
    ERROR_MESSAGE = "div[style*='color: red']"
    LOGIN_LINK = "a[href='/login']"
    PAGE_TITLE = "h2:has-text('Регистрация')"
    LOADING_BUTTON = "button:has-text('Создание...')"

    def navigate_to_register(self):
        """Перейти на страницу регистрации"""

        logger.info("Navigating to register page")
        self.navigate("/register")

    def enter_username(self, username: str):
        """Ввести имя пользователя."""
        logger.info(f"Entering username: {username}")
        self.fill(self.USERNAME_INPUT, username)

    def enter_password(self, password: str):
        """Ввести пароль."""
        logger.info("Entering password")
        self.fill(self.PASSWORD_INPUT, password)

    def enter_password_confirm(self, password: str):
        """Ввести подтверждение пароля."""
        logger.info("Entering password confirmation")
        self.fill(self.PASSWORD2_INPUT, password)

    def click_submit(self):
        """Нажать кнопку 'Создать аккаунт'."""
        logger.info("Clicking submit button")
        self.click(self.SUBMIT_BUTTON)

    def register(self, username: str, password: str):
        """Выполнить полную регистрацию."""
        logger.info(f"Registering user: {username}")
        self.enter_username(username)
        self.enter_password(password)
        self.enter_password_confirm(password)
        self.click_submit()

    def register_with_mismatch(self, username: str, password: str,
                               password2: str):
        """Регистрация с несовпадающими паролями."""
        logger.info(f"Registering with mismatched passwords")
        self.enter_username(username)
        self.enter_password(password)
        self.enter_password_confirm(password2)
        self.click_submit()

    def click_login_link(self):
        """Нажать ссылку 'Войти'."""
        logger.info("Clicking login link")
        self.click(self.LOGIN_LINK)

        # ============================================
        # МЕТОДЫ ДЛЯ ПРОВЕРОК
        # ============================================

    def is_page_loaded(self) -> bool:
        """Проверить, что страница регистрации загружена."""
        return self.is_visible(self.PAGE_TITLE)

    def is_error_visible(self) -> bool:
        """Проверить, видно ли сообщение об ошибке."""
        return self.is_visible(self.ERROR_MESSAGE)

    def get_error_message(self) -> str:
        """Получить текст сообщения об ошибке."""
        return self.get_text(self.ERROR_MESSAGE)

    def is_login_link_visible(self) -> bool:
        """Проверить, видна ли ссылка 'Войти'."""
        return self.is_visible(self.LOGIN_LINK)

    def is_loading(self) -> bool:
        """Проверить, что кнопка в состоянии загрузки."""
        return self.is_visible(self.LOADING_BUTTON)

    def wait_for_success(self):
        """Дождаться успешной регистрации (редирект на /login)."""
        self.wait_for_url("/login", timeout=10)
