import { Locator, Page, Route } from '@playwright/test';

/**
 * Tiện ích dùng chung cho các trang quản trị (nhóm sales + catalog):
 *  - ghi lại request GET /api/admin/* để kiểm tra tham số lọc/phân trang,
 *  - trả JSON cho route GET (mock dữ liệu đọc, KHÔNG đụng tới request ghi),
 *  - locator modal / phân trang (app không dùng role=dialog).
 */
export class AdminRequestLog {
  readonly urls: string[] = [];

  constructor(page: Page) {
    page.on('request', (r) => {
      if (r.method() === 'GET' && r.url().includes('/api/admin/')) this.urls.push(r.url());
    });
  }

  /** Có request GET tới đường dẫn kết thúc bằng `path` và chứa đủ các tham số query. */
  has(path: string, params: Record<string, string | number> = {}): boolean {
    return this.urls.some((u) => {
      const url = new URL(u);
      return (
        url.pathname.endsWith(path) &&
        Object.entries(params).every(([k, v]) => url.searchParams.get(k) === String(v))
      );
    });
  }

  /** Số request GET tới đường dẫn kết thúc bằng `path`. */
  count(path: string): number {
    return this.urls.filter((u) => new URL(u).pathname.endsWith(path)).length;
  }

  describe(): string {
    return JSON.stringify(this.urls.map((u) => new URL(u).pathname + new URL(u).search));
  }
}

/** Trả JSON cho request GET; request khác (POST/PUT/DELETE) chuyển tiếp cho mockWrite / writeGuard. */
export async function fulfillGet(route: Route, json: () => unknown, status = 200) {
  if (route.request().method() !== 'GET') return route.fallback();
  return route.fulfill({ status, json: json() });
}

/** Tham số query của request đang bị chặn. */
export function queryOf(route: Route): URLSearchParams {
  return new URL(route.request().url()).searchParams;
}

/** So khớp không phân biệt hoa thường. */
export function includesCI(value: unknown, needle: string): boolean {
  return String(value ?? '').toLowerCase().includes(needle.toLowerCase());
}

/** Modal của app: lớp phủ `div.fixed.inset-0` chứa tiêu đề h3 (không có role=dialog). */
export function modalByHeading(page: Page, heading: string | RegExp): Locator {
  return page
    .locator('div.fixed.inset-0')
    .filter({ has: page.getByRole('heading', { name: heading, exact: typeof heading === 'string' }) })
    .last();
}

/** Thanh phân trang cuối bảng (có dòng "Trang ..."). */
export function paginationBar(page: Page): Locator {
  return page.locator('div.border-t').filter({ has: page.getByText(/^Trang \d+/) }).last();
}
