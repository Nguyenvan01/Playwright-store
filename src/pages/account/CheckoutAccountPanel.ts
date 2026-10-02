import { Locator, Page } from '@playwright/test';

/** Khối "Đăng nhập / Đăng ký" trên /checkout khi đã đăng nhập (CheckoutPage.jsx: .ck-auth-user). */
export class CheckoutAccountPanel {
  readonly root: Locator;
  readonly name: Locator;
  readonly email: Locator;
  readonly logoutButton: Locator;

  constructor(readonly page: Page) {
    this.root = page.locator('.ck-auth-user');
    this.name = this.root.locator('.ck-auth-user-name');
    this.email = this.root.locator('.ck-auth-user-email');
    this.logoutButton = this.root.getByRole('button', { name: 'Đăng xuất', exact: true });
  }
}
