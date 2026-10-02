import { expect } from '@playwright/test';
import { env } from '@config/env';
import { ROUTES } from '@data/routes';
import type { RegisterForm } from '@data/types';
import { STORAGE_KEYS, detectReload } from '@utils/storage';
import { BaseKeywords } from './BaseKeywords';

export type Role = 'customer' | 'admin';

export class AuthKeywords extends BaseKeywords {
  /** Mở trang đăng nhập khách hàng. */
  async openLogin() {
    await this.step('Mở trang đăng nhập', async () => {
      await this.po.login.goto();
      await expect(this.po.login.heading).toHaveText('Đăng nhập');
    });
  }

  /** Nhập email/SĐT + mật khẩu và bấm ĐĂNG NHẬP. */
  async login(identifier: string, password: string) {
    await this.step(`Đăng nhập với "${identifier}"`, async () => {
      await this.po.login.login(identifier, password);
    });
  }

  /** Đăng nhập bằng tài khoản khách hàng test trong .env và chờ vào trang hồ sơ. */
  async loginAsCustomer() {
    await this.step('Đăng nhập tài khoản khách hàng test', async () => {
      expect(env.customer.email, 'Chưa cấu hình E2E_CUSTOMER_EMAIL').toBeTruthy();
      await this.po.login.goto();
      await this.po.login.login(env.customer.email, env.customer.password);
      await expect(this.page).toHaveURL(ROUTES.profile);
    });
  }

  /** Đăng nhập sẵn qua API (không qua UI) - phải gọi TRƯỚC lần mở trang đầu tiên. */
  async restoreSession(role: Role) {
    await this.step(`Khôi phục phiên đăng nhập ${role} qua API`, async () => {
      const entries: Record<string, string> = {};
      if (role === 'customer') {
        const auth = await this.api.customerLogin(env.customer.email, env.customer.password);
        entries[STORAGE_KEYS.customerToken] = auth.token;
        entries[STORAGE_KEYS.customerUser] = JSON.stringify(auth.user);
      } else {
        const auth = await this.api.adminLogin(env.admin.email, env.admin.password);
        entries[STORAGE_KEYS.adminToken] = auth.token;
      }
      await this.page.addInitScript((data) => {
        if (sessionStorage.getItem('__e2e_session')) return;
        for (const [k, v] of Object.entries(data)) localStorage.setItem(k, v);
        sessionStorage.setItem('__e2e_session', '1');
      }, entries);
    });
  }

  /** Chuyển form sang chế độ Đăng ký. */
  async openRegisterForm() {
    await this.step('Chuyển sang form đăng ký', async () => {
      await this.po.login.switchToRegister.click();
      await expect(this.po.login.heading).toHaveText('Tạo tài khoản');
    });
  }

  /** Điền form đăng ký và bấm TẠO TÀI KHOẢN (form phải đang mở). */
  async submitRegisterForm(form: RegisterForm) {
    await this.step(`Đăng ký tài khoản "${form.email}"`, async () => {
      const lp = this.po.login;
      await lp.nameInput.fill(form.name);
      await lp.identifierInput.fill(form.email);
      await lp.phoneInput.fill(form.phone);
      await lp.passwordInput.fill(form.password);
      await lp.confirmPasswordInput.fill(form.confirmPassword ?? form.password);
      await lp.registerButton.click();
    });
  }

  /** Kiểm tra các thông báo lỗi dưới từng ô nhập. */
  async verifyFieldErrors(messages: string[]) {
    await this.step(`Kiểm tra lỗi field: ${messages.join(' | ')}`, async () => {
      for (const m of messages) await expect(this.po.login.fieldError(m)).toBeVisible();
    });
  }

  /** Kiểm tra thông báo lỗi chung (lỗi từ server) trên form đăng nhập/đăng ký. */
  async verifyGeneralError(message: string) {
    await this.step(`Kiểm tra lỗi chung "${message}"`, async () => {
      await expect(this.po.login.generalError).toContainText(message);
    });
  }

  /** Đăng nhập sai và kiểm tra thông báo lỗi vẫn hiển thị (trang không bị reload). */
  async loginExpectingError(identifier: string, password: string, message: string) {
    await this.step(`Đăng nhập "${identifier}" và chờ lỗi "${message}"`, async () => {
      const reloaded = detectReload(this.page);
      await this.po.login.login(identifier, password);
      expect(await reloaded, 'Trang bị reload sau khi đăng nhập sai').toBe(false);
      await expect(this.po.login.generalError).toContainText(message);
      await expect(this.page).toHaveURL(ROUTES.login);
    });
  }

  /** Giả lập API đăng nhập thành công với user cho trước (kèm các API trang hồ sơ). */
  async mockLoginSuccess(user: Record<string, unknown>) {
    await this.step('Mock API đăng nhập thành công', async () => {
      await this.page.route('**/api/auth/login', (route) =>
        route.fulfill({ json: { success: true, token: 'mock-token', user } }),
      );
      await this.page.route(/\/api\/(profile|orders|wishlist|addresses)(\?.*)?$/, (route) =>
        route.fulfill({ json: { success: true, user, data: [], orders: [], wishlist: [], addresses: [] } }),
      );
    });
  }

  /** Giả lập API đăng ký trả lỗi (status + message). */
  async mockRegisterError(status: number, message: string) {
    await this.step(`Mock API đăng ký lỗi ${status}`, async () => {
      await this.page.route('**/api/auth/register', (route) =>
        route.fulfill({ status, json: { success: false, message } }),
      );
    });
  }

  /** Bấm nút hiện/ẩn mật khẩu và kiểm tra trạng thái hiển thị. */
  async togglePassword(expectVisible: boolean) {
    await this.step(`Bật/tắt hiện mật khẩu -> ${expectVisible ? 'hiện' : 'ẩn'}`, async () => {
      await this.po.login.togglePassword.click();
      await expect(this.po.login.passwordInput).toHaveAttribute('type', expectVisible ? 'text' : 'password');
    });
  }

  /** Kiểm tra menu tài khoản trên header hiển thị đúng email. */
  async verifyLoggedInAs(email: string) {
    await this.step(`Kiểm tra đang đăng nhập "${email}"`, async () => {
      const header = this.po.header;
      await header.userMenuButton.click();
      await expect(header.root.getByText(email)).toBeVisible();
      // Menu không đóng bằng ESC -> bấm lại nút để đóng, tránh ảnh hưởng bước sau
      await header.userMenuButton.click();
      await expect(header.root.getByText(email)).toBeHidden();
    });
  }

  /** Đăng xuất qua menu tài khoản trên header. */
  async logout() {
    await this.step('Đăng xuất', async () => {
      await this.po.header.logout();
    });
  }

  /** Kiểm tra đã đăng xuất: về trang chủ, có link đăng nhập, token bị xóa. */
  async verifyLoggedOut() {
    await this.step('Kiểm tra đã đăng xuất', async () => {
      await expect(this.page).toHaveURL(ROUTES.home);
      await expect(this.po.header.loginLink).toBeVisible();
      const token = await this.page.evaluate((k) => localStorage.getItem(k), STORAGE_KEYS.customerToken);
      expect(token).toBeNull();
    });
  }

  /** Kiểm tra token khách hàng trong localStorage bằng giá trị mong đợi. */
  async verifyStoredToken(expected: string) {
    await this.step('Kiểm tra token đã lưu', async () => {
      const token = await this.page.evaluate((k) => localStorage.getItem(k), STORAGE_KEYS.customerToken);
      expect(token).toBe(expected);
    });
  }
}
