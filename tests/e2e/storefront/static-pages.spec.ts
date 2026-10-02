import { test } from '@fixtures';
import { loadData } from '@data/loader';
import type { StaticPagesData } from '@data/storefront.types';
import { applyCaseMeta, caseTitle } from '@engine/cases';

const data = loadData<StaticPagesData>('storefront/static-pages.json');

test.describe('Trang tĩnh: tiêu đề và nội dung (data-driven)', () => {
  for (const c of data.pages) {
    test(caseTitle(c), async ({ k }) => {
      applyCaseMeta(c);
      await k.common.goto(c.path);
      await k.common.verifyLayoutLoaded();
      await k.content.verifyPageHeadings(c.h1, c.h2, c.h3);
      await k.content.verifyMainContains(c.texts);
    });
  }
});

test.describe('Trang tĩnh: lỗi nội dung', () => {
  for (const c of data.contentBugs) {
    test(caseTitle(c), async ({ k }) => {
      applyCaseMeta(c);
      await k.common.goto(c.path);
      await k.common.verifyLayoutLoaded();
      if (c.mustNotMatch) await k.content.verifyMainNotMatching(c.mustNotMatch);
      if (c.mustContain && c.block) await k.content.verifyBlockContains(c.block, c.mustContain);
      else if (c.mustContain) await k.content.verifyMainContains([c.mustContain]);
    });
  }
});

test.describe('Đường dẫn không tồn tại', () => {
  for (const c of data.unknownRoutes) {
    test(caseTitle(c), async ({ k }) => {
      applyCaseMeta(c);
      await k.common.goto(c.path);
      await k.content.verifyNotFoundPage(c.message);
    });
  }
});
