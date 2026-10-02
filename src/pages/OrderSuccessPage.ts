import { Locator, Page } from '@playwright/test';
import { BasePage } from './BasePage';

export class OrderSuccessPage extends BasePage {
  readonly path = '/order-success';
  readonly heading: Locator;
  readonly notFound: Locator;

  constructor(page: Page) {
    super(page);
    this.heading = page.getByRole('heading', { level: 1 });
    this.notFound = page.getByRole('heading', { name: 'Không tìm thấy thông tin đơn hàng' });
  }

  orderNumber(value: string): Locator {
    return this.page.getByText(value);
  }
}
