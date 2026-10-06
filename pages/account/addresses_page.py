# Trang /addresses (AddressesPage.jsx). Ô nhập không có label -> dùng placeholder; nút icon -> title.
import re

from pages.account.css_text import escape_regex


class AddressesPage:
    path = "/addresses"

    def __init__(self, page):
        self.page = page
        self.heading = page.get_by_role("heading", level=1, name="Địa chỉ")
        self.subtitle = self.heading.locator("xpath=following-sibling::p[1]")
        # Nút "Thêm địa chỉ" trên tiêu đề (tên gồm chữ icon "add_location").
        self.add_button = page.get_by_role("button", name="add_location Thêm địa chỉ", exact=True)
        self.empty_title = page.get_by_text("Bạn chưa có địa chỉ nào", exact=True)
        self.empty_add_button = page.get_by_role("button", name="Thêm địa chỉ mới", exact=True)
        self.form = page.locator("main form")
        self.form_heading = page.get_by_role(
            "heading", level=2, name=re.compile(r"^(Thêm địa chỉ mới|Sửa địa chỉ)$")
        )
        self.full_name = self.form.get_by_placeholder("Nguyễn Văn A")
        self.phone = self.form.get_by_placeholder("0912 345 678")
        self.address = self.form.get_by_placeholder("123 Đường ABC, Phường XYZ")
        self.ward = self.form.get_by_placeholder("Phường Bến Nghé")
        self.district = self.form.get_by_placeholder("Quận 1")
        self.city = self.form.locator("select")
        self.default_checkbox = self.form.get_by_role("checkbox", name="Đặt làm địa chỉ mặc định")
        self.submit_button = self.form.locator('button[type="submit"]')
        self.cancel_button = self.form.get_by_role("button", name="Hủy", exact=True)
        self.cards = page.locator("main div.rounded-2xl").filter(has=page.locator('button[title="Xóa"]'))
        self.default_badges = self.cards.get_by_text("Mặc định", exact=True)
        self.delete_modal = page.locator("div.fixed.inset-0").filter(
            has=page.get_by_role("heading", level=3, name="Xóa địa chỉ")
        )
        self.confirm_delete_button = self.delete_modal.get_by_role(
            "button", name=re.compile(r"^(Xóa địa chỉ|Đang xóa\.\.\.)$")
        )
        self.cancel_delete_button = self.delete_modal.get_by_role("button", name="Hủy", exact=True)

    def card(self, name):
        return self.cards.filter(
            has=self.page.locator("p.font-semibold", has_text=re.compile(f"^{escape_regex(name)}$"))
        )

    def name_row(self, name):
        """Dòng tên người nhận (+ badge "Mặc định" nếu có)."""
        return self.card(name).locator("div:has(> p.font-semibold)")

    def default_badge(self, name):
        return self.card(name).get_by_text("Mặc định", exact=True)

    def set_default_button(self, name):
        return self.card(name).get_by_title("Đặt làm mặc định")

    def edit_button(self, name):
        return self.card(name).get_by_title("Sửa", exact=True)

    def delete_button(self, name):
        return self.card(name).get_by_title("Xóa", exact=True)

    def field_error(self, message):
        return self.form.get_by_text(message, exact=True)
