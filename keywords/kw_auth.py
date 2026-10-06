# THƯ VIỆN KEYWORD - NHÓM auth: đăng nhập, đăng ký, đăng xuất, phiên đăng nhập khách hàng/admin.
import json
import re

from playwright.sync_api import expect

from config import ADMIN, CUSTOMER
from keywords.base_keywords import BaseKeywords, keyword
from utils.routes import ROUTES
from utils.storage import STORAGE_KEYS, detect_reload, init_script

# Role: "customer" | "admin"
_READ_TOKEN = "(k) => localStorage.getItem(k)"


class AuthKeywords(BaseKeywords):
    group = "auth"

    @keyword("openLogin")
    def open_login(self):
        """Mở trang đăng nhập khách hàng."""
        with self.step("Mở trang đăng nhập"):
            self.po.login.goto()
            expect(self.po.login.heading).to_have_text("Đăng nhập")

    @keyword("login")
    def login(self, identifier, password):
        """Nhập email/SĐT + mật khẩu và bấm ĐĂNG NHẬP."""
        with self.step(f'Đăng nhập với "{identifier}"'):
            self.po.login.login(identifier, password)

    @keyword("loginAsCustomer")
    def login_as_customer(self):
        """Đăng nhập bằng tài khoản khách hàng test trong .env và chờ vào trang hồ sơ."""
        with self.step("Đăng nhập tài khoản khách hàng test"):
            assert CUSTOMER["email"], "Chưa cấu hình E2E_CUSTOMER_EMAIL"
            self.po.login.goto()
            self.po.login.login(CUSTOMER["email"], CUSTOMER["password"])
            expect(self.page).to_have_url(ROUTES["profile"])

    @keyword("restoreSession")
    def restore_session(self, role):
        """Đăng nhập sẵn qua API (không qua UI) - phải gọi TRƯỚC lần mở trang đầu tiên."""
        with self.step(f"Khôi phục phiên đăng nhập {role} qua API"):
            entries = {}
            if role == "customer":
                auth = self.api.customer_login(CUSTOMER["email"], CUSTOMER["password"])
                entries[STORAGE_KEYS["customerToken"]] = auth["token"]
                entries[STORAGE_KEYS["customerUser"]] = json.dumps(auth["user"], ensure_ascii=False)
            else:
                auth = self.api.admin_login(ADMIN["email"], ADMIN["password"])
                entries[STORAGE_KEYS["adminToken"]] = auth["token"]
            self.page.add_init_script(
                init_script(
                    """(data) => {
                      if (sessionStorage.getItem('__e2e_session')) return;
                      for (const [k, v] of Object.entries(data)) localStorage.setItem(k, v);
                      sessionStorage.setItem('__e2e_session', '1');
                    }""",
                    entries,
                )
            )

    @keyword("openRegisterForm")
    def open_register_form(self):
        """Chuyển form sang chế độ Đăng ký."""
        with self.step("Chuyển sang form đăng ký"):
            self.po.login.switch_to_register.click()
            expect(self.po.login.heading).to_have_text("Tạo tài khoản")

    @keyword("submitRegisterForm")
    def submit_register_form(self, form):
        """Điền form đăng ký và bấm TẠO TÀI KHOẢN (form phải đang mở)."""
        with self.step(f'Đăng ký tài khoản "{form["email"]}"'):
            lp = self.po.login
            lp.name_input.fill(form["name"])
            lp.identifier_input.fill(form["email"])
            lp.phone_input.fill(form["phone"])
            lp.password_input.fill(form["password"])
            confirm = form.get("confirmPassword")
            lp.confirm_password_input.fill(form["password"] if confirm is None else confirm)
            lp.register_button.click()

    @keyword("verifyFieldErrors")
    def verify_field_errors(self, messages):
        """Kiểm tra các thông báo lỗi dưới từng ô nhập."""
        with self.step(f"Kiểm tra lỗi field: {' | '.join(messages)}"):
            for message in messages:
                expect(self.po.login.field_error(message)).to_be_visible()

    @keyword("verifyGeneralError")
    def verify_general_error(self, message):
        """Kiểm tra thông báo lỗi chung (lỗi từ server) trên form đăng nhập/đăng ký."""
        with self.step(f'Kiểm tra lỗi chung "{message}"'):
            expect(self.po.login.general_error).to_contain_text(message)

    @keyword("loginExpectingError")
    def login_expecting_error(self, identifier, password, message):
        """Đăng nhập sai và kiểm tra thông báo lỗi vẫn hiển thị (trang không bị reload)."""
        with self.step(f'Đăng nhập "{identifier}" và chờ lỗi "{message}"'):
            watcher = detect_reload(self.page)
            self.po.login.login(identifier, password)
            assert watcher.reloaded() is False, "Trang bị reload sau khi đăng nhập sai"
            expect(self.po.login.general_error).to_contain_text(message)
            expect(self.page).to_have_url(ROUTES["login"])

    @keyword("mockLoginSuccess")
    def mock_login_success(self, user):
        """Giả lập API đăng nhập thành công với user cho trước (kèm các API trang hồ sơ)."""
        with self.step("Mock API đăng nhập thành công"):
            self.page.route(
                "**/api/auth/login",
                lambda route: route.fulfill(json={"success": True, "token": "mock-token", "user": user}),
            )
            self.page.route(
                re.compile(r"/api/(profile|orders|wishlist|addresses)(\?.*)?$"),
                lambda route: route.fulfill(
                    json={
                        "success": True,
                        "user": user,
                        "data": [],
                        "orders": [],
                        "wishlist": [],
                        "addresses": [],
                    }
                ),
            )

    @keyword("mockRegisterError")
    def mock_register_error(self, status, message):
        """Giả lập API đăng ký trả lỗi (status + message)."""
        with self.step(f"Mock API đăng ký lỗi {status}"):
            self.page.route(
                "**/api/auth/register",
                lambda route: route.fulfill(status=status, json={"success": False, "message": message}),
            )

    @keyword("togglePassword")
    def toggle_password(self, expect_visible):
        """Bấm nút hiện/ẩn mật khẩu và kiểm tra trạng thái hiển thị."""
        with self.step(f"Bật/tắt hiện mật khẩu -> {'hiện' if expect_visible else 'ẩn'}"):
            self.po.login.toggle_password.click()
            expect(self.po.login.password_input).to_have_attribute(
                "type", "text" if expect_visible else "password"
            )

    @keyword("verifyLoggedInAs")
    def verify_logged_in_as(self, email):
        """Kiểm tra menu tài khoản trên header hiển thị đúng email."""
        with self.step(f'Kiểm tra đang đăng nhập "{email}"'):
            header = self.po.header
            header.user_menu_button.click()
            expect(header.root.get_by_text(email)).to_be_visible()
            # Menu không đóng bằng ESC -> bấm lại nút để đóng, tránh ảnh hưởng bước sau
            header.user_menu_button.click()
            expect(header.root.get_by_text(email)).to_be_hidden()

    @keyword("logout")
    def logout(self):
        """Đăng xuất qua menu tài khoản trên header."""
        with self.step("Đăng xuất"):
            self.po.header.logout()

    @keyword("verifyLoggedOut")
    def verify_logged_out(self):
        """Kiểm tra đã đăng xuất: về trang chủ, có link đăng nhập, token bị xóa."""
        with self.step("Kiểm tra đã đăng xuất"):
            expect(self.page).to_have_url(ROUTES["home"])
            expect(self.po.header.login_link).to_be_visible()
            token = self.page.evaluate(_READ_TOKEN, STORAGE_KEYS["customerToken"])
            assert token is None, f"Token chưa bị xóa: actual={token!r}"

    @keyword("verifyStoredToken")
    def verify_stored_token(self, expected):
        """Kiểm tra token khách hàng trong localStorage bằng giá trị mong đợi."""
        with self.step("Kiểm tra token đã lưu"):
            token = self.page.evaluate(_READ_TOKEN, STORAGE_KEYS["customerToken"])
            assert token == expected, f"Token: expected={expected!r}, actual={token!r}"
