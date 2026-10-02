import { Locator, Page } from '@playwright/test';
import { AdminTable } from '../marketing/AdminTable';

/** Trang quản trị Nhập hàng (/admin/import). */
export class ImportPage extends AdminTable {
  readonly path = '/admin/import';
  readonly searchPlaceholder = 'Tìm mã đơn, nhà cung cấp...';
  readonly createHeading = 'Tạo đơn nhập hàng';

  constructor(page: Page) {
    super(page);
  }

  get pageHeading(): Locator {
    return this.page.locator('main h2').first();
  }

  get createButton(): Locator {
    return this.page.getByRole('button', { name: 'Tạo đơn nhập hàng', exact: true }).first();
  }

  get statusFilter(): Locator {
    return this.selectWithOption('partial_received');
  }

  /** Select nhà cung cấp ở thanh lọc (option đầu "Tất cả NCC"). */
  get supplierFilter(): Locator {
    return this.page.locator('select').filter({ hasText: 'Tất cả NCC' }).first();
  }

  get createModal(): Locator {
    return this.modal(this.createHeading);
  }

  /** Dòng sản phẩm thứ `index` trong bảng sản phẩm nhập của modal tạo đơn. */
  itemRow(index: number): Locator {
    return this.createModal.locator('table tbody tr').nth(index);
  }

  itemProduct(index: number): Locator {
    return this.itemRow(index).locator('select').nth(0);
  }

  itemVariant(index: number): Locator {
    return this.itemRow(index).locator('select').nth(1);
  }

  /** Các ô input của dòng: 0 = SKU, 1 = Số lượng, 2 = Đơn giá, 3 = Ghi chú. */
  itemInput(index: number, position: number): Locator {
    return this.itemRow(index).locator('input').nth(position);
  }

  /** Thành tiền của dòng sản phẩm nhập. */
  itemLineTotal(index: number): Locator {
    return this.itemRow(index).locator('td').nth(5);
  }

  /** Giá trị "Tổng tiền nhập" trong modal tạo đơn. */
  get grandTotal(): Locator {
    return this.createModal.getByText('Tổng tiền nhập', { exact: true }).locator('xpath=following-sibling::span[1]');
  }

  /** Ô "SL thực nhận" của dòng thứ `index` trong modal Nhận hàng. */
  receiveInput(index: number): Locator {
    return this.modal('Nhận hàng').locator('table tbody tr').nth(index).locator('input');
  }

  get listReady(): Locator {
    return this.table.locator('tbody tr td span, tbody tr td[colspan]').first();
  }
}
