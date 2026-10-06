# ============================================================
# TEST: API - SẢN PHẨM
# Mục tiêu: danh sách + phân trang, chi tiết, 404, tìm kiếm, kids, gợi ý, tin tức
# Dữ liệu: sản phẩm thật lấy qua API (bỏ qua nếu DB trống)
# API cần quan sát: fixture api (get, list_products, get_product)
# Kết quả mong đợi: status/shape đúng; /products/suggested đang lỗi (bug đã biết)
# ============================================================
from urllib.parse import quote

import pytest
from playwright.sync_api import expect

from utils.assertions import assert_subset
from utils.cases import known_bug


class TestProductsApi:
    """API - Sản phẩm"""

    def test_list_with_pagination(self, api):
        """GET /products trả danh sách + phân trang"""
        res = api.get("/products?limit=5&page=1")
        expect(res).to_be_ok()
        body = res.json()
        data = body["data"]

        assert body["success"] is True, f"success: expected=True, actual={body.get('success')!r}"
        assert len(data["products"]) <= 5, f"Số sản phẩm: expected<=5, actual={len(data['products'])}"
        assert_subset(data["pagination"], {"page": 1, "limit": 5}, "pagination")
        for p in data["products"]:
            assert p.get("id") is not None, f"Sản phẩm thiếu id: {p!r}"
            assert isinstance(p.get("name"), str), f"name phải là chuỗi: {p!r}"
            assert isinstance(p.get("slug"), str), f"slug phải là chuỗi: {p!r}"

    def test_detail_has_sizes_colors_variants(self, api):
        """GET /products/:slug trả chi tiết có sizes/colors/variants"""
        products = api.list_products(limit=1)
        if not products:
            pytest.skip("DB chưa có sản phẩm")
        first = products[0]

        detail = api.get_product(first["slug"])
        assert detail["slug"] == first["slug"], f"slug: expected={first['slug']!r}, actual={detail['slug']!r}"
        for key in ("sizes", "colors", "variants"):
            assert isinstance(detail.get(key), list), f"{key}: expected=list, actual={detail.get(key)!r}"

    def test_detail_not_found(self, api):
        """GET /products/:slug không tồn tại trả 404"""
        res = api.get("/products/san-pham-khong-ton-tai-e2e-999")
        assert res.status == 404, f"expected=404, actual={res.status}"

    def test_search_by_keyword(self, api):
        """GET /products/search tìm theo từ khóa"""
        products = api.list_products(limit=1)
        if not products:
            pytest.skip("DB chưa có sản phẩm")
        first = products[0]

        keyword = first["name"].split(" ")[0]
        res = api.get(f"/products/search?q={quote(keyword, safe='')}")
        expect(res).to_be_ok()
        body = res.json()
        data = body.get("data")
        found = (data.get("products") if isinstance(data, dict) else None) or data or []
        assert len(found) > 0, f"Tìm '{keyword}': expected>0 kết quả, actual={len(found)}"

    def test_kids_endpoints(self, api):
        """GET /products/kids, /kids-categories hoạt động"""
        for path in ("/products/kids", "/products/kids-categories"):
            res = api.get(path)
            assert res.status == 200, f"{path}: expected=200, actual={res.status}"

    def test_suggested_products(self, api, request):
        """GET /products/suggested (gợi ý trong giỏ hàng) trả 200"""
        known_bug(
            request,
            'query dùng hàm HEX() của MySQL trên Postgres -> 500 "function hex(character varying) does not exist"',
        )
        res = api.get("/products/suggested?limit=6")
        assert res.status == 200, f"expected=200, actual={res.status}"

    def test_news_published(self, api):
        """GET /news trả danh sách bài viết đã publish"""
        res = api.get("/news?limit=3")
        expect(res).to_be_ok()
        body = res.json()
        assert body["success"] is True, f"success: expected=True, actual={body.get('success')!r}"
        assert len(body["news"]) <= 3, f"Số bài viết: expected<=3, actual={len(body['news'])}"
