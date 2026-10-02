import fs from 'node:fs/promises';
import { Page, expect } from '@playwright/test';
import type { ApiClient } from '@api/ApiClient';
import type { PageObjects } from '@pages/PageObjects';
import type { ImportItemInput, ImportMockData, ReportOverviewMock, WarehouseMock } from '@data/admin-ops.types';
import { AdminTable } from '@pages/admin/marketing/AdminTable';
import { WarehousePage } from '@pages/admin/ops/WarehousePage';
import { ImportPage } from '@pages/admin/ops/ImportPage';
import { ReportsPage } from '@pages/admin/ops/ReportsPage';
import { SettingsPage } from '@pages/admin/ops/SettingsPage';
import { BaseKeywords } from './BaseKeywords';

/** Ngày YYYY-MM-DD theo giờ Việt Nam (UTC+7). */
const vnToday = () => new Date(Date.now() + 7 * 3_600_000).toISOString().slice(0, 10);

/** Quản trị vận hành: kho hàng, nhập hàng, báo cáo, cài đặt. */
export class AdminOpsKeywords extends BaseKeywords {
  private readonly table: AdminTable;
  private readonly warehouse: WarehousePage;
  private readonly imports: ImportPage;
  private readonly reports: ReportsPage;
  private readonly settings: SettingsPage;
  /** URL các request GET đã đi qua API giả lập (để kiểm tra tham số lọc). */
  private readonly listQueries: URL[] = [];

  constructor(page: Page, po: PageObjects, api: ApiClient) {
    super(page, po, api);
    this.table = new AdminTable(page);
    this.warehouse = new WarehousePage(page);
    this.imports = new ImportPage(page);
    this.reports = new ReportsPage(page);
    this.settings = new SettingsPage(page);
  }

  /** Giả lập API GET: trả json theo query string và ghi lại URL đã gọi. */
  private async fakeGet(urlGlob: string, json: (q: URLSearchParams, url: URL) => unknown) {
    await this.page.route(urlGlob, async (route) => {
      const req = route.request();
      if (req.method() !== 'GET') return route.fallback();
      const url = new URL(req.url());
      this.listQueries.push(url);
      const body = json(url.searchParams, url);
      await route.fulfill(body === undefined ? { status: 404, json: { success: false } } : { status: 200, json: body });
    });
  }

  // ---------------------------------------------------------------------------
  // Dùng chung cho các trang vận hành
  // ---------------------------------------------------------------------------

  /** Kiểm tra bảng chính có đúng các cột theo thứ tự (đọc textContent, bỏ qua CSS viết hoa). */
  async verifyColumns(headers: string[]) {
    await this.step(`Kiểm tra cột: ${headers.join(' | ')}`, async () => {
      await expect(this.table.headerCells.first()).toBeVisible();
      expect(await this.table.headerTexts()).toEqual(headers);
    });
  }

  /** Kiểm tra các ô của dòng chứa text theo tên cột, vd: {"Tồn kho": "3"}. */
  async verifyRowCells(rowText: string, cells: Record<string, string>) {
    await this.step(`Kiểm tra dòng "${rowText}": ${JSON.stringify(cells)}`, async () => {
      await expect(this.table.row(rowText)).toBeVisible();
      for (const [header, value] of Object.entries(cells)) {
        const cell = await this.table.cell(rowText, header);
        await (value === '' ? expect(cell).toHaveText('') : expect(cell).toContainText(value));
      }
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

  /** Kiểm tra các thẻ thống kê (nhãn -> giá trị), vd: {"Tổng đơn": "3"}. */
  async verifyStatCards(cards: Record<string, string>) {
    await this.step(`Kiểm tra thẻ thống kê ${JSON.stringify(cards)}`, async () => {
      for (const [label, value] of Object.entries(cards)) {
        await expect(this.table.statValue(label)).toHaveText(value);
      }
    });
  }

  /** Kiểm tra request GET gần nhất (qua API giả lập) có các tham số; null = không gửi tham số đó. */
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
  // Kho hàng
  // ---------------------------------------------------------------------------

  /** Giả lập API kho hàng: lọc sản phẩm theo tham số filter (all, low, out) như server. */
  async mockWarehouse(data: WarehouseMock) {
    await this.step(`Mock kho hàng ${data.products.length} sản phẩm`, async () => {
      await this.fakeGet('**/api/admin/warehouse*', (q) => {
        const filter = q.get('filter');
        const products = data.products.filter((p) =>
          filter === 'low' ? p.stock > 0 && p.stock <= 5 : filter === 'out' ? p.stock === 0 : true,
        );
        return { stats: data.stats, products };
      });
    });
  }

  /** Mở trang Kho hàng và chờ bảng tải xong. */
  async openWarehouse() {
    await this.step('Mở trang Kho hàng', async () => {
      await this.page.goto(this.warehouse.path);
      await expect(this.po.adminUi.pageTitle).toHaveText('Kho hàng');
      await expect(this.warehouse.listReady).toBeVisible();
    });
  }

  /** Bấm tab lọc kho ("Tất cả", "Sắp hết", "Hết hàng") và chờ bảng tải lại. */
  async selectWarehouseTab(label: string) {
    await this.step(`Chọn tab kho "${label}"`, async () => {
      await this.warehouse.tab(label).click();
      await expect(this.warehouse.tab(label)).toHaveClass(/bg-red-600/);
      await expect(this.warehouse.listReady).toBeVisible();
    });
  }

  /** Kiểm tra số đếm trên tab kho; null = không hiển thị số. */
  async verifyWarehouseTabBadge(label: string, count: number | null) {
    await this.step(`Kiểm tra tab "${label}" có số ${count ?? '(không có)'}`, async () => {
      await (count === null
        ? expect(this.warehouse.tabBadge(label)).toHaveCount(0)
        : expect(this.warehouse.tabBadge(label)).toHaveText(String(count)));
    });
  }

  /** Kiểm tra thẻ "Tổng sản phẩm" bằng số dòng của tab "Tất cả" (dữ liệu thật). */
  async verifyWarehouseStatsMatchList() {
    await this.step('Kiểm tra "Tổng sản phẩm" khớp số dòng trong bảng', async () => {
      await expect(this.table.rows.first()).toBeVisible();
      const rows = await this.table.rows.count();
      await expect(this.table.statValue('Tổng sản phẩm')).toHaveText(String(rows));
    });
  }

  // ---------------------------------------------------------------------------
  // Nhập hàng
  // ---------------------------------------------------------------------------

  /** Giả lập toàn bộ API GET của trang Nhập hàng (đơn nhập lọc theo status/supplier_id/search, NCC, kho, sản phẩm, chi tiết). */
  async mockImportData(data: ImportMockData) {
    await this.step(`Mock trang Nhập hàng (${data.imports.length} đơn)`, async () => {
      await this.fakeGet('**/api/admin/imports*', (q) => {
        const search = (q.get('search') || '').toLowerCase();
        const list = data.imports.filter(
          (i) =>
            (!q.get('status') || i.status === q.get('status')) &&
            (!q.get('supplier_id') || String(i.supplier_id) === q.get('supplier_id')) &&
            (!search || i.code.toLowerCase().includes(search) || i.supplier_name.toLowerCase().includes(search)),
        );
        return { success: true, imports: list, orders: list };
      });
      await this.fakeGet('**/api/admin/imports/*', (_q, url) => {
        const found = data.imports.find((i) => String(i.id) === url.pathname.split('/').pop());
        return found ? { success: true, import: found, order: found } : undefined;
      });
      await this.fakeGet('**/api/admin/suppliers', () => ({ success: true, suppliers: data.suppliers }));
      await this.fakeGet('**/api/admin/warehouses', () => ({ success: true, warehouses: data.warehouses }));
      await this.fakeGet('**/api/admin/products/options', () => ({ success: true, products: data.products }));
    });
  }

  /** Mở trang Nhập hàng và chờ bảng tải xong. */
  async openImport() {
    await this.step('Mở trang Nhập hàng', async () => {
      await this.page.goto(this.imports.path);
      await expect(this.po.adminUi.pageTitle).toHaveText('Nhập hàng');
      await expect(this.imports.pageHeading).toHaveText('Nhập hàng');
      await expect(this.imports.listReady).toBeVisible();
    });
  }

  /** Lọc đơn nhập theo trạng thái (draft, processing, partial_received, received, cancelled; rỗng = tất cả). */
  async filterImportStatus(value: string) {
    await this.step(`Lọc đơn nhập theo trạng thái "${value}"`, async () => {
      await this.imports.statusFilter.selectOption(value);
    });
  }

  /** Lọc đơn nhập theo tên nhà cung cấp (rỗng = tất cả). */
  async filterImportSupplier(name: string) {
    await this.step(`Lọc đơn nhập theo NCC "${name}"`, async () => {
      await this.imports.supplierFilter.selectOption(name ? { label: name } : { value: '' });
    });
  }

  /** Bấm "Tạo đơn nhập hàng" và chờ modal tạo đơn. */
  async openCreateImport() {
    await this.step('Mở form "Tạo đơn nhập hàng"', async () => {
      await this.imports.createButton.click();
      await expect(this.imports.createModal).toBeVisible();
      await expect(this.imports.itemProduct(0).locator('option')).not.toHaveCount(1);
    });
  }

  /** Bấm "Thêm sản phẩm" để thêm 1 dòng sản phẩm nhập. */
  async addImportItemRow() {
    await this.step('Thêm dòng sản phẩm nhập', async () => {
      const before = await this.imports.createModal.locator('table tbody tr').count();
      await this.imports.createModal.getByRole('button', { name: 'Thêm sản phẩm', exact: true }).click();
      await expect(this.imports.createModal.locator('table tbody tr')).toHaveCount(before + 1);
    });
  }

  /** Điền dòng sản phẩm nhập thứ `index` (0 = dòng đầu): sản phẩm, biến thể, số lượng, đơn giá, ghi chú. */
  async fillImportItem(index: number, item: ImportItemInput) {
    await this.step(`Điền dòng sản phẩm nhập #${index + 1}: ${JSON.stringify(item)}`, async () => {
      if (item.product !== undefined) await this.imports.itemProduct(index).selectOption({ label: item.product });
      if (item.variant !== undefined) await this.imports.itemVariant(index).selectOption({ label: item.variant });
      if (item.quantity !== undefined) await this.imports.itemInput(index, 1).fill(String(item.quantity));
      if (item.unitCost !== undefined) await this.imports.itemInput(index, 2).fill(String(item.unitCost));
      if (item.note !== undefined) await this.imports.itemInput(index, 3).fill(item.note);
    });
  }

  /** Kiểm tra thành tiền dòng `index` và "Tổng tiền nhập" trong modal tạo đơn. */
  async verifyImportTotals(index: number, lineTotal: string, grandTotal: string) {
    await this.step(`Kiểm tra thành tiền ${lineTotal}, tổng tiền nhập ${grandTotal}`, async () => {
      await expect(this.imports.itemLineTotal(index)).toHaveText(lineTotal);
      await expect(this.imports.grandTotal).toHaveText(grandTotal);
    });
  }

  /** Nhập "SL thực nhận" cho từng dòng trong modal Nhận hàng. */
  async setReceiveQuantities(quantities: number[]) {
    await this.step(`Nhập SL thực nhận: ${quantities.join(', ')}`, async () => {
      for (const [i, qty] of quantities.entries()) await this.imports.receiveInput(i).fill(String(qty));
    });
  }

  // ---------------------------------------------------------------------------
  // Báo cáo
  // ---------------------------------------------------------------------------

  /** Giả lập API tổng quan báo cáo (ghi lại tham số period/start_date/end_date). */
  async mockReportsOverview(overview: ReportOverviewMock) {
    await this.step('Mock API báo cáo tổng quan', async () => {
      await this.fakeGet('**/api/admin/reports/overview*', () => ({ success: true, overview }));
    });
  }

  /** Mở trang Báo cáo và chờ thẻ tổng quan tải xong. */
  async openReports() {
    await this.step('Mở trang Báo cáo', async () => {
      await this.page.goto(this.reports.path);
      await expect(this.po.adminUi.pageTitle).toHaveText('Báo cáo');
      await expect(this.reports.pageHeading).toHaveText('Báo cáo');
      await expect(this.table.statValue('Doanh thu')).toBeVisible();
    });
  }

  /** Chọn kỳ báo cáo theo value (today, last7days, last30days, thisMonth, custom). */
  async selectReportPeriod(value: string) {
    await this.step(`Chọn kỳ báo cáo "${value}"`, async () => {
      await this.reports.periodSelect.selectOption(value);
    });
  }

  /** Ở kỳ "Tùy chọn": nhập từ ngày, đến ngày (YYYY-MM-DD) và bấm "Lọc". */
  async applyCustomRange(start: string, end: string) {
    await this.step(`Lọc báo cáo từ ${start} đến ${end}`, async () => {
      await this.reports.dateInputs.nth(0).fill(start);
      await this.reports.dateInputs.nth(1).fill(end);
      await this.reports.filterButton.click();
    });
  }

  /** Kiểm tra kỳ "Tùy chọn" mặc định: từ ngày 1 tháng này đến hôm nay (giờ VN). */
  async verifyCustomRangeDefaults() {
    await this.step('Kiểm tra khoảng ngày mặc định của kỳ "Tùy chọn"', async () => {
      const today = vnToday();
      await expect(this.reports.filterButton).toBeVisible();
      await expect(this.reports.dateInputs.nth(1)).toHaveValue(today);
      await expect(this.reports.dateInputs.nth(0)).toHaveValue(`${today.slice(0, 8)}01`);
    });
  }

  /** Kiểm tra bảng trong khối báo cáo có số dòng và dòng đầu chứa các text. */
  async verifyReportSection(heading: string, rows: number, firstRow: string[]) {
    await this.step(`Kiểm tra khối "${heading}" có ${rows} dòng`, async () => {
      await expect(this.reports.sectionRows(heading)).toHaveCount(rows);
      for (const text of firstRow) await expect(this.reports.sectionRows(heading).first()).toContainText(text);
    });
  }

  /** Kiểm tra khối báo cáo (theo tiêu đề h2) chứa các đoạn text. */
  async verifyReportSectionText(heading: string, texts: string[]) {
    await this.step(`Kiểm tra khối "${heading}" chứa: ${texts.join(' | ')}`, async () => {
      for (const text of texts) await expect(this.reports.section(heading)).toContainText(text);
    });
  }

  /** Bấm "Xuất báo cáo", kiểm tra tên file CSV (regex), BOM UTF-8 và các dòng nội dung. */
  async exportReport(filePattern: string, lines: string[]) {
    await this.step(`Xuất báo cáo CSV /${filePattern}/`, async () => {
      const [download] = await Promise.all([this.page.waitForEvent('download'), this.reports.exportButton.click()]);
      expect(download.suggestedFilename()).toMatch(new RegExp(filePattern));
      const content = await fs.readFile(await download.path(), 'utf8');
      expect(content.charCodeAt(0), 'File CSV thiếu BOM UTF-8').toBe(0xfeff);
      for (const line of lines) expect(content).toContain(line);
    });
  }

  // ---------------------------------------------------------------------------
  // Cài đặt
  // ---------------------------------------------------------------------------

  /** Giả lập API GET cài đặt website. */
  async mockSettings(settings: Record<string, string>) {
    await this.step('Mock API GET cài đặt', async () => {
      await this.fakeGet('**/api/admin/settings', () => ({ success: true, settings }));
    });
  }

  /** Mở trang Cài đặt và chờ dữ liệu tải xong. */
  async openSettings() {
    await this.step('Mở trang Cài đặt', async () => {
      await this.page.goto(this.settings.path);
      await expect(this.po.adminUi.pageTitle).toHaveText('Cài đặt');
      await expect(this.settings.pageHeading).toHaveText('Cài đặt');
      await expect(this.settings.panelReady).toBeVisible();
    });
  }

  /** Bấm 1 tab cài đặt, vd: "Bán hàng". */
  async openSettingsTab(label: string) {
    await this.step(`Mở tab cài đặt "${label}"`, async () => {
      await this.settings.tab(label).click();
      await expect(this.settings.panel).toContainText(label);
    });
  }

  /** Kiểm tra tab đang mở có đúng các nhãn ô nhập (theo thứ tự). */
  async verifySettingsFields(labels: string[]) {
    await this.step(`Kiểm tra ô nhập: ${labels.join(' | ')}`, async () => {
      await expect(this.settings.fieldLabels).toHaveCount(labels.length);
      expect((await this.settings.fieldLabels.allTextContents()).map((t) => t.trim())).toEqual(labels);
    });
  }

  /** Kiểm tra trạng thái các checkbox theo nhãn, vd: {"Cho phép COD": true}. */
  async verifyCheckboxes(states: Record<string, boolean>) {
    await this.step(`Kiểm tra checkbox ${JSON.stringify(states)}`, async () => {
      for (const [label, checked] of Object.entries(states)) {
        await (checked
          ? expect(this.po.adminUi.checkbox(label)).toBeChecked()
          : expect(this.po.adminUi.checkbox(label)).not.toBeChecked());
      }
    });
  }

  /** Bấm "Lưu cài đặt". */
  async saveSettings() {
    await this.step('Bấm "Lưu cài đặt"', async () => {
      await this.settings.saveButton.click();
    });
  }
}
