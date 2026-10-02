import { test } from '@fixtures';
import { buildCustomer } from '@data/factories';
import { baseContext, loadData, resolveData } from '@data/loader';
import type { RegisterData } from '@data/types';
import { applyCaseMeta, caseTitle } from '@engine/cases';

const data = loadData<RegisterData>('auth/register.json');

test.describe('Đăng ký tài khoản', () => {
  test.beforeEach(async ({ k }) => {
    await k.auth.openLogin();
    await k.auth.openRegisterForm();
  });

  test('Chuyển qua lại giữa Đăng nhập và Đăng ký', async ({ k, loginPage }) => {
    await test.expect(loginPage.nameInput).toBeVisible();
    await loginPage.switchToLogin.click();
    await test.expect(loginPage.heading).toHaveText('Đăng nhập');
    await test.expect(loginPage.nameInput).toBeHidden();
    await k.auth.openRegisterForm();
  });

  test.describe('Validate form (data-driven)', () => {
    for (const raw of data.validation) {
      test(caseTitle(raw), async ({ k }) => {
        applyCaseMeta(raw);
        const c = resolveData(raw, baseContext());
        await k.auth.submitRegisterForm(c.form);
        await k.auth.verifyFieldErrors(c.errors);
      });
    }
  });

  test.describe('Lỗi từ server (mock, data-driven)', () => {
    for (const c of data.serverErrors) {
      test(caseTitle(c), async ({ k }) => {
        applyCaseMeta(c);
        await k.auth.mockRegisterError(c.status, c.message);
        await k.auth.submitRegisterForm(buildCustomer());
        await k.auth.verifyGeneralError(c.message);
      });
    }
  });

  test('Đăng ký thành công tạo tài khoản thật', async ({ k }) => {
    applyCaseMeta({ id: 'REG-OK', title: '', requires: ['allowWrite'] });
    await k.auth.submitRegisterForm(buildCustomer());
    await k.common.verifyUrl('/profile');
  });
});
