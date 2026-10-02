import { Locator, Page } from '@playwright/test';

/**
 * Trang danh sách sản phẩm dùng ProductFilters: /nam, /nu, /tre-em, /giam-gia.
 * Bộ lọc desktop nằm trong <aside> (viewport >= lg).
 */
export class ListingPage {
  readonly breadcrumb: Locator;
  readonly heading: Locator;
  readonly countText: Locator;
  readonly sortSelect: Locator;
  readonly sidebar: Locator;
  readonly priceFrom: Locator;
  readonly priceTo: Locator;
  readonly showMoreCategories: Locator;
  readonly cards: Locator;
  readonly loadMoreButton: Locator;
  readonly spinner: Locator;

  constructor(readonly page: Page) {
    this.breadcrumb = page.locator('main nav').first();
    this.heading = page.getByRole('heading', { level: 1 });
    this.countText = page.getByText(/^Hiển thị \d+ trên \d+ sản phẩm$/);
    this.sortSelect = page.locator('main section select');
    this.sidebar = page.locator('aside');
    this.priceFrom = this.sidebar.getByPlaceholder('Từ');
    this.priceTo = this.sidebar.getByPlaceholder('Đến');
    this.showMoreCategories = this.sidebar.getByRole('button', { name: 'Xem thêm +' });
    this.cards = page.locator('main .product-card');
    this.loadMoreButton = page.getByRole('button', { name: 'Xem thêm sản phẩm' });
    this.spinner = page.locator('main .animate-spin');
  }

  async open(path: string) {
    await this.page.goto(path);
  }

  /** Tiêu đề 1 nhóm lọc (bấm để mở/đóng), vd: "Phần trăm giảm". */
  filterSectionToggle(title: string): Locator {
    return this.sidebar.getByRole('button', { name: new RegExp(`^${title}`) });
  }

  categoryButton(name: string): Locator {
    return this.sidebar.locator('ul').getByRole('button', { name, exact: true });
  }

  categoryButtons(): Locator {
    return this.sidebar.locator('ul button');
  }

  /** Nút size trong nhóm "Kích cỡ" (nhóm lọc thứ 2). */
  sizeButtons(): Locator {
    return this.filterGroup('Kích cỡ').locator('div.flex-wrap > button');
  }

  sizeButton(label: string): Locator {
    return this.filterGroup('Kích cỡ').getByRole('button', { name: label, exact: true });
  }

  colorButtons(): Locator {
    return this.filterGroup('Màu sắc').locator('button[title]');
  }

  colorButton(name: string): Locator {
    return this.filterGroup('Màu sắc').locator(`button[title="${name}"]`);
  }

  discountLabel(label: string): Locator {
    return this.sidebar.locator('label', { hasText: label });
  }

  discountCheckbox(label: string): Locator {
    return this.sidebar.getByRole('checkbox', { name: label });
  }

  /** Nội dung (đã mở) của 1 nhóm lọc theo tiêu đề. */
  filterGroup(title: string): Locator {
    const toggle = this.page.getByRole('button', { name: new RegExp(`^${title}`) });
    return this.sidebar.locator('div.border-b').filter({ has: toggle });
  }

  cardTitle(card: Locator): Locator {
    return card.locator('h3');
  }

  /** Giá bán hiện tại của thẻ (span đầu tiên dạng "123.000đ"). */
  cardPrice(card: Locator): Locator {
    return card.locator('span').filter({ hasText: /^[\d.]+đ$/ }).first();
  }

  /** Nhãn giảm giá trên ảnh: "Giảm 33%" (Nam/Nữ) hoặc "-33%" (Trẻ em/Giảm giá). */
  cardDiscountBadge(card: Locator): Locator {
    return card.locator('a').getByText(/^(Giảm |-)\d+%$/);
  }

  cardLink(card: Locator): Locator {
    return card.locator('a[href^="/product/"]').first();
  }

  cardAddToCart(card: Locator): Locator {
    return card.getByRole('button', { name: 'Thêm vào giỏ' });
  }

  cardViewDetail(card: Locator): Locator {
    return card.getByRole('button', { name: 'Xem chi tiết' });
  }

  /** Nút tim (yêu thích) trên ảnh - nút còn lại trong link ngoài 2 nút overlay. */
  cardFavorite(card: Locator): Locator {
    return card.locator('a button').filter({ hasNotText: /Thêm vào giỏ|Xem chi tiết/ });
  }

  pageButton(n: number): Locator {
    return this.page.locator('main section').getByRole('button', { name: String(n), exact: true });
  }

  /** Nút trang sau dạng icon Material ("navigate_next"). */
  nextPageButton(): Locator {
    return this.page.locator('main section').getByRole('button', { name: 'navigate_next', exact: true });
  }

  emptyState(text: string): Locator {
    return this.page.locator('main').getByText(text, { exact: true });
  }
}
