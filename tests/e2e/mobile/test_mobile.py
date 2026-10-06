# ============================================================
# TEST: GIAO DIỆN MOBILE (Pixel 7 - xem tests/e2e/mobile/conftest.py)
# Mục tiêu: trang chủ trên mobile, menu hamburger, không tràn ngang
# Dữ liệu: data/catalog/categories.json (danh mục đầu tiên)
# API cần quan sát: k.catalog.open_category_from_mobile_menu, k.common.verify_no_horizontal_overflow
# Kết quả mong đợi: menu desktop ẩn, menu mobile điều hướng được, trang không rộng hơn màn hình
# ============================================================
from playwright.sync_api import expect

from utils.cases import known_bug
from utils.data_loader import load_data

FIRST_CATEGORY = load_data("catalog/categories.json#0")


class TestMobile:
    """Giao diện mobile"""

    def test_home_hides_desktop_nav(self, k, po):
        """Trang chủ hiển thị, menu desktop bị ẩn"""
        k.catalog.open_home()
        expect(po.header.logo).to_be_visible()
        expect(po.header.desktop_nav).to_be_hidden()

    def test_mobile_menu_navigates(self, k, request):
        """Mở menu mobile và điều hướng tới danh mục"""
        known_bug(request, "header tràn ngang trên mobile, nút menu nằm ngoài màn hình")
        k.catalog.open_home()
        k.catalog.open_category_from_mobile_menu(FIRST_CATEGORY["nav"])
        k.common.verify_url(FIRST_CATEGORY["path"])

    def test_no_horizontal_overflow(self, k, request):
        """Không bị tràn ngang trên trang chủ"""
        known_bug(request, "ô tìm kiếm w-48 cố định làm header rộng hơn màn hình (~64px)")
        k.catalog.open_home()
        k.common.verify_no_horizontal_overflow()
