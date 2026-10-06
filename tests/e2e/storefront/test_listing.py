# ============================================================
# TEST: TRANG DANH SÁCH NAM / NỮ / TRẺ EM / GIẢM GIÁ
# Mục tiêu: bố cục, sắp xếp, trạng thái rỗng, lọc danh mục/màu/giá/giảm giá/size, phân trang,
#           nút trên thẻ sản phẩm
# Dữ liệu: data/storefront/listing.json (pages = thông tin từng trang, mockList = response cố định)
# API cần quan sát: k.listing.*, k.common.mock_get / verify_toast / verify_url, k.cart.verify_cart_badge
# Kết quả mong đợi: query gửi lên API (server) hoặc dòng "Hiển thị n trên t" (client) khớp dữ liệu
# ============================================================
import pytest

from utils.cases import case_params
from utils.data_loader import load_data

DATA = load_data("storefront/listing.json")


def listing_page(key):
    return DATA["pages"][key]


def mock_listing(k, p, product_list=None):
    """Mock API danh sách (và danh mục Trẻ em) của 1 trang bằng dữ liệu cố định."""
    k.common.mock_get(p["productsApi"], DATA["mockList"] if product_list is None else product_list)
    if p.get("categoriesApi"):
        k.common.mock_get(p["categoriesApi"], DATA["mockKidsCategories"])


def verify_filter_result(k, case):
    """Server: kiểm tra query gửi lên API; client: kiểm tra dòng "Hiển thị n trên t"."""
    if case.get("params"):
        k.listing.verify_list_request(case["params"])
    if case.get("countText"):
        k.listing.verify_count_text(case["countText"])


class TestListingLayout:
    """Trang danh sách: Nam / Nữ / Trẻ em / Giảm giá - Bố cục trang (dữ liệu thật)"""

    @pytest.mark.parametrize("case", case_params(DATA["layout"]))
    def test_layout(self, k, case):
        """Bố cục trang danh sách (data-driven)"""
        p = listing_page(case["page"])
        k.listing.open_listing(p["path"])
        k.listing.verify_listing_header(p["heading"], p["breadcrumb"], p["description"])
        k.listing.verify_count_matches_cards()
        k.listing.verify_sort_options(p["sortOptions"], p["defaultSort"])
        k.listing.verify_size_options(p["sizes"])
        k.listing.verify_color_options(p["colors"])
        k.listing.verify_price_inputs(p["priceDefault"]["from"], p["priceDefault"]["to"])
        k.common.verify_no_page_errors()

    @pytest.mark.parametrize("case", case_params([DATA["showMore"]]))
    def test_show_more_categories(self, k, case):
        """"Xem thêm +" hiện đủ danh mục"""
        p = listing_page(case["page"])
        k.listing.open_listing(p["path"])
        k.listing.verify_category_options(p["mockCategories"])
        k.listing.show_more_categories()
        k.listing.verify_category_options(case["categories"])


class TestListingSort:
    """Trang danh sách - Sắp xếp theo giá (dữ liệu thật)"""

    @pytest.mark.parametrize("case", case_params(DATA["sort"]))
    def test_sort_by_price(self, k, case):
        """Sắp xếp theo giá (data-driven)"""
        p = listing_page(case["page"])
        k.listing.open_listing(p["path"])
        k.listing.sort_by(case["option"])
        if p["mode"] == "server":
            k.listing.verify_list_request({"sort": "price", "order": case["order"]})
        k.listing.verify_prices_sorted(case["order"])


class TestListingEmpty:
    """Trang danh sách - Trạng thái rỗng (mock API)"""

    @pytest.mark.parametrize("case", case_params(DATA["empty"]))
    def test_empty_listing(self, k, case):
        """Trạng thái rỗng (data-driven)"""
        p = listing_page(case["page"])
        mock_listing(k, p, DATA["mockEmpty"])
        k.listing.open_listing(p["path"])
        k.listing.verify_empty_listing(p["emptyText"])


class TestListingCategoryFilter:
    """Trang danh sách - Lọc danh mục (mock API)"""

    @pytest.mark.parametrize("case", case_params(DATA["category"]))
    def test_filter_category(self, k, case):
        """Lọc danh mục (data-driven)"""
        p = listing_page(case["page"])
        mock_listing(k, p)
        k.listing.open_listing(p["path"])
        k.listing.verify_category_options(p["mockCategories"])
        k.listing.select_category(case["category"])
        verify_filter_result(k, case)


class TestListingColorFilter:
    """Trang danh sách - Lọc màu (mock API)"""

    @pytest.mark.parametrize("case", case_params(DATA["color"]))
    def test_filter_color(self, k, case):
        """Lọc màu (data-driven)"""
        p = listing_page(case["page"])
        mock_listing(k, p)
        k.listing.open_listing(p["path"])
        k.listing.select_color_filter(case["color"])
        verify_filter_result(k, case)


class TestListingPriceFilter:
    """Trang danh sách - Lọc khoảng giá (dữ liệu thật)"""

    @pytest.mark.parametrize("case", case_params(DATA["price"]))
    def test_filter_price(self, k, case):
        """Lọc khoảng giá (data-driven)"""
        p = listing_page(case["page"])
        k.listing.open_listing(p["path"])
        k.listing.set_price_range(case["from"], case["to"])
        verify_filter_result(k, case)
        k.listing.verify_prices_within(case["min"], case["max"])


class TestListingDiscountFilter:
    """Trang danh sách - Lọc phần trăm giảm (dữ liệu thật)"""

    @pytest.mark.parametrize("case", case_params(DATA["discount"]))
    def test_filter_discount(self, k, case):
        """Lọc phần trăm giảm (data-driven)"""
        p = listing_page(case["page"])
        k.listing.open_listing(p["path"])
        k.listing.select_discount(case["label"])
        verify_filter_result(k, case)
        k.listing.verify_discount_at_least(case["minPercent"])


class TestListingSizeFilter:
    """Trang danh sách - Lọc size (mock API)"""

    @pytest.mark.parametrize("case", case_params(DATA["size"]))
    def test_filter_size(self, k, case):
        """Lọc size (data-driven)"""
        p = listing_page(case["page"])
        mock_listing(k, p)
        k.listing.open_listing(p["path"])
        k.listing.select_size_filter(case["size"])
        verify_filter_result(k, case)
        k.listing.verify_products_shown()


class TestListingPaging:
    """Trang danh sách - Phân trang (mock API)"""

    @pytest.mark.parametrize("case", case_params(DATA["paging"]))
    def test_paging(self, k, case):
        """Phân trang (data-driven)"""
        p = listing_page(case["page"])
        mock_listing(k, p)
        k.listing.open_listing(p["path"])
        if case["via"] == "number":
            k.listing.go_to_page(2)
        if case["via"] == "next":
            k.listing.click_next_page()
        if case["via"] == "loadMore":
            k.listing.click_load_more()
        verify_filter_result(k, case)


class TestListingCardButtons:
    """Trang danh sách - Nút trên thẻ sản phẩm (dữ liệu thật)"""

    @pytest.mark.parametrize("case", case_params(DATA["overlayAdd"]))
    def test_overlay_add_to_cart(self, k, case):
        """Nút "Thêm vào giỏ" trên thẻ sản phẩm (data-driven)"""
        k.listing.open_listing(listing_page(case["page"])["path"])
        k.listing.add_first_card_to_cart()
        k.common.verify_toast(DATA["overlayToast"])
        k.listing.verify_opened_last_card()
        k.cart.verify_cart_badge(0)

    @pytest.mark.parametrize("case", case_params(DATA["overlayDetail"]))
    def test_overlay_view_detail(self, k, case):
        """Nút "Xem chi tiết" trên thẻ sản phẩm (data-driven)"""
        k.listing.open_listing(listing_page(case["page"])["path"])
        k.listing.view_first_card_detail()
        k.listing.verify_opened_last_card()

    @pytest.mark.parametrize("case", case_params(DATA["favorite"]))
    def test_favorite_button(self, k, case):
        """Nút yêu thích trên thẻ sản phẩm (data-driven)"""
        p = listing_page(case["page"])
        k.listing.open_listing(p["path"])
        k.listing.click_first_card_favorite()
        k.common.verify_url(p["path"])
