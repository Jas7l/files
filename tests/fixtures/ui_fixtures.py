"""UI testing fixtures for Playwright and Selenium."""

import pytest
import os
from typing import Optional
from tests.config.settings import settings
from tests.utils.logger import get_logger

logger = get_logger(__name__)


@pytest.fixture(scope="session")
def browser_type_launch_args():
    """Playwright browser launch arguments."""
    return {
        "headless": settings.headless_mode,
        "args": [
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-dev-shm-usage",
        ],
    }


@pytest.fixture(scope="function")
def playwright_browser_context_args():
    """Playwright browser context arguments."""
    return {
        "viewport": {"width": 1920, "height": 1080},
        "ignore_https_errors": True,
    }


@pytest.fixture(scope="function")
def playwright_page(browser, page):
    """Wrapped Playwright page fixture to add logging without shadowing plugin fixture."""
    logger.info(f"Playwright page initialized for {settings.base_url}")
    yield page
    logger.info("Closing Playwright page")


@pytest.fixture(scope="function")
def playwright_page_with_navigation(playwright_page):
    """Playwright page with navigation."""
    yield playwright_page


@pytest.fixture(scope="function")
def screenshot_on_failure(playwright_page, request):
    """Take screenshot on test failure."""
    yield

    if hasattr(request.node, "rep_call") and request.node.rep_call.failed:
        logs_dir = os.path.join(
            os.path.dirname(__file__), "..", "logs", "screenshots"
        )
        os.makedirs(logs_dir, exist_ok=True)

        screenshot_path = os.path.join(
            logs_dir, f"{request.node.name}_failure.png"
        )
        try:
            playwright_page.screenshot(path=screenshot_path)
            logger.error(f"Screenshot saved: {screenshot_path}")
        except Exception as e:
            logger.error(f"Could not take screenshot: {e}")


# ============ Selenium Fixtures ============


@pytest.fixture(scope="function")
def selenium_driver_kwargs():
    """Selenium driver kwargs."""
    options = {}
    if settings.headless_mode:
        options["headless"] = True
    return options


@pytest.fixture(scope="function")
def selenium_driver_init_args():
    """Selenium driver initialization arguments."""
    return {}


@pytest.fixture(scope="function")
def webdriver(request):
    """Selenium WebDriver fixture."""
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait

    options = webdriver.ChromeOptions()
    if settings.headless_mode:
        options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(f"--window-size=1920,1080")

    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(settings.implicit_wait)

    logger.info(f"WebDriver initialized, navigating to {settings.base_url}")

    yield driver

    logger.info("Closing WebDriver")
    driver.quit()


@pytest.fixture(scope="function")
def selenium_screenshot_on_failure(webdriver, request):
    """Take screenshot on Selenium test failure."""
    yield

    if hasattr(request.node, "rep_call") and request.node.rep_call.failed:
        logs_dir = os.path.join(
            os.path.dirname(__file__), "..", "logs", "screenshots"
        )
        os.makedirs(logs_dir, exist_ok=True)

        screenshot_path = os.path.join(
            logs_dir, f"{request.node.name}_failure.png"
        )
        webdriver.save_screenshot(screenshot_path)
        logger.error(f"Screenshot saved: {screenshot_path}")


