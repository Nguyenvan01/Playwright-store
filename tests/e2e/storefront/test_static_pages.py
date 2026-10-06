# ============================================================
# TEST: TRANG TĨNH (Giới thiệu, Giao hàng, Đổi trả, Bảo mật) VÀ ĐƯỜNG DẪN KHÔNG TỒN TẠI
# Mục tiêu: tiêu đề h1/h2/h3 và nội dung đúng; phát hiện lỗi nội dung; route lạ có trang báo lỗi
# Dữ liệu: data/storefront/static-pages.json (pages, contentBugs, unknownRoutes)
# API cần quan sát: k.common.goto / verify_layout_loaded, k.content.verify_*
# Kết quả mong đợi: nội dung khớp dữ liệu; bug đã biết được đánh dấu xfail
# ============================================================
import pytest

from utils.cases import case_params
from utils.data_loader import load_data

DATA = load_data("storefront/static-pages.json")


class TestStaticPages:
    """Trang tĩnh: tiêu đề và nội dung (data-driven)"""

    @pytest.mark.parametrize("case", case_params(DATA["pages"]))
    def test_static_page(self, k, case):
        """Trang tĩnh hiển thị đúng tiêu đề và nội dung (data-driven)"""
        k.common.goto(case["path"])
        k.common.verify_layout_loaded()
        k.content.verify_page_headings(case["h1"], case["h2"], case["h3"])
        k.content.verify_main_contains(case["texts"])


class TestStaticContentBugs:
    """Trang tĩnh: lỗi nội dung"""

    @pytest.mark.parametrize("case", case_params(DATA["contentBugs"]))
    def test_content_bug(self, k, case):
        """Trang tĩnh: lỗi nội dung (data-driven)"""
        k.common.goto(case["path"])
        k.common.verify_layout_loaded()
        if case.get("mustNotMatch"):
            k.content.verify_main_not_matching(case["mustNotMatch"])
        if case.get("mustContain") and case.get("block"):
            k.content.verify_block_contains(case["block"], case["mustContain"])
        elif case.get("mustContain"):
            k.content.verify_main_contains([case["mustContain"]])


class TestUnknownRoutes:
    """Đường dẫn không tồn tại"""

    @pytest.mark.parametrize("case", case_params(DATA["unknownRoutes"]))
    def test_unknown_route(self, k, case):
        """Đường dẫn không tồn tại hiển thị trang báo lỗi (data-driven)"""
        k.common.goto(case["path"])
        k.content.verify_not_found_page(case["message"])
