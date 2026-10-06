# ============================================================
# TEST: ĐĂNG NHẬP KHÁCH HÀNG
# Mục tiêu: validate form, lỗi từ server, hiện/ẩn mật khẩu, đăng nhập thành công (mock + thật)
# Dữ liệu: data/auth/login.json (validation, wrongCredentials, mockUser)
# API cần quan sát: k.auth.*, k.common.verify_url, po.login
# Kết quả mong đợi: hiện đúng lỗi từng field; đăng nhập đúng chuyển tới /profile và lưu token
# ============================================================
import pytest
from playwright.sync_api import expect

from config import CUSTOMER
from utils.cases import case_params, require
from utils.data_loader import base_context, load_data, resolve_data

DATA = load_data("auth/login.json")


@pytest.fixture(autouse=True)
def open_login(k):
    k.auth.open_login()


class TestLoginValidation:
    """Đăng nhập khách hàng - Validate form (data-driven)"""

    @pytest.mark.parametrize("case", case_params(DATA["validation"]))
    def test_validation(self, k, case):
        k.auth.login(case["identifier"], case["password"])
        k.auth.verify_field_errors(case["errors"])


class TestLoginServerErrors:
    """Đăng nhập khách hàng - Lỗi từ server (data-driven)"""

    @pytest.mark.parametrize("case", case_params(DATA["wrongCredentials"]))
    def test_wrong_credentials(self, k, case):
        c = resolve_data(case, base_context())
        k.auth.login_expecting_error(c["identifier"], c["password"], c["error"])


class TestLogin:
    """Đăng nhập khách hàng"""

    def test_field_error_clears_on_input(self, k, po):
        """Lỗi field biến mất khi người dùng nhập lại"""
        first = DATA["validation"][0]
        k.auth.login(first["identifier"], first["password"])
        k.auth.verify_field_errors(first["errors"])

        po.login.identifier_input.fill("a")
        expect(po.login.field_error(first["errors"][0])).to_be_hidden()

    def test_toggle_password(self, k, po):
        """Nút hiện/ẩn mật khẩu"""
        po.login.password_input.fill("secret123")
        k.auth.toggle_password(True)
        k.auth.toggle_password(False)

    def test_login_success_mock(self, k):
        """Đăng nhập thành công (mock API) chuyển tới trang hồ sơ"""
        k.auth.mock_login_success(DATA["mockUser"])
        k.auth.login(DATA["mockUser"]["email"], "matkhau123")
        k.common.verify_url("/profile")
        k.auth.verify_stored_token("mock-token")

    @pytest.mark.smoke
    def test_login_success_real_account(self, k):
        """Đăng nhập thành công với tài khoản thật"""
        require("customer")
        k.auth.login(CUSTOMER["email"], CUSTOMER["password"])
        k.common.verify_url("/profile")
        k.auth.verify_logged_in_as(CUSTOMER["email"])
