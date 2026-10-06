# Trang quản trị Cài đặt (/admin/settings).
import re

from pages.admin.marketing.admin_table import AdminTable


class SettingsPage(AdminTable):
    path = "/admin/settings"

    @property
    def page_heading(self):
        return self.page.locator("main h1")

    @property
    def save_button(self):
        return self.page.get_by_role("button", name=re.compile(r"^(Lưu cài đặt|Đang lưu\.\.\.)$"))

    def tab(self, label):
        return self.page.get_by_role("button", name=label, exact=True)

    @property
    def panel(self):
        """Khung nội dung tab (chứa tiêu đề tab đang mở + các ô nhập)."""
        return self.page.locator("main div.rounded-xl > div.p-6").first

    @property
    def field_labels(self):
        """Nhãn của các ô nhập trong tab đang mở."""
        return self.panel.locator("label")

    @property
    def panel_ready(self):
        """Tab đã tải xong dữ liệu (không còn skeleton)."""
        return self.panel.locator("label").first
