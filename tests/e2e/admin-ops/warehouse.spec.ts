import { test } from '@fixtures';
import { AUTH_FILES } from '@config/env';
import { loadData } from '@data/loader';
import type { WarehouseData } from '@data/admin-ops.types';
import { applyCaseMeta, caseTitle } from '@engine/cases';
import { hasAdminAuth } from '@utils/storage';

const d = loadData<WarehouseData>('admin-ops/warehouse.json');
const SEARCH = 'Tìm kiếm sản phẩm, SKU, danh mục...';

test.describe('Quản trị - Kho hàng', () => {
  test.use({ storageState: AUTH_FILES.admin });
  test.skip(() => !hasAdminAuth(), 'Cần E2E_ADMIN_EMAIL/PASSWORD trong .env');

  test('[ADO-WH-01] Dữ liệu thật: thẻ thống kê, đủ cột, có sản phẩm @smoke', async ({ k }) => {
    await k.adminOps.openWarehouse();
    for (const label of d.statLabels) await k.common.verifyTextVisible(label);
    await k.adminOps.verifyColumns(d.headers);
    await k.adminOps.verifyRowsAtLeast(1);
    await k.common.verifyNoPageErrors();
  });

  test(caseTitle(d.realStats), async ({ k }) => {
    applyCaseMeta(d.realStats);
    await k.adminOps.openWarehouse();
    await k.adminOps.verifyWarehouseStatsMatchList();
  });

  test('[ADO-WH-02] Thẻ thống kê hiển thị đúng số liệu API', async ({ k }) => {
    await k.adminOps.mockWarehouse(d.mock);
    await k.adminOps.openWarehouse();
    await k.adminOps.verifyStatCards(d.statCards);
    await k.adminOps.verifyListQuery('/admin/warehouse', { filter: 'all' });
    await k.adminOps.verifyRowCount(d.mock.products.length);
  });

  test.describe('Hiển thị dòng (data-driven)', () => {
    for (const c of d.rows) {
      test(caseTitle(c), async ({ k }) => {
        applyCaseMeta(c);
        await k.adminOps.mockWarehouse(d.mock);
        await k.adminOps.openWarehouse();
        await k.adminOps.verifyRowCells(c.rowText, c.expected);
      });
    }
  });

  test.describe('Tab lọc tồn kho (data-driven)', () => {
    for (const c of d.tabs) {
      test(caseTitle(c), async ({ k }) => {
        applyCaseMeta(c);
        await k.adminOps.mockWarehouse(d.mock);
        await k.adminOps.openWarehouse();
        if (c.tab === 'Tất cả') await k.adminOps.selectWarehouseTab('Hết hàng');
        await k.adminOps.selectWarehouseTab(c.tab);
        await k.adminOps.verifyListQuery('/admin/warehouse', { filter: c.filter });
        await k.adminOps.verifyRowCount(c.visible.length);
        await k.adminOps.verifyVisibleRows(c.visible, c.hidden);
      });
    }
  });

  test.describe('Tìm kiếm (data-driven)', () => {
    for (const c of d.search) {
      test(caseTitle(c), async ({ k }) => {
        applyCaseMeta(c);
        await k.adminOps.mockWarehouse(d.mock);
        await k.adminOps.openWarehouse();
        await k.admin.searchList(SEARCH, c.keyword);
        await k.adminOps.verifyVisibleRows(c.visible, c.hidden);
        if (c.emptyText) await k.common.verifyTextVisible(c.emptyText);
      });
    }
  });

  test.describe('Số đếm trên tab (data-driven)', () => {
    for (const c of d.tabBadges) {
      test(caseTitle(c), async ({ k }) => {
        applyCaseMeta(c);
        await k.adminOps.mockWarehouse(d.mock);
        await k.adminOps.openWarehouse();
        await k.adminOps.selectWarehouseTab(c.tab);
        for (const [tab, count] of Object.entries(c.badges)) await k.adminOps.verifyWarehouseTabBadge(tab, count);
      });
    }
  });
});
