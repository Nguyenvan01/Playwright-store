# ============================================================
# TEST: QUẢN TRỊ - KHUYẾN MÃI
# Mục tiêu: danh sách (thật + mock), trạng thái theo ngày, tìm kiếm, validate form, slug tự sinh,
#           thêm/sửa/xem/xóa (mock ghi)
# Dữ liệu: data/admin-marketing/promotions.json (startOffset/endOffset -> ngày so với hôm nay)
# Kết quả mong đợi: bảng/form khớp dữ liệu; request ghi gửi đúng payload; toast đúng
# ============================================================
import pytest

from utils.cases import case_params
from utils.data_loader import load_data

DATA = load_data("admin-marketing/promotions.json")
SEARCH = "Tìm theo tên, mô tả hoặc trạng thái"
LIST_API = "**/api/admin/promotions"
CREATE = "Thêm khuyến mãi"
EDIT = "Sửa khuyến mãi"

pytestmark = pytest.mark.role("admin")


def _open_mocked_list(k):
    k.admin_marketing.mock_promotion_list(DATA["list"])
    k.admin_marketing.open_promotions()


class TestPromotions:
    """Quản trị - Khuyến mãi"""

    @pytest.mark.smoke
    def test_real_data(self, k):
        """[ADM-PRO-01] Dữ liệu thật: đủ cột và có ít nhất 1 khuyến mãi"""
        k.admin_marketing.open_promotions()
        k.admin_marketing.verify_columns(DATA["headers"])
        k.admin_marketing.verify_rows_at_least(1)
        k.common.verify_no_page_errors()

    def test_empty_list(self, k):
        """[ADM-PRO-02] Danh sách rỗng hiển thị "Chưa có khuyến mãi nào\""""
        k.admin_marketing.mock_promotion_list([])
        k.admin_marketing.open_promotions()
        k.common.verify_text_visible("Chưa có khuyến mãi nào")

    def test_api_error(self, k):
        """[ADM-PRO-03] API lỗi hiển thị "Không thể tải danh sách khuyến mãi.\""""
        k.common.mock_get(LIST_API, {"success": False, "message": "Lỗi"}, 500)
        k.admin_marketing.open_promotions()
        k.common.verify_text_visible("Không thể tải danh sách khuyến mãi.")

    @pytest.mark.smoke
    def test_create_success(self, k):
        """[ADM-PRO-04] Thêm khuyến mãi thành công gửi đúng dữ liệu (mock POST)"""
        create = DATA["create"]
        k.common.mock_write("POST", LIST_API, {"success": True, "promotion": {"id": 99, **create["expectedPayload"]}})
        _open_mocked_list(k)
        k.admin_marketing.open_create_promotion()
        k.admin.fill_form(create["form"])
        k.admin_marketing.click_modal_button(CREATE, "Tạo mới")
        k.common.verify_request("POST", "/admin/promotions", create["expectedPayload"])
        k.common.verify_toast(create["toast"])
        k.admin.verify_modal_closed(CREATE)

    @pytest.mark.parametrize("case", case_params([DATA["saveError"]]))
    def test_save_error(self, k, case):
        k.common.mock_write("POST", LIST_API, {"success": False, "message": case["message"]}, case["status"])
        _open_mocked_list(k)
        k.admin_marketing.open_create_promotion()
        k.admin.fill_form(case["form"])
        k.admin_marketing.click_modal_button(CREATE, "Tạo mới")
        k.common.verify_request("POST", "/admin/promotions")
        k.common.verify_toast(case["message"])

    def test_edit(self, k):
        """[ADM-PRO-05] Sửa: form điền sẵn dữ liệu và gửi PUT đúng (mock)"""
        edit = DATA["edit"]
        k.common.mock_write("PUT", f"{LIST_API}/*", {"success": True})
        _open_mocked_list(k)
        k.admin.click_row_action(edit["title"], "Sửa")
        k.admin.verify_modal_open(EDIT)
        for label, value in edit["prefilled"].items():
            k.admin.verify_field_value(label, value)
        k.admin.fill_form(edit["form"])
        k.admin_marketing.click_modal_button(EDIT, "Cập nhật")
        k.common.verify_request("PUT", "/admin/promotions/3", edit["expectedPayload"])
        k.common.verify_toast(edit["toast"])
        k.admin.verify_modal_closed(EDIT)

    def test_view_then_edit(self, k):
        """[ADM-PRO-06] Xem chi tiết rồi bấm "Sửa" mở form sửa"""
        view = DATA["view"]
        _open_mocked_list(k)
        k.admin.click_row_action(view["title"], "Xem")
        k.admin_marketing.verify_modal_text(view["title"], view["texts"])
        k.admin_marketing.click_modal_button(view["title"], "Sửa")
        k.admin.verify_modal_open(EDIT)
        k.admin.verify_field_value("Tên khuyến mãi", view["title"])

    def test_delete_cancel(self, k):
        """[ADM-PRO-07] Xóa: bấm "Hủy" đóng hộp xác nhận, không gửi DELETE"""
        remove = DATA["remove"]
        k.common.mock_write("DELETE", f"{LIST_API}/*", {"success": True})
        _open_mocked_list(k)
        k.admin.click_row_action(remove["title"], "Xóa")
        k.admin_marketing.verify_modal_text(
            "Xác nhận xóa", [remove["title"], "Bạn có chắc chắn muốn xóa khuyến mãi này không?"]
        )
        k.admin_marketing.click_modal_button("Xác nhận xóa", "Hủy")
        k.admin.verify_modal_closed("Xác nhận xóa")
        k.common.verify_no_request("DELETE", "/admin/promotions")

    def test_delete_confirm(self, k):
        """[ADM-PRO-08] Xóa: xác nhận gửi DELETE đúng id và báo thành công (mock)"""
        remove = DATA["remove"]
        k.common.mock_write("DELETE", f"{LIST_API}/*", {"success": True})
        _open_mocked_list(k)
        k.admin.click_row_action(remove["title"], "Xóa")
        k.admin_marketing.click_modal_button("Xác nhận xóa", "Xóa")
        k.common.verify_request("DELETE", "/admin/promotions/2")
        k.common.verify_toast(remove["toast"])

    def test_close_form_resets(self, k):
        """[ADM-PRO-09] Đóng form bằng nút "Đóng" rồi mở lại -> form trống"""
        _open_mocked_list(k)
        k.admin_marketing.open_create_promotion()
        k.admin.fill_form({"Tên khuyến mãi": "Nháp sẽ bị bỏ"})
        k.admin_marketing.click_modal_button(CREATE, "Đóng")
        k.admin.verify_modal_closed(CREATE)
        k.admin_marketing.open_create_promotion()
        k.admin.verify_field_value("Tên khuyến mãi", "")
        k.admin.verify_field_value("Slug", "")


class TestPromotionStatus:
    """Quản trị - Khuyến mãi: Trạng thái tính theo ngày (data-driven)"""

    @pytest.mark.parametrize("case", case_params(DATA["statusCases"]))
    def test_status_by_date(self, k, case):
        k.admin_marketing.mock_promotion_list([case["promotion"]])
        k.admin_marketing.open_promotions()
        k.admin_marketing.verify_row_cells(case["promotion"]["title"], case["expected"])


class TestPromotionSearch:
    """Quản trị - Khuyến mãi: Tìm kiếm (data-driven)"""

    @pytest.mark.parametrize("case", case_params(DATA["search"]))
    def test_search(self, k, case):
        _open_mocked_list(k)
        k.admin.search_list(SEARCH, case["keyword"])
        k.admin_marketing.verify_visible_rows(case["visible"], case["hidden"])
        if case.get("emptyText"):
            k.common.verify_text_visible(case["emptyText"])


class TestPromotionValidation:
    """Quản trị - Khuyến mãi: Form thêm - kiểm tra dữ liệu (data-driven)"""

    @pytest.mark.parametrize("case", case_params(DATA["validation"]))
    def test_validation(self, k, case):
        k.common.mock_write("POST", LIST_API, {"success": True})
        _open_mocked_list(k)
        k.admin_marketing.open_create_promotion()
        k.admin.fill_form(case["form"])
        k.admin_marketing.click_modal_button(CREATE, "Tạo mới")
        k.common.verify_toast(case["toast"])
        k.admin.verify_modal_open(CREATE)
        k.common.verify_no_request("POST", "/admin/promotions")

    @pytest.mark.parametrize("case", case_params([DATA["invalidImage"]]))
    def test_invalid_image(self, k, case):
        k.common.mock_write("POST", LIST_API, {"success": True})
        _open_mocked_list(k)
        k.admin_marketing.open_create_promotion()
        k.admin.fill_form(case["form"])
        k.admin_marketing.click_modal_button(CREATE, "Tạo mới")
        k.admin.verify_modal_open(CREATE)
        k.common.verify_no_request("POST", "/admin/promotions")


class TestPromotionSlug:
    """Quản trị - Khuyến mãi: Slug tự sinh (data-driven)"""

    @pytest.mark.parametrize("case", case_params(DATA["slugCases"]))
    def test_slug(self, k, case):
        _open_mocked_list(k)
        k.admin_marketing.open_create_promotion()
        for step in case["steps"]:
            k.admin.fill_form(step)
        k.admin.verify_field_value("Slug", case["expectedSlug"])
