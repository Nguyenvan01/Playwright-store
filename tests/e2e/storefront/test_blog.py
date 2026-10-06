# ============================================================
# TEST: BLOG (/blog, /blog/:slug)
# Mục tiêu: danh sách bài viết, lọc theo danh mục, chi tiết bài, bài liên quan, slug sai, newsletter
# Dữ liệu: data/storefront/blog.json (mockList, filters, details, newsletterBug)
# API cần quan sát: k.content.*, k.common.verify_url / verify_no_page_errors
# Kết quả mong đợi: danh mục/bài viết khớp dữ liệu mock; slug sai quay về /blog
# ============================================================
import pytest

from utils.cases import case_params
from utils.data_loader import load_data

DATA = load_data("storefront/blog.json")
ALL_TITLES = [article["title"] for article in DATA["mockList"]["news"]]


class TestBlogRealData:
    """Blog (dữ liệu thật)"""

    @pytest.mark.smoke
    def test_blog_list_loaded(self, k):
        """[SF-BLOG-01] /blog hiển thị tiêu đề, danh mục và bài viết"""
        k.content.open_blog()
        k.content.verify_blog_loaded()
        k.common.verify_no_page_errors()

    def test_invalid_slug_redirects_to_blog(self, k):
        """[SF-BLOG-08] Slug bài viết không tồn tại -> chuyển về /blog"""
        k.content.open_blog_article_by_slug(DATA["invalidSlug"])
        k.common.verify_url("/blog")
        k.content.verify_blog_loaded()


class TestBlogMock:
    """Blog (mock API)"""

    @pytest.fixture(autouse=True)
    def mocked_blog(self, k):
        k.content.mock_blog_data(DATA["mockList"])
        k.content.open_blog()

    def test_pills_from_articles(self, k):
        """[SF-BLOG-02] Danh mục lấy từ bài viết, mặc định "Tất cả" hiển thị mọi bài"""
        k.content.verify_blog_pills(DATA["pills"])
        k.content.verify_blog_titles(ALL_TITLES)

    @pytest.mark.parametrize("case", case_params(DATA["filters"]))
    def test_filter_by_category(self, k, case):
        """Lọc blog theo danh mục (data-driven)"""
        k.content.filter_blog_by_category(case["category"])
        k.content.verify_blog_titles(case["titles"])
        k.content.verify_blog_category_of_cards(case["category"])
        k.content.filter_blog_by_category("Tất cả")
        k.content.verify_blog_titles(ALL_TITLES)

    @pytest.mark.parametrize("case", case_params(DATA["details"]))
    def test_article_detail(self, k, case):
        """Chi tiết bài viết (data-driven)"""
        k.content.open_blog_article(case["titleText"])
        k.content.verify_blog_article(case)

    def test_related_and_back_to_blog(self, k):
        """[SF-BLOG-09] Bài liên quan mở bài khác, "Quay lại Blog" về danh sách"""
        first, second = DATA["details"][0], DATA["details"][1]
        k.content.open_blog_article(first["titleText"])
        k.content.open_related_article(second["titleText"])
        k.content.verify_blog_article(second)
        k.content.click_back_to_blog()
        k.common.verify_url("/blog")

    @pytest.mark.parametrize("case", case_params([DATA["newsletterBug"]]))
    def test_blog_newsletter_no_reload(self, k, case):
        """Đăng ký nhận tin ở trang Blog không tải lại trang"""
        k.content.subscribe_blog_newsletter_without_reload(case["email"])


def test_blog_empty(k):
    """[SF-BLOG-10] Không có bài viết nào -> chỉ có "Tất cả" và thông báo trống"""
    k.content.mock_blog_data({"success": True, "news": []})
    k.content.open_blog()
    k.content.verify_blog_pills(["Tất cả"])
    k.content.verify_blog_empty()
