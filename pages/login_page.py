# Trang /login - dùng chung cho Đăng nhập và Đăng ký (chuyển bằng nút "Đăng ký ngay").
import re

from pages.base_page import BasePage


class LoginPage(BasePage):
    path = "/login"

    def __init__(self, page):
        super().__init__(page)
        self.heading = page.get_by_role("heading", level=1)
        self.name_input = page.get_by_placeholder("Nguyễn Văn A")
        self.identifier_input = page.get_by_placeholder("Nhập email hoặc số điện thoại")
        self.phone_input = page.get_by_placeholder("0912 345 678")
        self.password_input = page.get_by_placeholder("Nhập mật khẩu", exact=True)
        self.confirm_password_input = page.get_by_placeholder("Nhập lại mật khẩu")
        self.remember_me = page.get_by_label("Ghi nhớ đăng nhập")
        self.login_button = page.get_by_role("button", name="ĐĂNG NHẬP", exact=True)
        self.register_button = page.get_by_role("button", name="TẠO TÀI KHOẢN", exact=True)
        self.switch_to_register = page.get_by_role("button", name="Đăng ký ngay")
        self.switch_to_login = page.locator(".register-link").get_by_role("button", name="Đăng nhập")
        self.toggle_password = page.get_by_role("button", name=re.compile(r"(Hiện|Ẩn) mật khẩu"))
        self.general_error = page.locator(".login-card .bg-red-50")

    def field_error(self, message):
        return self.page.locator(".form-error", has_text=message)

    def login(self, identifier, password):
        self.identifier_input.fill(identifier)
        self.password_input.fill(password)
        self.login_button.click()

    def register(self, data):
        self.switch_to_register.click()
        self.name_input.fill(data["name"])
        self.identifier_input.fill(data["email"])
        self.phone_input.fill(data["phone"])
        self.password_input.fill(data["password"])
        confirm = data.get("confirmPassword")
        self.confirm_password_input.fill(data["password"] if confirm is None else confirm)
        self.register_button.click()
