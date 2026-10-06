# ============================================================
# TEST: API CÔNG KHAI - SẮP XẾP / BỘ LỌC / VALIDATE THAM SỐ (DATA-DRIVEN)
# Mục tiêu: /products sắp xếp đúng chiều, lọc đúng trường, phân trang không trùng,
#           tham số sai trả status + message đúng
# Dữ liệu: data/api/public.json (sorting, filters, validation)
# API cần quan sát: fixture api (get, list_products), case_params
# Kết quả mong đợi: khớp từng case; bug đã biết đánh dấu xfail(strict)
# ============================================================
import pytest
from playwright.sync_api import expect

from utils.cases import case_params, known_bug
from utils.data_loader import load_data

DATA = load_data("api/public.json")


class TestPublicSorting:
    """API công khai - sắp xếp (data-driven)"""

    @pytest.mark.parametrize("case", case_params(DATA["sorting"]))
    def test_sorting(self, api, case):
        """Sắp xếp sản phẩm theo giá (data-driven)"""
        res = api.get(f"/products?{case['query']}")
        expect(res).to_be_ok()
        prices = [float(p["price"]) for p in res.json()["data"]["products"]]
        expected = sorted(prices, reverse=case["order"] == "desc")
        assert prices == expected, f"Thứ tự giá ({case['order']}): expected={expected!r}, actual={prices!r}"


class TestPublicFilters:
    """API công khai - bộ lọc (data-driven)"""

    @pytest.mark.parametrize("case", case_params(DATA["filters"]))
    def test_filter(self, api, case):
        """Lọc sản phẩm theo trường (data-driven)"""
        res = api.get(f"/products?{case['query']}")
        expect(res).to_be_ok()
        products = res.json()["data"]["products"]
        if len(products) == 0:
            pytest.skip("Không có dữ liệu để kiểm tra bộ lọc")
        for p in products:
            assert p.get(case["field"]) == case["equals"], (
                f"{p.get('slug')}: {case['field']} expected={case['equals']!r}, actual={p.get(case['field'])!r}"
            )

    def test_paginate_all_pages_unique(self, api, request):
        """[API-PUB-P01] Duyệt hết các trang: đủ sản phẩm, không trùng"""
        known_bug(request, "ORDER BY created_at không có cột phụ (id) -> sản phẩm trùng/thiếu giữa các trang")
        limit = 5
        first = api.get(f"/products?limit={limit}&page=1").json()
        pagination = first["data"]["pagination"]
        total, total_pages = pagination["total"], pagination["total_pages"]
        seen = []
        for page in range(1, int(total_pages) + 1):
            seen.extend(p["id"] for p in api.list_products(limit=limit, page=page))
        unique = len(set(seen))
        assert unique == total, f"Thấy {unique}/{total} sản phẩm, {len(seen) - unique} bị trùng"


class TestPublicValidation:
    """API công khai - validate tham số (data-driven)"""

    @pytest.mark.parametrize("case", case_params(DATA["validation"]))
    def test_validation(self, api, case):
        """Validate tham số API công khai (data-driven)"""
        res = api.get(case["path"])
        assert res.status == case["status"], f"{case['path']}: expected={case['status']}, actual={res.status}"
        if case.get("message"):
            message = res.json().get("message")
            assert message == case["message"], f"message: expected={case['message']!r}, actual={message!r}"
