import { Page, expect } from '@playwright/test';
import type { ApiClient } from '@api/ApiClient';
import type { PageObjects } from '@pages/PageObjects';
import { detectReload } from '@utils/storage';
import { BaseKeywords } from './BaseKeywords';

export interface CapturedRequest {
  method: string;
  path: string;
  body: unknown;
}

export class CommonKeywords extends BaseKeywords {
  private readonly pageErrors: string[] = [];
  /** Các request đã bị mockWrite bắt lại (theo thứ tự). */
  readonly captured: CapturedRequest[] = [];

  constructor(page: Page, po: PageObjects, api: ApiClient) {
    super(page, po, api);
    page.on('pageerror', (err) => this.pageErrors.push(err.message));
  }

  /** Mở 1 đường dẫn bất kỳ, vd: "/about". */
  async goto(path: string) {
    await this.step(`Mở trang ${path}`, async () => {
      await this.page.goto(path);
    });
  }

  /** Tải lại trang hiện tại. */
  async reload() {
    await this.step('Tải lại trang', async () => {
      await this.page.reload();
    });
  }

  /** Kiểm tra URL hiện tại đúng đường dẫn, vd: "/profile". */
  async verifyUrl(path: string) {
    await this.step(`Kiểm tra URL là ${path}`, async () => {
      await expect(this.page).toHaveURL(path);
    });
  }

  /** Kiểm tra URL khớp biểu thức chính quy, vd: "/product/.+". */
  async verifyUrlMatches(pattern: string) {
    await this.step(`Kiểm tra URL khớp /${pattern}/`, async () => {
      await expect(this.page).toHaveURL(new RegExp(pattern));
    });
  }

  /** Kiểm tra có toast chứa nội dung. */
  async verifyToast(text: string) {
    await this.step(`Kiểm tra toast "${text}"`, async () => {
      await expect(this.po.home.toast(text)).toBeVisible();
    });
  }

  /** Kiểm tra 1 đoạn chữ đang hiển thị trên trang. */
  async verifyTextVisible(text: string) {
    await this.step(`Kiểm tra hiển thị "${text}"`, async () => {
      await expect(this.page.getByText(text).first()).toBeVisible();
    });
  }

  /** Kiểm tra trang có header và footer (trang khách hàng tải thành công). */
  async verifyLayoutLoaded() {
    await this.step('Kiểm tra header và footer hiển thị', async () => {
      await expect(this.po.header.root).toBeVisible();
      await expect(this.page.locator('footer')).toBeVisible();
    });
  }

  /** Kiểm tra không phát sinh lỗi JavaScript nào kể từ đầu test. */
  async verifyNoPageErrors() {
    await this.step('Kiểm tra không có lỗi JavaScript', async () => {
      expect(this.pageErrors, this.pageErrors.join('\n')).toHaveLength(0);
    });
  }

  /** Kiểm tra trang không bị tràn ngang (responsive). */
  async verifyNoHorizontalOverflow() {
    await this.step('Kiểm tra không tràn ngang', async () => {
      const overflow = await this.page.evaluate(
        () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
      );
      expect(overflow, `Trang rộng hơn màn hình ${overflow}px`).toBeLessThanOrEqual(1);
    });
  }

  /** Giả lập 1 API theo mẫu URL (glob của Playwright), trả về status + json. */
  async mockApi(urlPattern: string, response: { status?: number; json: unknown }) {
    await this.step(`Mock API ${urlPattern} -> ${response.status ?? 200}`, async () => {
      await this.page.route(urlPattern, (route) =>
        route.fulfill({ status: response.status ?? 200, json: response.json }),
      );
    });
  }

  /** Giả lập API ghi (POST/PUT/DELETE) theo mẫu URL, trả về json; lưu lại request để kiểm tra. */
  async mockWrite(method: string, urlPattern: string, json: unknown = { success: true }, status = 200) {
    await this.step(`Mock ${method} ${urlPattern} -> ${status}`, async () => {
      await this.page.route(urlPattern, async (route) => {
        const req = route.request();
        if (req.method() !== method.toUpperCase()) return route.fallback();
        let body: unknown = null;
        try {
          body = req.postDataJSON();
        } catch {
          body = req.postData();
        }
        this.captured.push({ method: req.method(), path: new URL(req.url()).pathname, body });
        await route.fulfill({ status, json });
      });
    });
  }

  /** Kiểm tra đã gửi request (method + đường dẫn chứa pathPart), body chứa các trường mong đợi. */
  async verifyRequest(method: string, pathPart: string, expectedBody?: Record<string, unknown>) {
    await this.step(`Kiểm tra đã gửi ${method} ${pathPart}`, async () => {
      await expect
        .poll(() => this.captured.some((r) => r.method === method.toUpperCase() && r.path.includes(pathPart)), {
          message: `Không thấy request ${method} ${pathPart}. Đã bắt: ${JSON.stringify(this.captured.map((r) => `${r.method} ${r.path}`))}`,
        })
        .toBe(true);
      if (expectedBody) {
        const req = [...this.captured].reverse().find((r) => r.method === method.toUpperCase() && r.path.includes(pathPart));
        expect(req?.body).toMatchObject(expectedBody);
      }
    });
  }

  /** Giả lập API GET (dữ liệu mẫu cho trang cần data, vd: danh sách đơn hàng). Chỉ chặn method GET. */
  async mockGet(urlPattern: string, json: unknown, status = 200) {
    await this.step(`Mock GET ${urlPattern} -> ${status}`, async () => {
      await this.page.route(urlPattern, (route) =>
        route.request().method() === 'GET' ? route.fulfill({ status, json }) : route.fallback(),
      );
    });
  }

  /** Tự động bấm OK (true) hoặc Hủy (false) cho hộp thoại window.confirm/alert tiếp theo. */
  async acceptNextDialog(accept = true) {
    await this.step(`${accept ? 'Đồng ý' : 'Hủy'} hộp thoại xác nhận tiếp theo`, async () => {
      this.page.once('dialog', (d) => (accept ? d.accept() : d.dismiss()));
    });
  }

  /** Kiểm tra KHÔNG có request ghi nào (method + đường dẫn) được gửi. */
  async verifyNoRequest(method: string, pathPart: string) {
    await this.step(`Kiểm tra KHÔNG gửi ${method} ${pathPart}`, async () => {
      expect(this.captured.filter((r) => r.method === method.toUpperCase() && r.path.includes(pathPart))).toHaveLength(0);
    });
  }

  /** Bắt đầu theo dõi reload; gọi verifyNoReload sau thao tác để kiểm tra. */
  watchReload(timeout = 3_000): Promise<boolean> {
    return detectReload(this.page, timeout);
  }
}
