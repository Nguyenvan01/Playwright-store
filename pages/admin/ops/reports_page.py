# Trang quản trị Báo cáo (/admin/reports).
from pages.admin.marketing.admin_table import AdminTable


class ReportsPage(AdminTable):
    path = "/admin/reports"

    @property
    def page_heading(self):
        return self.page.locator("main h1")

    @property
    def period_select(self):
        """Select chọn kỳ báo cáo (có option "custom")."""
        return self.select_with_option("custom")

    @property
    def date_inputs(self):
        return self.page.locator('main input[type="date"]')

    @property
    def filter_button(self):
        return self.page.get_by_role("button", name="Lọc", exact=True)

    @property
    def export_button(self):
        return self.page.get_by_role("button", name="Xuất báo cáo", exact=True)

    def section(self, heading):
        """Khối (section) có tiêu đề h2."""
        return self.page.locator("section").filter(
            has=self.page.get_by_role("heading", name=heading, exact=True)
        )

    def section_rows(self, heading):
        """Dòng dữ liệu của bảng trong khối có tiêu đề `heading`."""
        return self.section(heading).locator("tbody tr")
