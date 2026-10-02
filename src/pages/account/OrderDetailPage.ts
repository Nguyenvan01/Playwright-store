import { Locator, Page } from '@playwright/test';
import { cssText, escapeRegex } from './cssText';

/** Trang /orders/:id (OrderDetailPage.jsx). Tiêu đề khối h2 có chữ icon phía trước, vd: "receipt_long Thông tin đơn hàng". */
export class OrderDetailPage {
  readonly heading: Locator;
  readonly backLink: Locator;
  readonly statusValue: Locator;
  readonly paymentStatusValue: Locator;
  readonly itemsHeading: Locator;
  readonly itemsCard: Locator;
  readonly itemRows: Locator;
  readonly cancelButton: Locator;
  readonly cancelModal: Locator;
  readonly cancelReason: Locator;
  readonly confirmCancelButton: Locator;
  readonly closeCancelButton: Locator;
  readonly backToOrdersLink: Locator;

  constructor(readonly page: Page) {
    this.heading = page.getByRole('heading', { level: 1 });
    this.backLink = page.getByRole('link', { name: 'arrow_back Quay lại', exact: true });
    this.statusValue = page.locator('p:text-is("Trạng thái đơn hàng") + p');
    this.paymentStatusValue = page.locator('p:text-is("Thanh toán") + p');
    this.itemsHeading = page.getByRole('heading', { level: 2, name: /^Sản phẩm đã đặt \(\d+\)$/ });
    this.itemsCard = this.card('Sản phẩm đã đặt');
    this.itemRows = this.itemsCard.locator('div.divide-y > div');
    this.cancelButton = page.getByRole('button', { name: 'Hủy đơn hàng', exact: true });
    this.cancelModal = page
      .locator('div.fixed.inset-0')
      .filter({ hasText: 'Bạn có chắc muốn hủy đơn hàng này? Hành động này không thể hoàn tác.' });
    this.cancelReason = this.cancelModal.getByPlaceholder('Lý do hủy (tùy chọn)');
    this.confirmCancelButton = this.cancelModal.getByRole('button', { name: /^(Xác nhận hủy|Đang hủy\.\.\.)$/ });
    this.closeCancelButton = this.cancelModal.getByRole('button', { name: 'Đóng', exact: true });
    this.backToOrdersLink = page.getByRole('link', { name: 'Quay lại đơn hàng', exact: true });
  }

  /** Khối (card) theo tiêu đề h2, vd: "Thông tin giao hàng", "Chi tiết thanh toán". */
  card(title: string): Locator {
    return this.page
      .locator('main div.rounded-lg')
      .filter({ has: this.page.getByRole('heading', { level: 2, name: new RegExp(`(^|\\s)${escapeRegex(title)}`) }) });
  }

  /** Giá trị của 1 dòng "nhãn - giá trị" trong khối. */
  rowValue(cardTitle: string, label: string): Locator {
    return this.card(cardTitle).locator(`span:text-is("${cssText(label)}") + span`);
  }

  itemRow(name: string): Locator {
    return this.itemRows.filter({ has: this.page.getByText(name, { exact: true }) });
  }

  message(text: string): Locator {
    return this.page.locator('main').getByText(text, { exact: true });
  }
}
