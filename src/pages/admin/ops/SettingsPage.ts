import { Locator, Page } from '@playwright/test';
import { AdminTable } from '../marketing/AdminTable';

/** Trang quản trị Cài đặt (/admin/settings). */
export class SettingsPage extends AdminTable {
  readonly path = '/admin/settings';

  constructor(page: Page) {
    super(page);
  }

  get pageHeading(): Locator {
    return this.page.locator('main h1');
  }

  get saveButton(): Locator {
    return this.page.getByRole('button', { name: /^(Lưu cài đặt|Đang lưu\.\.\.)$/ });
  }

  tab(label: string): Locator {
    return this.page.getByRole('button', { name: label, exact: true });
  }

  /** Khung nội dung tab (chứa tiêu đề tab đang mở + các ô nhập). */
  get panel(): Locator {
    return this.page.locator('main div.rounded-xl > div.p-6').first();
  }

  /** Nhãn của các ô nhập trong tab đang mở. */
  get fieldLabels(): Locator {
    return this.panel.locator('label');
  }

  /** Tab đã tải xong dữ liệu (không còn skeleton). */
  get panelReady(): Locator {
    return this.panel.locator('label').first();
  }
}
