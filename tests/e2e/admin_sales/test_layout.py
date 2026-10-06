# ============================================================
# TEST: ADMIN - KHUNG TRANG (SIDEBAR, HEADER, THÔNG BÁO)
# Mục tiêu: tiêu đề header theo trang, thu gọn sidebar, mục đang chọn, chân sidebar,
#           menu người dùng, chuông thông báo (mock GET /admin/notifications)
# Dữ liệu: data/admin-sales/layout.json
# Kết quả mong đợi: tiêu đề/menu/panel thông báo hiển thị đúng; đăng xuất về /admin/login
# ============================================================
import pytest

from utils.cases import case_params
from utils.data_loader import load_data

DATA = load_data("admin-sales/layout.json")
NOTI = "**/api/admin/notifications"

pytestmark = pytest.mark.role("admin")


class TestHeaderTitles:
    """Admin - khung trang: Tiêu đề trang trên header (data-driven)"""

    @pytest.mark.parametrize("case", case_params(DATA["titles"]))
    def test_header_title(self, k, case):
        k.common.goto(case["path"])
        k.admin.verify_header_title(case["expect"])


class TestSidebar:
    """Admin - khung trang: Sidebar"""

    @pytest.mark.smoke
    def test_collapse_and_expand_sidebar(self, k):
        """[ADS-LAY-S01] Thu gọn rồi mở rộng sidebar"""
        k.admin.open_admin_page("/admin/products", "Sản phẩm")
        k.admin_sales.verify_sidebar_collapsed(False)
        k.admin_sales.toggle_sidebar()
        k.admin_sales.verify_sidebar_collapsed(True)
        k.admin_sales.toggle_sidebar()
        k.admin_sales.verify_sidebar_collapsed(False)

    @pytest.mark.parametrize("case", case_params(DATA["activeMenu"]))
    def test_active_menu(self, k, case):
        k.common.goto(case["path"])
        k.admin_sales.verify_active_menu(case["active"])

    def test_sidebar_user(self, k):
        """[ADS-LAY-S02] Chân sidebar hiển thị tên + vai trò tài khoản đang đăng nhập"""
        k.common.mock_get("**/api/admin/profile", DATA["profile"])
        k.admin.open_admin_page("/admin/brands", "Thương hiệu")
        k.admin_sales.verify_sidebar_user(DATA["profile"]["user"]["name"], DATA["profile"]["user"]["role"])

    def test_view_store(self, k):
        """[ADS-LAY-S03] "Xem cửa hàng" về trang chủ"""
        k.admin.open_admin_page("/admin/brands", "Thương hiệu")
        k.admin_sales.click_view_store()
        k.common.verify_url("/")
        k.common.verify_layout_loaded()

    def test_sidebar_logout(self, k):
        """[ADS-LAY-S04] "Đăng xuất" ở sidebar về trang đăng nhập admin"""
        k.admin.open_admin_page("/admin/brands", "Thương hiệu")
        k.admin_sales.logout("sidebar")
        k.admin.verify_on_admin_login()
        # Token đã bị xóa -> vào lại trang quản trị bị chặn
        k.common.goto("/admin/products")
        k.admin.verify_on_admin_login()


class TestUserMenu:
    """Admin - khung trang: Menu người dùng"""

    def test_user_menu_open_and_close(self, k):
        """[ADS-LAY-U00] Mở menu hiển thị tên, email và 3 mục; bấm ra ngoài thì đóng"""
        user = DATA["profile"]["user"]
        k.common.mock_get("**/api/admin/profile", DATA["profile"])
        k.admin.open_admin_page("/admin/brands", "Thương hiệu")
        k.admin_sales.open_user_menu()
        k.admin_sales.verify_user_menu(user["name"], user["email"], user["role"])
        k.admin_sales.click_outside_user_menu()
        k.admin_sales.verify_user_menu_open(False)

    @pytest.mark.parametrize("case", case_params(DATA["userMenu"]))
    def test_user_menu_item(self, k, case):
        k.common.goto(case["from"])
        k.admin_sales.open_user_menu()
        k.admin_sales.choose_user_menu_item(case["item"])
        k.common.verify_url(case["path"])
        k.admin.verify_header_title(case["pageTitle"])
        k.admin_sales.verify_user_menu_open(False)

    def test_user_menu_logout(self, k):
        """[ADS-LAY-U03] "Đăng xuất" trong menu người dùng về trang đăng nhập admin"""
        k.admin.open_admin_page("/admin/brands", "Thương hiệu")
        k.admin_sales.logout("menu")
        k.admin.verify_on_admin_login()


class TestNotifications:
    """Admin - khung trang: Chuông thông báo (mock GET /admin/notifications)"""

    @pytest.mark.parametrize("case", case_params(DATA["notifications"]["badges"]))
    def test_notification_badge(self, k, case):
        k.common.mock_get(NOTI, DATA["notifications"][case["response"]])
        k.admin.open_admin_page("/admin/brands", "Thương hiệu")
        k.admin_sales.verify_api_requested("/admin/notifications")
        k.admin_sales.verify_notification_badge(case["badge"])

    def test_empty_panel(self, k):
        """[ADS-NOTI-01] Không có thông báo -> panel trống"""
        k.common.mock_get(NOTI, DATA["notifications"]["empty"])
        k.admin.open_admin_page("/admin/brands", "Thương hiệu")
        k.admin_sales.open_notifications()
        k.admin_sales.verify_notifications_empty()
        k.admin_sales.verify_new_notification_chip(None)

    @pytest.mark.smoke
    def test_panel_list_stats_total(self, k):
        """[ADS-NOTI-02] Panel hiển thị danh sách, thống kê và tổng số thông báo"""
        k.common.mock_get(NOTI, DATA["notifications"]["some"])
        k.admin.open_admin_page("/admin/brands", "Thương hiệu")
        k.admin_sales.open_notifications()
        k.admin_sales.verify_notification_panel(DATA["notifications"]["panel"])

    def test_mark_all_read(self, k):
        """[ADS-NOTI-03] "Đánh dấu đã đọc" ẩn nhãn "n mới\""""
        k.common.mock_get(NOTI, DATA["notifications"]["some"])
        k.admin.open_admin_page("/admin/brands", "Thương hiệu")
        k.admin_sales.open_notifications()
        k.admin_sales.verify_new_notification_chip(DATA["notifications"]["panel"]["newChip"])
        k.admin_sales.mark_all_notifications_read()
        k.admin_sales.verify_new_notification_chip(None)

    def test_click_notification_navigates(self, k):
        """[ADS-NOTI-04] Bấm 1 thông báo -> điều hướng theo link và đóng panel"""
        target = DATA["notifications"]["clickItem"]
        k.common.mock_get(NOTI, DATA["notifications"]["some"])
        k.admin.open_admin_page("/admin/brands", "Thương hiệu")
        k.admin_sales.open_notifications()
        k.admin_sales.click_notification(target["title"])
        k.common.verify_url(target["path"])
        k.admin.verify_header_title(target["pageTitle"])
        k.admin_sales.verify_notification_panel_open(False)

    def test_view_all_orders(self, k):
        """[ADS-NOTI-05] "Xem tất cả đơn hàng" -> /admin/orders"""
        k.common.mock_get(NOTI, DATA["notifications"]["some"])
        k.admin.open_admin_page("/admin/brands", "Thương hiệu")
        k.admin_sales.open_notifications()
        k.admin_sales.click_view_all_orders()
        k.common.verify_url("/admin/orders")
        k.admin_sales.verify_notification_panel_open(False)

    def test_refresh_notifications(self, k):
        """[ADS-NOTI-06] "Làm mới" gọi lại API thông báo"""
        k.common.mock_get(NOTI, DATA["notifications"]["some"])
        k.admin.open_admin_page("/admin/brands", "Thương hiệu")
        k.admin_sales.open_notifications()
        k.admin_sales.verify_notification_panel(DATA["notifications"]["panel"])
        k.admin_sales.refresh_notifications()

    def test_close_panel(self, k):
        """[ADS-NOTI-07] Đóng panel bằng nút X và bằng bấm ra ngoài"""
        k.common.mock_get(NOTI, DATA["notifications"]["empty"])
        k.admin.open_admin_page("/admin/brands", "Thương hiệu")
        k.admin_sales.open_notifications()
        k.admin_sales.close_notifications("button")
        k.admin_sales.verify_notification_panel_open(False)
        k.admin_sales.open_notifications()
        k.admin_sales.close_notifications("overlay")
        k.admin_sales.verify_notification_panel_open(False)
