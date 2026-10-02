import { test } from '@fixtures';
import { AUTH_FILES } from '@config/env';
import { loadData } from '@data/loader';
import type { SettingsData } from '@data/admin-ops.types';
import { applyCaseMeta, caseTitle } from '@engine/cases';
import { hasAdminAuth } from '@utils/storage';

const d = loadData<SettingsData>('admin-ops/settings.json');
const API = '**/api/admin/settings';

test.describe('Quản trị - Cài đặt', () => {
  test.use({ storageState: AUTH_FILES.admin });
  test.skip(() => !hasAdminAuth(), 'Cần E2E_ADMIN_EMAIL/PASSWORD trong .env');

  test.describe('Các tab và ô nhập (data-driven, dữ liệu thật)', () => {
    for (const c of d.tabs) {
      test(caseTitle(c), async ({ k }) => {
        applyCaseMeta(c);
        await k.adminOps.openSettings();
        await k.adminOps.openSettingsTab(c.tab);
        await k.adminOps.verifySettingsFields(c.labels);
      });
    }
  });

  test(caseTitle(d.loaded), async ({ k }) => {
    applyCaseMeta(d.loaded);
    await k.adminOps.mockSettings(d.mock);
    await k.adminOps.openSettings();
    for (const [label, value] of Object.entries(d.loaded.fields)) await k.admin.verifyFieldValue(label, value);
    await k.adminOps.openSettingsTab('Bán hàng');
    await k.adminOps.verifyCheckboxes(d.loaded.checkboxes);
  });

  test('[ADO-SET-03] API lỗi -> toast "Không thể tải cấu hình website."', async ({ k }) => {
    await k.common.mockGet(API, { success: false }, 500);
    await k.adminOps.openSettings();
    await k.common.verifyToast('Không thể tải cấu hình website.');
  });

  test.describe('Kiểm tra dữ liệu trước khi lưu (data-driven)', () => {
    for (const c of d.validation) {
      test(caseTitle(c), async ({ k }) => {
        applyCaseMeta(c);
        await k.common.mockWrite('PUT', API, { success: true });
        await k.adminOps.mockSettings(d.mock);
        await k.adminOps.openSettings();
        await k.admin.fillForm(c.form);
        await k.adminOps.saveSettings();
        await k.common.verifyToast(c.toast);
        await k.common.verifyNoRequest('PUT', '/admin/settings');
      });
    }
  });

  test(caseTitle(d.save), async ({ k }) => {
    applyCaseMeta(d.save);
    await k.common.mockWrite('PUT', API, { success: true });
    await k.adminOps.mockSettings(d.mock);
    await k.adminOps.openSettings();
    for (const step of d.save.steps) {
      await k.adminOps.openSettingsTab(step.tab);
      await k.admin.fillForm(step.form);
    }
    await k.adminOps.saveSettings();
    await k.common.verifyRequest('PUT', '/admin/settings', d.save.expectedPayload);
    await k.common.verifyToast(d.save.toast);
  });

  test(caseTitle(d.serverError), async ({ k }) => {
    applyCaseMeta(d.serverError);
    await k.common.mockWrite('PUT', API, { success: false, message: d.serverError.message }, d.serverError.status);
    await k.adminOps.mockSettings(d.mock);
    await k.adminOps.openSettings();
    await k.adminOps.saveSettings();
    await k.common.verifyToast(d.serverError.message);
  });
});
