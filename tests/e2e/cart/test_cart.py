# ============================================================
# TEST: GIỎ HÀNG (DRAWER)
# Mục tiêu: mở/đóng drawer, tăng/giảm/xóa sản phẩm, tạm tính, lưu localStorage
# Dữ liệu: data/cart/items.json (2 sản phẩm đặt sẵn vào localStorage)
# API cần quan sát: k.cart.*, k.catalog.open_home, fixture purchasable (sản phẩm thật qua API)
# Kết quả mong đợi: badge, số lượng, tạm tính khớp dữ liệu; reload vẫn giữ giỏ
# ============================================================
import pytest

from utils.data_loader import load_data

DATA = load_data("cart/items.json")
SHIRT, JEANS = DATA["twoItems"]


def test_empty_cart(k):
    """Giỏ hàng trống"""
    k.catalog.open_home()
    k.cart.open_cart()
    k.cart.verify_cart_empty()


def test_open_close_drawer(k):
    """Mở/đóng drawer bằng nút X và phím ESC"""
    k.catalog.open_home()
    k.cart.open_cart()
    k.cart.close_cart()
    k.cart.open_cart()
    k.cart.close_cart_with_esc()


class TestSeededCart:
    """Có sẵn sản phẩm (cart/items.json)"""

    @pytest.fixture(autouse=True)
    def seeded(self, k):
        k.cart.seed_cart(DATA["twoItems"])
        k.catalog.open_home()

    @pytest.mark.smoke
    def test_badge_and_items(self, k):
        """Hiển thị số lượng và danh sách sản phẩm"""
        k.cart.verify_cart_badge(2)
        k.cart.open_cart()
        k.cart.verify_cart_item_count(2)
        k.cart.verify_cart_item(SHIRT["name"], f"| {SHIRT['size']}")

    def test_change_quantity_persists(self, k):
        """Tăng/giảm số lượng và lưu vào localStorage"""
        k.cart.open_cart()
        k.cart.increase_quantity(SHIRT["name"], 2)
        k.cart.verify_quantity(SHIRT["name"], 3)
        k.cart.decrease_quantity(SHIRT["name"])
        k.cart.verify_quantity(SHIRT["name"], 2)
        k.cart.verify_stored_quantity(SHIRT["name"], 2)

    def test_cannot_decrease_below_one(self, k):
        """Không giảm được dưới 1"""
        k.cart.open_cart()
        k.cart.verify_decrease_disabled(JEANS["name"])

    def test_remove_item(self, k):
        """Xóa sản phẩm khỏi giỏ"""
        k.cart.open_cart()
        k.cart.remove_item(SHIRT["name"])
        k.cart.verify_cart_item_count(1)
        k.cart.verify_cart_badge(1)

    def test_select_all_controls_checkout(self, k):
        """Mặc định chọn tất cả; bỏ chọn hết thì không thanh toán được"""
        k.cart.open_cart()
        k.cart.verify_all_selected(True)
        k.cart.verify_subtotal(DATA["expectedSubtotal"])
        k.cart.verify_checkout_enabled(True)

        k.cart.select_all(False)
        k.cart.verify_checkout_enabled(False)

    def test_cart_kept_after_reload(self, k):
        """Giỏ hàng được giữ sau khi reload"""
        k.common.reload()
        k.cart.verify_cart_badge(2)

    def test_checkout_button_navigates(self, k):
        """Bấm THANH TOÁN chuyển tới trang checkout"""
        k.cart.open_cart()
        k.cart.proceed_to_checkout()


@pytest.mark.smoke
def test_add_from_product_detail(k, purchasable):
    """Luồng thật: thêm sản phẩm từ trang chi tiết rồi xem trong giỏ"""
    k.catalog.open_product(purchasable["product"]["slug"])
    k.catalog.add_to_cart(purchasable["size"]["label"])
    k.cart.open_cart()
    k.cart.verify_cart_item(purchasable["product"]["name"], purchasable["size"]["label"])
