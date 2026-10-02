import { test } from '@fixtures';
import { loadData } from '@data/loader';
import type { CategoryCase } from '@data/types';

const categories = loadData<CategoryCase[]>('catalog/categories.json');

test.describe('Trang danh mục (data-driven)', () => {
  for (const c of categories) {
    test(`Menu "${c.nav}" mở ${c.path} và hiển thị sản phẩm @smoke`, async ({ k }) => {
      await k.catalog.openHome();
      await k.catalog.openCategoryFromMenu(c.nav);
      await k.catalog.verifyCategoryPage(c.path, c.heading);
    });
  }

  test('Click sản phẩm trong danh mục mở trang chi tiết', async ({ k }) => {
    const c = categories[0];
    await k.common.goto(c.path);
    await k.catalog.verifyCategoryPage(c.path, c.heading);
    await k.catalog.openFirstProductInList();
  });
});
