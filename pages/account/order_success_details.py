# Chi tiết trên trang /order-success (OrderSuccessPage.jsx) khi có dữ liệu đơn.
from pages.account.css_text import css_text


class OrderSuccessDetails:
    def __init__(self, page):
        self.page = page
        self.main = page.locator("main")
        self.order_number = self.main.locator('span:text-is("Mã đơn hàng:") + span')
        self.continue_links = self.main.get_by_role("link", name="Tiếp tục mua sắm", exact=True)
        self.view_orders_link = self.main.get_by_role("link", name="Xem đơn hàng", exact=True)

    def card(self, title):
        """Khối theo tiêu đề h2: "Thông tin thanh toán" | "Người nhận" | "Chi tiết thanh toán"."""
        return self.main.locator("div.rounded-2xl").filter(
            has=self.page.get_by_role("heading", level=2, name=title, exact=True)
        )

    def row_value(self, card_title, label):
        return self.card(card_title).locator(f'span:text-is("{css_text(label)}") + span')
