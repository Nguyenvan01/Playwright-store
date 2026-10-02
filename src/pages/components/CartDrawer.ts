import { Locator, Page, expect } from '@playwright/test';

/** Ngăn kéo giỏ hàng (role=dialog, aria-label="Giỏ hàng"). Luôn có trong DOM, mở bằng class. */
export class CartDrawer {
  readonly root: Locator;
  readonly title: Locator;
  readonly closeButton: Locator;
  readonly emptyState: Locator;
  readonly items: Locator;
  readonly selectAll: Locator;
  readonly subtotal: Locator;
  readonly checkoutButton: Locator;

  constructor(readonly page: Page) {
    this.root = page.getByRole('dialog', { name: 'Giỏ hàng' });
    this.title = this.root.getByRole('heading', { name: /Giỏ hàng \(\d+\)/ });
    this.closeButton = this.root.getByRole('button', { name: 'Đóng giỏ hàng' });
    this.emptyState = this.root.getByText('Giỏ hàng trống');
    this.items = this.root.locator('.cart-item');
    this.selectAll = this.root.getByLabel('Chọn tất cả');
    this.subtotal = this.root.locator('.cart-subtotal');
    this.checkoutButton = this.root.getByRole('button', { name: 'THANH TOÁN' });
  }

  async expectOpen() {
    await expect(this.root).toHaveClass(/cart-drawer--open/);
  }

  async expectClosed() {
    await expect(this.root).not.toHaveClass(/cart-drawer--open/);
  }

  item(name: string): Locator {
    return this.items.filter({ has: this.page.locator('.cart-item-title', { hasText: name }) });
  }

  quantity(name: string): Locator {
    return this.item(name).locator('.cart-qty-value');
  }

  async increase(name: string) {
    await this.item(name).getByRole('button', { name: 'Tăng số lượng' }).click();
  }

  async decrease(name: string) {
    await this.item(name).getByRole('button', { name: 'Giảm số lượng' }).click();
  }

  async remove(name: string) {
    await this.item(name).locator('.cart-item-menu-btn').click();
    await this.root.getByRole('button', { name: 'Xóa', exact: true }).click();
  }

  async close() {
    await this.closeButton.click();
  }
}
