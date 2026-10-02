import { test } from '@fixtures';
import { loadData, resolveData } from '@data/loader';
import type { SearchData } from '@data/types';
import { applyCaseMeta, caseTitle } from '@engine/cases';

const data = loadData<SearchData>('catalog/search.json');

test.describe('Tìm kiếm sản phẩm (data-driven)', () => {
  for (const raw of data.suggestions) {
    test(`Gợi ý: ${caseTitle(raw)}`, async ({ k, ctx }) => {
      applyCaseMeta(raw);
      const c = resolveData(raw, ctx);
      await k.catalog.openHome();
      await k.catalog.typeSearch(c.keyword);
      await k.catalog.verifySearchSuggestion(c.expectSuggestion);
      await k.catalog.clickSearchSuggestion(c.expectSuggestion);
      await k.catalog.verifyProductTitle(c.expectSuggestion);
    });
  }

  for (const raw of data.resultPage) {
    test(`Trang kết quả: ${caseTitle(raw)}`, async ({ k, ctx }) => {
      applyCaseMeta(raw);
      const c = resolveData(raw, ctx);
      await k.catalog.openHome();
      await k.catalog.submitSearch(c.keyword);
      await k.catalog.verifySearchResults(c.expectHeading);
    });
  }

  for (const c of data.noResult) {
    test(`Không có kết quả: ${caseTitle(c)}`, async ({ k }) => {
      applyCaseMeta(c);
      await k.catalog.openHome();
      await k.catalog.typeSearch(c.keyword);
      await k.catalog.verifyNoSearchSuggestion();
      await k.catalog.openSearchPage(c.keyword);
      await k.catalog.verifyNoSearchResults();
    });
  }
});
