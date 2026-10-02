import { Locator, Page } from '@playwright/test';
import { BasePage } from '../BasePage';

export class AdminLoginPage extends BasePage {
  readonly path = '/admin/login';
  readonly heading: Locator;
  readonly emailInput: Locator;
  readonly passwordInput: Locator;
  readonly submitButton: Locator;
  readonly errorMessage: Locator;
  readonly backToStoreLink: Locator;

  constructor(page: Page) {
    super(page);
    this.heading = page.getByRole('heading', { name: 'Đạt Hoàng Admin' });
    this.emailInput = page.getByPlaceholder('admin@clothing-store.vn');
    this.passwordInput = page.getByPlaceholder('Nhập mật khẩu admin');
    this.submitButton = page.getByRole('button', { name: /^Đăng nhập$|Đang đăng nhập/ });
    this.errorMessage = page.locator('form .bg-red-50');
    this.backToStoreLink = page.getByRole('link', { name: /Quay về cửa hàng/ });
  }

  async login(email: string, password: string) {
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
    await this.submitButton.click();
  }
}
