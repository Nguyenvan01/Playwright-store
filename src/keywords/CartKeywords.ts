import { expect } from '@playwright/test';
import { buildCartItem, CartItem } from '@data/factories';
import { readCart, seedCart } from '@utils/storage';
import { BaseKeywords } from './BaseKeywords';

export class CartKeywords extends BaseKeywords {
  /** Đặt sẵn sản phẩm vào giỏ (localStorage) - gọi TRƯỚC lần mở trang đầu tiên. */
  async seedCart(items: Partial<CartItem>[]) {
    await this.step(`Đặt sẵn ${items.length} sản phẩm vào giỏ`, async () => {
      await seedCart(this.page, items.map((i) => buildCartItem(i)));
    });
  }

  /** Bấm icon giỏ hàng để mở drawer. */
  async openCart() {
    await this.step('Mở giỏ hàng', async () => {
      await this.po.header.openCart();
      await this.po.cart.expectOpen();
    });
  }

  /** Đóng drawer bằng nút X. */
  async closeCart() {
    await this.step('Đóng giỏ hàng (nút X)', async () => {
      await this.po.cart.close();
      await this.po.cart.expectClosed();
    });
  }

  /** Đóng drawer bằng phím ESC. */
  async closeCartWithEsc() {
    await this.step('Đóng giỏ hàng (ESC)', async () => {
      await this.page.keyboard.press('Escape');
      await this.po.cart.expectClosed();
    });
  }

  /** Kiểm tra số trên icon giỏ hàng (0 = không hiện badge). */
  async verifyCartBadge(count: number) {
    await this.step(`Kiểm tra badge giỏ hàng = ${count}`, async () => {
      const badge = this.po.header.cartBadge;
      await (count === 0 ? expect(badge).toBeHidden() : expect(badge).toHaveText(count > 9 ? '9+' : String(count)));
    });
  }

  /** Kiểm tra drawer hiển thị "Giỏ hàng trống". */
  async verifyCartEmpty() {
    await this.step('Kiểm tra giỏ hàng trống', async () => {
      await expect(this.po.cart.emptyState).toBeVisible();
    });
  }

  /** Kiểm tra số dòng sản phẩm trong drawer (và tiêu đề "Giỏ hàng (n)"). */
  async verifyCartItemCount(count: number) {
    await this.step(`Kiểm tra giỏ có ${count} sản phẩm`, async () => {
      await expect(this.po.cart.title).toHaveText(`Giỏ hàng (${count})`);
      await expect(this.po.cart.items).toHaveCount(count);
    });
  }

  /** Kiểm tra 1 sản phẩm có trong giỏ, có thể kèm đoạn chữ (vd: size). */
  async verifyCartItem(name: string, containsText?: string) {
    await this.step(`Kiểm tra giỏ có "${name}"${containsText ? ` chứa "${containsText}"` : ''}`, async () => {
      const item = this.po.cart.item(name);
      await expect(item).toBeVisible();
      if (containsText) await expect(item).toContainText(containsText);
    });
  }

  /** Bấm "+" số lần cho 1 sản phẩm. */
  async increaseQuantity(name: string, times = 1) {
    await this.step(`Tăng số lượng "${name}" x${times}`, async () => {
      for (let i = 0; i < times; i++) await this.po.cart.increase(name);
    });
  }

  /** Bấm "-" số lần cho 1 sản phẩm. */
  async decreaseQuantity(name: string, times = 1) {
    await this.step(`Giảm số lượng "${name}" x${times}`, async () => {
      for (let i = 0; i < times; i++) await this.po.cart.decrease(name);
    });
  }

  /** Kiểm tra số lượng hiển thị của 1 sản phẩm. */
  async verifyQuantity(name: string, quantity: number) {
    await this.step(`Kiểm tra số lượng "${name}" = ${quantity}`, async () => {
      await expect(this.po.cart.quantity(name)).toHaveText(String(quantity));
    });
  }

  /** Kiểm tra nút "-" bị khóa (số lượng = 1). */
  async verifyDecreaseDisabled(name: string) {
    await this.step(`Kiểm tra không giảm được "${name}" dưới 1`, async () => {
      await expect(this.po.cart.item(name).getByRole('button', { name: 'Giảm số lượng' })).toBeDisabled();
    });
  }

  /** Xóa 1 sản phẩm khỏi giỏ. */
  async removeItem(name: string) {
    await this.step(`Xóa "${name}" khỏi giỏ`, async () => {
      await this.po.cart.remove(name);
      await expect(this.po.cart.item(name)).toHaveCount(0);
    });
  }

  /** Tick / bỏ tick "Chọn tất cả". */
  async selectAll(checked: boolean) {
    await this.step(`${checked ? 'Chọn' : 'Bỏ chọn'} tất cả sản phẩm`, async () => {
      await this.po.cart.selectAll.setChecked(checked);
    });
  }

  /** Kiểm tra trạng thái ô "Chọn tất cả". */
  async verifyAllSelected(checked: boolean) {
    await this.step(`Kiểm tra "Chọn tất cả" = ${checked}`, async () => {
      await (checked ? expect(this.po.cart.selectAll).toBeChecked() : expect(this.po.cart.selectAll).not.toBeChecked());
    });
  }

  /** Kiểm tra dòng Tạm tính chứa số tiền, vd: "550.000". */
  async verifySubtotal(amount: string) {
    await this.step(`Kiểm tra tạm tính ${amount}`, async () => {
      await expect(this.po.cart.subtotal).toContainText(amount);
    });
  }

  /** Kiểm tra nút THANH TOÁN bật/tắt. */
  async verifyCheckoutEnabled(enabled: boolean) {
    await this.step(`Kiểm tra nút THANH TOÁN ${enabled ? 'bật' : 'tắt'}`, async () => {
      const btn = this.po.cart.checkoutButton;
      await (enabled ? expect(btn).toBeEnabled() : expect(btn).toBeDisabled());
    });
  }

  /** Bấm THANH TOÁN trong drawer và chờ sang /checkout. */
  async proceedToCheckout() {
    await this.step('Bấm THANH TOÁN', async () => {
      await this.po.cart.checkoutButton.click();
      await expect(this.page).toHaveURL('/checkout');
    });
  }

  /** Kiểm tra số dòng sản phẩm lưu trong localStorage. */
  async verifyStoredItemCount(count: number) {
    await this.step(`Kiểm tra localStorage có ${count} sản phẩm`, async () => {
      expect(await readCart(this.page)).toHaveLength(count);
    });
  }

  /** Kiểm tra số lượng của 1 sản phẩm lưu trong localStorage. */
  async verifyStoredQuantity(name: string, quantity: number) {
    await this.step(`Kiểm tra localStorage: "${name}" = ${quantity}`, async () => {
      const cart = await readCart(this.page);
      expect(cart.find((i) => i.name === name)?.quantity).toBe(quantity);
    });
  }
}
