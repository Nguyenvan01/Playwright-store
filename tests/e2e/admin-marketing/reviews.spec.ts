import { test } from '@fixtures';
import { AUTH_FILES } from '@config/env';
import { loadData } from '@data/loader';
import type { ReviewsData } from '@data/admin-marketing.types';
import { applyCaseMeta, caseTitle } from '@engine/cases';
import { hasAdminAuth } from '@utils/storage';

const d = loadData<ReviewsData>('admin-marketing/reviews.json');
const SEARCH = 'Tìm khách hàng, sản phẩm, nội dung...';
const ITEM_API = '**/api/admin/reviews/*';
const STATUS_API = '**/api/admin/reviews/*/status';
const names = d.list.map((r) => r.user_name);

test.describe('Quản trị - Đánh giá', () => {
  test.use({ storageState: AUTH_FILES.admin });
  test.skip(() => !hasAdminAuth(), 'Cần E2E_ADMIN_EMAIL/PASSWORD trong .env');

  test('[ADM-REV-01] Dữ liệu thật: trang tải được, đủ cột @smoke', async ({ k }) => {
    await k.adminMarketing.openReviews();
    await k.adminMarketing.verifyColumns(d.headers);
    await k.common.verifyNoPageErrors();
  });

  test('[ADM-REV-02] Chưa có đánh giá -> trạng thái rỗng', async ({ k }) => {
    await k.adminMarketing.mockReviewList([]);
    await k.adminMarketing.openReviews();
    await k.common.verifyTextVisible('Chưa có đánh giá nào');
    await k.common.verifyTextVisible('Đánh giá mới của khách hàng sẽ hiển thị tại đây.');
  });

  test('[ADM-REV-03] API lỗi -> toast "Không thể tải danh sách đánh giá."', async ({ k }) => {
    await k.common.mockGet('**/api/admin/reviews*', { success: false }, 500);
    await k.adminMarketing.openReviews();
    await k.common.verifyToast('Không thể tải danh sách đánh giá.');
  });

  test.describe('Hiển thị dòng + nút theo trạng thái (data-driven)', () => {
    for (const c of d.rows) {
      test(caseTitle(c), async ({ k }) => {
        applyCaseMeta(c);
        await k.adminMarketing.mockReviewList(d.list);
        await k.adminMarketing.openReviews();
        await k.adminMarketing.verifyRowCount(d.list.length);
        await k.adminMarketing.verifyRowCells(c.rowText, c.expected);
        await k.adminMarketing.verifyRowActions(c.rowText, c.actions);
      });
    }
  });

  test.describe('Tìm kiếm (data-driven)', () => {
    for (const c of d.search) {
      test(caseTitle(c), async ({ k }) => {
        applyCaseMeta(c);
        await k.adminMarketing.mockReviewList(d.list);
        await k.adminMarketing.openReviews();
        await k.admin.searchList(SEARCH, c.keyword);
        await k.adminMarketing.verifyVisibleRows(c.visible, c.hidden);
        if (c.emptyText) await k.common.verifyTextVisible(c.emptyText);
      });
    }
  });

  test.describe('Lọc trạng thái / số sao (data-driven)', () => {
    for (const c of d.filters) {
      test(caseTitle(c), async ({ k }) => {
        applyCaseMeta(c);
        await k.adminMarketing.mockReviewList(d.list);
        await k.adminMarketing.openReviews();
        if (c.status !== 'all') await k.adminMarketing.filterReviewStatus(c.status);
        if (c.rating !== 'all') await k.adminMarketing.filterReviewRating(c.rating);
        await k.adminMarketing.verifyListQuery('/admin/reviews', c.query);
        await k.adminMarketing.verifyVisibleRows(c.visible, names.filter((n) => !c.visible.includes(n)));
        if (c.emptyText) await k.common.verifyTextVisible(c.emptyText);
      });
    }
  });

  test.describe('Duyệt / Ẩn trên dòng (data-driven)', () => {
    for (const c of d.statusActions) {
      test(caseTitle(c), async ({ k }) => {
        applyCaseMeta(c);
        await k.common.mockWrite('PUT', STATUS_API, { success: true });
        await k.adminMarketing.mockReviewList(d.list);
        await k.adminMarketing.openReviews();
        await k.admin.clickRowAction(c.rowText, c.action);
        await k.common.verifyRequest('PUT', `/admin/reviews/${c.reviewId}/status`, { status: c.status });
        await k.common.verifyToast(c.toast);
        await k.adminMarketing.verifyRowCells(c.rowText, { 'Trạng thái': c.badge });
      });
    }
  });

  test('[ADM-REV-04] Xem chi tiết và duyệt ngay trong modal (mock PUT)', async ({ k }) => {
    await k.common.mockWrite('PUT', STATUS_API, { success: true });
    await k.adminMarketing.mockReviewList(d.list);
    await k.adminMarketing.openReviews();
    await k.admin.clickRowAction(d.detail.rowText, 'Xem');
    await k.adminMarketing.verifyModalText('Chi tiết đánh giá', d.detail.texts);
    await k.adminMarketing.clickModalButton('Chi tiết đánh giá', d.detail.approveButton);
    await k.common.verifyRequest('PUT', '/admin/reviews/1/status', { status: 'approved' });
    await k.common.verifyToast(d.detail.toast);
    await k.adminMarketing.verifyModalText('Chi tiết đánh giá', [d.detail.badge, 'Ẩn đánh giá']);
  });

  test('[ADM-REV-05] Xóa: bấm "Hủy" không gửi DELETE', async ({ k }) => {
    await k.common.mockWrite('DELETE', ITEM_API, { success: true });
    await k.adminMarketing.mockReviewList(d.list);
    await k.adminMarketing.openReviews();
    await k.admin.clickRowAction(d.remove.rowText, 'Xóa');
    await k.adminMarketing.verifyModalText('Xóa đánh giá', ['Bạn có chắc chắn muốn xóa đánh giá này không?']);
    await k.adminMarketing.clickModalButton('Xóa đánh giá', 'Hủy');
    await k.admin.verifyModalClosed('Xóa đánh giá');
    await k.common.verifyNoRequest('DELETE', '/admin/reviews');
  });

  test('[ADM-REV-06] Xóa: xác nhận gửi DELETE và bỏ dòng (mock)', async ({ k }) => {
    await k.common.mockWrite('DELETE', ITEM_API, { success: true });
    await k.adminMarketing.mockReviewList(d.list);
    await k.adminMarketing.openReviews();
    await k.admin.clickRowAction(d.remove.rowText, 'Xóa');
    await k.adminMarketing.clickModalButton('Xóa đánh giá', 'Xóa');
    await k.common.verifyRequest('DELETE', '/admin/reviews/4');
    await k.common.verifyToast(d.remove.toast);
    await k.admin.verifyRow(d.remove.rowText, false);
  });

  test(caseTitle(d.updateError), async ({ k }) => {
    applyCaseMeta(d.updateError);
    await k.common.mockWrite('PUT', STATUS_API, { success: false, message: d.updateError.message }, d.updateError.status);
    await k.adminMarketing.mockReviewList(d.list);
    await k.adminMarketing.openReviews();
    await k.admin.clickRowAction(d.updateError.rowText, 'Duyệt');
    await k.common.verifyToast(d.updateError.message);
    await k.adminMarketing.verifyRowCells(d.updateError.rowText, { 'Trạng thái': 'Chờ duyệt' });
  });
});
