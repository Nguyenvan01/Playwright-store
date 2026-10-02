import { test } from '@fixtures';
import { MSG } from '@data/messages';

test.describe('Trang chi tiết sản phẩm', () => {
  test.beforeEach(async ({ k, purchasable }) => {
    await k.catalog.openProduct(purchasable.product.slug);
    await k.catalog.verifyProductTitle(purchasable.product.name);
  });

  test('Hiển thị đầy đủ các size và cảnh báo chọn size @smoke', async ({ k, purchasable }) => {
    await k.catalog.verifySizeCount(purchasable.product.sizes.length);
    await k.catalog.verifySizeWarning(true);
  });

  test('Chưa chọn size mà bấm thêm vào giỏ -> báo lỗi', async ({ k }) => {
    await k.catalog.addToCart();
    await k.common.verifyToast(MSG.product.selectSize);
    await k.cart.verifyCartBadge(0);
  });

  test('Chọn size làm mất cảnh báo', async ({ k, purchasable }) => {
    await k.catalog.selectSize(purchasable.size.label);
    await k.catalog.verifySizeWarning(false);
  });

  test('Thêm vào giỏ thành công cập nhật badge giỏ hàng @smoke', async ({ k, purchasable }) => {
    await k.catalog.addToCart(purchasable.size.label);
    await k.common.verifyToast(MSG.product.addedToCart(purchasable.product.name));
    await k.cart.verifyCartBadge(1);
  });
});

test('Slug không tồn tại hiển thị "Không tìm thấy sản phẩm"', async ({ k }) => {
  test.fail(true, 'BUG: ProductDetailPage hiển thị mockProduct (sản phẩm giả) khi API trả 404');
  await k.catalog.openProduct('san-pham-khong-ton-tai-e2e-999');
  await k.catalog.verifyProductNotFound();
});
