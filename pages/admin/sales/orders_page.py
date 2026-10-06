# Trang Đơn hàng (/admin/orders): thẻ trạng thái, bộ lọc, bảng, modal chi tiết, modal hủy đơn.
import re

from pages.admin.admin_ui import AdminUi
from pages.admin.sales.admin_api_mock import modal_by_heading, pagination_bar


class OrdersPage:
    path = "/admin/orders"

    def __init__(self, page):
        self.page = page
        self.ui = AdminUi(page)
        self.search_input = page.get_by_placeholder("Tìm mã đơn, tên, SĐT, email...", exact=True)
        self.status_select = page.locator("select").filter(
            has=page.locator("option", has_text="Tất cả trạng thái")
        )
        self.payment_select = page.locator("select").filter(
            has=page.locator("option", has_text="Tất cả TT thanh toán")
        )
        self.filters_button = page.get_by_role("button", name="Bộ lọc", exact=True)
        self.clear_filters_button = page.get_by_role("button", name="Xóa bộ lọc", exact=True)
        self.total_text = page.locator("main").get_by_text(re.compile(r"^\d+ đơn hàng$"))
        self.empty_text = page.get_by_text("Không có đơn hàng nào", exact=True)
        self.detail_modal = modal_by_heading(page, re.compile(r"^Chi tiết đơn hàng #"))
        self.cancel_modal = modal_by_heading(page, "Hủy đơn hàng")
        self.cancel_reason = page.get_by_placeholder("Nhập lý do hủy đơn hàng...", exact=True)

    def status_card(self, label):
        """Thẻ thống kê trạng thái (nút gồm nhãn + số lượng)."""
        return self.page.get_by_role("button", name=re.compile(rf"^{re.escape(label)}\s*\d+$"))

    def status_card_count(self, label):
        return self.status_card(label).locator("p")

    def date_input(self, label):
        """label: "Từ ngày" | "Đến ngày"."""
        return self.ui.field(label)

    def row(self, order_number):
        return (
            self.page.locator("tbody tr")
            .filter(has=self.page.get_by_text(order_number, exact=True))
            .first
        )

    @property
    def order_numbers(self):
        return self.page.locator("main tbody tr > td:first-child > span.font-bold")

    def row_payment(self, order_number):
        return self.row(order_number).locator("td").nth(5)

    def row_status(self, order_number):
        return self.row(order_number).locator("td").nth(6)

    def row_action(self, order_number, title):
        """title: "Xem chi tiết" | "Hủy đơn"."""
        return self.row(order_number).get_by_title(title, exact=True)

    # --- Modal chi tiết ---
    @property
    def detail_heading(self):
        return self.detail_modal.get_by_role("heading", level=3)

    @property
    def detail_close_button(self):
        return self.detail_modal.get_by_role("button").first

    @property
    def detail_status_badge(self):
        """Huy hiệu trạng thái đơn trên đầu modal."""
        return self.detail_modal.locator("div.sticky span.rounded-full").first

    @property
    def detail_payment_badge(self):
        return self.detail_modal.locator("div.sticky span.rounded-full").nth(1)

    def detail_info(self, label):
        """Ô thông tin nhỏ trong modal, vd: "Phương thức thanh toán" -> giá trị."""
        return (
            self.detail_modal.locator("div.bg-gray-50.rounded-xl")
            .filter(has=self.page.locator("p", has_text=re.compile(rf"^{re.escape(label)}$")))
            .locator("p.font-semibold")
        )

    def detail_block(self, heading):
        return (
            self.detail_modal.locator("div.rounded-xl.p-4")
            .filter(has=self.page.get_by_role("heading", name=heading, exact=True))
            .first
        )

    @property
    def status_section(self):
        return self.detail_block("Cập nhật trạng thái đơn hàng")

    @property
    def status_buttons(self):
        return self.status_section.get_by_role("button")

    @property
    def payment_section(self):
        return self.detail_block("Cập nhật thanh toán")

    @property
    def detail_payment_select(self):
        return self.payment_section.locator("select")

    @property
    def processing_warning(self):
        return self.detail_modal.get_by_text("Lưu ý khi xử lý", exact=True)

    @property
    def detail_items(self):
        return self.detail_modal.locator("tbody tr")

    def summary_value(self, label):
        """Dòng tổng kết (Tạm tính / Phí vận chuyển / Tổng thanh toán...) -> giá trị."""
        return (
            self.detail_modal.locator("div.flex.justify-between")
            .filter(has=self.page.get_by_text(label, exact=True))
            .locator("span")
            .last
        )

    @property
    def detail_logs(self):
        return self.detail_modal.locator("div.space-y-2 > div.flex.items-start")

    # --- Modal hủy ---
    @property
    def cancel_notes(self):
        return self.cancel_modal.locator("div.bg-amber-50 p")

    # --- Phân trang ---
    @property
    def pagination(self):
        return pagination_bar(self.page)

    def page_button(self, n):
        return self.pagination.get_by_role("button", name=str(n), exact=True)
