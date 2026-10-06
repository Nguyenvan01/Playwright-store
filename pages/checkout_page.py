# Trang thanh toán /checkout: form giao hàng, phương thức giao/thanh toán, tóm tắt đơn.
# Phương thức giao hàng: "standard" | "express". Thanh toán: "cod" | "bank" | "vnpay" | "momo".
from pages.base_page import BasePage


class CheckoutPage(BasePage):
    path = "/checkout"

    def __init__(self, page):
        super().__init__(page)
        self.first_name = page.get_by_label("Họ", exact=True)
        self.last_name = page.get_by_label("Tên", exact=True)
        self.phone = page.locator("#phone")
        self.city = page.get_by_label("Tỉnh / Thành phố")
        self.district = page.get_by_label("Quận / Huyện")
        self.ward = page.get_by_label("Phường / Xã")
        self.address = page.get_by_label("Địa chỉ chi tiết")
        self.submit_button = page.get_by_role("button", name="Thanh toán", exact=True)
        self.empty_cart_heading = page.get_by_role("heading", name="Giỏ hàng trống")
        self.login_button = page.get_by_role("button", name="Đăng nhập / Đăng ký")
        self.products_section = page.locator('section[aria-labelledby="product-title"]')
        self.summary_section = page.locator('section[aria-labelledby="summary-title"]')

    def fill_shipping(self, info):
        """info: dict khóa camelCase như data/checkout/addresses.json."""
        self.first_name.fill(info["firstName"])
        self.last_name.fill(info["lastName"])
        self.phone.fill(info["phone"])
        self.city.select_option(info["city"])
        self.district.select_option(info["district"])
        if info.get("ward"):
            self.ward.select_option(info["ward"])
        self.address.fill(info["address"])

    def choose_shipping(self, method):
        self.page.locator("label.ck-shipping-option").filter(
            has=self.page.locator(f'input[value="{method}"]')
        ).click()

    def choose_payment(self, method):
        self.page.locator("label.ck-payment-option").filter(
            has=self.page.locator(f'input[value="{method}"]')
        ).click()

    def place_order(self):
        self.submit_button.click()
