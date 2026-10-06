# ============================================================
# TEST: CHUYỂN HƯỚNG TRANG TÀI KHOẢN KHI CHƯA ĐĂNG NHẬP
# Mục tiêu: các trang cần đăng nhập chuyển về /login; đăng nhập từ checkout quay lại /checkout
# Dữ liệu: data/account/redirects.json (protectedRoutes, loginReturn)
# Kết quả mong đợi: URL đúng giá trị expected của từng case
# ============================================================
import pytest

from config import CUSTOMER
from utils.cases import case_params
from utils.data_loader import load_data

DATA = load_data("account/redirects.json")


class TestAccountRedirects:
    """Chuyển hướng trang tài khoản khi chưa đăng nhập"""

    @pytest.mark.parametrize("case", case_params(DATA["protectedRoutes"]))
    def test_protected_route(self, k, case):
        """Trang cần đăng nhập (data-driven)"""
        k.common.goto(case["path"])
        k.common.verify_url(case["expected"])

    @pytest.mark.parametrize("case", case_params([DATA["loginReturn"]]))
    def test_login_return_to_checkout(self, k, case):
        """Bấm Đăng nhập ở trang thanh toán, đăng nhập xong quay lại /checkout"""
        k.cart.seed_cart([case["cartItem"]])
        k.checkout.open_checkout()
        k.account.go_to_login_from_checkout()
        k.auth.login(CUSTOMER["email"], CUSTOMER["password"])
        k.common.verify_url(case["expected"])
