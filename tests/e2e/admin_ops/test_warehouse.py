# ============================================================
# TEST: QUẢN TRỊ - KHO HÀNG
# Mục tiêu: dữ liệu thật (thẻ, cột, dòng), thẻ thống kê từ API giả lập, hiển thị dòng, tab lọc, tìm kiếm, số đếm tab
# Dữ liệu: data/admin-ops/warehouse.json (warehouse mock + case + expected)
# API cần quan sát: k.admin_ops.*, k.admin.search_list, k.common.verify_text_visible
# Kết quả mong đợi: bảng/thẻ đúng số liệu, request GET gửi đúng filter, số đếm tab đúng
# ============================================================
import pytest

from utils.cases import case_params
from utils.data_loader import load_data

D = load_data("admin-ops/warehouse.json")
SEARCH = "Tìm kiếm sản phẩm, SKU, danh mục..."

pytestmark = pytest.mark.role("admin")


class TestWarehouse:
    """Quản trị - Kho hàng"""

    @pytest.mark.smoke
    def test_real_data(self, k):
        """[ADO-WH-01] Dữ liệu thật: thẻ thống kê, đủ cột, có sản phẩm"""
        k.admin_ops.open_warehouse()
        for label in D["statLabels"]:
            k.common.verify_text_visible(label)
        k.admin_ops.verify_columns(D["headers"])
        k.admin_ops.verify_rows_at_least(1)
        k.common.verify_no_page_errors()

    @pytest.mark.parametrize("case", case_params([D["realStats"]]))
    def test_real_stats_match_list(self, k, case):
        """Dữ liệu thật: thẻ "Tổng sản phẩm" bằng số sản phẩm trong bảng"""
        k.admin_ops.open_warehouse()
        k.admin_ops.verify_warehouse_stats_match_list()

    def test_stat_cards_from_api(self, k):
        """[ADO-WH-02] Thẻ thống kê hiển thị đúng số liệu API"""
        k.admin_ops.mock_warehouse(D["mock"])
        k.admin_ops.open_warehouse()
        k.admin_ops.verify_stat_cards(D["statCards"])
        k.admin_ops.verify_list_query("/admin/warehouse", {"filter": "all"})
        k.admin_ops.verify_row_count(len(D["mock"]["products"]))

    @pytest.mark.parametrize("case", case_params(D["rows"]))
    def test_row_display(self, k, case):
        """Hiển thị dòng (data-driven)"""
        k.admin_ops.mock_warehouse(D["mock"])
        k.admin_ops.open_warehouse()
        k.admin_ops.verify_row_cells(case["rowText"], case["expected"])

    @pytest.mark.parametrize("case", case_params(D["tabs"]))
    def test_filter_tab(self, k, case):
        """Tab lọc tồn kho (data-driven)"""
        k.admin_ops.mock_warehouse(D["mock"])
        k.admin_ops.open_warehouse()
        if case["tab"] == "Tất cả":
            k.admin_ops.select_warehouse_tab("Hết hàng")
        k.admin_ops.select_warehouse_tab(case["tab"])
        k.admin_ops.verify_list_query("/admin/warehouse", {"filter": case["filter"]})
        k.admin_ops.verify_row_count(len(case["visible"]))
        k.admin_ops.verify_visible_rows(case["visible"], case["hidden"])

    @pytest.mark.parametrize("case", case_params(D["search"]))
    def test_search(self, k, case):
        """Tìm kiếm (data-driven)"""
        k.admin_ops.mock_warehouse(D["mock"])
        k.admin_ops.open_warehouse()
        k.admin.search_list(SEARCH, case["keyword"])
        k.admin_ops.verify_visible_rows(case["visible"], case["hidden"])
        if case.get("emptyText"):
            k.common.verify_text_visible(case["emptyText"])

    @pytest.mark.parametrize("case", case_params(D["tabBadges"]))
    def test_tab_badges(self, k, case):
        """Số đếm trên tab (data-driven)"""
        k.admin_ops.mock_warehouse(D["mock"])
        k.admin_ops.open_warehouse()
        k.admin_ops.select_warehouse_tab(case["tab"])
        for tab, count in case["badges"].items():
            k.admin_ops.verify_warehouse_tab_badge(tab, count)
