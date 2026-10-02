import { expect } from '@playwright/test';
import type { ShippingInfo } from '@data/factories';
import { ROUTES } from '@data/routes';
import type { PaymentMethod, ShippingMethod } from '@pages/CheckoutPage';
import { BaseKeywords } from './BaseKeywords';

export class CheckoutKeywords extends BaseKeywords {
  /** Payload đơn hàng cuối cùng bắt được qua mockCreateOrder. */
  private lastOrderPayload: unknown;

  /** Mở trang thanh toán. */
  async openCheckout() {
    await this.step('Mở trang thanh toán', async () => {
      await this.po.checkout.goto();
    });
  }

  /** Kiểm tra trang thanh toán báo giỏ trống, không có nút Thanh toán. */
  async verifyEmptyCheckout() {
    await this.step('Kiểm tra trang thanh toán báo giỏ trống', async () => {
      await expect(this.po.checkout.emptyCartHeading).toBeVisible();
      await expect(this.po.checkout.submitButton).toHaveCount(0);
    });
  }

  /** Kiểm tra sản phẩm hiển thị trong khối sản phẩm của trang thanh toán. */
  async verifyProductInCheckout(name: string) {
    await this.step(`Kiểm tra trang thanh toán có "${name}"`, async () => {
      await expect(this.po.checkout.productsSection).toContainText(name);
    });
  }

  /** Kiểm tra nút "Đăng nhập / Đăng ký" cho khách vãng lai. */
  async verifyGuestLoginPrompt() {
    await this.step('Kiểm tra có nút Đăng nhập / Đăng ký', async () => {
      await expect(this.po.checkout.loginButton).toBeVisible();
    });
  }

  /** Điền thông tin giao hàng (dùng dữ liệu checkout/addresses.json). */
  async fillShipping(info: ShippingInfo) {
    await this.step(`Điền thông tin giao hàng: ${info.firstName} ${info.lastName}, ${info.city}`, async () => {
      await this.po.checkout.fillShipping(info);
    });
  }

  /** Xóa nội dung 1 ô trong form giao hàng: firstName | lastName | phone | address. */
  async clearShippingField(field: 'firstName' | 'lastName' | 'phone' | 'address') {
    await this.step(`Xóa ô ${field}`, async () => {
      await this.po.checkout[field].fill('');
    });
  }

  /** Chọn phương thức giao hàng: standard | express. */
  async chooseShipping(method: ShippingMethod) {
    await this.step(`Chọn giao hàng ${method}`, async () => {
      await this.po.checkout.chooseShipping(method);
    });
  }

  /** Chọn phương thức thanh toán: cod | bank | vnpay | momo. */
  async choosePayment(method: PaymentMethod) {
    await this.step(`Chọn thanh toán ${method}`, async () => {
      await this.po.checkout.choosePayment(method);
    });
  }

  /** Kiểm tra nút Thanh toán bật/tắt. */
  async verifySubmitEnabled(enabled: boolean) {
    await this.step(`Kiểm tra nút Thanh toán ${enabled ? 'bật' : 'tắt'}`, async () => {
      const btn = this.po.checkout.submitButton;
      await (enabled ? expect(btn).toBeEnabled() : expect(btn).toBeDisabled());
    });
  }

  /** Kiểm tra khối tóm tắt đơn hàng chứa đoạn chữ / số tiền. */
  async verifySummaryContains(text: string) {
    await this.step(`Kiểm tra tóm tắt đơn có "${text}"`, async () => {
      await expect(this.po.checkout.summarySection).toContainText(text);
    });
  }

  /** Giả lập API tạo đơn: thành công (orderNumber) hoặc lỗi (status + message). Lưu lại payload gửi lên. */
  async mockCreateOrder(options: { orderNumber?: string; status?: number; message?: string } = {}) {
    const status = options.status ?? 200;
    await this.step(`Mock API tạo đơn -> ${status}`, async () => {
      await this.page.route('**/api/orders', async (route) => {
        this.lastOrderPayload = route.request().postDataJSON();
        const json =
          status < 400
            ? { success: true, order: { id: 99999, order_number: options.orderNumber ?? 'E2E-000001' } }
            : { success: false, message: options.message ?? 'Lỗi' };
        await route.fulfill({ status, json });
      });
    });
  }

  /** Bấm nút Thanh toán. */
  async placeOrder() {
    await this.step('Bấm Thanh toán', async () => {
      await this.po.checkout.placeOrder();
    });
  }

  /** Kiểm tra trang đặt hàng thành công: tiêu đề + mã đơn (nếu có). */
  async verifyOrderSuccess(heading: string, orderNumber?: string) {
    await this.step(`Kiểm tra "${heading}"${orderNumber ? ` - mã ${orderNumber}` : ''}`, async () => {
      await expect(this.page).toHaveURL(ROUTES.orderSuccess);
      await expect(this.po.orderSuccess.heading).toHaveText(heading);
      if (orderNumber) await expect(this.po.orderSuccess.orderNumber(orderNumber)).toBeVisible();
    });
  }

  /** Kiểm tra payload đơn hàng gửi lên backend chứa các trường mong đợi. */
  async verifyLastOrderPayload(expected: Record<string, unknown>) {
    await this.step('Kiểm tra dữ liệu đơn hàng gửi lên server', async () => {
      expect(this.lastOrderPayload, 'Chưa bắt được request tạo đơn (gọi mockCreateOrder trước)').toBeTruthy();
      expect(this.lastOrderPayload).toMatchObject(expected);
    });
  }

  /** Kiểm tra vẫn ở trang thanh toán (đặt hàng thất bại). */
  async verifyStillOnCheckout() {
    await this.step('Kiểm tra vẫn ở trang thanh toán', async () => {
      await expect(this.page).toHaveURL(ROUTES.checkout);
    });
  }

  /** Mở /order-success trực tiếp và kiểm tra báo không có dữ liệu đơn. */
  async verifyOrderSuccessWithoutData() {
    await this.step('Kiểm tra /order-success không có dữ liệu', async () => {
      await this.po.orderSuccess.goto();
      await expect(this.po.orderSuccess.notFound).toBeVisible();
    });
  }
}
