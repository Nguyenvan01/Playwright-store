# Trang /search (pages/SearchPage.jsx): ?q= / ?category= / ?brand= hoặc không tham số.
import re


class SearchResultsPage:
    def __init__(self, page):
        self.page = page
        self.breadcrumb = page.locator("main nav").first
        self.heading = page.get_by_role("heading", level=1)
        self.subtitle = page.locator("main h1 + p")
        self.sort_select = page.locator("main select")
        self.cards = page.locator('main .grid a[href^="/product/"]')
        self.empty_heading = page.get_by_role("heading", name="Không tìm thấy sản phẩm nào")
        self.view_all_link = page.get_by_role("link", name="Xem tất cả sản phẩm")
        self.error_heading = page.get_by_role("heading", name="Đã xảy ra lỗi")
        self.retry_button = page.get_by_role("button", name="Thử lại")
        self.pagination = page.locator("main .mt-16")

    def open(self, query):
        self.page.goto(f"/search{query}")

    def breadcrumb_item(self, name):
        return self.breadcrumb.get_by_text(name, exact=True)

    def breadcrumb_link(self, name):
        return self.breadcrumb.get_by_role("link", name=name, exact=True)

    def chip(self, text):
        """Chip bộ lọc đang áp dụng, vd: 'Danh mục: Vay', 'Tìm: "ao"'."""
        return self.page.locator("main span.rounded-full").filter(has_text=text)

    def chip_close(self, text):
        return self.chip(text).get_by_role("link", name="close")

    def card_price(self, card):
        """Giá bán hiện tại của ProductCard (span đậm)."""
        return card.locator("span.font-bold").filter(has_text=re.compile(r"^[\d.]+đ$"))

    def page_button(self, n):
        return self.pagination.get_by_role("button", name=str(n), exact=True)

    def next_page_button(self):
        return self.pagination.get_by_role("button", name="chevron_right", exact=True)

    def prev_page_button(self):
        return self.pagination.get_by_role("button", name="chevron_left", exact=True)

    def empty_hint(self, text):
        return self.page.locator("main").get_by_text(text, exact=True)
