"""Base Page Object Model class for Playwright."""

from typing import Optional
from tests.utils.logger import get_logger

logger = get_logger(__name__)


class BasePlaywrightPage:
    """Base Page Object Model class for Playwright."""

    def __init__(self, page, base_url: str):
        """
        Initialize base page.

        Args:
            page: Playwright page object
            base_url: Application base URL
        """
        self.page = page
        self.base_url = base_url

    def navigate(self, path: str = ""):
        """Navigate to page."""
        url = f"{self.base_url}{path}"
        logger.info(f"Navigating to {url}")
        self.page.goto(url)

    def wait_for_element(self, selector: str, timeout: int = 5):
        """Wait for element to be visible."""
        logger.info(f"Waiting for element: {selector}")
        self.page.wait_for_selector(selector, timeout=timeout * 1000)

    def wait_for_element_hidden(self, selector: str, timeout: int = 5):
        """Wait for element to be hidden."""
        logger.info(f"Waiting for element to be hidden: {selector}")
        self.page.wait_for_selector(selector, state="hidden", timeout=timeout * 1000)

    def get_element(self, selector: str):
        """Get element by selector."""
        return self.page.locator(selector)

    def click(self, selector: str):
        """Click element."""
        logger.info(f"Clicking element: {selector}")
        self.page.click(selector)

    def fill(self, selector: str, text: str):
        """Fill text input."""
        logger.info(f"Filling {selector} with: {text}")
        self.page.fill(selector, text)

    def get_text(self, selector: str) -> str:
        """Get element text."""
        logger.info(f"Getting text from: {selector}")
        return self.page.text_content(selector)

    def is_visible(self, selector: str) -> bool:
        """Check if element is visible."""
        logger.info(f"Checking visibility of: {selector}")
        return self.page.is_visible(selector)

    def is_hidden(self, selector: str) -> bool:
        """Check if element is hidden."""
        logger.info(f"Checking if element is hidden: {selector}")
        return self.page.is_hidden(selector)

    def take_screenshot(self, filename: str):
        """Take screenshot."""
        logger.info(f"Taking screenshot: {filename}")
        self.page.screenshot(path=filename)

    def wait_for_url(self, url_pattern: str, timeout: int = 5):
        """Wait for URL to match pattern."""
        logger.info(f"Waiting for URL: {url_pattern}")
        self.page.wait_for_url(url_pattern, timeout=timeout * 1000)

    def reload(self):
        """Reload page."""
        logger.info("Reloading page")
        self.page.reload()

    def go_back(self):
        """Go back to previous page."""
        logger.info("Going back")
        self.page.go_back()

    def get_current_url(self) -> str:
        """Get current URL."""
        return self.page.url

    def get_title(self) -> str:
        """Get page title."""
        return self.page.title()