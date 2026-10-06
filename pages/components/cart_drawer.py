# Ngăn kéo giỏ hàng (role=dialog, aria-label="Giỏ hàng"). Luôn có trong DOM, mở bằng class.
import re

from playwright.sync_api import expect


class CartDrawer:
    def __init__(self, page):
        self.page = page
        self.root = page.get_by_role("dialog", name="Giỏ hàng")
        self.title = self.root.get_by_role("heading", name=re.compile(r"Giỏ hàng \(\d+\)"))
        self.close_button = self.root.get_by_role("button", name="Đóng giỏ hàng")
        self.empty_state = self.root.get_by_text("Giỏ hàng trống")
        self.items = self.root.locator(".cart-item")
        self.select_all = self.root.get_by_label("Chọn tất cả")
        self.subtotal = self.root.locator(".cart-subtotal")
        self.checkout_button = self.root.get_by_role("button", name="THANH TOÁN")

    def expect_open(self):
        expect(self.root).to_have_class(re.compile(r"cart-drawer--open"))

    def expect_closed(self):
        expect(self.root).not_to_have_class(re.compile(r"cart-drawer--open"))

    def item(self, name):
        return self.items.filter(has=self.page.locator(".cart-item-title", has_text=name))

    def quantity(self, name):
        return self.item(name).locator(".cart-qty-value")

    def increase(self, name):
        self.item(name).get_by_role("button", name="Tăng số lượng").click()

    def decrease(self, name):
        self.item(name).get_by_role("button", name="Giảm số lượng").click()

    def remove(self, name):
        self.item(name).locator(".cart-item-menu-btn").click()
        self.root.get_by_role("button", name="Xóa", exact=True).click()

    def close(self):
        self.close_button.click()
