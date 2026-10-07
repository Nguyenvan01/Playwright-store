# ASSERTION BỔ SUNG: những gì Playwright Python chưa có sẵn như bản TS.
# - poll_until  ~ expect.poll(...).toBe(true)
# - assert_subset ~ expect(actual).toMatchObject(expected)
import time
from contextvars import ContextVar

from config import EXPECT_TIMEOUT

# Page của test đang chạy (conftest đặt). Playwright sync chỉ xử lý sự kiện (page.on("request"),
# route handler...) khi đang chờ 1 lệnh Playwright -> phải chờ bằng page.wait_for_timeout,
# time.sleep sẽ "đóng băng" mọi sự kiện trong lúc poll.
current_page = ContextVar("current_page", default=None)


def poll_until(condition, message, timeout=EXPECT_TIMEOUT, interval=100):
    """Gọi lại condition() tới khi trả truthy; hết timeout (ms) thì AssertionError."""
    deadline = time.monotonic() + timeout / 1000
    while True:
        value = condition()
        if value:
            return value
        if time.monotonic() >= deadline:
            raise AssertionError(f"{message} (sau {timeout}ms)")
        page = current_page.get()
        if page is not None and not page.is_closed():
            page.wait_for_timeout(interval)
        else:
            time.sleep(interval / 1000)


def is_subset(expected, actual):
    """True nếu mọi khóa/giá trị trong expected có trong actual (đệ quy, như toMatchObject)."""
    if isinstance(expected, dict):
        return isinstance(actual, dict) and all(
            key in actual and is_subset(value, actual[key]) for key, value in expected.items()
        )
    if isinstance(expected, list):
        return (
            isinstance(actual, list)
            and len(expected) == len(actual)
            and all(is_subset(e, a) for e, a in zip(expected, actual))
        )
    return expected == actual


def assert_subset(actual, expected, message=""):
    assert is_subset(expected, actual), (
        f"{message + ': ' if message else ''}expected subset={expected!r}, actual={actual!r}"
    )
