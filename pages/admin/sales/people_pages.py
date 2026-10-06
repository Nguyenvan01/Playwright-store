# Trang Khách hàng / Nhân viên (/admin/customers, /admin/employees).
import re

from pages.admin.sales.admin_api_mock import modal_by_heading, pagination_bar


class PeopleListPage:
    """Phần chung của trang Khách hàng / Nhân viên: bảng, modal, lỗi field, phân trang."""

    def __init__(self, page):
        self.page = page

    def row(self, name):
        return self.rows(name).first

    def rows(self, name):
        return self.page.locator("tbody tr").filter(has=self.page.get_by_text(name, exact=True))

    def cell(self, name, index):
        return self.row(name).locator("td").nth(index)

    def modal(self, heading):
        return modal_by_heading(self.page, heading)

    def field_errors(self, heading):
        """Thông báo lỗi dưới các ô nhập trong modal đang mở (chữ đỏ)."""
        return self.modal(heading).locator("p.text-red-500")

    @property
    def pagination(self):
        return pagination_bar(self.page)

    @property
    def pagination_text(self):
        return self.pagination.get_by_text(re.compile(r"^Trang \d+"))

    def page_button(self, n):
        return self.pagination.get_by_role("button", name=str(n), exact=True)

    @property
    def next_page_button(self):
        return self.pagination.get_by_role("button").last


class CustomersPage(PeopleListPage):
    """Trang Khách hàng (/admin/customers). Cột: 0 Khách hàng, 1 Liên hệ, 2 Đơn hàng, 3 Tổng chi tiêu, 4 Điểm, 5 Trạng thái, 6 Thao tác."""

    path = "/admin/customers"
    search_placeholder = "Tìm theo tên, email, SĐT..."

    def status_badge(self, name):
        return self.cell(name, 5).locator("span")

    def detail_value(self, label):
        """Giá trị 1 dòng "Nhãn: giá trị" trong modal Chi tiết khách hàng."""
        return (
            self.modal("Chi tiết khách hàng")
            .locator("div.flex.justify-between")
            .filter(has=self.page.get_by_text(label, exact=True))
            .locator("span")
            .last
        )

    def detail_stat(self, label):
        """Ô số liệu (Đơn hàng / Tổng chi tiêu) trong modal chi tiết."""
        return (
            self.modal("Chi tiết khách hàng")
            .locator("div.rounded-lg.text-center")
            .filter(has=self.page.get_by_text(label, exact=True))
            .locator("p")
            .last
        )

    @property
    def detail_recent_orders(self):
        return self.modal("Chi tiết khách hàng").locator("div.space-y-2 > div.rounded-lg")

    @property
    def delete_warning(self):
        return self.modal("Xác nhận xóa").locator("p.text-orange-500")


class EmployeesPage(PeopleListPage):
    """Trang Nhân viên (/admin/employees). Cột: 0 Nhân viên, 1 Email, 2 Điện thoại, 3 Vai trò, 4 Ngày tạo, 5 Trạng thái, 6 Thao tác."""

    path = "/admin/employees"
    search_placeholder = "Tìm theo tên, email..."

    def __init__(self, page):
        super().__init__(page)
        self.heading = page.get_by_role("heading", name="Tài khoản nhân viên", exact=True)

    def role_badge(self, name):
        return self.cell(name, 3).locator("span")

    def toggle_button(self, name):
        """Nút gạt trạng thái (không có tên) ở cột Trạng thái."""
        return self.cell(name, 5).get_by_role("button")

    def edit_button(self, name):
        """Nút Sửa (icon, không có title) - nút đầu tiên ở cột Thao tác."""
        return self.cell(name, 6).get_by_role("button").first

    def delete_button(self, name):
        """Nút Xóa/Vô hiệu hóa (icon, không có title) - nút thứ 2 ở cột Thao tác."""
        return self.cell(name, 6).get_by_role("button").nth(1)

    def form_modal(self, editing):
        return self.modal("Cập nhật nhân viên" if editing else "Thêm nhân viên mới")

    def email_input(self, editing=False):
        """Ô Email trong form nhân viên (input type=email có kiểm tra native của trình duyệt)."""
        return self.form_modal(editing).locator('input[type="email"]')
