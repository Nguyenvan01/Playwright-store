# Trang /orders/:id (OrderDetailPage.jsx). Tiêu đề khối h2 có chữ icon phía trước,
# vd: "receipt_long Thông tin đơn hàng".
import re

from pages.account.css_text import css_text, escape_regex


class OrderDetailPage:
    def __init__(self, page):
        self.page = page
        self.heading = page.get_by_role("heading", level=1)
        self.back_link = page.get_by_role("link", name="arrow_back Quay lại", exact=True)
        self.status_value = page.locator('p:text-is("Trạng thái đơn hàng") + p')
        self.payment_status_value = page.locator('p:text-is("Thanh toán") + p')
        self.items_heading = page.get_by_role(
            "heading", level=2, name=re.compile(r"^Sản phẩm đã đặt \(\d+\)$")
        )
        self.items_card = self.card("Sản phẩm đã đặt")
        self.item_rows = self.items_card.locator("div.divide-y > div")
        self.cancel_button = page.get_by_role("button", name="Hủy đơn hàng", exact=True)
        self.cancel_modal = page.locator("div.fixed.inset-0").filter(
            has_text="Bạn có chắc muốn hủy đơn hàng này? Hành động này không thể hoàn tác."
        )
        self.cancel_reason = self.cancel_modal.get_by_placeholder("Lý do hủy (tùy chọn)")
        self.confirm_cancel_button = self.cancel_modal.get_by_role(
            "button", name=re.compile(r"^(Xác nhận hủy|Đang hủy\.\.\.)$")
        )
        self.close_cancel_button = self.cancel_modal.get_by_role("button", name="Đóng", exact=True)
        self.back_to_orders_link = page.get_by_role("link", name="Quay lại đơn hàng", exact=True)

    def card(self, title):
        """Khối (card) theo tiêu đề h2, vd: "Thông tin giao hàng", "Chi tiết thanh toán"."""
        return self.page.locator("main div.rounded-lg").filter(
            has=self.page.get_by_role("heading", level=2, name=re.compile(rf"(^|\s){escape_regex(title)}"))
        )

    def row_value(self, card_title, label):
        """Giá trị của 1 dòng "nhãn - giá trị" trong khối."""
        return self.card(card_title).locator(f'span:text-is("{css_text(label)}") + span')

    def item_row(self, name):
        return self.item_rows.filter(has=self.page.get_by_text(name, exact=True))

    def message(self, text):
        return self.page.locator("main").get_by_text(text, exact=True)
