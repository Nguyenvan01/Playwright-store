import { Locator, Page } from '@playwright/test';

/** Trang /blog (pages/BlogPage.jsx). */
export class BlogListPage {
  readonly heading: Locator;
  readonly subtitle: Locator;
  readonly categoryPills: Locator;
  readonly cards: Locator;
  readonly emptyState: Locator;
  readonly newsletterSection: Locator;
  readonly newsletterEmail: Locator;
  readonly newsletterSubmit: Locator;

  constructor(readonly page: Page) {
    this.heading = page.getByRole('heading', { level: 1, name: 'Blog Thời Trang' });
    this.subtitle = page.getByText('Cập nhật xu hướng, chia sẻ phong cách và câu chuyện từ Đạt Hoàng');
    this.categoryPills = page.locator('main section.sticky button');
    this.cards = page.locator('main a[href^="/blog/"]');
    this.emptyState = page.getByText('Không có bài viết nào trong danh mục này');
    this.newsletterSection = page
      .locator('main section')
      .filter({ has: page.getByRole('heading', { name: 'Đăng ký nhận tin mới nhất' }) });
    this.newsletterEmail = this.newsletterSection.getByPlaceholder('Nhập email của bạn');
    this.newsletterSubmit = this.newsletterSection.getByRole('button', { name: 'Đăng ký' });
  }

  async open() {
    await this.page.goto('/blog');
  }

  pill(name: string): Locator {
    return this.categoryPills.filter({ hasText: new RegExp(`^${name}$`) });
  }

  card(title: string): Locator {
    return this.cards.filter({ has: this.page.locator('h2', { hasText: title }) });
  }

  /** Nhãn danh mục của từng thẻ bài viết. */
  cardCategories(): Locator {
    return this.cards.locator('span.uppercase');
  }
}

/** Trang /blog/:slug (pages/BlogDetailPage.jsx). */
export class BlogDetailPage {
  readonly title: Locator;
  readonly backLink: Locator;
  readonly categoryBadge: Locator;
  readonly viewCount: Locator;
  readonly author: Locator;
  readonly summary: Locator;
  readonly tagsSection: Locator;
  readonly relatedHeading: Locator;
  readonly relatedSection: Locator;
  readonly relatedCards: Locator;
  readonly contentFallback: Locator;

  constructor(readonly page: Page) {
    this.title = page.getByRole('heading', { level: 1 });
    this.backLink = page.getByRole('link', { name: /Quay lại Blog/ });
    this.categoryBadge = page.locator('main .max-w-3xl span.rounded-full').first();
    this.viewCount = page.getByText(/\d+ lượt xem$/);
    this.author = page.locator('main .max-w-3xl p.font-semibold');
    this.summary = page.locator('main p.italic.border-l-4');
    this.tagsSection = page.locator('main div.flex-wrap').filter({ hasText: 'Tags:' });
    this.relatedHeading = page.getByRole('heading', { name: 'Bài viết liên quan' });
    this.relatedSection = page.locator('main section').filter({ has: this.relatedHeading });
    this.relatedCards = this.relatedSection.locator('a[href^="/blog/"]');
    this.contentFallback = page.getByText('Nội dung đang được cập nhật. Vui lòng quay lại sau.');
  }

  async open(slug: string) {
    await this.page.goto(`/blog/${slug}`);
  }

  tag(tag: string): Locator {
    return this.tagsSection.getByText(`#${tag}`, { exact: true });
  }

  relatedCard(title: string): Locator {
    return this.relatedCards.filter({ has: this.page.locator('h3', { hasText: title }) });
  }
}
