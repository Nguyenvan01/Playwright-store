import { Locator, Page } from '@playwright/test';
import { AdminTable } from './AdminTable';

/** Trang quản trị Liên hệ (/admin/contacts). */
export class ContactsPage extends AdminTable {
  readonly path = '/admin/contacts';
  readonly searchPlaceholder = 'Tìm theo tên, email, số điện thoại, nội dung...';

  constructor(page: Page) {
    super(page);
  }

  get pageHeading(): Locator {
    return this.page.locator('main h1');
  }

  get statusSelect(): Locator {
    return this.selectWithOption('processed');
  }

  get listReady(): Locator {
    return this.table.locator('tbody tr td p, tbody tr td button').first();
  }
}
