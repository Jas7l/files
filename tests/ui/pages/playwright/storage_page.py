from tests.ui.pages.base.base_playwright_page import BasePlaywrightPage
from tests.utils.logger import get_logger

logger = get_logger(__name__)


class StoragePage(BasePlaywrightPage):
    """Page Object для страницы хранения файлов (после логина)."""

    # ============================================
    # ЛОКАТОРЫ
    # ============================================

    # Заголовок страницы (условный)
    PAGE_TITLE = "h1:has-text('Мои файлы')"

    # Поле поиска
    SEARCH_INPUT = "input[placeholder='Поиск файлов...']"

    # Список файлов (контейнер)
    FILE_LIST = ".file-tree-container"  # или .file-list

    # Элемент загрузки
    LOADING_TEXT = "p:has-text('Загрузка...')"

    # Текст ошибки
    ERROR_TEXT = "p[style*='color: red']"

    # Панель статистики
    STATS_PANEL = ".storage-stats"

    # DragDrop зона
    DRAG_DROP_ZONE = ".drag-drop-zone"

    # Кнопка обновления
    REFRESH_BUTTON = "button:has-text('Обновить')"

    # Ошибка загрузки списка файлов (по тексту внутри p)
    FILE_ERROR = "p:has-text('Не удалось загрузить список файлов')"

    # Ошибка загрузки статистики
    STATS_ERROR = "span:has-text('Не удалось загрузить статистику')"

    # Элемент файла (для конкретного имени)
    def file_item_by_name(self, name: str) -> str:
        """Локатор для файла по имени."""
        return f".file-item:has-text('{name}')"

    # Кнопка удаления для файла
    def delete_button_by_name(self, name: str) -> str:
        """Локатор для кнопки удаления файла."""
        return f".file-item:has-text('{name}') button[aria-label='Удалить']"

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
        self.wait_for_element(self.FILE_LIST, timeout=timeout)

    def wait_for_loading_to_finish(self):
        """Дождаться окончания загрузки."""
        logger.info("Waiting for loading to finish")
        if self.is_visible(self.LOADING_TEXT):
            self.wait_for_element_hidden(self.LOADING_TEXT, timeout=10)

    def search_files(self, query: str):
        """Выполнить поиск файлов."""
        logger.info(f"Searching for: {query}")
        self.fill(self.SEARCH_INPUT, query)
        # Ждем обновления списка
        self.wait_for_loading_to_finish()

    def clear_search(self):
        """Очистить поле поиска."""
        logger.info("Clearing search")
        self.fill(self.SEARCH_INPUT, "")
        self.wait_for_loading_to_finish()

    def refresh_files(self):
        """Обновить список файлов."""
        logger.info("Refreshing files")
        self.click(self.REFRESH_BUTTON)
        self.wait_for_loading_to_finish()

    def delete_file(self, filename: str):
        """Удалить файл по имени."""
        logger.info(f"Deleting file: {filename}")
        # Наводим на файл (если нужно) и кликаем удаление
        delete_btn = self.delete_button_by_name(filename)
        self.click(delete_btn)

    def is_file_exists(self, filename: str) -> bool:
        """Проверить, что файл с именем существует."""
        return self.is_visible(self.file_item_by_name(filename))

    def get_file_count(self) -> int:
        """Получить количество файлов в списке."""
        return self.page.locator(self.FILE_LIST).count()

    def wait_for_file_appear(self, filename: str, timeout: int = 10):
        """Дождаться появления файла."""
        logger.info(f"Waiting for file to appear: {filename}")
        self.wait_for_element(self.file_item_by_name(filename), timeout=timeout)

    def wait_for_file_disappear(self, filename: str, timeout: int = 10):
        """Дождаться исчезновения файла."""
        logger.info(f"Waiting for file to disappear: {filename}")
        self.wait_for_element_hidden(self.file_item_by_name(filename), timeout=timeout)

    # ============================================
    # МЕТОДЫ ДЛЯ ПРОВЕРОК
    # ============================================

    def is_page_loaded(self) -> bool:
        """Проверить, что страница загружена."""
        return self.is_visible(self.FILE_LIST)

    def is_error_visible(self) -> bool:
        """Проверить, видна ли ошибка."""
        return self.is_visible(self.ERROR_TEXT)

    def is_stats_visible(self) -> bool:
        """Проверить, видна ли панель статистики."""
        return self.is_visible(self.STATS_PANEL)

    def get_search_value(self) -> str:
        """Получить значение поля поиска."""
        return self.page.input_value(self.SEARCH_INPUT)

    def is_loading(self) -> bool:
        """Проверить, идет ли загрузка."""
        return self.is_visible(self.LOADING_TEXT)

    def is_file_error_visible(self) -> bool:
        """Проверить, видна ли ошибка загрузки файлов."""
        return self.is_visible(self.FILE_ERROR)

    def is_stats_error_visible(self) -> bool:
        """Проверить, видна ли ошибка загрузки статистики."""
        return self.is_visible(self.STATS_ERROR)

    def is_any_error_visible(self) -> bool:
        """Проверить, видна ли любая ошибка на странице."""
        return self.is_file_error_visible() or self.is_stats_error_visible()

    def get_file_error_text(self) -> str:
        """Получить текст ошибки загрузки файлов."""
        return self.get_text(self.FILE_ERROR)