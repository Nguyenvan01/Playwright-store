import { Locator, Page } from '@playwright/test';

/** Trang Tổng quan (/admin): thẻ thống kê, biểu đồ, đơn gần đây, sản phẩm bán chạy, thẻ thao tác nhanh. */
export class DashboardPage {
  readonly path = '/admin';
  /** Lưới 4 thẻ thống kê đầu trang. */
  readonly statsGrid: Locator;

  constructor(readonly page: Page) {
    this.statsGrid = page.locator('main div.grid').first();
  }

  statCard(label: string): Locator {
    return this.statsGrid.locator('> div').filter({ has: this.page.getByText(label, { exact: true }) });
  }

  statValue(label: string): Locator {
    return this.statCard(label).locator('p.text-2xl');
  }

  /** Huy hiệu % tăng/giảm trên thẻ thống kê. */
  statChange(label: string): Locator {
    return this.statCard(label).locator('div.rounded-full');
  }

  statSub(label: string): Locator {
    return this.statCard(label).locator('p.text-xs');
  }

  /** Khối nội dung có tiêu đề h3. */
  section(title: string): Locator {
    return this.page
      .locator('main div.rounded-xl')
      .filter({ has: this.page.getByRole('heading', { name: title, exact: true }) })
      .first();
  }

  sectionHeading(title: string): Locator {
    return this.page.getByRole('heading', { name: title, exact: true });
  }

  /** Giá trị của 1 trạng thái trong khối "Đơn hàng theo trạng thái". */
  statusValue(label: string): Locator {
    return this.section('Đơn hàng theo trạng thái')
      .locator('div.flex.justify-between')
      .filter({ has: this.page.getByText(label, { exact: true }) })
      .locator('span')
      .last();
  }

  /** Các dòng trong khối danh sách (đơn gần đây / sản phẩm bán chạy). */
  sectionRows(title: string): Locator {
    return this.section(title).locator('div.divide-y > div');
  }

  sectionLink(title: string, label: string): Locator {
    return this.section(title).getByRole('link', { name: label, exact: true });
  }

  /** Thẻ thao tác nhanh cuối trang, vd: "Đơn hàng chờ xử lý". */
  quickCard(title: string): Locator {
    return this.page.locator('main div.group.rounded-xl').filter({ has: this.page.getByText(title, { exact: true }) });
  }

  quickCardValue(title: string): Locator {
    return this.quickCard(title).locator('p.text-2xl');
  }

  quickLink(label: string): Locator {
    return this.page.locator('main div.group.rounded-xl').getByRole('link', { name: label, exact: true });
  }

  get rangeSelect(): Locator {
    return this.section('Doanh thu & Đơn hàng').locator('select');
  }

  get chartTicks(): Locator {
    return this.section('Doanh thu & Đơn hàng').locator('.recharts-xAxis-tick-labels .recharts-cartesian-axis-tick-value');
  }

  get chartLines(): Locator {
    return this.section('Doanh thu & Đơn hàng').locator('g.recharts-line');
  }

  get chartAreas(): Locator {
    return this.section('Doanh thu & Đơn hàng').locator('g.recharts-area');
  }

  get chartLineDots(): Locator {
    return this.section('Doanh thu & Đơn hàng').locator('circle.recharts-line-dot');
  }
}
