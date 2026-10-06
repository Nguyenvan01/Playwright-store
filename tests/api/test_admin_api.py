# ============================================================
# TEST: API ADMIN (ĐÃ ĐĂNG NHẬP, CHỈ ĐỌC) + BẢO MẬT UPLOAD
# Mục tiêu: các endpoint đọc của admin trả đúng shape, chi tiết theo id khớp danh sách,
#           id không tồn tại trả 404; /admin/upload phải yêu cầu đăng nhập
# Dữ liệu: data/api/admin.json (readEndpoints, detailEndpoints, notFound)
# API cần quan sát: fixture api, fixture admin_headers (đăng nhập admin 1 lần / module)
# Kết quả mong đợi: khớp từng case; bug đã biết đánh dấu xfail(strict)
# ============================================================
import allure
import pytest
from playwright.sync_api import expect

from config import ADMIN, API_URL
from utils.cases import case_params, case_title
from utils.data_loader import load_data

DATA = load_data("api/admin.json")

needs_admin = pytest.mark.skipif(not ADMIN["email"], reason="Cần E2E_ADMIN_EMAIL/PASSWORD")


@pytest.fixture(scope="module")
def admin_headers(playwright):
    """Đăng nhập admin 1 lần cho cả module (tương đương beforeAll của TS)."""
    request = playwright.request.new_context()
    try:
        res = request.post(
            f"{API_URL}/admin/login",
            data={"email": ADMIN["email"], "password": ADMIN["password"]},
        )
        return {"Authorization": f"Bearer {res.json().get('token')}"}
    finally:
        request.dispose()


@needs_admin
class TestAdminReadEndpoints:
    """API admin (đã đăng nhập, chỉ đọc) - Danh sách / thống kê (data-driven)"""

    @pytest.mark.parametrize("case", case_params(DATA["readEndpoints"]))
    def test_read_endpoint(self, api, admin_headers, case):
        """Endpoint đọc của admin trả đủ trường (data-driven)"""
        allure.dynamic.title(f"{case_title(case)} - GET {case['path']}")
        res = api.get(case["path"], headers=admin_headers)
        expect(res).to_be_ok()
        body = res.json()
        for key in case["keys"]:
            assert key in body, f'thiếu trường "{key}"; các trường có: {sorted(body)}'


@needs_admin
class TestAdminDetailEndpoints:
    """API admin (đã đăng nhập, chỉ đọc) - Chi tiết theo id (data-driven)"""

    @pytest.mark.parametrize("case", case_params(DATA["detailEndpoints"]))
    def test_detail_by_id(self, api, admin_headers, case):
        """Chi tiết theo id khớp bản ghi đầu danh sách (data-driven)"""
        listing = api.get(case["list"], headers=admin_headers).json()
        items = listing.get(case["listKey"]) or []
        first = items[0] if items else None
        if not first:
            pytest.skip(f"Chưa có dữ liệu {case['listKey']} để kiểm tra")

        res = api.get(case["detail"].replace("{id}", str(first["id"])), headers=admin_headers)
        expect(res).to_be_ok()
        body = res.json()
        actual = (body.get(case["key"]) or {}).get("id")
        assert actual == first["id"], f"{case['key']}.id: expected={first['id']!r}, actual={actual!r}"


@needs_admin
class TestAdminNotFound:
    """API admin (đã đăng nhập, chỉ đọc) - Id không tồn tại (data-driven)"""

    @pytest.mark.parametrize("case", case_params(DATA["notFound"]))
    def test_not_found(self, api, admin_headers, case):
        """Id không tồn tại trả 404 (data-driven)"""
        allure.dynamic.title(f"{case_title(case)} - GET {case['path']}")
        res = api.get(case["path"], headers=admin_headers)
        assert res.status == 404, f"{case['path']}: expected=404, actual={res.status}"
        success = res.json().get("success")
        assert success is False, f"success: expected=False, actual={success!r}"


@pytest.mark.security
class TestAdminUploadSecurity:
    """API admin - bảo mật upload"""

    # routes/admin.js khai báo POST /upload TRƯỚC router.use(authMiddleware) -> ai cũng upload được.
    def test_upload_requires_token(self, api):
        """POST /admin/upload không có token phải trả 401"""
        res = api.post("/admin/upload")
        assert res.status == 401, f"Endpoint upload xử lý request không cần đăng nhập: expected=401, actual={res.status}"
