import { Locator, Page } from '@playwright/test';
import { AdminTable } from './AdminTable';

/** Trang quản trị Mã giảm giá (/admin/coupons) - nút sửa/xóa/bật tắt không có tên. */
export class CouponsPage extends AdminTable {
  readonly path = '/admin/coupons';

  constructor(page: Page) {
    super(page);
  }

  get addButton(): Locator {
    return this.page.getByRole('button', { name: 'Thêm mã', exact: true });
  }

  get emptyText(): Locator {
    return this.page.getByText('Chưa có mã giảm giá nào', { exact: true });
  }

  get listReady(): Locator {
    return this.table.or(this.emptyText).first();
  }

  /** Nút sửa (icon, không tên) trong cột Thao tác. */
  editButton(code: string): Locator {
    return this.row(code).locator('td').last().getByRole('button').nth(0);
  }

  /** Nút xóa (icon, không tên) trong cột Thao tác. */
  deleteButton(code: string): Locator {
    return this.row(code).locator('td').last().getByRole('button').nth(1);
  }

  /** Nút bật/tắt (icon, không tên) trong cột "Công khai" hoặc "Trạng thái". */
  async toggleButton(code: string, column: string): Promise<Locator> {
    return (await this.cell(code, column)).getByRole('button');
  }
}
