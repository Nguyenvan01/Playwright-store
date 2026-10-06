# ============================================================
# TEST: QUẢN TRỊ - ĐÁNH GIÁ
# Mục tiêu: danh sách (thật + mock), nút theo trạng thái, tìm kiếm, lọc trạng thái/số sao,
#           duyệt/ẩn, xem chi tiết, xóa (mock ghi)
# Dữ liệu: data/admin-marketing/reviews.json
# Kết quả mong đợi: bảng khớp dữ liệu; request lọc/ghi đúng tham số; toast đúng
# ============================================================
import pytest

from utils.cases import case_params
from utils.data_loader import load_data

DATA = load_data("admin-marketing/reviews.json")
SEARCH = "Tìm khách hàng, sản phẩm, nội dung..."
ITEM_API = "**/api/admin/reviews/*"
STATUS_API = "**/api/admin/reviews/*/status"
NAMES = [r["user_name"] for r in DATA["list"]]

pytestmark = pytest.mark.role("admin")


def _open_mocked_list(k):
    k.admin_marketing.mock_review_list(DATA["list"])
    k.admin_marketing.open_reviews()


class TestReviews:
    """Quản trị - Đánh giá"""

    @pytest.mark.smoke
    def test_real_data(self, k):
        """[ADM-REV-01] Dữ liệu thật: trang tải được, đủ cột"""
        k.admin_marketing.open_reviews()
        k.admin_marketing.verify_columns(DATA["headers"])
        k.common.verify_no_page_errors()

    def test_empty_list(self, k):
        """[ADM-REV-02] Chưa có đánh giá -> trạng thái rỗng"""
        k.admin_marketing.mock_review_list([])
        k.admin_marketing.open_reviews()
        k.common.verify_text_visible("Chưa có đánh giá nào")
        k.common.verify_text_visible("Đánh giá mới của khách hàng sẽ hiển thị tại đây.")

    def test_api_error(self, k):
        """[ADM-REV-03] API lỗi -> toast "Không thể tải danh sách đánh giá.\""""
        k.common.mock_get("**/api/admin/reviews*", {"success": False}, 500)
        k.admin_marketing.open_reviews()
        k.common.verify_toast("Không thể tải danh sách đánh giá.")

    def test_detail_approve(self, k):
        """[ADM-REV-04] Xem chi tiết và duyệt ngay trong modal (mock PUT)"""
        detail = DATA["detail"]
        k.common.mock_write("PUT", STATUS_API, {"success": True})
        _open_mocked_list(k)
        k.admin.click_row_action(detail["rowText"], "Xem")
        k.admin_marketing.verify_modal_text("Chi tiết đánh giá", detail["texts"])
        k.admin_marketing.click_modal_button("Chi tiết đánh giá", detail["approveButton"])
        k.common.verify_request("PUT", "/admin/reviews/1/status", {"status": "approved"})
        k.common.verify_toast(detail["toast"])
        k.admin_marketing.verify_modal_text("Chi tiết đánh giá", [detail["badge"], "Ẩn đánh giá"])

    def test_delete_cancel(self, k):
        """[ADM-REV-05] Xóa: bấm "Hủy" không gửi DELETE"""
        k.common.mock_write("DELETE", ITEM_API, {"success": True})
        _open_mocked_list(k)
        k.admin.click_row_action(DATA["remove"]["rowText"], "Xóa")
        k.admin_marketing.verify_modal_text("Xóa đánh giá", ["Bạn có chắc chắn muốn xóa đánh giá này không?"])
        k.admin_marketing.click_modal_button("Xóa đánh giá", "Hủy")
        k.admin.verify_modal_closed("Xóa đánh giá")
        k.common.verify_no_request("DELETE", "/admin/reviews")

    def test_delete_confirm(self, k):
        """[ADM-REV-06] Xóa: xác nhận gửi DELETE và bỏ dòng (mock)"""
        remove = DATA["remove"]
        k.common.mock_write("DELETE", ITEM_API, {"success": True})
        _open_mocked_list(k)
        k.admin.click_row_action(remove["rowText"], "Xóa")
        k.admin_marketing.click_modal_button("Xóa đánh giá", "Xóa")
        k.common.verify_request("DELETE", "/admin/reviews/4")
        k.common.verify_toast(remove["toast"])
        k.admin.verify_row(remove["rowText"], False)

    @pytest.mark.parametrize("case", case_params([DATA["updateError"]]))
    def test_update_error(self, k, case):
        k.common.mock_write("PUT", STATUS_API, {"success": False, "message": case["message"]}, case["status"])
        _open_mocked_list(k)
        k.admin.click_row_action(case["rowText"], "Duyệt")
        k.common.verify_toast(case["message"])
        k.admin_marketing.verify_row_cells(case["rowText"], {"Trạng thái": "Chờ duyệt"})


class TestReviewRows:
    """Quản trị - Đánh giá: Hiển thị dòng + nút theo trạng thái (data-driven)"""

    @pytest.mark.parametrize("case", case_params(DATA["rows"]))
    def test_row(self, k, case):
        _open_mocked_list(k)
        k.admin_marketing.verify_row_count(len(DATA["list"]))
        k.admin_marketing.verify_row_cells(case["rowText"], case["expected"])
        k.admin_marketing.verify_row_actions(case["rowText"], case["actions"])


class TestReviewSearch:
    """Quản trị - Đánh giá: Tìm kiếm (data-driven)"""

    @pytest.mark.parametrize("case", case_params(DATA["search"]))
    def test_search(self, k, case):
        _open_mocked_list(k)
        k.admin.search_list(SEARCH, case["keyword"])
        k.admin_marketing.verify_visible_rows(case["visible"], case["hidden"])
        if case.get("emptyText"):
            k.common.verify_text_visible(case["emptyText"])


class TestReviewFilters:
    """Quản trị - Đánh giá: Lọc trạng thái / số sao (data-driven)"""

    @pytest.mark.parametrize("case", case_params(DATA["filters"]))
    def test_filter(self, k, case):
        _open_mocked_list(k)
        if case["status"] != "all":
            k.admin_marketing.filter_review_status(case["status"])
        if case["rating"] != "all":
            k.admin_marketing.filter_review_rating(case["rating"])
        k.admin_marketing.verify_list_query("/admin/reviews", case["query"])
        k.admin_marketing.verify_visible_rows(
            case["visible"], [n for n in NAMES if n not in case["visible"]]
        )
        if case.get("emptyText"):
            k.common.verify_text_visible(case["emptyText"])


class TestReviewStatusActions:
    """Quản trị - Đánh giá: Duyệt / Ẩn trên dòng (data-driven)"""

    @pytest.mark.parametrize("case", case_params(DATA["statusActions"]))
    def test_status_action(self, k, case):
        k.common.mock_write("PUT", STATUS_API, {"success": True})
        _open_mocked_list(k)
        k.admin.click_row_action(case["rowText"], case["action"])
        k.common.verify_request("PUT", f"/admin/reviews/{case['reviewId']}/status", {"status": case["status"]})
        k.common.verify_toast(case["toast"])
        k.admin_marketing.verify_row_cells(case["rowText"], {"Trạng thái": case["badge"]})
