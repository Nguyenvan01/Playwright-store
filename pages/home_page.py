# Trang chủ "/": khối SẢN PHẨM MỚI, thẻ sản phẩm, footer.
from pages.base_page import BasePage
from pages.components.cart_drawer import CartDrawer
from pages.components.header import Header


class HomePage(BasePage):
    path = "/"

    def __init__(self, page):
        super().__init__(page)
        self.header = Header(page)
        self.cart = CartDrawer(page)
        self.new_products_heading = page.get_by_role("heading", name="SẢN PHẨM MỚI")
        self.product_cards = page.locator('main a[href^="/product/"], section a[href^="/product/"]')
        self.footer = page.locator("footer")

    def product_card(self, name):
        return self.product_cards.filter(has=self.page.locator("h3", has_text=name))
