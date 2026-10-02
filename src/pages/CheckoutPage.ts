import { Locator, Page } from '@playwright/test';
import { BasePage } from './BasePage';
import type { ShippingInfo } from '@data/factories';

export type ShippingMethod = 'standard' | 'express';
export type PaymentMethod = 'cod' | 'bank' | 'vnpay' | 'momo';

export class CheckoutPage extends BasePage {
  readonly path = '/checkout';
  readonly firstName: Locator;
  readonly lastName: Locator;
  readonly phone: Locator;
  readonly city: Locator;
  readonly district: Locator;
  readonly ward: Locator;
  readonly address: Locator;
  readonly submitButton: Locator;
  readonly emptyCartHeading: Locator;
  readonly loginButton: Locator;
  readonly productsSection: Locator;
  readonly summarySection: Locator;

  constructor(page: Page) {
    super(page);
    this.firstName = page.getByLabel('Họ', { exact: true });
    this.lastName = page.getByLabel('Tên', { exact: true });
    this.phone = page.locator('#phone');
    this.city = page.getByLabel('Tỉnh / Thành phố');
    this.district = page.getByLabel('Quận / Huyện');
    this.ward = page.getByLabel('Phường / Xã');
    this.address = page.getByLabel('Địa chỉ chi tiết');
    this.submitButton = page.getByRole('button', { name: 'Thanh toán', exact: true });
    this.emptyCartHeading = page.getByRole('heading', { name: 'Giỏ hàng trống' });
    this.loginButton = page.getByRole('button', { name: 'Đăng nhập / Đăng ký' });
    this.productsSection = page.locator('section[aria-labelledby="product-title"]');
    this.summarySection = page.locator('section[aria-labelledby="summary-title"]');
  }

  async fillShipping(info: ShippingInfo) {
    await this.firstName.fill(info.firstName);
    await this.lastName.fill(info.lastName);
    await this.phone.fill(info.phone);
    await this.city.selectOption(info.city);
    await this.district.selectOption(info.district);
    if (info.ward) await this.ward.selectOption(info.ward);
    await this.address.fill(info.address);
  }

  async chooseShipping(method: ShippingMethod) {
    await this.page.locator('label.ck-shipping-option').filter({
      has: this.page.locator(`input[value="${method}"]`),
    }).click();
  }

  async choosePayment(method: PaymentMethod) {
    await this.page.locator('label.ck-payment-option').filter({
      has: this.page.locator(`input[value="${method}"]`),
    }).click();
  }

  async placeOrder() {
    await this.submitButton.click();
  }
}
