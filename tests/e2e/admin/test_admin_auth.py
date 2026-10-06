# ============================================================
# TEST: ĐĂNG NHẬP TRANG QUẢN TRỊ
# Mục tiêu: chặn truy cập /admin khi chưa đăng nhập, báo lỗi sai mật khẩu, link về cửa hàng, đăng nhập thành công
# Dữ liệu: tài khoản admin trong .env (E2E_ADMIN_EMAIL/PASSWORD), thông báo lỗi trong utils/messages.py
# API cần quan sát: k.admin.*, k.common.goto / verify_url
# Kết quả mong đợi: chưa đăng nhập bị về /admin/login; đăng nhập đúng vào Dashboard /admin
# ============================================================
import pytest

from utils.cases import known_bug, require
from utils.messages import MSG


class TestAdminLogin:
    """Đăng nhập trang quản trị"""

    @pytest.mark.smoke
    def test_redirect_to_login_when_not_logged_in(self, k):
        """Chưa đăng nhập vào /admin bị chuyển về /admin/login"""
        k.common.goto("/admin/products")
        k.admin.verify_on_admin_login()

    def test_wrong_password_shows_error(self, k, request):
        """Sai mật khẩu hiển thị lỗi"""
        known_bug(
            request,
            "interceptor 401 trong services/api.js reload sang /admin/login nên thông báo lỗi bị mất",
        )
        k.admin.open_admin_login()
        k.admin.login_admin_expecting_error(
            "admin@clothing-store.vn", "sai-mat-khau-e2e", MSG["login"]["wrongCredentials"]
        )

    def test_back_to_store_link(self, k):
        """Link "Quay về cửa hàng" về trang chủ"""
        k.admin.open_admin_login()
        k.admin.back_to_store()
        k.common.verify_url("/")

    def test_login_success_to_dashboard(self, k):
        """Đăng nhập thành công vào Dashboard"""
        require("admin")
        k.admin.login_as_admin()
        k.admin.verify_admin_page("/admin")
