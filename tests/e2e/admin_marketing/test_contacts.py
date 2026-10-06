# ============================================================
# TEST: QUẢN TRỊ - LIÊN HỆ
# Mục tiêu: danh sách (thật + mock), nút theo trạng thái, tìm kiếm, lọc trạng thái,
#           đổi trạng thái xử lý, xem chi tiết, xóa (mock ghi)
# Dữ liệu: data/admin-marketing/contacts.json
# Kết quả mong đợi: bảng khớp dữ liệu; request lọc/ghi đúng tham số; toast đúng
# ============================================================
import pytest

from utils.cases import case_params
from utils.data_loader import load_data

DATA = load_data("admin-marketing/contacts.json")
SEARCH = "Tìm theo tên, email, số điện thoại, nội dung..."
ITEM_API = "**/api/admin/contacts/*"
STATUS_API = "**/api/admin/contacts/*/status"
NAMES = [c["name"] for c in DATA["list"]]

pytestmark = pytest.mark.role("admin")


def _open_mocked_list(k, contacts=None):
    k.admin_marketing.mock_contact_list(DATA["list"] if contacts is None else contacts)
    k.admin_marketing.open_contacts()


class TestContacts:
    """Quản trị - Liên hệ"""

    @pytest.mark.smoke
    def test_real_data(self, k):
        """[ADM-CTC-01] Dữ liệu thật: trang tải được, đủ cột"""
        k.admin_marketing.open_contacts()
        k.admin_marketing.verify_columns(DATA["headers"])
        k.common.verify_no_page_errors()

    def test_empty_list(self, k):
        """[ADM-CTC-02] Chưa có liên hệ -> trạng thái rỗng"""
        k.admin_marketing.mock_contact_list([])
        k.admin_marketing.open_contacts()
        k.common.verify_text_visible("Chưa có liên hệ nào")
        k.common.verify_text_visible("Liên hệ mới từ khách hàng sẽ hiển thị tại đây.")

    def test_api_error(self, k):
        """[ADM-CTC-03] API lỗi -> toast "Không thể tải danh sách liên hệ.\""""
        k.common.mock_get("**/api/admin/contacts*", {"success": False}, 500)
        k.admin_marketing.open_contacts()
        k.common.verify_toast("Không thể tải danh sách liên hệ.")

    def test_detail_mark_processed(self, k):
        """[ADM-CTC-04] Xem chi tiết và đánh dấu đã xử lý trong modal (mock PUT)"""
        detail = DATA["detail"]
        k.common.mock_write("PUT", STATUS_API, {"success": True})
        _open_mocked_list(k)
        k.admin.click_row_action(detail["rowText"], "Xem")
        k.admin_marketing.verify_modal_text("Chi tiết liên hệ", detail["texts"])
        k.admin_marketing.click_modal_button("Chi tiết liên hệ", detail["button"])
        k.common.verify_request("PUT", "/admin/contacts/1/status", {"status": "processed"})
        k.common.verify_toast(DATA["toast"])
        k.admin_marketing.verify_modal_text("Chi tiết liên hệ", [detail["badge"], "Đánh dấu chưa xử lý"])

    def test_delete_cancel(self, k):
        """[ADM-CTC-05] Xóa: bấm "Hủy" không gửi DELETE"""
        k.common.mock_write("DELETE", ITEM_API, {"success": True})
        _open_mocked_list(k)
        k.admin.click_row_action(DATA["remove"]["rowText"], "Xóa")
        k.admin_marketing.verify_modal_text("Xóa liên hệ", ["Bạn có chắc chắn muốn xóa liên hệ này không?"])
        k.admin_marketing.click_modal_button("Xóa liên hệ", "Hủy")
        k.admin.verify_modal_closed("Xóa liên hệ")
        k.common.verify_no_request("DELETE", "/admin/contacts")

    def test_delete_confirm(self, k):
        """[ADM-CTC-06] Xóa: xác nhận gửi DELETE và bỏ dòng (mock)"""
        remove = DATA["remove"]
        k.common.mock_write("DELETE", ITEM_API, {"success": True})
        _open_mocked_list(k)
        k.admin.click_row_action(remove["rowText"], "Xóa")
        k.admin_marketing.click_modal_button("Xóa liên hệ", "Xóa")
        k.common.verify_request("DELETE", "/admin/contacts/3")
        k.common.verify_toast(remove["toast"])
        k.admin.verify_row(remove["rowText"], False)


class TestContactRows:
    """Quản trị - Liên hệ: Hiển thị dòng + nút theo trạng thái (data-driven)"""

    @pytest.mark.parametrize("case", case_params(DATA["rows"]))
    def test_row(self, k, case):
        _open_mocked_list(k)
        k.admin_marketing.verify_row_count(len(DATA["list"]))
        k.admin_marketing.verify_row_cells(case["rowText"], case["expected"])
        k.admin_marketing.verify_row_actions(case["rowText"], case["actions"])


class TestContactSearch:
    """Quản trị - Liên hệ: Tìm kiếm (data-driven)"""

    @pytest.mark.parametrize("case", case_params(DATA["search"]))
    def test_search(self, k, case):
        _open_mocked_list(k)
        k.admin.search_list(SEARCH, case["keyword"])
        k.admin_marketing.verify_visible_rows(case["visible"], case["hidden"])
        if case.get("emptyText"):
            k.common.verify_text_visible(case["emptyText"])


class TestContactFilters:
    """Quản trị - Liên hệ: Lọc trạng thái (data-driven)"""

    @pytest.mark.parametrize("case", case_params(DATA["filters"]))
    def test_filter(self, k, case):
        _open_mocked_list(k, case.get("list"))
        k.admin_marketing.filter_contact_status(case["status"])
        k.admin_marketing.verify_list_query("/admin/contacts", case["query"])
        k.admin_marketing.verify_visible_rows(
            case["visible"], [n for n in NAMES if n not in case["visible"]]
        )
        if case.get("emptyText"):
            k.common.verify_text_visible(case["emptyText"])


class TestContactStatusActions:
    """Quản trị - Liên hệ: Đổi trạng thái xử lý trên dòng (data-driven)"""

    @pytest.mark.parametrize("case", case_params(DATA["statusActions"]))
    def test_status_action(self, k, case):
        k.common.mock_write("PUT", STATUS_API, {"success": True})
        _open_mocked_list(k)
        k.admin.click_row_action(case["rowText"], case["action"])
        k.common.verify_request("PUT", f"/admin/contacts/{case['contactId']}/status", {"status": case["status"]})
        k.common.verify_toast(DATA["toast"])
        k.admin_marketing.verify_row_cells(case["rowText"], {"Trạng thái": case["badge"]})
        k.admin_marketing.verify_row_actions(case["rowText"], case["actionsAfter"])
