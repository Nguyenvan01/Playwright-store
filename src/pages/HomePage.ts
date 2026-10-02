import { Locator, Page } from '@playwright/test';
import { BasePage } from './BasePage';
import { Header } from './components/Header';
import { CartDrawer } from './components/CartDrawer';

export class HomePage extends BasePage {
  readonly path = '/';
  readonly header: Header;
  readonly cart: CartDrawer;
  readonly newProductsHeading: Locator;
  readonly productCards: Locator;
  readonly footer: Locator;

  constructor(page: Page) {
    super(page);
    this.header = new Header(page);
    this.cart = new CartDrawer(page);
    this.newProductsHeading = page.getByRole('heading', { name: 'SẢN PHẨM MỚI' });
    this.productCards = page.locator('main a[href^="/product/"], section a[href^="/product/"]');
    this.footer = page.locator('footer');
  }

  productCard(name: string): Locator {
    return this.productCards.filter({ has: this.page.locator('h3', { hasText: name }) });
  }
}
