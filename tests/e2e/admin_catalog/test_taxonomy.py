# ============================================================
# TEST: ADMIN - DANH MỤC & THƯƠNG HIỆU (LƯỚI THẺ)
# Mục tiêu: Danh mục và Thương hiệu dùng chung cấu trúc lưới thẻ + modal -> 1 bộ test chạy cho cả 2 (data-driven):
#           dữ liệu thật, hiển thị thẻ, tìm kiếm, thêm/sửa/xóa/gạt Hoạt động (mock), slug tự sinh
# Dữ liệu: data/admin-catalog/fixtures.json (thẻ giả), data/admin-catalog/taxonomy.json (1 phần tử / trang)
# API cần quan sát: k.admin_catalog.*, k.admin.click_button / fill_form, k.common.mock_write / verify_request
# Kết quả mong đợi: thẻ + modal đúng dữ liệu, request POST/PUT/DELETE đúng payload (mock, không ghi DB)
# Ghi chú: mỗi trang sinh 1 bộ class riêng (TestAdminCategory*, TestAdminBrand*) bằng hàm _build_suite.
# ============================================================
import pytest

from utils.cases import case_params, known_bug
from utils.data_loader import load_data

FIXTURE = load_data("admin-catalog/fixtures.json")
ENTITIES = load_data("admin-catalog/taxonomy.json")
ID = {"category": "ADC-CAT", "brand": "ADC-BRD"}

pytestmark = pytest.mark.role("admin")


def _title(text):
    """Gán docstring (tiêu đề test) có tham số theo trang."""

    def decorate(function):
        function.__doc__ = text
        return function

    return decorate


def _build_suite(e):
    id_ = ID[e["key"]]
    api = f"**/api/admin/{e['api']}"
    items = FIXTURE[e["fixture"]]
    label = e["label"]

    class RealData:
        @pytest.mark.smoke
        @_title(f"[{id_}-01] Dữ liệu thật: trang {label} có thẻ, ô tìm kiếm, nút thêm")
        def test_real_data(self, k):
            k.admin.open_admin_page(e["path"], e["title"])
            k.admin_catalog.verify_api_requested(f"/admin/{e['api']}")
            k.admin_catalog.verify_card_count_at_least(1)
            k.common.verify_no_page_errors()

    RealData.__doc__ = f"Admin - {label}"

    @pytest.fixture
    def mocked(self, k):
        """Dữ liệu mock: mock API của trang rồi mở trang."""
        k.admin_catalog.mock_catalog_api({e["fixture"]: items})
        k.admin.open_admin_page(e["path"], e["title"])

    @pytest.mark.usefixtures("mocked")
    class Mock:
        @_title(f"[{id_}-02] Thẻ hiển thị tên, slug, mô tả và nút gạt theo dữ liệu")
        def test_cards_display(self, k):
            k.admin_catalog.verify_cards([i["name"] for i in items])
            for i in items:
                k.admin_catalog.verify_card_details(i["name"], i["slug"], i.get("description"))
                k.admin_catalog.verify_card_active(i["name"], i["is_active"])

        @_title(f"[{id_}-03] Thêm {label.lower()} (mock POST) -> payload đúng, toast, thẻ mới")
        def test_create(self, k):
            k.common.mock_write("POST", api, e["create"]["response"])
            k.admin.click_button(e["addButton"])
            k.admin.verify_modal_open(e["addHeading"])
            k.admin.fill_form(e["create"]["form"])
            k.admin.click_button("Lưu")
            k.common.verify_request("POST", f"/admin/{e['api']}", e["create"]["payload"])
            k.common.verify_toast(e["toasts"]["created"])
            k.admin.verify_modal_closed(e["addHeading"])
            k.admin_catalog.verify_cards([e["create"]["name"]])

        @_title(f"[{id_}-04] Bỏ trống tên -> trình duyệt chặn, không gửi request")
        def test_empty_name_blocked(self, k):
            k.common.mock_write("POST", api, e["create"]["response"])
            k.admin.click_button(e["addButton"])
            k.admin.click_button("Lưu")
            k.admin.verify_modal_open(e["addHeading"])
            k.common.verify_no_request("POST", f"/admin/{e['api']}")

        @_title(f'[{id_}-05] "Hủy" đóng modal thêm, không gửi request')
        def test_cancel_create(self, k):
            k.common.mock_write("POST", api, e["create"]["response"])
            k.admin.click_button(e["addButton"])
            k.admin.fill_form({e["nameLabel"]: e["create"]["name"]})
            k.admin.click_button("Hủy")
            k.admin.verify_modal_closed(e["addHeading"])
            k.common.verify_no_request("POST", f"/admin/{e['api']}")
            k.admin_catalog.verify_cards([], [e["create"]["name"]])

        @_title(f"[{id_}-06] Lưu lỗi -> toast lỗi, modal vẫn mở giữ dữ liệu đã nhập")
        def test_save_error_keeps_modal(self, k, request):
            source = "AdminCategories.jsx:57-59" if e["key"] == "category" else "AdminBrands.jsx:57-59"
            known_bug(request, f"{source} - catch gọi setShowForm(false) nên modal đóng, mất dữ liệu vừa nhập")
            k.common.mock_write(
                "POST", api, {"success": False, "message": "Có lỗi xảy ra, vui lòng thử lại sau."}, 500
            )
            k.admin.click_button(e["addButton"])
            k.admin.fill_form({e["nameLabel"]: e["create"]["name"]})
            k.admin.click_button("Lưu")
            k.common.verify_toast(e["toasts"]["saveFailed"])
            k.admin.verify_modal_open(e["addHeading"])
            k.admin.verify_field_value(e["nameLabel"], e["create"]["name"])

        @_title(f"[{id_}-07] Sửa: modal điền sẵn dữ liệu, lưu gửi PUT (mock) và cập nhật thẻ")
        def test_edit(self, k):
            ed = e["edit"]
            k.common.mock_write("PUT", f"{api}/{ed['id']}", ed["response"])
            k.admin_catalog.click_card_edit(ed["target"])
            k.admin.verify_modal_open(e["editHeading"])
            for field, value in ed["prefill"].items():
                k.admin.verify_field_value(field, value)
            k.admin.fill_form(ed["form"])
            k.admin.click_button("Lưu")
            k.common.verify_request("PUT", f"/admin/{e['api']}/{ed['id']}", ed["payload"])
            k.common.verify_toast(e["toasts"]["updated"])
            k.admin.verify_modal_closed(e["editHeading"])
            k.admin_catalog.verify_card_details(ed["name"], ed["payload"]["slug"], ed.get("description"))

        @_title(f'[{id_}-08] Xóa: modal xác nhận đúng tên; "Hủy" không gửi request')
        def test_delete_cancel(self, k):
            d = e["delete"]
            k.common.mock_write("DELETE", f"{api}/{d['id']}", {"success": True})
            k.admin_catalog.click_card_delete(d["target"])
            k.admin_catalog.verify_delete_confirm_message(e["deleteMessage"].replace("{name}", d["target"], 1))
            k.admin.click_button("Hủy")
            k.admin.verify_modal_closed("Xác nhận xóa")
            k.common.verify_no_request("DELETE", f"/admin/{e['api']}/")
            k.admin_catalog.verify_cards([d["target"]])

        @_title(f"[{id_}-09] Xóa thành công (mock DELETE) -> toast, thẻ biến mất")
        def test_delete_success(self, k):
            d = e["delete"]
            k.common.mock_write("DELETE", f"{api}/{d['id']}", {"success": True})
            k.admin_catalog.click_card_delete(d["target"])
            k.admin.click_button("Xóa")
            k.common.verify_request("DELETE", f"/admin/{e['api']}/{d['id']}")
            k.common.verify_toast(e["toasts"]["deleted"])
            k.admin_catalog.verify_cards([], [d["target"]])

        @_title(f"[{id_}-10] Xóa bị server từ chối -> toast thông điệp server, thẻ còn nguyên")
        def test_delete_rejected(self, k):
            d = e["delete"]
            k.common.mock_write("DELETE", f"{api}/{d['id']}", {"success": False, "message": d["errorMessage"]}, 400)
            k.admin_catalog.click_card_delete(d["target"])
            k.admin.click_button("Xóa")
            k.common.verify_toast(d["errorMessage"])
            k.admin.verify_modal_closed("Xác nhận xóa")
            k.admin_catalog.verify_cards([d["target"]])

        @_title(f"[{id_}-11] Gạt tắt Hoạt động (mock PUT) -> gửi is_active=false, toast")
        def test_toggle_off(self, k):
            t = e["toggle"]
            k.common.mock_write("PUT", f"{api}/{t['id']}", {"success": True})
            k.admin_catalog.click_card_toggle(t["target"])
            k.common.verify_request("PUT", f"/admin/{e['api']}/{t['id']}", t["payload"])
            k.common.verify_toast(e["toasts"]["toggled"])
            k.admin_catalog.verify_card_active(t["target"], False)

        @_title(f"[{id_}-12] Gạt Hoạt động lỗi -> toast lỗi, giữ nguyên trạng thái")
        def test_toggle_error(self, k, request):
            source = "AdminCategories.jsx:36-38" if e["key"] == "category" else "AdminBrands.jsx:36-38"
            known_bug(request, f"{source} - nhánh catch vẫn đảo trạng thái nên nút gạt đổi dù API lỗi")
            t = e["toggle"]
            k.common.mock_write("PUT", f"{api}/{t['id']}", {"success": False}, 500)
            k.admin_catalog.click_card_toggle(t["target"])
            k.common.verify_toast(e["toasts"]["toggleFailed"])
            k.admin_catalog.verify_card_active(t["target"], True)

        @_title(f'[{id_}-13] {label} nổi bật hiển thị nhãn "Nổi bật"')
        def test_featured_badge(self, k, request):
            known_bug(request, e["featured"]["knownBug"])
            k.admin_catalog.verify_card_featured(e["featured"]["target"], True)

    Mock.mocked = mocked
    Mock.__doc__ = f"Admin - {label} - Dữ liệu mock"

    @pytest.mark.usefixtures("mocked")
    class Search:
        @pytest.mark.parametrize("case", case_params(e["searches"]))
        def test_search(self, k, case):
            """Tìm kiếm (data-driven)"""
            k.admin.search_list(e["searchPlaceholder"], case["text"])
            k.admin_catalog.verify_cards(case["visible"], case["hidden"])
            if case.get("empty"):
                k.admin_catalog.verify_cards_empty(e["empty"])

    Search.mocked = mocked
    Search.__doc__ = f"Admin - {label} - Dữ liệu mock - Tìm kiếm (data-driven)"

    suite = {"RealData": RealData, "Mock": Mock, "Search": Search}

    if e.get("slugAutofill"):

        @pytest.mark.usefixtures("mocked")
        class SlugAutofill:
            @pytest.mark.parametrize("case", case_params(e["slugAutofill"]))
            def test_slug_autofill(self, k, case):
                """Slug tự sinh khi gõ tên (data-driven)"""
                k.admin.click_button(e["addButton"])
                k.admin.fill_form({e["nameLabel"]: case["name"]})
                k.admin.verify_field_value("Slug", case["slug"])

        SlugAutofill.mocked = mocked
        SlugAutofill.__doc__ = f"Admin - {label} - Dữ liệu mock - Slug tự sinh khi gõ tên (data-driven)"
        suite["SlugAutofill"] = SlugAutofill

    return suite


# Sinh class test cho từng trang: TestAdminCategoryRealData, TestAdminBrandMock, ...
for _entity in ENTITIES:
    for _suffix, _cls in _build_suite(_entity).items():
        _name = f"TestAdmin{_entity['key'].capitalize()}{_suffix}"
        _cls.__name__ = _cls.__qualname__ = _name
        globals()[_name] = _cls
