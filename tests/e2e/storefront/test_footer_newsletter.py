# ============================================================
# TEST: FOOTER VÀ KHỐI ĐĂNG KÝ NHẬN TIN
# Mục tiêu: footer đủ cột/link/bản quyền, link footer đúng đích; newsletter hợp lệ / bị trình duyệt chặn
# Dữ liệu: data/storefront/footer.json (headings, links, linkCases, newsletter)
# API cần quan sát: k.content.verify_footer_*, k.content.subscribe_newsletter
# Kết quả mong đợi: footer khớp dữ liệu; email hợp lệ -> cảm ơn, email sai -> HTML5 validation chặn
# ============================================================
import pytest

from utils.cases import case_params
from utils.data_loader import load_data

DATA = load_data("storefront/footer.json")


class TestFooter:
    """Footer"""

    def test_footer_content(self, k):
        """[SF-FOOT-01] Footer có đủ cột, link và dòng bản quyền"""
        k.content.open_home_page()
        k.content.verify_footer_content(DATA["headings"], DATA["links"])

    @pytest.mark.parametrize("case", case_params(DATA["linkCases"]))
    def test_footer_link(self, k, case):
        """Link footer trỏ đúng trang (data-driven)"""
        k.content.open_home_page()
        if case.get("link"):
            k.content.verify_footer_link(case["link"], case["href"])
        else:
            k.content.verify_footer_has_link_to(case["href"])


class TestNewsletter:
    """Đăng ký nhận tin (data-driven)"""

    @pytest.mark.parametrize("case", case_params(DATA["newsletter"]))
    def test_subscribe_newsletter(self, k, case):
        """Đăng ký nhận tin (data-driven)"""
        k.common.goto(case["path"])
        k.content.subscribe_newsletter(case["email"])
        if case["success"]:
            k.content.verify_newsletter_thanks()
        else:
            validity = case.get("validity")
            k.content.verify_newsletter_blocked(validity if validity is not None else "valid")
