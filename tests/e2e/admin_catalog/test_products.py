# ============================================================
# TEST: ADMIN - DANH SÁCH SẢN PHẨM
# Mục tiêu: dữ liệu thật (cột, phân trang), dữ liệu mock (dòng, tìm kiếm/lọc, nổi bật, trạng thái,
#           xem/sửa/xóa, chọn nhiều, phân trang)
# Dữ liệu: data/admin-catalog/fixtures.json (sản phẩm giả), data/admin-catalog/products.json (case + expected)
# API cần quan sát: k.admin_catalog.*, k.common.mock_write / verify_request / verify_no_request
# Kết quả mong đợi: bảng hiển thị đúng dữ liệu, request GET/PUT/DELETE đúng tham số (mock, không ghi DB)
# ============================================================
import pytest

from utils.cases import case_params, known_bug
from utils.data_loader import load_data

FIXTURE = load_data("admin-catalog/fixtures.json")
DATA = load_data("admin-catalog/products.json")

pytestmark = pytest.mark.role("admin")


@pytest.fixture
def mocked_list(k):
    """Dữ liệu mock: mock API danh mục hàng và mở /admin/products."""
    k.admin_catalog.mock_catalog_api(FIXTURE)
    k.admin.open_admin_page("/admin/products", "Sản phẩm")


class TestProductsList:
    """Admin - Danh sách sản phẩm"""

    @pytest.mark.smoke
    def test_real_data_columns_pagination(self, k):
        """[ADC-PRD-01] Dữ liệu thật: có sản phẩm, đủ cột, phân trang 10/trang"""
        k.admin.open_admin_page("/admin/products", "Sản phẩm")
        k.admin_catalog.verify_api_requested("/admin/products", {"page": 1, "limit": 10})
        k.admin_catalog.verify_columns(DATA["headers"])
        k.admin_catalog.verify_product_count_at_least(1)
        k.admin_catalog.verify_products_pagination_first_page()
        k.common.verify_no_page_errors()

    def test_add_product_opens_form(self, k):
        """[ADC-PRD-02] "Thêm sản phẩm" mở form tạo mới"""
        k.admin_catalog.mock_catalog_api(FIXTURE)
        k.admin.open_admin_page("/admin/products", "Sản phẩm")
        k.admin_catalog.click_add_product()
        k.common.verify_url("/admin/products/create")
        k.admin.verify_header_title("Thêm sản phẩm mới")
        k.admin_catalog.verify_product_form_ready("Tạo sản phẩm")


@pytest.mark.usefixtures("mocked_list")
class TestProductsMock:
    """Dữ liệu mock"""

    def test_rows_display(self, k):
        """[ADC-PRD-03] Mỗi dòng hiển thị đúng thương hiệu, SKU, danh mục, giá, tồn kho, đã bán, nổi bật, trạng thái"""
        k.admin_catalog.verify_product_rows(DATA["rows"])
        k.admin_catalog.verify_products_pagination(None)

    def test_view_link(self, k):
        """[ADC-PRD-04] Link "Xem" trỏ tới trang sản phẩm ngoài cửa hàng"""
        k.admin_catalog.verify_product_view_link(DATA["viewLink"]["product"], DATA["viewLink"]["href"])

    def test_edit_opens_form(self, k):
        """[ADC-PRD-05] "Sửa" mở form chỉnh sửa của đúng sản phẩm"""
        k.admin_catalog.click_product_action(DATA["editLink"]["product"], "Sửa")
        k.common.verify_url(DATA["editLink"]["path"])
        k.admin_catalog.verify_product_form_ready("Cập nhật")
        k.admin.verify_field_value("Tên sản phẩm", DATA["editLink"]["product"])


@pytest.mark.usefixtures("mocked_list")
class TestProductsFilter:
    """Dữ liệu mock - Tìm kiếm & lọc (data-driven)"""

    @pytest.mark.parametrize("case", case_params(DATA["filters"]))
    def test_search_and_filter(self, k, case):
        """Tìm kiếm & lọc (data-driven)"""
        if case.get("search"):
            k.admin_catalog.search_products(case["search"])
        if case.get("category"):
            k.admin_catalog.filter_products_by_category(case["category"])
        if case.get("brand"):
            k.admin_catalog.filter_products_by_brand(case["brand"])
        k.admin_catalog.verify_api_requested("/admin/products", {**case["request"], "page": 1})
        for name in case["rows"]:
            k.admin_catalog.verify_product_listed(name)
        for name in case["hidden"]:
            k.admin_catalog.verify_product_listed(name, False)


@pytest.mark.usefixtures("mocked_list")
class TestProductsFeatured:
    """Dữ liệu mock - Nổi bật (mock PUT /toggle-featured, data-driven)"""

    @pytest.mark.parametrize("case", case_params(DATA["featured"]))
    def test_toggle_featured(self, k, case):
        """Nổi bật (mock PUT /toggle-featured, data-driven)"""
        k.common.mock_write(
            "PUT",
            f"**/api/admin/products/{case['productId']}/toggle-featured",
            {"success": not case.get("status")},
            case.get("status") or 200,
        )
        k.admin_catalog.verify_product_featured_title(case["product"], case["before"])
        k.admin_catalog.click_product_featured(case["product"])
        k.common.verify_request("PUT", f"/admin/products/{case['productId']}/toggle-featured")
        k.common.verify_toast(case["toast"])
        k.admin_catalog.verify_product_featured_title(case["product"], case["after"])


@pytest.mark.usefixtures("mocked_list")
class TestProductsStatus:
    """Dữ liệu mock - Trạng thái bán (mock PUT /toggle, data-driven)"""

    @pytest.mark.parametrize("case", case_params(DATA["status"]))
    def test_toggle_status(self, k, case):
        """Trạng thái bán (mock PUT /toggle, data-driven)"""
        k.common.mock_write(
            "PUT",
            f"**/api/admin/products/{case['productId']}/toggle",
            {"success": not case.get("status")},
            case.get("status") or 200,
        )
        k.admin_catalog.verify_product_active(case["product"], case["before"])
        k.admin_catalog.click_product_status(case["product"])
        k.common.verify_request("PUT", f"/admin/products/{case['productId']}/toggle")
        k.common.verify_toast(case["toast"])
        k.admin_catalog.verify_product_active(case["product"], case["after"])


@pytest.mark.usefixtures("mocked_list")
class TestProductsDelete:
    """Dữ liệu mock - Xóa sản phẩm (mock DELETE)"""

    def test_cancel_delete_modal(self, k):
        """[ADC-PRD-06] Modal "Xóa sản phẩm?" + "Hủy" không gửi request"""
        k.common.mock_write("DELETE", "**/api/admin/products/*", {"success": True})
        k.admin_catalog.click_product_action("Mũ lưỡi trai E2E", "Xóa")
        k.admin_catalog.verify_delete_product_modal(DATA["deleteModal"]["heading"], DATA["deleteModal"]["message"])
        k.admin.click_button("Hủy")
        k.admin.verify_modal_closed(DATA["deleteModal"]["heading"])
        k.common.verify_no_request("DELETE", "/admin/products/")
        k.admin_catalog.verify_product_listed("Mũ lưỡi trai E2E")

    @pytest.mark.parametrize("case", case_params(DATA["delete"]))
    def test_delete(self, k, case):
        """Xóa sản phẩm (mock DELETE)"""
        k.common.mock_write(
            "DELETE",
            f"**/api/admin/products/{case['productId']}",
            {"success": case["status"] == 200},
            case["status"],
        )
        k.admin_catalog.click_product_action(case["product"], "Xóa")
        k.admin.click_button("Xóa")
        k.common.verify_request("DELETE", f"/admin/products/{case['productId']}")
        k.common.verify_toast(case["toast"])
        k.admin.verify_modal_closed(DATA["deleteModal"]["heading"])
        k.admin_catalog.verify_product_listed(case["product"], not case["removed"])


@pytest.mark.usefixtures("mocked_list")
class TestProductsBulk:
    """Dữ liệu mock - Chọn nhiều"""

    def test_bulk_selection_count(self, k):
        """[ADC-PRD-07] Chọn từng dòng / chọn tất cả hiển thị số sản phẩm được chọn"""
        k.admin_catalog.verify_bulk_selection(None)
        k.admin_catalog.select_products(DATA["bulk"]["select"])
        k.admin_catalog.verify_bulk_selection(DATA["bulk"]["text"])
        k.admin_catalog.select_all_products()
        k.admin_catalog.verify_bulk_selection(DATA["bulk"]["allText"])

    def test_bulk_delete(self, k, request):
        """[ADC-PRD-08] "Xóa đã chọn" xóa các sản phẩm đã chọn"""
        known_bug(request, 'AdminProducts.jsx:170 nút "Xóa đã chọn" không có onClick -> bấm không làm gì')
        k.common.mock_write("DELETE", "**/api/admin/products/*", {"success": True})
        k.admin_catalog.select_products(DATA["bulk"]["select"])
        k.admin_catalog.click_bulk_delete()
        k.common.verify_request("DELETE", "/admin/products/")


class TestProductsPagination:
    """Admin - Danh sách sản phẩm - Phân trang"""

    def test_pagination_page_two(self, k):
        """[ADC-PRD-09] Phân trang: sang trang 2 gọi API page=2"""
        k.admin_catalog.mock_catalog_api({**FIXTURE, "productsTotal": DATA["pagination"]["total"]})
        k.admin.open_admin_page("/admin/products", "Sản phẩm")
        k.admin_catalog.verify_products_pagination(DATA["pagination"]["first"])
        k.admin_catalog.go_to_products_page(2)
        k.admin_catalog.verify_api_requested("/admin/products", {"page": 2, "limit": 10})
        k.admin_catalog.verify_products_pagination(DATA["pagination"]["second"])
