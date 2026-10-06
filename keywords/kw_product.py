# THƯ VIỆN KEYWORD - NHÓM product: trang chi tiết sản phẩm mở rộng (ảnh, màu, SKU, accordion,
# đánh giá, sản phẩm liên quan).
import re

from playwright.sync_api import expect

from keywords.base_keywords import BaseKeywords, keyword
from pages.storefront.product_extras_page import ProductExtrasPage
from utils.assertions import poll_until


class ProductKeywords(BaseKeywords):
    group = "product"

    def __init__(self, page, po, api, common=None):
        super().__init__(page, po, api, common)
        self._pdp = ProductExtrasPage(page)

    @keyword("mockProductDetail")
    def mock_product_detail(self, slug, response):
        """Mock GET /api/products/{slug} bằng dữ liệu cho trước (shape { success, data })."""
        with self.step(f'Mock chi tiết sản phẩm "{slug}"'):
            self.page.route(
                f"**/api/products/{slug}",
                lambda route: route.fulfill(json=response)
                if route.request.method == "GET"
                else route.fallback(),
            )

    @keyword("openProductPage")
    def open_product_page(self, slug):
        """Mở trang chi tiết /product/{slug} và chờ tên sản phẩm hiển thị."""
        with self.step(f'Mở trang chi tiết "{slug}"'):
            self._pdp.open(slug)
            expect(self.po.product.title).to_be_visible()

    @keyword("verifyBreadcrumb")
    def verify_breadcrumb(self, title):
        """Kiểm tra breadcrumb "Trang chủ | {tên sản phẩm}"."""
        with self.step(f'Kiểm tra breadcrumb "Trang chủ | {title}"'):
            expect(self._pdp.breadcrumb).to_have_text(f"Trang chủ|{title}", use_inner_text=False)
            expect(self._pdp.breadcrumb_home).to_have_attribute("href", "/")

    @keyword("clickBreadcrumbHome")
    def click_breadcrumb_home(self):
        """Bấm "Trang chủ" trên breadcrumb."""
        with self.step('Bấm "Trang chủ" trên breadcrumb'):
            self._pdp.breadcrumb_home.click()

    @keyword("verifyGallery")
    def verify_gallery(self, count):
        """Kiểm tra bộ ảnh: số thumbnail ("Thumbnail 1..n") và bộ đếm "1/n"."""
        with self.step(f"Kiểm tra bộ ảnh có {count} ảnh"):
            expect(self._pdp.thumbnails).to_have_count(count)
            for i in range(1, count + 1):
                expect(self._pdp.thumbnail(i)).to_be_visible()
            expect(self._pdp.image_counter).to_have_text(f"1/{count}")
            expect(self._pdp.next_image_button).to_be_visible()

    @keyword("clickThumbnail")
    def click_thumbnail(self, n):
        """Bấm thumbnail thứ n (đánh số từ 1)."""
        with self.step(f"Bấm Thumbnail {n}"):
            self._pdp.thumbnail(n).click()

    @keyword("clickNextImage")
    def click_next_image(self):
        """Bấm nút mũi tên chuyển ảnh tiếp theo trên ảnh chính."""
        with self.step("Bấm ảnh tiếp theo"):
            self._pdp.next_image_button.click()

    @keyword("verifyCurrentImage")
    def verify_current_image(self, n, total):
        """Kiểm tra ảnh chính đang là ảnh thứ n: bộ đếm "n/tổng", thumbnail n được viền, cùng nguồn ảnh."""
        with self.step(f"Kiểm tra đang xem ảnh {n}/{total}"):
            expect(self._pdp.image_counter).to_have_text(f"{n}/{total}")
            expect(self._pdp.thumbnails.nth(n - 1)).to_have_class(re.compile(r"border-\[#2f3a45\]"))
            src = self._pdp.thumbnail(n).locator("img").get_attribute("src")
            expect(self._pdp.main_image).to_have_attribute("src", src or "")

    @keyword("verifyNextImageHidden")
    def verify_next_image_hidden(self):
        """Kiểm tra nút ảnh tiếp theo bị ẩn (đang ở ảnh cuối)."""
        with self.step("Kiểm tra ẩn nút ảnh tiếp theo ở ảnh cuối"):
            expect(self._pdp.next_image_button).to_have_count(0)

    @keyword("verifyColorOptions")
    def verify_color_options(self, colors):
        """Kiểm tra các ô màu (theo title) và màu đang chọn mặc định (màu đầu tiên)."""
        with self.step(f"Kiểm tra màu: {', '.join(colors)}"):
            titles = self._pdp.color_buttons.evaluate_all(
                "els => els.map((e) => e.getAttribute('title'))"
            )
            assert titles == colors, f"Màu: expected={colors!r}, actual={titles!r}"
            expect(self._pdp.selected_color_name).to_have_text(colors[0])

    @keyword("selectColor")
    def select_color(self, color):
        """Chọn 1 màu (theo title) và kiểm tra tên màu hiển thị cạnh "Màu sắc:"."""
        with self.step(f'Chọn màu "{color}"'):
            self._pdp.color_button(color).click()
            expect(self._pdp.selected_color_name).to_have_text(color)
            expect(self._pdp.color_button(color)).to_have_class(re.compile(r"ring-\[#d71920\]"))

    @keyword("verifySku")
    def verify_sku(self, sku):
        """Kiểm tra dòng "SKU: ..." và nút "Copy"."""
        with self.step(f"Kiểm tra SKU {sku}"):
            expect(self._pdp.sku).to_have_text(f"SKU: {sku}")
            expect(self._pdp.copy_label("Copy")).to_be_visible()

    @keyword("copySku")
    def copy_sku(self):
        """Bấm "Copy" mã SKU."""
        with self.step("Bấm Copy SKU"):
            self._pdp.copy_sku_button.click()

    @keyword("verifySkuCopied")
    def verify_sku_copied(self, sku):
        """Kiểm tra đã copy SKU: nút đổi thành "Đã copy", clipboard chứa SKU, sau 2 giây trở lại "Copy"."""
        with self.step(f"Kiểm tra đã copy SKU {sku}"):
            expect(self._pdp.copy_label("Đã copy")).to_be_visible()
            poll_until(
                lambda: self.page.evaluate("() => navigator.clipboard.readText()") == sku,
                f"Clipboard không chứa SKU {sku!r}",
            )
            expect(self._pdp.copy_label("Copy")).to_be_visible(timeout=5_000)

    @keyword("verifyPrice")
    def verify_price(self, price):
        """Kiểm tra giá bán hiển thị đúng định dạng, vd: "449.000đ"."""
        with self.step(f'Kiểm tra giá "{price}"'):
            expect(self._pdp.price).to_have_text(price)

    @keyword("verifyComparePrice")
    def verify_compare_price(self, compare_price, discount):
        """Kiểm tra giá gốc gạch ngang và nhãn phần trăm giảm, vd: "599.000đ", "-25%"."""
        with self.step(f'Kiểm tra giá gốc "{compare_price}" và giảm "{discount}"'):
            expect(self._pdp.compare_price).to_have_text(compare_price)
            expect(self._pdp.discount_badge).to_have_text(discount)

    @keyword("verifyDiscountBadge")
    def verify_discount_badge(self, discount):
        """Kiểm tra nhãn phần trăm giảm cạnh giá, vd: "-25%"."""
        with self.step(f'Kiểm tra nhãn giảm "{discount}"'):
            expect(self._pdp.discount_badge).to_have_text(discount)
            expect(self._pdp.compare_price).to_be_visible()

    @keyword("toggleAccordion")
    def toggle_accordion(self, title):
        """Bấm tiêu đề 1 accordion: "Mô tả" / "Chất liệu" / "Hướng dẫn sử dụng"."""
        with self.step(f'Bấm accordion "{title}"'):
            self._pdp.accordion_header(title).click()

    @keyword("verifyOpenAccordion")
    def verify_open_accordion(self, title, all_titles):
        """Kiểm tra chỉ đúng 1 accordion đang mở (title), các accordion còn lại đóng; title rỗng = tất cả đóng."""
        with self.step(f'Kiểm tra accordion đang mở: "{title or "(không)"}"'):
            for t in all_titles:
                is_open = t == title
                expect(self._pdp.accordion_indicator(t)).to_have_text("—" if is_open else "+")
                expect(self._pdp.accordion_panel(t)).to_have_class(
                    re.compile(r"max-h-\[500px\]") if is_open else re.compile(r"max-h-0")
                )

    @keyword("verifyAccordionContent")
    def verify_accordion_content(self, title, lines):
        """Kiểm tra nội dung trong 1 accordion (các dòng/đoạn)."""
        with self.step(f'Kiểm tra nội dung "{title}"'):
            expect(self._pdp.accordion_panel(title).locator("p, li")).to_have_text(lines)

    @keyword("verifyServices")
    def verify_services(self, services):
        """Kiểm tra danh sách dịch vụ dưới nút mua (tiêu đề + mô tả)."""
        with self.step(f"Kiểm tra {len(services)} dịch vụ"):
            expect(self._pdp.service_items).to_have_count(len(services))
            for service in services:
                expect(self._pdp.service_item(service["title"])).to_contain_text(service["desc"])

    @keyword("verifyServiceText")
    def verify_service_text(self, title, desc):
        """Kiểm tra mô tả của 1 dịch vụ, vd: "Miễn phí giao hàng" -> "Với đơn hàng trên 500.000đ."."""
        with self.step(f'Kiểm tra dịch vụ "{title}": "{desc}"'):
            expect(self._pdp.service_item(title).locator("div.text-xs")).to_have_text(desc)

    @keyword("verifyRelatedProduct")
    def verify_related_product(self, name):
        """Kiểm tra khối "SẢN PHẨM CÙNG PHONG CÁCH" có sản phẩm theo tên."""
        with self.step(f'Kiểm tra sản phẩm cùng phong cách "{name}"'):
            expect(self._pdp.related_heading).to_be_visible()
            expect(self._pdp.related_item(name)).to_be_visible()

    @keyword("openRelatedProduct")
    def open_related_product(self, name):
        """Bấm 1 sản phẩm trong "SẢN PHẨM CÙNG PHONG CÁCH"."""
        with self.step(f'Mở sản phẩm cùng phong cách "{name}"'):
            self._pdp.related_item(name).click()

    @keyword("verifyReviewLoginPrompt")
    def verify_review_login_prompt(self):
        """Kiểm tra khách chưa đăng nhập: chỉ thấy lời nhắc đăng nhập để đánh giá."""
        with self.step('Kiểm tra lời nhắc "Vui lòng đăng nhập để đánh giá sản phẩm"'):
            expect(self._pdp.login_prompt).to_be_visible()
            expect(self._pdp.review_login_link).to_have_attribute("href", "/login")
            expect(self._pdp.write_review_button).to_have_count(0)

    @keyword("clickReviewLogin")
    def click_review_login(self):
        """Bấm "Đăng nhập" trong khối đánh giá."""
        with self.step('Bấm "Đăng nhập" ở khối đánh giá'):
            self._pdp.review_login_link.click()

    @keyword("openReviewForm")
    def open_review_form(self):
        """Bấm "Viết đánh giá" và kiểm tra form hiện ra."""
        with self.step('Mở form "Viết đánh giá"'):
            self._pdp.write_review_button.click()
            expect(self._pdp.review_form_title).to_be_visible()
            expect(self._pdp.review_stars).to_have_count(5)

    @keyword("fillReview")
    def fill_review(self, stars, content):
        """Chọn số sao (0 = bỏ qua) và nhập nội dung đánh giá."""
        with self.step(f'Nhập đánh giá {stars} sao: "{content}"'):
            if stars > 0:
                self._pdp.review_stars.nth(stars - 1).click()
            self._pdp.review_content.fill(content)

    @keyword("submitReview")
    def submit_review(self):
        """Bấm "Gửi đánh giá"."""
        with self.step('Bấm "Gửi đánh giá"'):
            self._pdp.submit_review_button.click()

    @keyword("verifyReviewErrors")
    def verify_review_errors(self, messages):
        """Kiểm tra các thông báo lỗi dưới form đánh giá (đúng và đủ)."""
        with self.step(f"Kiểm tra lỗi form đánh giá: {' | '.join(messages)}"):
            for message in messages:
                expect(self._pdp.review_error(message)).to_be_visible()
            expect(self._pdp.review_form.locator("p.text-red-500")).to_have_count(len(messages))

    @keyword("cancelReview")
    def cancel_review(self):
        """Bấm "Hủy" trên form đánh giá."""
        with self.step('Bấm "Hủy" form đánh giá'):
            self._pdp.cancel_review_button.click()

    @keyword("closeReviewForm")
    def close_review_form(self):
        """Bấm nút "×" đóng form đánh giá."""
        with self.step('Bấm "×" đóng form đánh giá'):
            self._pdp.close_review_button.click()

    @keyword("verifyReviewFormClosed")
    def verify_review_form_closed(self):
        """Kiểm tra form đánh giá đã đóng và nút "Viết đánh giá" hiện lại."""
        with self.step("Kiểm tra form đánh giá đã đóng"):
            expect(self._pdp.review_form_title).to_have_count(0)
            expect(self._pdp.write_review_button).to_be_visible()
