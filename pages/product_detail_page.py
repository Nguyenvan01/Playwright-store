# Trang chi tiết sản phẩm /product/:slug (size, màu, thêm vào giỏ).
import re

from pages.base_page import BasePage
from pages.components.cart_drawer import CartDrawer
from pages.components.header import Header
from utils.routes import product_route


class ProductDetailPage(BasePage):
    path = "/"

    def __init__(self, page):
        super().__init__(page)
        self.header = Header(page)
        self.cart = CartDrawer(page)
        self.title = page.locator("h1.product-title")
        self.size_buttons = page.locator(".size-options button")
        self.available_sizes = page.locator(".size-options button:not([disabled])")
        self.size_warning = page.locator(".size-selector").get_by_text("Vui lòng chọn kích cỡ")
        self.color_buttons = page.locator(".color-selector button")
        self.add_to_cart_button = page.locator(".action-buttons").get_by_role(
            "button", name="Thêm vào giỏ hàng"
        )
        self.not_found = page.get_by_text("Không tìm thấy sản phẩm.")

    def open(self, slug):
        self.goto(product_route(slug))

    def select_size(self, label=None):
        button = (
            self.size_buttons.filter(has_text=re.compile(f"^{label}$"))
            if label
            else self.available_sizes.first
        )
        button.click()

    def add_to_cart(self, size=None):
        self.select_size(size)
        self.add_to_cart_button.click()
