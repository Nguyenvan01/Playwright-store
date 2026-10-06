# ============================================================
# TEST: ADMIN - ĐƠN HÀNG
# Mục tiêu: danh sách, bộ lọc, chi tiết, chuyển trạng thái, thanh toán, hủy đơn, phân trang
# Dữ liệu: data/admin-sales/orders.json
# Production không có đơn hàng nào -> mọi dữ liệu đơn đều mock (GET) qua admin_sales.mock_orders_api,
# mọi thao tác ghi (đổi trạng thái, thanh toán, hủy) đều mock bằng common.mock_write trước khi bấm.
# Kết quả mong đợi: bảng/modal khớp dữ liệu mock; request ghi gửi đúng body; toast đúng
# ============================================================
import pytest

from utils.cases import case_params, known_bug
from utils.data_loader import load_data

DATA = load_data("admin-sales/orders.json")
ALL_NUMBERS = [o["order_number"] for o in DATA["fixture"]["orders"]]

pytestmark = pytest.mark.role("admin")


def test_no_orders(k):
    """[ADS-ORD-01] Không có đơn -> "Không có đơn hàng nào\""""
    k.admin_sales.mock_orders_api({"orders": [], "stats": {}})
    k.admin.open_admin_page("/admin/orders", "Đơn hàng")
    k.admin_sales.verify_orders_empty()


@pytest.fixture
def orders_page(k):
    """Mock dữ liệu đơn hàng rồi mở trang Đơn hàng."""
    k.admin_sales.mock_orders_api(DATA["fixture"])
    k.admin.open_admin_page("/admin/orders", "Đơn hàng")


@pytest.mark.usefixtures("orders_page")
class TestOrdersList:
    """Admin - Đơn hàng: Danh sách & bộ lọc (mock dữ liệu)"""

    @pytest.mark.smoke
    def test_table_columns_cards_rows(self, k):
        """[ADS-ORD-02] Bảng đơn hàng: đủ cột, thẻ trạng thái và dữ liệu dòng"""
        k.admin_sales.verify_columns(DATA["headers"])
        k.admin_sales.verify_order_status_cards(DATA["statusCards"])
        k.admin_sales.verify_order_rows(ALL_NUMBERS)
        k.admin_sales.verify_order_row(DATA["row"])

    @pytest.mark.parametrize("case", case_params(DATA["filters"]))
    def test_filter(self, k, case):
        if case.get("search"):
            k.admin_sales.search_orders(case["search"])
        if case.get("status"):
            k.admin_sales.filter_orders_by_status(case["status"])
        if case.get("payment"):
            k.admin_sales.filter_orders_by_payment(case["payment"])
        if case.get("card"):
            k.admin_sales.click_order_status_card(case["card"])
            k.admin_sales.verify_order_status_card_active(case["card"], True)
        if case.get("dateFrom") and case.get("dateTo"):
            k.admin_sales.filter_orders_by_date(case["dateFrom"], case["dateTo"])
        k.admin_sales.verify_api_requested("/admin/orders", case["request"])
        if case.get("rows"):
            k.admin_sales.verify_order_rows(case["rows"])
        if case.get("selectValue"):
            k.admin_sales.verify_order_filters({"status": case["selectValue"]})

    def test_click_active_card_clears_filter(self, k):
        """[ADS-ORD-03] Bấm lại thẻ trạng thái đang chọn -> bỏ lọc"""
        k.admin_sales.click_order_status_card("Đã giao")
        k.admin_sales.verify_order_rows(["E2E-0005"])
        k.admin_sales.click_order_status_card("Đã giao")
        k.admin_sales.verify_order_status_card_active("Đã giao", False)
        k.admin_sales.verify_order_filters({"status": ""})
        k.admin_sales.verify_order_rows(ALL_NUMBERS)

    def test_clear_filters(self, k):
        """[ADS-ORD-04] "Xóa bộ lọc" đưa mọi bộ lọc về mặc định"""
        k.admin_sales.search_orders("E2E-000")
        k.admin_sales.filter_orders_by_status("pending")
        k.admin_sales.filter_orders_by_payment("unpaid")
        k.admin_sales.verify_order_rows(["E2E-0001", "E2E-0008"])
        k.admin_sales.clear_order_filters()
        k.admin_sales.verify_order_filters({"search": "", "status": "", "payment": ""})
        k.admin_sales.verify_order_rows(ALL_NUMBERS)


@pytest.mark.usefixtures("orders_page")
class TestOrderCancelAction:
    """Admin - Đơn hàng: Nút "Hủy đơn" trên dòng theo trạng thái (data-driven)"""

    @pytest.mark.parametrize("case", case_params(DATA["cancelAction"]))
    def test_cancel_action(self, k, case):
        k.admin_sales.verify_order_cancel_action(case["order"], case["visible"])


@pytest.mark.usefixtures("orders_page")
class TestOrderDetail:
    """Admin - Đơn hàng: Chi tiết đơn hàng"""

    def test_detail_modal(self, k):
        """[ADS-ORD-05] Modal chi tiết hiển thị đủ người nhận, địa chỉ, sản phẩm, tổng tiền, lịch sử"""
        k.admin_sales.open_order_detail(DATA["detail"]["number"])
        k.admin_sales.verify_api_requested(f"/admin/orders/{DATA['fixture']['orders'][2]['id']}")
        k.admin_sales.verify_order_detail(DATA["detail"])
        k.admin_sales.close_order_detail()

    def test_status_api_error(self, k):
        """[ADS-ORD-06] API đổi trạng thái lỗi -> báo lỗi server, giữ trạng thái cũ"""
        msg = 'Không thể chuyển từ trạng thái "pending" sang "confirmed"'
        k.common.mock_write("PUT", "**/api/admin/orders/9001/status", {"success": False, "message": msg}, 400)
        k.admin_sales.open_order_detail("E2E-0001")
        k.admin_sales.click_order_status_button("Xác nhận")
        k.common.verify_request("PUT", "/admin/orders/9001/status", {"status": "confirmed"})
        k.common.verify_toast(msg)
        k.admin_sales.verify_order_detail_status("Chờ xác nhận")
        k.admin_sales.verify_order_row_status("E2E-0001", "Chờ xác nhận")

    def test_update_payment(self, k):
        """[ADS-ORD-07] Cập nhật thanh toán "Đã thanh toán" (mock PUT)"""
        p = DATA["payment"]
        k.common.mock_write(
            "PUT", f"**/api/admin/orders/{p['orderId']}/payment", {"success": True, "payment_status": p["value"]}
        )
        k.admin_sales.open_order_detail(p["order"])
        k.admin_sales.verify_order_detail_payment("Chưa thanh toán", True)
        k.admin_sales.change_order_payment(p["value"])
        k.common.verify_request("PUT", f"/admin/orders/{p['orderId']}/payment", {"payment_status": p["value"]})
        k.common.verify_toast(p["toast"])
        k.admin_sales.verify_order_detail_payment(p["label"], False)

    def test_paid_order_hides_payment_block(self, k):
        """[ADS-ORD-08] Đơn đã thanh toán không hiện khối "Cập nhật thanh toán\""""
        k.admin_sales.open_order_detail("E2E-0002")
        k.admin_sales.verify_order_detail_payment("Đã thanh toán", False)

    def test_confirm_pushes_notification(self, k, page, request):
        """[ADS-ORD-09] Thông báo "Đơn xác nhận" xuất hiện trong chuông sau khi xác nhận đơn"""
        known_bug(
            request,
            "AdminOrders.jsx:160-168 pushNotification() rồi gọi ngay fetchNotifications(true) -> NotificationContext.jsx:55 ghi đè bằng danh sách từ server nên thông báo vừa đẩy biến mất",
        )
        n = DATA["pushNotification"]

        def is_notif_fetch(response):
            return "/api/admin/notifications" in response.url

        k.common.mock_write("PUT", f"**/api/admin/orders/{n['orderId']}/status", {"success": True})
        k.admin_sales.open_order_detail(n["order"])
        # Đợi lần làm mới thông báo do app tự gọi sau khi đổi trạng thái -> kết quả không phụ thuộc thời điểm
        with page.expect_response(is_notif_fetch):
            k.admin_sales.click_order_status_button(n["click"])
            k.common.verify_toast("Đã cập nhật trạng thái: Đã xác nhận")
        k.admin_sales.close_order_detail()
        with page.expect_response(is_notif_fetch):
            k.admin_sales.open_notifications()
        k.admin_sales.verify_notification_visible(n["title"])


@pytest.mark.usefixtures("orders_page")
class TestOrderStatusTransitions:
    """Admin - Đơn hàng: Chuyển trạng thái đơn (data-driven, mock PUT)"""

    @pytest.mark.parametrize("case", case_params(DATA["transitions"]))
    def test_transition(self, k, case):
        status_path = f"/admin/orders/{case['orderId']}/status"
        k.common.mock_write("PUT", f"**/api{status_path}", {"success": True, "status": case.get("status")})
        k.admin_sales.open_order_detail(case["order"])
        k.admin_sales.verify_order_status_buttons(case["buttons"])
        k.admin_sales.verify_order_processing_warning(bool(case.get("warning")))
        if not case.get("click"):
            k.common.verify_no_request("PUT", status_path)
            return
        k.admin_sales.click_order_status_button(case["click"])
        k.common.verify_request("PUT", status_path, {"status": case["status"]})
        k.common.verify_toast(f"Đã cập nhật trạng thái: {case['label']}")
        k.admin_sales.verify_order_detail_status(case["label"])
        k.admin_sales.verify_order_row_status(case["order"], case["label"])


@pytest.mark.usefixtures("orders_page")
class TestOrderCancel:
    """Admin - Đơn hàng: Hủy đơn từ bảng (mock POST /cancel)"""

    @pytest.mark.smoke
    def test_cancel_paid_order(self, k):
        """[ADS-ORD-10] Hủy đơn đã thanh toán có lý do -> gửi lý do, báo hoàn tiền, đơn thành "Đã hủy\""""
        c = DATA["cancel"]
        k.common.mock_write("POST", f"**/api/admin/orders/{c['orderId']}/cancel", {"success": True})
        k.admin_sales.open_cancel_order(c["order"])
        k.admin_sales.verify_cancel_notes([c["refundNote"]])
        k.admin_sales.fill_cancel_reason(c["reason"])
        k.admin.click_button("Xác nhận hủy")
        k.common.verify_request("POST", f"/admin/orders/{c['orderId']}/cancel", {"reason": c["reason"]})
        k.common.verify_toast(c["toast"])
        k.admin.verify_modal_closed("Hủy đơn hàng")
        k.admin_sales.verify_order_row_status(c["order"], "Đã hủy")
        k.admin_sales.verify_order_cancel_action(c["order"], False)

    def test_close_cancel_modal(self, k):
        """[ADS-ORD-11] "Đóng" modal hủy -> không gửi request, đơn giữ nguyên"""
        c = DATA["cancel"]
        k.common.mock_write("POST", f"**/api/admin/orders/{c['orderId']}/cancel", {"success": True})
        k.admin_sales.open_cancel_order(c["order"])
        k.admin_sales.fill_cancel_reason(c["reason"])
        k.admin.click_button("Đóng")
        k.admin.verify_modal_closed("Hủy đơn hàng")
        k.common.verify_no_request("POST", f"/admin/orders/{c['orderId']}/cancel")
        k.admin_sales.verify_order_row_status(c["order"], "Đã xác nhận")

    def test_cancel_rejected(self, k):
        """[ADS-ORD-12] Server từ chối hủy -> báo lỗi, modal vẫn mở"""
        c = DATA["cancel"]
        k.common.mock_write(
            "POST",
            f"**/api/admin/orders/{c['orderId']}/cancel",
            {"success": False, "message": c["error"]["message"]},
            c["error"]["status"],
        )
        k.admin_sales.open_cancel_order(c["order"])
        k.admin.click_button("Xác nhận hủy")
        k.common.verify_request("POST", f"/admin/orders/{c['orderId']}/cancel", {"reason": ""})
        k.common.verify_toast(c["error"]["message"])
        k.admin.verify_modal_open("Hủy đơn hàng")
        k.admin_sales.verify_order_row_status(c["order"], "Đã xác nhận")

    def test_cancel_points_order(self, k, request):
        """[ADS-ORD-13] Đơn dùng điểm -> modal hủy báo hoàn điểm tích lũy"""
        known_bug(
            request,
            "AdminOrders.jsx:700 kiểm tra order.points_used nhưng API danh sách (adminController.getOrders) chỉ trả points_discount -> không bao giờ báo hoàn điểm",
        )
        k.admin_sales.open_cancel_order(DATA["cancel"]["pointsOrder"])
        k.admin_sales.verify_cancel_notes([DATA["cancel"]["pointsNote"]])


class TestOrdersPagination:
    """Admin - Đơn hàng: Phân trang"""

    def test_pagination_text(self, k):
        """[ADS-ORD-14] Nhiều trang -> hiển thị "Trang 1 / 3 — 45 đơn hàng\""""
        k.admin_sales.mock_orders_api({**DATA["fixture"], "total": DATA["pagination"]["total"]})
        k.admin.open_admin_page("/admin/orders", "Đơn hàng")
        k.admin_sales.verify_pagination_text(DATA["pagination"]["text"])
        k.admin_sales.verify_page_button(3)

    def test_go_to_page_2(self, k, request):
        """[ADS-ORD-15] Bấm trang 2 tải dữ liệu trang 2"""
        known_bug(
            request,
            "AdminOrders.jsx:125-130 useEffect tải đơn chỉ phụ thuộc [filters], đổi trang không gọi lại API",
        )
        k.admin_sales.mock_orders_api({**DATA["fixture"], "total": DATA["pagination"]["total"]})
        k.admin.open_admin_page("/admin/orders", "Đơn hàng")
        k.admin_sales.verify_pagination_text(DATA["pagination"]["text"])
        k.admin_sales.go_to_page(DATA["pagination"]["page"])
        k.admin_sales.verify_api_requested("/admin/orders", {"page": DATA["pagination"]["page"]})
