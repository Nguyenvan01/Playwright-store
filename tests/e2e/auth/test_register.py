# ============================================================
# TEST: ĐĂNG KÝ TÀI KHOẢN
# Mục tiêu: chuyển form Đăng nhập/Đăng ký, validate form, lỗi server (mock), đăng ký thật
# Dữ liệu: data/auth/register.json (validation, serverErrors); khách hàng sinh bởi build_customer
# API cần quan sát: k.auth.open_register_form, k.auth.submit_register_form, po.login
# Kết quả mong đợi: hiện đúng lỗi field / lỗi chung; đăng ký thành công chuyển tới /profile
# ============================================================
import pytest
from playwright.sync_api import expect

from utils.cases import case_params, require
from utils.data_loader import base_context, load_data, resolve_data
from utils.factories import build_customer

DATA = load_data("auth/register.json")


@pytest.fixture(autouse=True)
def open_register(k):
    k.auth.open_login()
    k.auth.open_register_form()


class TestRegister:
    """Đăng ký tài khoản"""

    def test_switch_login_register(self, k, po):
        """Chuyển qua lại giữa Đăng nhập và Đăng ký"""
        expect(po.login.name_input).to_be_visible()
        po.login.switch_to_login.click()
        expect(po.login.heading).to_have_text("Đăng nhập")
        expect(po.login.name_input).to_be_hidden()
        k.auth.open_register_form()

    def test_register_success_real(self, k):
        """Đăng ký thành công tạo tài khoản thật"""
        require("allowWrite")
        k.auth.submit_register_form(build_customer())
        k.common.verify_url("/profile")


class TestRegisterValidation:
    """Đăng ký tài khoản - Validate form (data-driven)"""

    @pytest.mark.parametrize("case", case_params(DATA["validation"]))
    def test_validation(self, k, case):
        c = resolve_data(case, base_context())
        k.auth.submit_register_form(c["form"])
        k.auth.verify_field_errors(c["errors"])


class TestRegisterServerErrors:
    """Đăng ký tài khoản - Lỗi từ server (mock, data-driven)"""

    @pytest.mark.parametrize("case", case_params(DATA["serverErrors"]))
    def test_server_error(self, k, case):
        k.auth.mock_register_error(case["status"], case["message"])
        k.auth.submit_register_form(build_customer())
        k.auth.verify_general_error(case["message"])
