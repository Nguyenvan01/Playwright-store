import { test } from '@fixtures';
import { AUTH_FILES } from '@config/env';
import { loadData } from '@data/loader';
import type { WishlistData } from '@data/account.types';
import { applyCaseMeta, caseTitle } from '@engine/cases';
import { hasCustomerAuth } from '@utils/storage';
import { API } from './support';

const data = loadData<WishlistData>('account/wishlist.json');

/** Trang /favorites. App không có UI thêm yêu thích -> danh sách lấy từ mock GET /api/wishlist. */
test.describe('Danh sách yêu thích', () => {
  test.use({ storageState: AUTH_FILES.customer });
  test.skip(() => !hasCustomerAuth(), 'Chưa có tài khoản test (xem .env)');

  test('[ACC-WL-E01] Chưa có sản phẩm yêu thích: thông báo trống, 0 sản phẩm', async ({ k }) => {
    await k.common.mockGet(API.wishlist, data.empty);
    await k.account.openWishlist();
    await k.account.verifyWishlistEmpty();
  });

  test('[ACC-WL-H01] Bấm trái tim trên trang danh mục lưu sản phẩm vào yêu thích', async ({ k }) => {
    test.fail(
      true,
      'BUG: MenPage.jsx:391 (và KidsPage.jsx:347) - nút trái tim không có onClick, nằm trong <Link>; không nơi nào gọi POST /api/wishlist nên khách không thể thêm yêu thích',
    );
    await k.common.mockWrite('POST', API.wishlist, { success: true, message: 'Đã thêm vào danh sách yêu thích' }, 201);
    await k.account.favoriteFromListing(data.heart.listingPath);
    await k.common.verifyRequest('POST', '/api/wishlist');
  });

  test.describe('Có sản phẩm yêu thích', () => {
    test.beforeEach(async ({ k }) => {
      await k.common.mockGet(API.wishlist, data.response);
      await k.account.openWishlist();
      await k.account.verifyWishlistLoaded();
    });

    test('[ACC-WL-01] Hiển thị số lượng và danh sách (mới lưu trước) @smoke', async ({ k }) => {
      await k.account.verifyWishlistCount(data.count);
      await k.account.verifyWishlistProducts(data.recentOrder);
    });

    test.describe('Sắp xếp (data-driven)', () => {
      for (const c of data.sort) {
        test(caseTitle(c), async ({ k }) => {
          applyCaseMeta(c);
          await k.account.sortWishlist(c.sort);
          await k.account.verifyWishlistProducts(c.expected);
        });
      }
    });

    test.describe('Tìm kiếm (data-driven)', () => {
      for (const c of data.search) {
        test(caseTitle(c), async ({ k }) => {
          applyCaseMeta(c);
          await k.account.searchWishlist(c.query);
          if (c.expected.length) await k.account.verifyWishlistProducts(c.expected);
          else await k.account.verifyWishlistNoMatch();
          await k.account.verifyWishlistCount(data.count);
        });
      }
    });

    test.describe('Tình trạng hàng + thông tin thẻ (data-driven)', () => {
      for (const c of data.availability) {
        test(caseTitle(c), async ({ k }) => {
          applyCaseMeta(c);
          await k.account.verifyWishlistItem(c.name, c.texts);
          await k.account.verifyWishlistItemAvailable(c.name, c.available);
        });
      }
    });

    test('[ACC-WL-R01] Bỏ yêu thích: gửi DELETE đúng sản phẩm, cập nhật danh sách và số lượng', async ({ k }) => {
      const r = data.remove;
      await k.common.mockWrite('DELETE', API.wishlistItem, { success: true, message: 'Đã xóa khỏi danh sách yêu thích' });
      await k.account.removeFromWishlist(r.name);
      await k.common.verifyRequest('DELETE', `/api/wishlist/${r.productId}`);
      await k.account.verifyWishlistProducts(r.remaining);
      await k.account.verifyWishlistCount(r.remaining.length);
    });

    test('[ACC-WL-R02] Bỏ yêu thích thất bại: sản phẩm được khôi phục', async ({ k }) => {
      const r = data.remove;
      await k.common.mockWrite('DELETE', API.wishlistItem, r.errorResponse, r.errorStatus);
      await k.account.removeFromWishlist(r.name);
      await k.common.verifyRequest('DELETE', `/api/wishlist/${r.productId}`);
      await k.account.verifyWishlistProducts(data.recentOrder);
      await k.account.verifyWishlistCount(data.count);
    });

    test('[ACC-WL-C01] Thêm vào giỏ sản phẩm không có biến thể: toast + giỏ có 1 sản phẩm', async ({ k }) => {
      await k.account.addWishlistItemToCart(data.addSimple.name);
      await k.common.verifyToast(data.addSimple.toast);
      await k.cart.verifyStoredItemCount(1);
      await k.cart.verifyCartBadge(1);
    });

    test('[ACC-WL-C02] Thêm vào giỏ sản phẩm có biến thể: chuyển sang trang sản phẩm để chọn size', async ({ k }) => {
      await k.account.addWishlistItemToCart(data.addWithVariants.name);
      await k.common.verifyUrl(`/product/${data.addWithVariants.slug}`);
      await k.cart.verifyStoredItemCount(0);
    });
  });
});
