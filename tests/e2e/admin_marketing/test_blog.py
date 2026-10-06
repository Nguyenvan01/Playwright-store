# ============================================================
# TEST: QUẢN TRỊ - BÀI VIẾT
# Mục tiêu: danh sách (thật + mock), tìm kiếm, validate form, slug, thêm/sửa/ẩn/nổi bật/xem/xóa
#           (mock ghi), ảnh xem trước
# Dữ liệu: data/admin-marketing/blog.json
# Kết quả mong đợi: bảng/form khớp dữ liệu; request ghi gửi đúng payload; toast đúng
# ============================================================
import pytest

from utils.cases import case_params
from utils.data_loader import load_data

DATA = load_data("admin-marketing/blog.json")
SEARCH = "Tìm theo tiêu đề, slug, mô tả..."
LIST_API = "**/api/admin/blogs"
ITEM_API = "**/api/admin/blogs/*"
CREATE = "Thêm bài viết"
EDIT = "Sửa bài viết"
# Ảnh PNG 1x1 dạng data URL (không cần mạng).
PIXEL = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="

pytestmark = pytest.mark.role("admin")


def _open_mocked_list(k):
    k.admin_marketing.mock_blog_list(DATA["list"])
    k.admin_marketing.open_blog()


class TestBlog:
    """Quản trị - Bài viết"""

    @pytest.mark.smoke
    def test_real_data(self, k):
        """[ADM-BLG-01] Dữ liệu thật: đủ cột và có ít nhất 1 bài viết"""
        k.admin_marketing.open_blog()
        k.admin_marketing.verify_columns(DATA["headers"])
        k.admin_marketing.verify_rows_at_least(1)
        k.common.verify_no_page_errors()

    def test_empty_list(self, k):
        """[ADM-BLG-02] Chưa có bài viết -> trạng thái rỗng"""
        k.admin_marketing.mock_blog_list([])
        k.admin_marketing.open_blog()
        k.common.verify_text_visible("Chưa có bài viết nào")
        k.common.verify_text_visible("Nhấn Thêm bài viết để tạo nội dung mới.")

    @pytest.mark.smoke
    def test_create_success(self, k):
        """[ADM-BLG-03] Thêm bài viết thành công gửi đúng dữ liệu, bài mới lên đầu (mock POST)"""
        create = DATA["create"]
        created = {"id": 99, **create["expectedPayload"], "created_at": "2026-10-01T03:00:00.000Z"}
        k.common.mock_write("POST", LIST_API, {"success": True, "blog": created})
        _open_mocked_list(k)
        k.admin_marketing.open_create_blog()
        k.admin.fill_form(create["form"])
        k.admin_marketing.click_modal_button(CREATE, "Lưu bài viết")
        k.common.verify_request("POST", "/admin/blogs", create["expectedPayload"])
        k.common.verify_toast(create["toast"])
        k.admin.verify_modal_closed(CREATE)
        k.admin_marketing.verify_row_count(len(DATA["list"]) + 1)
        k.admin_marketing.verify_row_cells(
            create["expectedPayload"]["title"], {"Trạng thái": "Ẩn", "Bài viết": "Nổi bật"}
        )

    def test_edit_keeps_slug(self, k):
        """[ADM-BLG-04] Sửa: form điền sẵn, giữ slug cũ khi đổi tiêu đề, gửi PUT đúng (mock)"""
        edit = DATA["edit"]
        updated = {**DATA["list"][0], "title": edit["form"]["Tiêu đề"]}
        k.common.mock_write("PUT", ITEM_API, {"success": True, "blog": updated})
        _open_mocked_list(k)
        k.admin.click_row_action(edit["title"], "Sửa")
        k.admin.verify_modal_open(EDIT)
        for label, value in edit["prefilled"].items():
            k.admin.verify_field_value(label, value)
        k.admin.fill_form(edit["form"])
        k.admin.verify_field_value("Slug", edit["prefilled"]["Slug"])
        k.admin_marketing.click_modal_button(EDIT, "Lưu bài viết")
        k.common.verify_request("PUT", "/admin/blogs/1", edit["expectedPayload"])
        k.common.verify_toast(edit["toast"])
        k.admin.verify_row(str(edit["form"]["Tiêu đề"]))

    def test_view_detail(self, k):
        """[ADM-BLG-05] Xem chi tiết bài viết"""
        _open_mocked_list(k)
        k.admin.click_row_action(DATA["view"]["title"], "Xem")
        k.admin_marketing.verify_modal_text("Chi tiết bài viết", DATA["view"]["texts"])

    def test_delete_cancel(self, k):
        """[ADM-BLG-06] Xóa: bấm "Hủy" không gửi DELETE"""
        k.common.mock_write("DELETE", ITEM_API, {"success": True})
        _open_mocked_list(k)
        k.admin.click_row_action(DATA["remove"]["title"], "Xóa")
        k.admin_marketing.verify_modal_text("Xóa bài viết", ["Bạn có chắc chắn muốn xóa bài viết này không?"])
        k.admin_marketing.click_modal_button("Xóa bài viết", "Hủy")
        k.admin.verify_modal_closed("Xóa bài viết")
        k.common.verify_no_request("DELETE", "/admin/blogs")

    def test_delete_confirm(self, k):
        """[ADM-BLG-07] Xóa: xác nhận gửi DELETE và bỏ dòng (mock)"""
        remove = DATA["remove"]
        k.common.mock_write("DELETE", ITEM_API, {"success": True})
        _open_mocked_list(k)
        k.admin.click_row_action(remove["title"], "Xóa")
        k.admin_marketing.click_modal_button("Xóa bài viết", "Xóa")
        k.common.verify_request("DELETE", "/admin/blogs/3")
        k.common.verify_toast(remove["toast"])
        k.admin.verify_row(remove["title"], False)

    def test_image_preview(self, k):
        """[ADM-BLG-08] Ảnh: URL hợp lệ hiện ảnh xem trước, URL hỏng hiện lỗi"""
        _open_mocked_list(k)
        k.admin_marketing.open_create_blog()
        k.admin_marketing.set_blog_image(PIXEL)
        k.admin_marketing.set_blog_image(DATA["invalidImage"]["url"], DATA["invalidImage"]["error"])

    def test_cancel_edit_then_create_empty(self, k):
        """[ADM-BLG-09] Hủy form sửa rồi bấm "Thêm bài viết" -> form trống"""
        _open_mocked_list(k)
        k.admin.click_row_action(DATA["edit"]["title"], "Sửa")
        k.admin_marketing.click_modal_button(EDIT, "Hủy")
        k.admin.verify_modal_closed(EDIT)
        k.admin_marketing.open_create_blog()
        k.admin.verify_field_value("Tiêu đề", "")
        k.admin.verify_field_value("Slug", "")
        k.admin.verify_field_value("Mô tả ngắn", "")


class TestBlogRows:
    """Quản trị - Bài viết: Hiển thị dòng (data-driven)"""

    @pytest.mark.parametrize("case", case_params(DATA["rows"]))
    def test_row(self, k, case):
        _open_mocked_list(k)
        k.admin_marketing.verify_row_count(len(DATA["list"]))
        k.admin_marketing.verify_row_cells(case["rowText"], case["expected"])
        k.admin_marketing.verify_row_actions(case["rowText"], case["actions"])


class TestBlogSearch:
    """Quản trị - Bài viết: Tìm kiếm (data-driven)"""

    @pytest.mark.parametrize("case", case_params(DATA["search"]))
    def test_search(self, k, case):
        _open_mocked_list(k)
        k.admin.search_list(SEARCH, case["keyword"])
        k.admin_marketing.verify_visible_rows(case["visible"], case["hidden"])
        if case.get("emptyText"):
            k.common.verify_text_visible(case["emptyText"])


class TestBlogValidation:
    """Quản trị - Bài viết: Form thêm - kiểm tra dữ liệu (data-driven)"""

    @pytest.mark.parametrize("case", case_params(DATA["validation"]))
    def test_validation(self, k, case):
        k.common.mock_write("POST", LIST_API, {"success": True})
        _open_mocked_list(k)
        k.admin_marketing.open_create_blog()
        k.admin.fill_form(case["form"])
        k.admin_marketing.click_modal_button(CREATE, "Lưu bài viết")
        k.common.verify_toast(case["toast"])
        k.admin.verify_modal_open(CREATE)
        k.common.verify_no_request("POST", "/admin/blogs")


class TestBlogSlug:
    """Quản trị - Bài viết: Slug (data-driven)"""

    @pytest.mark.parametrize("case", case_params(DATA["slugCases"]))
    def test_slug(self, k, case):
        _open_mocked_list(k)
        k.admin_marketing.open_create_blog()
        for step in case["steps"]:
            k.admin.fill_form(step)
        k.admin.verify_field_value("Slug", case["expectedSlug"])


class TestBlogToggles:
    """Quản trị - Bài viết: Ẩn/Hiển thị, nổi bật trên dòng (data-driven)"""

    @pytest.mark.parametrize("case", case_params(DATA["toggles"]))
    def test_toggle(self, k, case):
        k.common.mock_write("PUT", ITEM_API, {"success": True})
        _open_mocked_list(k)
        k.admin.click_row_action(case["rowText"], case["action"])
        k.common.verify_request("PUT", "/admin/blogs/", case["expectedPayload"])
        k.common.verify_toast(case["toast"])
        k.admin_marketing.verify_row_cells(case["rowText"], case["expected"])
