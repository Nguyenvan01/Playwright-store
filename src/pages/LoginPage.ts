import { Locator, Page } from '@playwright/test';
import { BasePage } from './BasePage';

/** Trang /login - dùng chung cho Đăng nhập và Đăng ký (chuyển bằng nút "Đăng ký ngay"). */
export class LoginPage extends BasePage {
  readonly path = '/login';
  readonly heading: Locator;
  readonly nameInput: Locator;
  readonly identifierInput: Locator;
  readonly phoneInput: Locator;
  readonly passwordInput: Locator;
  readonly confirmPasswordInput: Locator;
  readonly rememberMe: Locator;
  readonly loginButton: Locator;
  readonly registerButton: Locator;
  readonly switchToRegister: Locator;
  readonly switchToLogin: Locator;
  readonly togglePassword: Locator;
  readonly generalError: Locator;

  constructor(page: Page) {
    super(page);
    this.heading = page.getByRole('heading', { level: 1 });
    this.nameInput = page.getByPlaceholder('Nguyễn Văn A');
    this.identifierInput = page.getByPlaceholder('Nhập email hoặc số điện thoại');
    this.phoneInput = page.getByPlaceholder('0912 345 678');
    this.passwordInput = page.getByPlaceholder('Nhập mật khẩu', { exact: true });
    this.confirmPasswordInput = page.getByPlaceholder('Nhập lại mật khẩu');
    this.rememberMe = page.getByLabel('Ghi nhớ đăng nhập');
    this.loginButton = page.getByRole('button', { name: 'ĐĂNG NHẬP', exact: true });
    this.registerButton = page.getByRole('button', { name: 'TẠO TÀI KHOẢN', exact: true });
    this.switchToRegister = page.getByRole('button', { name: 'Đăng ký ngay' });
    this.switchToLogin = page.locator('.register-link').getByRole('button', { name: 'Đăng nhập' });
    this.togglePassword = page.getByRole('button', { name: /(Hiện|Ẩn) mật khẩu/ });
    this.generalError = page.locator('.login-card .bg-red-50');
  }

  fieldError(message: string): Locator {
    return this.page.locator('.form-error', { hasText: message });
  }

  async login(identifier: string, password: string) {
    await this.identifierInput.fill(identifier);
    await this.passwordInput.fill(password);
    await this.loginButton.click();
  }

  async register(data: { name: string; email: string; phone: string; password: string; confirmPassword?: string }) {
    await this.switchToRegister.click();
    await this.nameInput.fill(data.name);
    await this.identifierInput.fill(data.email);
    await this.phoneInput.fill(data.phone);
    await this.passwordInput.fill(data.password);
    await this.confirmPasswordInput.fill(data.confirmPassword ?? data.password);
    await this.registerButton.click();
  }
}
