# Sidebar tài khoản bên trái. Có 2 phiên bản trong app:
# - AccountSidebar.jsx (hồ sơ, đơn hàng, yêu thích): link "Hồ sơ cá nhân", "Đơn hàng của tôi", "Yêu thích".
# - Sidebar riêng trong OrderDetailPage/AddressesPage: tên link có chữ ligature Material Symbols,
#   vd: "person Hồ sơ cá nhân", "location_on Sổ địa chỉ".
import re

from pages.account.css_text import escape_regex


class AccountSidebar:
    def __init__(self, page):
        self.page = page
        self.root = page.locator("main aside")
        self.logout_button = self.root.get_by_role("button", name=re.compile(r"Đăng xuất$"))

    def link(self, label):
        """Link theo nhãn hiển thị (bỏ qua chữ icon phía trước)."""
        return self.root.get_by_role("link", name=re.compile(rf"(^|\s){escape_regex(label)}$"))
