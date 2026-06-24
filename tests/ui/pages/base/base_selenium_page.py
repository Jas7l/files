"""Base Selenium Page Object Model class."""

from typing import Optional, Union
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from tests.utils.logger import get_logger

logger = get_logger(__name__)


class BaseSeleniumPage:
    """Base Selenium Page Object Model class."""

    def __init__(self, driver, base_url: str, timeout: int = 10):
        """
        Initialize base page.

        Args:
            driver: Selenium WebDriver instance
            base_url: Application base URL
            timeout: Wait timeout in seconds
        """
        self.driver = driver
        self.base_url = base_url
        self.timeout = timeout
        self.wait = WebDriverWait(driver, timeout)

    def navigate(self, path: str = ""):
        """Navigate to page."""
        url = f"{self.base_url}{path}"
        logger.info(f"Navigating to {url}")
        self.driver.get(url)

    def find_element(self, by: By, value: str):
        """Find element with wait."""
        logger.info(f"Finding element: {by}={value}")
        return self.wait.until(EC.presence_of_element_located((by, value)))

    def find_clickable_element(self, by: By, value: str):
        """Find clickable element with wait."""
        logger.info(f"Finding clickable element: {by}={value}")
        return self.wait.until(EC.element_to_be_clickable((by, value)))

    def click(self, by: By, value: str):
        """Click element."""
        logger.info(f"Clicking element: {by}={value}")
        element = self.find_clickable_element(by, value)
        element.click()

    def fill(self, by: By, value: str, text: str):
        """Fill text input."""
        logger.info(f"Filling {by}={value} with text")
        element = self.find_element(by, value)
        element.clear()
        element.send_keys(text)

    def get_text(self, by: By, value: str) -> str:
        """Get element text."""
        logger.info(f"Getting text from: {by}={value}")
        element = self.find_element(by, value)
        return element.text

    def is_visible(self, by: By, value: str, timeout: Optional[int] = None) -> bool:
        """Check if element is visible."""
        logger.info(f"Checking visibility of: {by}={value}")
        wait = WebDriverWait(self.driver, timeout or self.timeout)
        try:
            wait.until(EC.visibility_of_element_located((by, value)))
            return True
        except TimeoutException:
            return False

    def is_present(self, by: By, value: str, timeout: Optional[int] = None) -> bool:
        """Check if element is present in DOM."""
        logger.info(f"Checking presence of: {by}={value}")
        wait = WebDriverWait(self.driver, timeout or self.timeout)
        try:
            wait.until(EC.presence_of_element_located((by, value)))
            return True
        except TimeoutException:
            return False

    def take_screenshot(self, filename: str):
        """Take screenshot."""
        logger.info(f"Taking screenshot: {filename}")
        self.driver.save_screenshot(filename)

    def wait_for_url(self, url_pattern: str, timeout: Optional[int] = None):
        """Wait for URL to match pattern."""
        logger.info(f"Waiting for URL: {url_pattern}")
        wait = WebDriverWait(self.driver, timeout or self.timeout)
        wait.until(EC.url_contains(url_pattern))

    def reload(self):
        """Reload page."""
        logger.info("Reloading page")
        self.driver.refresh()

    def go_back(self):
        """Go back to previous page."""
        logger.info("Going back")
        self.driver.back()

    def get_current_url(self) -> str:
        """Get current URL."""
        return self.driver.current_url

    def get_title(self) -> str:
        """Get page title."""
        return self.driver.title

    def wait_for_element(self, by: By, value: str,
                         timeout: Optional[int] = None):
        """Ожидание появления элемента."""
        logger.info(f"Waiting for element: {by}={value}")
        wait = WebDriverWait(self.driver, timeout or self.timeout)
        return wait.until(EC.presence_of_element_located((by, value)))