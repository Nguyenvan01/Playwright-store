import { Locator, Page } from '@playwright/test';

/** Modal "Đổi mật khẩu" trên trang hồ sơ (PasswordModal trong ProfilePage.jsx) - không có role=dialog. */
export class PasswordModal {
  readonly root: Locator;
  readonly heading: Locator;
  readonly currentPassword: Locator;
  readonly newPassword: Locator;
  readonly confirmPassword: Locator;
  readonly submitButton: Locator;
  readonly cancelButton: Locator;
  /** Nút chữ "Đóng" ở góc trên (khác nút nền mờ cũng có aria-label "Đóng"). */
  readonly closeButton: Locator;
  readonly backdrop: Locator;
  readonly error: Locator;

  constructor(readonly page: Page) {
    this.heading = page.getByRole('heading', { level: 3, name: 'Đổi mật khẩu' });
    this.root = page.locator('div.fixed.inset-0').filter({ has: this.heading });
    this.currentPassword = this.root.getByPlaceholder('Nhập mật khẩu hiện tại');
    this.newPassword = this.root.getByPlaceholder('Ít nhất 6 ký tự');
    this.confirmPassword = this.root.getByPlaceholder('Nhập lại mật khẩu mới');
    this.submitButton = this.root.getByRole('button', { name: /^(Xác nhận|Đang xử lý\.\.\.)$/ });
    this.cancelButton = this.root.getByRole('button', { name: 'Hủy', exact: true });
    this.closeButton = this.root.locator('button:text-is("Đóng")');
    this.backdrop = this.root.locator('button[aria-label="Đóng"]');
    this.error = this.root.locator('form .bg-red-50');
  }
}
