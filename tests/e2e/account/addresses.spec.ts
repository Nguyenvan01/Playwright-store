import { test } from '@fixtures';
import { AUTH_FILES } from '@config/env';
import { loadData } from '@data/loader';
import type { AddressesData } from '@data/account.types';
import { applyCaseMeta, caseTitle } from '@engine/cases';
import { hasCustomerAuth } from '@utils/storage';
import { API } from './support';

const data = loadData<AddressesData>('account/addresses.json');
const created = data.create.form;

/** Sổ địa chỉ /addresses. Mọi thao tác ghi (thêm/sửa/xóa/đặt mặc định) đều mock + kiểm tra payload. */
test.describe('Sổ địa chỉ', () => {
  test.use({ storageState: AUTH_FILES.customer });
  test.skip(() => !hasCustomerAuth(), 'Chưa có tài khoản test (xem .env)');

  test.describe('Chưa có địa chỉ', () => {
    test.beforeEach(async ({ k }) => {
      await k.common.mockGet(API.addresses, data.empty);
      await k.account.openAddresses();
    });

    test('[ACC-ADR-E01] Hiển thị màn hình trống', async ({ k }) => {
      await k.account.verifyAddressesEmpty();
    });

    test('[ACC-ADR-E02] Thêm địa chỉ đầu tiên từ màn hình trống: server đặt làm mặc định', async ({ k }) => {
      await k.common.mockWrite('POST', API.addresses, data.createFirst, 201);
      await k.account.openAddAddressFromEmptyState();
      await k.account.verifyAddressFormOpen('Thêm địa chỉ mới');
      await k.account.fillAddressForm(created);
      await k.account.submitAddressForm();
      await k.common.verifyRequest('POST', '/api/addresses', { ...created });
      await k.account.verifyAddressFormClosed();
      await k.account.verifyAddressList([String(created.fullName)]);
      await k.account.verifyAddressDefault(String(created.fullName), true);
    });
  });

  test.describe('Có địa chỉ', () => {
    test.beforeEach(async ({ k }) => {
      await k.common.mockGet(API.addresses, data.list);
      await k.account.openAddresses();
      await k.account.verifyAddressList(data.names);
    });

    test('[ACC-ADR-01] Danh sách địa chỉ: thông tin thẻ và địa chỉ mặc định @smoke', async ({ k }) => {
      for (const [name, texts] of Object.entries(data.cardTexts)) await k.account.verifyAddressCard(name, texts);
      await k.account.verifyAddressDefault(data.defaultName, true);
      await k.account.verifyAddressDefault(data.otherName, false);
      await k.account.verifyDefaultBadgeCount(1);
    });

    test.describe('Validate form thêm địa chỉ (data-driven)', () => {
      for (const c of data.validation) {
        test(caseTitle(c), async ({ k }) => {
          applyCaseMeta(c);
          await k.common.mockWrite('POST', API.addresses, data.create.response, 201);
          await k.account.openAddAddressForm();
          await k.account.fillAddressForm({ ...data.validForm, ...c.form });
          await k.account.submitAddressForm();
          await k.account.verifyAddressFormErrors(c.errors);
          await k.common.verifyNoRequest('POST', '/api/addresses');
        });
      }
    });

    test('[ACC-ADR-02] Thêm địa chỉ mới (SĐT có khoảng trắng hợp lệ): gửi đúng payload, hiện thẻ mới @smoke', async ({ k }) => {
      await k.common.mockWrite('POST', API.addresses, data.create.response, 201);
      await k.account.openAddAddressForm();
      await k.account.fillAddressForm(created);
      await k.account.submitAddressForm();
      await k.common.verifyRequest('POST', '/api/addresses', { ...created });
      await k.account.verifyAddressFormClosed();
      await k.account.verifyAddressList([String(created.fullName), ...data.names]);
      await k.account.verifyAddressCard(String(created.fullName), data.create.cardTexts);
      await k.account.verifyAddressDefault(String(created.fullName), false);
    });

    test('[ACC-ADR-03] Thêm địa chỉ mặc định mới: chỉ còn 1 badge Mặc định', async ({ k }) => {
      test.fail(
        true,
        'BUG: AddressesPage.jsx:218 thêm địa chỉ mặc định vào đầu danh sách nhưng không bỏ is_default của địa chỉ cũ (backend đã bỏ) -> 2 badge "Mặc định"',
      );
      const form = data.createDefault.form;
      await k.common.mockWrite('POST', API.addresses, data.createDefault.response, 201);
      await k.account.openAddAddressForm();
      await k.account.fillAddressForm(form);
      await k.account.submitAddressForm();
      await k.common.verifyRequest('POST', '/api/addresses', { isDefault: true });
      await k.account.verifyAddressDefault(String(form.fullName), true);
      await k.account.verifyDefaultBadgeCount(1);
    });

    test('[ACC-ADR-04] Hủy form thêm: đóng form, không gửi request', async ({ k }) => {
      await k.common.mockWrite('POST', API.addresses, data.create.response, 201);
      await k.account.openAddAddressForm();
      await k.account.fillAddressForm(created);
      await k.account.cancelAddressForm();
      await k.account.verifyAddressFormClosed();
      await k.common.verifyNoRequest('POST', '/api/addresses');
      await k.account.verifyAddressList(data.names);
    });

    test('[ACC-ADR-05] Sửa địa chỉ: form điền sẵn, gửi PUT, thẻ cập nhật', async ({ k }) => {
      const e = data.edit;
      await k.common.mockWrite('PUT', API.address, e.response);
      await k.account.editAddress(e.name);
      await k.account.verifyAddressFormOpen('Sửa địa chỉ');
      await k.account.verifyAddressFormValues(e.expectedForm);
      await k.account.fillAddressForm(e.changes);
      await k.account.submitAddressForm();
      await k.common.verifyRequest('PUT', `/api/addresses/${data.otherId}`, {
        ...e.expectedForm,
        ...e.changes,
        isDefault: false,
      });
      await k.account.verifyAddressFormClosed();
      await k.account.verifyAddressList([data.defaultName, e.newName]);
      await k.account.verifyAddressCard(e.newName, [String(e.changes.address)]);
    });

    test('[ACC-ADR-06] Đặt làm mặc định: gửi PUT isDefault, badge chuyển sang địa chỉ mới', async ({ k }) => {
      await k.common.mockWrite('PUT', API.address, data.setDefault.response);
      await k.account.setDefaultAddress(data.otherName);
      await k.common.verifyRequest('PUT', `/api/addresses/${data.otherId}`, { isDefault: true });
      await k.account.verifyAddressDefault(data.otherName, true);
      await k.account.verifyAddressDefault(data.defaultName, false);
      await k.account.verifyDefaultBadgeCount(1);
    });

    test('[ACC-ADR-07] Sau khi đổi mặc định, thẻ địa chỉ không hiện ký tự "0" thừa', async ({ k }) => {
      test.fail(
        true,
        'BUG: AddressesPage.jsx:226 đặt is_default = 0 (số) và dòng 331 render {addr.is_default && ...} -> React in ra chữ "0" cạnh tên người nhận',
      );
      await k.common.mockWrite('PUT', API.address, data.setDefault.response);
      await k.account.setDefaultAddress(data.otherName);
      await k.account.verifyAddressDefault(data.otherName, true);
      await k.account.verifyAddressNameRow(data.otherName, true);
      await k.account.verifyAddressNameRow(data.defaultName, false);
    });

    test('[ACC-ADR-08] Xóa địa chỉ: hộp xác nhận, gửi DELETE, thẻ biến mất', async ({ k }) => {
      await k.common.mockWrite('DELETE', API.address, data.delete.response);
      await k.account.deleteAddress(data.otherName);
      await k.account.verifyDeleteAddressDialog(data.delete.dialogText);
      await k.account.confirmDeleteAddress();
      await k.common.verifyRequest('DELETE', `/api/addresses/${data.otherId}`);
      await k.account.verifyAddressList([data.defaultName]);
    });

    test('[ACC-ADR-09] Hủy xóa: không gửi request, danh sách giữ nguyên', async ({ k }) => {
      await k.common.mockWrite('DELETE', API.address, data.delete.response);
      await k.account.deleteAddress(data.otherName);
      await k.account.cancelDeleteAddress();
      await k.common.verifyNoRequest('DELETE', '/api/addresses');
      await k.account.verifyAddressList(data.names);
    });

    test('[ACC-ADR-10] Xóa địa chỉ mặc định: địa chỉ còn lại được hiển thị là mặc định', async ({ k }) => {
      test.fail(
        true,
        'BUG: AddressesPage.jsx:235 chỉ lọc bỏ địa chỉ đã xóa, không tải lại danh sách; backend (customerController.js deleteAddress) đã chuyển mặc định sang địa chỉ khác nhưng UI không có badge "Mặc định" nào',
      );
      await k.common.mockWrite('DELETE', API.address, data.delete.response);
      await k.account.deleteAddress(data.defaultName);
      await k.account.confirmDeleteAddress();
      await k.common.verifyRequest('DELETE', `/api/addresses/${data.defaultId}`);
      await k.account.verifyAddressList([data.otherName]);
      await k.account.verifyAddressDefault(data.otherName, true);
    });

    test(caseTitle(data.serverError), async ({ k }) => {
      const c = data.serverError;
      applyCaseMeta(c);
      await k.common.mockWrite('POST', API.addresses, c.response, c.status);
      await k.account.openAddAddressForm();
      await k.account.fillAddressForm(created);
      await k.account.submitAddressForm();
      await k.common.verifyRequest('POST', '/api/addresses');
      await k.common.verifyTextVisible(c.message);
    });
  });
});
