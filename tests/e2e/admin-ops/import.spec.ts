import { test } from '@fixtures';
import type { Keywords } from '@keywords/index';
import { AUTH_FILES } from '@config/env';
import { loadData } from '@data/loader';
import type { FormFields } from '@data/admin-marketing.types';
import type { ImportData, ImportItemInput } from '@data/admin-ops.types';
import { applyCaseMeta, caseTitle } from '@engine/cases';
import { hasAdminAuth } from '@utils/storage';

/**
 * Trang Nhập hàng có lỗi vòng lặp tải lại (toast tạo lại mỗi lần render -> effect gọi lại API),
 * nên MỌI request GET đều được giả lập để không gọi liên tục lên production.
 */
const d = loadData<ImportData>('admin-ops/import.json');
const SEARCH = 'Tìm mã đơn, nhà cung cấp...';
const LIST_API = '**/api/admin/imports';
const ITEM_API = '**/api/admin/imports/*';
const CREATE = 'Tạo đơn nhập hàng';
const codes = d.mock.imports.map((i) => i.code);

/** Mở form tạo đơn và điền: thông tin chung -> các dòng sản phẩm -> thanh toán. */
async function fillCreateForm(k: Keywords, form: FormFields, items: ImportItemInput[], payment?: FormFields) {
  await k.adminOps.openCreateImport();
  if (Object.keys(form).length) await k.admin.fillForm(form);
  for (const [i, item] of items.entries()) {
    if (i > 0) await k.adminOps.addImportItemRow();
    await k.adminOps.fillImportItem(i, item);
  }
  if (payment) await k.admin.fillForm(payment);
}

test.describe('Quản trị - Nhập hàng (API giả lập)', () => {
  test.use({ storageState: AUTH_FILES.admin });
  test.skip(() => !hasAdminAuth(), 'Cần E2E_ADMIN_EMAIL/PASSWORD trong .env');

  test.beforeEach(async ({ k }) => {
    await k.adminOps.mockImportData(d.mock);
  });

  test('[ADO-IMP-01] Trang tải: tiêu đề, đủ cột, thẻ thống kê @smoke', async ({ k }) => {
    await k.adminOps.openImport();
    await k.adminOps.verifyColumns(d.headers);
    await k.adminOps.verifyRowCount(d.mock.imports.length);
    await k.adminOps.verifyStatCards(d.statCards);
    await k.common.verifyNoPageErrors();
  });

  test.describe('Hiển thị dòng + nút theo trạng thái (data-driven)', () => {
    for (const c of d.rows) {
      test(caseTitle(c), async ({ k }) => {
        applyCaseMeta(c);
        await k.adminOps.openImport();
        await k.adminOps.verifyRowCells(c.rowText, c.expected);
        await k.adminOps.verifyRowActions(c.rowText, c.actions);
      });
    }
  });

  test.describe('Lọc / tìm kiếm phía server (data-driven)', () => {
    for (const c of d.filters) {
      test(caseTitle(c), async ({ k }) => {
        applyCaseMeta(c);
        await k.adminOps.openImport();
        if (c.action === 'status') await k.adminOps.filterImportStatus(c.value);
        if (c.action === 'supplier') await k.adminOps.filterImportSupplier(c.value);
        if (c.action === 'search') await k.admin.searchList(SEARCH, c.value);
        await k.adminOps.verifyListQuery('/admin/imports', c.query);
        await k.adminOps.verifyVisibleRows(c.visible, codes.filter((code) => !c.visible.includes(code)));
        if (c.emptyText) await k.common.verifyTextVisible(c.emptyText);
      });
    }
  });

  test.describe('Form tạo đơn - kiểm tra dữ liệu (data-driven)', () => {
    for (const c of d.validation) {
      test(caseTitle(c), async ({ k }) => {
        applyCaseMeta(c);
        await k.common.mockWrite('POST', LIST_API, { success: true });
        await k.adminOps.openImport();
        await fillCreateForm(k, c.form, c.items);
        await k.adminOps.clickModalButton(CREATE, 'Tạo đơn nhập hàng');
        await k.common.verifyToast(c.toast);
        await k.admin.verifyModalOpen(CREATE);
        await k.common.verifyNoRequest('POST', '/admin/imports');
      });
    }
  });

  test(caseTitle(d.totals), async ({ k }) => {
    applyCaseMeta(d.totals);
    await k.adminOps.openImport();
    await fillCreateForm(k, d.totals.form, d.totals.items);
    await k.adminOps.verifyImportTotals(0, d.totals.lineTotal, d.totals.grandTotal);
  });

  test.describe('Tạo đơn thành công (data-driven, mock POST)', () => {
    for (const c of d.create) {
      test(caseTitle(c), async ({ k }) => {
        applyCaseMeta(c);
        await k.common.mockWrite('POST', LIST_API, { success: true, import: { id: 99 } });
        await k.adminOps.openImport();
        await fillCreateForm(k, c.form, c.items, c.payment);
        await k.adminOps.clickModalButton(CREATE, c.button);
        await k.common.verifyRequest('POST', '/admin/imports', c.expectedPayload);
        await k.common.verifyToast(c.toast);
        await k.admin.verifyModalClosed(CREATE);
      });
    }
  });

  test(caseTitle(d.createError), async ({ k }) => {
    applyCaseMeta(d.createError);
    await k.common.mockWrite('POST', LIST_API, { success: false, message: d.createError.message }, d.createError.status);
    await k.adminOps.openImport();
    await fillCreateForm(k, d.createError.form, d.createError.items);
    await k.adminOps.clickModalButton(CREATE, 'Tạo đơn nhập hàng');
    await k.common.verifyToast(d.createError.message);
    await k.admin.verifyModalOpen(CREATE);
  });

  test('[ADO-IMP-02] Xem chi tiết đơn nhập', async ({ k }) => {
    await k.adminOps.openImport();
    await k.admin.clickRowAction(d.detail.rowText, 'Xem chi tiết');
    await k.adminOps.verifyModalText('Chi tiết đơn nhập hàng', d.detail.texts);
    await k.adminOps.verifyListQuery(`/admin/imports/${d.detail.id}`, {});
  });

  test.describe('Nhận hàng (data-driven)', () => {
    for (const c of d.receive.cases) {
      test(caseTitle(c), async ({ k }) => {
        applyCaseMeta(c);
        await k.common.mockWrite('POST', `${ITEM_API}/receive`, { success: true });
        await k.adminOps.openImport();
        await k.admin.clickRowAction(d.receive.rowText, 'Nhận hàng');
        await k.adminOps.verifyModalText('Nhận hàng', [d.receive.rowText]);
        await k.adminOps.setReceiveQuantities(c.quantities);
        await k.adminOps.clickModalButton('Nhận hàng', 'Xác nhận nhận hàng');
        await k.common.verifyToast(c.toast);
        if (c.expectedPayload) {
          await k.common.verifyRequest('POST', `/admin/imports/${d.receive.id}/receive`, c.expectedPayload);
          await k.admin.verifyModalClosed('Nhận hàng');
        } else {
          await k.common.verifyNoRequest('POST', '/receive');
        }
      });
    }
  });

  test('[ADO-IMP-03] Hủy đơn: đồng ý hộp thoại gửi DELETE (mock)', async ({ k }) => {
    await k.common.mockWrite('DELETE', ITEM_API, { success: true });
    await k.adminOps.openImport();
    await k.common.acceptNextDialog(true);
    await k.admin.clickRowAction(d.cancel.rowText, 'Hủy đơn');
    await k.common.verifyRequest('DELETE', `/admin/imports/${d.cancel.id}`);
    await k.common.verifyToast(d.cancel.toast);
  });

  test('[ADO-IMP-05] Hủy đơn: bấm Hủy trên hộp thoại không gửi DELETE', async ({ k }) => {
    await k.common.mockWrite('DELETE', ITEM_API, { success: true });
    await k.adminOps.openImport();
    await k.common.acceptNextDialog(false);
    await k.admin.clickRowAction(d.cancel.rowText, 'Hủy đơn');
    await k.adminOps.verifyRowCells(d.cancel.rowText, { 'Trạng thái': 'Đang xử lý' });
    await k.common.verifyNoRequest('DELETE', '/admin/imports');
  });
});
