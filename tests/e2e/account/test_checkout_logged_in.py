# ============================================================
# TEST: THANH TOÁN KHI ĐÃ ĐĂNG NHẬP
# Mục tiêu: điền sẵn từ tài khoản, đăng xuất trên checkout, payload tạo đơn, trang đặt hàng thành công
# Dữ liệu: data/account/checkout.json, data/checkout/addresses.json
#          User trong localStorage được thay bằng user mẫu (seed_stored_user) để dữ liệu điền sẵn ổn định;
#          token vẫn là token thật của tài khoản test. Tạo đơn luôn được mock (trừ ACC-CO-05).
# Kết quả mong đợi: form điền sẵn đúng, payload POST /api/orders đúng, trang thành công đủ thông tin
# ============================================================
import pytest

from tests.e2e.account.support import API
from utils.cases import case_params, known_bug, require
from utils.data_loader import load_data

DATA = load_data("account/checkout.json")
ADDRESS = load_data("checkout/addresses.json")[DATA["address"]]
USER = DATA["user"]
CART_ITEM_NAME = str(DATA["cartItem"]["name"])

pytestmark = pytest.mark.role("customer")


class TestCheckoutPrefill:
    """Thanh toán khi đã đăng nhập - Điền sẵn thông tin từ tài khoản (data-driven)"""

    @pytest.mark.parametrize("case", case_params(DATA["prefill"]))
    def test_prefill(self, k, case):
        """Điền sẵn thông tin từ tài khoản (data-driven)"""
        k.account.seed_stored_user(case["user"])
        k.cart.seed_cart([DATA["cartItem"]])
        k.checkout.open_checkout()
        k.account.verify_checkout_account(str(case["user"]["name"]), str(case["user"]["email"]))
        k.account.verify_checkout_prefill(case["expected"])


class TestCheckoutWithCart:
    """Thanh toán khi đã đăng nhập - Có sản phẩm trong giỏ"""

    @pytest.fixture(autouse=True)
    def opened_checkout(self, k):
        k.account.seed_stored_user(USER)
        k.cart.seed_cart([DATA["cartItem"]])
        k.checkout.open_checkout()
        k.account.verify_checkout_account(USER["name"], USER["email"])

    def test_logout_on_checkout(self, k):
        """[ACC-CO-01] Đăng xuất ngay trên trang thanh toán: chuyển sang chế độ khách, giữ giỏ hàng"""
        k.account.logout_on_checkout()
        k.account.verify_checkout_guest_mode()
        k.checkout.verify_product_in_checkout(CART_ITEM_NAME)

    @pytest.mark.parametrize("case", case_params(DATA["payments"]))
    def test_order_payload(self, k, case):
        """Payload tạo đơn theo phương thức thanh toán (mock, data-driven)"""
        k.common.mock_write("POST", API["createOrder"], DATA["createResponse"], 201)
        k.checkout.fill_shipping(ADDRESS)
        k.checkout.choose_payment(case["payment"])
        k.checkout.place_order()
        k.common.verify_request("POST", "/api/orders", case["expectedPayload"])

    @pytest.mark.smoke
    def test_cod_success_page(self, k):
        """[ACC-CO-02] Đặt hàng COD thành công: trang thành công hiển thị đủ thông tin"""
        s = DATA["success"]
        k.common.mock_write("POST", API["createOrder"], DATA["createResponse"], 201)
        k.checkout.fill_shipping(ADDRESS)
        k.checkout.choose_payment("cod")
        k.checkout.place_order()
        k.checkout.verify_order_success(s["heading"], DATA["orderNumber"])
        k.account.verify_order_success_number(DATA["orderNumber"])
        k.account.verify_order_success_info("Thông tin thanh toán", s["payment"])
        k.account.verify_order_success_info("Người nhận", s["recipient"])
        k.account.verify_order_success_info("Chi tiết thanh toán", s["totals"])
        k.account.verify_order_success_links()
        k.cart.verify_stored_item_count(0)

    def test_cod_success_status(self, k, request):
        """[ACC-CO-03] Trang thành công (COD) hiển thị đúng trạng thái đơn vừa tạo"""
        known_bug(
            request,
            'OrderSuccessPage.jsx:188 luôn ghi "Đã xác nhận" cho COD, trong khi backend tạo đơn với '
            'status "pending" (Chờ xác nhận)',
        )
        k.common.mock_write("POST", API["createOrder"], DATA["createResponse"], 201)
        k.checkout.fill_shipping(ADDRESS)
        k.checkout.place_order()
        k.checkout.verify_order_success(DATA["success"]["heading"], DATA["orderNumber"])
        k.account.verify_order_success_info(
            "Thông tin thanh toán", {"Trạng thái": DATA["success"]["codStatusExpected"]}
        )

    def test_view_orders_from_success(self, k):
        """[ACC-CO-04] Từ trang thành công bấm Xem đơn hàng thấy đơn vừa đặt"""
        k.common.mock_write("POST", API["createOrder"], DATA["createResponse"], 201)
        k.common.mock_get(API["orders"], DATA["ordersAfter"])
        k.checkout.fill_shipping(ADDRESS)
        k.checkout.place_order()
        k.checkout.verify_order_success(DATA["success"]["heading"], DATA["orderNumber"])
        k.account.open_orders_from_success()
        k.account.verify_order_list([DATA["orderNumber"]])
        k.account.verify_order_status(DATA["orderNumber"], "Chờ xác nhận")


class TestCheckoutRealOrder:
    """Thanh toán khi đã đăng nhập"""

    def test_real_bank_transfer_order(self, k, purchasable, request):
        """[ACC-CO-05] Đặt hàng thật bằng Chuyển khoản ngân hàng (ghi DB)"""
        require("allowWrite")
        known_bug(
            request,
            "CheckoutPage.jsx:541 gửi payment_method 'bank', vi phạm CHECK orders.payment_method "
            "(database/schema.pg.sql:417) -> backend 500 'Lỗi server khi tạo đơn hàng'",
        )
        k.catalog.open_product(purchasable["product"]["slug"])
        k.catalog.add_to_cart(purchasable["size"]["label"])
        k.checkout.open_checkout()
        k.checkout.fill_shipping(ADDRESS)
        k.checkout.choose_payment("bank")
        k.checkout.place_order()
        k.checkout.verify_order_success("Đang chờ thanh toán")
