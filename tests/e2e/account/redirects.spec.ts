import { test } from '@fixtures';
import { env } from '@config/env';
import { loadData } from '@data/loader';
import type { RedirectsData } from '@data/account.types';
import { applyCaseMeta, caseTitle } from '@engine/cases';

const data = loadData<RedirectsData>('account/redirects.json');

/** Chưa đăng nhập (không dùng storageState): các trang tài khoản phải chuyển về /login. */
test.describe('Chuyển hướng trang tài khoản khi chưa đăng nhập', () => {
  test.describe('Trang cần đăng nhập (data-driven)', () => {
    for (const c of data.protectedRoutes) {
      test(caseTitle(c), async ({ k }) => {
        applyCaseMeta(c);
        await k.common.goto(c.path);
        await k.common.verifyUrl(c.expected);
      });
    }
  });

  test(caseTitle(data.loginReturn), async ({ k }) => {
    const c = data.loginReturn;
    applyCaseMeta(c);
    await k.cart.seedCart([c.cartItem]);
    await k.checkout.openCheckout();
    await k.account.goToLoginFromCheckout();
    await k.auth.login(env.customer.email, env.customer.password);
    await k.common.verifyUrl(c.expected);
  });
});
