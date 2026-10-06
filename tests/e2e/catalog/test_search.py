# ============================================================
# TEST: TÌM KIẾM SẢN PHẨM (DATA-DRIVEN)
# Mục tiêu: gợi ý trên header, trang kết quả /search, trường hợp không có kết quả
# Dữ liệu: data/catalog/search.json (${product.name}, ${productFirstWord} lấy từ sản phẩm thật)
# API cần quan sát: k.catalog.type_search, submit_search, open_search_page, verify_search_*
# Kết quả mong đợi: gợi ý đúng sản phẩm; trang kết quả có tiêu đề + sản phẩm; chuỗi lạ -> rỗng
# ============================================================
import allure
import pytest

from utils.cases import case_params, case_title
from utils.data_loader import load_data, resolve_data

DATA = load_data("catalog/search.json")


class TestSearch:
    """Tìm kiếm sản phẩm (data-driven)"""

    @pytest.mark.parametrize("case", case_params(DATA["suggestions"]))
    def test_suggestion(self, k, ctx, case):
        allure.dynamic.title(f"Gợi ý: {case_title(case)}")
        c = resolve_data(case, ctx)
        k.catalog.open_home()
        k.catalog.type_search(c["keyword"])
        k.catalog.verify_search_suggestion(c["expectSuggestion"])
        k.catalog.click_search_suggestion(c["expectSuggestion"])
        k.catalog.verify_product_title(c["expectSuggestion"])

    @pytest.mark.parametrize("case", case_params(DATA["resultPage"]))
    def test_result_page(self, k, ctx, case):
        allure.dynamic.title(f"Trang kết quả: {case_title(case)}")
        c = resolve_data(case, ctx)
        k.catalog.open_home()
        k.catalog.submit_search(c["keyword"])
        k.catalog.verify_search_results(c["expectHeading"])

    @pytest.mark.parametrize("case", case_params(DATA["noResult"]))
    def test_no_result(self, k, case):
        allure.dynamic.title(f"Không có kết quả: {case_title(case)}")
        k.catalog.open_home()
        k.catalog.type_search(case["keyword"])
        k.catalog.verify_no_search_suggestion()
        k.catalog.open_search_page(case["keyword"])
        k.catalog.verify_no_search_results()
