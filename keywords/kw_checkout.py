# THƯ VIỆN KEYWORD - NHÓM checkout: form giao hàng, phương thức thanh toán, đặt hàng (mock API).
from playwright.sync_api import expect

from keywords.base_keywords import BaseKeywords, keyword
from utils.assertions import assert_subset
from utils.routes import ROUTES

# Tên ô trong dữ liệu (camelCase) -> thuộc tính của CheckoutPage.
SHIPPING_FIELDS = {
    "firstName": "first_name",
    "lastName": "last_name",
    "phone": "phone",
    "address": "address",
}


class CheckoutKeywords(BaseKeywords):
    group = "checkout"

    def __init__(self, page, po, api, common=None):
        super().__init__(page, po, api, common)
        # Payload đơn hàng cuối cùng bắt được qua mockCreateOrder.
        self._last_order_payload = None

    @keyword("openCheckout")
    def open_checkout(self):
        """Mở trang thanh toán."""
        with self.step("Mở trang thanh toán"):
            self.po.checkout.goto()

    @keyword("verifyEmptyCheckout")
    def verify_empty_checkout(self):
        """Kiểm tra trang thanh toán báo giỏ trống, không có nút Thanh toán."""
        with self.step("Kiểm tra trang thanh toán báo giỏ trống"):
            expect(self.po.checkout.empty_cart_heading).to_be_visible()
            expect(self.po.checkout.submit_button).to_have_count(0)

    @keyword("verifyProductInCheckout")
    def verify_product_in_checkout(self, name):
        """Kiểm tra sản phẩm hiển thị trong khối sản phẩm của trang thanh toán."""
        with self.step(f'Kiểm tra trang thanh toán có "{name}"'):
            expect(self.po.checkout.products_section).to_contain_text(name)

    @keyword("verifyGuestLoginPrompt")
    def verify_guest_login_prompt(self):
        """Kiểm tra nút "Đăng nhập / Đăng ký" cho khách vãng lai."""
        with self.step("Kiểm tra có nút Đăng nhập / Đăng ký"):
            expect(self.po.checkout.login_button).to_be_visible()

    @keyword("fillShipping")
    def fill_shipping(self, info):
        """Điền thông tin giao hàng (dùng dữ liệu checkout/addresses.json)."""
        with self.step(
            f"Điền thông tin giao hàng: {info['firstName']} {info['lastName']}, {info['city']}"
        ):
            self.po.checkout.fill_shipping(info)

    @keyword("clearShippingField")
    def clear_shipping_field(self, field):
        """Xóa nội dung 1 ô trong form giao hàng: firstName | lastName | phone | address."""
        with self.step(f"Xóa ô {field}"):
            if field not in SHIPPING_FIELDS:
                raise ValueError(f"field không hợp lệ: {field!r}; chọn {list(SHIPPING_FIELDS)}")
            getattr(self.po.checkout, SHIPPING_FIELDS[field]).fill("")

    @keyword("chooseShipping")
    def choose_shipping(self, method):
        """Chọn phương thức giao hàng: standard | express."""
        with self.step(f"Chọn giao hàng {method}"):
            self.po.checkout.choose_shipping(method)

    @keyword("choosePayment")
    def choose_payment(self, method):
        """Chọn phương thức thanh toán: cod | bank | vnpay | momo."""
        with self.step(f"Chọn thanh toán {method}"):
            self.po.checkout.choose_payment(method)

    @keyword("verifySubmitEnabled")
    def verify_submit_enabled(self, enabled):
        """Kiểm tra nút Thanh toán bật/tắt."""
        with self.step(f"Kiểm tra nút Thanh toán {'bật' if enabled else 'tắt'}"):
            button = self.po.checkout.submit_button
            if enabled:
                expect(button).to_be_enabled()
            else:
                expect(button).to_be_disabled()

    @keyword("verifySummaryContains")
    def verify_summary_contains(self, text):
        """Kiểm tra khối tóm tắt đơn hàng chứa đoạn chữ / số tiền."""
        with self.step(f'Kiểm tra tóm tắt đơn có "{text}"'):
            expect(self.po.checkout.summary_section).to_contain_text(text)

    @keyword("mockCreateOrder")
    def mock_create_order(self, options=None):
        """Giả lập API tạo đơn: thành công (orderNumber) hoặc lỗi (status + message). Lưu lại payload gửi lên.

        options: dict khóa camelCase như bản TS/Excel, vd: {"orderNumber": "E2E-1"} hoặc
        {"status": 500, "message": "Lỗi"}.
        """
        options = options or {}
        status = options.get("status") or 200

        def handle(route):
            self._last_order_payload = route.request.post_data_json
            json_body = (
                {
                    "success": True,
                    "order": {"id": 99999, "order_number": options.get("orderNumber") or "E2E-000001"},
                }
                if status < 400
                else {"success": False, "message": options.get("message") or "Lỗi"}
            )
            route.fulfill(status=status, json=json_body)

        with self.step(f"Mock API tạo đơn -> {status}"):
            self.page.route("**/api/orders", handle)

    @keyword("placeOrder")
    def place_order(self):
        """Bấm nút Thanh toán."""
        with self.step("Bấm Thanh toán"):
            self.po.checkout.place_order()

    @keyword("verifyOrderSuccess")
    def verify_order_success(self, heading, order_number=None):
        """Kiểm tra trang đặt hàng thành công: tiêu đề + mã đơn (nếu có)."""
        with self.step(f'Kiểm tra "{heading}"{f" - mã {order_number}" if order_number else ""}'):
            expect(self.page).to_have_url(ROUTES["orderSuccess"])
            expect(self.po.order_success.heading).to_have_text(heading)
            if order_number:
                expect(self.po.order_success.order_number(order_number)).to_be_visible()

    @keyword("verifyLastOrderPayload")
    def verify_last_order_payload(self, expected):
        """Kiểm tra payload đơn hàng gửi lên backend chứa các trường mong đợi."""
        with self.step("Kiểm tra dữ liệu đơn hàng gửi lên server"):
            assert self._last_order_payload, "Chưa bắt được request tạo đơn (gọi mockCreateOrder trước)"
            assert_subset(self._last_order_payload, expected, "Payload đơn hàng")

    @keyword("verifyStillOnCheckout")
    def verify_still_on_checkout(self):
        """Kiểm tra vẫn ở trang thanh toán (đặt hàng thất bại)."""
        with self.step("Kiểm tra vẫn ở trang thanh toán"):
            expect(self.page).to_have_url(ROUTES["checkout"])

    @keyword("verifyOrderSuccessWithoutData")
    def verify_order_success_without_data(self):
        """Mở /order-success trực tiếp và kiểm tra báo không có dữ liệu đơn."""
        with self.step("Kiểm tra /order-success không có dữ liệu"):
            self.po.order_success.goto()
            expect(self.po.order_success.not_found).to_be_visible()
