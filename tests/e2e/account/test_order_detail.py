# ============================================================
# TEST: CHI TIẾT ĐƠN HÀNG
# Mục tiêu: nội dung trang /orders/:id, nút hủy theo trạng thái, hủy đơn, lỗi tải đơn, điều hướng
# Dữ liệu: data/account/order-detail.json (mock GET /api/orders/:id), orders.json
# Kết quả mong đợi: thông tin / sản phẩm / tổng tiền khớp JSON; POST hủy đúng payload
# ============================================================
import pytest

from tests.e2e.account.support import API
from utils.cases import case_params, known_bug
from utils.data_loader import load_data

DATA = load_data("account/order-detail.json")
ORDERS = load_data("account/orders.json")
PENDING_ORDER = DATA["pending"]["order"]
PENDING_ID = PENDING_ORDER["id"]

pytestmark = pytest.mark.role("customer")


def verify_detail_view(k, view):
    """Kiểm tra toàn bộ nội dung trang chi tiết theo dữ liệu mong đợi trong JSON."""
    k.account.verify_order_detail_heading(view["heading"])
    k.account.verify_order_detail_status(view["status"], view["payment"])
    k.account.verify_order_detail_info("Thông tin đơn hàng", view["orderInfo"])
    k.account.verify_order_detail_info("Thông tin giao hàng", view["shippingInfo"])
    k.account.verify_order_detail_items(view["itemsHeading"], [i["name"] for i in view["items"]])
    for item in view["items"]:
        k.account.verify_order_detail_item(item["name"], item["texts"])
    k.account.verify_order_detail_totals(view["totals"])


class TestOrderDetail:
    """Chi tiết đơn hàng"""

    @pytest.mark.smoke
    def test_pending_order(self, k):
        """[ACC-ODT-01] Đơn chờ xác nhận: thông tin, sản phẩm, giảm giá, phí giao nhanh"""
        k.common.mock_get(API["orderDetail"], DATA["pending"])
        k.account.open_order_detail(PENDING_ID)
        verify_detail_view(k, DATA["pendingView"])

    def test_delivered_order(self, k):
        """[ACC-ODT-02] Đơn đã giao: miễn phí vận chuyển, có mã vận đơn, không có dòng giảm giá"""
        order = DATA["delivered"]["order"]
        k.common.mock_get(API["orderDetail"], DATA["delivered"])
        k.account.open_order_detail(order["id"])
        verify_detail_view(k, DATA["deliveredView"])
        k.account.verify_order_detail_cancelable(False)

    def test_labels_match_list(self, k, request):
        """[ACC-ODT-03] Nhãn trạng thái/thanh toán thống nhất với trang danh sách (trả hàng, thanh toán một phần)"""
        known_bug(
            request,
            'OrderDetailPage.jsx:22,28 dùng nhãn "Trả hàng" / "Thanh toán 1 phần", khác accountUtils.js:36,42 '
            'của trang danh sách ("Đã trả hàng" / "Thanh toán một phần")',
        )
        order = DATA["returned"]["order"]
        k.common.mock_get(API["orderDetail"], DATA["returned"])
        k.account.open_order_detail(order["id"])
        k.account.verify_order_detail_status(DATA["returnedExpected"]["status"], DATA["returnedExpected"]["payment"])

    @pytest.mark.parametrize("case", case_params(DATA["statuses"]))
    def test_cancel_button_by_status(self, k, case):
        """Nút Hủy đơn hàng theo trạng thái (data-driven)"""
        k.common.mock_get(
            API["orderDetail"], {**DATA["pending"], "order": {**PENDING_ORDER, "status": case["status"]}}
        )
        k.account.open_order_detail(PENDING_ID)
        k.account.verify_order_detail_status(case["statusLabel"], DATA["pendingView"]["payment"])
        k.account.verify_order_detail_cancelable(case["cancelable"])

    @pytest.mark.parametrize("case", case_params(DATA["errors"]))
    def test_load_error(self, k, case):
        """Lỗi tải đơn hàng (mock, data-driven)"""
        k.common.mock_get(API["orderDetail"], case["response"], case["status"])
        k.account.open_order_detail(999999)
        k.account.verify_order_detail_error(case["message"])

    def test_error_back_to_orders(self, k):
        """[ACC-ODT-08] Màn hình lỗi: nút Quay lại đơn hàng về /orders"""
        error = DATA["errors"][1]
        k.common.mock_get(API["orderDetail"], error["response"], error["status"])
        k.common.mock_get(API["orders"], ORDERS["list"])
        k.account.open_order_detail(999999)
        k.account.back_to_orders_from_error()
        k.account.verify_order_list(ORDERS["allCodes"])

    def test_back_link_to_orders(self, k):
        """[ACC-ODT-09] Nút Quay lại ở đầu trang chi tiết về danh sách đơn"""
        k.common.mock_get(API["orderDetail"], DATA["pending"])
        k.common.mock_get(API["orders"], ORDERS["list"])
        k.account.open_order_detail(PENDING_ID)
        k.account.verify_order_detail_heading(DATA["pendingView"]["heading"])
        k.account.go_back_from_order_detail()
        k.account.verify_orders_loaded()


class TestCancelFromDetail:
    """Chi tiết đơn hàng - Hủy đơn từ trang chi tiết"""

    @pytest.fixture(autouse=True)
    def opened_pending(self, k):
        k.common.mock_get(API["orderDetail"], DATA["pending"])
        k.account.open_order_detail(PENDING_ID)
        k.account.verify_order_detail_status(DATA["pendingView"]["status"], DATA["pendingView"]["payment"])

    def test_cancel_with_reason(self, k):
        """[ACC-ODT-04] Hủy có lý do: gửi lý do, đóng hộp thoại, trạng thái thành Đã hủy"""
        k.common.mock_write("POST", API["cancelOrder"], DATA["cancel"]["response"])
        k.account.open_cancel_order_dialog()
        k.account.confirm_cancel_order(DATA["cancel"]["reason"])
        k.common.verify_request("POST", f"/api/orders/{PENDING_ID}/cancel", {"reason": DATA["cancel"]["reason"]})
        k.account.verify_cancel_order_dialog(False)
        k.account.verify_order_detail_status("Đã hủy", DATA["pendingView"]["payment"])
        k.account.verify_order_detail_cancelable(False)

    def test_cancel_without_reason(self, k):
        """[ACC-ODT-05] Hủy không nhập lý do: gửi reason rỗng"""
        k.common.mock_write("POST", API["cancelOrder"], DATA["cancel"]["response"])
        k.account.open_cancel_order_dialog()
        k.account.confirm_cancel_order()
        k.common.verify_request("POST", f"/api/orders/{PENDING_ID}/cancel", {"reason": ""})
        k.account.verify_order_detail_status("Đã hủy", DATA["pendingView"]["payment"])

    def test_close_cancel_dialog(self, k):
        """[ACC-ODT-06] Đóng hộp xác nhận: không gửi request, đơn giữ nguyên"""
        k.common.mock_write("POST", API["cancelOrder"], DATA["cancel"]["response"])
        k.account.open_cancel_order_dialog()
        k.account.close_cancel_order_dialog()
        k.account.verify_cancel_order_dialog(False)
        k.common.verify_no_request("POST", "/cancel")
        k.account.verify_order_detail_status(DATA["pendingView"]["status"], DATA["pendingView"]["payment"])
        k.account.verify_order_detail_cancelable(True)

    def test_cancel_failure_shows_error(self, k, request):
        """[ACC-ODT-07] Hủy thất bại hiển thị thông báo lỗi từ server"""
        known_bug(
            request,
            "OrderDetailPage.jsx:156 - catch {} nuốt lỗi hủy đơn, hộp thoại vẫn mở và không có thông báo nào",
        )
        k.common.mock_write(
            "POST", API["cancelOrder"], DATA["cancel"]["errorResponse"], DATA["cancel"]["errorStatus"]
        )
        k.account.open_cancel_order_dialog()
        k.account.confirm_cancel_order(DATA["cancel"]["reason"])
        k.common.verify_request("POST", f"/api/orders/{PENDING_ID}/cancel")
        k.common.verify_text_visible(str(DATA["cancel"]["errorResponse"]["message"]))
