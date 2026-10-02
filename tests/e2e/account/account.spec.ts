import { test } from '@fixtures';
import { AUTH_FILES, env } from '@config/env';
import { hasCustomerAuth } from '@utils/storage';

test.describe('Tài khoản khách hàng (đã đăng nhập)', () => {
  test.use({ storageState: AUTH_FILES.customer });
  test.skip(() => !hasCustomerAuth(), 'Chưa có tài khoản test (xem .env)');

  test('Mở trực tiếp /profile (F5, bookmark) hiển thị thông tin tài khoản', async ({ k }) => {
    test.fail(true, "BUG: profileToForm(null) ở lần render đầu -> crash 'Cannot read properties of null (reading name)'");
    await k.account.openProfile();
    await k.account.verifyProfileLoaded();
  });

  test('Vào hồ sơ qua menu tài khoản hiển thị thông tin @smoke', async ({ k }) => {
    await k.catalog.openHome();
    await k.account.openAccountMenuLink('Hồ sơ cá nhân');
    await k.common.verifyUrl('/profile');
    await k.account.verifyProfileLoaded();
  });

  test('Vào /login khi đã đăng nhập sẽ chuyển sang /profile', async ({ k }) => {
    await k.common.goto('/login');
    await k.common.verifyUrl('/profile');
  });

  test('Menu tài khoản điều hướng tới Đơn hàng và Yêu thích', async ({ k }) => {
    await k.catalog.openHome();
    await k.auth.verifyLoggedInAs(env.customer.email);
    await k.account.openAccountMenuLink('Đơn hàng của tôi');
    await k.common.verifyUrl('/orders');
    await k.account.verifyOrdersLoaded();
    await k.account.openAccountMenuLink('Yêu thích');
    await k.common.verifyUrl('/favorites');
    await k.account.verifyWishlistLoaded();
  });

  test('Đăng xuất xóa token và về trang chủ', async ({ k }) => {
    await k.catalog.openHome();
    await k.auth.logout();
    await k.auth.verifyLoggedOut();
  });
});

test('Chưa đăng nhập: icon tài khoản dẫn tới trang đăng nhập', async ({ k }) => {
  await k.catalog.openHome();
  await k.account.clickAccountIcon();
  await k.common.verifyUrl('/login');
});
