import { test } from '@fixtures';
import { loadData } from '@data/loader';
import type { AddressBook, CheckoutData } from '@data/types';
import { applyCaseMeta, caseTitle } from '@engine/cases';

const data = loadData<CheckoutData>('checkout/checkout.json');
const addresses = loadData<AddressBook>('checkout/addresses.json');
const item = data.cartItem as { name: string; price: number; quantity: number };

test.describe('Thanh toán', () => {
  test('Giỏ trống -> hiển thị thông báo, không có form', async ({ k }) => {
    await k.checkout.openCheckout();
    await k.checkout.verifyEmptyCheckout();
  });

  test('/order-success không có dữ liệu đơn', async ({ k }) => {
    await k.checkout.verifyOrderSuccessWithoutData();
  });

  test.describe('Khách vãng lai, có sản phẩm trong giỏ', () => {
    test.beforeEach(async ({ k }) => {
      await k.cart.seedCart([data.cartItem]);
      await k.checkout.openCheckout();
    });

    test('Hiển thị sản phẩm và nút Đăng nhập @smoke', async ({ k }) => {
      await k.checkout.verifyProductInCheckout(item.name);
      await k.checkout.verifyGuestLoginPrompt();
      await k.checkout.verifySubmitEnabled(false);
    });

    test.describe('Đặt hàng (mock API, data-driven)', () => {
      for (const c of data.orders) {
        test(caseTitle(c), async ({ k }) => {
          applyCaseMeta(c);
          const address = addresses[c.address];
          const orderNumber = `E2E-${c.id}`;

          await k.checkout.mockCreateOrder({ orderNumber });
          await k.checkout.fillShipping(address);
          await k.checkout.chooseShipping(c.shippingMethod);
          await k.checkout.choosePayment(c.payment);
          if (c.expected.shippingFee) await k.checkout.verifySummaryContains('30.000');
          await k.checkout.placeOrder();

          await k.checkout.verifyOrderSuccess(c.expected.heading, orderNumber);
          await k.checkout.verifyLastOrderPayload({
            recipient_name: `${address.firstName} ${address.lastName}`,
            recipient_phone: address.phone,
            city: address.city,
            district: address.district,
            shipping_method: c.shippingMethod,
            shipping_fee: c.expected.shippingFee,
            payment_method: c.payment,
            payment_status: c.expected.paymentStatus,
            items: [test.expect.objectContaining({ product_name: item.name, quantity: item.quantity, unit_price: item.price })],
          });
          await k.cart.verifyStoredItemCount(0);
        });
      }
    });

    test.describe('Thiếu thông tin bắt buộc (data-driven)', () => {
      for (const c of data.incomplete) {
        test(caseTitle(c), async ({ k }) => {
          applyCaseMeta(c);
          await k.checkout.fillShipping(addresses.hcm);
          await k.checkout.verifySubmitEnabled(true);
          await k.checkout.clearShippingField(c.missing as 'firstName' | 'lastName' | 'phone' | 'address');
          await k.checkout.verifySubmitEnabled(false);
        });
      }
    });

    test.describe('Backend lỗi (mock, data-driven)', () => {
      for (const c of data.serverErrors) {
        test(caseTitle(c), async ({ k }) => {
          applyCaseMeta(c);
          await k.checkout.mockCreateOrder({ status: c.status, message: c.message });
          await k.checkout.fillShipping(addresses.hcm);
          await k.checkout.placeOrder();
          await k.common.verifyToast(c.message);
          await k.checkout.verifyStillOnCheckout();
          await k.cart.verifyStoredItemCount(1);
        });
      }
    });
  });

  test('Đặt hàng thật end-to-end (ghi DB)', async ({ k, purchasable }) => {
    applyCaseMeta({ id: 'CO-REAL', title: '', requires: ['allowWrite'] });
    await k.catalog.openProduct(purchasable.product.slug);
    await k.catalog.addToCart(purchasable.size.label);
    await k.checkout.openCheckout();
    await k.checkout.fillShipping(addresses.hcm);
    await k.checkout.placeOrder();
    await k.checkout.verifyOrderSuccess('Đặt hàng thành công');
  });
});
