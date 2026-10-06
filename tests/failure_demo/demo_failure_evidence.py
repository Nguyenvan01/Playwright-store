# ============================================================
# DEMO CÓ CHỦ ĐÍCH FAIL: FAILURE EVIDENCE (OFFLINE)
# Chạy riêng để quan sát screenshot, page source, URL, log và Allure:
#   python -m pytest tests/failure_demo/demo_failure_evidence.py
# File không khớp python_files=test_*.py nên không làm đỏ suite mặc định.
# ============================================================
import pytest

pytestmark = pytest.mark.failure_demo


def test_intentional_wrong_badge(k, page):
    """Badge giỏ hàng sai số lượng (cố tình FAIL)"""
    page.route(
        "http://e2e.local/**",
        lambda route: route.fulfill(
            content_type="text/html",
            body="<header><button><svg><circle cx='8' cy='21'/></svg>"
                 "<span class='rounded-full'>2</span></button></header>",
        ),
    )
    page.goto("http://e2e.local/")
    k.cart.verify_cart_badge(5)
