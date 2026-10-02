import { test } from '@fixtures';
import { loadData } from '@data/loader';
import type { CategoryCase } from '@data/types';

const [firstCategory] = loadData<CategoryCase[]>('catalog/categories.json');

test.describe('Giao diện mobile @mobile', () => {
  test('Trang chủ hiển thị, menu desktop bị ẩn', async ({ k, header }) => {
    await k.catalog.openHome();
    await test.expect(header.logo).toBeVisible();
    await test.expect(header.desktopNav).toBeHidden();
  });

  test('Mở menu mobile và điều hướng tới danh mục', async ({ k }) => {
    test.fail(true, 'BUG: header tràn ngang trên mobile, nút menu nằm ngoài màn hình');
    await k.catalog.openHome();
    await k.catalog.openCategoryFromMobileMenu(firstCategory.nav);
    await k.common.verifyUrl(firstCategory.path);
  });

  test('Không bị tràn ngang trên trang chủ', async ({ k }) => {
    test.fail(true, 'BUG: ô tìm kiếm w-48 cố định làm header rộng hơn màn hình (~64px)');
    await k.catalog.openHome();
    await k.common.verifyNoHorizontalOverflow();
  });
});
