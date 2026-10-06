# ============================================================
# TEST: HỒ SƠ CÁ NHÂN
# Mục tiêu: hiển thị thông tin, chỉnh sửa hồ sơ, đổi mật khẩu, tổng quan tài khoản
# Dữ liệu: data/account/profile.json, orders.json, wishlist.json, addresses.json
#          (GET được mock bằng JSON; mọi request ghi đều mock + kiểm tra payload)
# Kết quả mong đợi: thông tin / thống kê khớp dữ liệu; payload PUT đúng; lỗi hiển thị đúng
# Lưu ý: luôn vào qua menu tài khoản (mở trực tiếp /profile bị crash - xem test_account.py)
# ============================================================
import pytest

from config import CUSTOMER
from tests.e2e.account.support import API, mock_account_data
from utils.cases import case_params, known_bug
from utils.data_loader import load_data

PROFILE = load_data("account/profile.json")
ORDERS = load_data("account/orders.json")
WISHLIST = load_data("account/wishlist.json")
ADDRESSES = load_data("account/addresses.json")
GOLD = PROFILE["responses"]["gold"]
GOLD_USER = GOLD["user"]

pytestmark = pytest.mark.role("customer")


class TestProfile:
    """Hồ sơ cá nhân"""

    def test_real_profile_shows_email(self, k):
        """[ACC-PRF-R01] Dữ liệu thật: hồ sơ hiển thị email tài khoản test"""
        k.account.open_profile_from_menu()
        k.account.verify_profile_fields({"Email": CUSTOMER["email"]})


class TestProfileDisplay:
    """Hồ sơ cá nhân - Hiển thị thông tin tài khoản (data-driven)"""

    @pytest.mark.parametrize("case", case_params(PROFILE["display"]))
    def test_display(self, k, case):
        """Hiển thị thông tin tài khoản (data-driven)"""
        mock_account_data(k, profile=PROFILE["responses"][case["response"]])
        k.account.open_profile_from_menu()
        k.account.verify_profile_fields(case["expected"])


class TestProfileEdit:
    """Hồ sơ cá nhân - Chỉnh sửa hồ sơ"""

    @pytest.fixture(autouse=True)
    def mocked_profile(self, k):
        mock_account_data(k, profile=GOLD)

    @pytest.mark.parametrize("case", case_params(PROFILE["edit"]))
    def test_edit(self, k, case):
        """Chỉnh sửa hồ sơ (data-driven)"""
        k.common.mock_write("PUT", API["profile"], {"success": True, "user": {**GOLD_USER, **case["expectedBody"]}})
        k.account.open_profile_from_menu()
        k.account.start_edit_profile()
        k.account.fill_profile_form(case["form"])
        k.account.save_profile()
        k.common.verify_request("PUT", "/api/profile", case["expectedBody"])
        k.account.verify_profile_editing(False)
        k.account.verify_profile_fields(case["expectedView"])

    @pytest.mark.parametrize("case", case_params([PROFILE["editServerError"]]))
    def test_edit_server_error(self, k, case):
        """Lỗi server khi lưu hồ sơ hiển thị thông báo lỗi"""
        k.common.mock_write("PUT", API["profile"], {"success": False, "message": case["message"]}, case["status"])
        k.account.open_profile_from_menu()
        k.account.start_edit_profile()
        k.account.fill_profile_form(case["form"])
        k.account.save_profile()
        k.common.verify_request("PUT", "/api/profile", {"name": case["form"]["name"]})
        k.common.verify_text_visible(case["message"])

    def test_edit_form_prefilled(self, k):
        """[ACC-PRF-E04] Form sửa điền sẵn dữ liệu hiện tại, ô Email bị khóa"""
        k.account.open_profile_from_menu()
        k.account.start_edit_profile()
        k.account.verify_profile_editing(True)
        k.account.verify_profile_email_locked(GOLD_USER["email"])
        k.account.verify_profile_form(
            {
                "name": GOLD_USER["name"],
                "phone": GOLD_USER["phone"],
                "birthDate": GOLD_USER["birthDate"],
                "gender": GOLD_USER["gender"],
            }
        )

    def test_cancel_edit(self, k):
        """[ACC-PRF-E05] Hủy sửa: không gửi request, giữ nguyên thông tin, mở lại form thấy giá trị cũ"""
        k.common.mock_write("PUT", API["profile"], GOLD)
        k.account.open_profile_from_menu()
        k.account.start_edit_profile()
        k.account.fill_profile_form({"name": "Tên Sẽ Bị Hủy", "phone": "0999999999"})
        k.account.cancel_edit_profile()
        k.account.verify_profile_editing(False)
        k.common.verify_no_request("PUT", "/api/profile")
        k.account.verify_profile_fields({"Họ và tên": GOLD_USER["name"], "Số điện thoại": GOLD_USER["phone"]})
        k.account.start_edit_profile()
        k.account.verify_profile_form({"name": GOLD_USER["name"], "phone": GOLD_USER["phone"]})


class TestChangePassword:
    """Hồ sơ cá nhân - Đổi mật khẩu"""

    @pytest.fixture(autouse=True)
    def opened_profile(self, k):
        mock_account_data(k, profile=GOLD)
        k.account.open_profile_from_menu()

    @pytest.mark.parametrize("case", case_params(PROFILE["password"]["validation"]))
    def test_client_validation(self, k, case):
        """Validate phía client (data-driven)"""
        k.common.mock_write("PUT", API["changePassword"], {"success": True})
        k.account.open_change_password()
        k.account.fill_change_password(case["form"])
        k.account.submit_change_password()
        k.account.verify_change_password_error(case["error"])
        k.common.verify_no_request("PUT", "/api/profile/change-password")

    @pytest.mark.parametrize("case", case_params(PROFILE["password"]["serverErrors"]))
    def test_server_error(self, k, case):
        """Lỗi từ server (mock, data-driven)"""
        k.common.mock_write(
            "PUT", API["changePassword"], {"success": False, "message": case["message"]}, case["status"]
        )
        k.account.open_change_password()
        k.account.fill_change_password(case["form"])
        k.account.submit_change_password()
        k.common.verify_request(
            "PUT",
            "/api/profile/change-password",
            {"currentPassword": case["form"]["currentPassword"], "newPassword": case["form"]["newPassword"]},
        )
        k.account.verify_change_password_error(case["message"])

    @pytest.mark.smoke
    def test_change_password_success(self, k):
        """[ACC-PWD-01] Đổi mật khẩu thành công: gửi đúng payload và đóng modal"""
        form = PROFILE["password"]["success"]
        k.common.mock_write("PUT", API["changePassword"], {"success": True, "message": "Đổi mật khẩu thành công"})
        k.account.open_change_password()
        k.account.verify_change_password_form_empty()
        k.account.fill_change_password(form)
        k.account.submit_change_password()
        k.common.verify_request(
            "PUT",
            "/api/profile/change-password",
            {"currentPassword": form["currentPassword"], "newPassword": form["newPassword"]},
        )
        k.account.verify_change_password_closed()

    def test_close_and_cancel(self, k):
        """[ACC-PWD-02] Nút Đóng và nút Hủy đều đóng modal, không gửi request"""
        k.common.mock_write("PUT", API["changePassword"], {"success": True})
        k.account.open_change_password()
        k.account.close_change_password()
        k.account.verify_change_password_closed()
        k.account.open_change_password()
        k.account.fill_change_password(PROFILE["password"]["success"])
        k.account.cancel_change_password()
        k.account.verify_change_password_closed()
        k.common.verify_no_request("PUT", "/api/profile/change-password")

    def test_reopen_after_cancel_is_empty(self, k, request):
        """[ACC-PWD-03] Mở lại modal sau khi Hủy thì form trống, không còn lỗi cũ"""
        known_bug(
            request,
            "ProfilePage.jsx:33-37 - PasswordModal luôn được mount, state form/error giữ nguyên khi đóng "
            "(chỉ reset sau khi đổi thành công) -> mở lại vẫn thấy mật khẩu cũ và lỗi cũ",
        )
        invalid = PROFILE["password"]["validation"][1]
        k.account.open_change_password()
        k.account.fill_change_password(invalid["form"])
        k.account.submit_change_password()
        k.account.verify_change_password_error(invalid["error"])
        k.account.cancel_change_password()
        k.account.open_change_password()
        k.account.verify_change_password_form_empty()


class TestProfileOverview:
    """Hồ sơ cá nhân - Tổng quan tài khoản"""

    @pytest.mark.smoke
    def test_overview(self, k):
        """[ACC-PRF-S01] Thống kê, đơn gần đây, yêu thích gần đây, địa chỉ mặc định"""
        mock_account_data(
            k,
            profile=GOLD,
            orders=ORDERS["list"],
            wishlist=WISHLIST["response"],
            addresses=ADDRESSES["list"],
        )
        k.account.open_profile_from_menu()
        k.account.verify_profile_summary(PROFILE["summary"])
        k.account.verify_recent_orders(PROFILE["recentOrders"])
        k.account.verify_recent_favorites(PROFILE["recentFavorites"])
        k.account.verify_default_address(PROFILE["defaultAddressText"])

    def test_overview_empty_account(self, k):
        """[ACC-PRF-S02] Tài khoản chưa có dữ liệu: thống kê 0 và các thông báo trống"""
        mock_account_data(k, profile=PROFILE["responses"]["basic"])
        k.account.open_profile_from_menu()
        k.account.verify_profile_summary({"Tổng đơn hàng": "0", "Đơn đang xử lý": "0", "Sản phẩm yêu thích": "0"})
        k.account.verify_recent_orders([])
        k.account.verify_recent_favorites([])
        k.account.verify_default_address(["Bạn chưa cập nhật địa chỉ giao hàng"])

    def test_total_orders_counts_all(self, k, request):
        """[ACC-PRF-S03] Tổng đơn hàng đếm đủ mọi đơn (tài khoản có 12 đơn)"""
        known_bug(
            request,
            "ProfilePage.jsx:185 chỉ lấy 10 đơn (limit 10) và ProfileSummary.jsx:22 đếm orders.length "
            'thay vì pagination.total -> "Tổng đơn hàng" tối đa là 10',
        )
        mock_account_data(k, profile=GOLD, orders=ORDERS["profileFirstPage"])
        k.account.open_profile_from_menu()
        k.account.verify_profile_summary({"Tổng đơn hàng": ORDERS["profileTotalOrders"]})

    def test_update_address_link(self, k):
        """[ACC-PRF-S04] Nút Cập nhật địa chỉ dẫn tới sổ địa chỉ"""
        mock_account_data(k, profile=GOLD, addresses=ADDRESSES["list"])
        k.account.open_profile_from_menu()
        k.account.click_update_address()
        k.account.verify_address_list(ADDRESSES["names"])
