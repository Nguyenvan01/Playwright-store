# ============================================================
# TEST: CHI TIẾT SẢN PHẨM - PHẦN MỞ RỘNG
# Mục tiêu: breadcrumb, bộ ảnh, màu, SKU (clipboard), giá, accordion, dịch vụ, sản phẩm liên quan,
#           form đánh giá (validation, gửi thành công, lỗi server, hủy/đóng)
# Dữ liệu: data/storefront/product.json (mockProduct: 3 ảnh, 3 màu, có giá gốc,
#          1 sản phẩm liên quan là sản phẩm thật - ${product.*} lấy từ fixture ctx)
# API cần quan sát: k.product.*, k.catalog.verify_product_title, k.common.mock_write / verify_request
# Kết quả mong đợi: giao diện khớp dữ liệu mock; đánh giá gửi đúng body, không gửi khi lỗi validation
# ============================================================
import pytest

from utils.cases import case_params
from utils.data_loader import load_data, resolve_data

DATA = load_data("storefront/product.json")
E = DATA["expected"]


@pytest.fixture(autouse=True)
def mocked_product_page(k, ctx):
    """Trang chi tiết dùng dữ liệu mock cố định (3 ảnh, 3 màu, có giá gốc, 1 sản phẩm liên quan là sản phẩm thật)."""
    k.product.mock_product_detail(DATA["mockSlug"], resolve_data(DATA["mockProduct"], ctx))
    k.product.open_product_page(DATA["mockSlug"])
    k.catalog.verify_product_title(E["title"])


class TestProductExtras:
    """Chi tiết sản phẩm: ảnh, màu, SKU, giá, accordion"""

    @pytest.mark.smoke
    def test_breadcrumb_home(self, k):
        """[SF-PDP-01] Breadcrumb "Trang chủ | tên sản phẩm" quay về trang chủ"""
        k.product.verify_breadcrumb(E["title"])
        k.product.click_breadcrumb_home()
        k.common.verify_url("/")

    def test_gallery_thumbnails(self, k):
        """[SF-PDP-02] Bộ ảnh: thumbnail và bộ đếm ảnh"""
        k.product.verify_gallery(E["imageCount"])
        k.product.verify_current_image(1, E["imageCount"])
        k.product.click_thumbnail(3)
        k.product.verify_current_image(3, E["imageCount"])
        k.product.click_thumbnail(2)
        k.product.verify_current_image(2, E["imageCount"])

    def test_next_image_until_last(self, k):
        """[SF-PDP-03] Nút ảnh tiếp theo chuyển tới ảnh cuối rồi ẩn đi"""
        for i in range(2, E["imageCount"] + 1):
            k.product.click_next_image()
            k.product.verify_current_image(i, E["imageCount"])
        k.product.verify_next_image_hidden()

    def test_select_color(self, k):
        """[SF-PDP-04] Chọn màu đổi tên màu đang chọn"""
        k.product.verify_color_options(E["colors"])
        k.product.select_color(E["colors"][2])
        k.product.select_color(E["colors"][1])

    def test_discount_badge(self, k):
        """[SF-PDP-06] Có giá gốc gạch ngang và nhãn phần trăm giảm"""
        k.product.verify_discount_badge(E["discount"])

    @pytest.mark.parametrize("case", case_params([DATA["priceBug"]]))
    def test_price_format(self, k, case):
        """Giá bán và giá gốc hiển thị đúng định dạng "449.000đ\""""
        k.product.verify_price(case["expected"])
        k.product.verify_compare_price(E["comparePrice"], E["discount"])

    def test_accordion(self, k):
        """[SF-PDP-08] Accordion: mặc định mở "Mô tả", chỉ mở 1 mục mỗi lúc, bấm lại thì đóng"""
        k.product.verify_open_accordion("Mô tả", DATA["accordions"])
        k.product.verify_accordion_content("Mô tả", E["description"])
        k.product.toggle_accordion("Chất liệu")
        k.product.verify_open_accordion("Chất liệu", DATA["accordions"])
        k.product.verify_accordion_content("Chất liệu", E["materials"])
        k.product.toggle_accordion("Hướng dẫn sử dụng")
        k.product.verify_open_accordion("Hướng dẫn sử dụng", DATA["accordions"])
        k.product.verify_accordion_content("Hướng dẫn sử dụng", E["care"])
        k.product.toggle_accordion("Hướng dẫn sử dụng")
        k.product.verify_open_accordion("", DATA["accordions"])

    def test_services(self, k):
        """[SF-PDP-09] Danh sách dịch vụ: COD, miễn phí giao hàng, đổi hàng 30 ngày"""
        k.product.verify_services(E["services"])

    @pytest.mark.parametrize("case", case_params([DATA["shippingThresholdBug"]]))
    def test_shipping_threshold(self, k, case):
        """Ngưỡng miễn phí giao hàng khớp chính sách (500.000đ như /shipping và giỏ hàng)"""
        k.product.verify_service_text(case["service"], case["expected"])

    def test_related_product(self, k, ctx):
        """[SF-PDP-11] "SẢN PHẨM CÙNG PHONG CÁCH" mở trang chi tiết sản phẩm liên quan"""
        related = resolve_data(E["relatedName"], ctx)
        k.product.verify_related_product(related)
        k.product.open_related_product(related)
        k.common.verify_url_matches("/product/" + resolve_data("${product.slug}", ctx) + "$")
        k.catalog.verify_product_title(related)

    def test_review_login_prompt(self, k):
        """[SF-PDP-12] Khách chưa đăng nhập chỉ thấy lời nhắc đăng nhập để đánh giá"""
        k.product.verify_review_login_prompt()
        k.product.click_review_login()
        k.common.verify_url("/login")


class TestProductClipboard:
    """Chi tiết sản phẩm: ảnh, màu, SKU, giá, accordion - Quyền clipboard"""

    @pytest.fixture
    def browser_context_args(self, browser_context_args):
        return {**browser_context_args, "permissions": ["clipboard-read", "clipboard-write"]}

    def test_copy_sku(self, k):
        """[SF-PDP-05] Copy SKU -> "Đã copy", clipboard chứa SKU, 2 giây sau trở lại "Copy\""""
        k.product.verify_sku(E["sku"])
        k.product.copy_sku()
        k.product.verify_sku_copied(E["sku"])


@pytest.mark.role("customer")
class TestProductReviews:
    """Chi tiết sản phẩm: đánh giá (đã đăng nhập)"""

    @pytest.fixture(autouse=True)
    def review_form(self, k):
        k.common.mock_write(
            "POST", "**/api/reviews", {"success": True, "message": DATA["reviewSuccess"]["message"]}
        )
        k.product.open_review_form()

    @pytest.mark.parametrize("case", case_params(DATA["reviewValidation"]))
    def test_review_validation(self, k, case):
        """Validation form đánh giá (data-driven)"""
        k.product.fill_review(case["stars"], case["content"])
        k.product.submit_review()
        k.product.verify_review_errors(case["errors"])
        k.common.verify_no_request("POST", "/api/reviews")

    @pytest.mark.parametrize("case", case_params([DATA["reviewSuccess"]]))
    def test_review_success(self, k, case):
        """Gửi đánh giá hợp lệ (mock API) -> toast từ server, form đóng"""
        k.product.fill_review(case["stars"], case["content"])
        k.product.submit_review()
        k.common.verify_toast(case["message"])
        k.common.verify_request(
            "POST",
            "/api/reviews",
            {
                "product_id": DATA["mockProduct"]["data"]["id"],
                "rating": case["stars"],
                "content": case["content"],
            },
        )
        k.product.verify_review_form_closed()

    @pytest.mark.parametrize("case", case_params(DATA["reviewServerErrors"]))
    def test_review_server_error(self, k, case):
        """Server trả lỗi khi gửi đánh giá (data-driven)"""
        k.common.mock_write(
            "POST", "**/api/reviews", {"success": False, "message": case["message"]}, case["status"]
        )
        k.product.fill_review(case["stars"], case["content"])
        k.product.submit_review()
        k.common.verify_request(
            "POST", "/api/reviews", {"rating": case["stars"], "content": case["content"]}
        )
        k.common.verify_toast(case["toast"])

    def test_cancel_review(self, k):
        """[SF-PDP-22] Bấm "Hủy" đóng form đánh giá, không gửi request"""
        k.product.fill_review(4, "Đang viết dở")
        k.product.cancel_review()
        k.product.verify_review_form_closed()
        k.common.verify_no_request("POST", "/api/reviews")

    def test_close_review_clears_errors(self, k):
        """[SF-PDP-23] Bấm "×" đóng form và xóa thông báo lỗi"""
        k.product.submit_review()
        k.product.verify_review_errors(
            ["Vui lòng chọn số sao đánh giá.", "Vui lòng nhập nội dung đánh giá."]
        )
        k.product.close_review_form()
        k.product.verify_review_form_closed()
        k.product.open_review_form()
        k.product.verify_review_errors([])
