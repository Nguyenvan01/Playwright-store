# ============================================================
# TEST: THANH TOÁN
# Mục tiêu: giỏ trống, khách vãng lai, đặt hàng (mock API), thiếu thông tin, backend lỗi, đặt thật
# Dữ liệu: data/checkout/checkout.json (cartItem, orders, incomplete, serverErrors),
#          data/checkout/addresses.json (hcm, hanoi, danang)
# API cần quan sát: k.checkout.*, k.cart.seed_cart, k.cart.verify_stored_item_count
# Kết quả mong đợi: payload đơn đúng dữ liệu, trang /order-success đúng tiêu đề + mã đơn,
#                   lỗi backend giữ nguyên giỏ và ở lại /checkout
# ============================================================
import pytest

from utils.cases import case_params, require
from utils.data_loader import load_data

DATA = load_data("checkout/checkout.json")
ADDRESSES = load_data("checkout/addresses.json")
ITEM = DATA["cartItem"]


@pytest.fixture
def guest_with_cart(k):
    """Khách vãng lai, có sản phẩm trong giỏ."""
    k.cart.seed_cart([DATA["cartItem"]])
    k.checkout.open_checkout()


class TestCheckout:
    """Thanh toán"""

    def test_empty_cart(self, k):
        """Giỏ trống -> hiển thị thông báo, không có form"""
        k.checkout.open_checkout()
        k.checkout.verify_empty_checkout()

    def test_order_success_without_data(self, k):
        """/order-success không có dữ liệu đơn"""
        k.checkout.verify_order_success_without_data()

    def test_real_order_end_to_end(self, k, purchasable):
        """Đặt hàng thật end-to-end (ghi DB)"""
        require("allowWrite")
        k.catalog.open_product(purchasable["product"]["slug"])
        k.catalog.add_to_cart(purchasable["size"]["label"])
        k.checkout.open_checkout()
        k.checkout.fill_shipping(ADDRESSES["hcm"])
        k.checkout.place_order()
        k.checkout.verify_order_success("Đặt hàng thành công")


@pytest.mark.usefixtures("guest_with_cart")
class TestCheckoutGuest:
    """Thanh toán - Khách vãng lai, có sản phẩm trong giỏ"""

    @pytest.mark.smoke
    def test_shows_product_and_login(self, k):
        """Hiển thị sản phẩm và nút Đăng nhập"""
        k.checkout.verify_product_in_checkout(ITEM["name"])
        k.checkout.verify_guest_login_prompt()
        k.checkout.verify_submit_enabled(False)


@pytest.mark.usefixtures("guest_with_cart")
class TestCheckoutOrders:
    """Thanh toán - Khách vãng lai - Đặt hàng (mock API, data-driven)"""

    @pytest.mark.parametrize("case", case_params(DATA["orders"]))
    def test_place_order(self, k, case):
        address = ADDRESSES[case["address"]]
        order_number = f"E2E-{case['id']}"

        k.checkout.mock_create_order({"orderNumber": order_number})
        k.checkout.fill_shipping(address)
        k.checkout.choose_shipping(case["shippingMethod"])
        k.checkout.choose_payment(case["payment"])
        if case["expected"]["shippingFee"]:
            k.checkout.verify_summary_contains("30.000")
        k.checkout.place_order()

        k.checkout.verify_order_success(case["expected"]["heading"], order_number)
        k.checkout.verify_last_order_payload(
            {
                "recipient_name": f"{address['firstName']} {address['lastName']}",
                "recipient_phone": address["phone"],
                "city": address["city"],
                "district": address["district"],
                "shipping_method": case["shippingMethod"],
                "shipping_fee": case["expected"]["shippingFee"],
                "payment_method": case["payment"],
                "payment_status": case["expected"]["paymentStatus"],
                # Tương đương expect.objectContaining: chỉ so các trường liệt kê.
                "items": [
                    {
                        "product_name": ITEM["name"],
                        "quantity": ITEM["quantity"],
                        "unit_price": ITEM["price"],
                    }
                ],
            }
        )
        k.cart.verify_stored_item_count(0)


@pytest.mark.usefixtures("guest_with_cart")
class TestCheckoutIncomplete:
    """Thanh toán - Khách vãng lai - Thiếu thông tin bắt buộc (data-driven)"""

    @pytest.mark.parametrize("case", case_params(DATA["incomplete"]))
    def test_missing_field(self, k, case):
        k.checkout.fill_shipping(ADDRESSES["hcm"])
        k.checkout.verify_submit_enabled(True)
        k.checkout.clear_shipping_field(case["missing"])
        k.checkout.verify_submit_enabled(False)


@pytest.mark.usefixtures("guest_with_cart")
class TestCheckoutServerErrors:
    """Thanh toán - Khách vãng lai - Backend lỗi (mock, data-driven)"""

    @pytest.mark.parametrize("case", case_params(DATA["serverErrors"]))
    def test_server_error(self, k, case):
        k.checkout.mock_create_order({"status": case["status"], "message": case["message"]})
        k.checkout.fill_shipping(ADDRESSES["hcm"])
        k.checkout.place_order()
        k.common.verify_toast(case["message"])
        k.checkout.verify_still_on_checkout()
        k.cart.verify_stored_item_count(1)
