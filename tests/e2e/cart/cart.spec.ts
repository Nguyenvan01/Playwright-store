import { test } from '@fixtures';
import { loadData } from '@data/loader';
import type { CartData } from '@data/types';

const data = loadData<CartData>('cart/items.json');
const [shirt, jeans] = data.twoItems as { name: string; size: string }[];

test.describe('Giỏ hàng (drawer)', () => {
  test('Giỏ hàng trống', async ({ k }) => {
    await k.catalog.openHome();
    await k.cart.openCart();
    await k.cart.verifyCartEmpty();
  });

  test('Mở/đóng drawer bằng nút X và phím ESC', async ({ k }) => {
    await k.catalog.openHome();
    await k.cart.openCart();
    await k.cart.closeCart();
    await k.cart.openCart();
    await k.cart.closeCartWithEsc();
  });

  test.describe('Có sẵn sản phẩm (cart/items.json)', () => {
    test.beforeEach(async ({ k }) => {
      await k.cart.seedCart(data.twoItems);
      await k.catalog.openHome();
    });

    test('Hiển thị số lượng và danh sách sản phẩm @smoke', async ({ k }) => {
      await k.cart.verifyCartBadge(2);
      await k.cart.openCart();
      await k.cart.verifyCartItemCount(2);
      await k.cart.verifyCartItem(shirt.name, `| ${shirt.size}`);
    });

    test('Tăng/giảm số lượng và lưu vào localStorage', async ({ k }) => {
      await k.cart.openCart();
      await k.cart.increaseQuantity(shirt.name, 2);
      await k.cart.verifyQuantity(shirt.name, 3);
      await k.cart.decreaseQuantity(shirt.name);
      await k.cart.verifyQuantity(shirt.name, 2);
      await k.cart.verifyStoredQuantity(shirt.name, 2);
    });

    test('Không giảm được dưới 1', async ({ k }) => {
      await k.cart.openCart();
      await k.cart.verifyDecreaseDisabled(jeans.name);
    });

    test('Xóa sản phẩm khỏi giỏ', async ({ k }) => {
      await k.cart.openCart();
      await k.cart.removeItem(shirt.name);
      await k.cart.verifyCartItemCount(1);
      await k.cart.verifyCartBadge(1);
    });

    test('Mặc định chọn tất cả; bỏ chọn hết thì không thanh toán được', async ({ k }) => {
      await k.cart.openCart();
      await k.cart.verifyAllSelected(true);
      await k.cart.verifySubtotal(data.expectedSubtotal);
      await k.cart.verifyCheckoutEnabled(true);

      await k.cart.selectAll(false);
      await k.cart.verifyCheckoutEnabled(false);
    });

    test('Giỏ hàng được giữ sau khi reload', async ({ k }) => {
      await k.common.reload();
      await k.cart.verifyCartBadge(2);
    });

    test('Bấm THANH TOÁN chuyển tới trang checkout', async ({ k }) => {
      await k.cart.openCart();
      await k.cart.proceedToCheckout();
    });
  });
});

test('Luồng thật: thêm sản phẩm từ trang chi tiết rồi xem trong giỏ @smoke', async ({ k, purchasable }) => {
  await k.catalog.openProduct(purchasable.product.slug);
  await k.catalog.addToCart(purchasable.size.label);
  await k.cart.openCart();
  await k.cart.verifyCartItem(purchasable.product.name, purchasable.size.label);
});
