# Trang Blog: danh sách /blog (pages/BlogPage.jsx) và chi tiết /blog/:slug (pages/BlogDetailPage.jsx).
import re


class BlogListPage:
    """Trang /blog (pages/BlogPage.jsx)."""

    def __init__(self, page):
        self.page = page
        self.heading = page.get_by_role("heading", level=1, name="Blog Thời Trang")
        self.subtitle = page.get_by_text(
            "Cập nhật xu hướng, chia sẻ phong cách và câu chuyện từ Đạt Hoàng"
        )
        self.category_pills = page.locator("main section.sticky button")
        self.cards = page.locator('main a[href^="/blog/"]')
        self.empty_state = page.get_by_text("Không có bài viết nào trong danh mục này")
        self.newsletter_section = page.locator("main section").filter(
            has=page.get_by_role("heading", name="Đăng ký nhận tin mới nhất")
        )
        self.newsletter_email = self.newsletter_section.get_by_placeholder("Nhập email của bạn")
        self.newsletter_submit = self.newsletter_section.get_by_role("button", name="Đăng ký")

    def open(self):
        self.page.goto("/blog")

    def pill(self, name):
        return self.category_pills.filter(has_text=re.compile(f"^{name}$"))

    def card(self, title):
        return self.cards.filter(has=self.page.locator("h2", has_text=title))

    def card_categories(self):
        """Nhãn danh mục của từng thẻ bài viết."""
        return self.cards.locator("span.uppercase")


class BlogDetailPage:
    """Trang /blog/:slug (pages/BlogDetailPage.jsx)."""

    def __init__(self, page):
        self.page = page
        self.title = page.get_by_role("heading", level=1)
        self.back_link = page.get_by_role("link", name=re.compile(r"Quay lại Blog"))
        self.category_badge = page.locator("main .max-w-3xl span.rounded-full").first
        self.view_count = page.get_by_text(re.compile(r"\d+ lượt xem$"))
        self.author = page.locator("main .max-w-3xl p.font-semibold")
        self.summary = page.locator("main p.italic.border-l-4")
        self.tags_section = page.locator("main div.flex-wrap").filter(has_text="Tags:")
        self.related_heading = page.get_by_role("heading", name="Bài viết liên quan")
        self.related_section = page.locator("main section").filter(has=self.related_heading)
        self.related_cards = self.related_section.locator('a[href^="/blog/"]')
        self.content_fallback = page.get_by_text(
            "Nội dung đang được cập nhật. Vui lòng quay lại sau."
        )

    def open(self, slug):
        self.page.goto(f"/blog/{slug}")

    def tag(self, tag):
        return self.tags_section.get_by_text(f"#{tag}", exact=True)

    def related_card(self, title):
        return self.related_cards.filter(has=self.page.locator("h3", has_text=title))
