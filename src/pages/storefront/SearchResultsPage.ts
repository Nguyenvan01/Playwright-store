import { Locator, Page } from '@playwright/test';

/** Trang /search (pages/SearchPage.jsx): ?q= / ?category= / ?brand= hoặc không tham số. */
export class SearchResultsPage {
  readonly breadcrumb: Locator;
  readonly heading: Locator;
  readonly subtitle: Locator;
  readonly sortSelect: Locator;
  readonly cards: Locator;
  readonly emptyHeading: Locator;
  readonly viewAllLink: Locator;
  readonly errorHeading: Locator;
  readonly retryButton: Locator;
  readonly pagination: Locator;

  constructor(readonly page: Page) {
    this.breadcrumb = page.locator('main nav').first();
    this.heading = page.getByRole('heading', { level: 1 });
    this.subtitle = page.locator('main h1 + p');
    this.sortSelect = page.locator('main select');
    this.cards = page.locator('main .grid a[href^="/product/"]');
    this.emptyHeading = page.getByRole('heading', { name: 'Không tìm thấy sản phẩm nào' });
    this.viewAllLink = page.getByRole('link', { name: 'Xem tất cả sản phẩm' });
    this.errorHeading = page.getByRole('heading', { name: 'Đã xảy ra lỗi' });
    this.retryButton = page.getByRole('button', { name: 'Thử lại' });
    this.pagination = page.locator('main .mt-16');
  }

  async open(query: string) {
    await this.page.goto(`/search${query}`);
  }

  breadcrumbItem(name: string): Locator {
    return this.breadcrumb.getByText(name, { exact: true });
  }

  breadcrumbLink(name: string): Locator {
    return this.breadcrumb.getByRole('link', { name, exact: true });
  }

  /** Chip bộ lọc đang áp dụng, vd: 'Danh mục: Vay', 'Tìm: "ao"'. */
  chip(text: string): Locator {
    return this.page.locator('main span.rounded-full').filter({ hasText: text });
  }

  chipClose(text: string): Locator {
    return this.chip(text).getByRole('link', { name: 'close' });
  }

  /** Giá bán hiện tại của ProductCard (span đậm). */
  cardPrice(card: Locator): Locator {
    return card.locator('span.font-bold').filter({ hasText: /^[\d.]+đ$/ });
  }

  pageButton(n: number): Locator {
    return this.pagination.getByRole('button', { name: String(n), exact: true });
  }

  nextPageButton(): Locator {
    return this.pagination.getByRole('button', { name: 'chevron_right', exact: true });
  }

  prevPageButton(): Locator {
    return this.pagination.getByRole('button', { name: 'chevron_left', exact: true });
  }

  emptyHint(text: string): Locator {
    return this.page.locator('main').getByText(text, { exact: true });
  }
}
