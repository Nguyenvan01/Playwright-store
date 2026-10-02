import { Locator, Page } from '@playwright/test';

export abstract class BasePage {
  /** Vùng chứa toast (ToastContext) ở góc trên phải. */
  readonly toasts: Locator;

  constructor(readonly page: Page) {
    this.toasts = page.locator('div.fixed.top-4.right-4');
  }

  /** URL tương đối của trang (để trống nếu trang cần tham số, vd: product/:slug). */
  abstract readonly path: string;

  async goto(path = this.path) {
    await this.page.goto(path);
  }

  toast(message: string | RegExp): Locator {
    return this.toasts.getByText(message);
  }
}
