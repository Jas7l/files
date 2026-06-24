"""Custom assertions for test automation."""

from typing import Any, Optional, List
import json


class AssertionError(Exception):
    """Custom assertion error."""

    pass


class Assert:
    """Custom assertion helper class."""

    @staticmethod
    def equal(actual: Any, expected: Any, message: Optional[str] = None):
        """Assert that actual equals expected."""
        if actual != expected:
            msg = message or f"Expected {expected}, but got {actual}"
            raise AssertionError(msg)

    @staticmethod
    def not_equal(actual: Any, expected: Any, message: Optional[str] = None):
        """Assert that actual does not equal expected."""
        if actual == expected:
            msg = message or f"Expected not equal to {expected}, but got {actual}"
            raise AssertionError(msg)

    @staticmethod
    def is_true(condition: bool, message: Optional[str] = None):
        """Assert that condition is True."""
        if not condition:
            msg = message or "Expected condition to be True"
            raise AssertionError(msg)

    @staticmethod
    def is_false(condition: bool, message: Optional[str] = None):
        """Assert that condition is False."""
        if condition:
            msg = message or "Expected condition to be False"
            raise AssertionError(msg)

    @staticmethod
    def is_none(value: Any, message: Optional[str] = None):
        """Assert that value is None."""
        if value is not None:
            msg = message or f"Expected None, but got {value}"
            raise AssertionError(msg)

    @staticmethod
    def is_not_none(value: Any, message: Optional[str] = None):
        """Assert that value is not None."""
        if value is None:
            msg = message or "Expected not None"
            raise AssertionError(msg)

    @staticmethod
    def contains(container: Any, item: Any, message: Optional[str] = None):
        """Assert that container contains item."""
        if item not in container:
            msg = message or f"Expected {item} to be in {container}"
            raise AssertionError(msg)

    @staticmethod
    def not_contains(container: Any, item: Any, message: Optional[str] = None):
        """Assert that container does not contain item."""
        if item in container:
            msg = message or f"Expected {item} not to be in {container}"
            raise AssertionError(msg)

    @staticmethod
    def is_instance(obj: Any, cls: type, message: Optional[str] = None):
        """Assert that object is instance of class."""
        if not isinstance(obj, cls):
            msg = message or f"Expected {obj} to be instance of {cls}"
            raise AssertionError(msg)

    @staticmethod
    def has_key(data: dict, key: str, message: Optional[str] = None):
        """Assert that dictionary has key."""
        if key not in data:
            msg = message or f"Expected key '{key}' in {list(data.keys())}"
            raise AssertionError(msg)

    @staticmethod
    def response_status(status_code: int, expected: int, message: Optional[str] = None):
        """Assert response status code."""
        if status_code != expected:
            msg = message or f"Expected status {expected}, got {status_code}"
            raise AssertionError(msg)

    @staticmethod
    def response_has_key(response: dict, key: str, message: Optional[str] = None):
        """Assert that response has key."""
        if key not in response:
            msg = message or f"Response missing key '{key}'. Keys: {list(response.keys())}"
            raise AssertionError(msg)

    @staticmethod
    def response_value(
        response: dict,
        key: str,
        expected_value: Any,
        message: Optional[str] = None,
    ):
        """Assert response value at key."""
        Assert.has_key(response, key, message)
        actual = response[key]
        if actual != expected_value:
            msg = (
                message
                or f"Response['{key}'] expected {expected_value}, got {actual}"
            )
            raise AssertionError(msg)

