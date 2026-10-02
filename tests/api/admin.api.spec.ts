import { test, expect } from '@fixtures';
import { env } from '@config/env';
import { loadData } from '@data/loader';
import type { DataCase } from '@data/types';
import { applyCaseMeta, caseTitle } from '@engine/cases';

interface AdminApiData {
  readEndpoints: (DataCase & { path: string; keys: string[] })[];
  detailEndpoints: (DataCase & { list: string; listKey: string; detail: string; key: string })[];
  notFound: (DataCase & { path: string })[];
}

const data = loadData<AdminApiData>('api/admin.json');

test.describe('API admin (đã đăng nhập, chỉ đọc) @api', () => {
  test.skip(!env.admin.email, 'Cần E2E_ADMIN_EMAIL/PASSWORD');

  let headers: Record<string, string>;
  test.beforeAll(async ({ playwright }) => {
    const request = await playwright.request.newContext();
    const res = await request.post(`${env.apiURL}/admin/login`, {
      data: { email: env.admin.email, password: env.admin.password },
    });
    headers = { Authorization: `Bearer ${(await res.json()).token}` };
    await request.dispose();
  });

  test.describe('Danh sách / thống kê (data-driven)', () => {
    for (const c of data.readEndpoints) {
      test(`${caseTitle(c)} - GET ${c.path}`, async ({ api }) => {
        applyCaseMeta(c);
        const res = await api.get(c.path, { headers });
        await expect(res).toBeOK();
        const body = await res.json();
        for (const key of c.keys) expect(body, `thiếu trường "${key}"`).toHaveProperty(key);
      });
    }
  });

  test.describe('Chi tiết theo id (data-driven)', () => {
    for (const c of data.detailEndpoints) {
      test(caseTitle(c), async ({ api }) => {
        applyCaseMeta(c);
        const list = await (await api.get(c.list, { headers })).json();
        const first = list[c.listKey]?.[0];
        test.skip(!first, `Chưa có dữ liệu ${c.listKey} để kiểm tra`);

        const res = await api.get(c.detail.replace('{id}', String(first.id)), { headers });
        await expect(res).toBeOK();
        const body = await res.json();
        expect(body[c.key]?.id).toBe(first.id);
      });
    }
  });

  test.describe('Id không tồn tại (data-driven)', () => {
    for (const c of data.notFound) {
      test(`${caseTitle(c)} - GET ${c.path}`, async ({ api }) => {
        applyCaseMeta(c);
        const res = await api.get(c.path, { headers });
        expect(res.status()).toBe(404);
        expect((await res.json()).success).toBe(false);
      });
    }
  });
});

test.describe('API admin - bảo mật upload @api @security', () => {
  // routes/admin.js khai báo POST /upload TRƯỚC router.use(authMiddleware) -> ai cũng upload được.
  test('POST /admin/upload không có token phải trả 401', async ({ api }) => {
    const res = await api.post('/admin/upload');
    expect(res.status(), 'Endpoint upload xử lý request không cần đăng nhập').toBe(401);
  });
});
