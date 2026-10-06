# ASSERTION BỔ SUNG: những gì Playwright Python chưa có sẵn như bản TS.
# - poll_until  ~ expect.poll(...).toBe(true)
# - assert_subset ~ expect(actual).toMatchObject(expected)
import time

from config import EXPECT_TIMEOUT


def poll_until(condition, message, timeout=EXPECT_TIMEOUT, interval=100):
    """Gọi lại condition() tới khi trả truthy; hết timeout (ms) thì AssertionError."""
    deadline = time.monotonic() + timeout / 1000
    while True:
        value = condition()
        if value:
            return value
        if time.monotonic() >= deadline:
            raise AssertionError(f"{message} (sau {timeout}ms)")
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
