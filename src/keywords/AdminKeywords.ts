import { expect } from '@playwright/test';
import { env } from '@config/env';
import { ROUTES } from '@data/routes';
import { detectReload } from '@utils/storage';
import { BaseKeywords } from './BaseKeywords';

export class AdminKeywords extends BaseKeywords {
  /** Mở trang đăng nhập quản trị. */
  async openAdminLogin() {
    await this.step('Mở trang đăng nhập admin', async () => {
      await this.po.adminLogin.goto();
      await expect(this.po.adminLogin.heading).toBeVisible();
    });
  }

  /** Nhập email + mật khẩu admin và bấm Đăng nhập. */
  async loginAdmin(email: string, password: string) {
    await this.step(`Đăng nhập admin "${email}"`, async () => {
      await this.po.adminLogin.login(email, password);
    });
  }

  /** Đăng nhập bằng tài khoản admin test trong .env và chờ vào Dashboard. */
  async loginAsAdmin() {
    await this.step('Đăng nhập tài khoản admin test', async () => {
      expect(env.admin.email, 'Chưa cấu hình E2E_ADMIN_EMAIL').toBeTruthy();
      await this.po.adminLogin.goto();
      await this.po.adminLogin.login(env.admin.email, env.admin.password);
      await expect(this.page).toHaveURL(ROUTES.admin.dashboard);
    });
  }

  /** Đăng nhập admin sai và kiểm tra thông báo lỗi vẫn hiển thị (không reload). */
  async loginAdminExpectingError(email: string, password: string, message: string) {
    await this.step(`Đăng nhập admin "${email}" và chờ lỗi "${message}"`, async () => {
      const reloaded = detectReload(this.page);
      await this.po.adminLogin.login(email, password);
      expect(await reloaded, 'Trang bị reload sau khi đăng nhập sai').toBe(false);
      await expect(this.po.adminLogin.errorMessage).toHaveText(message);
      await expect(this.page).toHaveURL(ROUTES.admin.login);
    });
  }

  /** Kiểm tra đang ở trang đăng nhập admin (bị chặn khi chưa đăng nhập). */
  async verifyOnAdminLogin() {
    await this.step('Kiểm tra bị chuyển về /admin/login', async () => {
      await expect(this.page).toHaveURL(ROUTES.admin.login);
      await expect(this.po.adminLogin.heading).toBeVisible();
    });
  }

  /** Bấm "Quay về cửa hàng" trên trang đăng nhập admin. */
  async backToStore() {
    await this.step('Bấm "Quay về cửa hàng"', async () => {
      await this.po.adminLogin.backToStoreLink.click();
    });
  }

  /** Mở trang quản trị /admin (cần đã đăng nhập) và chờ sidebar. */
  async openDashboard() {
    await this.step('Mở trang quản trị', async () => {
      await this.po.adminLayout.goto();
      await expect(this.po.adminLayout.sidebar).toBeVisible();
    });
  }

  /** Bấm 1 mục trên sidebar quản trị, vd: "Sản phẩm". */
  async navigateMenu(label: string) {
    await this.step(`Sidebar -> "${label}"`, async () => {
      await this.po.adminLayout.navigateTo(label);
    });
  }

  /** Mở 1 trang quản trị theo đường dẫn và kiểm tra tiêu đề trên header. */
  async openAdminPage(path: string, title: string) {
    await this.step(`Mở trang quản trị ${path} "${title}"`, async () => {
      await this.page.goto(path);
      await expect(this.po.adminUi.pageTitle).toHaveText(title);
    });
  }

  /** Kiểm tra tiêu đề trang trên header admin. */
  async verifyHeaderTitle(title: string) {
    await this.step(`Kiểm tra tiêu đề "${title}"`, async () => {
      await expect(this.po.adminUi.pageTitle).toHaveText(title);
    });
  }

  /** Kiểm tra bảng có đủ các cột (theo thứ tự). */
  async verifyTableHeaders(headers: string[]) {
    await this.step(`Kiểm tra cột bảng: ${headers.join(' | ')}`, async () => {
      // textContent: lấy chữ gốc, không bị CSS `uppercase` biến đổi như innerText
      const texts = (await this.po.adminUi.tableHeaders.allTextContents()).map((t) => t.replace(/\s+/g, ' ').trim()).filter(Boolean);
      expect(texts).toEqual(expect.arrayContaining(headers));
      const idx = headers.map((h) => texts.indexOf(h));
      expect(idx, 'Thứ tự cột không đúng').toEqual([...idx].sort((a, b) => a - b));
    });
  }

  /** Gõ vào ô tìm kiếm có placeholder cho trước. */
  async searchList(placeholder: string, text: string) {
    await this.step(`Tìm "${text}"`, async () => {
      await this.page.getByPlaceholder(placeholder, { exact: true }).fill(text);
    });
  }

  /** Bấm 1 nút theo tên hiển thị (ưu tiên nút trong modal đang mở). */
  async clickButton(name: string) {
    await this.step(`Bấm "${name}"`, async () => {
      await this.po.adminUi.button(name).click();
    });
  }

  /** Bấm nút hành động (title) trên dòng chứa text, vd: ("Áo thun", "Sửa"). */
  async clickRowAction(rowText: string, title: string) {
    await this.step(`Dòng "${rowText}" -> "${title}"`, async () => {
      await this.po.adminUi.rowAction(rowText, title).click();
    });
  }

  /** Kiểm tra có/không có dòng chứa text trong bảng. */
  async verifyRow(text: string, visible = true) {
    await this.step(`Kiểm tra ${visible ? 'có' : 'không có'} dòng "${text}"`, async () => {
      const row = this.po.adminUi.row(text);
      await (visible ? expect(row.first()).toBeVisible() : expect(row).toHaveCount(0));
    });
  }

  /** Điền form theo label: chuỗi -> input/textarea/select (value hoặc label option), boolean -> checkbox. */
  async fillForm(fields: Record<string, string | number | boolean>) {
    await this.step(`Điền form: ${Object.keys(fields).join(', ')}`, async () => {
      for (const [label, value] of Object.entries(fields)) {
        if (typeof value === 'boolean') {
          await this.po.adminUi.checkbox(label).setChecked(value);
          continue;
        }
        const el = this.po.adminUi.field(label);
        const tag = await el.evaluate((n) => n.tagName.toLowerCase());
        if (tag === 'select') {
          const v = String(value);
          const byValue = await el.locator(`option[value="${v.replace(/"/g, '\\"')}"]`).count();
          await el.selectOption(byValue ? { value: v } : { label: v });
        } else {
          await el.fill(String(value));
        }
      }
    });
  }

  /** Kiểm tra giá trị hiện tại của 1 ô trong form (theo label). */
  async verifyFieldValue(label: string, value: string) {
    await this.step(`Kiểm tra ô "${label}" = "${value}"`, async () => {
      await expect(this.po.adminUi.field(label)).toHaveValue(value);
    });
  }

  /** Kiểm tra modal/khối có tiêu đề đang hiển thị. */
  async verifyModalOpen(heading: string) {
    await this.step(`Kiểm tra mở "${heading}"`, async () => {
      await expect(this.po.adminUi.heading(heading)).toBeVisible();
    });
  }

  /** Kiểm tra modal/khối có tiêu đề đã đóng. */
  async verifyModalClosed(heading: string) {
    await this.step(`Kiểm tra đã đóng "${heading}"`, async () => {
      await expect(this.page.getByRole('heading', { name: heading, exact: true })).toHaveCount(0);
    });
  }

  /** Kiểm tra đang ở 1 trang quản trị (URL + tiêu đề trang). */
  async verifyAdminPage(path: string) {
    await this.step(`Kiểm tra trang quản trị ${path}`, async () => {
      await expect(this.page).toHaveURL(path);
      await expect(this.po.adminLayout.sidebar).toBeVisible();
      await expect(this.po.adminLayout.pageTitle).toBeVisible();
    });
  }
}
