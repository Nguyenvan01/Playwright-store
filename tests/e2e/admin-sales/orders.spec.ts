import { test } from '@fixtures';
import { AUTH_FILES } from '@config/env';
import { loadData } from '@data/loader';
import type { OrdersData } from '@data/admin-sales.types';
import { applyCaseMeta, caseTitle } from '@engine/cases';
import { hasAdminAuth } from '@utils/storage';

/**
 * Production không có đơn hàng nào -> mọi dữ liệu đơn đều mock (GET) qua adminSales.mockOrdersApi,
 * mọi thao tác ghi (đổi trạng thái, thanh toán, hủy) đều mock bằng common.mockWrite trước khi bấm.
 */
const data = loadData<OrdersData>('admin-sales/orders.json');

test.describe('Admin - Đơn hàng', () => {
  test.use({ storageState: AUTH_FILES.admin });
  test.skip(() => !hasAdminAuth(), 'Cần E2E_ADMIN_EMAIL/PASSWORD trong .env');

  test('[ADS-ORD-01] Không có đơn -> "Không có đơn hàng nào"', async ({ k }) => {
    await k.adminSales.mockOrdersApi({ orders: [], stats: {} });
    await k.admin.openAdminPage('/admin/orders', 'Đơn hàng');
    await k.adminSales.verifyOrdersEmpty();
  });

  test.describe('Danh sách & bộ lọc (mock dữ liệu)', () => {
    test.beforeEach(async ({ k }) => {
      await k.adminSales.mockOrdersApi(data.fixture);
      await k.admin.openAdminPage('/admin/orders', 'Đơn hàng');
    });

    test('[ADS-ORD-02] Bảng đơn hàng: đủ cột, thẻ trạng thái và dữ liệu dòng @smoke', async ({ k }) => {
      await k.adminSales.verifyColumns(data.headers);
      await k.adminSales.verifyOrderStatusCards(data.statusCards);
      await k.adminSales.verifyOrderRows(data.fixture.orders.map((o) => o.order_number));
      await k.adminSales.verifyOrderRow(data.row);
    });

    for (const c of data.filters) {
      test(caseTitle(c), async ({ k }) => {
        applyCaseMeta(c);
        if (c.search) await k.adminSales.searchOrders(c.search);
        if (c.status) await k.adminSales.filterOrdersByStatus(c.status);
        if (c.payment) await k.adminSales.filterOrdersByPayment(c.payment);
        if (c.card) {
          await k.adminSales.clickOrderStatusCard(c.card);
          await k.adminSales.verifyOrderStatusCardActive(c.card, true);
        }
        if (c.dateFrom && c.dateTo) await k.adminSales.filterOrdersByDate(c.dateFrom, c.dateTo);
        await k.adminSales.verifyApiRequested('/admin/orders', c.request);
        if (c.rows) await k.adminSales.verifyOrderRows(c.rows);
        if (c.selectValue) await k.adminSales.verifyOrderFilters({ status: c.selectValue });
      });
    }

    test('[ADS-ORD-03] Bấm lại thẻ trạng thái đang chọn -> bỏ lọc', async ({ k }) => {
      await k.adminSales.clickOrderStatusCard('Đã giao');
      await k.adminSales.verifyOrderRows(['E2E-0005']);
      await k.adminSales.clickOrderStatusCard('Đã giao');
      await k.adminSales.verifyOrderStatusCardActive('Đã giao', false);
      await k.adminSales.verifyOrderFilters({ status: '' });
      await k.adminSales.verifyOrderRows(data.fixture.orders.map((o) => o.order_number));
    });

    test('[ADS-ORD-04] "Xóa bộ lọc" đưa mọi bộ lọc về mặc định', async ({ k }) => {
      await k.adminSales.searchOrders('E2E-000');
      await k.adminSales.filterOrdersByStatus('pending');
      await k.adminSales.filterOrdersByPayment('unpaid');
      await k.adminSales.verifyOrderRows(['E2E-0001', 'E2E-0008']);
      await k.adminSales.clearOrderFilters();
      await k.adminSales.verifyOrderFilters({ search: '', status: '', payment: '' });
      await k.adminSales.verifyOrderRows(data.fixture.orders.map((o) => o.order_number));
    });

    test.describe('Nút "Hủy đơn" trên dòng theo trạng thái (data-driven)', () => {
      for (const c of data.cancelAction) {
        test(caseTitle(c), async ({ k }) => {
          applyCaseMeta(c);
          await k.adminSales.verifyOrderCancelAction(c.order, c.visible);
        });
      }
    });
  });

  test.describe('Chi tiết đơn hàng', () => {
    test.beforeEach(async ({ k }) => {
      await k.adminSales.mockOrdersApi(data.fixture);
      await k.admin.openAdminPage('/admin/orders', 'Đơn hàng');
    });

    test('[ADS-ORD-05] Modal chi tiết hiển thị đủ người nhận, địa chỉ, sản phẩm, tổng tiền, lịch sử', async ({ k }) => {
      await k.adminSales.openOrderDetail(data.detail.number);
      await k.adminSales.verifyApiRequested(`/admin/orders/${data.fixture.orders[2].id}`);
      await k.adminSales.verifyOrderDetail(data.detail);
      await k.adminSales.closeOrderDetail();
    });

    test.describe('Chuyển trạng thái đơn (data-driven, mock PUT)', () => {
      for (const c of data.transitions) {
        test(caseTitle(c), async ({ k }) => {
          applyCaseMeta(c);
          await k.common.mockWrite('PUT', `**/api/admin/orders/${c.orderId}/status`, { success: true, status: c.status });
          await k.adminSales.openOrderDetail(c.order);
          await k.adminSales.verifyOrderStatusButtons(c.buttons);
          await k.adminSales.verifyOrderProcessingWarning(!!c.warning);
          if (!c.click) {
            await k.common.verifyNoRequest('PUT', `/admin/orders/${c.orderId}/status`);
            return;
          }
          await k.adminSales.clickOrderStatusButton(c.click);
          await k.common.verifyRequest('PUT', `/admin/orders/${c.orderId}/status`, { status: c.status });
          await k.common.verifyToast(`Đã cập nhật trạng thái: ${c.label}`);
          await k.adminSales.verifyOrderDetailStatus(c.label!);
          await k.adminSales.verifyOrderRowStatus(c.order, c.label!);
        });
      }
    });

    test('[ADS-ORD-06] API đổi trạng thái lỗi -> báo lỗi server, giữ trạng thái cũ', async ({ k }) => {
      const msg = 'Không thể chuyển từ trạng thái "pending" sang "confirmed"';
      await k.common.mockWrite('PUT', '**/api/admin/orders/9001/status', { success: false, message: msg }, 400);
      await k.adminSales.openOrderDetail('E2E-0001');
      await k.adminSales.clickOrderStatusButton('Xác nhận');
      await k.common.verifyRequest('PUT', '/admin/orders/9001/status', { status: 'confirmed' });
      await k.common.verifyToast(msg);
      await k.adminSales.verifyOrderDetailStatus('Chờ xác nhận');
      await k.adminSales.verifyOrderRowStatus('E2E-0001', 'Chờ xác nhận');
    });

    test('[ADS-ORD-07] Cập nhật thanh toán "Đã thanh toán" (mock PUT)', async ({ k }) => {
      const p = data.payment;
      await k.common.mockWrite('PUT', `**/api/admin/orders/${p.orderId}/payment`, { success: true, payment_status: p.value });
      await k.adminSales.openOrderDetail(p.order);
      await k.adminSales.verifyOrderDetailPayment('Chưa thanh toán', true);
      await k.adminSales.changeOrderPayment(p.value);
      await k.common.verifyRequest('PUT', `/admin/orders/${p.orderId}/payment`, { payment_status: p.value });
      await k.common.verifyToast(p.toast);
      await k.adminSales.verifyOrderDetailPayment(p.label, false);
    });

    test('[ADS-ORD-08] Đơn đã thanh toán không hiện khối "Cập nhật thanh toán"', async ({ k }) => {
      await k.adminSales.openOrderDetail('E2E-0002');
      await k.adminSales.verifyOrderDetailPayment('Đã thanh toán', false);
    });

    test('[ADS-ORD-09] Thông báo "Đơn xác nhận" xuất hiện trong chuông sau khi xác nhận đơn', async ({ page, k }) => {
      test.fail(
        true,
        'BUG: AdminOrders.jsx:160-168 pushNotification() rồi gọi ngay fetchNotifications(true) -> NotificationContext.jsx:55 ghi đè bằng danh sách từ server nên thông báo vừa đẩy biến mất',
      );
      const n = data.pushNotification;
      const isNotifFetch = (r: { url(): string }) => r.url().includes('/api/admin/notifications');
      await k.common.mockWrite('PUT', `**/api/admin/orders/${n.orderId}/status`, { success: true });
      await k.adminSales.openOrderDetail(n.order);
      // Đợi lần làm mới thông báo do app tự gọi sau khi đổi trạng thái -> kết quả không phụ thuộc thời điểm
      const refreshed = page.waitForResponse(isNotifFetch);
      await k.adminSales.clickOrderStatusButton(n.click);
      await k.common.verifyToast('Đã cập nhật trạng thái: Đã xác nhận');
      await refreshed;
      await k.adminSales.closeOrderDetail();
      const panelFetch = page.waitForResponse(isNotifFetch);
      await k.adminSales.openNotifications();
      await panelFetch;
      await k.adminSales.verifyNotificationVisible(n.title);
    });
  });

  test.describe('Hủy đơn từ bảng (mock POST /cancel)', () => {
    test.beforeEach(async ({ k }) => {
      await k.adminSales.mockOrdersApi(data.fixture);
      await k.admin.openAdminPage('/admin/orders', 'Đơn hàng');
    });

    test('[ADS-ORD-10] Hủy đơn đã thanh toán có lý do -> gửi lý do, báo hoàn tiền, đơn thành "Đã hủy" @smoke', async ({ k }) => {
      const c = data.cancel;
      await k.common.mockWrite('POST', `**/api/admin/orders/${c.orderId}/cancel`, { success: true });
      await k.adminSales.openCancelOrder(c.order);
      await k.adminSales.verifyCancelNotes([c.refundNote]);
      await k.adminSales.fillCancelReason(c.reason);
      await k.admin.clickButton('Xác nhận hủy');
      await k.common.verifyRequest('POST', `/admin/orders/${c.orderId}/cancel`, { reason: c.reason });
      await k.common.verifyToast(c.toast);
      await k.admin.verifyModalClosed('Hủy đơn hàng');
      await k.adminSales.verifyOrderRowStatus(c.order, 'Đã hủy');
      await k.adminSales.verifyOrderCancelAction(c.order, false);
    });

    test('[ADS-ORD-11] "Đóng" modal hủy -> không gửi request, đơn giữ nguyên', async ({ k }) => {
      const c = data.cancel;
      await k.common.mockWrite('POST', `**/api/admin/orders/${c.orderId}/cancel`, { success: true });
      await k.adminSales.openCancelOrder(c.order);
      await k.adminSales.fillCancelReason(c.reason);
      await k.admin.clickButton('Đóng');
      await k.admin.verifyModalClosed('Hủy đơn hàng');
      await k.common.verifyNoRequest('POST', `/admin/orders/${c.orderId}/cancel`);
      await k.adminSales.verifyOrderRowStatus(c.order, 'Đã xác nhận');
    });

    test('[ADS-ORD-12] Server từ chối hủy -> báo lỗi, modal vẫn mở', async ({ k }) => {
      const c = data.cancel;
      await k.common.mockWrite('POST', `**/api/admin/orders/${c.orderId}/cancel`, { success: false, message: c.error.message }, c.error.status);
      await k.adminSales.openCancelOrder(c.order);
      await k.admin.clickButton('Xác nhận hủy');
      await k.common.verifyRequest('POST', `/admin/orders/${c.orderId}/cancel`, { reason: '' });
      await k.common.verifyToast(c.error.message);
      await k.admin.verifyModalOpen('Hủy đơn hàng');
      await k.adminSales.verifyOrderRowStatus(c.order, 'Đã xác nhận');
    });

    test('[ADS-ORD-13] Đơn dùng điểm -> modal hủy báo hoàn điểm tích lũy', async ({ k }) => {
      test.fail(
        true,
        'BUG: AdminOrders.jsx:700 kiểm tra order.points_used nhưng API danh sách (adminController.getOrders) chỉ trả points_discount -> không bao giờ báo hoàn điểm',
      );
      await k.adminSales.openCancelOrder(data.cancel.pointsOrder);
      await k.adminSales.verifyCancelNotes([data.cancel.pointsNote]);
    });
  });

  test.describe('Phân trang', () => {
    test('[ADS-ORD-14] Nhiều trang -> hiển thị "Trang 1 / 3 — 45 đơn hàng"', async ({ k }) => {
      await k.adminSales.mockOrdersApi({ ...data.fixture, total: data.pagination.total });
      await k.admin.openAdminPage('/admin/orders', 'Đơn hàng');
      await k.adminSales.verifyPaginationText(data.pagination.text);
      await k.adminSales.verifyPageButton(3);
    });

    test('[ADS-ORD-15] Bấm trang 2 tải dữ liệu trang 2', async ({ k }) => {
      test.fail(true, 'BUG: AdminOrders.jsx:125-130 useEffect tải đơn chỉ phụ thuộc [filters], đổi trang không gọi lại API');
      await k.adminSales.mockOrdersApi({ ...data.fixture, total: data.pagination.total });
      await k.admin.openAdminPage('/admin/orders', 'Đơn hàng');
      await k.adminSales.verifyPaginationText(data.pagination.text);
      await k.adminSales.goToPage(data.pagination.page);
      await k.adminSales.verifyApiRequested('/admin/orders', { page: data.pagination.page });
    });
  });
});
