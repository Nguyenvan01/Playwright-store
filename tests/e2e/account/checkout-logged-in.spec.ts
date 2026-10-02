import { test } from '@fixtures';
import { AUTH_FILES } from '@config/env';
import { loadData } from '@data/loader';
import type { AccountCheckoutData } from '@data/account.types';
import type { AddressBook } from '@data/types';
import { applyCaseMeta, caseTitle } from '@engine/cases';
import { hasCustomerAuth } from '@utils/storage';
import { API } from './support';

const data = loadData<AccountCheckoutData>('account/checkout.json');
const address = loadData<AddressBook>('checkout/addresses.json')[data.address];
const user = data.user as Record<string, string>;
const cartItemName = String(data.cartItem.name);

/**
 * Thanh toán khi đã đăng nhập. User trong localStorage được thay bằng user mẫu (seedStoredUser)
 * để dữ liệu điền sẵn ổn định; token vẫn là token thật của tài khoản test. Tạo đơn luôn được mock.
 */
test.describe('Thanh toán khi đã đăng nhập', () => {
  test.use({ storageState: AUTH_FILES.customer });
  test.skip(() => !hasCustomerAuth(), 'Chưa có tài khoản test (xem .env)');

  test.describe('Điền sẵn thông tin từ tài khoản (data-driven)', () => {
    for (const c of data.prefill) {
      test(caseTitle(c), async ({ k }) => {
        applyCaseMeta(c);
        await k.account.seedStoredUser(c.user);
        await k.cart.seedCart([data.cartItem]);
        await k.checkout.openCheckout();
        await k.account.verifyCheckoutAccount(String(c.user.name), String(c.user.email));
        await k.account.verifyCheckoutPrefill(c.expected);
      });
    }
  });

  test.describe('Có sản phẩm trong giỏ', () => {
    test.beforeEach(async ({ k }) => {
      await k.account.seedStoredUser(data.user);
      await k.cart.seedCart([data.cartItem]);
      await k.checkout.openCheckout();
      await k.account.verifyCheckoutAccount(user.name, user.email);
    });

    test('[ACC-CO-01] Đăng xuất ngay trên trang thanh toán: chuyển sang chế độ khách, giữ giỏ hàng', async ({ k }) => {
      await k.account.logoutOnCheckout();
      await k.account.verifyCheckoutGuestMode();
      await k.checkout.verifyProductInCheckout(cartItemName);
    });

    test.describe('Payload tạo đơn theo phương thức thanh toán (mock, data-driven)', () => {
      for (const c of data.payments) {
        test(caseTitle(c), async ({ k }) => {
          applyCaseMeta(c);
          await k.common.mockWrite('POST', API.createOrder, data.createResponse, 201);
          await k.checkout.fillShipping(address);
          await k.checkout.choosePayment(c.payment);
          await k.checkout.placeOrder();
          await k.common.verifyRequest('POST', '/api/orders', c.expectedPayload);
        });
      }
    });

    test('[ACC-CO-02] Đặt hàng COD thành công: trang thành công hiển thị đủ thông tin @smoke', async ({ k }) => {
      const s = data.success;
      await k.common.mockWrite('POST', API.createOrder, data.createResponse, 201);
      await k.checkout.fillShipping(address);
      await k.checkout.choosePayment('cod');
      await k.checkout.placeOrder();
      await k.checkout.verifyOrderSuccess(s.heading, data.orderNumber);
      await k.account.verifyOrderSuccessNumber(data.orderNumber);
      await k.account.verifyOrderSuccessInfo('Thông tin thanh toán', s.payment);
      await k.account.verifyOrderSuccessInfo('Người nhận', s.recipient);
      await k.account.verifyOrderSuccessInfo('Chi tiết thanh toán', s.totals);
      await k.account.verifyOrderSuccessLinks();
      await k.cart.verifyStoredItemCount(0);
    });

    test('[ACC-CO-03] Trang thành công (COD) hiển thị đúng trạng thái đơn vừa tạo', async ({ k }) => {
      test.fail(
        true,
        'BUG: OrderSuccessPage.jsx:188 luôn ghi "Đã xác nhận" cho COD, trong khi backend tạo đơn với status "pending" (Chờ xác nhận)',
      );
      await k.common.mockWrite('POST', API.createOrder, data.createResponse, 201);
      await k.checkout.fillShipping(address);
      await k.checkout.placeOrder();
      await k.checkout.verifyOrderSuccess(data.success.heading, data.orderNumber);
      await k.account.verifyOrderSuccessInfo('Thông tin thanh toán', { 'Trạng thái': data.success.codStatusExpected });
    });

    test('[ACC-CO-04] Từ trang thành công bấm Xem đơn hàng thấy đơn vừa đặt', async ({ k }) => {
      await k.common.mockWrite('POST', API.createOrder, data.createResponse, 201);
      await k.common.mockGet(API.orders, data.ordersAfter);
      await k.checkout.fillShipping(address);
      await k.checkout.placeOrder();
      await k.checkout.verifyOrderSuccess(data.success.heading, data.orderNumber);
      await k.account.openOrdersFromSuccess();
      await k.account.verifyOrderList([data.orderNumber]);
      await k.account.verifyOrderStatus(data.orderNumber, 'Chờ xác nhận');
    });
  });

  test('[ACC-CO-05] Đặt hàng thật bằng Chuyển khoản ngân hàng (ghi DB)', async ({ k, purchasable }) => {
    applyCaseMeta({
      id: 'ACC-CO-05',
      title: '',
      requires: ['allowWrite'],
      knownBug:
        "CheckoutPage.jsx:541 gửi payment_method 'bank', vi phạm CHECK orders.payment_method (database/schema.pg.sql:417) -> backend 500 'Lỗi server khi tạo đơn hàng'",
    });
    await k.catalog.openProduct(purchasable.product.slug);
    await k.catalog.addToCart(purchasable.size.label);
    await k.checkout.openCheckout();
    await k.checkout.fillShipping(address);
    await k.checkout.choosePayment('bank');
    await k.checkout.placeOrder();
    await k.checkout.verifyOrderSuccess('Đang chờ thanh toán');
  });
});
