# tests/ui/pages/selenium_storage_page.py
from selenium.webdriver.common.by import By
from tests.ui.pages.base.base_selenium_page import BaseSeleniumPage
from tests.utils.logger import get_logger

logger = get_logger(__name__)


class SeleniumStoragePage(BaseSeleniumPage):
    """Page Object для страницы хранения файлов (Selenium)."""

    # ============================================
    # ЛОКАТОРЫ
    # ============================================

    # Заголовок страницы
    PAGE_TITLE = (By.XPATH, "//h1[text()='Мои файлы']")

    # Поле поиска
    SEARCH_INPUT = (By.CSS_SELECTOR, "input[placeholder='Поиск файлов...']")

    # Список файлов (контейнер)
    FILE_LIST = (By.CSS_SELECTOR, ".file-tree-container")

    # Элемент загрузки
    LOADING_TEXT = (By.XPATH, "//p[text()='Загрузка...']")

    # Текст ошибки
    ERROR_TEXT = (By.CSS_SELECTOR, "p[style*='color: red']")

    # Панель статистики
    STATS_PANEL = (By.CSS_SELECTOR, ".storage-stats")

    # DragDrop зона
    DRAG_DROP_ZONE = (By.CSS_SELECTOR, ".drag-drop-zone")

    # Кнопка обновления
    REFRESH_BUTTON = (By.XPATH, "//button[text()='Обновить']")

    # Ошибка загрузки списка файлов
    FILE_ERROR = (By.XPATH, "//p[text()='Не удалось загрузить список файлов']")

    # Ошибка загрузки статистики
    STATS_ERROR = (By.XPATH,
                   "//span[text()='Не удалось загрузить статистику']")

    # ============================================
    # МЕТОДЫ ДЛЯ ЛОКАТОРОВ ПО ИМЕНИ
    # ============================================

    def file_item_by_name(self, name: str) -> tuple:
        """Локатор для файла по имени."""
        return (By.XPATH,
                f"//div[contains(@class, 'file-item') and contains(text(), '{name}')]")

    def delete_button_by_name(self, name: str) -> tuple:
        """Локатор для кнопки удаления файла."""
        return (By.XPATH,
                f"//div[contains(@class, 'file-item') and contains(text(), '{name}')]//button[@aria-label='Удалить']")

    # ============================================
    # МЕТОДЫ ДЛЯ ДЕЙСТВИЙ
    # ============================================

    def navigate_to_storage(self):
        """Перейти на страницу хранения."""
        logger.info("Navigating to storage page")
        self.navigate("/app")

    def wait_for_storage_page(self, timeout: int = 10):
        """Дождаться загрузки страницы с файлами."""
        logger.info("Waiting for storage page to load")
        self.wait_for_element(*self.DRAG_DROP_ZONE, timeout=timeout)

    def wait_for_loading_to_finish(self):
        """Дождаться окончания загрузки."""
        logger.info("Waiting for loading to finish")
        if self.is_visible(*self.LOADING_TEXT):
            self.wait.until(lambda d: not self.is_visible(*self.LOADING_TEXT))

    def search_files(self, query: str):
        """Выполнить поиск файлов."""
        logger.info(f"Searching for: {query}")
        self.fill(*self.SEARCH_INPUT, query)
        self.wait_for_loading_to_finish()

    def clear_search(self):
        """Очистить поле поиска."""
        logger.info("Clearing search")
        self.fill(*self.SEARCH_INPUT, "")
        self.wait_for_loading_to_finish()

    def refresh_files(self):
        """Обновить список файлов."""
        logger.info("Refreshing files")
        self.click(*self.REFRESH_BUTTON)
        self.wait_for_loading_to_finish()

    def delete_file(self, filename: str):
        """Удалить файл по имени."""
        logger.info(f"Deleting file: {filename}")
        delete_btn = self.delete_button_by_name(filename)
        self.click(*delete_btn)

    def is_file_exists(self, filename: str) -> bool:
        """Проверить, что файл с именем существует."""
        return self.is_visible(*self.file_item_by_name(filename))

    def get_file_count(self) -> int:
        """Получить количество файлов в списке."""
        return len(self.driver.find_elements(*self.FILE_LIST))

    def wait_for_file_appear(self, filename: str, timeout: int = 10):
        """Дождаться появления файла."""
        logger.info(f"Waiting for file to appear: {filename}")
        self.wait_for_element(*self.file_item_by_name(filename),
                              timeout=timeout)

    def wait_for_file_disappear(self, filename: str, timeout: int = 10):
        """Дождаться исчезновения файла."""
        logger.info(f"Waiting for file to disappear: {filename}")
        import time
        start_time = time.time()
        while time.time() - start_time < timeout:
            if not self.is_visible(*self.file_item_by_name(filename)):
                return True
            time.sleep(0.5)
        raise AssertionError(f"File {filename} still visible after {timeout}s")

        # ============================================
        # МЕТОДЫ ДЛЯ ПРОВЕРОК
        # ============================================

    def is_page_loaded(self) -> bool:
        """Проверить, что страница загружена."""
        return self.is_visible(*self.DRAG_DROP_ZONE)

    def is_error_visible(self) -> bool:
        """Проверить, видна ли ошибка."""
        return self.is_visible(*self.ERROR_TEXT)

    def is_stats_visible(self) -> bool:
        """Проверить, видна ли панель статистики."""
        return self.is_visible(*self.STATS_PANEL)

    def get_search_value(self) -> str:
        """Получить значение поля поиска."""
        element = self.find_element(*self.SEARCH_INPUT)
        return element.get_attribute("value")

    def is_loading(self) -> bool:
        """Проверить, идет ли загрузка."""
        return self.is_visible(*self.LOADING_TEXT)

    def is_file_error_visible(self) -> bool:
        """Проверить, видна ли ошибка загрузки файлов."""
        return self.is_visible(*self.FILE_ERROR)

    def is_stats_error_visible(self) -> bool:
        """Проверить, видна ли ошибка загрузки статистики."""
        return self.is_visible(*self.STATS_ERROR)

    def is_any_error_visible(self) -> bool:
        """Проверить, видна ли любая ошибка на странице."""
        return self.is_file_error_visible() or self.is_stats_error_visible()

    def get_file_error_text(self) -> str:
        """Получить текст ошибки загрузки файлов."""
        return self.get_text(*self.FILE_ERROR)

    def is_drag_drop_zone_visible(self) -> bool:
        """Проверить, видна ли зона drag-and-drop."""
        return self.is_visible(*self.DRAG_DROP_ZONE)