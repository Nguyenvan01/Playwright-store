# ============================================================
# DEMO: ERROR TAXONOMY
# Mục tiêu: cùng một vocabulary lỗi cho log, JUnit và Allure.
# Kịch bản: phân loại exception mà không nuốt hoặc thay đổi exception.
# ============================================================
import pytest
from playwright._impl._errors import Error, TimeoutError

from utils.error_classifier import classify_exception, classify_report_text

pytestmark = pytest.mark.core


@pytest.mark.parametrize(
    ("error", "expected"),
    [
        (AssertionError("actual != expected"), "ASSERTION_FAILED"),
        (TimeoutError("Timeout 10000ms exceeded"), "TIMEOUT"),
        (Error("strict mode violation: locator resolved to 2 elements"), "LOCATOR_AMBIGUOUS"),
        (Error("net::ERR_CONNECTION_REFUSED at http://localhost:3000/"), "NETWORK_ERROR"),
        (Error("Target page, context or browser has been closed"), "BROWSER_CLOSED"),
        (Error("Element is not attached to the DOM"), "PLAYWRIGHT_ERROR"),
        (ValueError("missing column"), "DATA_OR_CONTRACT_ERROR"),
        (KeyError("product"), "DATA_OR_CONTRACT_ERROR"),
        (RuntimeError("unexpected"), "UNEXPECTED_ERROR"),
    ],
)
def test_classify_exception(error, expected):
    assert classify_exception(error) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("playwright._impl._errors.TimeoutError: Locator.click: Timeout 10000ms", "TIMEOUT"),
        ("AssertionError: Locator expected to be visible", "ASSERTION_FAILED"),
        ("ValueError: Keyword không tồn tại", "DATA_OR_CONTRACT_ERROR"),
        ("", "UNEXPECTED_ERROR"),
    ],
)
def test_classify_report_text(text, expected):
    assert classify_report_text(text) == expected
