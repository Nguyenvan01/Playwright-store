import { test } from '@fixtures';
import { loadData } from '@data/loader';
import type { FooterData } from '@data/storefront.types';
import { applyCaseMeta, caseTitle } from '@engine/cases';

const data = loadData<FooterData>('storefront/footer.json');

test.describe('Footer', () => {
  test('[SF-FOOT-01] Footer có đủ cột, link và dòng bản quyền', async ({ k }) => {
    await k.content.openHomePage();
    await k.content.verifyFooterContent(data.headings, data.links);
  });

  for (const c of data.linkCases) {
    test(caseTitle(c), async ({ k }) => {
      applyCaseMeta(c);
      await k.content.openHomePage();
      if (c.link) await k.content.verifyFooterLink(c.link, c.href);
      else await k.content.verifyFooterHasLinkTo(c.href);
    });
  }
});

test.describe('Đăng ký nhận tin (data-driven)', () => {
  for (const c of data.newsletter) {
    test(caseTitle(c), async ({ k }) => {
      applyCaseMeta(c);
      await k.common.goto(c.path);
      await k.content.subscribeNewsletter(c.email);
      if (c.success) await k.content.verifyNewsletterThanks();
      else await k.content.verifyNewsletterBlocked(c.validity ?? 'valid');
    });
  }
});
