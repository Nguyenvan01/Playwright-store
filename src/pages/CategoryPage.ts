import { Locator, Page } from '@playwright/test';
import { BasePage } from './BasePage';
import { Header } from './components/Header';

/** Các trang danh mục: /nam, /nu, /tre-em, /giam-gia. */
export class CategoryPage extends BasePage {
  readonly path: string;
  readonly header: Header;
  readonly heading: Locator;
  readonly productLinks: Locator;
  readonly sortSelect: Locator;
  readonly emptyState: Locator;

  constructor(page: Page, path = '/nam') {
    super(page);
    this.path = path;
    this.header = new Header(page);
    this.heading = page.getByRole('heading', { level: 1 });
    this.productLinks = page.locator('a[href^="/product/"]').filter({ visible: true });
    this.sortSelect = page.locator('select').first();
    this.emptyState = page.getByText(/Không tìm thấy sản phẩm/);
  }
}
