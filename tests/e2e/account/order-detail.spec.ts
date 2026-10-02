import { test } from '@fixtures';
import { AUTH_FILES } from '@config/env';
import { loadData } from '@data/loader';
import type { OrderDetailData, OrderDetailView, OrdersData } from '@data/account.types';
import { applyCaseMeta, caseTitle } from '@engine/cases';
import { hasCustomerAuth } from '@utils/storage';
import type { Keywords } from '@keywords/index';
import { API } from './support';

const data = loadData<OrderDetailData>('account/order-detail.json');
const orders = loadData<OrdersData>('account/orders.json');
const pendingOrder = data.pending.order as Record<string, unknown>;
const pendingId = pendingOrder.id as number;

/** Kiểm tra toàn bộ nội dung trang chi tiết theo dữ liệu mong đợi trong JSON. */
async function verifyDetailView(k: Keywords, view: OrderDetailView) {
  await k.account.verifyOrderDetailHeading(view.heading);
  await k.account.verifyOrderDetailStatus(view.status, view.payment);
  await k.account.verifyOrderDetailInfo('Thông tin đơn hàng', view.orderInfo);
  await k.account.verifyOrderDetailInfo('Thông tin giao hàng', view.shippingInfo);
  await k.account.verifyOrderDetailItems(view.itemsHeading, view.items.map((i) => i.name));
  for (const item of view.items) await k.account.verifyOrderDetailItem(item.name, item.texts);
  await k.account.verifyOrderDetailTotals(view.totals);
}

test.describe('Chi tiết đơn hàng', () => {
  test.use({ storageState: AUTH_FILES.customer });
  test.skip(() => !hasCustomerAuth(), 'Chưa có tài khoản test (xem .env)');

  test('[ACC-ODT-01] Đơn chờ xác nhận: thông tin, sản phẩm, giảm giá, phí giao nhanh @smoke', async ({ k }) => {
    await k.common.mockGet(API.orderDetail, data.pending);
    await k.account.openOrderDetail(pendingId);
    await verifyDetailView(k, data.pendingView);
  });

  test('[ACC-ODT-02] Đơn đã giao: miễn phí vận chuyển, có mã vận đơn, không có dòng giảm giá', async ({ k }) => {
    const order = data.delivered.order as Record<string, unknown>;
    await k.common.mockGet(API.orderDetail, data.delivered);
    await k.account.openOrderDetail(order.id as number);
    await verifyDetailView(k, data.deliveredView);
    await k.account.verifyOrderDetailCancelable(false);
  });

  test('[ACC-ODT-03] Nhãn trạng thái/thanh toán thống nhất với trang danh sách (trả hàng, thanh toán một phần)', async ({ k }) => {
    test.fail(
      true,
      'BUG: OrderDetailPage.jsx:22,28 dùng nhãn "Trả hàng" / "Thanh toán 1 phần", khác accountUtils.js:36,42 của trang danh sách ("Đã trả hàng" / "Thanh toán một phần")',
    );
    const order = data.returned.order as Record<string, unknown>;
    await k.common.mockGet(API.orderDetail, data.returned);
    await k.account.openOrderDetail(order.id as number);
    await k.account.verifyOrderDetailStatus(data.returnedExpected.status, data.returnedExpected.payment);
  });

  test.describe('Nút Hủy đơn hàng theo trạng thái (data-driven)', () => {
    for (const c of data.statuses) {
      test(caseTitle(c), async ({ k }) => {
        applyCaseMeta(c);
        await k.common.mockGet(API.orderDetail, { ...data.pending, order: { ...pendingOrder, status: c.status } });
        await k.account.openOrderDetail(pendingId);
        await k.account.verifyOrderDetailStatus(c.statusLabel, data.pendingView.payment);
        await k.account.verifyOrderDetailCancelable(c.cancelable);
      });
    }
  });

  test.describe('Hủy đơn từ trang chi tiết', () => {
    test.beforeEach(async ({ k }) => {
      await k.common.mockGet(API.orderDetail, data.pending);
      await k.account.openOrderDetail(pendingId);
      await k.account.verifyOrderDetailStatus(data.pendingView.status, data.pendingView.payment);
    });

    test('[ACC-ODT-04] Hủy có lý do: gửi lý do, đóng hộp thoại, trạng thái thành Đã hủy', async ({ k }) => {
      await k.common.mockWrite('POST', API.cancelOrder, data.cancel.response);
      await k.account.openCancelOrderDialog();
      await k.account.confirmCancelOrder(data.cancel.reason);
      await k.common.verifyRequest('POST', `/api/orders/${pendingId}/cancel`, { reason: data.cancel.reason });
      await k.account.verifyCancelOrderDialog(false);
      await k.account.verifyOrderDetailStatus('Đã hủy', data.pendingView.payment);
      await k.account.verifyOrderDetailCancelable(false);
    });

    test('[ACC-ODT-05] Hủy không nhập lý do: gửi reason rỗng', async ({ k }) => {
      await k.common.mockWrite('POST', API.cancelOrder, data.cancel.response);
      await k.account.openCancelOrderDialog();
      await k.account.confirmCancelOrder();
      await k.common.verifyRequest('POST', `/api/orders/${pendingId}/cancel`, { reason: '' });
      await k.account.verifyOrderDetailStatus('Đã hủy', data.pendingView.payment);
    });

    test('[ACC-ODT-06] Đóng hộp xác nhận: không gửi request, đơn giữ nguyên', async ({ k }) => {
      await k.common.mockWrite('POST', API.cancelOrder, data.cancel.response);
      await k.account.openCancelOrderDialog();
      await k.account.closeCancelOrderDialog();
      await k.account.verifyCancelOrderDialog(false);
      await k.common.verifyNoRequest('POST', '/cancel');
      await k.account.verifyOrderDetailStatus(data.pendingView.status, data.pendingView.payment);
      await k.account.verifyOrderDetailCancelable(true);
    });

    test('[ACC-ODT-07] Hủy thất bại hiển thị thông báo lỗi từ server', async ({ k }) => {
      test.fail(true, 'BUG: OrderDetailPage.jsx:156 - catch {} nuốt lỗi hủy đơn, hộp thoại vẫn mở và không có thông báo nào');
      await k.common.mockWrite('POST', API.cancelOrder, data.cancel.errorResponse, data.cancel.errorStatus);
      await k.account.openCancelOrderDialog();
      await k.account.confirmCancelOrder(data.cancel.reason);
      await k.common.verifyRequest('POST', `/api/orders/${pendingId}/cancel`);
      await k.common.verifyTextVisible(String(data.cancel.errorResponse.message));
    });
  });

  test.describe('Lỗi tải đơn hàng (mock, data-driven)', () => {
    for (const c of data.errors) {
      test(caseTitle(c), async ({ k }) => {
        applyCaseMeta(c);
        await k.common.mockGet(API.orderDetail, c.response, c.status);
        await k.account.openOrderDetail(999999);
        await k.account.verifyOrderDetailError(c.message);
      });
    }
  });

  test('[ACC-ODT-08] Màn hình lỗi: nút Quay lại đơn hàng về /orders', async ({ k }) => {
    await k.common.mockGet(API.orderDetail, data.errors[1].response, data.errors[1].status);
    await k.common.mockGet(API.orders, orders.list);
    await k.account.openOrderDetail(999999);
    await k.account.backToOrdersFromError();
    await k.account.verifyOrderList(orders.allCodes);
  });

  test('[ACC-ODT-09] Nút Quay lại ở đầu trang chi tiết về danh sách đơn', async ({ k }) => {
    await k.common.mockGet(API.orderDetail, data.pending);
    await k.common.mockGet(API.orders, orders.list);
    await k.account.openOrderDetail(pendingId);
    await k.account.verifyOrderDetailHeading(data.pendingView.heading);
    await k.account.goBackFromOrderDetail();
    await k.account.verifyOrdersLoaded();
  });
});
