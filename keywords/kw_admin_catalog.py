# THƯ VIỆN KEYWORD - NHÓM adminCatalog: quản trị danh mục hàng (sản phẩm, form sản phẩm, danh mục, thương hiệu).
import base64
import json
import math
import re
from urllib.parse import urlparse

from playwright.sync_api import expect

from keywords.base_keywords import BaseKeywords, keyword
from pages.admin.catalog.product_form_page import ProductFormPage
from pages.admin.catalog.products_list_page import ProductsListPage
from pages.admin.catalog.taxonomy_page import TaxonomyPage
from pages.admin.sales.admin_api_mock import AdminRequestLog, fulfill_get, includes_ci, query_of
from utils.assertions import poll_until
from utils.storage import STORAGE_KEYS

PRODUCTS_PAGE_SIZE = 10
# Ảnh PNG 1x1 dùng cho test tải ảnh lên (không cần file trên đĩa).
PNG_1X1 = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+ip1sAAAAASUVORK5CYII="
)
# Chưa thấy request upload (khác None = request không có header Authorization).
_UNSET = object()

ACTIVE_CLASS = re.compile(r"text-green-500")
INACTIVE_CLASS = re.compile(r"text-gray-300")
SELECTED_CLASS = re.compile(r"bg-\[#d71920\]")


class AdminCatalogKeywords(BaseKeywords):
    group = "adminCatalog"

    def __init__(self, page, po, api, common=None):
        super().__init__(page, po, api, common)
        self.list = ProductsListPage(page)
        self.form = ProductFormPage(page)
        self.taxonomy = TaxonomyPage(page)
        self.requests = AdminRequestLog(page)
        self._upload_authorization = _UNSET

    # ===========================================================================
    # Mock dữ liệu đọc (GET) - KHÔNG chặn request ghi
    # ===========================================================================

    @keyword("mockCatalogApi")
    def mock_catalog_api(self, fixture):
        """Mock GET /admin/products (lọc search/category/brand), /admin/products/:id, /admin/categories, /admin/brands."""
        parts = ", ".join(fixture)
        with self.step(f"Mock API danh mục hàng ({parts})"):
            if fixture.get("categories") is not None:
                categories = fixture["categories"]
                self.page.route(
                    re.compile(r"/api/admin/categories(?:\?.*)?$"),
                    lambda route: fulfill_get(route, lambda: {"categories": categories}),
                )
            if fixture.get("brands") is not None:
                brands = fixture["brands"]
                self.page.route(
                    re.compile(r"/api/admin/brands(?:\?.*)?$"),
                    lambda route: fulfill_get(route, lambda: {"brands": brands}),
                )
            if fixture.get("products") is not None:
                products = fixture["products"]
                details = fixture.get("productDetails") or {}

                def handle(route):
                    match = re.search(r"products/(\d+)$", urlparse(route.request.url).path)
                    if match:
                        product_id = match.group(1)
                        product = next((p for p in products if str(p["id"]) == product_id), None)
                        if not product:
                            return fulfill_get(route, lambda: {"success": False, "message": "Không tìm thấy"}, 404)
                        return fulfill_get(route, lambda: {"product": {**product, **details.get(product_id, {})}})
                    q = query_of(route)
                    search = q.get("search") or ""
                    filtered = [
                        p
                        for p in products
                        if (not search or includes_ci(p.get("name"), search) or includes_ci(p.get("sku"), search))
                        and (not q.get("category") or str(p.get("category_id")) == q.get("category"))
                        and (not q.get("brand") or str(p.get("brand_id")) == q.get("brand"))
                    ]
                    total = fixture.get("productsTotal")
                    total = len(filtered) if total is None else total
                    return fulfill_get(
                        route,
                        lambda: {
                            "products": filtered,
                            "total": total,
                            "totalPages": math.ceil(total / PRODUCTS_PAGE_SIZE),
                            "page": int(q.get("page") or 1),
                        },
                    )

                self.page.route(re.compile(r"/api/admin/products(?:/(\d+))?(?:\?.*)?$"), handle)

    @keyword("verifyApiRequested")
    def verify_api_requested(self, path, params=None):
        """Kiểm tra trình duyệt đã gọi GET tới đường dẫn (vd: "/admin/products") với đủ tham số query."""
        params = params or {}
        shown = json.dumps(params, ensure_ascii=False)
        with self.step(f"Kiểm tra đã gọi GET {path} {shown}"):
            try:
                poll_until(lambda: self.requests.has(path, params), "")
            except AssertionError:
                raise AssertionError(
                    f"Không thấy GET {path} với {shown}. Đã gọi: {self.requests.describe()}"
                ) from None

    @keyword("verifyColumns")
    def verify_columns(self, headers):
        """Kiểm tra tiêu đề cột bảng theo nội dung gốc (bỏ qua CSS uppercase), đúng thứ tự."""
        with self.step(f"Kiểm tra cột bảng: {' | '.join(headers)}"):
            ths = self.page.locator("main table").first.locator("thead th")
            expect(ths.first).to_be_visible()
            texts = [t.strip() for t in ths.all_text_contents() if t.strip()]
            assert texts == headers, f"Cột bảng: expected={headers!r}, actual={texts!r}"

    # ===========================================================================
    # Danh sách sản phẩm
    # ===========================================================================

    @keyword("verifyProductCountAtLeast")
    def verify_product_count_at_least(self, minimum):
        """Kiểm tra bảng sản phẩm có ít nhất `min` dòng dữ liệu."""
        with self.step(f"Kiểm tra có >= {minimum} sản phẩm"):
            expect(self.list.data_rows.first).to_be_visible()
            count = self.list.data_rows.count()
            assert count >= minimum, f"Số sản phẩm: expected>={minimum}, actual={count}"

    @keyword("verifyProductRows")
    def verify_product_rows(self, rows):
        """Kiểm tra từng dòng sản phẩm: thương hiệu, SKU, danh mục, giá, tồn kho (đỏ khi <= 5), đã bán, nổi bật, trạng thái."""
        with self.step(f"Kiểm tra {len(rows)} dòng sản phẩm"):
            expect(self.list.data_rows).to_have_count(len(rows))
            for r in rows:
                name = r["name"]
                expect(self.list.cell(name, 1), name).to_contain_text(r["brand"])
                expect(self.list.cell(name, 2), name).to_have_text(r["sku"])
                expect(self.list.cell(name, 3), name).to_have_text(r["category"])
                expect(self.list.cell(name, 4), name).to_have_text(r["price"])
                expect(self.list.cell(name, 5), name).to_have_text(r["stock"])
                expect(self.list.cell(name, 5).locator("span"), name).to_have_class(
                    re.compile(r"text-red-600") if r.get("lowStock") else re.compile(r"text-gray-700")
                )
                expect(self.list.cell(name, 6), name).to_have_text(r["sold"])
                expect(self.list.featured_button(name), name).to_have_attribute(
                    "title", "Bỏ nổi bật" if r.get("featured") else "Đánh dấu nổi bật"
                )
                expect(self.list.status_button(name), name).to_have_class(
                    ACTIVE_CLASS if r.get("active") else INACTIVE_CLASS
                )

    @keyword("verifyProductListed")
    def verify_product_listed(self, name, visible=True):
        """Kiểm tra có/không có dòng sản phẩm theo tên chính xác."""
        with self.step(f"Kiểm tra {'có' if visible else 'không có'} sản phẩm \"{name}\""):
            if visible:
                expect(self.list.row(name)).to_be_visible()
            else:
                expect(self.list.rows(name)).to_have_count(0)

    @keyword("searchProducts")
    def search_products(self, text):
        """Gõ từ khóa vào ô tìm sản phẩm."""
        with self.step(f'Tìm sản phẩm "{text}"'):
            self.list.search_input.fill(text)

    @keyword("filterProductsByCategory")
    def filter_products_by_category(self, label):
        """Chọn lọc danh mục theo tên hiển thị."""
        with self.step(f'Lọc danh mục "{label}"'):
            self.list.category_select.select_option(label=label)

    @keyword("filterProductsByBrand")
    def filter_products_by_brand(self, label):
        """Chọn lọc thương hiệu theo tên hiển thị."""
        with self.step(f'Lọc thương hiệu "{label}"'):
            self.list.brand_select.select_option(label=label)

    @keyword("clickProductFeatured")
    def click_product_featured(self, name):
        """Bấm nút ngôi sao (nổi bật) trên dòng sản phẩm."""
        with self.step(f'Bấm ngôi sao nổi bật của "{name}"'):
            self.list.featured_button(name).click()

    @keyword("verifyProductFeaturedTitle")
    def verify_product_featured_title(self, name, title):
        """Kiểm tra title nút ngôi sao: "Đánh dấu nổi bật" (chưa nổi bật) hoặc "Bỏ nổi bật"."""
        with self.step(f'Kiểm tra ngôi sao của "{name}" = "{title}"'):
            expect(self.list.featured_button(name)).to_have_attribute("title", title)

    @keyword("clickProductStatus")
    def click_product_status(self, name):
        """Bấm nút gạt trạng thái bán trên dòng sản phẩm."""
        with self.step(f'Bấm gạt trạng thái của "{name}"'):
            self.list.status_button(name).click()

    @keyword("verifyProductActive")
    def verify_product_active(self, name, active):
        """Kiểm tra nút gạt trạng thái bán đang bật (xanh) hay tắt (xám)."""
        with self.step(f"Kiểm tra \"{name}\" {'đang bán' if active else 'ngừng bán'}"):
            expect(self.list.status_button(name)).to_have_class(ACTIVE_CLASS if active else INACTIVE_CLASS)

    @keyword("clickProductAction")
    def click_product_action(self, name, title):
        """Bấm nút hành động "Xem" / "Sửa" / "Xóa" trên dòng sản phẩm."""
        with self.step(f'Sản phẩm "{name}" -> "{title}"'):
            self.list.action(name, title).click()

    @keyword("verifyProductViewLink")
    def verify_product_view_link(self, name, href):
        """Kiểm tra link "Xem" của sản phẩm trỏ tới trang chi tiết ngoài cửa hàng."""
        with self.step(f'Kiểm tra link "Xem" của "{name}" = {href}'):
            expect(self.list.action(name, "Xem")).to_have_attribute("href", href)

    @keyword("verifyDeleteProductModal")
    def verify_delete_product_modal(self, heading, message):
        """Kiểm tra modal xóa sản phẩm đang mở với tiêu đề + nội dung cảnh báo."""
        with self.step(f'Kiểm tra modal "{heading}"'):
            expect(self.list.delete_modal).to_be_visible()
            expect(self.list.delete_modal.get_by_text(message, exact=True)).to_be_visible()

    @keyword("selectProducts")
    def select_products(self, names):
        """Tích chọn các dòng sản phẩm theo tên."""
        with self.step(f"Chọn sản phẩm: {', '.join(names)}"):
            for name in names:
                self.list.row_checkbox(name).check()

    @keyword("selectAllProducts")
    def select_all_products(self):
        """Tích ô chọn tất cả trên đầu bảng sản phẩm."""
        with self.step("Chọn tất cả sản phẩm"):
            self.list.header_checkbox.check()

    @keyword("verifyBulkSelection")
    def verify_bulk_selection(self, text):
        """Kiểm tra thanh thao tác hàng loạt "{n} sản phẩm được chọn" (null = ẩn)."""
        with self.step(f"Kiểm tra thanh chọn hàng loạt = {'(ẩn)' if text is None else text}"):
            if text is None:
                expect(self.list.bulk_bar_text).to_have_count(0)
            else:
                expect(self.list.bulk_bar_text).to_have_text(text)
                expect(self.list.bulk_delete_button).to_be_visible()

    @keyword("clickBulkDelete")
    def click_bulk_delete(self):
        """Bấm "Xóa đã chọn" trên thanh thao tác hàng loạt."""
        with self.step('Bấm "Xóa đã chọn"'):
            self.list.bulk_delete_button.click()

    @keyword("verifyProductsPagination")
    def verify_products_pagination(self, text):
        """Kiểm tra dòng phân trang sản phẩm, vd: "Trang 1 trên 3" (null = không có phân trang)."""
        with self.step(f"Kiểm tra phân trang sản phẩm = {'(không có)' if text is None else text}"):
            if text is None:
                expect(self.list.pagination_text).to_have_count(0)
            else:
                expect(self.list.pagination_text).to_have_text(text)

    @keyword("verifyProductsPaginationFirstPage")
    def verify_products_pagination_first_page(self):
        """Kiểm tra dòng phân trang sản phẩm khớp mẫu "Trang 1 trên N"."""
        with self.step('Kiểm tra phân trang "Trang 1 trên N"'):
            expect(self.list.pagination_text).to_have_text(re.compile(r"^Trang 1 trên \d+$"))

    @keyword("goToProductsPage")
    def go_to_products_page(self, n):
        """Bấm số trang trên phân trang sản phẩm."""
        with self.step(f"Bấm trang sản phẩm {n}"):
            self.list.page_button(n).click()

    @keyword("clickAddProduct")
    def click_add_product(self):
        """Bấm "Thêm sản phẩm" trên trang danh sách."""
        with self.step('Bấm "Thêm sản phẩm"'):
            self.list.add_link.click()

    # ===========================================================================
    # Form sản phẩm
    # ===========================================================================

    @keyword("verifyProductFormReady")
    def verify_product_form_ready(self, submit_label):
        """Chờ form sản phẩm tải xong (hết "Đang tải dữ liệu...") và kiểm tra nhãn nút lưu."""
        with self.step(f'Kiểm tra form sản phẩm sẵn sàng (nút "{submit_label}")'):
            expect(self.form.loading_text).to_have_count(0)
            expect(self.form.submit_button).to_have_text(submit_label)

    @keyword("submitProductForm")
    def submit_product_form(self):
        """Bấm nút lưu form sản phẩm ("Tạo sản phẩm" / "Cập nhật")."""
        with self.step("Bấm lưu form sản phẩm"):
            self.form.submit_button.click()

    @keyword("verifyProductFormError")
    def verify_product_form_error(self, text):
        """Kiểm tra hộp lỗi đỏ trên form sản phẩm."""
        with self.step(f'Kiểm tra lỗi form sản phẩm "{text}"'):
            expect(self.form.error_box).to_have_text(text)

    @keyword("clickBackToProducts")
    def click_back_to_products(self):
        """Bấm "Quay lại" trên form sản phẩm."""
        with self.step('Bấm "Quay lại"'):
            self.form.back_button.click()

    @keyword("toggleVariantBuilder")
    def toggle_variant_builder(self):
        """Bấm "+ Tạo biến thể" / "Tắt chế độ" trong khối Biến thể."""
        with self.step("Bật/tắt chế độ tạo biến thể"):
            self.form.variant_toggle.click()

    @keyword("verifyVariantToggleLabel")
    def verify_variant_toggle_label(self, label):
        """Kiểm tra nhãn nút bật/tắt chế độ tạo biến thể."""
        with self.step(f'Kiểm tra nút biến thể = "{label}"'):
            expect(self.form.variant_toggle).to_have_text(label)

    @keyword("selectVariantSizes")
    def select_variant_sizes(self, sizes):
        """Chọn các size trong chế độ tạo biến thể (vd: ["S", "M"])."""
        with self.step(f"Chọn size: {', '.join(sizes)}"):
            for size in sizes:
                self.form.size_button(size).click()
                expect(self.form.size_button(size)).to_have_class(SELECTED_CLASS)

    @keyword("selectVariantColors")
    def select_variant_colors(self, colors):
        """Chọn các màu trong chế độ tạo biến thể (vd: ["Đen", "Trắng"])."""
        with self.step(f"Chọn màu: {', '.join(colors)}"):
            for color in colors:
                self.form.color_button(color).click()
                expect(self.form.color_button(color)).to_have_class(SELECTED_CLASS)

    @keyword("verifyGenerateVariantsButton")
    def verify_generate_variants_button(self, label, enabled):
        """Kiểm tra nút "Tạo {n} biến thể" (nhãn + bật/tắt)."""
        with self.step(f"Kiểm tra nút \"{label}\" {'bật' if enabled else 'bị khóa'}"):
            expect(self.form.generate_button).to_have_text(label)
            if enabled:
                expect(self.form.generate_button).to_be_enabled()
            else:
                expect(self.form.generate_button).to_be_disabled()

    @keyword("generateVariants")
    def generate_variants(self):
        """Bấm "Tạo {n} biến thể"."""
        with self.step("Bấm tạo biến thể"):
            self.form.generate_button.click()

    @keyword("verifyVariantRows")
    def verify_variant_rows(self, rows):
        """Kiểm tra lưới biến thể: size, màu, SKU từng dòng (đúng thứ tự)."""
        with self.step(f"Kiểm tra {len(rows)} biến thể"):
            expect(self.form.variant_rows).to_have_count(len(rows))
            for i, r in enumerate(rows):
                expect(self.form.variant_cell(i, "size")).to_have_text(r["size"])
                expect(self.form.variant_cell(i, "color")).to_have_text(r["color"])
                expect(self.form.variant_sku(i)).to_have_value(r["sku"])

    @keyword("verifyVariantCount")
    def verify_variant_count(self, count):
        """Kiểm tra số dòng biến thể."""
        with self.step(f"Kiểm tra có {count} biến thể"):
            expect(self.form.variant_rows).to_have_count(count)

    @keyword("removeVariant")
    def remove_variant(self, index):
        """Xóa dòng biến thể thứ `index` (bắt đầu từ 0)."""
        with self.step(f"Xóa biến thể #{index + 1}"):
            self.form.variant_remove(index).click()

    @keyword("addImageUrl")
    def add_image_url(self, url):
        """Dán URL ảnh vào ô "Dán URL ảnh..." và nhấn Enter."""
        with self.step(f"Thêm ảnh từ URL {url}"):
            self.form.image_url_input.fill(url)
            self.form.image_url_input.press("Enter")

    @keyword("verifyImageCount")
    def verify_image_count(self, count):
        """Kiểm tra số ảnh trong khối Hình ảnh và nhãn "Ảnh chính" (ảnh đầu tiên)."""
        with self.step(f"Kiểm tra có {count} ảnh"):
            expect(self.form.image_tiles).to_have_count(count)
            expect(self.form.main_image_badge).to_have_count(1 if count > 0 else 0)

    @keyword("removeImage")
    def remove_image(self, index):
        """Rê chuột vào ảnh thứ `index` và bấm nút X để xóa."""
        with self.step(f"Xóa ảnh #{index + 1}"):
            self.form.image_tiles.nth(index).hover()
            self.form.image_remove(index).click()

    @keyword("uploadProductImage")
    def upload_product_image(self, file_name, response):
        """Mock POST /api/admin/upload (ghi lại header Authorization) rồi chọn 1 ảnh PNG để tải lên."""
        with self.step(f'Tải ảnh "{file_name}" lên (mock upload)'):
            self._upload_authorization = _UNSET

            def handle(route):
                if route.request.method != "POST":
                    return route.fallback()
                self._upload_authorization = route.request.all_headers().get("authorization")
                route.fulfill(status=200, json=response)

            self.page.route("**/api/admin/upload", handle)
            self.form.file_input.set_input_files(
                {"name": file_name, "mimeType": "image/png", "buffer": PNG_1X1}
            )

    @keyword("verifyUploadUsedAdminToken")
    def verify_upload_used_admin_token(self):
        """Kiểm tra request tải ảnh gửi đúng token admin (Bearer + admin_token trong localStorage)."""
        with self.step("Kiểm tra upload gửi token admin"):
            poll_until(lambda: self._upload_authorization is not _UNSET, "Chưa thấy request upload")
            token = self.page.evaluate("k => localStorage.getItem(k)", STORAGE_KEYS["adminToken"])
            assert token, "Không có admin_token trong localStorage"
            actual = self._upload_authorization
            assert actual == f"Bearer {token}", (
                f"Header Authorization của upload không phải token admin: "
                f"expected='Bearer <admin_token>', actual={actual!r}"
            )

    # ===========================================================================
    # Danh mục / Thương hiệu (lưới thẻ)
    # ===========================================================================

    @keyword("verifyCardCountAtLeast")
    def verify_card_count_at_least(self, minimum):
        """Kiểm tra có ít nhất `min` thẻ (danh mục / thương hiệu)."""
        with self.step(f"Kiểm tra có >= {minimum} thẻ"):
            expect(self.taxonomy.card_names.first).to_be_visible()
            count = self.taxonomy.card_names.count()
            assert count >= minimum, f"Số thẻ: expected>={minimum}, actual={count}"

    @keyword("verifyCards")
    def verify_cards(self, visible, hidden=None):
        """Kiểm tra các thẻ hiển thị (`visible`) và không hiển thị (`hidden`) theo tên."""
        hidden = hidden or []
        with self.step(f"Kiểm tra thẻ hiện: {', '.join(visible) or '-'} | ẩn: {', '.join(hidden) or '-'}"):
            for name in visible:
                expect(self.taxonomy.card(name), name).to_be_visible()
            for name in hidden:
                expect(self.taxonomy.card(name), name).to_have_count(0)

    @keyword("verifyCardsEmpty")
    def verify_cards_empty(self, text):
        """Kiểm tra lưới thẻ trống với thông báo, vd: "Không tìm thấy danh mục"."""
        with self.step(f'Kiểm tra "{text}"'):
            expect(self.page.get_by_text(text, exact=True)).to_be_visible()
            expect(self.taxonomy.cards).to_have_count(0)

    @keyword("clickCardEdit")
    def click_card_edit(self, name):
        """Rê chuột vào thẻ rồi bấm icon Sửa (icon ẩn tới khi hover, không có tên)."""
        with self.step(f'Thẻ "{name}" -> Sửa'):
            self.taxonomy.card(name).hover()
            self.taxonomy.edit_button(name).click()

    @keyword("clickCardDelete")
    def click_card_delete(self, name):
        """Rê chuột vào thẻ rồi bấm icon Xóa (icon ẩn tới khi hover, không có tên)."""
        with self.step(f'Thẻ "{name}" -> Xóa'):
            self.taxonomy.card(name).hover()
            self.taxonomy.delete_button(name).click()

    @keyword("clickCardToggle")
    def click_card_toggle(self, name):
        """Bấm nút gạt Hoạt động trên thẻ."""
        with self.step(f'Thẻ "{name}" -> gạt Hoạt động'):
            self.taxonomy.toggle_button(name).click()

    @keyword("verifyCardActive")
    def verify_card_active(self, name, active):
        """Kiểm tra nút gạt Hoạt động trên thẻ đang bật (xanh) hay tắt (xám)."""
        with self.step(f"Kiểm tra thẻ \"{name}\" {'đang hoạt động' if active else 'tắt'}"):
            expect(self.taxonomy.toggle_button(name)).to_have_class(ACTIVE_CLASS if active else INACTIVE_CLASS)

    @keyword("verifyCardFeatured")
    def verify_card_featured(self, name, featured):
        """Kiểm tra thẻ có/không có nhãn "Nổi bật"."""
        with self.step(f"Kiểm tra thẻ \"{name}\" {'có' if featured else 'không có'} nhãn \"Nổi bật\""):
            expect(self.taxonomy.card(name)).to_be_visible()
            if featured:
                expect(self.taxonomy.featured_badge(name)).to_be_visible()
            else:
                expect(self.taxonomy.featured_badge(name)).to_have_count(0)

    @keyword("verifyCardDetails")
    def verify_card_details(self, name, slug, description=None):
        """Kiểm tra slug (/{slug}) và mô tả hiển thị trên thẻ."""
        with self.step(f'Kiểm tra thẻ "{name}" có slug /{slug}'):
            expect(self.taxonomy.slug(name)).to_have_text(f"/{slug}")
            if description:
                expect(self.taxonomy.card(name)).to_contain_text(description)

    @keyword("verifyDeleteConfirmMessage")
    def verify_delete_confirm_message(self, message):
        """Kiểm tra nội dung modal "Xác nhận xóa"."""
        with self.step(f'Kiểm tra modal xác nhận xóa: "{message}"'):
            expect(self.taxonomy.delete_modal).to_be_visible()
            expect(self.taxonomy.delete_message).to_have_text(message)
