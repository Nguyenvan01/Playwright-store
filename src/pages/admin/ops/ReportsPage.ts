import { Locator, Page } from '@playwright/test';
import { AdminTable } from '../marketing/AdminTable';

/** Trang quản trị Báo cáo (/admin/reports). */
export class ReportsPage extends AdminTable {
  readonly path = '/admin/reports';

  constructor(page: Page) {
    super(page);
  }

  get pageHeading(): Locator {
    return this.page.locator('main h1');
  }

  /** Select chọn kỳ báo cáo (có option "custom"). */
  get periodSelect(): Locator {
    return this.selectWithOption('custom');
  }

  get dateInputs(): Locator {
    return this.page.locator('main input[type="date"]');
  }

  get filterButton(): Locator {
    return this.page.getByRole('button', { name: 'Lọc', exact: true });
  }

  get exportButton(): Locator {
    return this.page.getByRole('button', { name: 'Xuất báo cáo', exact: true });
  }

  /** Khối (section) có tiêu đề h2. */
  section(heading: string): Locator {
    return this.page.locator('section').filter({ has: this.page.getByRole('heading', { name: heading, exact: true }) });
  }

  /** Dòng dữ liệu của bảng trong khối có tiêu đề `heading`. */
  sectionRows(heading: string): Locator {
    return this.section(heading).locator('tbody tr');
  }
}
