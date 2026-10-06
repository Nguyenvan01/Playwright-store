# Trang quản trị Mã giảm giá (/admin/coupons) - nút sửa/xóa/bật tắt không có tên.
from pages.admin.marketing.admin_table import AdminTable


class CouponsPage(AdminTable):
    path = "/admin/coupons"

    @property
    def add_button(self):
        return self.page.get_by_role("button", name="Thêm mã", exact=True)

    @property
    def empty_text(self):
        return self.page.get_by_text("Chưa có mã giảm giá nào", exact=True)

    @property
    def list_ready(self):
        return self.table.or_(self.empty_text).first

    def edit_button(self, code):
        """Nút sửa (icon, không tên) trong cột Thao tác."""
        return self.row(code).locator("td").last.get_by_role("button").nth(0)

    def delete_button(self, code):
        """Nút xóa (icon, không tên) trong cột Thao tác."""
        return self.row(code).locator("td").last.get_by_role("button").nth(1)

    def toggle_button(self, code, column):
        """Nút bật/tắt (icon, không tên) trong cột "Công khai" hoặc "Trạng thái"."""
        return self.cell(code, column).get_by_role("button")
