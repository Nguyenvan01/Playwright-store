# ============================================================
# TEST: LỌC GIÁ - RACE CONDITION (SF-LST-RACE)
# Mục tiêu: ô "Từ" và "Đến" mỗi ô gọi API riêng khi blur, app không hủy/bỏ qua response cũ.
# Dữ liệu: mock trong file: request chỉ có min_price trả chậm, request có cả min+max trả ngay
#          -> response cũ về sau ghi đè.
# API cần quan sát: page.route, ListingPage (price_from, price_to, cards)
# Kết quả mong đợi: kết quả cuối là khoảng 300k-600k (1 sản phẩm) - hiện là bug đã biết (xfail)
# ============================================================
from playwright.sync_api import expect

from pages.storefront.listing_page import ListingPage
from utils.cases import known_bug


def product(product_id, price):
    return {
        "id": product_id,
        "name": f"SP Race {product_id}",
        "slug": f"sp-race-{product_id}",
        "price": price,
        "compare_price": None,
        "image_url": None,
        "category_slug": "ao-thun",
        "avg_rating": 0,
        "review_count": 0,
    }


def body(products):
    return {
        "success": True,
        "data": {
            "products": products,
            "pagination": {"page": 1, "limit": 8, "total": len(products), "total_pages": 1},
        },
    }


def test_slow_old_response_must_not_override(page, k, request):
    """[SF-LST-RACE] Lọc giá: response cũ trả chậm không được ghi đè kết quả mới"""
    known_bug(
        request,
        "ProductFilters.jsx handleApply gọi API mỗi lần blur, MenPage không hủy request cũ -> kết quả cũ ghi đè",
    )
    cheap = product(1, 350000)
    expensive = product(2, 799000)

    def handle(route):
        url = route.request.url
        if "max_price=" in url:
            return route.fulfill(json=body([cheap]))
        if "min_price=" in url:
            # Response cũ về chậm. Mỗi handler chạy trong greenlet riêng nên chờ ở đây
            # không chặn request mới (khác time.sleep sẽ chặn cả vòng sự kiện).
            page.wait_for_timeout(1500)
            return route.fulfill(json=body([cheap, expensive]))
        return route.fulfill(json=body([cheap, expensive]))

    page.route("**/api/products?*", handle)

    listing = ListingPage(page)
    k.common.goto("/nam")
    expect(listing.cards).to_have_count(2)

    # Người dùng nhập liền 2 ô như bình thường; đợi cả response chậm về
    with page.expect_response(
        lambda r: "min_price=" in r.url and "max_price=" not in r.url
    ):
        listing.price_from.fill("300000")
        listing.price_to.fill("600000")
        listing.price_to.blur()

    # Kết quả cuối phải là khoảng 300k-600k (chỉ 1 sản phẩm)
    expect(listing.cards, "Kết quả bị response cũ ghi đè").to_have_count(1)
