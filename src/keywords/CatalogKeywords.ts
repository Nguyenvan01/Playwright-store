import { expect } from '@playwright/test';
import { BaseKeywords } from './BaseKeywords';

export class CatalogKeywords extends BaseKeywords {
  /** Mở trang chủ và chờ danh sách sản phẩm. */
  async openHome() {
    await this.step('Mở trang chủ', async () => {
      await this.po.home.goto();
      await expect(this.po.home.productCards.first()).toBeVisible();
    });
  }

  /** Kiểm tra trang chủ: logo, ô tìm kiếm, khối SẢN PHẨM MỚI, footer. */
  async verifyHomeLoaded() {
    await this.step('Kiểm tra trang chủ hiển thị đầy đủ', async () => {
      const home = this.po.home;
      await expect(home.header.logo).toBeVisible();
      await expect(home.header.searchInput).toBeVisible();
      await expect(home.newProductsHeading).toBeVisible();
      await expect(home.footer).toBeVisible();
    });
  }

  /** Bấm logo trên header. */
  async clickLogo() {
    await this.step('Bấm logo', async () => {
      await this.po.header.logo.click();
    });
  }

  /** Kiểm tra link danh mục trên menu trỏ đúng đường dẫn. */
  async verifyMenuLink(nav: string, path: string) {
    await this.step(`Kiểm tra menu "${nav}" -> ${path}`, async () => {
      await expect(this.po.header.navLink(nav)).toHaveAttribute('href', path);
    });
  }

  /** Bấm 1 danh mục trên menu header, vd: "NAM". */
  async openCategoryFromMenu(nav: string) {
    await this.step(`Mở danh mục "${nav}" từ menu`, async () => {
      await this.po.header.navLink(nav).click();
    });
  }

  /** Mở menu mobile (hamburger) và bấm 1 danh mục. */
  async openCategoryFromMobileMenu(nav: string) {
    await this.step(`Mở danh mục "${nav}" từ menu mobile`, async () => {
      await this.po.header.mobileMenuToggle.click();
      await this.po.header.mobileNavLink(nav).click();
    });
  }

  /** Kiểm tra đang ở trang danh mục (URL + tiêu đề) và có sản phẩm hoặc thông báo rỗng. */
  async verifyCategoryPage(path: string, heading: string) {
    await this.step(`Kiểm tra trang danh mục ${path} "${heading}"`, async () => {
      const category = this.po.category(path);
      await expect(this.page).toHaveURL(path);
      await expect(category.heading).toHaveText(heading);
      await expect(category.productLinks.first().or(category.emptyState)).toBeVisible();
    });
  }

  /** Bấm sản phẩm đầu tiên trong danh sách đang hiển thị và chờ trang chi tiết. */
  async openFirstProductInList() {
    await this.step('Mở sản phẩm đầu tiên trong danh sách', async () => {
      await this.page.locator('a[href^="/product/"]').filter({ visible: true }).first().click();
      await expect(this.page).toHaveURL(/\/product\/.+/);
      await expect(this.po.product.title).toBeVisible();
    });
  }

  /** Mở trang chi tiết sản phẩm theo slug. */
  async openProduct(slug: string) {
    await this.step(`Mở sản phẩm "${slug}"`, async () => {
      await this.po.product.open(slug);
    });
  }

  /** Kiểm tra tên sản phẩm trên trang chi tiết. */
  async verifyProductTitle(name: string) {
    await this.step(`Kiểm tra tên sản phẩm "${name}"`, async () => {
      await expect(this.po.product.title).toHaveText(name);
    });
  }

  /** Kiểm tra số nút size trên trang chi tiết. */
  async verifySizeCount(count: number) {
    await this.step(`Kiểm tra có ${count} size`, async () => {
      await expect(this.po.product.sizeButtons).toHaveCount(count);
    });
  }

  /** Chọn size (để trống = size còn hàng đầu tiên). */
  async selectSize(label?: string) {
    await this.step(`Chọn size ${label ?? '(đầu tiên còn hàng)'}`, async () => {
      await this.po.product.selectSize(label);
    });
  }

  /** Kiểm tra cảnh báo "Vui lòng chọn kích cỡ" hiện/ẩn. */
  async verifySizeWarning(visible: boolean) {
    await this.step(`Kiểm tra cảnh báo chọn size ${visible ? 'hiện' : 'ẩn'}`, async () => {
      const w = this.po.product.sizeWarning;
      await (visible ? expect(w).toBeVisible() : expect(w).toBeHidden());
    });
  }

  /** Chọn size (nếu có) rồi bấm "Thêm vào giỏ hàng". */
  async addToCart(size?: string) {
    await this.step(`Thêm vào giỏ hàng${size ? ` (size ${size})` : ''}`, async () => {
      if (size) await this.po.product.selectSize(size);
      await this.po.product.addToCartButton.click();
    });
  }

  /** Kiểm tra trang "Không tìm thấy sản phẩm". */
  async verifyProductNotFound() {
    await this.step('Kiểm tra hiển thị "Không tìm thấy sản phẩm"', async () => {
      await expect(this.po.product.notFound).toBeVisible();
    });
  }

  /** Gõ từ khóa vào ô tìm kiếm trên header (chưa Enter). */
  async typeSearch(keyword: string) {
    await this.step(`Gõ tìm kiếm "${keyword}"`, async () => {
      await this.po.header.typeSearch(keyword);
    });
  }

  /** Kiểm tra dropdown gợi ý có sản phẩm. */
  async verifySearchSuggestion(name: string) {
    await this.step(`Kiểm tra gợi ý có "${name}"`, async () => {
      await expect(this.po.header.searchResult(name).first()).toBeVisible();
      await expect(this.po.header.searchSeeMore).toBeVisible();
    });
  }

  /** Bấm 1 sản phẩm trong dropdown gợi ý. */
  async clickSearchSuggestion(name: string) {
    await this.step(`Bấm gợi ý "${name}"`, async () => {
      await this.po.header.searchResult(name).first().click();
    });
  }

  /** Kiểm tra dropdown báo không có kết quả. */
  async verifyNoSearchSuggestion() {
    await this.step('Kiểm tra gợi ý báo không có kết quả', async () => {
      await expect(this.po.header.searchNoResult).toBeVisible();
    });
  }

  /** Gõ từ khóa vào ô tìm kiếm và nhấn Enter. */
  async submitSearch(keyword: string) {
    await this.step(`Tìm kiếm "${keyword}" + Enter`, async () => {
      await this.po.header.submitSearch(keyword);
    });
  }

  /** Mở thẳng trang kết quả /search?q=... */
  async openSearchPage(keyword: string) {
    await this.step(`Mở trang tìm kiếm "${keyword}"`, async () => {
      await this.po.search.search(keyword);
    });
  }

  /** Kiểm tra trang kết quả tìm kiếm có tiêu đề và ít nhất 1 sản phẩm. */
  async verifySearchResults(heading: string) {
    await this.step(`Kiểm tra trang kết quả "${heading}"`, async () => {
      await expect(this.page).toHaveURL(/\/search\?q=/);
      await expect(this.po.search.heading).toHaveText(heading);
      await expect(this.po.search.productLinks.first()).toBeVisible();
    });
  }

  /** Kiểm tra trang kết quả tìm kiếm rỗng. */
  async verifyNoSearchResults() {
    await this.step('Kiểm tra trang kết quả rỗng', async () => {
      await expect(this.po.search.noResult).toBeVisible();
    });
  }
}
