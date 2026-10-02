import { Locator, Page } from '@playwright/test';

/** Header dùng chung cho các trang khách hàng (logo, menu, tìm kiếm, tài khoản, giỏ hàng). */
export class Header {
  readonly root: Locator;
  readonly logo: Locator;
  readonly desktopNav: Locator;
  readonly searchInput: Locator;
  readonly searchSeeMore: Locator;
  readonly searchNoResult: Locator;
  readonly loginLink: Locator;
  readonly userMenuButton: Locator;
  readonly logoutButton: Locator;
  readonly cartButton: Locator;
  readonly cartBadge: Locator;
  readonly mobileMenuToggle: Locator;

  constructor(readonly page: Page) {
    this.root = page.locator('header').first();
    this.logo = this.root.getByRole('link', { name: 'Đạt Hoàng', exact: true });
    this.desktopNav = this.root.locator('nav');
    this.searchInput = this.root.getByPlaceholder('Tìm kiếm sản phẩm...');
    this.searchSeeMore = this.root.getByText(/Xem thêm kết quả cho/);
    this.searchNoResult = this.root.getByText('Không tìm thấy sản phẩm nào');
    this.loginLink = this.root.locator('a[href="/login"]');
    // Các nút icon chưa có aria-label -> nhận diện qua svg. Nên bổ sung data-testid ở app.
    this.userMenuButton = this.root
      .locator('button')
      .filter({ has: page.locator('svg circle[cx="12"][cy="7"]') });
    this.logoutButton = this.root.getByRole('button', { name: 'Đăng xuất' });
    this.cartButton = this.root
      .locator('button')
      .filter({ has: page.locator('svg circle[cx="8"][cy="21"]') })
      .first();
    this.cartBadge = this.cartButton.locator('span.rounded-full');
    this.mobileMenuToggle = this.root.locator('button.lg\\:hidden');
  }

  navLink(name: string): Locator {
    return this.desktopNav.getByRole('link', { name, exact: true });
  }

  mobileNavLink(name: string): Locator {
    return this.root.locator('div.lg\\:hidden').getByRole('link', { name, exact: true });
  }

  searchResult(productName: string): Locator {
    return this.root.locator('h4', { hasText: productName });
  }

  async typeSearch(query: string) {
    await this.searchInput.fill(query);
  }

  async submitSearch(query: string) {
    await this.searchInput.fill(query);
    await this.searchInput.press('Enter');
  }

  async openCart() {
    await this.cartButton.click();
  }

  async logout() {
    await this.userMenuButton.click();
    await this.logoutButton.click();
  }
}
