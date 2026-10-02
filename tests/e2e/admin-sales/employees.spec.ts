import { test } from '@fixtures';
import { AUTH_FILES } from '@config/env';
import { loadData } from '@data/loader';
import type { EmployeesData } from '@data/admin-sales.types';
import { applyCaseMeta, caseTitle } from '@engine/cases';
import { hasAdminAuth } from '@utils/storage';

/**
 * Danh sách nhân viên được mock; mọi thao tác ghi đều mock.
 * Không test được an toàn (cần ghi thật lên API): backend updateEmployee bỏ qua email/password,
 * không kiểm tra quyền theo vai trò, staff tạo được admin, response lộ hash mật khẩu.
 */
const data = loadData<EmployeesData>('admin-sales/employees.json');
const ADD = 'Thêm nhân viên mới';
const EDIT = 'Cập nhật nhân viên';

test.describe('Admin - Nhân viên', () => {
  test.use({ storageState: AUTH_FILES.admin });
  test.skip(() => !hasAdminAuth(), 'Cần E2E_ADMIN_EMAIL/PASSWORD trong .env');

  test('[ADS-EMP-00] Trang nhân viên dữ liệu thật: tiêu đề và cột bảng @smoke', async ({ k }) => {
    await k.admin.openAdminPage('/admin/employees', 'Nhân viên');
    await k.adminSales.verifyEmployeesHeading(data.heading);
    await k.adminSales.verifyColumns(data.headers);
    await k.adminSales.verifyApiRequested('/admin/employees', { page: 1 });
  });

  test.describe('Dữ liệu mock', () => {
    test.beforeEach(async ({ k }) => {
      await k.adminSales.mockEmployeesApi(data.fixture);
      await k.admin.openAdminPage('/admin/employees', 'Nhân viên');
    });

    test('[ADS-EMP-01] Nhãn vai trò hiển thị tiếng Việt cho 4 vai trò', async ({ k }) => {
      for (const r of data.roles) await k.adminSales.verifyEmployeeRole(r.name, r.label);
      await k.adminSales.verifyEmployeeActive('Thủ Kho E2E', false);
      await k.adminSales.verifyEmployeeActive('Nhân Viên E2E', true);
    });

    test('[ADS-EMP-02] Tìm nhân viên gửi từ khóa lên API và lọc bảng', async ({ k }) => {
      await k.admin.searchList('Tìm theo tên, email...', data.search.text);
      await k.adminSales.verifyApiRequested('/admin/employees', data.search.request);
      for (const n of data.search.rows) await k.adminSales.verifyPersonRow(n);
      for (const n of data.search.hidden) await k.adminSales.verifyPersonRow(n, false);
    });

    test.describe('Thêm nhân viên', () => {
      test.beforeEach(async ({ k }) => {
        await k.common.mockWrite('POST', '**/api/admin/employees', { success: true, employee: {} });
        await k.admin.clickButton('Thêm nhân viên');
        await k.admin.verifyModalOpen(ADD);
      });

      for (const c of data.addValidation) {
        test(caseTitle(c), async ({ k }) => {
          applyCaseMeta(c);
          if (Object.keys(c.form).length) await k.admin.fillForm(c.form);
          await k.admin.clickButton('Lưu');
          if (c.nativeEmailInvalid) await k.adminSales.verifyEmployeeEmailNativeInvalid();
          await k.adminSales.verifyFieldErrors(ADD, c.errors);
          await k.common.verifyNoRequest('POST', '/admin/employees');
        });
      }

      test('[ADS-EMP-03] Mặc định vai trò "staff" và tài khoản hoạt động', async ({ k }) => {
        await k.admin.verifyFieldValue('Vai trò', 'staff');
        await test.expect(k.po.adminUi.checkbox('Tài khoản hoạt động')).toBeChecked();
      });
    });

    for (const c of data.create) {
      test(caseTitle(c), async ({ k }) => {
        applyCaseMeta(c);
        await k.common.mockWrite('POST', '**/api/admin/employees', c.response);
        await k.admin.clickButton('Thêm nhân viên');
        await k.admin.fillForm(c.form);
        await k.admin.clickButton('Lưu');
        await k.common.verifyRequest('POST', '/admin/employees', c.payload);
        await k.common.verifyToast(data.createToast);
        await k.admin.verifyModalClosed(ADD);
        await k.adminSales.verifyEmployeeRole(c.name, c.roleLabel);
      });
    }

    test.describe('Sửa nhân viên', () => {
      test('[ADS-EMP-04] Form sửa điền sẵn; đổi tên + vai trò gửi PUT không kèm mật khẩu (mock)', async ({ k }) => {
        const e = data.edit;
        await k.common.mockWrite('PUT', `**/api/admin/employees/${e.id}`, e.response);
        await k.adminSales.clickEmployeeAction(e.employee, 'Sửa');
        await k.admin.verifyModalOpen(EDIT);
        for (const [label, value] of Object.entries(e.prefill)) await k.admin.verifyFieldValue(label, value);
        await k.adminSales.verifyFieldPlaceholder('Mật khẩu', e.passwordPlaceholder);
        await k.admin.fillForm(e.form);
        await k.admin.clickButton('Lưu');
        await k.common.verifyRequest('PUT', `/admin/employees/${e.id}`, e.payload);
        await test.expect(k.common.captured.at(-1)?.body, 'Không đổi mật khẩu thì không gửi password').not.toHaveProperty('password');
        await k.common.verifyToast(e.toast);
        await k.admin.verifyModalClosed(EDIT);
        await k.adminSales.verifyEmployeeRole(e.newName, e.roleLabel);
      });

      test('[ADS-EMP-05] Nhập mật khẩu mới khi sửa -> payload có password', async ({ k }) => {
        const e = data.edit;
        await k.common.mockWrite('PUT', `**/api/admin/employees/${e.id}`, e.response);
        await k.adminSales.clickEmployeeAction(e.employee, 'Sửa');
        await k.admin.fillForm(e.withPassword.form);
        await k.admin.clickButton('Lưu');
        await k.common.verifyRequest('PUT', `/admin/employees/${e.id}`, e.withPassword.payload);
        await k.common.verifyToast(e.toast);
      });

      for (const c of data.editValidation) {
        test(caseTitle(c), async ({ k }) => {
          applyCaseMeta(c);
          await k.common.mockWrite('PUT', '**/api/admin/employees/*', { success: true, employee: {} });
          await k.adminSales.clickEmployeeAction(c.employee, 'Sửa');
          await k.admin.fillForm(c.form);
          await k.admin.clickButton('Lưu');
          await k.adminSales.verifyFieldErrors(EDIT, c.errors);
          await k.common.verifyNoRequest('PUT', '/admin/employees/');
        });
      }
    });

    test.describe('Vô hiệu hóa (nút Xóa) - backend luôn trả 400', () => {
      test('[ADS-EMP-06] Modal "Xác nhận vô hiệu hóa" + "Hủy" không gửi request', async ({ k }) => {
        const d = data.delete;
        await k.common.mockWrite('DELETE', `**/api/admin/employees/${d.id}`, d.backendResponse, d.backendStatus);
        await k.adminSales.clickEmployeeAction(d.employee, 'Xóa');
        await k.admin.verifyModalOpen(d.heading);
        await k.adminSales.verifyModalText(d.heading, 'Hành động này không thể hoàn tác');
        await test.expect(k.po.page.getByText(d.message)).toBeVisible();
        await k.admin.clickButton('Hủy');
        await k.admin.verifyModalClosed(d.heading);
        await k.common.verifyNoRequest('DELETE', '/admin/employees/');
      });

      test('[ADS-EMP-07] Xác nhận -> hiển thị lỗi backend, nhân viên vẫn trong bảng', async ({ k }) => {
        const d = data.delete;
        await k.common.mockWrite('DELETE', `**/api/admin/employees/${d.id}`, d.backendResponse, d.backendStatus);
        await k.adminSales.clickEmployeeAction(d.employee, 'Xóa');
        await k.admin.clickButton('Xác nhận');
        await k.common.verifyRequest('DELETE', `/admin/employees/${d.id}`);
        await k.common.verifyToast(d.backendResponse.message);
        await k.admin.verifyModalClosed(d.heading);
        await k.adminSales.verifyPersonRow(d.employee);
      });

      test('[ADS-EMP-08] Xác nhận vô hiệu hóa thành công', async ({ k }) => {
        test.fail(
          true,
          'BUG: adminController.deleteEmployee luôn trả 400 "Không thể xóa tài khoản nhân viên..." -> nút Xóa/Vô hiệu hóa ở AdminEmployees.jsx:112-121 không bao giờ thành công (phải dùng nút gạt)',
        );
        const d = data.delete;
        await k.common.mockWrite('DELETE', `**/api/admin/employees/${d.id}`, d.backendResponse, d.backendStatus);
        await k.adminSales.clickEmployeeAction(d.employee, 'Xóa');
        await k.admin.clickButton('Xác nhận');
        await k.common.verifyToast(d.successToast);
      });
    });

    test.describe('Nút gạt trạng thái (mock PUT /toggle)', () => {
      test('[ADS-EMP-09] Tắt tài khoản thành công -> toast + nút gạt xám', async ({ k }) => {
        const t = data.toggle;
        await k.common.mockWrite('PUT', `**/api/admin/employees/${t.id}/toggle`, { success: true });
        await k.adminSales.clickEmployeeAction(t.employee, 'Trạng thái');
        await k.common.verifyRequest('PUT', `/admin/employees/${t.id}/toggle`);
        await k.common.verifyToast(t.toast);
        await k.adminSales.verifyEmployeeActive(t.employee, false);
      });

      test('[ADS-EMP-10] API lỗi -> báo lỗi và giữ nguyên trạng thái', async ({ k }) => {
        test.fail(true, 'BUG: AdminEmployees.jsx:65-67 nhánh catch vẫn đảo is_active nên nút gạt đổi màu dù API lỗi');
        const t = data.toggle;
        await k.common.mockWrite('PUT', `**/api/admin/employees/${t.id}/toggle`, { success: false, message: 'Lỗi' }, 500);
        await k.adminSales.clickEmployeeAction(t.employee, 'Trạng thái');
        await k.common.verifyToast(t.errorToast);
        await k.adminSales.verifyEmployeeActive(t.employee, true);
      });
    });
  });
});
