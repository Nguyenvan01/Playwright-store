import { Page, expect } from '@playwright/test';
import type { ApiClient } from '@api/ApiClient';
import type { PageObjects } from '@pages/PageObjects';
import type { BlogMock, ContactMock, CouponMock, PromotionMock, ReviewMock } from '@data/admin-marketing.types';
import { AdminTable } from '@pages/admin/marketing/AdminTable';
import { PromotionsPage } from '@pages/admin/marketing/PromotionsPage';
import { CouponsPage } from '@pages/admin/marketing/CouponsPage';
import { ReviewsPage } from '@pages/admin/marketing/ReviewsPage';
import { BlogPage } from '@pages/admin/marketing/BlogPage';
import { ContactsPage } from '@pages/admin/marketing/ContactsPage';
import { BaseKeywords } from './BaseKeywords';

/** Ngày YYYY-MM-DD theo giờ Việt Nam (UTC+7), lệch `offset` ngày so với hôm nay. */
const vnDate = (offset = 0) => new Date(Date.now() + 7 * 3_600_000 + offset * 86_400_000).toISOString().slice(0, 10);

/** Quản trị marketing/nội dung: khuyến mãi, mã giảm giá, đánh giá, bài viết, liên hệ. */
export class AdminMarketingKeywords extends BaseKeywords {
  private readonly table: AdminTable;
  private readonly promotions: PromotionsPage;
  private readonly coupons: CouponsPage;
  private readonly reviews: ReviewsPage;
  private readonly blog: BlogPage;
  private readonly contacts: ContactsPage;
  /** URL các request GET danh sách đã đi qua API giả lập (để kiểm tra tham số lọc). */
  private readonly listQueries: URL[] = [];

  constructor(page: Page, po: PageObjects, api: ApiClient) {
    super(page, po, api);
    this.table = new AdminTable(page);
    this.promotions = new PromotionsPage(page);
    this.coupons = new CouponsPage(page);
    this.reviews = new ReviewsPage(page);
    this.blog = new BlogPage(page);
    this.contacts = new ContactsPage(page);
  }

  /** Giả lập API GET danh sách: lọc dữ liệu mẫu theo query string và ghi lại URL đã gọi. */
  private async fakeList<T>(urlGlob: string, json: (items: T[]) => unknown, items: T[], filter?: (item: T, q: URLSearchParams) => boolean) {
    await this.page.route(urlGlob, async (route) => {
      const req = route.request();
      if (req.method() !== 'GET') return route.fallback();
      const url = new URL(req.url());
      this.listQueries.push(url);
      const result = filter ? items.filter((i) => filter(i, url.searchParams)) : items;
      await route.fulfill({ status: 200, json: json(result) });
    });
  }

  // ---------------------------------------------------------------------------
  // Dùng chung cho các trang marketing
  // ---------------------------------------------------------------------------

  /** Kiểm tra bảng chính có đúng các cột theo thứ tự (đọc textContent, bỏ qua CSS viết hoa). */
  async verifyColumns(headers: string[]) {
    await this.step(`Kiểm tra cột: ${headers.join(' | ')}`, async () => {
      await expect(this.table.headerCells.first()).toBeVisible();
      expect(await this.table.headerTexts()).toEqual(headers);
    });
  }

  /** Kiểm tra các ô của dòng chứa text theo tên cột, vd: {"Trạng thái": "Hết hạn"}. */
  async verifyRowCells(rowText: string, cells: Record<string, string>) {
    await this.step(`Kiểm tra dòng "${rowText}": ${JSON.stringify(cells)}`, async () => {
      await expect(this.table.row(rowText)).toBeVisible();
      for (const [header, value] of Object.entries(cells)) {
        const cell = await this.table.cell(rowText, header);
        await (value === '' ? expect(cell).toHaveText('') : expect(cell).toContainText(value));
      }
    });
  }

  /** Kiểm tra ô ở cột `column` của dòng thứ `rowIndex` (0 = đầu) khớp biểu thức chính quy. */
  async verifyCellPattern(rowIndex: number, column: string, pattern: string) {
    await this.step(`Kiểm tra dòng #${rowIndex + 1}, cột "${column}" khớp /${pattern}/`, async () => {
      await expect(this.table.rows.nth(rowIndex)).toBeVisible();
      await expect(await this.table.cellAt(rowIndex, column)).toHaveText(new RegExp(pattern));
    });
  }

  /** Kiểm tra chữ hiển thị của option đang chọn trong select (theo label của ô). */
  async verifySelectedOption(label: string, text: string) {
    await this.step(`Kiểm tra "${label}" đang chọn "${text}"`, async () => {
      const select = this.po.adminUi.field(label);
      await expect.poll(() => select.evaluate((s: HTMLSelectElement) => s.selectedOptions[0]?.textContent?.trim())).toBe(text);
    });
  }

  /** Kiểm tra số dòng dữ liệu đang hiển thị trong bảng chính. */
  async verifyRowCount(count: number) {
    await this.step(`Kiểm tra bảng có ${count} dòng`, async () => {
      await expect(this.table.rows).toHaveCount(count);
    });
  }

  /** Kiểm tra bảng có ít nhất `min` dòng dữ liệu thật (không phải dòng trạng thái rỗng). */
  async verifyRowsAtLeast(min: number) {
    await this.step(`Kiểm tra bảng có ít nhất ${min} dòng`, async () => {
      await expect(this.table.rows.first()).toBeVisible();
      await expect(this.table.rows.locator('td[colspan]')).toHaveCount(0);
      expect(await this.table.rows.count()).toBeGreaterThanOrEqual(min);
    });
  }

  /** Kiểm tra dòng chứa text có đúng các nút hành động (theo title, đúng thứ tự). */
  async verifyRowActions(rowText: string, titles: string[]) {
    await this.step(`Kiểm tra nút trên dòng "${rowText}": ${titles.join(', ')}`, async () => {
      const buttons = this.table.titledButtons(rowText);
      await expect(buttons).toHaveCount(titles.length);
      expect(await buttons.evaluateAll((els) => els.map((e) => e.getAttribute('title')))).toEqual(titles);
    });
  }

  /** Kiểm tra các dòng hiển thị/không hiển thị sau khi tìm kiếm hoặc lọc. */
  async verifyVisibleRows(visible: string[], hidden: string[] = []) {
    await this.step(`Kiểm tra hiển thị [${visible.join(', ')}], ẩn [${hidden.join(', ')}]`, async () => {
      for (const text of visible) await expect(this.table.ui.row(text).first()).toBeVisible();
      for (const text of hidden) await expect(this.table.ui.row(text)).toHaveCount(0);
    });
  }

  /** Kiểm tra modal có tiêu đề `heading` đang mở và chứa các đoạn text. */
  async verifyModalText(heading: string, texts: string[]) {
    await this.step(`Kiểm tra modal "${heading}" chứa: ${texts.join(' | ')}`, async () => {
      const modal = this.table.modal(heading);
      await expect(modal).toBeVisible();
      for (const text of texts) await expect(modal).toContainText(text);
    });
  }

  /** Bấm nút theo tên bên trong modal có tiêu đề `heading`. */
  async clickModalButton(heading: string, name: string) {
    await this.step(`Modal "${heading}" -> bấm "${name}"`, async () => {
      await this.table.modalButton(heading, name).click();
    });
  }

  /** Kiểm tra request GET danh sách gần nhất (qua API giả lập) có các tham số; null = không gửi tham số đó. */
  async verifyListQuery(pathPart: string, params: Record<string, string | null>) {
    await this.step(`Kiểm tra GET ${pathPart} có ${JSON.stringify(params)}`, async () => {
      await expect
        .poll(() => {
          const last = [...this.listQueries].reverse().find((u) => u.pathname.includes(pathPart));
          if (!last) return 'chưa có request';
          return Object.fromEntries(Object.keys(params).map((key) => [key, last.searchParams.get(key)]));
        })
        .toEqual(params);
    });
  }

  // ---------------------------------------------------------------------------
  // Khuyến mãi
  // ---------------------------------------------------------------------------

  /** Giả lập danh sách + chi tiết khuyến mãi; startOffset/endOffset đổi thành ngày so với hôm nay. */
  async mockPromotionList(promotions: PromotionMock[]) {
    await this.step(`Mock danh sách ${promotions.length} khuyến mãi`, async () => {
      const list = promotions.map(({ startOffset, endOffset, ...p }) => ({
        ...p,
        name: p.title,
        start_date: startOffset === undefined ? (p.start_date ?? '') : vnDate(startOffset),
        end_date: endOffset === undefined ? (p.end_date ?? '') : vnDate(endOffset),
      }));
      await this.fakeList('**/api/admin/promotions', (items) => ({ success: true, promotions: items }), list);
      await this.page.route('**/api/admin/promotions/*', async (route) => {
        if (route.request().method() !== 'GET') return route.fallback();
        const id = Number(new URL(route.request().url()).pathname.split('/').pop());
        const found = list.find((p) => p.id === id);
        await route.fulfill(found ? { json: { success: true, promotion: found } } : { status: 404, json: { success: false } });
      });
    });
  }

  /** Mở trang Khuyến mãi và chờ danh sách tải xong. */
  async openPromotions() {
    await this.step('Mở trang Khuyến mãi', async () => {
      await this.page.goto(this.promotions.path);
      await expect(this.po.adminUi.pageTitle).toHaveText('Khuyến mãi');
      await expect(this.promotions.listHeading).toBeVisible();
      await expect(this.promotions.listReady).toBeVisible();
    });
  }

  /** Bấm "Thêm khuyến mãi" và chờ modal tạo mới. */
  async openCreatePromotion() {
    await this.step('Mở form "Thêm khuyến mãi"', async () => {
      await this.promotions.addButton.click();
      await expect(this.promotions.modal('Thêm khuyến mãi')).toBeVisible();
    });
  }

  // ---------------------------------------------------------------------------
  // Mã giảm giá
  // ---------------------------------------------------------------------------

  /** Giả lập API GET danh sách mã giảm giá. */
  async mockCouponList(coupons: CouponMock[]) {
    await this.step(`Mock danh sách ${coupons.length} mã giảm giá`, async () => {
      await this.fakeList('**/api/admin/coupons', (items) => ({ coupons: items }), coupons);
    });
  }

  /** Mở trang Mã giảm giá và chờ danh sách tải xong. */
  async openCoupons() {
    await this.step('Mở trang Mã giảm giá', async () => {
      await this.page.goto(this.coupons.path);
      await expect(this.po.adminUi.pageTitle).toHaveText('Mã giảm giá');
      await expect(this.coupons.listReady).toBeVisible();
    });
  }

  /** Bấm "Thêm mã" và chờ modal "Thêm mã giảm giá". */
  async openCreateCoupon() {
    await this.step('Mở form "Thêm mã giảm giá"', async () => {
      await this.coupons.addButton.click();
      await expect(this.coupons.modal('Thêm mã giảm giá')).toBeVisible();
    });
  }

  /** Bấm nút sửa (icon không tên) trên dòng mã giảm giá. */
  async clickCouponEdit(code: string) {
    await this.step(`Sửa mã giảm giá "${code}"`, async () => {
      await this.coupons.editButton(code).click();
      await expect(this.coupons.modal('Sửa mã giảm giá')).toBeVisible();
    });
  }

  /** Bấm nút xóa (icon không tên) trên dòng mã giảm giá. */
  async clickCouponDelete(code: string) {
    await this.step(`Xóa mã giảm giá "${code}"`, async () => {
      await this.coupons.deleteButton(code).click();
      await expect(this.coupons.modal('Xác nhận xóa')).toBeVisible();
    });
  }

  /** Bấm nút bật/tắt ở cột "Công khai" hoặc "Trạng thái" của mã giảm giá. */
  async toggleCoupon(code: string, column: string) {
    await this.step(`Bật/tắt "${column}" của mã "${code}"`, async () => {
      await (await this.coupons.toggleButton(code, column)).click();
    });
  }

  /** Kiểm tra nút bật/tắt ở cột của mã giảm giá đang bật (xanh) hay tắt (xám). */
  async verifyCouponToggle(code: string, column: string, on: boolean) {
    await this.step(`Kiểm tra "${column}" của mã "${code}" đang ${on ? 'bật' : 'tắt'}`, async () => {
      const button = await this.coupons.toggleButton(code, column);
      await expect(button).toHaveClass(on ? /text-green-500/ : /text-gray-300/);
    });
  }

  // ---------------------------------------------------------------------------
  // Đánh giá
  // ---------------------------------------------------------------------------

  /** Giả lập API GET đánh giá: lọc theo tham số status/rating như server. */
  async mockReviewList(reviews: ReviewMock[]) {
    await this.step(`Mock danh sách ${reviews.length} đánh giá`, async () => {
      await this.fakeList(
        '**/api/admin/reviews*',
        (items) => ({ success: true, reviews: items, total: items.length, totalPages: 1, page: 1 }),
        reviews,
        (r, q) => (!q.get('status') || r.status === q.get('status')) && (!q.get('rating') || r.rating === Number(q.get('rating'))),
      );
    });
  }

  /** Mở trang Đánh giá và chờ danh sách tải xong. */
  async openReviews() {
    await this.step('Mở trang Đánh giá', async () => {
      await this.page.goto(this.reviews.path);
      await expect(this.po.adminUi.pageTitle).toHaveText('Đánh giá');
      await expect(this.reviews.pageHeading).toHaveText('Đánh giá');
      await expect(this.reviews.listReady).toBeVisible();
    });
  }

  /** Chọn bộ lọc trạng thái đánh giá (all, pending, approved, hidden). */
  async filterReviewStatus(value: string) {
    await this.step(`Lọc đánh giá theo trạng thái "${value}"`, async () => {
      await this.reviews.statusSelect.selectOption(value);
      await expect(this.reviews.listReady).toBeVisible();
    });
  }

  /** Chọn bộ lọc số sao (all, 5, 4, 3, 2, 1). */
  async filterReviewRating(value: string) {
    await this.step(`Lọc đánh giá theo số sao "${value}"`, async () => {
      await this.reviews.ratingSelect.selectOption(value);
      await expect(this.reviews.listReady).toBeVisible();
    });
  }

  // ---------------------------------------------------------------------------
  // Bài viết
  // ---------------------------------------------------------------------------

  /** Giả lập API GET danh sách bài viết. */
  async mockBlogList(posts: BlogMock[]) {
    await this.step(`Mock danh sách ${posts.length} bài viết`, async () => {
      await this.fakeList('**/api/admin/blogs', (items) => ({ success: true, blogs: items, posts: items }), posts);
    });
  }

  /** Mở trang Bài viết và chờ danh sách tải xong. */
  async openBlog() {
    await this.step('Mở trang Bài viết', async () => {
      await this.page.goto(this.blog.path);
      await expect(this.po.adminUi.pageTitle).toHaveText('Bài viết');
      await expect(this.blog.pageHeading).toHaveText('Bài viết');
      await expect(this.blog.listReady).toBeVisible();
    });
  }

  /** Bấm "Thêm bài viết" và chờ modal tạo mới. */
  async openCreateBlog() {
    await this.step('Mở form "Thêm bài viết"', async () => {
      await this.blog.addButton.click();
      await expect(this.blog.modal('Thêm bài viết')).toBeVisible();
    });
  }

  /** Nhập URL ảnh bài viết và kiểm tra ảnh xem trước hoặc thông báo lỗi ảnh. */
  async setBlogImage(url: string, error = '') {
    await this.step(`Nhập URL ảnh "${url}"`, async () => {
      await this.blog.imageUrlInput.fill(url);
      if (error) await expect(this.page.getByText(error, { exact: true })).toBeVisible();
      else await expect(this.blog.imagePreview).toBeVisible();
    });
  }

  // ---------------------------------------------------------------------------
  // Liên hệ
  // ---------------------------------------------------------------------------

  /** Giả lập API GET liên hệ: lọc theo tham số status như server. */
  async mockContactList(contacts: ContactMock[]) {
    await this.step(`Mock danh sách ${contacts.length} liên hệ`, async () => {
      await this.fakeList(
        '**/api/admin/contacts*',
        (items) => ({ success: true, contacts: items }),
        contacts,
        (c, q) => !q.get('status') || c.status === q.get('status'),
      );
    });
  }

  /** Mở trang Liên hệ và chờ danh sách tải xong. */
  async openContacts() {
    await this.step('Mở trang Liên hệ', async () => {
      await this.page.goto(this.contacts.path);
      await expect(this.po.adminUi.pageTitle).toHaveText('Liên hệ');
      await expect(this.contacts.pageHeading).toHaveText('Liên hệ');
      await expect(this.contacts.listReady).toBeVisible();
    });
  }

  /** Chọn bộ lọc trạng thái liên hệ (all, pending, processed). */
  async filterContactStatus(value: string) {
    await this.step(`Lọc liên hệ theo trạng thái "${value}"`, async () => {
      await this.contacts.statusSelect.selectOption(value);
      await expect(this.contacts.listReady).toBeVisible();
    });
  }
}
