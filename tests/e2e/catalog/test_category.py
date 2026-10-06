# ============================================================
# TEST: TRANG DANH MỤC (DATA-DRIVEN)
# Mục tiêu: menu header mở đúng trang danh mục; click sản phẩm mở trang chi tiết
# Dữ liệu: data/catalog/categories.json (nav, path, heading)
# API cần quan sát: k.catalog.open_category_from_menu, k.catalog.verify_category_page
# Kết quả mong đợi: URL + tiêu đề đúng, có sản phẩm hoặc thông báo rỗng
# ============================================================
import allure
import pytest

from utils.data_loader import load_data

CATEGORIES = load_data("catalog/categories.json")


class TestCategory:
    """Trang danh mục (data-driven)"""

    @pytest.mark.smoke
    @pytest.mark.parametrize("category", CATEGORIES, ids=[c["path"] for c in CATEGORIES])
    def test_menu_opens_category(self, k, category):
        """Menu "{nav}" mở {path} và hiển thị sản phẩm"""
        allure.dynamic.title(f'Menu "{category["nav"]}" mở {category["path"]} và hiển thị sản phẩm')
        k.catalog.open_home()
        k.catalog.open_category_from_menu(category["nav"])
        k.catalog.verify_category_page(category["path"], category["heading"])

    def test_click_product_opens_detail(self, k):
        """Click sản phẩm trong danh mục mở trang chi tiết"""
        c = CATEGORIES[0]
        k.common.goto(c["path"])
        k.catalog.verify_category_page(c["path"], c["heading"])
        k.catalog.open_first_product_in_list()
