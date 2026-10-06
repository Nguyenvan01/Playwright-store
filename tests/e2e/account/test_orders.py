# ============================================================
# TEST: ĐƠN HÀNG CỦA TÔI
# Mục tiêu: thống kê, lọc theo tab / ô thống kê, tìm theo mã, nhãn trạng thái, hủy đơn, điều hướng
# Dữ liệu: data/account/orders.json (mock GET /api/orders đủ mọi trạng thái), order-detail.json
# Kết quả mong đợi: danh sách + thống kê khớp dữ liệu; POST hủy đơn đúng payload
# ============================================================
import pytest

from tests.e2e.account.support import API
from utils.cases import case_params, known_bug
from utils.data_loader import load_data

DATA = load_data("account/orders.json")
DETAIL = load_data("account/order-detail.json")

pytestmark = pytest.mark.role("customer")


class TestOrdersEmpty:
    """Đơn hàng của tôi"""

    def test_no_orders(self, k):
        """[ACC-ORD-E01] Tài khoản chưa có đơn: thống kê 0 và thông báo trống"""
        k.common.mock_get(API["orders"], DATA["empty"])
        k.account.open_orders()
        k.account.verify_orders_loaded()
        k.account.verify_orders_empty(DATA["emptyMessage"])
        k.account.verify_order_stats(
            {"Tất cả đơn": 0, "Chờ xác nhận": 0, "Đang giao": 0, "Đã giao": 0, "Đã hủy": 0}
        )


class TestOrdersWithData:
    """Đơn hàng của tôi - Có đơn hàng"""

    @pytest.fixture(autouse=True)
    def opened_orders(self, k):
        k.common.mock_get(API["orders"], DATA["list"])
        k.account.open_orders()
        k.account.verify_orders_loaded()

    @pytest.mark.smoke
    def test_stats_and_all_orders(self, k):
        """[ACC-ORD-01] Hiển thị thống kê và toàn bộ đơn (mới nhất trước)"""
        k.account.verify_order_stats(DATA["stats"])
        k.account.verify_order_list(DATA["allCodes"])

    @pytest.mark.parametrize("case", case_params(DATA["tabs"]))
    def test_filter_by_tab(self, k, case):
        """Lọc theo tab trạng thái (data-driven)"""
        k.account.filter_orders_by_status(case["tab"])
        k.account.verify_order_list(case["expected"])

    @pytest.mark.parametrize("case", case_params(DATA["statButtons"]))
    def test_filter_by_stat(self, k, case):
        """Lọc bằng ô thống kê (data-driven)"""
        k.account.click_order_stat(case["stat"])
        k.account.verify_order_list(case["expected"])

    @pytest.mark.parametrize("case", case_params(DATA["search"]))
    def test_search(self, k, case):
        """Tìm theo mã đơn (data-driven)"""
        k.account.search_orders(case["query"])
        if case["expected"]:
            k.account.verify_order_list(case["expected"])
        else:
            k.account.verify_orders_empty(DATA["noMatchMessage"])

    def test_tab_and_search_combined(self, k):
        """[ACC-ORD-S05] Kết hợp tab và tìm kiếm: mã đúng nhưng khác trạng thái -> không có kết quả"""
        k.account.filter_orders_by_status("Đã giao")
        k.account.search_orders(DATA["cancel"]["pendingCode"])
        k.account.verify_orders_empty(DATA["noMatchMessage"])
        k.account.filter_orders_by_status("Tất cả")
        k.account.verify_order_list([DATA["cancel"]["pendingCode"]])

    @pytest.mark.parametrize("case", case_params(DATA["labels"]))
    def test_order_labels(self, k, case):
        """Thông tin từng đơn: nhãn trạng thái, thanh toán, vận chuyển (data-driven)"""
        k.account.verify_order_status(case["code"], case["status"])
        k.account.verify_order_item(case["code"], case["texts"])

    @pytest.mark.parametrize("case", case_params(DATA["cancelButtons"]))
    def test_cancel_button_by_status(self, k, case):
        """Nút Hủy đơn theo trạng thái (data-driven)"""
        k.account.verify_order_cancelable(case["code"], case["cancelable"])

    @pytest.mark.smoke
    def test_cancel_pending_order(self, k):
        """[ACC-ORD-C01] Hủy đơn chờ xác nhận: gửi lý do mặc định, đổi trạng thái và thống kê"""
        c = DATA["cancel"]
        k.common.mock_write("POST", API["cancelOrder"], c["response"])
        k.account.cancel_order_from_list(c["pendingCode"])
        k.common.verify_request("POST", f"/api/orders/{c['pendingId']}/cancel", {"reason": c["reason"]})
        k.account.verify_order_status(c["pendingCode"], "Đã hủy")
        k.account.verify_order_cancelable(c["pendingCode"], False)
        k.account.verify_order_stats(c["statsAfter"])

    def test_cancel_failure_shows_error(self, k, request):
        """[ACC-ORD-C02] Hủy đơn thất bại hiển thị thông báo lỗi cho khách"""
        known_bug(
            request,
            "OrdersPage.jsx:87-88 - lỗi POST /orders/:id/cancel chỉ gọi lại fetchOrders(), không hiển thị "
            "thông báo -> khách không biết vì sao hủy không được",
        )
        c = DATA["cancel"]
        k.common.mock_write("POST", API["cancelOrder"], c["errorResponse"], c["errorStatus"])
        k.account.cancel_order_from_list(c["pendingCode"])
        k.common.verify_request("POST", f"/api/orders/{c['pendingId']}/cancel")
        k.account.verify_order_status(c["pendingCode"], "Chờ xác nhận")
        k.common.verify_text_visible(str(c["errorResponse"]["message"]))

    def test_open_detail_from_list(self, k):
        """[ACC-ORD-D01] Xem chi tiết từ danh sách mở đúng trang chi tiết đơn"""
        k.common.mock_get(API["orderDetail"], DETAIL["pending"])
        k.account.open_order_from_list(DATA["cancel"]["pendingCode"])
        k.common.verify_url(f"/orders/{DATA['cancel']['pendingId']}")
        k.account.verify_order_detail_heading(DETAIL["pendingView"]["heading"])

    def test_sidebar_navigation(self, k):
        """[ACC-ORD-N01] Sidebar: chuyển sang Yêu thích rồi Hồ sơ (điều hướng trong app)"""
        k.account.click_sidebar_link("Yêu thích")
        k.common.verify_url("/favorites")
        k.account.verify_wishlist_loaded()
        k.account.click_sidebar_link("Hồ sơ cá nhân")
        k.common.verify_url("/profile")
        k.account.verify_profile_loaded()

    def test_logout_from_sidebar(self, k):
        """[ACC-ORD-N02] Đăng xuất từ sidebar về trang chủ và xóa token"""
        k.account.logout_from_sidebar()
        k.auth.verify_logged_out()
