# THƯ VIỆN KEYWORD - NHÓM admin: đăng nhập quản trị, điều hướng sidebar, thao tác chung trên bảng/form/modal.
import re

from playwright.sync_api import expect

from config import ADMIN
from keywords.base_keywords import BaseKeywords, keyword
from utils.routes import ROUTES
from utils.storage import detect_reload


class AdminKeywords(BaseKeywords):
    group = "admin"

    @keyword("openAdminLogin")
    def open_admin_login(self):
        """Mở trang đăng nhập quản trị."""
        with self.step("Mở trang đăng nhập admin"):
            self.po.admin_login.goto()
            expect(self.po.admin_login.heading).to_be_visible()

    @keyword("loginAdmin")
    def login_admin(self, email, password):
        """Nhập email + mật khẩu admin và bấm Đăng nhập."""
        with self.step(f'Đăng nhập admin "{email}"'):
            self.po.admin_login.login(email, password)

    @keyword("loginAsAdmin")
    def login_as_admin(self):
        """Đăng nhập bằng tài khoản admin test trong .env và chờ vào Dashboard."""
        with self.step("Đăng nhập tài khoản admin test"):
            assert ADMIN["email"], "Chưa cấu hình E2E_ADMIN_EMAIL"
            self.po.admin_login.goto()
            self.po.admin_login.login(ADMIN["email"], ADMIN["password"])
            expect(self.page).to_have_url(ROUTES["adminDashboard"])

    @keyword("loginAdminExpectingError")
    def login_admin_expecting_error(self, email, password, message):
        """Đăng nhập admin sai và kiểm tra thông báo lỗi vẫn hiển thị (không reload)."""
        with self.step(f'Đăng nhập admin "{email}" và chờ lỗi "{message}"'):
            watcher = detect_reload(self.page)
            self.po.admin_login.login(email, password)
            reloaded = watcher.reloaded()
            assert reloaded is False, f"Trang bị reload sau khi đăng nhập sai: expected=False, actual={reloaded!r}"
            expect(self.po.admin_login.error_message).to_have_text(message)
            expect(self.page).to_have_url(ROUTES["adminLogin"])

    @keyword("verifyOnAdminLogin")
    def verify_on_admin_login(self):
        """Kiểm tra đang ở trang đăng nhập admin (bị chặn khi chưa đăng nhập)."""
        with self.step("Kiểm tra bị chuyển về /admin/login"):
            expect(self.page).to_have_url(ROUTES["adminLogin"])
            expect(self.po.admin_login.heading).to_be_visible()

    @keyword("backToStore")
    def back_to_store(self):
        """Bấm "Quay về cửa hàng" trên trang đăng nhập admin."""
        with self.step('Bấm "Quay về cửa hàng"'):
            self.po.admin_login.back_to_store_link.click()

    @keyword("openDashboard")
    def open_dashboard(self):
        """Mở trang quản trị /admin (cần đã đăng nhập) và chờ sidebar."""
        with self.step("Mở trang quản trị"):
            self.po.admin_layout.goto()
            expect(self.po.admin_layout.sidebar).to_be_visible()

    @keyword("navigateMenu")
    def navigate_menu(self, label):
        """Bấm 1 mục trên sidebar quản trị, vd: "Sản phẩm"."""
        with self.step(f'Sidebar -> "{label}"'):
            self.po.admin_layout.navigate_to(label)

    @keyword("openAdminPage")
    def open_admin_page(self, path, title):
        """Mở 1 trang quản trị theo đường dẫn và kiểm tra tiêu đề trên header."""
        with self.step(f'Mở trang quản trị {path} "{title}"'):
            self.page.goto(path)
            expect(self.po.admin_ui.page_title).to_have_text(title)

    @keyword("verifyHeaderTitle")
    def verify_header_title(self, title):
        """Kiểm tra tiêu đề trang trên header admin."""
        with self.step(f'Kiểm tra tiêu đề "{title}"'):
            expect(self.po.admin_ui.page_title).to_have_text(title)

    @keyword("verifyTableHeaders")
    def verify_table_headers(self, headers):
        """Kiểm tra bảng có đủ các cột (theo thứ tự)."""
        with self.step(f"Kiểm tra cột bảng: {' | '.join(headers)}"):
            # textContent: lấy chữ gốc, không bị CSS `uppercase` biến đổi như innerText
            texts = [
                re.sub(r"\s+", " ", t).strip() for t in self.po.admin_ui.table_headers.all_text_contents()
            ]
            texts = [t for t in texts if t]
            missing = [h for h in headers if h not in texts]
            assert not missing, f"Thiếu cột: expected={headers!r}, actual={texts!r}"
            idx = [texts.index(h) for h in headers]
            assert idx == sorted(idx), f"Thứ tự cột không đúng: expected={headers!r}, actual={texts!r}"

    @keyword("searchList")
    def search_list(self, placeholder, text):
        """Gõ vào ô tìm kiếm có placeholder cho trước."""
        with self.step(f'Tìm "{text}"'):
            self.page.get_by_placeholder(placeholder, exact=True).fill(text)

    @keyword("clickButton")
    def click_button(self, name):
        """Bấm 1 nút theo tên hiển thị (ưu tiên nút trong modal đang mở)."""
        with self.step(f'Bấm "{name}"'):
            self.po.admin_ui.button(name).click()

    @keyword("clickRowAction")
    def click_row_action(self, row_text, title):
        """Bấm nút hành động (title) trên dòng chứa text, vd: ("Áo thun", "Sửa")."""
        with self.step(f'Dòng "{row_text}" -> "{title}"'):
            self.po.admin_ui.row_action(row_text, title).click()

    @keyword("verifyRow")
    def verify_row(self, text, visible=True):
        """Kiểm tra có/không có dòng chứa text trong bảng."""
        with self.step(f"Kiểm tra {'có' if visible else 'không có'} dòng \"{text}\""):
            row = self.po.admin_ui.row(text)
            if visible:
                expect(row.first).to_be_visible()
            else:
                expect(row).to_have_count(0)

    @keyword("fillForm")
    def fill_form(self, fields):
        """Điền form theo label: chuỗi -> input/textarea/select (value hoặc label option), boolean -> checkbox."""
        with self.step(f"Điền form: {', '.join(fields)}"):
            for label, value in fields.items():
                if isinstance(value, bool):
                    self.po.admin_ui.checkbox(label).set_checked(value)
                    continue
                element = self.po.admin_ui.field(label)
                tag = element.evaluate("n => n.tagName.toLowerCase()")
                text = str(value)
                if tag == "select":
                    escaped = text.replace('"', '\\"')
                    by_value = element.locator(f'option[value="{escaped}"]').count()
                    if by_value:
                        element.select_option(value=text)
                    else:
                        element.select_option(label=text)
                else:
                    element.fill(text)

    @keyword("verifyFieldValue")
    def verify_field_value(self, label, value):
        """Kiểm tra giá trị hiện tại của 1 ô trong form (theo label)."""
        with self.step(f'Kiểm tra ô "{label}" = "{value}"'):
            expect(self.po.admin_ui.field(label)).to_have_value(str(value))

    @keyword("verifyModalOpen")
    def verify_modal_open(self, heading):
        """Kiểm tra modal/khối có tiêu đề đang hiển thị."""
        with self.step(f'Kiểm tra mở "{heading}"'):
            expect(self.po.admin_ui.heading(heading)).to_be_visible()

    @keyword("verifyModalClosed")
    def verify_modal_closed(self, heading):
        """Kiểm tra modal/khối có tiêu đề đã đóng."""
        with self.step(f'Kiểm tra đã đóng "{heading}"'):
            expect(self.page.get_by_role("heading", name=heading, exact=True)).to_have_count(0)

    @keyword("verifyAdminPage")
    def verify_admin_page(self, path):
        """Kiểm tra đang ở 1 trang quản trị (URL + tiêu đề trang)."""
        with self.step(f"Kiểm tra trang quản trị {path}"):
            expect(self.page).to_have_url(path)
            expect(self.po.admin_layout.sidebar).to_be_visible()
            expect(self.po.admin_layout.page_title).to_be_visible()
