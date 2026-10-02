import { test } from '@fixtures';
import { AUTH_FILES } from '@config/env';
import { loadData } from '@data/loader';
import type { LayoutData } from '@data/admin-sales.types';
import { applyCaseMeta, caseTitle } from '@engine/cases';
import { hasAdminAuth } from '@utils/storage';

const data = loadData<LayoutData>('admin-sales/layout.json');
const NOTI = '**/api/admin/notifications';

test.describe('Admin - khung trang (sidebar, header, thông báo)', () => {
  test.use({ storageState: AUTH_FILES.admin });
  test.skip(() => !hasAdminAuth(), 'Cần E2E_ADMIN_EMAIL/PASSWORD trong .env');

  test.describe('Tiêu đề trang trên header (data-driven)', () => {
    for (const c of data.titles) {
      test(caseTitle(c), async ({ k }) => {
        applyCaseMeta(c);
        await k.common.goto(c.path);
        await k.admin.verifyHeaderTitle(c.expect);
      });
    }
  });

  test.describe('Sidebar', () => {
    test('[ADS-LAY-S01] Thu gọn rồi mở rộng sidebar @smoke', async ({ k }) => {
      await k.admin.openAdminPage('/admin/products', 'Sản phẩm');
      await k.adminSales.verifySidebarCollapsed(false);
      await k.adminSales.toggleSidebar();
      await k.adminSales.verifySidebarCollapsed(true);
      await k.adminSales.toggleSidebar();
      await k.adminSales.verifySidebarCollapsed(false);
    });

    for (const c of data.activeMenu) {
      test(caseTitle(c), async ({ k }) => {
        applyCaseMeta(c);
        await k.common.goto(c.path);
        await k.adminSales.verifyActiveMenu(c.active);
      });
    }

    test('[ADS-LAY-S02] Chân sidebar hiển thị tên + vai trò tài khoản đang đăng nhập', async ({ k }) => {
      await k.common.mockGet('**/api/admin/profile', data.profile);
      await k.admin.openAdminPage('/admin/brands', 'Thương hiệu');
      await k.adminSales.verifySidebarUser(data.profile.user.name, data.profile.user.role);
    });

    test('[ADS-LAY-S03] "Xem cửa hàng" về trang chủ', async ({ k }) => {
      await k.admin.openAdminPage('/admin/brands', 'Thương hiệu');
      await k.adminSales.clickViewStore();
      await k.common.verifyUrl('/');
      await k.common.verifyLayoutLoaded();
    });

    test('[ADS-LAY-S04] "Đăng xuất" ở sidebar về trang đăng nhập admin', async ({ k }) => {
      await k.admin.openAdminPage('/admin/brands', 'Thương hiệu');
      await k.adminSales.logout('sidebar');
      await k.admin.verifyOnAdminLogin();
      // Token đã bị xóa -> vào lại trang quản trị bị chặn
      await k.common.goto('/admin/products');
      await k.admin.verifyOnAdminLogin();
    });
  });

  test.describe('Menu người dùng', () => {
    test('[ADS-LAY-U00] Mở menu hiển thị tên, email và 3 mục; bấm ra ngoài thì đóng', async ({ k }) => {
      await k.common.mockGet('**/api/admin/profile', data.profile);
      await k.admin.openAdminPage('/admin/brands', 'Thương hiệu');
      await k.adminSales.openUserMenu();
      await k.adminSales.verifyUserMenu(data.profile.user.name, data.profile.user.email, data.profile.user.role);
      await k.adminSales.clickOutsideUserMenu();
      await k.adminSales.verifyUserMenuOpen(false);
    });

    for (const c of data.userMenu) {
      test(caseTitle(c), async ({ k }) => {
        applyCaseMeta(c);
        await k.common.goto(c.from);
        await k.adminSales.openUserMenu();
        await k.adminSales.chooseUserMenuItem(c.item);
        await k.common.verifyUrl(c.path);
        await k.admin.verifyHeaderTitle(c.pageTitle);
        await k.adminSales.verifyUserMenuOpen(false);
      });
    }

    test('[ADS-LAY-U03] "Đăng xuất" trong menu người dùng về trang đăng nhập admin', async ({ k }) => {
      await k.admin.openAdminPage('/admin/brands', 'Thương hiệu');
      await k.adminSales.logout('menu');
      await k.admin.verifyOnAdminLogin();
    });
  });

  test.describe('Chuông thông báo (mock GET /admin/notifications)', () => {
    for (const c of data.notifications.badges) {
      test(caseTitle(c), async ({ k }) => {
        applyCaseMeta(c);
        await k.common.mockGet(NOTI, data.notifications[c.response]);
        await k.admin.openAdminPage('/admin/brands', 'Thương hiệu');
        await k.adminSales.verifyApiRequested('/admin/notifications');
        await k.adminSales.verifyNotificationBadge(c.badge);
      });
    }

    test('[ADS-NOTI-01] Không có thông báo -> panel trống', async ({ k }) => {
      await k.common.mockGet(NOTI, data.notifications.empty);
      await k.admin.openAdminPage('/admin/brands', 'Thương hiệu');
      await k.adminSales.openNotifications();
      await k.adminSales.verifyNotificationsEmpty();
      await k.adminSales.verifyNewNotificationChip(null);
    });

    test('[ADS-NOTI-02] Panel hiển thị danh sách, thống kê và tổng số thông báo @smoke', async ({ k }) => {
      await k.common.mockGet(NOTI, data.notifications.some);
      await k.admin.openAdminPage('/admin/brands', 'Thương hiệu');
      await k.adminSales.openNotifications();
      await k.adminSales.verifyNotificationPanel(data.notifications.panel);
    });

    test('[ADS-NOTI-03] "Đánh dấu đã đọc" ẩn nhãn "n mới"', async ({ k }) => {
      await k.common.mockGet(NOTI, data.notifications.some);
      await k.admin.openAdminPage('/admin/brands', 'Thương hiệu');
      await k.adminSales.openNotifications();
      await k.adminSales.verifyNewNotificationChip(data.notifications.panel.newChip);
      await k.adminSales.markAllNotificationsRead();
      await k.adminSales.verifyNewNotificationChip(null);
    });

    test('[ADS-NOTI-04] Bấm 1 thông báo -> điều hướng theo link và đóng panel', async ({ k }) => {
      const target = data.notifications.clickItem;
      await k.common.mockGet(NOTI, data.notifications.some);
      await k.admin.openAdminPage('/admin/brands', 'Thương hiệu');
      await k.adminSales.openNotifications();
      await k.adminSales.clickNotification(target.title);
      await k.common.verifyUrl(target.path);
      await k.admin.verifyHeaderTitle(target.pageTitle);
      await k.adminSales.verifyNotificationPanelOpen(false);
    });

    test('[ADS-NOTI-05] "Xem tất cả đơn hàng" -> /admin/orders', async ({ k }) => {
      await k.common.mockGet(NOTI, data.notifications.some);
      await k.admin.openAdminPage('/admin/brands', 'Thương hiệu');
      await k.adminSales.openNotifications();
      await k.adminSales.clickViewAllOrders();
      await k.common.verifyUrl('/admin/orders');
      await k.adminSales.verifyNotificationPanelOpen(false);
    });

    test('[ADS-NOTI-06] "Làm mới" gọi lại API thông báo', async ({ k }) => {
      await k.common.mockGet(NOTI, data.notifications.some);
      await k.admin.openAdminPage('/admin/brands', 'Thương hiệu');
      await k.adminSales.openNotifications();
      await k.adminSales.verifyNotificationPanel(data.notifications.panel);
      await k.adminSales.refreshNotifications();
    });

    test('[ADS-NOTI-07] Đóng panel bằng nút X và bằng bấm ra ngoài', async ({ k }) => {
      await k.common.mockGet(NOTI, data.notifications.empty);
      await k.admin.openAdminPage('/admin/brands', 'Thương hiệu');
      await k.adminSales.openNotifications();
      await k.adminSales.closeNotifications('button');
      await k.adminSales.verifyNotificationPanelOpen(false);
      await k.adminSales.openNotifications();
      await k.adminSales.closeNotifications('overlay');
      await k.adminSales.verifyNotificationPanelOpen(false);
    });
  });
});
