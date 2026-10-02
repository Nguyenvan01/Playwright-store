import { test, expect } from '@fixtures';

test.describe('API - Health & Home @api @smoke', () => {
  test('GET /health trả về 200', async ({ api }) => {
    const res = await api.get('/health');
    expect(res.status()).toBe(200);
  });

  test('GET /home trả đủ các khối dữ liệu trang chủ', async ({ api }) => {
    const res = await api.get('/home');
    await expect(res).toBeOK();
    const body = await res.json();
    expect(body.success).toBe(true);
    expect(body.data).toEqual(
      expect.objectContaining({
        banners: expect.any(Array),
        categories: expect.any(Array),
        featuredProducts: expect.any(Array),
      }),
    );
  });

  test('Route không tồn tại trả 404', async ({ api }) => {
    const res = await api.get('/khong-ton-tai-e2e');
    expect(res.status()).toBe(404);
  });
});
