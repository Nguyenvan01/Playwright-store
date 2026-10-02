import { test } from '@fixtures';
import { AUTH_FILES } from '@config/env';
import { loadData } from '@data/loader';
import type { DashboardData } from '@data/admin-sales.types';
import { applyCaseMeta, caseTitle } from '@engine/cases';
import { hasAdminAuth } from '@utils/storage';

const data = loadData<DashboardData>('admin-sales/dashboard.json');
const DASHBOARD_API = '**/api/admin/dashboard';

test.describe('Admin - Tổng quan (dashboard)', () => {
  test.use({ storageState: AUTH_FILES.admin });
  test.skip(() => !hasAdminAuth(), 'Cần E2E_ADMIN_EMAIL/PASSWORD trong .env');

  test('[ADS-DASH-01] Dashboard dữ liệu thật: đủ thẻ thống kê và các khối @smoke', async ({ k }) => {
    await k.admin.openAdminPage('/admin', 'Tổng quan');
    await k.adminSales.verifyApiRequested('/admin/dashboard');
    await k.adminSales.verifyStatCardLabels(data.cardLabels);
    await k.adminSales.verifyDashboardSections(data.sections);
    await k.common.verifyNoPageErrors();
  });

  test.describe('Hiển thị số liệu (mock GET /admin/dashboard)', () => {
    test.beforeEach(async ({ k }) => {
      await k.common.mockGet(DASHBOARD_API, data.response);
      await k.admin.openAdminPage('/admin', 'Tổng quan');
    });

    test('[ADS-DASH-02] Thẻ thống kê hiển thị đúng giá trị, dòng phụ và % doanh thu', async ({ k }) => {
      await k.adminSales.verifyStatCards(data.expected.cards);
    });

    test('[ADS-DASH-03] Khối "Đơn hàng theo trạng thái" đúng số lượng', async ({ k }) => {
      await k.adminSales.verifyOrderStatusBreakdown(data.expected.statusBreakdown);
    });

    test('[ADS-DASH-04] "Đơn hàng gần đây" và "Sản phẩm bán chạy"', async ({ k }) => {
      await k.adminSales.verifyRecentOrders(data.expected.recentOrders);
      await k.adminSales.verifyTopProducts(data.expected.topProducts);
    });

    test('[ADS-DASH-05] Thẻ thao tác nhanh hiển thị đúng số liệu', async ({ k }) => {
      await k.adminSales.verifyQuickCards(data.expected.quickCards);
    });

    test('[ADS-DASH-06] Biểu đồ vẽ vùng doanh thu + đường đơn hàng theo dữ liệu tháng', async ({ k }) => {
      await k.adminSales.verifyChartTicks(data.expected.chartTicks);
      await k.adminSales.verifyChartSeries(data.expected.chartTicks.length);
    });

    test('[ADS-DASH-07] Đổi khoảng thời gian biểu đồ thì tải lại số liệu', async ({ k }) => {
      test.fail(true, 'BUG: AdminDashboard.jsx:227-232 - ô chọn "7 ngày qua/30 ngày qua/..." không có onChange, không gọi lại API');
      await k.adminSales.verifyApiRequested('/admin/dashboard');
      await k.adminSales.selectRevenueRange(data.rangeOption);
      await k.adminSales.verifyApiRequested('/admin/dashboard', { range: data.rangeOption });
    });

    for (const c of data.fakeGrowth) {
      test(caseTitle(c), async ({ k }) => {
        applyCaseMeta(c);
        await k.adminSales.verifyStatCardHasNoChange(c.card);
      });
    }
  });

  test('[ADS-DASH-08] API dashboard lỗi -> hiển thị 0, không crash', async ({ k }) => {
    await k.common.mockGet(DASHBOARD_API, { success: false, message: 'Có lỗi xảy ra, vui lòng thử lại sau.' }, 500);
    await k.admin.openAdminPage('/admin', 'Tổng quan');
    await k.adminSales.verifyStatCards(data.zeroCards);
    await k.adminSales.verifyRecentOrders([]);
  });

  test.describe('Link điều hướng (data-driven)', () => {
    for (const c of data.links) {
      test(caseTitle(c), async ({ k }) => {
        applyCaseMeta(c);
        await k.common.mockGet(DASHBOARD_API, data.response);
        await k.admin.openAdminPage('/admin', 'Tổng quan');
        await k.adminSales.clickDashboardLink(c.label, c.section);
        await k.common.verifyUrl(c.path);
        await k.admin.verifyHeaderTitle(c.pageTitle);
      });
    }

    test('[ADS-DASH-L06] "Xử lý đơn hàng" mở trang Đơn hàng đã lọc "Chờ xác nhận"', async ({ k }) => {
      test.fail(true, 'BUG: AdminDashboard.jsx:384 link tới /admin/orders?status=pending nhưng AdminOrders.jsx:80-83 không đọc query string -> không lọc');
      await k.common.mockGet(DASHBOARD_API, data.response);
      await k.admin.openAdminPage('/admin', 'Tổng quan');
      await k.adminSales.clickDashboardLink('Xử lý đơn hàng');
      await k.admin.verifyHeaderTitle('Đơn hàng');
      await k.adminSales.verifyOrderFilters({ status: 'pending' });
      await k.adminSales.verifyApiRequested('/admin/orders', { status: 'pending' });
    });
  });
});
