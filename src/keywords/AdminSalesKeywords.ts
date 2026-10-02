import { Page, expect } from '@playwright/test';
import type { ApiClient } from '@api/ApiClient';
import type { PageObjects } from '@pages/PageObjects';
import { AdminRequestLog, fulfillGet, includesCI, queryOf } from '@pages/admin/sales/AdminApiMock';
import { AdminShellPage } from '@pages/admin/sales/AdminShellPage';
import { DashboardPage } from '@pages/admin/sales/DashboardPage';
import { OrdersPage } from '@pages/admin/sales/OrdersPage';
import { CustomersPage, EmployeesPage } from '@pages/admin/sales/PeoplePages';
import type {
  CustomerRecord,
  EmployeeRecord,
  OrderDetailExpect,
  OrdersFixture,
  StatCardExpect,
} from '@data/admin-sales.types';
import { BaseKeywords } from './BaseKeywords';

const PAGE_SIZE = 20;

/** Quản trị bán hàng: layout/header/thông báo, dashboard, đơn hàng, khách hàng, nhân viên. */
export class AdminSalesKeywords extends BaseKeywords {
  private readonly shell: AdminShellPage;
  private readonly dashboard: DashboardPage;
  private readonly orders: OrdersPage;
  private readonly customers: CustomersPage;
  private readonly employees: EmployeesPage;
  private readonly requests: AdminRequestLog;

  constructor(page: Page, po: PageObjects, api: ApiClient) {
    super(page, po, api);
    this.shell = new AdminShellPage(page);
    this.dashboard = new DashboardPage(page);
    this.orders = new OrdersPage(page);
    this.customers = new CustomersPage(page);
    this.employees = new EmployeesPage(page);
    this.requests = new AdminRequestLog(page);
  }

  // ===========================================================================
  // Mock dữ liệu đọc (GET) - KHÔNG chặn request ghi
  // ===========================================================================

  /** Mock GET /admin/orders (lọc search/status/payment_status), /admin/orders/stats và /admin/orders/:id. */
  async mockOrdersApi(fixture: OrdersFixture) {
    await this.step(`Mock API đơn hàng (${fixture.orders.length} đơn)`, async () => {
      await this.page.route(/\/api\/admin\/orders(?:\/([^/?#]+))?(?:\?.*)?$/, (route) => {
        const seg = new URL(route.request().url()).pathname.split('/admin/orders')[1]?.replace(/^\//, '') ?? '';
        if (seg === 'stats') return fulfillGet(route, () => ({ stats: fixture.stats ?? {} }));
        if (seg) {
          const order = fixture.orders.find((o) => String(o.id) === seg);
          if (!order) return fulfillGet(route, () => ({ success: false, message: 'Không tìm thấy' }), 404);
          return fulfillGet(route, () => ({ order: { ...order, ...(fixture.details?.[seg] ?? {}) } }));
        }
        const q = queryOf(route);
        const search = q.get('search') ?? '';
        const list = fixture.orders.filter(
          (o) =>
            (!q.get('status') || o.status === q.get('status')) &&
            (!q.get('payment_status') || o.payment_status === q.get('payment_status')) &&
            (!search ||
              ['order_number', 'customer_name', 'customer_phone', 'customer_email'].some((k) => includesCI(o[k], search))),
        );
        const total = fixture.total ?? list.length;
        return fulfillGet(route, () => ({
          orders: list,
          total,
          totalPages: Math.ceil(total / PAGE_SIZE),
          page: Number(q.get('page') ?? 1),
          stats: {},
        }));
      });
    });
  }

  /** Mock GET /admin/customers (lọc search) và /admin/customers/:id. */
  async mockCustomersApi(fixture: { customers: CustomerRecord[]; details?: Record<string, Record<string, unknown>>; total?: number }) {
    await this.step(`Mock API khách hàng (${fixture.customers.length} khách)`, async () => {
      await this.page.route(/\/api\/admin\/customers(?:\/(\d+))?(?:\?.*)?$/, (route) => {
        const id = new URL(route.request().url()).pathname.match(/customers\/(\d+)$/)?.[1];
        if (id) {
          const c = fixture.customers.find((x) => String(x.id) === id);
          return fulfillGet(route, () => ({ success: true, customer: { ...c, ...(fixture.details?.[id] ?? {}) } }));
        }
        const search = queryOf(route).get('search') ?? '';
        const list = fixture.customers.filter(
          (c) => !search || ['name', 'email', 'phone'].some((k) => includesCI(c[k], search)),
        );
        const total = fixture.total ?? list.length;
        return fulfillGet(route, () => ({
          success: true,
          customers: list,
          total,
          totalPages: Math.ceil(total / PAGE_SIZE),
          page: Number(queryOf(route).get('page') ?? 1),
        }));
      });
    });
  }

  /** Mock GET /admin/employees (lọc search theo tên/email). */
  async mockEmployeesApi(fixture: { employees: EmployeeRecord[]; total?: number }) {
    await this.step(`Mock API nhân viên (${fixture.employees.length} người)`, async () => {
      await this.page.route(/\/api\/admin\/employees(?:\?.*)?$/, (route) => {
        const search = queryOf(route).get('search') ?? '';
        const list = fixture.employees.filter((e) => !search || ['name', 'email'].some((k) => includesCI(e[k], search)));
        const total = fixture.total ?? list.length;
        return fulfillGet(route, () => ({
          employees: list,
          total,
          totalPages: Math.ceil(total / PAGE_SIZE),
          page: Number(queryOf(route).get('page') ?? 1),
        }));
      });
    });
  }

  /** Kiểm tra trình duyệt đã gọi GET tới đường dẫn (vd: "/admin/orders") với đủ tham số query. */
  async verifyApiRequested(path: string, params: Record<string, string | number> = {}) {
    await this.step(`Kiểm tra đã gọi GET ${path} ${JSON.stringify(params)}`, async () => {
      await expect
        .poll(() => this.requests.has(path, params), {
          message: `Không thấy GET ${path} với ${JSON.stringify(params)}. Đã gọi: ${this.requests.describe()}`,
        })
        .toBe(true);
    });
  }

  /** Kiểm tra tiêu đề cột bảng theo nội dung gốc (bỏ qua CSS uppercase), đúng thứ tự. */
  async verifyColumns(headers: string[]) {
    await this.step(`Kiểm tra cột bảng: ${headers.join(' | ')}`, async () => {
      const ths = this.page.locator('main table').first().locator('thead th');
      await expect(ths.first()).toBeVisible();
      const texts = (await ths.allTextContents()).map((t) => t.trim()).filter(Boolean);
      expect(texts).toEqual(headers);
    });
  }

  /** Kiểm tra số request GET tới đường dẫn đạt ít nhất `min` lần. */
  async verifyApiRequestCount(path: string, min: number) {
    await this.step(`Kiểm tra GET ${path} được gọi >= ${min} lần`, async () => {
      await expect.poll(() => this.requests.count(path)).toBeGreaterThanOrEqual(min);
    });
  }

  // ===========================================================================
  // Layout: sidebar / header / menu người dùng
  // ===========================================================================

  /** Bấm nút thu gọn / mở rộng sidebar. */
  async toggleSidebar() {
    await this.step('Bấm nút thu gọn/mở rộng sidebar', async () => {
      await this.shell.sidebarToggle.click();
    });
  }

  /** Kiểm tra sidebar đang thu gọn (72px, ẩn chữ menu) hoặc mở rộng (260px). */
  async verifySidebarCollapsed(collapsed: boolean) {
    await this.step(`Kiểm tra sidebar ${collapsed ? 'thu gọn' : 'mở rộng'}`, async () => {
      await expect(this.shell.sidebar).toHaveClass(collapsed ? /w-\[72px\]/ : /w-\[260px\]/);
      await expect(this.shell.main).toHaveClass(collapsed ? /ml-\[72px\]/ : /ml-\[260px\]/);
      await expect(this.shell.header).toHaveClass(collapsed ? /left-\[72px\]/ : /left-\[260px\]/);
      const label = this.shell.menuNav.getByText('Sản phẩm', { exact: true });
      await (collapsed ? expect(label).toHaveCount(0) : expect(label).toBeVisible());
      await (collapsed
        ? expect(this.shell.storeLink.getByText('Xem cửa hàng')).toHaveCount(0)
        : expect(this.shell.storeLink).toHaveText('Xem cửa hàng'));
    });
  }

  /** Kiểm tra chỉ có đúng 1 mục sidebar đang sáng và đó là `label`. */
  async verifyActiveMenu(label: string) {
    await this.step(`Kiểm tra mục sidebar đang chọn là "${label}"`, async () => {
      await expect(this.shell.activeMenuLinks).toHaveCount(1);
      await expect(this.shell.activeMenuLinks).toHaveText(label);
      await expect(this.shell.menuLink(label)).toHaveClass(/bg-\[#d71920\]/);
    });
  }

  /** Bấm "Xem cửa hàng" ở chân sidebar. */
  async clickViewStore() {
    await this.step('Sidebar -> "Xem cửa hàng"', async () => {
      await this.shell.storeLink.click();
    });
  }

  /** Đăng xuất từ chân sidebar ("sidebar") hoặc menu người dùng trên header ("menu"). */
  async logout(from: 'sidebar' | 'menu') {
    await this.step(`Đăng xuất từ ${from === 'sidebar' ? 'sidebar' : 'menu người dùng'}`, async () => {
      if (from === 'sidebar') {
        await this.shell.sidebarLogout.click();
      } else {
        await this.shell.userButton.click();
        await this.shell.userMenuItem('Đăng xuất').click();
      }
    });
  }

  /** Kiểm tra khối người dùng ở chân sidebar (tên + vai trò). */
  async verifySidebarUser(name: string, role: string) {
    await this.step(`Kiểm tra sidebar hiện "${name}" (${role})`, async () => {
      await expect(this.shell.sidebarUser.locator('p').first()).toHaveText(name);
      await expect(this.shell.sidebarUser.locator('p').last()).toHaveText(role);
    });
  }

  /** Mở menu người dùng trên header. */
  async openUserMenu() {
    await this.step('Mở menu người dùng', async () => {
      await this.shell.userButton.click();
      await expect(this.shell.userMenu).toBeVisible();
    });
  }

  /** Kiểm tra nút người dùng và menu thả xuống hiển thị tên, email, 3 mục. */
  async verifyUserMenu(name: string, email: string, role: string) {
    await this.step(`Kiểm tra menu người dùng "${name}" <${email}>`, async () => {
      await expect(this.shell.userButton).toContainText(name);
      await expect(this.shell.userButton).toContainText(role);
      await expect(this.shell.userMenu.locator('p').first()).toHaveText(name);
      await expect(this.shell.userMenu.locator('p').nth(1)).toHaveText(email);
      await expect(this.shell.userMenu.getByRole('button')).toHaveText(['Tổng quan', 'Cài đặt', 'Đăng xuất']);
    });
  }

  /** Bấm 1 mục trong menu người dùng ("Tổng quan" / "Cài đặt" / "Đăng xuất"). */
  async chooseUserMenuItem(label: string) {
    await this.step(`Menu người dùng -> "${label}"`, async () => {
      await this.shell.userMenuItem(label).click();
    });
  }

  /** Bấm ra ngoài menu người dùng (vào tiêu đề trang) để đóng menu. */
  async clickOutsideUserMenu() {
    await this.step('Bấm ra ngoài menu người dùng', async () => {
      await this.shell.pageTitle.click();
    });
  }

  /** Kiểm tra menu người dùng đang mở/đóng. */
  async verifyUserMenuOpen(open: boolean) {
    await this.step(`Kiểm tra menu người dùng ${open ? 'đang mở' : 'đã đóng'}`, async () => {
      await (open ? expect(this.shell.userMenu).toBeVisible() : expect(this.shell.userMenu).toHaveCount(0));
    });
  }

  // ===========================================================================
  // Chuông thông báo
  // ===========================================================================

  /** Bấm chuông thông báo để mở panel. */
  async openNotifications() {
    await this.step('Mở panel thông báo', async () => {
      await this.shell.bellButton.click();
      await expect(this.shell.notificationPanel.getByText('Thông báo', { exact: true })).toBeVisible();
    });
  }

  /** Đóng panel thông báo bằng nút X ("button") hoặc bấm ra ngoài ("overlay"). */
  async closeNotifications(via: 'button' | 'overlay' = 'button') {
    await this.step(`Đóng panel thông báo (${via === 'button' ? 'nút X' : 'bấm ra ngoài'})`, async () => {
      if (via === 'button') await this.shell.closePanelButton.click();
      else await this.shell.notificationOverlay.click({ position: { x: 20, y: 400 } });
    });
  }

  /** Kiểm tra panel thông báo đang mở / đã đóng. */
  async verifyNotificationPanelOpen(open: boolean) {
    await this.step(`Kiểm tra panel thông báo ${open ? 'đang mở' : 'đã đóng'}`, async () => {
      await (open ? expect(this.shell.notificationPanel).toBeVisible() : expect(this.shell.notificationPanel).toHaveCount(0));
    });
  }

  /** Kiểm tra số trên chuông (null = không hiển thị số). */
  async verifyNotificationBadge(expected: string | null) {
    await this.step(`Kiểm tra số trên chuông = ${expected ?? '(không có)'}`, async () => {
      await (expected === null
        ? expect(this.shell.bellBadge).toHaveCount(0)
        : expect(this.shell.bellBadge).toHaveText(expected));
    });
  }

  /** Kiểm tra panel: danh sách tiêu đề thông báo, thanh thống kê và dòng "{n} thông báo". */
  async verifyNotificationPanel(expected: { items: string[]; stats: string[]; footer: string }) {
    await this.step(`Kiểm tra panel có ${expected.items.length} thông báo`, async () => {
      await expect(this.shell.notificationItems.locator('p.font-semibold')).toHaveText(expected.items);
      await expect(this.shell.notificationStats).toHaveText(expected.stats);
      await expect(this.shell.notificationFooterCount).toHaveText(expected.footer);
      await expect(this.shell.viewAllOrdersLink).toBeVisible();
    });
  }

  /** Kiểm tra panel trống: "Không có thông báo nào" và "0 thông báo". */
  async verifyNotificationsEmpty() {
    await this.step('Kiểm tra panel "Không có thông báo nào"', async () => {
      await expect(this.shell.notificationEmpty).toBeVisible();
      await expect(this.shell.notificationItems).toHaveCount(0);
      await expect(this.shell.notificationFooterCount).toHaveText('0 thông báo');
      await expect(this.shell.notificationStats).toHaveCount(0);
    });
  }

  /** Kiểm tra có/không có thông báo theo tiêu đề trong panel. */
  async verifyNotificationVisible(title: string, visible = true) {
    await this.step(`Kiểm tra ${visible ? 'có' : 'không có'} thông báo "${title}"`, async () => {
      const item = this.shell.notificationItem(title);
      await (visible ? expect(item.first()).toBeVisible() : expect(item).toHaveCount(0));
    });
  }

  /** Bấm 1 thông báo theo tiêu đề. */
  async clickNotification(title: string) {
    await this.step(`Bấm thông báo "${title}"`, async () => {
      await this.shell.notificationItem(title).first().click();
    });
  }

  /** Kiểm tra nhãn "{n} mới" cạnh tiêu đề panel (null = không có). */
  async verifyNewNotificationChip(text: string | null) {
    await this.step(`Kiểm tra nhãn thông báo mới = ${text ?? '(không có)'}`, async () => {
      await (text === null
        ? expect(this.shell.notificationNewChip).toHaveCount(0)
        : expect(this.shell.notificationNewChip).toHaveText(text));
      await (text === null
        ? expect(this.shell.markAllReadButton).toHaveCount(0)
        : expect(this.shell.markAllReadButton).toBeVisible());
    });
  }

  /** Bấm "Đánh dấu đã đọc" trong panel thông báo. */
  async markAllNotificationsRead() {
    await this.step('Bấm "Đánh dấu đã đọc"', async () => {
      await this.shell.markAllReadButton.click();
    });
  }

  /** Bấm nút "Làm mới" trong panel thông báo và kiểm tra API thông báo được gọi lại. */
  async refreshNotifications() {
    await this.step('Bấm "Làm mới" thông báo', async () => {
      const before = this.requests.count('/admin/notifications');
      await this.shell.refreshButton.click();
      await expect
        .poll(() => this.requests.count('/admin/notifications'), { message: 'Không gọi lại GET /admin/notifications' })
        .toBeGreaterThan(before);
    });
  }

  /** Bấm "Xem tất cả đơn hàng" ở chân panel thông báo. */
  async clickViewAllOrders() {
    await this.step('Panel thông báo -> "Xem tất cả đơn hàng"', async () => {
      await this.shell.viewAllOrdersLink.click();
    });
  }

  // ===========================================================================
  // Dashboard
  // ===========================================================================

  /** Kiểm tra 4 thẻ thống kê hiển thị đúng nhãn (theo thứ tự). */
  async verifyStatCardLabels(labels: string[]) {
    await this.step(`Kiểm tra thẻ thống kê: ${labels.join(' | ')}`, async () => {
      await expect(this.dashboard.statsGrid.locator('> div p.text-sm')).toHaveText(labels);
    });
  }

  /** Kiểm tra giá trị / dòng phụ / % thay đổi của các thẻ thống kê. */
  async verifyStatCards(cards: StatCardExpect[]) {
    await this.step(`Kiểm tra giá trị ${cards.length} thẻ thống kê`, async () => {
      for (const c of cards) {
        await expect(this.dashboard.statValue(c.label), c.label).toHaveText(c.value);
        if (c.sub !== undefined) await expect(this.dashboard.statSub(c.label), c.label).toHaveText(c.sub);
        if (c.change !== undefined) await expect(this.dashboard.statChange(c.label), c.label).toHaveText(c.change);
      }
    });
  }

  /** Kiểm tra thẻ thống kê KHÔNG hiển thị huy hiệu % tăng/giảm. */
  async verifyStatCardHasNoChange(label: string) {
    await this.step(`Kiểm tra thẻ "${label}" không có % tăng trưởng`, async () => {
      await expect(this.dashboard.statValue(label)).toBeVisible();
      await expect(this.dashboard.statChange(label)).toHaveCount(0);
    });
  }

  /** Kiểm tra các khối tiêu đề trên dashboard. */
  async verifyDashboardSections(titles: string[]) {
    await this.step(`Kiểm tra các khối: ${titles.join(' | ')}`, async () => {
      for (const t of titles) await expect(this.dashboard.sectionHeading(t)).toBeVisible();
    });
  }

  /** Kiểm tra số lượng đơn theo từng trạng thái (khối "Đơn hàng theo trạng thái"). */
  async verifyOrderStatusBreakdown(values: Record<string, string>) {
    await this.step('Kiểm tra khối "Đơn hàng theo trạng thái"', async () => {
      for (const [label, value] of Object.entries(values)) {
        await expect(this.dashboard.statusValue(label), label).toHaveText(value);
      }
    });
  }

  /** Kiểm tra danh sách "Đơn hàng gần đây" (mã, khách, tổng tiền, trạng thái). */
  async verifyRecentOrders(orders: { number: string; customer: string; total: string; status: string }[]) {
    await this.step(`Kiểm tra ${orders.length} đơn hàng gần đây`, async () => {
      const rows = this.dashboard.sectionRows('Đơn hàng gần đây');
      await expect(rows).toHaveCount(orders.length);
      for (const [i, o] of orders.entries()) {
        const row = rows.nth(i);
        await expect(row.locator('p').first()).toHaveText(o.number);
        await expect(row).toContainText(o.customer);
        await expect(row).toContainText(o.total);
        await expect(row.locator('span.rounded-full')).toHaveText(o.status);
      }
    });
  }

  /** Kiểm tra danh sách "Sản phẩm bán chạy" (tên + số đã bán, theo thứ tự). */
  async verifyTopProducts(products: { name: string; sold: string }[]) {
    await this.step(`Kiểm tra ${products.length} sản phẩm bán chạy`, async () => {
      const rows = this.dashboard.sectionRows('Sản phẩm bán chạy');
      await expect(rows).toHaveCount(products.length);
      for (const [i, p] of products.entries()) {
        await expect(rows.nth(i)).toContainText(`${i + 1}`);
        await expect(rows.nth(i).locator('p.truncate')).toHaveText(p.name);
        await expect(rows.nth(i)).toContainText(p.sold);
      }
    });
  }

  /** Kiểm tra giá trị các thẻ thao tác nhanh cuối dashboard. */
  async verifyQuickCards(cards: { title: string; value: string }[]) {
    await this.step(`Kiểm tra ${cards.length} thẻ thao tác nhanh`, async () => {
      for (const c of cards) await expect(this.dashboard.quickCardValue(c.title), c.title).toHaveText(c.value);
    });
  }

  /** Bấm 1 link trên dashboard; `section` dùng khi trùng tên (vd: "Xem tất cả"). */
  async clickDashboardLink(label: string, section?: string) {
    await this.step(`Dashboard -> "${label}"${section ? ` (${section})` : ''}`, async () => {
      await (section ? this.dashboard.sectionLink(section, label) : this.dashboard.quickLink(label)).click();
    });
  }

  /** Kiểm tra nhãn trục X của biểu đồ doanh thu. */
  async verifyChartTicks(ticks: string[]) {
    await this.step(`Kiểm tra trục X biểu đồ: ${ticks.join(', ')}`, async () => {
      await expect(this.dashboard.chartTicks).toHaveText(ticks);
    });
  }

  /** Kiểm tra biểu đồ vẽ vùng doanh thu + đường đơn hàng với `points` điểm dữ liệu. */
  async verifyChartSeries(points: number) {
    await this.step(`Kiểm tra biểu đồ có vùng doanh thu + đường đơn hàng (${points} điểm)`, async () => {
      await expect(this.dashboard.chartAreas).toHaveCount(1);
      await expect(this.dashboard.chartLines).toHaveCount(1);
      await expect(this.dashboard.chartLineDots).toHaveCount(points);
    });
  }

  /** Chọn khoảng thời gian cho biểu đồ doanh thu, vd: "30 ngày qua". */
  async selectRevenueRange(option: string) {
    await this.step(`Chọn khoảng "${option}" cho biểu đồ`, async () => {
      await this.dashboard.rangeSelect.selectOption({ label: option });
    });
  }

  // ===========================================================================
  // Đơn hàng
  // ===========================================================================

  /** Kiểm tra số lượng trên 7 thẻ trạng thái đơn hàng. */
  async verifyOrderStatusCards(counts: Record<string, string>) {
    await this.step('Kiểm tra thẻ trạng thái đơn hàng', async () => {
      for (const [label, count] of Object.entries(counts)) {
        await expect(this.orders.statusCardCount(label), label).toHaveText(count);
      }
    });
  }

  /** Bấm 1 thẻ trạng thái đơn hàng (bật/tắt lọc). */
  async clickOrderStatusCard(label: string) {
    await this.step(`Bấm thẻ trạng thái "${label}"`, async () => {
      await this.orders.statusCard(label).click();
    });
  }

  /** Kiểm tra thẻ trạng thái đang được chọn (viền đỏ) hay không. */
  async verifyOrderStatusCardActive(label: string, active: boolean) {
    await this.step(`Kiểm tra thẻ "${label}" ${active ? 'đang chọn' : 'không chọn'}`, async () => {
      await (active
        ? expect(this.orders.statusCard(label)).toHaveClass(/ring-2/)
        : expect(this.orders.statusCard(label)).not.toHaveClass(/ring-2/));
    });
  }

  /** Gõ từ khóa vào ô tìm đơn hàng. */
  async searchOrders(text: string) {
    await this.step(`Tìm đơn hàng "${text}"`, async () => {
      await this.orders.searchInput.fill(text);
    });
  }

  /** Chọn lọc trạng thái đơn (value: pending, confirmed... hoặc "" = tất cả). */
  async filterOrdersByStatus(value: string) {
    await this.step(`Lọc trạng thái đơn = "${value}"`, async () => {
      await this.orders.statusSelect.selectOption(value);
    });
  }

  /** Chọn lọc trạng thái thanh toán (value: unpaid, paid, partially_paid, refunded). */
  async filterOrdersByPayment(value: string) {
    await this.step(`Lọc thanh toán = "${value}"`, async () => {
      await this.orders.paymentSelect.selectOption(value);
    });
  }

  /** Mở "Bộ lọc" và nhập khoảng ngày (yyyy-mm-dd). */
  async filterOrdersByDate(from: string, to: string) {
    await this.step(`Lọc đơn từ ${from} đến ${to}`, async () => {
      if (!(await this.orders.clearFiltersButton.isVisible())) await this.orders.filtersButton.click();
      await this.orders.dateInput('Từ ngày').fill(from);
      await this.orders.dateInput('Đến ngày').fill(to);
    });
  }

  /** Bấm "Bộ lọc" rồi "Xóa bộ lọc". */
  async clearOrderFilters() {
    await this.step('Xóa bộ lọc đơn hàng', async () => {
      if (!(await this.orders.clearFiltersButton.isVisible())) await this.orders.filtersButton.click();
      await this.orders.clearFiltersButton.click();
    });
  }

  /** Kiểm tra giá trị hiện tại của ô tìm kiếm, lọc trạng thái, lọc thanh toán. */
  async verifyOrderFilters(expected: { search?: string; status?: string; payment?: string }) {
    await this.step(`Kiểm tra bộ lọc đơn ${JSON.stringify(expected)}`, async () => {
      if (expected.search !== undefined) await expect(this.orders.searchInput).toHaveValue(expected.search);
      if (expected.status !== undefined) await expect(this.orders.statusSelect).toHaveValue(expected.status);
      if (expected.payment !== undefined) await expect(this.orders.paymentSelect).toHaveValue(expected.payment);
    });
  }

  /** Kiểm tra bảng đơn hàng hiển thị đúng các mã đơn (theo thứ tự). */
  async verifyOrderRows(numbers: string[]) {
    await this.step(`Kiểm tra bảng đơn: ${numbers.join(', ')}`, async () => {
      await expect(this.orders.orderNumbers).toHaveText(numbers);
    });
  }

  /** Kiểm tra 1 dòng đơn hàng: khách, số sản phẩm, tổng tiền, thanh toán, trạng thái. */
  async verifyOrderRow(row: { number: string; customer: string; items: string; total: string; payment: string; status: string }) {
    await this.step(`Kiểm tra dòng đơn ${row.number}`, async () => {
      const r = this.orders.row(row.number);
      await expect(r.locator('td').nth(1).locator('p').first()).toHaveText(row.customer);
      await expect(r.locator('td').nth(3)).toHaveText(row.items);
      await expect(r.locator('td').nth(4)).toHaveText(row.total);
      await expect(this.orders.rowPayment(row.number)).toHaveText(row.payment);
      await expect(this.orders.rowStatus(row.number)).toHaveText(row.status);
    });
  }

  /** Kiểm tra trạng thái hiển thị trên dòng đơn hàng. */
  async verifyOrderRowStatus(number: string, label: string) {
    await this.step(`Kiểm tra đơn ${number} có trạng thái "${label}"`, async () => {
      await expect(this.orders.rowStatus(number)).toHaveText(label);
    });
  }

  /** Kiểm tra bảng trống "Không có đơn hàng nào" và "0 đơn hàng". */
  async verifyOrdersEmpty() {
    await this.step('Kiểm tra "Không có đơn hàng nào"', async () => {
      await expect(this.orders.emptyText).toBeVisible();
      await expect(this.orders.totalText).toHaveText('0 đơn hàng');
    });
  }

  /** Bấm "Xem chi tiết" trên dòng đơn hàng và chờ modal chi tiết. */
  async openOrderDetail(number: string) {
    await this.step(`Mở chi tiết đơn ${number}`, async () => {
      await this.orders.rowAction(number, 'Xem chi tiết').click();
      await expect(this.orders.detailHeading).toHaveText(`Chi tiết đơn hàng #${number}`);
    });
  }

  /** Đóng modal chi tiết đơn (nút X). */
  async closeOrderDetail() {
    await this.step('Đóng modal chi tiết đơn', async () => {
      await this.orders.detailCloseButton.click();
      await expect(this.orders.detailModal).toHaveCount(0);
    });
  }

  /** Kiểm tra nội dung modal chi tiết đơn: người nhận, địa chỉ, thông tin, sản phẩm, tổng tiền, lịch sử. */
  async verifyOrderDetail(d: OrderDetailExpect) {
    await this.step(`Kiểm tra chi tiết đơn ${d.number}`, async () => {
      const m = this.orders.detailModal;
      await expect(this.orders.detailHeading).toHaveText(d.heading);
      await expect(this.orders.detailStatusBadge).toHaveText(d.status);
      await expect(this.orders.detailPaymentBadge).toHaveText(d.payment);
      await expect(this.orders.detailBlock('Người nhận')).toContainText(d.recipient);
      await expect(this.orders.detailBlock('Người nhận')).toContainText(d.email);
      await expect(this.orders.detailBlock('Người nhận')).toContainText(d.phone);
      await expect(this.orders.detailBlock('Địa chỉ giao hàng')).toContainText(d.address);
      for (const [label, value] of Object.entries(d.info)) {
        await expect(this.orders.detailInfo(label), label).toHaveText(value);
      }
      await expect(m.getByRole('heading', { name: `Sản phẩm (${d.items.length})`, exact: true })).toBeVisible();
      await expect(this.orders.detailItems).toHaveCount(d.items.length);
      for (const [i, item] of d.items.entries()) {
        const row = this.orders.detailItems.nth(i);
        await expect(row).toContainText(item.name);
        await expect(row).toContainText(item.variant);
        await expect(row.locator('td').nth(1)).toHaveText(item.qty);
        await expect(row.locator('td').last()).toHaveText(item.total);
      }
      for (const [label, value] of Object.entries(d.summary)) {
        await expect(this.orders.summaryValue(label), label).toHaveText(value);
      }
      await expect(this.orders.detailLogs.locator('p.text-gray-700')).toHaveText(d.logs);
    });
  }

  /** Kiểm tra các nút chuyển trạng thái trong modal chi tiết ([] = không có khối cập nhật trạng thái). */
  async verifyOrderStatusButtons(labels: string[]) {
    await this.step(`Kiểm tra nút trạng thái: ${labels.join(', ') || '(không có)'}`, async () => {
      await expect(this.orders.detailHeading).toBeVisible();
      await (labels.length
        ? expect(this.orders.statusButtons).toHaveText(labels)
        : expect(this.orders.statusSection).toHaveCount(0));
    });
  }

  /** Bấm 1 nút chuyển trạng thái trong modal chi tiết đơn. */
  async clickOrderStatusButton(label: string) {
    await this.step(`Bấm nút trạng thái "${label}"`, async () => {
      await this.orders.statusButtons.getByText(label, { exact: true }).click();
    });
  }

  /** Kiểm tra huy hiệu trạng thái trên đầu modal chi tiết. */
  async verifyOrderDetailStatus(label: string) {
    await this.step(`Kiểm tra modal chi tiết có trạng thái "${label}"`, async () => {
      await expect(this.orders.detailStatusBadge).toHaveText(label);
    });
  }

  /** Kiểm tra hiện/ẩn cảnh báo "Lưu ý khi xử lý" (đơn đang giao/đã giao). */
  async verifyOrderProcessingWarning(visible: boolean) {
    await this.step(`Kiểm tra ${visible ? 'có' : 'không có'} "Lưu ý khi xử lý"`, async () => {
      await (visible ? expect(this.orders.processingWarning).toBeVisible() : expect(this.orders.processingWarning).toHaveCount(0));
    });
  }

  /** Chọn trạng thái thanh toán trong modal chi tiết (value: paid, unpaid, partially_paid). */
  async changeOrderPayment(value: string) {
    await this.step(`Cập nhật thanh toán = "${value}"`, async () => {
      await this.orders.detailPaymentSelect.selectOption(value);
    });
  }

  /** Kiểm tra trạng thái thanh toán trên modal chi tiết và khối "Cập nhật thanh toán" có hiện không. */
  async verifyOrderDetailPayment(label: string, editable: boolean) {
    await this.step(`Kiểm tra thanh toán "${label}" (${editable ? 'còn' : 'không còn'} cho sửa)`, async () => {
      await expect(this.orders.detailPaymentBadge).toHaveText(label);
      await (editable ? expect(this.orders.paymentSection).toBeVisible() : expect(this.orders.paymentSection).toHaveCount(0));
    });
  }

  /** Kiểm tra dòng đơn có/không có nút "Hủy đơn". */
  async verifyOrderCancelAction(number: string, visible: boolean) {
    await this.step(`Kiểm tra đơn ${number} ${visible ? 'có' : 'không có'} nút "Hủy đơn"`, async () => {
      await expect(this.orders.rowAction(number, 'Xem chi tiết')).toBeVisible();
      await (visible
        ? expect(this.orders.rowAction(number, 'Hủy đơn')).toBeVisible()
        : expect(this.orders.rowAction(number, 'Hủy đơn')).toHaveCount(0));
    });
  }

  /** Bấm nút "Hủy đơn" trên dòng đơn hàng và chờ modal "Hủy đơn hàng". */
  async openCancelOrder(number: string) {
    await this.step(`Mở hủy đơn ${number}`, async () => {
      await this.orders.rowAction(number, 'Hủy đơn').click();
      await expect(this.orders.cancelModal).toBeVisible();
    });
  }

  /** Nhập lý do hủy đơn trong modal "Hủy đơn hàng". */
  async fillCancelReason(reason: string) {
    await this.step(`Nhập lý do hủy "${reason}"`, async () => {
      await this.orders.cancelReason.fill(reason);
    });
  }

  /** Kiểm tra các ghi chú (hoàn tiền / hoàn điểm) trong modal hủy đơn. */
  async verifyCancelNotes(notes: string[]) {
    await this.step(`Kiểm tra ghi chú hủy đơn: ${notes.join(' | ') || '(không có)'}`, async () => {
      await expect(this.orders.cancelModal).toBeVisible();
      await expect(this.orders.cancelNotes).toHaveText(notes);
    });
  }

  // ===========================================================================
  // Phân trang (đơn hàng / khách hàng / nhân viên)
  // ===========================================================================

  /** Bấm số trang trên thanh phân trang. */
  async goToPage(n: number) {
    await this.step(`Bấm trang ${n}`, async () => {
      await this.orders.pageButton(n).click();
    });
  }

  /** Bấm nút trang sau (mũi tên phải / "Sau"). */
  async clickNextPage() {
    await this.step('Bấm trang sau', async () => {
      await this.customers.nextPageButton.click();
    });
  }

  /** Kiểm tra dòng chữ phân trang, vd: "Trang 1 / 3 — 45 đơn hàng". */
  async verifyPaginationText(text: string) {
    await this.step(`Kiểm tra phân trang "${text}"`, async () => {
      await expect(this.customers.paginationText).toHaveText(text);
    });
  }

  /** Kiểm tra có/không có nút số trang. */
  async verifyPageButton(n: number, visible = true) {
    await this.step(`Kiểm tra ${visible ? 'có' : 'không có'} nút trang ${n}`, async () => {
      await (visible ? expect(this.orders.pageButton(n)).toBeVisible() : expect(this.orders.pageButton(n)).toHaveCount(0));
    });
  }

  // ===========================================================================
  // Khách hàng / Nhân viên
  // ===========================================================================

  /** Kiểm tra danh sách lỗi dưới ô nhập trong modal có tiêu đề `heading` (đúng thứ tự, [] = không lỗi). */
  async verifyFieldErrors(heading: string, errors: string[]) {
    await this.step(`Kiểm tra lỗi form "${heading}": ${errors.join(' | ') || '(không có)'}`, async () => {
      await expect(this.customers.modal(heading)).toBeVisible();
      await expect(this.customers.fieldErrors(heading)).toHaveText(errors);
    });
  }

  /** Kiểm tra modal có tiêu đề `heading` chứa đoạn chữ. */
  async verifyModalText(heading: string, text: string) {
    await this.step(`Kiểm tra modal "${heading}" có "${text}"`, async () => {
      await expect(this.customers.modal(heading).getByText(text, { exact: true })).toBeVisible();
    });
  }

  /** Kiểm tra placeholder của ô nhập theo label. */
  async verifyFieldPlaceholder(label: string, placeholder: string) {
    await this.step(`Kiểm tra ô "${label}" có placeholder "${placeholder}"`, async () => {
      await expect(this.po.adminUi.field(label)).toHaveAttribute('placeholder', placeholder);
    });
  }

  /** Kiểm tra dòng khách hàng: trạng thái, tổng chi tiêu, điểm. */
  async verifyCustomerRow(row: { name: string; status: string; spent?: string; points?: string }) {
    await this.step(`Kiểm tra dòng khách "${row.name}"`, async () => {
      await expect(this.customers.statusBadge(row.name)).toHaveText(row.status);
      if (row.spent) await expect(this.customers.cell(row.name, 3)).toHaveText(row.spent);
      if (row.points) await expect(this.customers.cell(row.name, 4)).toHaveText(row.points);
    });
  }

  /** Kiểm tra modal "Chi tiết khách hàng": tên, email, số liệu, thông tin, đơn gần đây. */
  async verifyCustomerDetail(d: {
    name: string;
    email: string;
    stats: Record<string, string>;
    values: Record<string, string>;
    recentOrders: string[];
  }) {
    await this.step(`Kiểm tra chi tiết khách "${d.name}"`, async () => {
      const m = this.customers.modal('Chi tiết khách hàng');
      await expect(m.locator('p.font-bold').first()).toHaveText(d.name);
      await expect(m.getByText(d.email, { exact: true })).toBeVisible();
      for (const [label, value] of Object.entries(d.stats)) await expect(this.customers.detailStat(label), label).toHaveText(value);
      for (const [label, value] of Object.entries(d.values)) await expect(this.customers.detailValue(label), label).toHaveText(value);
      await expect(this.customers.detailRecentOrders.locator('p.font-medium.text-gray-800')).toHaveText(d.recentOrders);
    });
  }

  /** Kiểm tra nhãn trạng thái của các đơn gần đây trong modal "Chi tiết khách hàng" (đúng thứ tự). */
  async verifyCustomerRecentOrderStatuses(labels: string[]) {
    await this.step(`Kiểm tra trạng thái đơn gần đây: ${labels.join(', ')}`, async () => {
      await expect(this.customers.detailRecentOrders.locator('p.text-xs.font-medium')).toHaveText(labels);
    });
  }

  /** Kiểm tra cảnh báo "khách đã có đơn -> khóa thay vì xóa" trong modal xóa (null = không có). */
  async verifyCustomerDeleteWarning(text: string | null) {
    await this.step(`Kiểm tra cảnh báo xóa khách = ${text ?? '(không có)'}`, async () => {
      await expect(this.customers.modal('Xác nhận xóa')).toBeVisible();
      await (text === null
        ? expect(this.customers.deleteWarning).toHaveCount(0)
        : expect(this.customers.deleteWarning).toHaveText(text));
    });
  }

  /** Kiểm tra có/không có dòng (khách hàng / nhân viên) theo tên chính xác. */
  async verifyPersonRow(name: string, visible = true) {
    await this.step(`Kiểm tra ${visible ? 'có' : 'không có'} dòng "${name}"`, async () => {
      await (visible ? expect(this.customers.row(name)).toBeVisible() : expect(this.customers.rows(name)).toHaveCount(0));
    });
  }

  /** Kiểm tra tiêu đề "Tài khoản nhân viên" trên trang nhân viên. */
  async verifyEmployeesHeading(text: string) {
    await this.step(`Kiểm tra tiêu đề "${text}"`, async () => {
      await expect(this.page.getByRole('heading', { name: text, exact: true })).toBeVisible();
    });
  }

  /** Kiểm tra nhãn vai trò của nhân viên. */
  async verifyEmployeeRole(name: string, label: string) {
    await this.step(`Kiểm tra "${name}" có vai trò "${label}"`, async () => {
      await expect(this.employees.roleBadge(name)).toHaveText(label);
    });
  }

  /** Bấm nút trên dòng nhân viên: "Sửa", "Xóa" (icon không title) hoặc "Trạng thái" (nút gạt). */
  async clickEmployeeAction(name: string, action: 'Sửa' | 'Xóa' | 'Trạng thái') {
    await this.step(`Nhân viên "${name}" -> ${action}`, async () => {
      const btn =
        action === 'Sửa'
          ? this.employees.editButton(name)
          : action === 'Xóa'
            ? this.employees.deleteButton(name)
            : this.employees.toggleButton(name);
      await btn.click();
    });
  }

  /** Kiểm tra nút gạt trạng thái nhân viên đang bật (xanh) hay tắt (xám). */
  async verifyEmployeeActive(name: string, active: boolean) {
    await this.step(`Kiểm tra "${name}" ${active ? 'đang hoạt động' : 'bị vô hiệu'}`, async () => {
      await expect(this.employees.toggleButton(name)).toHaveClass(active ? /text-green-500/ : /text-gray-300/);
    });
  }

  /** Kiểm tra ô Email trong form nhân viên bị trình duyệt đánh dấu không hợp lệ (chặn submit). */
  async verifyEmployeeEmailNativeInvalid(editing = false) {
    await this.step('Kiểm tra ô Email bị trình duyệt chặn (type=email)', async () => {
      const input = this.employees.emailInput(editing);
      expect(await input.evaluate((el: HTMLInputElement) => el.validity.valid)).toBe(false);
      expect(await input.evaluate((el: HTMLInputElement) => el.validationMessage)).not.toBe('');
    });
  }
}
