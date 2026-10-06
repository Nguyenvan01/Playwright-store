# ============================================================
# TEST: ADMIN - FORM SẢN PHẨM (TẠO / SỬA)
# Mục tiêu: validate form, slug tự sinh, tạo sản phẩm (payload + toast), biến thể, ảnh, sửa sản phẩm
# Dữ liệu: data/admin-catalog/fixtures.json (danh mục/thương hiệu/sản phẩm giả),
#          data/admin-catalog/product-form.json (case validate, slug, tạo, sửa, ảnh, upload)
# API cần quan sát: k.admin_catalog.*, k.admin.fill_form, k.common.mock_write / verify_request
# Kết quả mong đợi: request POST/PUT đúng payload (mock, không ghi DB), toast + điều hướng đúng
# ============================================================
import pytest

from utils.cases import case_params, known_bug
from utils.data_loader import load_data

FIXTURE = load_data("admin-catalog/fixtures.json")
DATA = load_data("admin-catalog/product-form.json")

pytestmark = pytest.mark.role("admin")


@pytest.fixture(autouse=True)
def mock_catalog(k):
    # Danh mục / thương hiệu / sản phẩm giả để dropdown và payload xác định được
    k.admin_catalog.mock_catalog_api(FIXTURE)


@pytest.fixture
def create_form(k, mock_catalog):
    """Mở form tạo sản phẩm (mock POST) và chờ form sẵn sàng."""
    k.common.mock_write("POST", "**/api/admin/products", DATA["create"]["response"])
    k.admin.open_admin_page("/admin/products/create", "Thêm sản phẩm mới")
    k.admin_catalog.verify_product_form_ready("Tạo sản phẩm")


@pytest.mark.usefixtures("create_form")
class TestProductCreateValidation:
    """Tạo sản phẩm - Validate (data-driven)"""

    @pytest.mark.parametrize("case", case_params(DATA["validation"]))
    def test_validation(self, k, case):
        """Validate (data-driven)"""
        if case["fields"]:
            k.admin.fill_form(case["fields"])
        k.admin_catalog.submit_product_form()
        k.admin_catalog.verify_product_form_error(case["error"])
        k.common.verify_no_request("POST", "/admin/products")
        k.common.verify_url("/admin/products/create")


@pytest.mark.usefixtures("create_form")
class TestProductCreateSlug:
    """Tạo sản phẩm - Slug tự sinh từ tên (data-driven)"""

    @pytest.mark.parametrize("case", case_params(DATA["slugs"]))
    def test_slug_autofill(self, k, case):
        """Slug tự sinh từ tên (data-driven)"""
        k.admin.fill_form({"Tên sản phẩm": case["name"]})
        k.admin.verify_field_value("Slug", case["slug"])


@pytest.mark.usefixtures("create_form")
class TestProductCreate:
    """Tạo sản phẩm"""

    @pytest.mark.smoke
    def test_create_full_product(self, k):
        """[ADC-PF-01] Tạo sản phẩm đầy đủ thông tin (mock POST) -> payload đúng, toast, về danh sách"""
        c = DATA["create"]
        k.admin.fill_form(c["fields"])
        k.admin.verify_field_value("Slug", c["slug"])
        k.admin_catalog.add_image_url(c["imageUrl"])
        k.admin_catalog.verify_image_count(1)
        k.admin_catalog.submit_product_form()
        k.common.verify_request("POST", "/admin/products", c["payload"])
        k.common.verify_toast(c["toast"])
        k.common.verify_url("/admin/products")
        k.admin.verify_header_title("Sản phẩm")

    def test_server_error_stays_on_form(self, k):
        """[ADC-PF-02] Server báo lỗi -> hiện lỗi trên form + toast, ở lại trang"""
        c = DATA["create"]
        k.common.mock_write(
            "POST",
            "**/api/admin/products",
            {"success": False, "message": c["error"]["message"]},
            c["error"]["status"],
        )
        k.admin.fill_form({"Tên sản phẩm": "Áo lỗi E2E", "Giá bán": "100000"})
        k.admin_catalog.submit_product_form()
        k.common.verify_request("POST", "/admin/products", {"name": "Áo lỗi E2E", "price": 100000})
        k.admin_catalog.verify_product_form_error(c["error"]["message"])
        k.common.verify_toast(c["error"]["message"])
        k.common.verify_url("/admin/products/create")

    def test_variant_builder(self, k):
        """[ADC-PF-03] Tạo biến thể: chọn size x màu sinh lưới SKU, xóa 1 dòng, gửi kèm payload"""
        v = DATA["variants"]
        k.admin.fill_form({"Tên sản phẩm": "Áo biến thể E2E", "Giá bán": v["price"], "SKU": v["sku"]})
        k.admin_catalog.verify_variant_toggle_label("+ Tạo biến thể")
        k.admin_catalog.toggle_variant_builder()
        k.admin_catalog.verify_variant_toggle_label("Tắt chế độ")
        k.admin_catalog.verify_generate_variants_button(v["buttonBefore"], False)
        k.admin_catalog.select_variant_sizes(v["sizes"])
        k.admin_catalog.verify_generate_variants_button("Tạo 0 biến thể", False)
        k.admin_catalog.select_variant_colors(v["colors"])
        k.admin_catalog.verify_generate_variants_button(v["buttonAfter"], True)
        k.admin_catalog.generate_variants()
        k.admin_catalog.verify_variant_toggle_label("+ Tạo biến thể")
        k.admin_catalog.verify_variant_rows(v["rows"])
        k.admin_catalog.remove_variant(1)
        remaining = [r for i, r in enumerate(v["rows"]) if i != 1]
        k.admin_catalog.verify_variant_rows(remaining)
        k.admin_catalog.submit_product_form()
        k.common.verify_request(
            "POST",
            "/admin/products",
            {
                "sku": v["sku"],
                "variants": [
                    {"sku": r["sku"], "price": v["price"], "stock": 0, "is_active": True} for r in remaining
                ],
            },
        )

    def test_images_from_url(self, k):
        """[ADC-PF-04] Ảnh từ URL: thêm, bỏ trùng, ảnh đầu là "Ảnh chính", xóa ảnh"""
        first, second = DATA["images"]["urls"]
        k.admin_catalog.verify_image_count(0)
        k.admin_catalog.add_image_url(first)
        k.admin_catalog.add_image_url(second)
        k.admin_catalog.verify_image_count(2)
        k.admin_catalog.add_image_url(first)
        k.admin_catalog.verify_image_count(2)
        k.admin_catalog.remove_image(0)
        k.admin_catalog.verify_image_count(1)

    def test_upload_uses_admin_token(self, k, request):
        """[ADC-PF-05] Tải ảnh lên gửi kèm token admin"""
        known_bug(request, DATA["upload"]["knownBug"])
        k.admin_catalog.upload_product_image(DATA["upload"]["fileName"], DATA["upload"]["response"])
        k.admin_catalog.verify_image_count(1)
        k.admin_catalog.verify_upload_used_admin_token()

    def test_back_without_request(self, k):
        """[ADC-PF-06] "Quay lại" về danh sách sản phẩm, không gửi request"""
        k.admin.fill_form({"Tên sản phẩm": "Bỏ dở E2E"})
        k.admin_catalog.click_back_to_products()
        k.common.verify_url("/admin/products")
        k.common.verify_no_request("POST", "/admin/products")


class TestProductEdit:
    """Sửa sản phẩm"""

    def test_edit_by_direct_url(self, k):
        """[ADC-PF-07] Mở trực tiếp URL sửa: tải chi tiết, điền sẵn; lưu gửi PUT giữ nguyên mô tả/chất liệu (mock)"""
        e = DATA["edit"]
        k.common.mock_write("PUT", f"**/api/admin/products/{e['id']}", {"success": True})
        k.common.goto(e["path"])
        k.admin_catalog.verify_product_form_ready("Cập nhật")
        k.admin_catalog.verify_api_requested(f"/admin/products/{e['id']}")
        for label, value in e["prefill"].items():
            k.admin.verify_field_value(label, value)
        k.admin_catalog.verify_variant_count(e["variantCount"])
        k.admin_catalog.verify_image_count(e["imageCount"])
        k.admin.fill_form(e["change"])
        k.admin_catalog.submit_product_form()
        k.common.verify_request("PUT", f"/admin/products/{e['id']}", e["payload"])
        k.common.verify_toast(e["toast"])
        k.common.verify_url("/admin/products")

    def test_edit_from_list_category_selected(self, k, request):
        """[ADC-PF-08] Bấm "Sửa" từ danh sách: danh mục được chọn sẵn"""
        known_bug(request, DATA["edit"]["fromListBug"])
        k.admin.open_admin_page("/admin/products", "Sản phẩm")
        k.admin_catalog.click_product_action(DATA["edit"]["product"], "Sửa")
        k.admin_catalog.verify_product_form_ready("Cập nhật")
        k.admin.verify_field_value("Danh mục", str(DATA["edit"]["prefill"]["Danh mục"]))

    def test_edit_from_list_keeps_details(self, k, request):
        """[ADC-PF-09] Bấm "Sửa" từ danh sách rồi lưu không làm mất mô tả/chất liệu/giới tính"""
        known_bug(request, DATA["edit"]["fromListBug"])
        e = DATA["edit"]
        k.common.mock_write("PUT", f"**/api/admin/products/{e['id']}", {"success": True})
        k.admin.open_admin_page("/admin/products", "Sản phẩm")
        k.admin_catalog.click_product_action(e["product"], "Sửa")
        k.admin_catalog.verify_product_form_ready("Cập nhật")
        k.admin.fill_form(e["change"])
        k.admin_catalog.submit_product_form()
        k.common.verify_request("PUT", f"/admin/products/{e['id']}", e["payload"])
