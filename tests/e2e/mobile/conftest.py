# ============================================================
# CẤU HÌNH MOBILE: mọi test trong tests/e2e/mobile chạy với thiết bị giả lập MOBILE_DEVICE (Pixel 7).
# Ghi đè browser_context_args (function scope) của tests/conftest.py: bỏ viewport desktop,
# thay bằng viewport / user agent / touch của thiết bị.
# ============================================================
import pytest

from config import MOBILE_DEVICE


@pytest.fixture
def browser_context_args(browser_context_args, playwright):
    args = {key: value for key, value in browser_context_args.items() if key != "viewport"}
    args.update(playwright.devices[MOBILE_DEVICE])
    return args
