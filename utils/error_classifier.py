# PHÂN LOẠI LỖI: hỗ trợ báo cáo, không thay đổi kiểu exception hoặc kết quả test.
# Cùng một vocabulary cho log, JUnit và Allure.
from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError


NETWORK_TOKENS = ("net::ERR_", "ECONNREFUSED", "ENOTFOUND", "ECONNRESET", "ETIMEDOUT")


def classify_exception(error):
    if isinstance(error, AssertionError):
        return "ASSERTION_FAILED"
    if isinstance(error, PlaywrightTimeoutError):
        return "TIMEOUT"
    if isinstance(error, PlaywrightError):
        message = error.message or ""
        if "strict mode violation" in message:
            return "LOCATOR_AMBIGUOUS"
        if any(token in message for token in NETWORK_TOKENS):
            return "NETWORK_ERROR"
        if "Target page, context or browser has been closed" in message:
            return "BROWSER_CLOSED"
        return "PLAYWRIGHT_ERROR"
    if isinstance(error, (ValueError, KeyError, TypeError)):
        return "DATA_OR_CONTRACT_ERROR"
    return "UNEXPECTED_ERROR"


def classify_report_text(text):
    """Phân loại dự phòng tại pytest hook khi chỉ còn traceback dạng chuỗi."""
    content = text or ""
    patterns = (
        ("TimeoutError", "TIMEOUT"),
        ("strict mode violation", "LOCATOR_AMBIGUOUS"),
        *((token, "NETWORK_ERROR") for token in NETWORK_TOKENS),
        ("has been closed", "BROWSER_CLOSED"),
        ("AssertionError", "ASSERTION_FAILED"),
        ("playwright._impl._errors.Error", "PLAYWRIGHT_ERROR"),
        ("ValueError", "DATA_OR_CONTRACT_ERROR"),
        ("KeyError", "DATA_OR_CONTRACT_ERROR"),
        ("TypeError", "DATA_OR_CONTRACT_ERROR"),
    )
    for token, category in patterns:
        if token in content:
            return category
    return "UNEXPECTED_ERROR"
