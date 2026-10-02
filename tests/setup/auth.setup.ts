import { test as setup } from '@playwright/test';
import { ApiClient } from '@api/ApiClient';
import { env, AUTH_FILES } from '@config/env';
import { buildCustomer } from '@data/factories';
import { STORAGE_KEYS, writeStorageState } from '@utils/storage';

/**
 * Đăng nhập qua API (nhanh, ổn định) rồi ghi token vào storageState.
 * Test UI cần đăng nhập chỉ việc `test.use({ storageState: AUTH_FILES.customer })`.
 * Nếu không có tài khoản -> ghi state rỗng, các test liên quan sẽ tự skip.
 */
setup('xác thực khách hàng', async ({ request }) => {
  const api = new ApiClient(request);
  let auth;

  if (env.customer.email && env.customer.password) {
    auth = await api.customerLogin(env.customer.email, env.customer.password);
  } else if (env.allowWrite) {
    auth = await api.registerCustomer(buildCustomer());
  } else {
    writeStorageState(AUTH_FILES.customer, {});
    setup.info().annotations.push({
      type: 'skip-reason',
      description: 'Chưa cấu hình E2E_CUSTOMER_EMAIL/PASSWORD và E2E_ALLOW_WRITE=0',
    });
    return;
  }

  writeStorageState(AUTH_FILES.customer, {
    [STORAGE_KEYS.customerToken]: auth.token,
    [STORAGE_KEYS.customerUser]: JSON.stringify(auth.user),
  });
});

setup('xác thực admin', async ({ request }) => {
  if (!env.admin.email || !env.admin.password) {
    writeStorageState(AUTH_FILES.admin, {});
    return;
  }
  const auth = await new ApiClient(request).adminLogin(env.admin.email, env.admin.password);
  writeStorageState(AUTH_FILES.admin, { [STORAGE_KEYS.adminToken]: auth.token });
});
