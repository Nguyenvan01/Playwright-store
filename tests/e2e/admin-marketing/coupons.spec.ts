import { test } from '@fixtures';
import { AUTH_FILES } from '@config/env';
import { loadData } from '@data/loader';
import type { CouponsData } from '@data/admin-marketing.types';
import { applyCaseMeta, caseTitle } from '@engine/cases';
import { hasAdminAuth } from '@utils/storage';

const d = loadData<CouponsData>('admin-marketing/coupons.json');
const LIST_API = '**/api/admin/coupons';
const CREATE = 'Thêm mã giảm giá';
const EDIT = 'Sửa mã giảm giá';

test.describe('Quản trị - Mã giảm giá', () => {
  test.use({ storageState: AUTH_FILES.admin });
  test.skip(() => !hasAdminAuth(), 'Cần E2E_ADMIN_EMAIL/PASSWORD trong .env');

  test('[ADM-CPN-01] Dữ liệu thật: đủ cột và có ít nhất 1 mã @smoke', async ({ k }) => {
    await k.adminMarketing.openCoupons();
    await k.adminMarketing.verifyColumns(d.headers);
    await k.adminMarketing.verifyRowsAtLeast(1);
    await k.common.verifyNoPageErrors();
  });

  test.describe('Dữ liệu thật - định dạng cột', () => {
    for (const c of d.realDataChecks) {
      test(caseTitle(c), async ({ k }) => {
        applyCaseMeta(c);
        await k.adminMarketing.openCoupons();
        await k.adminMarketing.verifyCellPattern(0, c.column, c.pattern);
      });
    }
  });

  test('[ADM-CPN-02] Danh sách rỗng hiển thị "Chưa có mã giảm giá nào"', async ({ k }) => {
    await k.adminMarketing.mockCouponList([]);
    await k.adminMarketing.openCoupons();
    await k.common.verifyTextVisible('Chưa có mã giảm giá nào');
  });

  test.describe('Hiển thị dòng (data-driven)', () => {
    for (const c of d.display) {
      test(caseTitle(c), async ({ k }) => {
        applyCaseMeta(c);
        await k.adminMarketing.mockCouponList(d.list);
        await k.adminMarketing.openCoupons();
        await k.adminMarketing.verifyRowCount(d.list.length);
        await k.adminMarketing.verifyRowCells(c.code, c.expected);
      });
    }
  });

  test.describe('Trường bắt buộc (data-driven)', () => {
    for (const c of d.required) {
      test(caseTitle(c), async ({ k }) => {
        applyCaseMeta(c);
        await k.common.mockWrite('POST', LIST_API, { success: true });
        await k.adminMarketing.mockCouponList(d.list);
        await k.adminMarketing.openCoupons();
        await k.adminMarketing.openCreateCoupon();
        await k.admin.fillForm(c.form);
        await k.adminMarketing.clickModalButton(CREATE, 'Tạo mới');
        await k.admin.verifyModalOpen(CREATE);
        await k.common.verifyNoRequest('POST', '/admin/coupons');
      });
    }
  });

  test('[ADM-CPN-03] Mã tự viết hoa khi nhập', async ({ k }) => {
    await k.adminMarketing.mockCouponList(d.list);
    await k.adminMarketing.openCoupons();
    await k.adminMarketing.openCreateCoupon();
    await k.admin.fillForm({ 'Mã': d.create.typedCode });
    await k.admin.verifyFieldValue('Mã', d.create.expectedCode);
  });

  test('[ADM-CPN-04] Thêm mã thành công gửi đúng dữ liệu và thêm dòng mới (mock POST) @smoke', async ({ k }) => {
    const created = { id: 99, code: d.create.expectedCode, name: 'Giảm 10% E2E', discount_type: 'percentage', discount_value: 10, used_count: 0, max_usage_total: 100, is_active: true, is_public: true };
    await k.common.mockWrite('POST', LIST_API, { success: true, coupon: created });
    await k.adminMarketing.mockCouponList(d.list);
    await k.adminMarketing.openCoupons();
    await k.adminMarketing.openCreateCoupon();
    await k.admin.fillForm({ 'Mã': d.create.typedCode, ...d.create.form });
    await k.adminMarketing.clickModalButton(CREATE, 'Tạo mới');
    await k.common.verifyRequest('POST', '/admin/coupons', d.create.expectedPayload);
    await k.common.verifyToast(d.create.toast);
    await k.admin.verifyModalClosed(CREATE);
    await k.adminMarketing.verifyRowCells(d.create.expectedCode, { 'Tên': 'Giảm 10% E2E', 'Giảm': '10%', 'Sử dụng': '0 / 100' });
  });

  test(caseTitle(d.saveError), async ({ k }) => {
    applyCaseMeta(d.saveError);
    await k.common.mockWrite('POST', LIST_API, { success: false, message: d.saveError.message }, d.saveError.status);
    await k.adminMarketing.mockCouponList(d.list);
    await k.adminMarketing.openCoupons();
    await k.adminMarketing.openCreateCoupon();
    await k.admin.fillForm(d.saveError.form);
    await k.adminMarketing.clickModalButton(CREATE, 'Tạo mới');
    await k.common.verifyRequest('POST', '/admin/coupons');
    await k.common.verifyToast(d.saveError.message);
  });

  test('[ADM-CPN-05] Sửa: form điền sẵn, gửi PUT đúng và cập nhật dòng (mock)', async ({ k }) => {
    const updated = { ...d.list[0], name: 'Flash Sale 20%', discount_value: 20 };
    await k.common.mockWrite('PUT', `${LIST_API}/*`, { success: true, coupon: updated });
    await k.adminMarketing.mockCouponList(d.list);
    await k.adminMarketing.openCoupons();
    await k.adminMarketing.clickCouponEdit(d.edit.code);
    for (const [label, value] of Object.entries(d.edit.prefilled)) await k.admin.verifyFieldValue(label, value);
    await k.admin.fillForm(d.edit.form);
    await k.adminMarketing.clickModalButton(EDIT, 'Cập nhật');
    await k.common.verifyRequest('PUT', '/admin/coupons/1', d.edit.expectedPayload);
    await k.common.verifyToast(d.edit.toast);
    await k.adminMarketing.verifyRowCells(d.edit.code, { 'Tên': 'Flash Sale 20%', 'Giảm': '20%' });
  });

  test(caseTitle(d.editDates), async ({ k }) => {
    applyCaseMeta(d.editDates);
    await k.adminMarketing.mockCouponList(d.list);
    await k.adminMarketing.openCoupons();
    await k.adminMarketing.clickCouponEdit(d.editDates.code);
    for (const [label, value] of Object.entries(d.editDates.prefilled)) await k.admin.verifyFieldValue(label, value);
  });

  test(caseTitle(d.typeLabel), async ({ k }) => {
    applyCaseMeta(d.typeLabel);
    await k.adminMarketing.mockCouponList(d.list);
    await k.adminMarketing.openCoupons();
    await k.adminMarketing.openCreateCoupon();
    await k.admin.fillForm({ [d.typeLabel.field]: d.typeLabel.value });
    await k.adminMarketing.verifySelectedOption(d.typeLabel.field, d.typeLabel.tableLabel);
  });

  test.describe('Bật/tắt Công khai - Trạng thái (data-driven)', () => {
    for (const c of d.toggles) {
      test(caseTitle(c), async ({ k }) => {
        applyCaseMeta(c);
        await k.common.mockWrite('PUT', `${LIST_API}/*`, { success: true });
        await k.adminMarketing.mockCouponList(d.list);
        await k.adminMarketing.openCoupons();
        await k.adminMarketing.verifyCouponToggle(c.code, c.column, c.from);
        await k.adminMarketing.toggleCoupon(c.code, c.column);
        await k.common.verifyRequest('PUT', '/admin/coupons/', { [c.field]: !c.from });
        await k.common.verifyToast(c.toast);
        await k.adminMarketing.verifyCouponToggle(c.code, c.column, !c.from);
      });
    }
  });

  test('[ADM-CPN-06] Xóa: bấm "Hủy" không gửi DELETE', async ({ k }) => {
    await k.common.mockWrite('DELETE', `${LIST_API}/*`, { success: true });
    await k.adminMarketing.mockCouponList(d.list);
    await k.adminMarketing.openCoupons();
    await k.adminMarketing.clickCouponDelete(d.remove.code);
    await k.adminMarketing.verifyModalText('Xác nhận xóa', [d.remove.confirmText, 'Hành động này không thể hoàn tác']);
    await k.adminMarketing.clickModalButton('Xác nhận xóa', 'Hủy');
    await k.admin.verifyModalClosed('Xác nhận xóa');
    await k.common.verifyNoRequest('DELETE', '/admin/coupons');
    await k.admin.verifyRow(d.remove.code);
  });

  test('[ADM-CPN-07] Xóa: xác nhận gửi DELETE đúng id và bỏ dòng (mock)', async ({ k }) => {
    await k.common.mockWrite('DELETE', `${LIST_API}/*`, { success: true });
    await k.adminMarketing.mockCouponList(d.list);
    await k.adminMarketing.openCoupons();
    await k.adminMarketing.clickCouponDelete(d.remove.code);
    await k.adminMarketing.clickModalButton('Xác nhận xóa', 'Xóa');
    await k.common.verifyRequest('DELETE', '/admin/coupons/1');
    await k.common.verifyToast(d.remove.toast);
    await k.admin.verifyRow(d.remove.code, false);
  });
});
