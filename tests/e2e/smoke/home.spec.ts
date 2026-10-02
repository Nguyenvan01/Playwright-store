import { test } from '@fixtures';
import { loadData } from '@data/loader';
import type { CategoryCase, StaticPage } from '@data/types';

const categories = loadData<CategoryCase[]>('catalog/categories.json');
const staticPages = loadData<StaticPage[]>('common/static-pages.json');

test.describe('Trang chủ @smoke', () => {
  test('Tải trang chủ, hiển thị header, sản phẩm và footer', async ({ k }) => {
    await k.catalog.openHome();
    await k.catalog.verifyHomeLoaded();
  });

  test('Không có lỗi JavaScript khi tải trang chủ', async ({ k }) => {
    await k.catalog.openHome();
    await k.common.verifyNoPageErrors();
  });

  test('Thanh điều hướng có đủ danh mục', async ({ k }) => {
    await k.catalog.openHome();
    for (const c of categories) await k.catalog.verifyMenuLink(c.nav, c.path);
  });

  test('Click logo quay về trang chủ', async ({ k }) => {
    await k.common.goto('/about');
    await k.catalog.clickLogo();
    await k.common.verifyUrl('/');
  });

  test('Click sản phẩm đầu tiên mở trang chi tiết', async ({ k }) => {
    await k.catalog.openHome();
    await k.catalog.openFirstProductInList();
  });
});

test.describe('Các trang tĩnh @smoke', () => {
  for (const p of staticPages) {
    test(`${p.title} (${p.path}) tải thành công`, async ({ k }) => {
      await k.common.goto(p.path);
      await k.common.verifyLayoutLoaded();
      await k.common.verifyNoPageErrors();
    });
  }
});
