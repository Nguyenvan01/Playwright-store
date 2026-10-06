# Trang /admin/login.
import re

from pages.base_page import BasePage


class AdminLoginPage(BasePage):
    path = "/admin/login"

    def __init__(self, page):
        super().__init__(page)
        self.heading = page.get_by_role("heading", name="Đạt Hoàng Admin")
        self.email_input = page.get_by_placeholder("admin@clothing-store.vn")
        self.password_input = page.get_by_placeholder("Nhập mật khẩu admin")
        self.submit_button = page.get_by_role("button", name=re.compile(r"^Đăng nhập$|Đang đăng nhập"))
        self.error_message = page.locator("form .bg-red-50")
        self.back_to_store_link = page.get_by_role("link", name=re.compile(r"Quay về cửa hàng"))

    def login(self, email, password):
        self.email_input.fill(email)
        self.password_input.fill(password)
        self.submit_button.click()
