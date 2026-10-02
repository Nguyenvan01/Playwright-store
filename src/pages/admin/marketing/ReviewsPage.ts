import { Locator, Page } from '@playwright/test';
import { AdminTable } from './AdminTable';

/** Trang quản trị Đánh giá (/admin/reviews). */
export class ReviewsPage extends AdminTable {
  readonly path = '/admin/reviews';
  readonly searchPlaceholder = 'Tìm khách hàng, sản phẩm, nội dung...';

  constructor(page: Page) {
    super(page);
  }

  /** Tiêu đề riêng của trang (h1 trong main, trùng chữ với h1 trên header). */
  get pageHeading(): Locator {
    return this.page.locator('main h1');
  }

  get statusSelect(): Locator {
    return this.selectWithOption('pending');
  }

  get ratingSelect(): Locator {
    return this.selectWithOption('5');
  }

  /** Hết skeleton: có dòng dữ liệu hoặc dòng trạng thái rỗng. */
  get listReady(): Locator {
    return this.table.locator('tbody tr td p, tbody tr td button').first();
  }
}
