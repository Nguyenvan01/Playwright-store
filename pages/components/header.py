# Header dùng chung cho các trang khách hàng (logo, menu, tìm kiếm, tài khoản, giỏ hàng).
import re


class Header:
    def __init__(self, page):
        self.page = page
        self.root = page.locator("header").first
        self.logo = self.root.get_by_role("link", name="Đạt Hoàng", exact=True)
        self.desktop_nav = self.root.locator("nav")
        self.search_input = self.root.get_by_placeholder("Tìm kiếm sản phẩm...")
        self.search_see_more = self.root.get_by_text(re.compile(r"Xem thêm kết quả cho"))
        self.search_no_result = self.root.get_by_text("Không tìm thấy sản phẩm nào")
        self.login_link = self.root.locator('a[href="/login"]')
        # Các nút icon chưa có aria-label -> nhận diện qua svg. Nên bổ sung data-testid ở app.
        self.user_menu_button = self.root.locator("button").filter(
            has=page.locator('svg circle[cx="12"][cy="7"]')
        )
        self.logout_button = self.root.get_by_role("button", name="Đăng xuất")
        self.cart_button = (
            self.root.locator("button").filter(has=page.locator('svg circle[cx="8"][cy="21"]')).first
        )
        self.cart_badge = self.cart_button.locator("span.rounded-full")
        self.mobile_menu_toggle = self.root.locator("button.lg\\:hidden")

    def nav_link(self, name):
        return self.desktop_nav.get_by_role("link", name=name, exact=True)

    def mobile_nav_link(self, name):
        return self.root.locator("div.lg\\:hidden").get_by_role("link", name=name, exact=True)

    def search_result(self, product_name):
        return self.root.locator("h4", has_text=product_name)

    def type_search(self, query):
        self.search_input.fill(query)

    def submit_search(self, query):
        self.search_input.fill(query)
        self.search_input.press("Enter")

    def open_cart(self):
        self.cart_button.click()

    def logout(self):
        self.user_menu_button.click()
        self.logout_button.click()
