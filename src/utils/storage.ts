import fs from 'node:fs';
import { Page } from '@playwright/test';
import { env, AUTH_FILES } from '@config/env';
import type { CartItem } from '@data/factories';

/** Key localStorage mà frontend đang dùng (xem src/contexts/*.jsx của app). */
export const STORAGE_KEYS = {
  cart: 'clothing_store_cart',
  customerToken: 'clothing_store_token',
  customerUser: 'clothing_store_auth',
  adminToken: 'admin_token',
} as const;

type StorageState = {
  cookies: [];
  origins: { origin: string; localStorage: { name: string; value: string }[] }[];
};

/** Tạo file storageState của Playwright trực tiếp từ các cặp key/value localStorage. */
export function writeStorageState(file: string, entries: Record<string, string>) {
  const state: StorageState = {
    cookies: [],
    origins: Object.keys(entries).length
      ? [
          {
            origin: new URL(env.baseURL).origin,
            localStorage: Object.entries(entries).map(([name, value]) => ({ name, value })),
          },
        ]
      : [],
  };
  fs.writeFileSync(file, JSON.stringify(state, null, 2));
}

function hasKey(file: string, key: string) {
  try {
    const state: StorageState = JSON.parse(fs.readFileSync(file, 'utf8'));
    return state.origins.some((o) => o.localStorage.some((e) => e.name === key && e.value));
  } catch {
    return false;
  }
}

export const hasCustomerAuth = () => hasKey(AUTH_FILES.customer, STORAGE_KEYS.customerToken);
export const hasAdminAuth = () => hasKey(AUTH_FILES.admin, STORAGE_KEYS.adminToken);

/**
 * Đặt sẵn giỏ hàng vào localStorage TRƯỚC khi app load (chỉ ở lần điều hướng đầu tiên,
 * các lần reload sau giữ nguyên giỏ hàng do app tự lưu).
 */
export async function seedCart(page: Page, items: CartItem[]) {
  await page.addInitScript(
    ({ key, value }) => {
      if (!sessionStorage.getItem('__e2e_cart_seeded')) {
        localStorage.setItem(key, value);
        sessionStorage.setItem('__e2e_cart_seeded', '1');
      }
    },
    { key: STORAGE_KEYS.cart, value: JSON.stringify(items) },
  );
}

export async function readCart(page: Page): Promise<CartItem[]> {
  return page.evaluate((key) => JSON.parse(localStorage.getItem(key) || '[]'), STORAGE_KEYS.cart);
}

/**
 * Trả về promise -> true nếu trang bị điều hướng/reload trong `timeout` ms kể từ lúc gọi.
 * Dùng để bắt lỗi app reload làm mất trạng thái (vd: thông báo lỗi đăng nhập).
 */
export function detectReload(page: Page, timeout = 3_000): Promise<boolean> {
  return page.waitForEvent('framenavigated', { timeout }).then(
    () => true,
    () => false,
  );
}
