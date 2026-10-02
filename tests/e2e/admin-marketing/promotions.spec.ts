import { test } from '@fixtures';
import { AUTH_FILES } from '@config/env';
import { loadData } from '@data/loader';
import type { PromotionsData } from '@data/admin-marketing.types';
import { applyCaseMeta, caseTitle } from '@engine/cases';
import { hasAdminAuth } from '@utils/storage';

const d = loadData<PromotionsData>('admin-marketing/promotions.json');
const SEARCH = 'Tìm theo tên, mô tả hoặc trạng thái';
const LIST_API = '**/api/admin/promotions';
const CREATE = 'Thêm khuyến mãi';
const EDIT = 'Sửa khuyến mãi';

test.describe('Quản trị - Khuyến mãi', () => {
  test.use({ storageState: AUTH_FILES.admin });
  test.skip(() => !hasAdminAuth(), 'Cần E2E_ADMIN_EMAIL/PASSWORD trong .env');

  test('[ADM-PRO-01] Dữ liệu thật: đủ cột và có ít nhất 1 khuyến mãi @smoke', async ({ k }) => {
    await k.adminMarketing.openPromotions();
    await k.adminMarketing.verifyColumns(d.headers);
    await k.adminMarketing.verifyRowsAtLeast(1);
    await k.common.verifyNoPageErrors();
  });

  test('[ADM-PRO-02] Danh sách rỗng hiển thị "Chưa có khuyến mãi nào"', async ({ k }) => {
    await k.adminMarketing.mockPromotionList([]);
    await k.adminMarketing.openPromotions();
    await k.common.verifyTextVisible('Chưa có khuyến mãi nào');
  });

  test('[ADM-PRO-03] API lỗi hiển thị "Không thể tải danh sách khuyến mãi."', async ({ k }) => {
    await k.common.mockGet(LIST_API, { success: false, message: 'Lỗi' }, 500);
    await k.adminMarketing.openPromotions();
    await k.common.verifyTextVisible('Không thể tải danh sách khuyến mãi.');
  });

  test.describe('Trạng thái tính theo ngày (data-driven)', () => {
    for (const c of d.statusCases) {
      test(caseTitle(c), async ({ k }) => {
        applyCaseMeta(c);
        await k.adminMarketing.mockPromotionList([c.promotion]);
        await k.adminMarketing.openPromotions();
        await k.adminMarketing.verifyRowCells(c.promotion.title, c.expected);
      });
    }
  });

  test.describe('Tìm kiếm (data-driven)', () => {
    for (const c of d.search) {
      test(caseTitle(c), async ({ k }) => {
        applyCaseMeta(c);
        await k.adminMarketing.mockPromotionList(d.list);
        await k.adminMarketing.openPromotions();
        await k.admin.searchList(SEARCH, c.keyword);
        await k.adminMarketing.verifyVisibleRows(c.visible, c.hidden);
        if (c.emptyText) await k.common.verifyTextVisible(c.emptyText);
      });
    }
  });

  test.describe('Form thêm - kiểm tra dữ liệu (data-driven)', () => {
    for (const c of d.validation) {
      test(caseTitle(c), async ({ k }) => {
        applyCaseMeta(c);
        await k.common.mockWrite('POST', LIST_API, { success: true });
        await k.adminMarketing.mockPromotionList(d.list);
        await k.adminMarketing.openPromotions();
        await k.adminMarketing.openCreatePromotion();
        await k.admin.fillForm(c.form);
        await k.adminMarketing.clickModalButton(CREATE, 'Tạo mới');
        await k.common.verifyToast(c.toast);
        await k.admin.verifyModalOpen(CREATE);
        await k.common.verifyNoRequest('POST', '/admin/promotions');
      });
    }

    test(caseTitle(d.invalidImage), async ({ k }) => {
      applyCaseMeta(d.invalidImage);
      await k.common.mockWrite('POST', LIST_API, { success: true });
      await k.adminMarketing.mockPromotionList(d.list);
      await k.adminMarketing.openPromotions();
      await k.adminMarketing.openCreatePromotion();
      await k.admin.fillForm(d.invalidImage.form);
      await k.adminMarketing.clickModalButton(CREATE, 'Tạo mới');
      await k.admin.verifyModalOpen(CREATE);
      await k.common.verifyNoRequest('POST', '/admin/promotions');
    });
  });

  test.describe('Slug tự sinh (data-driven)', () => {
    for (const c of d.slugCases) {
      test(caseTitle(c), async ({ k }) => {
        applyCaseMeta(c);
        await k.adminMarketing.mockPromotionList(d.list);
        await k.adminMarketing.openPromotions();
        await k.adminMarketing.openCreatePromotion();
        for (const step of c.steps) await k.admin.fillForm(step);
        await k.admin.verifyFieldValue('Slug', c.expectedSlug);
      });
    }
  });

  test('[ADM-PRO-04] Thêm khuyến mãi thành công gửi đúng dữ liệu (mock POST) @smoke', async ({ k }) => {
    await k.common.mockWrite('POST', LIST_API, { success: true, promotion: { id: 99, ...d.create.expectedPayload } });
    await k.adminMarketing.mockPromotionList(d.list);
    await k.adminMarketing.openPromotions();
    await k.adminMarketing.openCreatePromotion();
    await k.admin.fillForm(d.create.form);
    await k.adminMarketing.clickModalButton(CREATE, 'Tạo mới');
    await k.common.verifyRequest('POST', '/admin/promotions', d.create.expectedPayload);
    await k.common.verifyToast(d.create.toast);
    await k.admin.verifyModalClosed(CREATE);
  });

  test(caseTitle(d.saveError), async ({ k }) => {
    applyCaseMeta(d.saveError);
    await k.common.mockWrite('POST', LIST_API, { success: false, message: d.saveError.message }, d.saveError.status);
    await k.adminMarketing.mockPromotionList(d.list);
    await k.adminMarketing.openPromotions();
    await k.adminMarketing.openCreatePromotion();
    await k.admin.fillForm(d.saveError.form);
    await k.adminMarketing.clickModalButton(CREATE, 'Tạo mới');
    await k.common.verifyRequest('POST', '/admin/promotions');
    await k.common.verifyToast(d.saveError.message);
  });

  test('[ADM-PRO-05] Sửa: form điền sẵn dữ liệu và gửi PUT đúng (mock)', async ({ k }) => {
    await k.common.mockWrite('PUT', `${LIST_API}/*`, { success: true });
    await k.adminMarketing.mockPromotionList(d.list);
    await k.adminMarketing.openPromotions();
    await k.admin.clickRowAction(d.edit.title, 'Sửa');
    await k.admin.verifyModalOpen(EDIT);
    for (const [label, value] of Object.entries(d.edit.prefilled)) await k.admin.verifyFieldValue(label, value);
    await k.admin.fillForm(d.edit.form);
    await k.adminMarketing.clickModalButton(EDIT, 'Cập nhật');
    await k.common.verifyRequest('PUT', '/admin/promotions/3', d.edit.expectedPayload);
    await k.common.verifyToast(d.edit.toast);
    await k.admin.verifyModalClosed(EDIT);
  });

  test('[ADM-PRO-06] Xem chi tiết rồi bấm "Sửa" mở form sửa', async ({ k }) => {
    await k.adminMarketing.mockPromotionList(d.list);
    await k.adminMarketing.openPromotions();
    await k.admin.clickRowAction(d.view.title, 'Xem');
    await k.adminMarketing.verifyModalText(d.view.title, d.view.texts);
    await k.adminMarketing.clickModalButton(d.view.title, 'Sửa');
    await k.admin.verifyModalOpen(EDIT);
    await k.admin.verifyFieldValue('Tên khuyến mãi', d.view.title);
  });

  test('[ADM-PRO-07] Xóa: bấm "Hủy" đóng hộp xác nhận, không gửi DELETE', async ({ k }) => {
    await k.common.mockWrite('DELETE', `${LIST_API}/*`, { success: true });
    await k.adminMarketing.mockPromotionList(d.list);
    await k.adminMarketing.openPromotions();
    await k.admin.clickRowAction(d.remove.title, 'Xóa');
    await k.adminMarketing.verifyModalText('Xác nhận xóa', [d.remove.title, 'Bạn có chắc chắn muốn xóa khuyến mãi này không?']);
    await k.adminMarketing.clickModalButton('Xác nhận xóa', 'Hủy');
    await k.admin.verifyModalClosed('Xác nhận xóa');
    await k.common.verifyNoRequest('DELETE', '/admin/promotions');
  });

  test('[ADM-PRO-08] Xóa: xác nhận gửi DELETE đúng id và báo thành công (mock)', async ({ k }) => {
    await k.common.mockWrite('DELETE', `${LIST_API}/*`, { success: true });
    await k.adminMarketing.mockPromotionList(d.list);
    await k.adminMarketing.openPromotions();
    await k.admin.clickRowAction(d.remove.title, 'Xóa');
    await k.adminMarketing.clickModalButton('Xác nhận xóa', 'Xóa');
    await k.common.verifyRequest('DELETE', '/admin/promotions/2');
    await k.common.verifyToast(d.remove.toast);
  });

  test('[ADM-PRO-09] Đóng form bằng nút "Đóng" rồi mở lại -> form trống', async ({ k }) => {
    await k.adminMarketing.mockPromotionList(d.list);
    await k.adminMarketing.openPromotions();
    await k.adminMarketing.openCreatePromotion();
    await k.admin.fillForm({ 'Tên khuyến mãi': 'Nháp sẽ bị bỏ' });
    await k.adminMarketing.clickModalButton(CREATE, 'Đóng');
    await k.admin.verifyModalClosed(CREATE);
    await k.adminMarketing.openCreatePromotion();
    await k.admin.verifyFieldValue('Tên khuyến mãi', '');
    await k.admin.verifyFieldValue('Slug', '');
  });
});
