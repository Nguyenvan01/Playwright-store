# STORAGE: localStorage, storageState và theo dõi reload của trang.
import json
import os
from urllib.parse import urlparse

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from config import AUTH_FILES, BASE_URL

# Key localStorage mà frontend đang dùng (xem src/contexts/*.jsx của app).
STORAGE_KEYS = {
    "cart": "clothing_store_cart",
    "customerToken": "clothing_store_token",
    "customerUser": "clothing_store_auth",
    "adminToken": "admin_token",
}


def write_storage_state(file, entries):
    """Tạo file storageState của Playwright trực tiếp từ các cặp key/value localStorage."""
    origin = "{0.scheme}://{0.netloc}".format(urlparse(BASE_URL))
    state = {
        "cookies": [],
        "origins": [
            {
                "origin": origin,
                "localStorage": [{"name": k, "value": v} for k, v in entries.items()],
            }
        ]
        if entries
        else [],
    }
    file.parent.mkdir(parents=True, exist_ok=True)
    # Ghi file tạm rồi đổi tên: nhiều worker xdist ghi cùng lúc không làm hỏng file.
    tmp = file.with_suffix(f".{os.getpid()}.tmp")
    tmp.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, file)


def _has_key(file, key):
    try:
        state = json.loads(file.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return False
    return any(
        entry["name"] == key and entry["value"]
        for origin in state.get("origins", [])
        for entry in origin.get("localStorage", [])
    )


def has_customer_auth():
    return _has_key(AUTH_FILES["customer"], STORAGE_KEYS["customerToken"])


def has_admin_auth():
    return _has_key(AUTH_FILES["admin"], STORAGE_KEYS["adminToken"])


def init_script(js_function, arg):
    """Python add_init_script không nhận tham số -> nhúng arg dạng JSON vào script."""
    return f"({js_function})({json.dumps(arg, ensure_ascii=False)})"


def seed_cart(page, items):
    """Đặt sẵn giỏ hàng vào localStorage TRƯỚC khi app load (chỉ ở lần điều hướng đầu tiên,
    các lần reload sau giữ nguyên giỏ hàng do app tự lưu)."""
    page.add_init_script(
        init_script(
            """({ key, value }) => {
              if (!sessionStorage.getItem('__e2e_cart_seeded')) {
                localStorage.setItem(key, value);
                sessionStorage.setItem('__e2e_cart_seeded', '1');
              }
            }""",
            {"key": STORAGE_KEYS["cart"], "value": json.dumps(items, ensure_ascii=False)},
        )
    )


def read_cart(page):
    return page.evaluate("key => JSON.parse(localStorage.getItem(key) || '[]')", STORAGE_KEYS["cart"])


class ReloadWatcher:
    """Theo dõi trang có bị điều hướng/reload trong `timeout` ms kể từ lúc tạo hay không.
    Dùng để bắt lỗi app reload làm mất trạng thái (vd: thông báo lỗi đăng nhập).

        watcher = ReloadWatcher(page)
        ... thao tác ...
        assert watcher.reloaded() is False
    """

    def __init__(self, page, timeout=3_000):
        self.page = page
        self.timeout = timeout
        self._navigated = False
        page.on("framenavigated", self._on_navigated)

    def _on_navigated(self, frame):
        if frame == self.page.main_frame:
            self._navigated = True

    def reloaded(self):
        try:
            if not self._navigated:
                self.page.wait_for_event(
                    "framenavigated",
                    predicate=lambda frame: frame == self.page.main_frame,
                    timeout=self.timeout,
                )
                self._navigated = True
        except PlaywrightTimeoutError:
            pass
        finally:
            self.page.remove_listener("framenavigated", self._on_navigated)
        return self._navigated


def detect_reload(page, timeout=3_000):
    return ReloadWatcher(page, timeout)
