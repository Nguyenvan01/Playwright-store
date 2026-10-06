# ============================================================
# TEST: TRANG CHI TIẾT SẢN PHẨM
# Mục tiêu: hiển thị size, cảnh báo chọn size, thêm vào giỏ, slug không tồn tại
# Dữ liệu: fixture purchasable (sản phẩm thật qua API có size còn hàng), utils/messages.py
# API cần quan sát: k.catalog.*, k.common.verify_toast, k.cart.verify_cart_badge
# Kết quả mong đợi: đủ size; chưa chọn size -> toast lỗi; thêm thành công -> badge = 1
# ============================================================
import pytest

from utils.cases import known_bug
from utils.messages import MSG, added_to_cart


class TestProductDetail:
    """Trang chi tiết sản phẩm"""

    @pytest.fixture(autouse=True)
    def open_product(self, k, purchasable):
        k.catalog.open_product(purchasable["product"]["slug"])
        k.catalog.verify_product_title(purchasable["product"]["name"])

    @pytest.mark.smoke
    def test_sizes_and_warning(self, k, purchasable):
        """Hiển thị đầy đủ các size và cảnh báo chọn size"""
        k.catalog.verify_size_count(len(purchasable["product"]["sizes"]))
        k.catalog.verify_size_warning(True)

    def test_add_without_size_shows_error(self, k):
        """Chưa chọn size mà bấm thêm vào giỏ -> báo lỗi"""
        k.catalog.add_to_cart()
        k.common.verify_toast(MSG["product"]["selectSize"])
        k.cart.verify_cart_badge(0)

    def test_select_size_hides_warning(self, k, purchasable):
        """Chọn size làm mất cảnh báo"""
        k.catalog.select_size(purchasable["size"]["label"])
        k.catalog.verify_size_warning(False)

    @pytest.mark.smoke
    def test_add_to_cart_updates_badge(self, k, purchasable):
        """Thêm vào giỏ thành công cập nhật badge giỏ hàng"""
        k.catalog.add_to_cart(purchasable["size"]["label"])
        k.common.verify_toast(added_to_cart(purchasable["product"]["name"]))
        k.cart.verify_cart_badge(1)


def test_unknown_slug_shows_not_found(k, request):
    """Slug không tồn tại hiển thị "Không tìm thấy sản phẩm\""""
    known_bug(request, "ProductDetailPage hiển thị mockProduct (sản phẩm giả) khi API trả 404")
    k.catalog.open_product("san-pham-khong-ton-tai-e2e-999")
    k.catalog.verify_product_not_found()
