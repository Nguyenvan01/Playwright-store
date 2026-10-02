import { test } from '@fixtures';
import { loadData, resolveData } from '@data/loader';
import type { ListingData, SearchPageData } from '@data/storefront.types';
import { applyCaseMeta, caseTitle } from '@engine/cases';

const data = loadData<SearchPageData>('storefront/search-page.json');
const listing = loadData<ListingData>('storefront/listing.json');

test.describe('Trang kết quả /search', () => {
  test.describe('Tiêu đề, breadcrumb, chip theo tham số (dữ liệu thật)', () => {
    for (const raw of data.titles) {
      test(caseTitle(raw), async ({ k, ctx }) => {
        applyCaseMeta(raw);
        const c = resolveData(raw, ctx);
        await k.listing.openSearchResults(c.query);
        await k.listing.verifySearchTitle(c.heading);
        await k.listing.verifySearchBreadcrumbs(c.breadcrumbs);
        for (const [name, href] of c.breadcrumbLinks ?? []) await k.listing.verifySearchBreadcrumbLink(name, href);
        await k.listing.verifySearchSubtitleMatches();
        await k.listing.verifySearchSortOptions(data.sortOptions);
        for (const chip of c.chips ?? []) await k.listing.verifySearchChip(chip.text, chip.closeHref);
      });
    }

    test(caseTitle(data.closeChip), async ({ k }) => {
      const c = data.closeChip;
      applyCaseMeta(c);
      await k.listing.openSearchResults(c.query);
      await k.listing.closeSearchChip(c.chip);
      await k.common.verifyUrl('/search');
      await k.listing.verifySearchTitle(c.heading);
    });
  });

  test.describe('Sắp xếp theo giá (dữ liệu thật)', () => {
    for (const c of data.sort) {
      test(caseTitle(c), async ({ k }) => {
        applyCaseMeta(c);
        await k.listing.openSearchResults(c.query);
        await k.listing.sortSearchBy(c.option);
        await k.listing.verifyListRequest({ sort: 'price', order: c.order });
        await k.listing.verifySearchPricesSorted(c.order);
      });
    }
  });

  test.describe('Không có kết quả / lỗi', () => {
    for (const c of data.empty) {
      test(caseTitle(c), async ({ k }) => {
        applyCaseMeta(c);
        await k.listing.openSearchResults(c.query);
        await k.listing.verifySearchEmpty(c.hint);
        await k.listing.clickViewAllProducts();
        await k.common.verifyUrl('/search');
        await k.listing.verifySearchTitle('Tất cả sản phẩm');
      });
    }

    test(caseTitle(data.error), async ({ k }) => {
      applyCaseMeta(data.error);
      await k.common.mockGet('**/api/products?**', { success: false, message: 'Lỗi server' }, 500);
      await k.listing.openSearchResults('?q=ao');
      await k.listing.verifySearchError(data.error.message);
    });
  });

  test.describe('Phân trang (mock)', () => {
    for (const c of data.paging) {
      test(caseTitle(c), async ({ k }) => {
        applyCaseMeta(c);
        await k.common.mockGet('**/api/products?**', {
          ...listing.mockList,
          data: { ...listing.mockList.data, pagination: data.mockPagination },
        });
        await k.listing.openSearchResults('');
        await k.listing.verifySearchActivePage(1);
        if (c.via === 'number') await k.listing.goToSearchPage(2);
        else await k.listing.clickSearchNextPage();
        await k.listing.verifyListRequest({ page: '2', limit: '12' });
        await k.listing.verifySearchActivePage(2);
      });
    }
  });

  test(caseTitle(data.shortQuery), async ({ k }) => {
    const c = data.shortQuery;
    applyCaseMeta(c);
    await k.catalog.openHome();
    await k.listing.typeHeaderSearchExpectingStatus(c.keyword, 400);
    await k.listing.verifyHeaderSuggestionsHidden();
    await k.catalog.submitSearch(c.keyword);
    await k.listing.verifySearchTitle(`Kết quả tìm kiếm: "${c.keyword}"`);
    await k.listing.verifySearchSubtitleMatches();
  });
});
