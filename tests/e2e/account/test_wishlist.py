# ============================================================
# TEST: DANH SÁCH YÊU THÍCH
# Mục tiêu: hiển thị, sắp xếp, tìm kiếm, tình trạng hàng, bỏ yêu thích, thêm vào giỏ
# Dữ liệu: data/account/wishlist.json (app không có UI thêm yêu thích -> mock GET /api/wishlist)
# Kết quả mong đợi: thẻ sản phẩm + số lượng khớp dữ liệu; DELETE đúng sản phẩm; giỏ hàng cập nhật
# ============================================================
import pytest

from tests.e2e.account.support import API
from utils.cases import case_params, known_bug
from utils.data_loader import load_data

DATA = load_data("account/wishlist.json")

pytestmark = pytest.mark.role("customer")


class TestWishlist:
    """Danh sách yêu thích"""

    def test_empty_wishlist(self, k):
        """[ACC-WL-E01] Chưa có sản phẩm yêu thích: thông báo trống, 0 sản phẩm"""
        k.common.mock_get(API["wishlist"], DATA["empty"])
        k.account.open_wishlist()
        k.account.verify_wishlist_empty()

    def test_heart_on_listing(self, k, request):
        """[ACC-WL-H01] Bấm trái tim trên trang danh mục lưu sản phẩm vào yêu thích"""
        known_bug(
            request,
            "MenPage.jsx:391 (và KidsPage.jsx:347) - nút trái tim không có onClick, nằm trong <Link>; "
            "không nơi nào gọi POST /api/wishlist nên khách không thể thêm yêu thích",
        )
        k.common.mock_write(
            "POST", API["wishlist"], {"success": True, "message": "Đã thêm vào danh sách yêu thích"}, 201
        )
        k.account.favorite_from_listing(DATA["heart"]["listingPath"])
        k.common.verify_request("POST", "/api/wishlist")


class TestWishlistWithItems:
    """Danh sách yêu thích - Có sản phẩm yêu thích"""

    @pytest.fixture(autouse=True)
    def opened_wishlist(self, k):
        k.common.mock_get(API["wishlist"], DATA["response"])
        k.account.open_wishlist()
        k.account.verify_wishlist_loaded()

    @pytest.mark.smoke
    def test_count_and_list(self, k):
        """[ACC-WL-01] Hiển thị số lượng và danh sách (mới lưu trước)"""
        k.account.verify_wishlist_count(DATA["count"])
        k.account.verify_wishlist_products(DATA["recentOrder"])

    @pytest.mark.parametrize("case", case_params(DATA["sort"]))
    def test_sort(self, k, case):
        """Sắp xếp (data-driven)"""
        k.account.sort_wishlist(case["sort"])
        k.account.verify_wishlist_products(case["expected"])

    @pytest.mark.parametrize("case", case_params(DATA["search"]))
    def test_search(self, k, case):
        """Tìm kiếm (data-driven)"""
        k.account.search_wishlist(case["query"])
        if case["expected"]:
            k.account.verify_wishlist_products(case["expected"])
        else:
            k.account.verify_wishlist_no_match()
        k.account.verify_wishlist_count(DATA["count"])

    @pytest.mark.parametrize("case", case_params(DATA["availability"]))
    def test_availability(self, k, case):
        """Tình trạng hàng + thông tin thẻ (data-driven)"""
        k.account.verify_wishlist_item(case["name"], case["texts"])
        k.account.verify_wishlist_item_available(case["name"], case["available"])

    def test_remove(self, k):
        """[ACC-WL-R01] Bỏ yêu thích: gửi DELETE đúng sản phẩm, cập nhật danh sách và số lượng"""
        r = DATA["remove"]
        k.common.mock_write(
            "DELETE", API["wishlistItem"], {"success": True, "message": "Đã xóa khỏi danh sách yêu thích"}
        )
        k.account.remove_from_wishlist(r["name"])
        k.common.verify_request("DELETE", f"/api/wishlist/{r['productId']}")
        k.account.verify_wishlist_products(r["remaining"])
        k.account.verify_wishlist_count(len(r["remaining"]))

    def test_remove_failure_restores(self, k):
        """[ACC-WL-R02] Bỏ yêu thích thất bại: sản phẩm được khôi phục"""
        r = DATA["remove"]
        k.common.mock_write("DELETE", API["wishlistItem"], r["errorResponse"], r["errorStatus"])
        k.account.remove_from_wishlist(r["name"])
        k.common.verify_request("DELETE", f"/api/wishlist/{r['productId']}")
        k.account.verify_wishlist_products(DATA["recentOrder"])
        k.account.verify_wishlist_count(DATA["count"])

    def test_add_simple_to_cart(self, k):
        """[ACC-WL-C01] Thêm vào giỏ sản phẩm không có biến thể: toast + giỏ có 1 sản phẩm"""
        k.account.add_wishlist_item_to_cart(DATA["addSimple"]["name"])
        k.common.verify_toast(DATA["addSimple"]["toast"])
        k.cart.verify_stored_item_count(1)
        k.cart.verify_cart_badge(1)

    def test_add_with_variants_opens_product(self, k):
        """[ACC-WL-C02] Thêm vào giỏ sản phẩm có biến thể: chuyển sang trang sản phẩm để chọn size"""
        k.account.add_wishlist_item_to_cart(DATA["addWithVariants"]["name"])
        k.common.verify_url(f"/product/{DATA['addWithVariants']['slug']}")
        k.cart.verify_stored_item_count(0)
