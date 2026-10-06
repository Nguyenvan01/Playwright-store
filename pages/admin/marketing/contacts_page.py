# Trang quản trị Liên hệ (/admin/contacts).
from pages.admin.marketing.admin_table import AdminTable


class ContactsPage(AdminTable):
    path = "/admin/contacts"
    search_placeholder = "Tìm theo tên, email, số điện thoại, nội dung..."

    @property
    def page_heading(self):
        return self.page.locator("main h1")

    @property
    def status_select(self):
        return self.select_with_option("processed")

    @property
    def list_ready(self):
        return self.table.locator("tbody tr td p, tbody tr td button").first
