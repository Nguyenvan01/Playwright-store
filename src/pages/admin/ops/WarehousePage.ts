import { Locator, Page } from '@playwright/test';
import { AdminTable } from '../marketing/AdminTable';

/** Trang quản trị Kho hàng (/admin/warehouse). */
export class WarehousePage extends AdminTable {
  readonly path = '/admin/warehouse';
  readonly searchPlaceholder = 'Tìm kiếm sản phẩm, SKU, danh mục...';

  constructor(page: Page) {
    super(page);
  }

  /** Nút tab lọc ("Tất cả", "Sắp hết", "Hết hàng") - tên nút có kèm số đếm. */
  tab(label: string): Locator {
    return this.page.getByRole('button', { name: new RegExp(`^${label}(\\s+\\d+)?$`) });
  }

  /** Số đếm (badge) trên tab. */
  tabBadge(label: string): Locator {
    return this.tab(label).locator('span');
  }

  get emptyText(): Locator {
    return this.page.getByText('Không tìm thấy sản phẩm phù hợp.', { exact: true });
  }

  /** Hết skeleton: có tên sản phẩm hoặc dòng rỗng. */
  get listReady(): Locator {
    return this.table.locator('tbody tr td p, tbody tr td[colspan]').first();
  }
}
