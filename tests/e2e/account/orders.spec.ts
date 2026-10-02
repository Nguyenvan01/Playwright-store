import { test } from '@fixtures';
import { AUTH_FILES } from '@config/env';
import { loadData } from '@data/loader';
import type { OrderDetailData, OrdersData } from '@data/account.types';
import { applyCaseMeta, caseTitle } from '@engine/cases';
import { hasCustomerAuth } from '@utils/storage';
import { API } from './support';

const data = loadData<OrdersData>('account/orders.json');
const detail = loadData<OrderDetailData>('account/order-detail.json');

/** Trang "Đơn hàng của tôi" với danh sách đơn đủ mọi trạng thái (mock GET /api/orders). */
test.describe('Đơn hàng của tôi', () => {
  test.use({ storageState: AUTH_FILES.customer });
  test.skip(() => !hasCustomerAuth(), 'Chưa có tài khoản test (xem .env)');

  test('[ACC-ORD-E01] Tài khoản chưa có đơn: thống kê 0 và thông báo trống', async ({ k }) => {
    await k.common.mockGet(API.orders, data.empty);
    await k.account.openOrders();
    await k.account.verifyOrdersLoaded();
    await k.account.verifyOrdersEmpty(data.emptyMessage);
    await k.account.verifyOrderStats({ 'Tất cả đơn': 0, 'Chờ xác nhận': 0, 'Đang giao': 0, 'Đã giao': 0, 'Đã hủy': 0 });
  });

  test.describe('Có đơn hàng', () => {
    test.beforeEach(async ({ k }) => {
      await k.common.mockGet(API.orders, data.list);
      await k.account.openOrders();
      await k.account.verifyOrdersLoaded();
    });

    test('[ACC-ORD-01] Hiển thị thống kê và toàn bộ đơn (mới nhất trước) @smoke', async ({ k }) => {
      await k.account.verifyOrderStats(data.stats);
      await k.account.verifyOrderList(data.allCodes);
    });

    test.describe('Lọc theo tab trạng thái (data-driven)', () => {
      for (const c of data.tabs) {
        test(caseTitle(c), async ({ k }) => {
          applyCaseMeta(c);
          await k.account.filterOrdersByStatus(c.tab);
          await k.account.verifyOrderList(c.expected);
        });
      }
    });

    test.describe('Lọc bằng ô thống kê (data-driven)', () => {
      for (const c of data.statButtons) {
        test(caseTitle(c), async ({ k }) => {
          applyCaseMeta(c);
          await k.account.clickOrderStat(c.stat);
          await k.account.verifyOrderList(c.expected);
        });
      }
    });

    test.describe('Tìm theo mã đơn (data-driven)', () => {
      for (const c of data.search) {
        test(caseTitle(c), async ({ k }) => {
          applyCaseMeta(c);
          await k.account.searchOrders(c.query);
          if (c.expected.length) await k.account.verifyOrderList(c.expected);
          else await k.account.verifyOrdersEmpty(data.noMatchMessage);
        });
      }
    });

    test('[ACC-ORD-S05] Kết hợp tab và tìm kiếm: mã đúng nhưng khác trạng thái -> không có kết quả', async ({ k }) => {
      await k.account.filterOrdersByStatus('Đã giao');
      await k.account.searchOrders(data.cancel.pendingCode);
      await k.account.verifyOrdersEmpty(data.noMatchMessage);
      await k.account.filterOrdersByStatus('Tất cả');
      await k.account.verifyOrderList([data.cancel.pendingCode]);
    });

    test.describe('Thông tin từng đơn: nhãn trạng thái, thanh toán, vận chuyển (data-driven)', () => {
      for (const c of data.labels) {
        test(caseTitle(c), async ({ k }) => {
          applyCaseMeta(c);
          await k.account.verifyOrderStatus(c.code, c.status);
          await k.account.verifyOrderItem(c.code, c.texts);
        });
      }
    });

    test.describe('Nút Hủy đơn theo trạng thái (data-driven)', () => {
      for (const c of data.cancelButtons) {
        test(caseTitle(c), async ({ k }) => {
          applyCaseMeta(c);
          await k.account.verifyOrderCancelable(c.code, c.cancelable);
        });
      }
    });

    test('[ACC-ORD-C01] Hủy đơn chờ xác nhận: gửi lý do mặc định, đổi trạng thái và thống kê @smoke', async ({ k }) => {
      const c = data.cancel;
      await k.common.mockWrite('POST', API.cancelOrder, c.response);
      await k.account.cancelOrderFromList(c.pendingCode);
      await k.common.verifyRequest('POST', `/api/orders/${c.pendingId}/cancel`, { reason: c.reason });
      await k.account.verifyOrderStatus(c.pendingCode, 'Đã hủy');
      await k.account.verifyOrderCancelable(c.pendingCode, false);
      await k.account.verifyOrderStats(c.statsAfter);
    });

    test('[ACC-ORD-C02] Hủy đơn thất bại hiển thị thông báo lỗi cho khách', async ({ k }) => {
      test.fail(
        true,
        'BUG: OrdersPage.jsx:87-88 - lỗi POST /orders/:id/cancel chỉ gọi lại fetchOrders(), không hiển thị thông báo -> khách không biết vì sao hủy không được',
      );
      const c = data.cancel;
      await k.common.mockWrite('POST', API.cancelOrder, c.errorResponse, c.errorStatus);
      await k.account.cancelOrderFromList(c.pendingCode);
      await k.common.verifyRequest('POST', `/api/orders/${c.pendingId}/cancel`);
      await k.account.verifyOrderStatus(c.pendingCode, 'Chờ xác nhận');
      await k.common.verifyTextVisible(String(c.errorResponse.message));
    });

    test('[ACC-ORD-D01] Xem chi tiết từ danh sách mở đúng trang chi tiết đơn', async ({ k }) => {
      await k.common.mockGet(API.orderDetail, detail.pending);
      await k.account.openOrderFromList(data.cancel.pendingCode);
      await k.common.verifyUrl(`/orders/${data.cancel.pendingId}`);
      await k.account.verifyOrderDetailHeading(detail.pendingView.heading);
    });

    test('[ACC-ORD-N01] Sidebar: chuyển sang Yêu thích rồi Hồ sơ (điều hướng trong app)', async ({ k }) => {
      await k.account.clickSidebarLink('Yêu thích');
      await k.common.verifyUrl('/favorites');
      await k.account.verifyWishlistLoaded();
      await k.account.clickSidebarLink('Hồ sơ cá nhân');
      await k.common.verifyUrl('/profile');
      await k.account.verifyProfileLoaded();
    });

    test('[ACC-ORD-N02] Đăng xuất từ sidebar về trang chủ và xóa token', async ({ k }) => {
      await k.account.logoutFromSidebar();
      await k.auth.verifyLoggedOut();
    });
  });
});
