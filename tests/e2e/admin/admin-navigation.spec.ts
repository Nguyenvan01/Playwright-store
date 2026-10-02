import { test } from '@fixtures';
import { AUTH_FILES } from '@config/env';
import { loadData } from '@data/loader';
import type { AdminMenuItem } from '@data/types';
import { hasAdminAuth } from '@utils/storage';

const menu = loadData<AdminMenuItem[]>('admin/menu.json');

test.describe('Điều hướng trang quản trị (data-driven)', () => {
  test.use({ storageState: AUTH_FILES.admin });
  test.skip(() => !hasAdminAuth(), 'Cần E2E_ADMIN_EMAIL/PASSWORD trong .env');

  for (const item of menu) {
    test(`Menu "${item.label}" mở ${item.path}`, async ({ k }) => {
      await k.admin.openDashboard();
      await k.admin.navigateMenu(item.label);
      await k.admin.verifyAdminPage(item.path);
      await k.common.verifyNoPageErrors();
    });
  }
});
