# ============================================================
# TEST: QUẢN TRỊ - MÃ GIẢM GIÁ
# Mục tiêu: danh sách (thật + mock), định dạng cột, trường bắt buộc, thêm/sửa/xóa, bật/tắt (mock ghi)
# Dữ liệu: data/admin-marketing/coupons.json
# Kết quả mong đợi: bảng/form khớp dữ liệu; request ghi gửi đúng payload; toast đúng
# ============================================================
import pytest

from utils.cases import case_params
from utils.data_loader import load_data

DATA = load_data("admin-marketing/coupons.json")
LIST_API = "**/api/admin/coupons"
CREATE = "Thêm mã giảm giá"
EDIT = "Sửa mã giảm giá"

pytestmark = pytest.mark.role("admin")


def _open_mocked_list(k):
    k.admin_marketing.mock_coupon_list(DATA["list"])
    k.admin_marketing.open_coupons()


class TestCoupons:
    """Quản trị - Mã giảm giá"""

    @pytest.mark.smoke
    def test_real_data(self, k):
        """[ADM-CPN-01] Dữ liệu thật: đủ cột và có ít nhất 1 mã"""
        k.admin_marketing.open_coupons()
        k.admin_marketing.verify_columns(DATA["headers"])
        k.admin_marketing.verify_rows_at_least(1)
        k.common.verify_no_page_errors()

    def test_empty_list(self, k):
        """[ADM-CPN-02] Danh sách rỗng hiển thị "Chưa có mã giảm giá nào\""""
        k.admin_marketing.mock_coupon_list([])
        k.admin_marketing.open_coupons()
        k.common.verify_text_visible("Chưa có mã giảm giá nào")

    def test_code_uppercase(self, k):
        """[ADM-CPN-03] Mã tự viết hoa khi nhập"""
        _open_mocked_list(k)
        k.admin_marketing.open_create_coupon()
        k.admin.fill_form({"Mã": DATA["create"]["typedCode"]})
        k.admin.verify_field_value("Mã", DATA["create"]["expectedCode"])

    @pytest.mark.smoke
    def test_create_success(self, k):
        """[ADM-CPN-04] Thêm mã thành công gửi đúng dữ liệu và thêm dòng mới (mock POST)"""
        create = DATA["create"]
        created = {
            "id": 99,
            "code": create["expectedCode"],
            "name": "Giảm 10% E2E",
            "discount_type": "percentage",
            "discount_value": 10,
            "used_count": 0,
            "max_usage_total": 100,
            "is_active": True,
            "is_public": True,
        }
        k.common.mock_write("POST", LIST_API, {"success": True, "coupon": created})
        _open_mocked_list(k)
        k.admin_marketing.open_create_coupon()
        k.admin.fill_form({"Mã": create["typedCode"], **create["form"]})
        k.admin_marketing.click_modal_button(CREATE, "Tạo mới")
        k.common.verify_request("POST", "/admin/coupons", create["expectedPayload"])
        k.common.verify_toast(create["toast"])
        k.admin.verify_modal_closed(CREATE)
        k.admin_marketing.verify_row_cells(
            create["expectedCode"], {"Tên": "Giảm 10% E2E", "Giảm": "10%", "Sử dụng": "0 / 100"}
        )

    @pytest.mark.parametrize("case", case_params([DATA["saveError"]]))
    def test_save_error(self, k, case):
        k.common.mock_write("POST", LIST_API, {"success": False, "message": case["message"]}, case["status"])
        _open_mocked_list(k)
        k.admin_marketing.open_create_coupon()
        k.admin.fill_form(case["form"])
        k.admin_marketing.click_modal_button(CREATE, "Tạo mới")
        k.common.verify_request("POST", "/admin/coupons")
        k.common.verify_toast(case["message"])

    def test_edit(self, k):
        """[ADM-CPN-05] Sửa: form điền sẵn, gửi PUT đúng và cập nhật dòng (mock)"""
        edit = DATA["edit"]
        updated = {**DATA["list"][0], "name": "Flash Sale 20%", "discount_value": 20}
        k.common.mock_write("PUT", f"{LIST_API}/*", {"success": True, "coupon": updated})
        _open_mocked_list(k)
        k.admin_marketing.click_coupon_edit(edit["code"])
        for label, value in edit["prefilled"].items():
            k.admin.verify_field_value(label, value)
        k.admin.fill_form(edit["form"])
        k.admin_marketing.click_modal_button(EDIT, "Cập nhật")
        k.common.verify_request("PUT", "/admin/coupons/1", edit["expectedPayload"])
        k.common.verify_toast(edit["toast"])
        k.admin_marketing.verify_row_cells(edit["code"], {"Tên": "Flash Sale 20%", "Giảm": "20%"})

    @pytest.mark.parametrize("case", case_params([DATA["editDates"]]))
    def test_edit_dates_prefilled(self, k, case):
        _open_mocked_list(k)
        k.admin_marketing.click_coupon_edit(case["code"])
        for label, value in case["prefilled"].items():
            k.admin.verify_field_value(label, value)

    @pytest.mark.parametrize("case", case_params([DATA["typeLabel"]]))
    def test_type_label(self, k, case):
        _open_mocked_list(k)
        k.admin_marketing.open_create_coupon()
        k.admin.fill_form({case["field"]: case["value"]})
        k.admin_marketing.verify_selected_option(case["field"], case["tableLabel"])

    def test_delete_cancel(self, k):
        """[ADM-CPN-06] Xóa: bấm "Hủy" không gửi DELETE"""
        remove = DATA["remove"]
        k.common.mock_write("DELETE", f"{LIST_API}/*", {"success": True})
        _open_mocked_list(k)
        k.admin_marketing.click_coupon_delete(remove["code"])
        k.admin_marketing.verify_modal_text(
            "Xác nhận xóa", [remove["confirmText"], "Hành động này không thể hoàn tác"]
        )
        k.admin_marketing.click_modal_button("Xác nhận xóa", "Hủy")
        k.admin.verify_modal_closed("Xác nhận xóa")
        k.common.verify_no_request("DELETE", "/admin/coupons")
        k.admin.verify_row(remove["code"])

    def test_delete_confirm(self, k):
        """[ADM-CPN-07] Xóa: xác nhận gửi DELETE đúng id và bỏ dòng (mock)"""
        remove = DATA["remove"]
        k.common.mock_write("DELETE", f"{LIST_API}/*", {"success": True})
        _open_mocked_list(k)
        k.admin_marketing.click_coupon_delete(remove["code"])
        k.admin_marketing.click_modal_button("Xác nhận xóa", "Xóa")
        k.common.verify_request("DELETE", "/admin/coupons/1")
        k.common.verify_toast(remove["toast"])
        k.admin.verify_row(remove["code"], False)


class TestCouponRealDataFormat:
    """Quản trị - Mã giảm giá: Dữ liệu thật - định dạng cột"""

    @pytest.mark.parametrize("case", case_params(DATA["realDataChecks"]))
    def test_cell_format(self, k, case):
        k.admin_marketing.open_coupons()
        k.admin_marketing.verify_cell_pattern(0, case["column"], case["pattern"])


class TestCouponDisplay:
    """Quản trị - Mã giảm giá: Hiển thị dòng (data-driven)"""

    @pytest.mark.parametrize("case", case_params(DATA["display"]))
    def test_row_display(self, k, case):
        _open_mocked_list(k)
        k.admin_marketing.verify_row_count(len(DATA["list"]))
        k.admin_marketing.verify_row_cells(case["code"], case["expected"])


class TestCouponRequired:
    """Quản trị - Mã giảm giá: Trường bắt buộc (data-driven)"""

    @pytest.mark.parametrize("case", case_params(DATA["required"]))
    def test_required(self, k, case):
        k.common.mock_write("POST", LIST_API, {"success": True})
        _open_mocked_list(k)
        k.admin_marketing.open_create_coupon()
        k.admin.fill_form(case["form"])
        k.admin_marketing.click_modal_button(CREATE, "Tạo mới")
        k.admin.verify_modal_open(CREATE)
        k.common.verify_no_request("POST", "/admin/coupons")


class TestCouponToggles:
    """Quản trị - Mã giảm giá: Bật/tắt Công khai - Trạng thái (data-driven)"""

    @pytest.mark.parametrize("case", case_params(DATA["toggles"]))
    def test_toggle(self, k, case):
        k.common.mock_write("PUT", f"{LIST_API}/*", {"success": True})
        _open_mocked_list(k)
        k.admin_marketing.verify_coupon_toggle(case["code"], case["column"], case["from"])
        k.admin_marketing.toggle_coupon(case["code"], case["column"])
        k.common.verify_request("PUT", "/admin/coupons/", {case["field"]: not case["from"]})
        k.common.verify_toast(case["toast"])
        k.admin_marketing.verify_coupon_toggle(case["code"], case["column"], not case["from"])
