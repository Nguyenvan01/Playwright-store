# ============================================================
# TEST: API - HEALTH & HOME
# Mục tiêu: backend sống, /home trả đủ khối dữ liệu trang chủ, route lạ trả 404
# Dữ liệu: không cần (chỉ gọi API công khai)
# API cần quan sát: fixture api (utils.api_client.ApiClient)
# Kết quả mong đợi: /health 200; /home có banners/categories/featuredProducts là mảng
# ============================================================
import pytest
from playwright.sync_api import expect

# Cả describe gắn @smoke -> mọi test trong file thuộc bộ smoke.
pytestmark = pytest.mark.smoke


class TestHealthAndHome:
    """API - Health & Home"""

    def test_health_ok(self, api):
        """GET /health trả về 200"""
        res = api.get("/health")
        assert res.status == 200, f"GET /health: expected=200, actual={res.status}"

    def test_home_blocks(self, api):
        """GET /home trả đủ các khối dữ liệu trang chủ"""
        res = api.get("/home")
        expect(res).to_be_ok()
        body = res.json()
        assert body["success"] is True, f"success: expected=True, actual={body.get('success')!r}"
        for key in ("banners", "categories", "featuredProducts"):
            value = body["data"].get(key)
            assert isinstance(value, list), f"data.{key}: expected=list, actual={value!r}"

    def test_unknown_route_404(self, api):
        """Route không tồn tại trả 404"""
        res = api.get("/khong-ton-tai-e2e")
        assert res.status == 404, f"Route lạ: expected=404, actual={res.status}"
