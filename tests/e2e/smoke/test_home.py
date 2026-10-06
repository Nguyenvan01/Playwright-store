# ============================================================
# TEST: SMOKE - TRANG CHỦ VÀ CÁC TRANG TĨNH
# Mục tiêu: trang chủ tải đủ thành phần, không lỗi JS, menu đủ danh mục, logo, trang tĩnh
# Dữ liệu: data/catalog/categories.json, data/common/static-pages.json
# API cần quan sát: k.catalog.open_home, verify_home_loaded, k.common.verify_no_page_errors
# Kết quả mong đợi: mọi trang tải thành công, có header/footer và không có lỗi JavaScript
# ============================================================
import allure
import pytest

from utils.data_loader import load_data

CATEGORIES = load_data("catalog/categories.json")
STATIC_PAGES = load_data("common/static-pages.json")

pytestmark = pytest.mark.smoke


class TestHome:
    """Trang chủ"""

    def test_home_loaded(self, k):
        """Tải trang chủ, hiển thị header, sản phẩm và footer"""
        k.catalog.open_home()
        k.catalog.verify_home_loaded()

    def test_no_js_errors(self, k):
        """Không có lỗi JavaScript khi tải trang chủ"""
        k.catalog.open_home()
        k.common.verify_no_page_errors()

    def test_nav_has_all_categories(self, k):
        """Thanh điều hướng có đủ danh mục"""
        k.catalog.open_home()
        for c in CATEGORIES:
            k.catalog.verify_menu_link(c["nav"], c["path"])

    def test_logo_returns_home(self, k):
        """Click logo quay về trang chủ"""
        k.common.goto("/about")
        k.catalog.click_logo()
        k.common.verify_url("/")

    def test_first_product_opens_detail(self, k):
        """Click sản phẩm đầu tiên mở trang chi tiết"""
        k.catalog.open_home()
        k.catalog.open_first_product_in_list()


class TestStaticPages:
    """Các trang tĩnh"""

    @pytest.mark.parametrize("static_page", STATIC_PAGES, ids=[p["path"] for p in STATIC_PAGES])
    def test_static_page_loads(self, k, static_page):
        """{title} ({path}) tải thành công"""
        allure.dynamic.title(f"{static_page['title']} ({static_page['path']}) tải thành công")
        k.common.goto(static_page["path"])
        k.common.verify_layout_loaded()
        k.common.verify_no_page_errors()
