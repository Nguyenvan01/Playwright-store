import { Locator, Page } from '@playwright/test';
import { BasePage } from '../BasePage';

/** Khung trang quản trị: sidebar + header có tiêu đề trang. */
export class AdminLayout extends BasePage {
  readonly path = '/admin';
  readonly sidebar: Locator;
  readonly pageTitle: Locator;

  constructor(page: Page) {
    super(page);
    this.sidebar = page.locator('aside').first();
    this.pageTitle = page.locator('header h1');
  }

  menuLink(label: string): Locator {
    return this.sidebar.getByRole('link', { name: label, exact: true });
  }

  async navigateTo(label: string) {
    await this.menuLink(label).click();
  }
}
