# ============================================================
# TEST: ĐIỀU HƯỚNG TRANG QUẢN TRỊ (DATA-DRIVEN)
# Mục tiêu: mỗi mục sidebar mở đúng trang quản trị, không lỗi JavaScript
# Dữ liệu: data/admin/menu.json (label + path của từng mục menu)
# API cần quan sát: k.admin.open_dashboard / navigate_menu / verify_admin_page
# Kết quả mong đợi: URL đúng path, có sidebar + tiêu đề trang, không có page error
# ============================================================
import allure
import pytest

from utils.data_loader import load_data

MENU = load_data("admin/menu.json")

pytestmark = pytest.mark.role("admin")


class TestAdminNavigation:
    """Điều hướng trang quản trị (data-driven)"""

    @pytest.mark.parametrize("item", [pytest.param(item, id=item["path"]) for item in MENU])
    def test_menu_opens_page(self, k, item):
        """Menu "<label>" mở <path>"""
        allure.dynamic.title(f'Menu "{item["label"]}" mở {item["path"]}')
        k.admin.open_dashboard()
        k.admin.navigate_menu(item["label"])
        k.admin.verify_admin_page(item["path"])
        k.common.verify_no_page_errors()
