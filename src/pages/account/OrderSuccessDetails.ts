import { Locator, Page } from '@playwright/test';
import { cssText } from './cssText';

/** Chi tiết trên trang /order-success (OrderSuccessPage.jsx) khi có dữ liệu đơn. */
export class OrderSuccessDetails {
  readonly main: Locator;
  readonly orderNumber: Locator;
  readonly continueLinks: Locator;
  readonly viewOrdersLink: Locator;

  constructor(readonly page: Page) {
    this.main = page.locator('main');
    this.orderNumber = this.main.locator('span:text-is("Mã đơn hàng:") + span');
    this.continueLinks = this.main.getByRole('link', { name: 'Tiếp tục mua sắm', exact: true });
    this.viewOrdersLink = this.main.getByRole('link', { name: 'Xem đơn hàng', exact: true });
  }

  /** Khối theo tiêu đề h2: "Thông tin thanh toán" | "Người nhận" | "Chi tiết thanh toán". */
  card(title: string): Locator {
    return this.main
      .locator('div.rounded-2xl')
      .filter({ has: this.page.getByRole('heading', { level: 2, name: title, exact: true }) });
  }

  rowValue(cardTitle: string, label: string): Locator {
    return this.card(cardTitle).locator(`span:text-is("${cssText(label)}") + span`);
  }
}
