import { test } from '@fixtures';
import { loadData } from '@data/loader';
import type { BlogData } from '@data/storefront.types';
import { applyCaseMeta, caseTitle } from '@engine/cases';

const data = loadData<BlogData>('storefront/blog.json');
const allTitles = data.mockList.news.map((a) => a.title);

test.describe('Blog (dữ liệu thật)', () => {
  test('[SF-BLOG-01] /blog hiển thị tiêu đề, danh mục và bài viết @smoke', async ({ k }) => {
    await k.content.openBlog();
    await k.content.verifyBlogLoaded();
    await k.common.verifyNoPageErrors();
  });

  test('[SF-BLOG-08] Slug bài viết không tồn tại -> chuyển về /blog', async ({ k }) => {
    await k.content.openBlogArticleBySlug(data.invalidSlug);
    await k.common.verifyUrl('/blog');
    await k.content.verifyBlogLoaded();
  });
});

test.describe('Blog (mock API)', () => {
  test.beforeEach(async ({ k }) => {
    await k.content.mockBlogData(data.mockList);
    await k.content.openBlog();
  });

  test('[SF-BLOG-02] Danh mục lấy từ bài viết, mặc định "Tất cả" hiển thị mọi bài', async ({ k }) => {
    await k.content.verifyBlogPills(data.pills);
    await k.content.verifyBlogTitles(allTitles);
  });

  for (const c of data.filters) {
    test(caseTitle(c), async ({ k }) => {
      applyCaseMeta(c);
      await k.content.filterBlogByCategory(c.category);
      await k.content.verifyBlogTitles(c.titles);
      await k.content.verifyBlogCategoryOfCards(c.category);
      await k.content.filterBlogByCategory('Tất cả');
      await k.content.verifyBlogTitles(allTitles);
    });
  }

  for (const c of data.details) {
    test(caseTitle(c), async ({ k }) => {
      applyCaseMeta(c);
      await k.content.openBlogArticle(c.titleText);
      await k.content.verifyBlogArticle(c);
    });
  }

  test('[SF-BLOG-09] Bài liên quan mở bài khác, "Quay lại Blog" về danh sách', async ({ k }) => {
    const [first, second] = data.details;
    await k.content.openBlogArticle(first.titleText);
    await k.content.openRelatedArticle(second.titleText);
    await k.content.verifyBlogArticle(second);
    await k.content.clickBackToBlog();
    await k.common.verifyUrl('/blog');
  });

  test(caseTitle(data.newsletterBug), async ({ k }) => {
    applyCaseMeta(data.newsletterBug);
    await k.content.subscribeBlogNewsletterWithoutReload(data.newsletterBug.email);
  });
});

test('[SF-BLOG-10] Không có bài viết nào -> chỉ có "Tất cả" và thông báo trống', async ({ k }) => {
  await k.content.mockBlogData({ success: true, news: [] });
  await k.content.openBlog();
  await k.content.verifyBlogPills(['Tất cả']);
  await k.content.verifyBlogEmpty();
});
