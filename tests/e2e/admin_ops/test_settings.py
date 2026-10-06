# ============================================================
# TEST: QUẢN TRỊ - CÀI ĐẶT
# Mục tiêu: các tab + nhãn ô nhập (dữ liệu thật), điền form từ API, lỗi tải, kiểm tra trước khi lưu, lưu (mock PUT)
# Dữ liệu: data/admin-ops/settings.json (settings mock + case + expected)
# API cần quan sát: k.admin_ops.*, k.admin.fill_form / verify_field_value, k.common.mock_write / verify_request
# Kết quả mong đợi: form hiển thị đúng dữ liệu, PUT gửi đủ thay đổi (mock, không ghi DB), toast đúng
# ============================================================
import pytest

from utils.cases import case_params
from utils.data_loader import load_data

D = load_data("admin-ops/settings.json")
API = "**/api/admin/settings"

pytestmark = pytest.mark.role("admin")


class TestSettings:
    """Quản trị - Cài đặt"""

    @pytest.mark.parametrize("case", case_params(D["tabs"]))
    def test_tab_fields(self, k, case):
        """Các tab và ô nhập (data-driven, dữ liệu thật)"""
        k.admin_ops.open_settings()
        k.admin_ops.open_settings_tab(case["tab"])
        k.admin_ops.verify_settings_fields(case["labels"])

    @pytest.mark.parametrize("case", case_params([D["loaded"]]))
    def test_values_loaded(self, k, case):
        """Giá trị từ API được điền vào form"""
        k.admin_ops.mock_settings(D["mock"])
        k.admin_ops.open_settings()
        for label, value in case["fields"].items():
            k.admin.verify_field_value(label, value)
        k.admin_ops.open_settings_tab("Bán hàng")
        k.admin_ops.verify_checkboxes(case["checkboxes"])

    def test_api_error_toast(self, k):
        """[ADO-SET-03] API lỗi -> toast "Không thể tải cấu hình website.\""""
        k.common.mock_get(API, {"success": False}, 500)
        k.admin_ops.open_settings()
        k.common.verify_toast("Không thể tải cấu hình website.")

    @pytest.mark.parametrize("case", case_params(D["validation"]))
    def test_validation_before_save(self, k, case):
        """Kiểm tra dữ liệu trước khi lưu (data-driven)"""
        k.common.mock_write("PUT", API, {"success": True})
        k.admin_ops.mock_settings(D["mock"])
        k.admin_ops.open_settings()
        k.admin.fill_form(case["form"])
        k.admin_ops.save_settings()
        k.common.verify_toast(case["toast"])
        k.common.verify_no_request("PUT", "/admin/settings")

    @pytest.mark.parametrize("case", case_params([D["save"]]))
    def test_save_multiple_tabs(self, k, case):
        """Sửa ở nhiều tab rồi "Lưu cài đặt" gửi PUT đủ thay đổi (mock)"""
        k.common.mock_write("PUT", API, {"success": True})
        k.admin_ops.mock_settings(D["mock"])
        k.admin_ops.open_settings()
        for step in case["steps"]:
            k.admin_ops.open_settings_tab(step["tab"])
            k.admin.fill_form(step["form"])
        k.admin_ops.save_settings()
        k.common.verify_request("PUT", "/admin/settings", case["expectedPayload"])
        k.common.verify_toast(case["toast"])

    @pytest.mark.parametrize("case", case_params([D["serverError"]]))
    def test_save_server_error(self, k, case):
        """Server báo lỗi khi lưu"""
        k.common.mock_write("PUT", API, {"success": False, "message": case["message"]}, case["status"])
        k.admin_ops.mock_settings(D["mock"])
        k.admin_ops.open_settings()
        k.admin_ops.save_settings()
        k.common.verify_toast(case["message"])
