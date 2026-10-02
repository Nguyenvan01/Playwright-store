import { Locator, Page } from '@playwright/test';
import { BasePage } from './BasePage';
import { Header } from './components/Header';

export class SearchPage extends BasePage {
  readonly path = '/search';
  readonly header: Header;
  readonly heading: Locator;
  readonly resultCount: Locator;
  readonly productLinks: Locator;
  readonly noResult: Locator;

  constructor(page: Page) {
    super(page);
    this.header = new Header(page);
    this.heading = page.getByRole('heading', { level: 1 });
    this.resultCount = page.getByText(/^\d+ sản phẩm$/);
    this.productLinks = page.locator('a[href^="/product/"]').filter({ visible: true });
    this.noResult = page.getByRole('heading', { name: 'Không tìm thấy sản phẩm nào' });
  }

  async search(query: string) {
    await this.goto(`/search?q=${encodeURIComponent(query)}`);
  }
}
