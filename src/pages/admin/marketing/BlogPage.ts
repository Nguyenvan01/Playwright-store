import { Locator, Page } from '@playwright/test';
import { AdminTable } from './AdminTable';

/** Trang quản trị Bài viết (/admin/blog). */
export class BlogPage extends AdminTable {
  readonly path = '/admin/blog';
  readonly searchPlaceholder = 'Tìm theo tiêu đề, slug, mô tả...';

  constructor(page: Page) {
    super(page);
  }

  get pageHeading(): Locator {
    return this.page.locator('main h1');
  }

  get addButton(): Locator {
    return this.page.getByRole('button', { name: 'Thêm bài viết', exact: true });
  }

  get imageUrlInput(): Locator {
    return this.page.getByPlaceholder('Dán URL ảnh...', { exact: true });
  }

  get imagePreview(): Locator {
    return this.page.getByRole('img', { name: 'Xem trước ảnh bài viết' });
  }

  get listReady(): Locator {
    return this.table.locator('tbody tr td p, tbody tr td button').first();
  }
}
