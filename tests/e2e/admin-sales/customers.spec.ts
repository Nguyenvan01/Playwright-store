import { test } from '@fixtures';
import { AUTH_FILES } from '@config/env';
import { loadData } from '@data/loader';
import type { CustomersData } from '@data/admin-sales.types';
import { applyCaseMeta, caseTitle } from '@engine/cases';
import { hasAdminAuth } from '@utils/storage';

/** Danh sách khách hàng được mock (không phụ thuộc / không lộ dữ liệu khách thật); mọi thao tác ghi đều mock. */
const data = loadData<CustomersData>('admin-sales/customers.json');
const ADD = 'Thêm khách hàng';
const EDIT = 'Cập nhật khách hàng';

test.describe('Admin - Khách hàng', () => {
  test.use({ storageState: AUTH_FILES.admin });
  test.skip(() => !hasAdminAuth(), 'Cần E2E_ADMIN_EMAIL/PASSWORD trong .env');

  test.beforeEach(async ({ k }) => {
    await k.adminSales.mockCustomersApi(data.fixture);
    await k.admin.openAdminPage('/admin/customers', 'Khách hàng');
  });

  test('[ADS-CUS-01] Bảng khách hàng: đủ cột, trạng thái, chi tiêu, điểm @smoke', async ({ k }) => {
    await k.adminSales.verifyColumns(data.headers);
    for (const r of data.rows) await k.adminSales.verifyCustomerRow(r);
  });

  test('[ADS-CUS-02] Tìm khách hàng gửi từ khóa lên API và lọc bảng', async ({ k }) => {
    await k.admin.searchList('Tìm theo tên, email, SĐT...', data.search.text);
    await k.adminSales.verifyApiRequested('/admin/customers', { search: data.search.text, page: 1 });
    for (const n of data.search.rows) await k.adminSales.verifyPersonRow(n);
    for (const n of data.search.hidden) await k.adminSales.verifyPersonRow(n, false);
  });

  test.describe('Thêm khách hàng', () => {
    test.beforeEach(async ({ k }) => {
      await k.common.mockWrite('POST', '**/api/admin/customers', data.add.response);
      await k.admin.clickButton(ADD);
      await k.admin.verifyModalOpen(ADD);
    });

    for (const c of data.addValidation) {
      test(caseTitle(c), async ({ k }) => {
        applyCaseMeta(c);
        if (Object.keys(c.form).length) await k.admin.fillForm(c.form);
        await k.admin.clickButton('Lưu');
        await k.adminSales.verifyFieldErrors(ADD, c.errors);
        await k.common.verifyNoRequest('POST', '/admin/customers');
      });
    }

    test('[ADS-CUS-03] Form thêm có placeholder và gợi ý mật khẩu mặc định', async ({ k }) => {
      await k.adminSales.verifyFieldPlaceholder('Họ và tên', 'Nguyễn Văn A');
      await k.adminSales.verifyFieldPlaceholder('Email', 'email@example.com');
      await k.adminSales.verifyFieldPlaceholder('Số điện thoại', '0912345678');
      await k.adminSales.verifyModalText(ADD, data.add.passwordHint);
    });

    test('[ADS-CUS-04] Thêm khách hợp lệ (mock POST) -> toast, đóng modal, dòng mới đầu bảng', async ({ k }) => {
      await k.admin.fillForm(data.add.form);
      await k.admin.clickButton('Lưu');
      await k.common.verifyRequest('POST', '/admin/customers', data.add.payload);
      await k.common.verifyToast(data.add.toast);
      await k.admin.verifyModalClosed(ADD);
      await k.adminSales.verifyPersonRow(data.add.form['Họ và tên'] as string);
    });

    test('[ADS-CUS-05] Lỗi sửa xong ô nhập thì thông báo lỗi biến mất', async ({ k }) => {
      await k.admin.clickButton('Lưu');
      await k.adminSales.verifyFieldErrors(ADD, ['Họ và tên không được để trống.', 'Email không được để trống.']);
      await k.admin.fillForm({ 'Họ và tên': 'Khách E2E' });
      await k.adminSales.verifyFieldErrors(ADD, ['Email không được để trống.']);
    });

    test('[ADS-CUS-06] "Hủy" đóng modal, không gửi request', async ({ k }) => {
      await k.admin.fillForm(data.add.form);
      await k.admin.clickButton('Hủy');
      await k.admin.verifyModalClosed(ADD);
      await k.common.verifyNoRequest('POST', '/admin/customers');
    });
  });

  test('[ADS-CUS-07] Server báo "Email đã tồn tại." -> toast lỗi, modal vẫn mở', async ({ k }) => {
    await k.common.mockWrite('POST', '**/api/admin/customers', { success: false, message: data.add.error.message }, data.add.error.status);
    await k.admin.clickButton(ADD);
    await k.admin.fillForm(data.add.form);
    await k.admin.clickButton('Lưu');
    await k.common.verifyRequest('POST', '/admin/customers', data.add.payload);
    await k.common.verifyToast(data.add.error.message);
    await k.admin.verifyModalOpen(ADD);
  });

  test.describe('Sửa khách hàng', () => {
    test('[ADS-CUS-08] Form sửa điền sẵn dữ liệu; lưu gửi PUT đúng payload (mock) và cập nhật dòng', async ({ k }) => {
      const e = data.edit;
      await k.common.mockWrite('PUT', `**/api/admin/customers/${e.id}`, e.response);
      await k.admin.clickRowAction(e.customer, 'Sửa');
      await k.admin.verifyModalOpen(EDIT);
      for (const [label, value] of Object.entries(e.prefill)) await k.admin.verifyFieldValue(label, value);
      await k.admin.fillForm(e.form);
      await k.admin.clickButton('Lưu');
      await k.common.verifyRequest('PUT', `/admin/customers/${e.id}`, e.payload);
      await test.expect(k.common.captured.at(-1)?.body, 'Không đổi mật khẩu thì không gửi password').not.toHaveProperty('password');
      await k.common.verifyToast(e.toast);
      await k.admin.verifyModalClosed(EDIT);
      await k.adminSales.verifyCustomerRow({ name: e.newName, status: e.status });
    });

    for (const c of data.editValidation) {
      test(caseTitle(c), async ({ k }) => {
        applyCaseMeta(c);
        await k.common.mockWrite('PUT', '**/api/admin/customers/*', { success: true, customer: {} });
        await k.admin.clickRowAction(c.customer, 'Sửa');
        await k.admin.fillForm(c.form);
        await k.admin.clickButton('Lưu');
        await k.adminSales.verifyFieldErrors(EDIT, c.errors);
        await k.common.verifyNoRequest('PUT', '/admin/customers/');
      });
    }
  });

  test('[ADS-CUS-09] Modal chi tiết khách hàng (GET /admin/customers/:id)', async ({ k }) => {
    await k.admin.clickRowAction(data.detail.customer, 'Chi tiết');
    await k.admin.verifyModalOpen('Chi tiết khách hàng');
    await k.adminSales.verifyApiRequested('/admin/customers/9601');
    await k.adminSales.verifyCustomerDetail(data.detail);
  });

  test('[ADS-CUS-13] Đơn gần đây trong chi tiết khách hiển thị trạng thái tiếng Việt', async ({ k }) => {
    test.fail(true, `BUG: ${data.detail.statusBug}`);
    await k.admin.clickRowAction(data.detail.customer, 'Chi tiết');
    await k.adminSales.verifyCustomerDetail(data.detail);
    await k.adminSales.verifyCustomerRecentOrderStatuses(data.detail.recentStatuses);
  });

  test.describe('Xóa khách hàng (mock DELETE, data-driven)', () => {
    test('[ADS-CUS-10] Modal xác nhận xóa: nội dung + "Hủy" không gửi request', async ({ k }) => {
      await k.common.mockWrite('DELETE', '**/api/admin/customers/*', { success: true });
      await k.admin.clickRowAction('Trần Thị Kiểm Thử', 'Xóa');
      await k.adminSales.verifyModalText('Xác nhận xóa', 'Hành động này không thể hoàn tác');
      await k.adminSales.verifyCustomerDeleteWarning(null);
      await test.expect(k.po.page.getByText(data.deleteText)).toBeVisible();
      await k.admin.clickButton('Hủy');
      await k.admin.verifyModalClosed('Xác nhận xóa');
      await k.common.verifyNoRequest('DELETE', '/admin/customers/');
      await k.adminSales.verifyPersonRow('Trần Thị Kiểm Thử');
    });

    for (const c of data.delete) {
      test(caseTitle(c), async ({ k }) => {
        applyCaseMeta(c);
        await k.common.mockWrite('DELETE', `**/api/admin/customers/${c.customerId}`, c.response, c.status);
        await k.admin.clickRowAction(c.customer, 'Xóa');
        await k.adminSales.verifyCustomerDeleteWarning(c.warning ?? null);
        await k.admin.clickButton('Xóa');
        await k.common.verifyRequest('DELETE', `/admin/customers/${c.customerId}`);
        await k.common.verifyToast(c.toast);
        await k.admin.verifyModalClosed('Xác nhận xóa');
        await k.adminSales.verifyPersonRow(c.customer, !c.removed);
        if (c.rowStatus) await k.adminSales.verifyCustomerRow({ name: c.customer, status: c.rowStatus });
      });
    }
  });

  test.describe('Phân trang (20 khách/trang)', () => {
    test.beforeEach(async ({ k }) => {
      await k.adminSales.mockCustomersApi({ ...data.fixture, total: data.pagination.total });
      await k.common.reload();
    });

    test('[ADS-CUS-11] Bấm trang 2 gọi API page=2', async ({ k }) => {
      await k.adminSales.verifyPaginationText('Trang 1 / 8');
      await k.adminSales.goToPage(2);
      await k.adminSales.verifyApiRequested('/admin/customers', { page: 2 });
      await k.adminSales.verifyPaginationText('Trang 2 / 8');
    });

    test('[ADS-CUS-12] Sang trang 6 thì dãy số trang dịch theo (hiện nút 6)', async ({ k }) => {
      test.fail(true, 'BUG: AdminCustomers.jsx:271 dãy nút trang luôn là 1..5 (không dịch theo trang hiện tại) -> không bấm trực tiếp được trang 6-8');
      await k.adminSales.goToPage(data.pagination.lastClicked);
      await k.adminSales.clickNextPage();
      await k.adminSales.verifyPaginationText(data.pagination.text);
      await k.adminSales.verifyApiRequested('/admin/customers', { page: data.pagination.expectedPage });
      await k.adminSales.verifyPageButton(data.pagination.expectedPage);
    });
  });
});
