import { Locator, Page } from '@playwright/test';

/**
 * Các khối trên trang chủ (pages/Home.jsx): banner, ưu đãi, SẢN PHẨM MỚI, HOMEWEAR/T-SHIRT/VÁY,
 * bộ sưu tập, C-LIVE, tin tức. Newsletter + Footer nằm ở `SiteChrome`.
 */
export class HomeSections {
  // ---- Banner (components/Banner.jsx) - khối đầu tiên trong <main> ----
  readonly banner: Locator;
  readonly bannerSlides: Locator;
  readonly bannerPrev: Locator;
  readonly bannerNext: Locator;
  readonly bannerDots: Locator;

  // ---- Ưu đãi (components/VoucherSection.jsx) ----
  readonly voucherHeading: Locator;
  readonly voucherSection: Locator;
  readonly voucherCards: Locator;

  // ---- SẢN PHẨM MỚI ----
  readonly newProductsHeading: Locator;
  readonly newProductsBlock: Locator;
  readonly newProductsViewAll: Locator;
  readonly newProductsTabs: Locator;
  readonly newProductsScroll: Locator;
  readonly newProductsPrev: Locator;
  readonly newProductsNext: Locator;

  // ---- Bộ sưu tập (components/CollectionSection.jsx) ----
  readonly collectionTiles: Locator;

  // ---- C-LIVE ----
  readonly cliveHeading: Locator;
  readonly cliveImage: Locator;

  // ---- Tin tức (components/BlogSection.jsx) ----
  readonly blogHeading: Locator;
  readonly blogSection: Locator;
  readonly blogSeeMore: Locator;
  readonly blogEmpty: Locator;
  readonly blogFeaturedTitle: Locator;
  readonly blogSecondaryTitles: Locator;

  constructor(readonly page: Page) {
    this.banner = page.locator('main > div').first();
    this.bannerSlides = this.banner.locator(':scope > a');
    this.bannerPrev = this.banner.locator(':scope > button').nth(0);
    this.bannerNext = this.banner.locator(':scope > button').nth(1);
    this.bannerDots = this.banner.locator(':scope > div > button');

    this.voucherHeading = page.getByRole('heading', { name: 'ƯU ĐÃI NỔI BẬT' });
    this.voucherSection = page.locator('section').filter({ has: this.voucherHeading });
    this.voucherCards = this.voucherSection.locator('.grid > div');

    this.newProductsHeading = page.getByRole('heading', { name: 'SẢN PHẨM MỚI' });
    this.newProductsBlock = page.locator('main .container').filter({ has: this.newProductsHeading });
    this.newProductsViewAll = this.newProductsBlock.getByRole('link', { name: /Xem tất cả/ });
    this.newProductsTabs = this.newProductsBlock.locator('.border-b > button');
    this.newProductsScroll = page.locator('#new-products-scroll');
    this.newProductsPrev = this.newProductsBlock.locator('.group\\/carousel > button').nth(0);
    this.newProductsNext = this.newProductsBlock.locator('.group\\/carousel > button').nth(1);

    this.collectionTiles = page.locator('main section .grid-cols-3 > div');

    this.cliveHeading = page.getByRole('heading', { name: 'C-LIVE - NHƯ MUA SẮM TẠI CỬA HÀNG' });
    this.cliveImage = page.getByRole('img', { name: 'C-LIVE' });

    this.blogHeading = page.getByRole('heading', { name: 'Tin tức thời trang' });
    this.blogSection = page.locator('section').filter({ has: this.blogHeading });
    this.blogSeeMore = this.blogSection.getByRole('link', { name: 'Xem thêm' });
    this.blogEmpty = this.blogSection.getByText('Chưa có tin tức thời trang nào');
    this.blogFeaturedTitle = this.blogSection.locator('h3');
    this.blogSecondaryTitles = this.blogSection.locator('h4');
  }

  /** Slide đang hiển thị (opacity-100). */
  activeSlide(): Locator {
    return this.bannerSlides.and(this.page.locator('.opacity-100'));
  }

  /** Nút "Khám phá ngay" của chữ đè trên banner (chỉ có ở slide thứ 3 trở đi). */
  bannerOverlayCta(index: number): Locator {
    return this.bannerSlides.nth(index).locator('a', { hasText: 'Khám phá ngay' });
  }

  bannerOverlayTitle(index: number): Locator {
    return this.bannerSlides.nth(index).locator('h2');
  }

  voucherCard(title: string): Locator {
    return this.voucherCards.filter({ has: this.page.locator('p', { hasText: title }) });
  }

  newProductsTab(name: string): Locator {
    return this.newProductsTabs.filter({ hasText: new RegExp(`^${name}$`) });
  }

  /** Thẻ sản phẩm (ProductCard) trong carousel SẢN PHẨM MỚI. */
  newProductCards(): Locator {
    return this.newProductsScroll.locator('a[href^="/product/"]');
  }

  /** Khối banner + lưới sản phẩm HOMEWEAR / T-SHIRT / VÁY (theo tiêu đề h2). */
  promoBlock(title: string): Locator {
    return this.page.locator('main > section').filter({ has: this.page.getByRole('heading', { name: title, exact: true }) });
  }

  promoBlockCards(title: string): Locator {
    return this.promoBlock(title).locator('.grid a[href^="/product/"]');
  }

  promoBlockLink(title: string, name: string): Locator {
    return this.promoBlock(title).getByRole('link', { name, exact: true });
  }

  collectionTile(title: string): Locator {
    return this.collectionTiles.filter({ has: this.page.locator('h3', { hasText: title }) });
  }

  collectionCta(title: string): Locator {
    return this.collectionTile(title).locator('a');
  }

  /** Thẻ ProductCard bất kỳ trên trang theo tên sản phẩm. */
  productCard(name: string): Locator {
    return this.page.locator('a[href^="/product/"]').filter({ has: this.page.locator('h3', { hasText: name }) });
  }

  /** Nút thêm nhanh vào giỏ (icon) trên ProductCard - hiện khi hover. */
  quickAddButton(name: string): Locator {
    return this.productCard(name).first().locator('button.absolute');
  }

  /** Link bất kỳ trong <main> theo tên (dùng để kiểm tra link chết). */
  mainLink(name: string): Locator {
    return this.page.locator('main').getByRole('link', { name, exact: true });
  }
}
