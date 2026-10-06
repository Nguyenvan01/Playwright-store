# ============================================================
# TEST: TÀI KHOẢN KHÁCH HÀNG (ĐIỀU HƯỚNG CƠ BẢN)
# Mục tiêu: vào hồ sơ / đơn hàng / yêu thích qua menu, /login khi đã đăng nhập, đăng xuất
# Dữ liệu: tài khoản test thật (CUSTOMER trong .env, phiên đăng nhập qua marker role)
# Kết quả mong đợi: điều hướng đúng URL, trang tài khoản tải xong; chưa đăng nhập -> /login
# ============================================================
import pytest

from config import CUSTOMER
from utils.cases import known_bug


@pytest.mark.role("customer")
class TestCustomerAccount:
    """Tài khoản khách hàng (đã đăng nhập)"""

    def test_open_profile_directly(self, k, request):
        """Mở trực tiếp /profile (F5, bookmark) hiển thị thông tin tài khoản"""
        known_bug(request, "profileToForm(null) ở lần render đầu -> crash 'Cannot read properties of null (reading name)'")
        k.account.open_profile()
        k.account.verify_profile_loaded()

    @pytest.mark.smoke
    def test_profile_from_menu(self, k):
        """Vào hồ sơ qua menu tài khoản hiển thị thông tin"""
        k.catalog.open_home()
        k.account.open_account_menu_link("Hồ sơ cá nhân")
        k.common.verify_url("/profile")
        k.account.verify_profile_loaded()

    def test_login_redirects_to_profile(self, k):
        """Vào /login khi đã đăng nhập sẽ chuyển sang /profile"""
        k.common.goto("/login")
        k.common.verify_url("/profile")

    def test_menu_orders_and_wishlist(self, k):
        """Menu tài khoản điều hướng tới Đơn hàng và Yêu thích"""
        k.catalog.open_home()
        k.auth.verify_logged_in_as(CUSTOMER["email"])
        k.account.open_account_menu_link("Đơn hàng của tôi")
        k.common.verify_url("/orders")
        k.account.verify_orders_loaded()
        k.account.open_account_menu_link("Yêu thích")
        k.common.verify_url("/favorites")
        k.account.verify_wishlist_loaded()

    def test_logout(self, k):
        """Đăng xuất xóa token và về trang chủ"""
        k.catalog.open_home()
        k.auth.logout()
        k.auth.verify_logged_out()


def test_account_icon_guest(k):
    """Chưa đăng nhập: icon tài khoản dẫn tới trang đăng nhập"""
    k.catalog.open_home()
    k.account.click_account_icon()
    k.common.verify_url("/login")
