# Trang /order-success: kết quả đặt hàng.
from pages.base_page import BasePage


class OrderSuccessPage(BasePage):
    path = "/order-success"

    def __init__(self, page):
        super().__init__(page)
        self.heading = page.get_by_role("heading", level=1)
        self.not_found = page.get_by_role("heading", name="Không tìm thấy thông tin đơn hàng")

    def order_number(self, value):
        return self.page.get_by_text(value)
