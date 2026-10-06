# THƯ VIỆN KEYWORD - NHÓM cart: giỏ hàng (drawer + localStorage).
from playwright.sync_api import expect

from keywords.base_keywords import BaseKeywords, keyword
from utils.factories import build_cart_item
from utils.storage import read_cart, seed_cart
from utils.routes import ROUTES


class CartKeywords(BaseKeywords):
    group = "cart"

    @keyword("seedCart")
    def seed_cart(self, items):
        """Đặt sẵn sản phẩm vào giỏ (localStorage) - gọi TRƯỚC lần mở trang đầu tiên."""
        with self.step(f"Đặt sẵn {len(items)} sản phẩm vào giỏ"):
            seed_cart(self.page, [build_cart_item(**item) for item in items])

    @keyword("openCart")
    def open_cart(self):
        """Bấm icon giỏ hàng để mở drawer."""
        with self.step("Mở giỏ hàng"):
            self.po.header.open_cart()
            self.po.cart.expect_open()

    @keyword("closeCart")
    def close_cart(self):
        """Đóng drawer bằng nút X."""
        with self.step("Đóng giỏ hàng (nút X)"):
            self.po.cart.close()
            self.po.cart.expect_closed()

    @keyword("closeCartWithEsc")
    def close_cart_with_esc(self):
        """Đóng drawer bằng phím ESC."""
        with self.step("Đóng giỏ hàng (ESC)"):
            self.page.keyboard.press("Escape")
            self.po.cart.expect_closed()

    @keyword("verifyCartBadge")
    def verify_cart_badge(self, count):
        """Kiểm tra số trên icon giỏ hàng (0 = không hiện badge)."""
        with self.step(f"Kiểm tra badge giỏ hàng = {count}"):
            badge = self.po.header.cart_badge
            if count == 0:
                expect(badge).to_be_hidden()
            else:
                expect(badge).to_have_text("9+" if count > 9 else str(count))

    @keyword("verifyCartEmpty")
    def verify_cart_empty(self):
        """Kiểm tra drawer hiển thị "Giỏ hàng trống"."""
        with self.step("Kiểm tra giỏ hàng trống"):
            expect(self.po.cart.empty_state).to_be_visible()

    @keyword("verifyCartItemCount")
    def verify_cart_item_count(self, count):
        """Kiểm tra số dòng sản phẩm trong drawer (và tiêu đề "Giỏ hàng (n)")."""
        with self.step(f"Kiểm tra giỏ có {count} sản phẩm"):
            expect(self.po.cart.title).to_have_text(f"Giỏ hàng ({count})")
            expect(self.po.cart.items).to_have_count(count)

    @keyword("verifyCartItem")
    def verify_cart_item(self, name, contains_text=None):
        """Kiểm tra 1 sản phẩm có trong giỏ, có thể kèm đoạn chữ (vd: size)."""
        suffix = f' chứa "{contains_text}"' if contains_text else ""
        with self.step(f'Kiểm tra giỏ có "{name}"{suffix}'):
            item = self.po.cart.item(name)
            expect(item).to_be_visible()
            if contains_text:
                expect(item).to_contain_text(contains_text)

    @keyword("increaseQuantity")
    def increase_quantity(self, name, times=1):
        """Bấm "+" số lần cho 1 sản phẩm."""
        with self.step(f'Tăng số lượng "{name}" x{times}'):
            for _ in range(times):
                self.po.cart.increase(name)

    @keyword("decreaseQuantity")
    def decrease_quantity(self, name, times=1):
        """Bấm "-" số lần cho 1 sản phẩm."""
        with self.step(f'Giảm số lượng "{name}" x{times}'):
            for _ in range(times):
                self.po.cart.decrease(name)

    @keyword("verifyQuantity")
    def verify_quantity(self, name, quantity):
        """Kiểm tra số lượng hiển thị của 1 sản phẩm."""
        with self.step(f'Kiểm tra số lượng "{name}" = {quantity}'):
            expect(self.po.cart.quantity(name)).to_have_text(str(quantity))

    @keyword("verifyDecreaseDisabled")
    def verify_decrease_disabled(self, name):
        """Kiểm tra nút "-" bị khóa (số lượng = 1)."""
        with self.step(f'Kiểm tra không giảm được "{name}" dưới 1'):
            button = self.po.cart.item(name).get_by_role("button", name="Giảm số lượng")
            expect(button).to_be_disabled()

    @keyword("removeItem")
    def remove_item(self, name):
        """Xóa 1 sản phẩm khỏi giỏ."""
        with self.step(f'Xóa "{name}" khỏi giỏ'):
            self.po.cart.remove(name)
            expect(self.po.cart.item(name)).to_have_count(0)

    @keyword("selectAll")
    def select_all(self, checked):
        """Tick / bỏ tick "Chọn tất cả"."""
        with self.step(f"{'Chọn' if checked else 'Bỏ chọn'} tất cả sản phẩm"):
            self.po.cart.select_all.set_checked(checked)

    @keyword("verifyAllSelected")
    def verify_all_selected(self, checked):
        """Kiểm tra trạng thái ô "Chọn tất cả"."""
        with self.step(f'Kiểm tra "Chọn tất cả" = {str(checked).lower()}'):
            if checked:
                expect(self.po.cart.select_all).to_be_checked()
            else:
                expect(self.po.cart.select_all).not_to_be_checked()

    @keyword("verifySubtotal")
    def verify_subtotal(self, amount):
        """Kiểm tra dòng Tạm tính chứa số tiền, vd: "550.000"."""
        with self.step(f"Kiểm tra tạm tính {amount}"):
            expect(self.po.cart.subtotal).to_contain_text(amount)

    @keyword("verifyCheckoutEnabled")
    def verify_checkout_enabled(self, enabled):
        """Kiểm tra nút THANH TOÁN bật/tắt."""
        with self.step(f"Kiểm tra nút THANH TOÁN {'bật' if enabled else 'tắt'}"):
            button = self.po.cart.checkout_button
            if enabled:
                expect(button).to_be_enabled()
            else:
                expect(button).to_be_disabled()

    @keyword("proceedToCheckout")
    def proceed_to_checkout(self):
        """Bấm THANH TOÁN trong drawer và chờ sang /checkout."""
        with self.step("Bấm THANH TOÁN"):
            self.po.cart.checkout_button.click()
            expect(self.page).to_have_url(ROUTES["checkout"])

    @keyword("verifyStoredItemCount")
    def verify_stored_item_count(self, count):
        """Kiểm tra số dòng sản phẩm lưu trong localStorage."""
        with self.step(f"Kiểm tra localStorage có {count} sản phẩm"):
            cart = read_cart(self.page)
            assert len(cart) == count, f"localStorage: expected={count}, actual={len(cart)}"

    @keyword("verifyStoredQuantity")
    def verify_stored_quantity(self, name, quantity):
        """Kiểm tra số lượng của 1 sản phẩm lưu trong localStorage."""
        with self.step(f'Kiểm tra localStorage: "{name}" = {quantity}'):
            item = next((i for i in read_cart(self.page) if i["name"] == name), None)
            actual = item["quantity"] if item else None
            assert actual == quantity, f'"{name}": expected={quantity}, actual={actual}'
