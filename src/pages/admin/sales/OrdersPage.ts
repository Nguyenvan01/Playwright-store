import { Locator, Page } from '@playwright/test';
import { AdminUi } from '../AdminUi';
import { modalByHeading, paginationBar } from './AdminApiMock';

const escapeRe = (s: string) => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');

/** Trang Đơn hàng (/admin/orders): thẻ trạng thái, bộ lọc, bảng, modal chi tiết, modal hủy đơn. */
export class OrdersPage {
  readonly path = '/admin/orders';
  readonly ui: AdminUi;
  readonly searchInput: Locator;
  readonly statusSelect: Locator;
  readonly paymentSelect: Locator;
  readonly filtersButton: Locator;
  readonly clearFiltersButton: Locator;
  readonly totalText: Locator;
  readonly emptyText: Locator;
  readonly detailModal: Locator;
  readonly cancelModal: Locator;
  readonly cancelReason: Locator;

  constructor(readonly page: Page) {
    this.ui = new AdminUi(page);
    this.searchInput = page.getByPlaceholder('Tìm mã đơn, tên, SĐT, email...', { exact: true });
    this.statusSelect = page.locator('select').filter({ has: page.locator('option', { hasText: 'Tất cả trạng thái' }) });
    this.paymentSelect = page.locator('select').filter({ has: page.locator('option', { hasText: 'Tất cả TT thanh toán' }) });
    this.filtersButton = page.getByRole('button', { name: 'Bộ lọc', exact: true });
    this.clearFiltersButton = page.getByRole('button', { name: 'Xóa bộ lọc', exact: true });
    this.totalText = page.locator('main').getByText(/^\d+ đơn hàng$/);
    this.emptyText = page.getByText('Không có đơn hàng nào', { exact: true });
    this.detailModal = modalByHeading(page, /^Chi tiết đơn hàng #/);
    this.cancelModal = modalByHeading(page, 'Hủy đơn hàng');
    this.cancelReason = page.getByPlaceholder('Nhập lý do hủy đơn hàng...', { exact: true });
  }

  /** Thẻ thống kê trạng thái (nút gồm nhãn + số lượng). */
  statusCard(label: string): Locator {
    return this.page.getByRole('button', { name: new RegExp(`^${escapeRe(label)}\\s*\\d+$`) });
  }

  statusCardCount(label: string): Locator {
    return this.statusCard(label).locator('p');
  }

  dateInput(label: 'Từ ngày' | 'Đến ngày'): Locator {
    return this.ui.field(label);
  }

  row(orderNumber: string): Locator {
    return this.page.locator('tbody tr').filter({ has: this.page.getByText(orderNumber, { exact: true }) }).first();
  }

  get orderNumbers(): Locator {
    return this.page.locator('main tbody tr > td:first-child > span.font-bold');
  }

  rowPayment(orderNumber: string): Locator {
    return this.row(orderNumber).locator('td').nth(5);
  }

  rowStatus(orderNumber: string): Locator {
    return this.row(orderNumber).locator('td').nth(6);
  }

  rowAction(orderNumber: string, title: 'Xem chi tiết' | 'Hủy đơn'): Locator {
    return this.row(orderNumber).getByTitle(title, { exact: true });
  }

  // --- Modal chi tiết ---
  get detailHeading(): Locator {
    return this.detailModal.getByRole('heading', { level: 3 });
  }

  get detailCloseButton(): Locator {
    return this.detailModal.getByRole('button').first();
  }

  /** Huy hiệu trạng thái đơn trên đầu modal. */
  get detailStatusBadge(): Locator {
    return this.detailModal.locator('div.sticky span.rounded-full').first();
  }

  get detailPaymentBadge(): Locator {
    return this.detailModal.locator('div.sticky span.rounded-full').nth(1);
  }

  /** Ô thông tin nhỏ trong modal, vd: "Phương thức thanh toán" -> giá trị. */
  detailInfo(label: string): Locator {
    return this.detailModal
      .locator('div.bg-gray-50.rounded-xl')
      .filter({ has: this.page.locator('p', { hasText: new RegExp(`^${escapeRe(label)}$`) }) })
      .locator('p.font-semibold');
  }

  detailBlock(heading: string): Locator {
    return this.detailModal
      .locator('div.rounded-xl.p-4')
      .filter({ has: this.page.getByRole('heading', { name: heading, exact: true }) })
      .first();
  }

  get statusSection(): Locator {
    return this.detailBlock('Cập nhật trạng thái đơn hàng');
  }

  get statusButtons(): Locator {
    return this.statusSection.getByRole('button');
  }

  get paymentSection(): Locator {
    return this.detailBlock('Cập nhật thanh toán');
  }

  get detailPaymentSelect(): Locator {
    return this.paymentSection.locator('select');
  }

  get processingWarning(): Locator {
    return this.detailModal.getByText('Lưu ý khi xử lý', { exact: true });
  }

  get detailItems(): Locator {
    return this.detailModal.locator('tbody tr');
  }

  /** Dòng tổng kết (Tạm tính / Phí vận chuyển / Tổng thanh toán...) -> giá trị. */
  summaryValue(label: string): Locator {
    return this.detailModal
      .locator('div.flex.justify-between')
      .filter({ has: this.page.getByText(label, { exact: true }) })
      .locator('span')
      .last();
  }

  get detailLogs(): Locator {
    return this.detailModal.locator('div.space-y-2 > div.flex.items-start');
  }

  // --- Modal hủy ---
  get cancelNotes(): Locator {
    return this.cancelModal.locator('div.bg-amber-50 p');
  }

  // --- Phân trang ---
  get pagination(): Locator {
    return paginationBar(this.page);
  }

  pageButton(n: number): Locator {
    return this.pagination.getByRole('button', { name: String(n), exact: true });
  }
}
