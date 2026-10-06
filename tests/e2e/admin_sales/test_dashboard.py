# ============================================================
# TEST: ADMIN - TỔNG QUAN (DASHBOARD)
# Mục tiêu: thẻ thống kê, các khối, biểu đồ, link điều hướng; dữ liệu thật và mock GET /admin/dashboard
# Dữ liệu: data/admin-sales/dashboard.json
# Kết quả mong đợi: số liệu hiển thị khớp dữ liệu mock; API lỗi -> hiển thị 0, không crash
# ============================================================
import pytest

from utils.cases import case_params, known_bug
from utils.data_loader import load_data

DATA = load_data("admin-sales/dashboard.json")
DASHBOARD_API = "**/api/admin/dashboard"

pytestmark = pytest.mark.role("admin")


class TestDashboard:
    """Admin - Tổng quan (dashboard)"""

    @pytest.mark.smoke
    def test_real_dashboard(self, k):
        """[ADS-DASH-01] Dashboard dữ liệu thật: đủ thẻ thống kê và các khối"""
        k.admin.open_admin_page("/admin", "Tổng quan")
        k.admin_sales.verify_api_requested("/admin/dashboard")
        k.admin_sales.verify_stat_card_labels(DATA["cardLabels"])
        k.admin_sales.verify_dashboard_sections(DATA["sections"])
        k.common.verify_no_page_errors()

    def test_api_error_shows_zero(self, k):
        """[ADS-DASH-08] API dashboard lỗi -> hiển thị 0, không crash"""
        k.common.mock_get(
            DASHBOARD_API, {"success": False, "message": "Có lỗi xảy ra, vui lòng thử lại sau."}, 500
        )
        k.admin.open_admin_page("/admin", "Tổng quan")
        k.admin_sales.verify_stat_cards(DATA["zeroCards"])
        k.admin_sales.verify_recent_orders([])


class TestDashboardMocked:
    """Admin - Tổng quan: Hiển thị số liệu (mock GET /admin/dashboard)"""

    @pytest.fixture(autouse=True)
    def mocked_dashboard(self, k):
        k.common.mock_get(DASHBOARD_API, DATA["response"])
        k.admin.open_admin_page("/admin", "Tổng quan")

    def test_stat_cards(self, k):
        """[ADS-DASH-02] Thẻ thống kê hiển thị đúng giá trị, dòng phụ và % doanh thu"""
        k.admin_sales.verify_stat_cards(DATA["expected"]["cards"])

    def test_status_breakdown(self, k):
        """[ADS-DASH-03] Khối "Đơn hàng theo trạng thái" đúng số lượng"""
        k.admin_sales.verify_order_status_breakdown(DATA["expected"]["statusBreakdown"])

    def test_recent_orders_and_top_products(self, k):
        """[ADS-DASH-04] "Đơn hàng gần đây" và "Sản phẩm bán chạy\""""
        k.admin_sales.verify_recent_orders(DATA["expected"]["recentOrders"])
        k.admin_sales.verify_top_products(DATA["expected"]["topProducts"])

    def test_quick_cards(self, k):
        """[ADS-DASH-05] Thẻ thao tác nhanh hiển thị đúng số liệu"""
        k.admin_sales.verify_quick_cards(DATA["expected"]["quickCards"])

    def test_chart(self, k):
        """[ADS-DASH-06] Biểu đồ vẽ vùng doanh thu + đường đơn hàng theo dữ liệu tháng"""
        k.admin_sales.verify_chart_ticks(DATA["expected"]["chartTicks"])
        k.admin_sales.verify_chart_series(len(DATA["expected"]["chartTicks"]))

    def test_change_chart_range(self, k, request):
        """[ADS-DASH-07] Đổi khoảng thời gian biểu đồ thì tải lại số liệu"""
        known_bug(
            request,
            'AdminDashboard.jsx:227-232 - ô chọn "7 ngày qua/30 ngày qua/..." không có onChange, không gọi lại API',
        )
        k.admin_sales.verify_api_requested("/admin/dashboard")
        k.admin_sales.select_revenue_range(DATA["rangeOption"])
        k.admin_sales.verify_api_requested("/admin/dashboard", {"range": DATA["rangeOption"]})

    @pytest.mark.parametrize("case", case_params(DATA["fakeGrowth"]))
    def test_fake_growth(self, k, case):
        k.admin_sales.verify_stat_card_has_no_change(case["card"])


class TestDashboardLinks:
    """Admin - Tổng quan: Link điều hướng (data-driven)"""

    @pytest.mark.parametrize("case", case_params(DATA["links"]))
    def test_dashboard_link(self, k, case):
        k.common.mock_get(DASHBOARD_API, DATA["response"])
        k.admin.open_admin_page("/admin", "Tổng quan")
        k.admin_sales.click_dashboard_link(case["label"], case.get("section"))
        k.common.verify_url(case["path"])
        k.admin.verify_header_title(case["pageTitle"])

    def test_process_orders_link_filters_pending(self, k, request):
        """[ADS-DASH-L06] "Xử lý đơn hàng" mở trang Đơn hàng đã lọc "Chờ xác nhận\""""
        known_bug(
            request,
            "AdminDashboard.jsx:384 link tới /admin/orders?status=pending nhưng AdminOrders.jsx:80-83 không đọc query string -> không lọc",
        )
        k.common.mock_get(DASHBOARD_API, DATA["response"])
        k.admin.open_admin_page("/admin", "Tổng quan")
        k.admin_sales.click_dashboard_link("Xử lý đơn hàng")
        k.admin.verify_header_title("Đơn hàng")
        k.admin_sales.verify_order_filters({"status": "pending"})
        k.admin_sales.verify_api_requested("/admin/orders", {"status": "pending"})
