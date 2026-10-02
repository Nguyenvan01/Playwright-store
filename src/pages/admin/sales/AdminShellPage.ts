import { Locator, Page } from '@playwright/test';

/**
 * Khung trang quản trị: sidebar (thu gọn, menu, chân sidebar), header (tiêu đề, chuông thông báo, menu người dùng).
 * Lưu ý: h1 header, link sidebar và nút trong menu người dùng trùng tên ("Tổng quan", "Cài đặt", "Đăng xuất")
 * -> luôn scope theo vùng.
 */
export class AdminShellPage {
  readonly sidebar: Locator;
  readonly header: Locator;
  readonly main: Locator;
  readonly pageTitle: Locator;
  /** Nút thu gọn/mở rộng sidebar (icon chevron, không có tên) - nút đầu tiên trong sidebar. */
  readonly sidebarToggle: Locator;
  readonly menuNav: Locator;
  readonly activeMenuLinks: Locator;
  readonly storeLink: Locator;
  readonly sidebarLogout: Locator;
  readonly sidebarUser: Locator;
  /** Chuông thông báo (không có tên) - nút đầu tiên bên phải header. */
  readonly bellButton: Locator;
  readonly bellBadge: Locator;
  readonly notificationPanel: Locator;
  readonly notificationOverlay: Locator;
  readonly notificationEmpty: Locator;
  readonly notificationItems: Locator;
  readonly notificationStats: Locator;
  readonly notificationFooterCount: Locator;
  readonly notificationNewChip: Locator;
  readonly markAllReadButton: Locator;
  readonly refreshButton: Locator;
  readonly closePanelButton: Locator;
  readonly viewAllOrdersLink: Locator;
  /** Nút mở menu người dùng (avatar + tên) - nút thứ 2 bên phải header. */
  readonly userButton: Locator;
  readonly userMenu: Locator;

  constructor(readonly page: Page) {
    this.sidebar = page.locator('aside').first();
    this.header = page.locator('header').first();
    this.main = page.locator('main').first();
    this.pageTitle = this.header.locator('h1');
    this.sidebarToggle = this.sidebar.locator('button').first();
    this.menuNav = this.sidebar.locator('nav');
    this.activeMenuLinks = this.menuNav.locator('a.bg-\\[\\#d71920\\]');
    this.storeLink = this.sidebar.locator('a[href="/"]');
    this.sidebarLogout = this.sidebar.locator('div.border-t button');
    this.sidebarUser = this.sidebar.locator('div.border-t div.bg-gray-50');

    this.bellButton = this.header.getByRole('button').first();
    this.bellBadge = this.bellButton.locator('span');
    this.notificationPanel = page.locator('div.fixed.top-16.right-6');
    this.notificationOverlay = page.locator('div.fixed.inset-0.z-40');
    this.notificationEmpty = this.notificationPanel.getByText('Không có thông báo nào', { exact: true });
    this.notificationItems = this.notificationPanel.locator('div.cursor-pointer');
    this.notificationStats = this.notificationPanel.locator('div.overflow-x-auto > span');
    this.notificationFooterCount = this.notificationPanel.getByText(/^\d+ thông báo$/);
    this.notificationNewChip = this.notificationPanel.getByText(/^\d+ mới$/);
    this.markAllReadButton = this.notificationPanel.getByRole('button', { name: 'Đánh dấu đã đọc', exact: true });
    this.refreshButton = this.notificationPanel.getByTitle('Làm mới', { exact: true });
    this.closePanelButton = this.notificationPanel.locator('div.border-b').first().getByRole('button').last();
    this.viewAllOrdersLink = this.notificationPanel.getByRole('link', { name: 'Xem tất cả đơn hàng', exact: true });

    this.userButton = this.header.getByRole('button').nth(1);
    this.userMenu = this.header.locator('div.absolute.right-0.top-full');
  }

  menuLink(label: string): Locator {
    return this.menuNav.getByRole('link', { name: label, exact: true });
  }

  notificationItem(title: string): Locator {
    return this.notificationItems.filter({ has: this.page.getByText(title, { exact: true }) });
  }

  userMenuItem(label: string): Locator {
    return this.userMenu.getByRole('button', { name: label, exact: true });
  }
}
