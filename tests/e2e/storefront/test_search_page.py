# ============================================================
# TEST: TRANG KẾT QUẢ /search
# Mục tiêu: tiêu đề, breadcrumb, chip theo tham số; sắp xếp giá; rỗng / lỗi; phân trang;
#           gõ 1 ký tự ở header (API gợi ý 400)
# Dữ liệu: data/storefront/search-page.json (+ mockList trong data/storefront/listing.json)
# API cần quan sát: k.listing.*search*, k.common.mock_get / verify_url, k.catalog.open_home / submit_search
# Kết quả mong đợi: trang /search hiển thị đúng theo tham số; API được gọi với đúng query
# ============================================================
import pytest

from utils.cases import case_params
from utils.data_loader import load_data, resolve_data

DATA = load_data("storefront/search-page.json")
LISTING = load_data("storefront/listing.json")


class TestSearchTitles:
    """Trang kết quả /search - Tiêu đề, breadcrumb, chip theo tham số (dữ liệu thật)"""

    @pytest.mark.parametrize("case", case_params(DATA["titles"]))
    def test_title_breadcrumb_chips(self, k, ctx, case):
        """Tiêu đề, breadcrumb, chip theo tham số (data-driven)"""
        c = resolve_data(case, ctx)
        k.listing.open_search_results(c["query"])
        k.listing.verify_search_title(c["heading"])
        k.listing.verify_search_breadcrumbs(c["breadcrumbs"])
        for name, href in c.get("breadcrumbLinks") or []:
            k.listing.verify_search_breadcrumb_link(name, href)
        k.listing.verify_search_subtitle_matches()
        k.listing.verify_search_sort_options(DATA["sortOptions"])
        for chip in c.get("chips") or []:
            k.listing.verify_search_chip(chip["text"], chip["closeHref"])

    @pytest.mark.parametrize("case", case_params([DATA["closeChip"]]))
    def test_close_chip(self, k, case):
        """Bỏ chip Danh mục quay về "Tất cả sản phẩm\""""
        k.listing.open_search_results(case["query"])
        k.listing.close_search_chip(case["chip"])
        k.common.verify_url("/search")
        k.listing.verify_search_title(case["heading"])


class TestSearchSort:
    """Trang kết quả /search - Sắp xếp theo giá (dữ liệu thật)"""

    @pytest.mark.parametrize("case", case_params(DATA["sort"]))
    def test_sort_by_price(self, k, case):
        """Sắp xếp theo giá (data-driven)"""
        k.listing.open_search_results(case["query"])
        k.listing.sort_search_by(case["option"])
        k.listing.verify_list_request({"sort": "price", "order": case["order"]})
        k.listing.verify_search_prices_sorted(case["order"])


class TestSearchEmptyAndError:
    """Trang kết quả /search - Không có kết quả / lỗi"""

    @pytest.mark.parametrize("case", case_params(DATA["empty"]))
    def test_empty_results(self, k, case):
        """Không có kết quả (data-driven)"""
        k.listing.open_search_results(case["query"])
        k.listing.verify_search_empty(case["hint"])
        k.listing.click_view_all_products()
        k.common.verify_url("/search")
        k.listing.verify_search_title("Tất cả sản phẩm")

    @pytest.mark.parametrize("case", case_params([DATA["error"]]))
    def test_api_error(self, k, case):
        """API lỗi 500: hiển thị "Đã xảy ra lỗi" và nút Thử lại (mock)"""
        k.common.mock_get("**/api/products?**", {"success": False, "message": "Lỗi server"}, 500)
        k.listing.open_search_results("?q=ao")
        k.listing.verify_search_error(case["message"])


class TestSearchPaging:
    """Trang kết quả /search - Phân trang (mock)"""

    @pytest.mark.parametrize("case", case_params(DATA["paging"]))
    def test_paging(self, k, case):
        """Phân trang /search (data-driven)"""
        mock_list = LISTING["mockList"]
        k.common.mock_get(
            "**/api/products?**",
            {**mock_list, "data": {**mock_list["data"], "pagination": DATA["mockPagination"]}},
        )
        k.listing.open_search_results("")
        k.listing.verify_search_active_page(1)
        if case["via"] == "number":
            k.listing.go_to_search_page(2)
        else:
            k.listing.click_search_next_page()
        k.listing.verify_list_request({"page": "2", "limit": "12"})
        k.listing.verify_search_active_page(2)


class TestSearchShortQuery:
    """Trang kết quả /search - từ khóa 1 ký tự"""

    @pytest.mark.parametrize("case", case_params([DATA["shortQuery"]]))
    def test_short_query(self, k, case):
        """Gõ 1 ký tự: API gợi ý trả 400 nên không hiện dropdown, Enter vẫn ra trang kết quả có sản phẩm"""
        k.catalog.open_home()
        k.listing.type_header_search_expecting_status(case["keyword"], 400)
        k.listing.verify_header_suggestions_hidden()
        k.catalog.submit_search(case["keyword"])
        k.listing.verify_search_title(f'Kết quả tìm kiếm: "{case["keyword"]}"')
        k.listing.verify_search_subtitle_matches()
