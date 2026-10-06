# Trang danh sách sản phẩm dùng ProductFilters: /nam, /nu, /tre-em, /giam-gia.
# Bộ lọc desktop nằm trong <aside> (viewport >= lg).
import re


class ListingPage:
    def __init__(self, page):
        self.page = page
        self.breadcrumb = page.locator("main nav").first
        self.heading = page.get_by_role("heading", level=1)
        self.count_text = page.get_by_text(re.compile(r"^Hiển thị \d+ trên \d+ sản phẩm$"))
        self.sort_select = page.locator("main section select")
        self.sidebar = page.locator("aside")
        self.price_from = self.sidebar.get_by_placeholder("Từ")
        self.price_to = self.sidebar.get_by_placeholder("Đến")
        self.show_more_categories = self.sidebar.get_by_role("button", name="Xem thêm +")
        self.cards = page.locator("main .product-card")
        self.load_more_button = page.get_by_role("button", name="Xem thêm sản phẩm")
        self.spinner = page.locator("main .animate-spin")

    def open(self, path):
        self.page.goto(path)

    def filter_section_toggle(self, title):
        """Tiêu đề 1 nhóm lọc (bấm để mở/đóng), vd: "Phần trăm giảm"."""
        return self.sidebar.get_by_role("button", name=re.compile(f"^{title}"))

    def category_button(self, name):
        return self.sidebar.locator("ul").get_by_role("button", name=name, exact=True)

    def category_buttons(self):
        return self.sidebar.locator("ul button")

    def size_buttons(self):
        """Nút size trong nhóm "Kích cỡ" (nhóm lọc thứ 2)."""
        return self.filter_group("Kích cỡ").locator("div.flex-wrap > button")

    def size_button(self, label):
        return self.filter_group("Kích cỡ").get_by_role("button", name=label, exact=True)

    def color_buttons(self):
        return self.filter_group("Màu sắc").locator("button[title]")

    def color_button(self, name):
        return self.filter_group("Màu sắc").locator(f'button[title="{name}"]')

    def discount_label(self, label):
        return self.sidebar.locator("label", has_text=label)

    def discount_checkbox(self, label):
        return self.sidebar.get_by_role("checkbox", name=label)

    def filter_group(self, title):
        """Nội dung (đã mở) của 1 nhóm lọc theo tiêu đề."""
        toggle = self.page.get_by_role("button", name=re.compile(f"^{title}"))
        return self.sidebar.locator("div.border-b").filter(has=toggle)

    def card_title(self, card):
        return card.locator("h3")

    def card_price(self, card):
        """Giá bán hiện tại của thẻ (span đầu tiên dạng "123.000đ")."""
        return card.locator("span").filter(has_text=re.compile(r"^[\d.]+đ$")).first

    def card_discount_badge(self, card):
        """Nhãn giảm giá trên ảnh: "Giảm 33%" (Nam/Nữ) hoặc "-33%" (Trẻ em/Giảm giá)."""
        return card.locator("a").get_by_text(re.compile(r"^(Giảm |-)\d+%$"))

    def card_link(self, card):
        return card.locator('a[href^="/product/"]').first

    def card_add_to_cart(self, card):
        return card.get_by_role("button", name="Thêm vào giỏ")

    def card_view_detail(self, card):
        return card.get_by_role("button", name="Xem chi tiết")

    def card_favorite(self, card):
        """Nút tim (yêu thích) trên ảnh - nút còn lại trong link ngoài 2 nút overlay."""
        return card.locator("a button").filter(has_not_text=re.compile(r"Thêm vào giỏ|Xem chi tiết"))

    def page_button(self, n):
        return self.page.locator("main section").get_by_role("button", name=str(n), exact=True)

    def next_page_button(self):
        """Nút trang sau dạng icon Material ("navigate_next")."""
        return self.page.locator("main section").get_by_role(
            "button", name="navigate_next", exact=True
        )

    def empty_state(self, text):
        return self.page.locator("main").get_by_text(text, exact=True)
