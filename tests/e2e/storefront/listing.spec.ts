import { test } from '@fixtures';
import type { Keywords } from '@keywords/index';
import { loadData } from '@data/loader';
import type { ListingData, ListingExpect, ListingPageInfo } from '@data/storefront.types';
import { applyCaseMeta, caseTitle } from '@engine/cases';

const data = loadData<ListingData>('storefront/listing.json');
const page = (key: keyof ListingData['pages']): ListingPageInfo => data.pages[key];

/** Mock API danh sách (và danh mục Trẻ em) của 1 trang bằng dữ liệu cố định. */
async function mockListing(k: Keywords, p: ListingPageInfo, list: unknown = data.mockList) {
  await k.common.mockGet(p.productsApi, list);
  if (p.categoriesApi) await k.common.mockGet(p.categoriesApi, data.mockKidsCategories);
}

/** Server: kiểm tra query gửi lên API; client: kiểm tra dòng "Hiển thị n trên t". */
async function verifyFilterResult(k: Keywords, c: ListingExpect) {
  if (c.params) await k.listing.verifyListRequest(c.params);
  if (c.countText) await k.listing.verifyCountText(c.countText);
}

test.describe('Trang danh sách: Nam / Nữ / Trẻ em / Giảm giá', () => {
  test.describe('Bố cục trang (dữ liệu thật)', () => {
    for (const c of data.layout) {
      test(caseTitle(c), async ({ k }) => {
        applyCaseMeta(c);
        const p = page(c.page);
        await k.listing.openListing(p.path);
        await k.listing.verifyListingHeader(p.heading, p.breadcrumb, p.description);
        await k.listing.verifyCountMatchesCards();
        await k.listing.verifySortOptions(p.sortOptions, p.defaultSort);
        await k.listing.verifySizeOptions(p.sizes);
        await k.listing.verifyColorOptions(p.colors);
        await k.listing.verifyPriceInputs(p.priceDefault.from, p.priceDefault.to);
        await k.common.verifyNoPageErrors();
      });
    }

    test(caseTitle(data.showMore), async ({ k }) => {
      applyCaseMeta(data.showMore);
      const p = page(data.showMore.page);
      await k.listing.openListing(p.path);
      await k.listing.verifyCategoryOptions(p.mockCategories);
      await k.listing.showMoreCategories();
      await k.listing.verifyCategoryOptions(data.showMore.categories);
    });
  });

  test.describe('Sắp xếp theo giá (dữ liệu thật)', () => {
    for (const c of data.sort) {
      test(caseTitle(c), async ({ k }) => {
        applyCaseMeta(c);
        const p = page(c.page);
        await k.listing.openListing(p.path);
        await k.listing.sortBy(c.option);
        if (p.mode === 'server') await k.listing.verifyListRequest({ sort: 'price', order: c.order });
        await k.listing.verifyPricesSorted(c.order);
      });
    }
  });

  test.describe('Trạng thái rỗng (mock API)', () => {
    for (const c of data.empty) {
      test(caseTitle(c), async ({ k }) => {
        applyCaseMeta(c);
        const p = page(c.page);
        await mockListing(k, p, data.mockEmpty);
        await k.listing.openListing(p.path);
        await k.listing.verifyEmptyListing(p.emptyText);
      });
    }
  });

  test.describe('Lọc danh mục (mock API)', () => {
    for (const c of data.category) {
      test(caseTitle(c), async ({ k }) => {
        applyCaseMeta(c);
        const p = page(c.page);
        await mockListing(k, p);
        await k.listing.openListing(p.path);
        await k.listing.verifyCategoryOptions(p.mockCategories);
        await k.listing.selectCategory(c.category);
        await verifyFilterResult(k, c);
      });
    }
  });

  test.describe('Lọc màu (mock API)', () => {
    for (const c of data.color) {
      test(caseTitle(c), async ({ k }) => {
        applyCaseMeta(c);
        const p = page(c.page);
        await mockListing(k, p);
        await k.listing.openListing(p.path);
        await k.listing.selectColorFilter(c.color);
        await verifyFilterResult(k, c);
      });
    }
  });

  test.describe('Lọc khoảng giá (dữ liệu thật)', () => {
    for (const c of data.price) {
      test(caseTitle(c), async ({ k }) => {
        applyCaseMeta(c);
        const p = page(c.page);
        await k.listing.openListing(p.path);
        await k.listing.setPriceRange(c.from, c.to);
        await verifyFilterResult(k, c);
        await k.listing.verifyPricesWithin(c.min, c.max);
      });
    }
  });

  test.describe('Lọc phần trăm giảm (dữ liệu thật)', () => {
    for (const c of data.discount) {
      test(caseTitle(c), async ({ k }) => {
        applyCaseMeta(c);
        const p = page(c.page);
        await k.listing.openListing(p.path);
        await k.listing.selectDiscount(c.label);
        await verifyFilterResult(k, c);
        await k.listing.verifyDiscountAtLeast(c.minPercent);
      });
    }
  });

  test.describe('Lọc size (mock API)', () => {
    for (const c of data.size) {
      test(caseTitle(c), async ({ k }) => {
        applyCaseMeta(c);
        const p = page(c.page);
        await mockListing(k, p);
        await k.listing.openListing(p.path);
        await k.listing.selectSizeFilter(c.size);
        await verifyFilterResult(k, c);
        await k.listing.verifyProductsShown();
      });
    }
  });

  test.describe('Phân trang (mock API)', () => {
    for (const c of data.paging) {
      test(caseTitle(c), async ({ k }) => {
        applyCaseMeta(c);
        const p = page(c.page);
        await mockListing(k, p);
        await k.listing.openListing(p.path);
        if (c.via === 'number') await k.listing.goToPage(2);
        if (c.via === 'next') await k.listing.clickNextPage();
        if (c.via === 'loadMore') await k.listing.clickLoadMore();
        await verifyFilterResult(k, c);
      });
    }
  });

  test.describe('Nút trên thẻ sản phẩm (dữ liệu thật)', () => {
    for (const c of data.overlayAdd) {
      test(caseTitle(c), async ({ k }) => {
        applyCaseMeta(c);
        await k.listing.openListing(page(c.page).path);
        await k.listing.addFirstCardToCart();
        await k.common.verifyToast(data.overlayToast);
        await k.listing.verifyOpenedLastCard();
        await k.cart.verifyCartBadge(0);
      });
    }

    for (const c of data.overlayDetail) {
      test(caseTitle(c), async ({ k }) => {
        applyCaseMeta(c);
        await k.listing.openListing(page(c.page).path);
        await k.listing.viewFirstCardDetail();
        await k.listing.verifyOpenedLastCard();
      });
    }

    for (const c of data.favorite) {
      test(caseTitle(c), async ({ k }) => {
        applyCaseMeta(c);
        const p = page(c.page);
        await k.listing.openListing(p.path);
        await k.listing.clickFirstCardFavorite();
        await k.common.verifyUrl(p.path);
      });
    }
  });
});
