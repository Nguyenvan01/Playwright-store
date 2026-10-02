import { Locator, Page } from '@playwright/test';
import { AdminTable } from './AdminTable';

/** Trang quản trị Khuyến mãi (/admin/promotions) - có cả bảng desktop và thẻ mobile trong DOM. */
export class PromotionsPage extends AdminTable {
  readonly path = '/admin/promotions';
  readonly searchPlaceholder = 'Tìm theo tên, mô tả hoặc trạng thái';

  constructor(page: Page) {
    super(page);
  }

  get listHeading(): Locator {
    return this.page.getByRole('heading', { name: 'Danh sách khuyến mãi', exact: true });
  }

  /** Nút "Thêm khuyến mãi" trên đầu trang (không phải nút trong trạng thái rỗng). */
  get addButton(): Locator {
    return this.page.getByRole('button', { name: 'Thêm khuyến mãi', exact: true }).first();
  }

  /** Khung danh sách đã tải xong (bảng, trạng thái rỗng hoặc không tìm thấy). */
  get listReady(): Locator {
    return this.table
      .or(this.page.getByRole('heading', { name: 'Chưa có khuyến mãi nào' }))
      .or(this.page.getByRole('heading', { name: 'Không tìm thấy khuyến mãi phù hợp.' }))
      .first();
  }
}
