import { test, expect } from '@fixtures';

test.describe('API - Sản phẩm @api', () => {
  test('GET /products trả danh sách + phân trang', async ({ api }) => {
    const res = await api.get('/products?limit=5&page=1');
    await expect(res).toBeOK();
    const { success, data } = await res.json();

    expect(success).toBe(true);
    expect(data.products.length).toBeLessThanOrEqual(5);
    expect(data.pagination).toMatchObject({ page: 1, limit: 5 });
    for (const p of data.products) {
      expect(p).toEqual(
        expect.objectContaining({ id: expect.anything(), name: expect.any(String), slug: expect.any(String) }),
      );
    }
  });

  test('GET /products/:slug trả chi tiết có sizes/colors/variants', async ({ api }) => {
    const [first] = await api.listProducts({ limit: 1 });
    test.skip(!first, 'DB chưa có sản phẩm');

    const detail = await api.getProduct(first.slug);
    expect(detail.slug).toBe(first.slug);
    expect(Array.isArray(detail.sizes)).toBe(true);
    expect(Array.isArray(detail.colors)).toBe(true);
    expect(Array.isArray(detail.variants)).toBe(true);
  });

  test('GET /products/:slug không tồn tại trả 404', async ({ api }) => {
    const res = await api.get('/products/san-pham-khong-ton-tai-e2e-999');
    expect(res.status()).toBe(404);
  });

  test('GET /products/search tìm theo từ khóa', async ({ api }) => {
    const [first] = await api.listProducts({ limit: 1 });
    test.skip(!first, 'DB chưa có sản phẩm');

    const keyword = first.name.split(' ')[0];
    const res = await api.get(`/products/search?q=${encodeURIComponent(keyword)}`);
    await expect(res).toBeOK();
    const body = await res.json();
    const products = body.data?.products ?? body.data ?? [];
    expect(products.length).toBeGreaterThan(0);
  });

  test('GET /products/kids, /kids-categories hoạt động', async ({ api }) => {
    for (const path of ['/products/kids', '/products/kids-categories']) {
      const res = await api.get(path);
      expect(res.status(), path).toBe(200);
    }
  });

  test('GET /products/suggested (gợi ý trong giỏ hàng) trả 200', async ({ api }) => {
    test.fail(true, 'BUG: query dùng hàm HEX() của MySQL trên Postgres -> 500 "function hex(character varying) does not exist"');
    const res = await api.get('/products/suggested?limit=6');
    expect(res.status()).toBe(200);
  });

  test('GET /news trả danh sách bài viết đã publish', async ({ api }) => {
    const res = await api.get('/news?limit=3');
    await expect(res).toBeOK();
    const body = await res.json();
    expect(body.success).toBe(true);
    expect(body.news.length).toBeLessThanOrEqual(3);
  });
});
