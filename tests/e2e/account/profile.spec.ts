import { test } from '@fixtures';
import { AUTH_FILES, env } from '@config/env';
import { loadData } from '@data/loader';
import type { AddressesData, OrdersData, ProfileData, WishlistData } from '@data/account.types';
import { applyCaseMeta, caseTitle } from '@engine/cases';
import { hasCustomerAuth } from '@utils/storage';
import { API, mockAccountData } from './support';

const profile = loadData<ProfileData>('account/profile.json');
const orders = loadData<OrdersData>('account/orders.json');
const wishlist = loadData<WishlistData>('account/wishlist.json');
const addresses = loadData<AddressesData>('account/addresses.json');
const gold = profile.responses.gold;
const goldUser = gold.user as Record<string, string>;

/**
 * Trang hồ sơ: luôn vào qua menu tài khoản (mở trực tiếp /profile bị crash - xem account.spec.ts).
 * Dữ liệu GET được mock bằng JSON trong test-data/account; mọi request ghi đều mock + kiểm tra payload.
 */
test.describe('Hồ sơ cá nhân', () => {
  test.use({ storageState: AUTH_FILES.customer });
  test.skip(() => !hasCustomerAuth(), 'Chưa có tài khoản test (xem .env)');

  test('[ACC-PRF-R01] Dữ liệu thật: hồ sơ hiển thị email tài khoản test', async ({ k }) => {
    await k.account.openProfileFromMenu();
    await k.account.verifyProfileFields({ Email: env.customer.email });
  });

  test.describe('Hiển thị thông tin tài khoản (data-driven)', () => {
    for (const c of profile.display) {
      test(caseTitle(c), async ({ k }) => {
        applyCaseMeta(c);
        await mockAccountData(k, { profile: profile.responses[c.response] });
        await k.account.openProfileFromMenu();
        await k.account.verifyProfileFields(c.expected);
      });
    }
  });

  test.describe('Chỉnh sửa hồ sơ', () => {
    test.beforeEach(async ({ k }) => {
      await mockAccountData(k, { profile: gold });
    });

    for (const c of profile.edit) {
      test(caseTitle(c), async ({ k }) => {
        applyCaseMeta(c);
        await k.common.mockWrite('PUT', API.profile, { success: true, user: { ...goldUser, ...c.expectedBody } });
        await k.account.openProfileFromMenu();
        await k.account.startEditProfile();
        await k.account.fillProfileForm(c.form);
        await k.account.saveProfile();
        await k.common.verifyRequest('PUT', '/api/profile', c.expectedBody);
        await k.account.verifyProfileEditing(false);
        await k.account.verifyProfileFields(c.expectedView);
      });
    }

    test(caseTitle(profile.editServerError), async ({ k }) => {
      const c = profile.editServerError;
      applyCaseMeta(c);
      await k.common.mockWrite('PUT', API.profile, { success: false, message: c.message }, c.status);
      await k.account.openProfileFromMenu();
      await k.account.startEditProfile();
      await k.account.fillProfileForm(c.form);
      await k.account.saveProfile();
      await k.common.verifyRequest('PUT', '/api/profile', { name: c.form.name });
      await k.common.verifyTextVisible(c.message);
    });

    test('[ACC-PRF-E04] Form sửa điền sẵn dữ liệu hiện tại, ô Email bị khóa', async ({ k }) => {
      await k.account.openProfileFromMenu();
      await k.account.startEditProfile();
      await k.account.verifyProfileEditing(true);
      await k.account.verifyProfileEmailLocked(goldUser.email);
      await k.account.verifyProfileForm({
        name: goldUser.name,
        phone: goldUser.phone,
        birthDate: goldUser.birthDate,
        gender: goldUser.gender,
      });
    });

    test('[ACC-PRF-E05] Hủy sửa: không gửi request, giữ nguyên thông tin, mở lại form thấy giá trị cũ', async ({ k }) => {
      await k.common.mockWrite('PUT', API.profile, gold);
      await k.account.openProfileFromMenu();
      await k.account.startEditProfile();
      await k.account.fillProfileForm({ name: 'Tên Sẽ Bị Hủy', phone: '0999999999' });
      await k.account.cancelEditProfile();
      await k.account.verifyProfileEditing(false);
      await k.common.verifyNoRequest('PUT', '/api/profile');
      await k.account.verifyProfileFields({ 'Họ và tên': goldUser.name, 'Số điện thoại': goldUser.phone });
      await k.account.startEditProfile();
      await k.account.verifyProfileForm({ name: goldUser.name, phone: goldUser.phone });
    });
  });

  test.describe('Đổi mật khẩu', () => {
    test.beforeEach(async ({ k }) => {
      await mockAccountData(k, { profile: gold });
      await k.account.openProfileFromMenu();
    });

    test.describe('Validate phía client (data-driven)', () => {
      for (const c of profile.password.validation) {
        test(caseTitle(c), async ({ k }) => {
          applyCaseMeta(c);
          await k.common.mockWrite('PUT', API.changePassword, { success: true });
          await k.account.openChangePassword();
          await k.account.fillChangePassword(c.form);
          await k.account.submitChangePassword();
          await k.account.verifyChangePasswordError(c.error);
          await k.common.verifyNoRequest('PUT', '/api/profile/change-password');
        });
      }
    });

    test.describe('Lỗi từ server (mock, data-driven)', () => {
      for (const c of profile.password.serverErrors) {
        test(caseTitle(c), async ({ k }) => {
          applyCaseMeta(c);
          await k.common.mockWrite('PUT', API.changePassword, { success: false, message: c.message }, c.status);
          await k.account.openChangePassword();
          await k.account.fillChangePassword(c.form);
          await k.account.submitChangePassword();
          await k.common.verifyRequest('PUT', '/api/profile/change-password', {
            currentPassword: c.form.currentPassword,
            newPassword: c.form.newPassword,
          });
          await k.account.verifyChangePasswordError(c.message);
        });
      }
    });

    test('[ACC-PWD-01] Đổi mật khẩu thành công: gửi đúng payload và đóng modal @smoke', async ({ k }) => {
      const form = profile.password.success;
      await k.common.mockWrite('PUT', API.changePassword, { success: true, message: 'Đổi mật khẩu thành công' });
      await k.account.openChangePassword();
      await k.account.verifyChangePasswordFormEmpty();
      await k.account.fillChangePassword(form);
      await k.account.submitChangePassword();
      await k.common.verifyRequest('PUT', '/api/profile/change-password', {
        currentPassword: form.currentPassword,
        newPassword: form.newPassword,
      });
      await k.account.verifyChangePasswordClosed();
    });

    test('[ACC-PWD-02] Nút Đóng và nút Hủy đều đóng modal, không gửi request', async ({ k }) => {
      await k.common.mockWrite('PUT', API.changePassword, { success: true });
      await k.account.openChangePassword();
      await k.account.closeChangePassword();
      await k.account.verifyChangePasswordClosed();
      await k.account.openChangePassword();
      await k.account.fillChangePassword(profile.password.success);
      await k.account.cancelChangePassword();
      await k.account.verifyChangePasswordClosed();
      await k.common.verifyNoRequest('PUT', '/api/profile/change-password');
    });

    test('[ACC-PWD-03] Mở lại modal sau khi Hủy thì form trống, không còn lỗi cũ', async ({ k }) => {
      test.fail(
        true,
        'BUG: ProfilePage.jsx:33-37 - PasswordModal luôn được mount, state form/error giữ nguyên khi đóng (chỉ reset sau khi đổi thành công) -> mở lại vẫn thấy mật khẩu cũ và lỗi cũ',
      );
      await k.account.openChangePassword();
      await k.account.fillChangePassword(profile.password.validation[1].form);
      await k.account.submitChangePassword();
      await k.account.verifyChangePasswordError(profile.password.validation[1].error);
      await k.account.cancelChangePassword();
      await k.account.openChangePassword();
      await k.account.verifyChangePasswordFormEmpty();
    });
  });

  test.describe('Tổng quan tài khoản', () => {
    test('[ACC-PRF-S01] Thống kê, đơn gần đây, yêu thích gần đây, địa chỉ mặc định @smoke', async ({ k }) => {
      await mockAccountData(k, {
        profile: gold,
        orders: orders.list,
        wishlist: wishlist.response,
        addresses: addresses.list,
      });
      await k.account.openProfileFromMenu();
      await k.account.verifyProfileSummary(profile.summary);
      await k.account.verifyRecentOrders(profile.recentOrders);
      await k.account.verifyRecentFavorites(profile.recentFavorites);
      await k.account.verifyDefaultAddress(profile.defaultAddressText);
    });

    test('[ACC-PRF-S02] Tài khoản chưa có dữ liệu: thống kê 0 và các thông báo trống', async ({ k }) => {
      await mockAccountData(k, { profile: profile.responses.basic });
      await k.account.openProfileFromMenu();
      await k.account.verifyProfileSummary({ 'Tổng đơn hàng': '0', 'Đơn đang xử lý': '0', 'Sản phẩm yêu thích': '0' });
      await k.account.verifyRecentOrders([]);
      await k.account.verifyRecentFavorites([]);
      await k.account.verifyDefaultAddress(['Bạn chưa cập nhật địa chỉ giao hàng']);
    });

    test('[ACC-PRF-S03] Tổng đơn hàng đếm đủ mọi đơn (tài khoản có 12 đơn)', async ({ k }) => {
      test.fail(
        true,
        'BUG: ProfilePage.jsx:185 chỉ lấy 10 đơn (limit 10) và ProfileSummary.jsx:22 đếm orders.length thay vì pagination.total -> "Tổng đơn hàng" tối đa là 10',
      );
      await mockAccountData(k, { profile: gold, orders: orders.profileFirstPage });
      await k.account.openProfileFromMenu();
      await k.account.verifyProfileSummary({ 'Tổng đơn hàng': orders.profileTotalOrders });
    });

    test('[ACC-PRF-S04] Nút Cập nhật địa chỉ dẫn tới sổ địa chỉ', async ({ k }) => {
      await mockAccountData(k, { profile: gold, addresses: addresses.list });
      await k.account.openProfileFromMenu();
      await k.account.clickUpdateAddress();
      await k.account.verifyAddressList(addresses.names);
    });
  });
});
