# Các khối trên trang chủ (pages/Home.jsx): banner, ưu đãi, SẢN PHẨM MỚI, HOMEWEAR/T-SHIRT/VÁY,
# bộ sưu tập, C-LIVE, tin tức. Newsletter + Footer nằm ở `SiteChrome`.
import re


class HomeSections:
    def __init__(self, page):
        self.page = page
        # ---- Banner (components/Banner.jsx) - khối đầu tiên trong <main> ----
        self.banner = page.locator("main > div").first
        self.banner_slides = self.banner.locator(":scope > a")
        self.banner_prev = self.banner.locator(":scope > button").nth(0)
        self.banner_next = self.banner.locator(":scope > button").nth(1)
        self.banner_dots = self.banner.locator(":scope > div > button")

        # ---- Ưu đãi (components/VoucherSection.jsx) ----
        self.voucher_heading = page.get_by_role("heading", name="ƯU ĐÃI NỔI BẬT")
        self.voucher_section = page.locator("section").filter(has=self.voucher_heading)
        self.voucher_cards = self.voucher_section.locator(".grid > div")

        # ---- SẢN PHẨM MỚI ----
        self.new_products_heading = page.get_by_role("heading", name="SẢN PHẨM MỚI")
        self.new_products_block = page.locator("main .container").filter(
            has=self.new_products_heading
        )
        self.new_products_view_all = self.new_products_block.get_by_role(
            "link", name=re.compile(r"Xem tất cả")
        )
        self.new_products_tabs = self.new_products_block.locator(".border-b > button")
        self.new_products_scroll = page.locator("#new-products-scroll")
        self.new_products_prev = self.new_products_block.locator(".group\\/carousel > button").nth(0)
        self.new_products_next = self.new_products_block.locator(".group\\/carousel > button").nth(1)

        # ---- Bộ sưu tập (components/CollectionSection.jsx) ----
        self.collection_tiles = page.locator("main section .grid-cols-3 > div")

        # ---- C-LIVE ----
        self.clive_heading = page.get_by_role("heading", name="C-LIVE - NHƯ MUA SẮM TẠI CỬA HÀNG")
        self.clive_image = page.get_by_role("img", name="C-LIVE")

        # ---- Tin tức (components/BlogSection.jsx) ----
        self.blog_heading = page.get_by_role("heading", name="Tin tức thời trang")
        self.blog_section = page.locator("section").filter(has=self.blog_heading)
        self.blog_see_more = self.blog_section.get_by_role("link", name="Xem thêm")
        self.blog_empty = self.blog_section.get_by_text("Chưa có tin tức thời trang nào")
        self.blog_featured_title = self.blog_section.locator("h3")
        self.blog_secondary_titles = self.blog_section.locator("h4")

    def active_slide(self):
        """Slide đang hiển thị (opacity-100)."""
        return self.banner_slides.and_(self.page.locator(".opacity-100"))

    def banner_overlay_cta(self, index):
        """Nút "Khám phá ngay" của chữ đè trên banner (chỉ có ở slide thứ 3 trở đi)."""
        return self.banner_slides.nth(index).locator("a", has_text="Khám phá ngay")

    def banner_overlay_title(self, index):
        return self.banner_slides.nth(index).locator("h2")

    def voucher_card(self, title):
        return self.voucher_cards.filter(has=self.page.locator("p", has_text=title))

    def new_products_tab(self, name):
        return self.new_products_tabs.filter(has_text=re.compile(f"^{name}$"))

    def new_product_cards(self):
        """Thẻ sản phẩm (ProductCard) trong carousel SẢN PHẨM MỚI."""
        return self.new_products_scroll.locator('a[href^="/product/"]')

    def promo_block(self, title):
        """Khối banner + lưới sản phẩm HOMEWEAR / T-SHIRT / VÁY (theo tiêu đề h2)."""
        return self.page.locator("main > section").filter(
            has=self.page.get_by_role("heading", name=title, exact=True)
        )

    def promo_block_cards(self, title):
        return self.promo_block(title).locator('.grid a[href^="/product/"]')

    def promo_block_link(self, title, name):
        return self.promo_block(title).get_by_role("link", name=name, exact=True)

    def collection_tile(self, title):
        return self.collection_tiles.filter(has=self.page.locator("h3", has_text=title))

    def collection_cta(self, title):
        return self.collection_tile(title).locator("a")

    def product_card(self, name):
        """Thẻ ProductCard bất kỳ trên trang theo tên sản phẩm."""
        return self.page.locator('a[href^="/product/"]').filter(
            has=self.page.locator("h3", has_text=name)
        )

    def quick_add_button(self, name):
        """Nút thêm nhanh vào giỏ (icon) trên ProductCard - hiện khi hover."""
        return self.product_card(name).first.locator("button.absolute")

    def main_link(self, name):
        """Link bất kỳ trong <main> theo tên (dùng để kiểm tra link chết)."""
        return self.page.locator("main").get_by_role("link", name=name, exact=True)
