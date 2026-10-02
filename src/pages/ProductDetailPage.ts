import { Locator, Page } from '@playwright/test';
import { BasePage } from './BasePage';
import { Header } from './components/Header';
import { CartDrawer } from './components/CartDrawer';

export class ProductDetailPage extends BasePage {
  readonly path = '/';
  readonly header: Header;
  readonly cart: CartDrawer;
  readonly title: Locator;
  readonly sizeButtons: Locator;
  readonly availableSizes: Locator;
  readonly sizeWarning: Locator;
  readonly colorButtons: Locator;
  readonly addToCartButton: Locator;
  readonly notFound: Locator;

  constructor(page: Page) {
    super(page);
    this.header = new Header(page);
    this.cart = new CartDrawer(page);
    this.title = page.locator('h1.product-title');
    this.sizeButtons = page.locator('.size-options button');
    this.availableSizes = page.locator('.size-options button:not([disabled])');
    this.sizeWarning = page.locator('.size-selector').getByText('Vui lòng chọn kích cỡ');
    this.colorButtons = page.locator('.color-selector button');
    this.addToCartButton = page.locator('.action-buttons').getByRole('button', { name: 'Thêm vào giỏ hàng' });
    this.notFound = page.getByText('Không tìm thấy sản phẩm.');
  }

  async open(slug: string) {
    await this.goto(`/product/${slug}`);
  }

  async selectSize(label?: string) {
    const button = label
      ? this.sizeButtons.filter({ hasText: new RegExp(`^${label}$`) })
      : this.availableSizes.first();
    await button.click();
  }

  async addToCart(size?: string) {
    await this.selectSize(size);
    await this.addToCartButton.click();
  }
}
