# ============================================================
# DEMO: VÒNG ĐỜI BROWSER + WRITE GUARD (OFFLINE)
# Mục tiêu: kiểm tra fixture page/k của conftest mà không cần app thật
# Kịch bản: trang giả http://e2e.local phục vụ bằng page.route; gọi fetch từ trang
# Kết quả mong đợi: GET đi qua; POST bị write guard chặn (418) khi E2E_ALLOW_WRITE=0;
#                   mock của test (đăng ký sau) được ưu tiên hơn guard
# ============================================================
import pytest

from config import ALLOW_WRITE

pytestmark = pytest.mark.core

ORIGIN = "http://e2e.local"
FETCH = """async ([url, method]) => {
  const res = await fetch(url, { method, headers: { 'Content-Type': 'application/json' },
                                 body: method === 'GET' ? undefined : JSON.stringify({ a: 1 }) });
  return [res.status, await res.json()];
}"""


@pytest.fixture
def fake_site(page):
    """Trang + API giả; request ghi được fallback xuống write guard."""
    def serve(route):
        if route.request.method != "GET":
            return route.fallback()
        if "/api/" in route.request.url:
            return route.fulfill(json={"success": True, "data": []})
        return route.fulfill(content_type="text/html", body="<h1>E2E</h1><footer>f</footer>")

    page.route(f"{ORIGIN}/**", serve)
    page.goto(f"{ORIGIN}/")
    return page


def test_get_passes_write_guard(fake_site):
    """GET không bị write guard chặn"""
    status, body = fake_site.evaluate(FETCH, [f"{ORIGIN}/api/products", "GET"])
    assert (status, body["success"]) == (200, True)


@pytest.mark.skipif(ALLOW_WRITE, reason="Chỉ kiểm tra khi E2E_ALLOW_WRITE=0")
def test_write_is_blocked(fake_site):
    """POST bị chặn với 418 khi chưa cho phép ghi dữ liệu thật"""
    status, body = fake_site.evaluate(FETCH, [f"{ORIGIN}/api/orders", "POST"])
    assert status == 418, f"status: expected=418, actual={status}"
    assert "Đã chặn ghi dữ liệu thật" in body["message"]


def test_mock_write_has_priority_and_is_captured(k, fake_site):
    """mockWrite của test được ưu tiên hơn write guard và lưu lại body request"""
    k.common.mock_write("POST", "**/api/orders", {"success": True, "order_number": "X1"}, 201)
    status, body = fake_site.evaluate(FETCH, [f"{ORIGIN}/api/orders", "POST"])
    assert (status, body["order_number"]) == (201, "X1")
    k.common.verify_request("POST", "/api/orders", {"a": 1})
    k.common.verify_no_request("DELETE", "/api/orders")


def test_keyword_step_failure_keeps_original_error(k, fake_site):
    """Keyword thất bại ném lại AssertionError gốc (không đổi thành boolean)"""
    with pytest.raises(AssertionError):
        k.common.verify_request("PUT", "/api/never")
