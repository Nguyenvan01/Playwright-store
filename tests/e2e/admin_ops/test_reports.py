# ============================================================
# TEST: QUẢN TRỊ - BÁO CÁO
# Mục tiêu: dữ liệu thật (thẻ + khối), số liệu từ API giả lập, trạng thái rỗng/lỗi, chọn kỳ, khoảng ngày, xuất CSV
# Dữ liệu: data/admin-ops/reports.json (overview mock + case + expected)
# API cần quan sát: k.admin_ops.*, k.common.verify_text_visible / mock_get / verify_toast
# Kết quả mong đợi: thẻ/khối hiển thị đúng số liệu, request overview đúng tham số, file CSV đúng tên + BOM + nội dung
# ============================================================
import pytest

from utils.cases import case_params
from utils.data_loader import load_data

D = load_data("admin-ops/reports.json")
OVERVIEW = "/admin/reports/overview"

pytestmark = pytest.mark.role("admin")


class TestReports:
    """Quản trị - Báo cáo"""

    @pytest.mark.smoke
    def test_real_data(self, k):
        """[ADO-RPT-01] Dữ liệu thật: đủ thẻ tổng quan và các khối báo cáo"""
        k.admin_ops.open_reports()
        for text in [*D["cardLabels"], *D["sectionHeadings"]]:
            k.common.verify_text_visible(text)
        k.common.verify_no_page_errors()

    def test_overview_cards(self, k):
        """[ADO-RPT-02] Thẻ tổng quan, cảnh báo, biểu đồ trạng thái hiển thị đúng số liệu API"""
        k.admin_ops.mock_reports_overview(D["overview"])
        k.admin_ops.open_reports()
        k.admin_ops.verify_stat_cards(D["summaryCards"])
        k.common.verify_text_visible("+12.5% so với kỳ trước")
        k.admin_ops.verify_report_section_text("Trạng thái đơn hàng", D["statusLegend"])

    def test_top_tables(self, k):
        """[ADO-RPT-03] Bảng "Sản phẩm bán chạy" và "Khách hàng mua nhiều\""""
        k.admin_ops.mock_reports_overview(D["overview"])
        k.admin_ops.open_reports()
        for section in D["sections"]:
            k.admin_ops.verify_report_section(section["heading"], section["rows"], section["firstRow"])
        k.admin_ops.verify_report_section_text("Sản phẩm bán chạy", ["Chưa phân loại"])

    def test_empty_data(self, k):
        """[ADO-RPT-04] Không có dữ liệu: thẻ = 0 và các khối báo trống"""
        k.admin_ops.mock_reports_overview(D["emptyOverview"])
        k.admin_ops.open_reports()
        k.admin_ops.verify_stat_cards(D["emptyCards"])
        for heading, text in D["emptyTexts"].items():
            k.admin_ops.verify_report_section_text(heading, [text])

    def test_api_error_toast(self, k):
        """[ADO-RPT-05] API lỗi -> toast "Không thể tải dữ liệu báo cáo.\""""
        k.common.mock_get("**/api/admin/reports/overview*", {"success": False}, 500)
        k.admin_ops.open_reports()
        k.common.verify_toast("Không thể tải dữ liệu báo cáo.")

    @pytest.mark.parametrize("case", case_params(D["periods"]))
    def test_select_period(self, k, case):
        """Chọn kỳ báo cáo (data-driven)"""
        k.admin_ops.mock_reports_overview(D["overview"])
        k.admin_ops.open_reports()
        if case["value"]:
            k.admin_ops.select_report_period(case["value"])
        k.admin_ops.verify_list_query(
            OVERVIEW, {"period": case["apiPeriod"], "start_date": None, "end_date": None}
        )
        k.admin_ops.verify_report_section_text("Doanh thu theo thời gian", [case["label"]])

    @pytest.mark.parametrize("case", case_params([D["custom"]]))
    def test_custom_range(self, k, case):
        """Kỳ "Tùy chọn" + "Lọc" gửi khoảng ngày"""
        k.admin_ops.mock_reports_overview(D["overview"])
        k.admin_ops.open_reports()
        k.admin_ops.select_report_period("custom")
        k.admin_ops.apply_custom_range(case["start"], case["end"])
        k.admin_ops.verify_list_query(
            OVERVIEW, {"period": "custom", "start_date": case["start"], "end_date": case["end"]}
        )

    @pytest.mark.parametrize("case", case_params([D["customDefaults"]]))
    def test_custom_range_defaults(self, k, case):
        """Khoảng ngày mặc định của kỳ "Tùy chọn\""""
        k.admin_ops.mock_reports_overview(D["overview"])
        k.admin_ops.open_reports()
        k.admin_ops.select_report_period("custom")
        k.admin_ops.verify_custom_range_defaults()

    @pytest.mark.parametrize("case", case_params(D["exports"]))
    def test_export_csv(self, k, case):
        """Xuất báo cáo CSV (data-driven)"""
        k.admin_ops.mock_reports_overview(D["overview"])
        k.admin_ops.open_reports()
        if case["value"]:
            k.admin_ops.select_report_period(case["value"])
        if case.get("range"):
            k.admin_ops.apply_custom_range(case["range"]["start"], case["range"]["end"])
        k.admin_ops.export_report(case["filePattern"], case["lines"])
