# Các phần mở rộng của trang chi tiết sản phẩm (pages/ProductDetailPage.jsx).
import re


class ProductExtrasPage:
    def __init__(self, page):
        self.page = page
        self.breadcrumb = page.locator("nav.breadcrumb")
        self.breadcrumb_home = self.breadcrumb.get_by_role("link", name="Trang chủ")
        self.thumbnails = page.locator(".thumbnail-list button")
        self.main_image = page.locator("img.main-product-image")
        self.image_counter = page.locator(".image-counter")
        self.next_image_button = page.locator("button.next-image-button")
        self.color_buttons = page.locator(".color-selector button[title]")
        self.selected_color_name = (
            page.locator(".color-selector")
            .get_by_text("Màu sắc:")
            .locator("xpath=following-sibling::span[1]")
        )
        self.sku = page.locator(".product-sku")
        self.copy_sku_button = page.locator("button.copy-sku")
        self.price = page.locator(".product-price")
        self.compare_price = page.locator(".product-price + span.line-through")
        self.discount_badge = page.locator(".product-info").get_by_text(re.compile(r"^-\d+%$"))
        self.service_items = page.locator(".service-list .service-item")

        self.reviews_heading = page.get_by_role("heading", name="ĐÁNH GIÁ SẢN PHẨM")
        self.reviews_section = page.locator("section").filter(has=self.reviews_heading)
        self.login_prompt = self.reviews_section.get_by_text("Vui lòng đăng nhập để đánh giá sản phẩm")
        self.review_login_link = self.reviews_section.get_by_role("link", name="Đăng nhập")
        self.write_review_button = self.reviews_section.get_by_role("button", name="Viết đánh giá")
        self.review_form_title = self.reviews_section.get_by_role(
            "heading", name="VIẾT ĐÁNH GIÁ CỦA BẠN"
        )
        self.review_form = self.reviews_section.locator("div.mb-8").filter(
            has=page.get_by_role("heading", name="VIẾT ĐÁNH GIÁ CỦA BẠN")
        )
        self.review_stars = self.review_form.locator('button[type="button"]')
        self.review_content = self.review_form.get_by_placeholder(
            "Chia sẻ trải nghiệm của bạn về sản phẩm này..."
        )
        self.submit_review_button = self.review_form.get_by_role(
            "button", name=re.compile(r"Gửi đánh giá|Đang gửi\.\.\.")
        )
        self.cancel_review_button = self.review_form.get_by_role("button", name="Hủy", exact=True)
        self.close_review_button = self.review_form.get_by_role("button", name="×", exact=True)

        self.related_heading = page.get_by_role("heading", name="SẢN PHẨM CÙNG PHONG CÁCH")
        self.related_section = page.locator("section").filter(has=self.related_heading)
        self.related_items = self.related_section.locator('a[href^="/product/"]')

    def open(self, slug):
        self.page.goto(f"/product/{slug}")

    def thumbnail(self, n):
        return self.page.get_by_role("button", name=f"Thumbnail {n}", exact=True)

    def color_button(self, name):
        return self.page.locator(f'.color-selector button[title="{name}"]')

    def copy_label(self, text):
        """text: "Copy" hoặc "Đã copy"."""
        return self.copy_sku_button.get_by_text(text, exact=True)

    def accordion_header(self, title):
        """Nút tiêu đề accordion: "Mô tả" / "Chất liệu" / "Hướng dẫn sử dụng"."""
        return self.page.locator(".product-accordion button.accordion-header").filter(has_text=title)

    def accordion_indicator(self, title):
        """Dấu hiệu mở/đóng ("—" đang mở, "+" đang đóng) bên phải tiêu đề accordion."""
        return self.accordion_header(title).locator("span").nth(1)

    def accordion_panel(self, title):
        """Vùng nội dung của 1 accordion (đóng = max-h-0)."""
        header = self.page.locator("button.accordion-header", has_text=title)
        return (
            self.page.locator(".product-accordion .accordion-item")
            .filter(has=header)
            .locator(":scope > div")
        )

    def service_item(self, title):
        return self.service_items.filter(has_text=title)

    def review_error(self, message):
        return self.review_form.locator("p.text-red-500", has_text=message)

    def related_item(self, name):
        return self.related_items.filter(has=self.page.locator("h4", has_text=name))
