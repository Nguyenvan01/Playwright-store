import { Locator, Page } from '@playwright/test';
import { escapeRegex } from './cssText';

/**
 * Sidebar tài khoản bên trái. Có 2 phiên bản trong app:
 * - AccountSidebar.jsx (hồ sơ, đơn hàng, yêu thích): link "Hồ sơ cá nhân", "Đơn hàng của tôi", "Yêu thích".
 * - Sidebar riêng trong OrderDetailPage/AddressesPage: tên link có chữ ligature Material Symbols,
 *   vd: "person Hồ sơ cá nhân", "location_on Sổ địa chỉ".
 */
export class AccountSidebar {
  readonly root: Locator;
  readonly logoutButton: Locator;

  constructor(readonly page: Page) {
    this.root = page.locator('main aside');
    this.logoutButton = this.root.getByRole('button', { name: /Đăng xuất$/ });
  }

  /** Link theo nhãn hiển thị (bỏ qua chữ icon phía trước). */
  link(label: string): Locator {
    return this.root.getByRole('link', { name: new RegExp(`(^|\\s)${escapeRegex(label)}$`) });
  }
}
