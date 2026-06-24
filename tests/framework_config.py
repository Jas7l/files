"""Test automation framework configuration."""

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

FRAMEWORK_VERSION = "2.0.0"

TEST_FRAMEWORK = "pytest"
REPORTING_TOOL = "allure"
DRIVER_BROWSER = ["playwright", "selenium"]

TESTS_DIR = Path(__file__).parent
LOGS_DIR = TESTS_DIR / "logs"
REPORTS_DIR = TESTS_DIR / "reports"
SCREENSHOTS_DIR = LOGS_DIR / "screenshots"

for directory in [LOGS_DIR, REPORTS_DIR, SCREENSHOTS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)


