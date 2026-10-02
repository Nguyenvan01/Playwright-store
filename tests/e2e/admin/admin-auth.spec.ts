import { test } from '@fixtures';
import { MSG } from '@data/messages';
import { applyCaseMeta } from '@engine/cases';

test.describe('Đăng nhập trang quản trị', () => {
  test('Chưa đăng nhập vào /admin bị chuyển về /admin/login @smoke', async ({ k }) => {
    await k.common.goto('/admin/products');
    await k.admin.verifyOnAdminLogin();
  });

  test('Sai mật khẩu hiển thị lỗi', async ({ k }) => {
    test.fail(true, 'BUG: interceptor 401 trong services/api.js reload sang /admin/login nên thông báo lỗi bị mất');
    await k.admin.openAdminLogin();
    await k.admin.loginAdminExpectingError('admin@clothing-store.vn', 'sai-mat-khau-e2e', MSG.login.wrongCredentials);
  });

  test('Link "Quay về cửa hàng" về trang chủ', async ({ k }) => {
    await k.admin.openAdminLogin();
    await k.admin.backToStore();
    await k.common.verifyUrl('/');
  });

  test('Đăng nhập thành công vào Dashboard', async ({ k }) => {
    applyCaseMeta({ id: 'ADM-OK', title: '', requires: ['admin'] });
    await k.admin.loginAsAdmin();
    await k.admin.verifyAdminPage('/admin');
  });
});
