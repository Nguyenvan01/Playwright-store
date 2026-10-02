import { test, expect } from '@fixtures';
import { loadData } from '@data/loader';
import type { DataCase } from '@data/types';
import { applyCaseMeta, caseTitle } from '@engine/cases';

interface PublicApiData {
  sorting: (DataCase & { query: string; order: 'asc' | 'desc' })[];
  filters: (DataCase & { query: string; field: string; equals: string })[];
  validation: (DataCase & { path: string; status: number; message?: string })[];
}

const data = loadData<PublicApiData>('api/public.json');

test.describe('API công khai - sắp xếp (data-driven) @api', () => {
  for (const c of data.sorting) {
    test(caseTitle(c), async ({ api }) => {
      applyCaseMeta(c);
      const res = await api.get(`/products?${c.query}`);
      await expect(res).toBeOK();
      const prices = (await res.json()).data.products.map((p: { price: string | number }) => Number(p.price));
      const sorted = [...prices].sort((a, b) => (c.order === 'asc' ? a - b : b - a));
      expect(prices).toEqual(sorted);
    });
  }
});

test.describe('API công khai - bộ lọc (data-driven) @api', () => {
  for (const c of data.filters) {
    test(caseTitle(c), async ({ api }) => {
      applyCaseMeta(c);
      const res = await api.get(`/products?${c.query}`);
      await expect(res).toBeOK();
      const products: Record<string, unknown>[] = (await res.json()).data.products;
      test.skip(products.length === 0, 'Không có dữ liệu để kiểm tra bộ lọc');
      for (const p of products) expect(p[c.field], `${p.slug}`).toBe(c.equals);
    });
  }

  test('[API-PUB-P01] Duyệt hết các trang: đủ sản phẩm, không trùng', async ({ api }) => {
    test.fail(true, 'BUG: ORDER BY created_at không có cột phụ (id) -> sản phẩm trùng/thiếu giữa các trang');
    const limit = 5;
    const first = await (await api.get(`/products?limit=${limit}&page=1`)).json();
    const { total, total_pages } = first.data.pagination;
    const seen: number[] = [];
    for (let page = 1; page <= total_pages; page++) {
      seen.push(...(await api.listProducts({ limit, page })).map((p) => p.id));
    }
    expect(new Set(seen).size, `Thấy ${new Set(seen).size}/${total} sản phẩm, ${seen.length - new Set(seen).size} bị trùng`).toBe(total);
  });
});

test.describe('API công khai - validate tham số (data-driven) @api', () => {
  for (const c of data.validation) {
    test(caseTitle(c), async ({ api }) => {
      applyCaseMeta(c);
      const res = await api.get(c.path);
      expect(res.status()).toBe(c.status);
      if (c.message) expect((await res.json()).message).toBe(c.message);
    });
  }
});
