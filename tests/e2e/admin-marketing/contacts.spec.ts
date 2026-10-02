import { test } from '@fixtures';
import { AUTH_FILES } from '@config/env';
import { loadData } from '@data/loader';
import type { ContactsData } from '@data/admin-marketing.types';
import { applyCaseMeta, caseTitle } from '@engine/cases';
import { hasAdminAuth } from '@utils/storage';

const d = loadData<ContactsData>('admin-marketing/contacts.json');
const SEARCH = 'Tìm theo tên, email, số điện thoại, nội dung...';
const ITEM_API = '**/api/admin/contacts/*';
const STATUS_API = '**/api/admin/contacts/*/status';
const names = d.list.map((c) => c.name);

test.describe('Quản trị - Liên hệ', () => {
  test.use({ storageState: AUTH_FILES.admin });
  test.skip(() => !hasAdminAuth(), 'Cần E2E_ADMIN_EMAIL/PASSWORD trong .env');

  test('[ADM-CTC-01] Dữ liệu thật: trang tải được, đủ cột @smoke', async ({ k }) => {
    await k.adminMarketing.openContacts();
    await k.adminMarketing.verifyColumns(d.headers);
    await k.common.verifyNoPageErrors();
  });

  test('[ADM-CTC-02] Chưa có liên hệ -> trạng thái rỗng', async ({ k }) => {
    await k.adminMarketing.mockContactList([]);
    await k.adminMarketing.openContacts();
    await k.common.verifyTextVisible('Chưa có liên hệ nào');
    await k.common.verifyTextVisible('Liên hệ mới từ khách hàng sẽ hiển thị tại đây.');
  });

  test('[ADM-CTC-03] API lỗi -> toast "Không thể tải danh sách liên hệ."', async ({ k }) => {
    await k.common.mockGet('**/api/admin/contacts*', { success: false }, 500);
    await k.adminMarketing.openContacts();
    await k.common.verifyToast('Không thể tải danh sách liên hệ.');
  });

  test.describe('Hiển thị dòng + nút theo trạng thái (data-driven)', () => {
    for (const c of d.rows) {
      test(caseTitle(c), async ({ k }) => {
        applyCaseMeta(c);
        await k.adminMarketing.mockContactList(d.list);
        await k.adminMarketing.openContacts();
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
        await k.adminMarketing.mockContactList(d.list);
        await k.adminMarketing.openContacts();
        await k.admin.searchList(SEARCH, c.keyword);
        await k.adminMarketing.verifyVisibleRows(c.visible, c.hidden);
        if (c.emptyText) await k.common.verifyTextVisible(c.emptyText);
      });
    }
  });

  test.describe('Lọc trạng thái (data-driven)', () => {
    for (const c of d.filters) {
      test(caseTitle(c), async ({ k }) => {
        applyCaseMeta(c);
        await k.adminMarketing.mockContactList(c.list ?? d.list);
        await k.adminMarketing.openContacts();
        await k.adminMarketing.filterContactStatus(c.status);
        await k.adminMarketing.verifyListQuery('/admin/contacts', c.query);
        await k.adminMarketing.verifyVisibleRows(c.visible, names.filter((n) => !c.visible.includes(n)));
        if (c.emptyText) await k.common.verifyTextVisible(c.emptyText);
      });
    }
  });

  test.describe('Đổi trạng thái xử lý trên dòng (data-driven)', () => {
    for (const c of d.statusActions) {
      test(caseTitle(c), async ({ k }) => {
        applyCaseMeta(c);
        await k.common.mockWrite('PUT', STATUS_API, { success: true });
        await k.adminMarketing.mockContactList(d.list);
        await k.adminMarketing.openContacts();
        await k.admin.clickRowAction(c.rowText, c.action);
        await k.common.verifyRequest('PUT', `/admin/contacts/${c.contactId}/status`, { status: c.status });
        await k.common.verifyToast(d.toast);
        await k.adminMarketing.verifyRowCells(c.rowText, { 'Trạng thái': c.badge });
        await k.adminMarketing.verifyRowActions(c.rowText, c.actionsAfter);
      });
    }
  });

  test('[ADM-CTC-04] Xem chi tiết và đánh dấu đã xử lý trong modal (mock PUT)', async ({ k }) => {
    await k.common.mockWrite('PUT', STATUS_API, { success: true });
    await k.adminMarketing.mockContactList(d.list);
    await k.adminMarketing.openContacts();
    await k.admin.clickRowAction(d.detail.rowText, 'Xem');
    await k.adminMarketing.verifyModalText('Chi tiết liên hệ', d.detail.texts);
    await k.adminMarketing.clickModalButton('Chi tiết liên hệ', d.detail.button);
    await k.common.verifyRequest('PUT', '/admin/contacts/1/status', { status: 'processed' });
    await k.common.verifyToast(d.toast);
    await k.adminMarketing.verifyModalText('Chi tiết liên hệ', [d.detail.badge, 'Đánh dấu chưa xử lý']);
  });

  test('[ADM-CTC-05] Xóa: bấm "Hủy" không gửi DELETE', async ({ k }) => {
    await k.common.mockWrite('DELETE', ITEM_API, { success: true });
    await k.adminMarketing.mockContactList(d.list);
    await k.adminMarketing.openContacts();
    await k.admin.clickRowAction(d.remove.rowText, 'Xóa');
    await k.adminMarketing.verifyModalText('Xóa liên hệ', ['Bạn có chắc chắn muốn xóa liên hệ này không?']);
    await k.adminMarketing.clickModalButton('Xóa liên hệ', 'Hủy');
    await k.admin.verifyModalClosed('Xóa liên hệ');
    await k.common.verifyNoRequest('DELETE', '/admin/contacts');
  });

  test('[ADM-CTC-06] Xóa: xác nhận gửi DELETE và bỏ dòng (mock)', async ({ k }) => {
    await k.common.mockWrite('DELETE', ITEM_API, { success: true });
    await k.adminMarketing.mockContactList(d.list);
    await k.adminMarketing.openContacts();
    await k.admin.clickRowAction(d.remove.rowText, 'Xóa');
    await k.adminMarketing.clickModalButton('Xóa liên hệ', 'Xóa');
    await k.common.verifyRequest('DELETE', '/admin/contacts/3');
    await k.common.verifyToast(d.remove.toast);
    await k.admin.verifyRow(d.remove.rowText, false);
  });
});
