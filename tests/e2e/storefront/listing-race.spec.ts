import { test, expect } from '@fixtures';
import { ListingPage } from '@pages/storefront/ListingPage';

/**
 * SF-LST-RACE: ô "Từ" và "Đến" mỗi ô gọi API riêng khi blur, app không hủy/bỏ qua response cũ.
 * Mock: request chỉ có min_price trả chậm, request có cả min+max trả ngay -> response cũ về sau ghi đè.
 */
const product = (id: number, price: number) => ({
  id, name: `SP Race ${id}`, slug: `sp-race-${id}`, price, compare_price: null,
  image_url: null, category_slug: 'ao-thun', avg_rating: 0, review_count: 0,
});
const body = (products: ReturnType<typeof product>[]) => ({
  success: true,
  data: { products, pagination: { page: 1, limit: 8, total: products.length, total_pages: 1 } },
});

test('[SF-LST-RACE] Lọc giá: response cũ trả chậm không được ghi đè kết quả mới', async ({ page, k }) => {
  test.fail(true, 'BUG: ProductFilters.jsx handleApply gọi API mỗi lần blur, MenPage không hủy request cũ -> kết quả cũ ghi đè');
  const cheap = product(1, 350000);
  const expensive = product(2, 799000);

  await page.route('**/api/products?*', async (route) => {
    const url = route.request().url();
    if (url.includes('max_price=')) return route.fulfill({ json: body([cheap]) });
    if (url.includes('min_price=')) {
      await new Promise((r) => setTimeout(r, 1500)); // response cũ về chậm
      return route.fulfill({ json: body([cheap, expensive]) });
    }
    return route.fulfill({ json: body([cheap, expensive]) });
  });

  const listing = new ListingPage(page);
  await k.common.goto('/nam');
  await expect(listing.cards).toHaveCount(2);

  // Người dùng nhập liền 2 ô như bình thường
  await listing.priceFrom.fill('300000');
  await listing.priceTo.fill('600000');
  await listing.priceTo.blur();

  // Đợi cả response chậm về, kết quả cuối phải là khoảng 300k-600k (chỉ 1 sản phẩm)
  await page.waitForResponse((r) => r.url().includes('min_price=') && !r.url().includes('max_price='));
  await expect(listing.cards, 'Kết quả bị response cũ ghi đè').toHaveCount(1);
});
