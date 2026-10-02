import { test } from '@fixtures';
import { env } from '@config/env';
import { baseContext, loadData, resolveData } from '@data/loader';
import type { LoginData } from '@data/types';
import { applyCaseMeta, caseTitle } from '@engine/cases';

const data = loadData<LoginData>('auth/login.json');

test.describe('Đăng nhập khách hàng', () => {
  test.beforeEach(async ({ k }) => {
    await k.auth.openLogin();
  });

  test.describe('Validate form (data-driven)', () => {
    for (const c of data.validation) {
      test(caseTitle(c), async ({ k }) => {
        applyCaseMeta(c);
        await k.auth.login(c.identifier, c.password);
        await k.auth.verifyFieldErrors(c.errors);
      });
    }
  });

  test.describe('Lỗi từ server (data-driven)', () => {
    for (const raw of data.wrongCredentials) {
      test(caseTitle(raw), async ({ k }) => {
        applyCaseMeta(raw);
        const c = resolveData(raw, baseContext());
        await k.auth.loginExpectingError(c.identifier, c.password, c.error);
      });
    }
  });

  test('Lỗi field biến mất khi người dùng nhập lại', async ({ k, loginPage }) => {
    const [first] = data.validation;
    await k.auth.login(first.identifier, first.password);
    await k.auth.verifyFieldErrors(first.errors);

    await loginPage.identifierInput.fill('a');
    await test.expect(loginPage.fieldError(first.errors[0])).toBeHidden();
  });

  test('Nút hiện/ẩn mật khẩu', async ({ k, loginPage }) => {
    await loginPage.passwordInput.fill('secret123');
    await k.auth.togglePassword(true);
    await k.auth.togglePassword(false);
  });

  test('Đăng nhập thành công (mock API) chuyển tới trang hồ sơ', async ({ k }) => {
    await k.auth.mockLoginSuccess(data.mockUser);
    await k.auth.login(data.mockUser.email, 'matkhau123');
    await k.common.verifyUrl('/profile');
    await k.auth.verifyStoredToken('mock-token');
  });

  test('Đăng nhập thành công với tài khoản thật @smoke', async ({ k }) => {
    applyCaseMeta({ id: 'LOGIN-OK', title: '', requires: ['customer'] });
    await k.auth.login(env.customer.email, env.customer.password);
    await k.common.verifyUrl('/profile');
    await k.auth.verifyLoggedInAs(env.customer.email);
  });
});
