import type { Keywords } from '@keywords/index';
import { loadData } from '@data/loader';
import type { ApiRecord } from '@data/account.types';

/** Mẫu URL (glob Playwright) của các API tài khoản. `*` không vượt qua "/". */
export const API = {
  profile: '**/api/profile',
  changePassword: '**/api/profile/change-password',
  /** GET danh sách (có query ?page=&limit=) và POST tạo đơn. */
  orders: '**/api/orders*',
  createOrder: '**/api/orders',
  orderDetail: '**/api/orders/*',
  cancelOrder: '**/api/orders/*/cancel',
  wishlist: '**/api/wishlist',
  wishlistItem: '**/api/wishlist/*',
  addresses: '**/api/addresses',
  address: '**/api/addresses/*',
} as const;

const EMPTY = {
  orders: loadData<ApiRecord>('account/orders.json#empty'),
  wishlist: loadData<ApiRecord>('account/wishlist.json#empty'),
  addresses: loadData<ApiRecord>('account/addresses.json#empty'),
};

/**
 * Mock 4 API mà trang hồ sơ gọi (profile, orders, wishlist, addresses).
 * Không truyền profile -> dùng dữ liệu thật của tài khoản test; các API còn lại mặc định rỗng.
 */
export async function mockAccountData(
  k: Keywords,
  data: { profile?: ApiRecord; orders?: ApiRecord; wishlist?: ApiRecord; addresses?: ApiRecord } = {},
) {
  if (data.profile) await k.common.mockGet(API.profile, data.profile);
  await k.common.mockGet(API.orders, data.orders ?? EMPTY.orders);
  await k.common.mockGet(API.wishlist, data.wishlist ?? EMPTY.wishlist);
  await k.common.mockGet(API.addresses, data.addresses ?? EMPTY.addresses);
}
