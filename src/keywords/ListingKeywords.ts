import { Locator, Page, expect } from '@playwright/test';
import type { ApiClient } from '@api/ApiClient';
import type { PageObjects } from '@pages/PageObjects';
import { ListingPage } from '@pages/storefront/ListingPage';
import { SearchResultsPage } from '@pages/storefront/SearchResultsPage';
import { BaseKeywords } from './BaseKeywords';

const EMPTY_LISTING = /^Không (tìm thấy|có) sản phẩm/;

/** Đổi "1.234.000đ" -> 1234000. */
const toNumber = (text: string) => Number(text.replace(/[^\d]/g, ''));

/** Trang danh sách sản phẩm: Nam/Nữ/Trẻ em/Giảm giá, bộ lọc, sắp xếp, phân trang, trang /search. */
export class ListingKeywords extends BaseKeywords {
  private readonly listing: ListingPage;
  private readonly results: SearchResultsPage;
  /** URL các request GET danh sách sản phẩm (/api/products...) - để kiểm tra tham số lọc. */
  private readonly productRequests: URL[] = [];
  /** href của thẻ sản phẩm vừa thao tác (để kiểm tra điều hướng). */
  private lastCardHref = '';

  constructor(page: Page, po: PageObjects, api: ApiClient) {
    super(page, po, api);
    this.listing = new ListingPage(page);
    this.results = new SearchResultsPage(page);
    page.on('request', (req) => {
      const url = new URL(req.url());
      if (req.method() === 'GET' && /\/api\/products(\/kids)?$/.test(url.pathname)) this.productRequests.push(url);
    });
  }

  // ---------------------------------------------------------------------------
  // /nam, /nu, /tre-em, /giam-gia
  // ---------------------------------------------------------------------------

  /** Mở trang danh sách (vd: "/nam") và chờ tải xong (có sản phẩm hoặc thông báo rỗng). */
  async openListing(path: string) {
    await this.step(`Mở trang danh sách ${path}`, async () => {
      await this.listing.open(path);
      await this.waitListingSettled();
    });
  }

  /** Kiểm tra đầu trang danh sách: breadcrumb "Trang chủ > {mục}", tiêu đề h1, đoạn mô tả. */
  async verifyListingHeader(heading: string, breadcrumb: string, description: string) {
    await this.step(`Kiểm tra đầu trang "${heading}"`, async () => {
      await expect(this.listing.heading).toHaveText(heading);
      await expect(this.listing.breadcrumb.getByRole('link', { name: 'Trang chủ' })).toHaveAttribute('href', '/');
      await expect(this.listing.breadcrumb.locator('span').last()).toHaveText(breadcrumb);
      await expect(this.page.getByText(description)).toBeVisible();
    });
  }

  /** Kiểm tra dòng "Hiển thị n trên t sản phẩm": n = số thẻ đang hiển thị và n <= t. */
  async verifyCountMatchesCards() {
    await this.step('Kiểm tra "Hiển thị n trên t sản phẩm" khớp số thẻ', async () => {
      await this.waitListingSettled();
      const [, shown, total] = (await this.listing.countText.textContent())!.match(/Hiển thị (\d+) trên (\d+)/)!.map(Number);
      await expect(this.listing.cards).toHaveCount(shown);
      expect(shown).toBeLessThanOrEqual(total);
    });
  }

  /** Kiểm tra chính xác dòng "Hiển thị n trên t sản phẩm". */
  async verifyCountText(text: string) {
    await this.step(`Kiểm tra "${text}"`, async () => {
      await expect(this.listing.countText).toHaveText(text);
    });
  }

  /** Kiểm tra các lựa chọn sắp xếp (theo thứ tự) và lựa chọn đang được chọn. */
  async verifySortOptions(options: string[], selected: string) {
    await this.step(`Kiểm tra sắp xếp: ${options.join(' / ')} (đang chọn "${selected}")`, async () => {
      await expect(this.listing.sortSelect.locator('option')).toHaveText(options);
      const value = await this.listing.sortSelect.inputValue();
      await expect(this.listing.sortSelect.locator(`option[value="${value}"]`)).toHaveText(selected);
    });
  }

  /** Chọn kiểu sắp xếp theo nhãn, vd: "Giá: Thấp → Cao". */
  async sortBy(option: string) {
    await this.step(`Sắp xếp theo "${option}"`, async () => {
      await this.listing.sortSelect.selectOption({ label: option });
    });
  }

  /** Kiểm tra giá trên các thẻ sản phẩm đã sắp xếp: "asc" tăng dần, "desc" giảm dần. */
  async verifyPricesSorted(order: 'asc' | 'desc') {
    await this.step(`Kiểm tra giá sắp xếp ${order === 'asc' ? 'tăng' : 'giảm'} dần`, async () => {
      await this.expectSorted(() => this.readPrices(this.listing.cards, (c) => this.listing.cardPrice(c)), order);
    });
  }

  /** Kiểm tra các nút danh mục đang hiển thị trong bộ lọc (theo thứ tự). */
  async verifyCategoryOptions(names: string[]) {
    await this.step(`Kiểm tra danh mục lọc: ${names.join(', ')}`, async () => {
      await expect(this.listing.categoryButtons()).toHaveText(names);
    });
  }

  /** Bấm "Xem thêm +" trong nhóm danh mục để hiện các danh mục còn lại. */
  async showMoreCategories() {
    await this.step('Bấm "Xem thêm +" ở danh mục', async () => {
      await this.listing.showMoreCategories.click();
      await expect(this.listing.showMoreCategories).toBeHidden();
    });
  }

  /** Bấm 1 danh mục trong bộ lọc và kiểm tra nút được đánh dấu chọn. */
  async selectCategory(name: string) {
    await this.step(`Lọc danh mục "${name}"`, async () => {
      await this.listing.categoryButton(name).click();
      await expect(this.listing.categoryButton(name)).toHaveClass(/font-semibold/);
    });
  }

  /** Kiểm tra các nút size trong bộ lọc "Kích cỡ". */
  async verifySizeOptions(sizes: string[]) {
    await this.step(`Kiểm tra size lọc: ${sizes.join(', ')}`, async () => {
      await expect(this.listing.sizeButtons()).toHaveText(sizes);
    });
  }

  /** Bấm 1 size trong bộ lọc "Kích cỡ". */
  async selectSizeFilter(size: string) {
    await this.step(`Lọc size "${size}"`, async () => {
      await this.listing.sizeButton(size).click();
    });
  }

  /** Kiểm tra các ô màu trong bộ lọc "Màu sắc" (theo thuộc tính title). */
  async verifyColorOptions(colors: string[]) {
    await this.step(`Kiểm tra màu lọc: ${colors.join(', ')}`, async () => {
      const titles = await this.listing.colorButtons().evaluateAll((els) => els.map((e) => e.getAttribute('title')));
      expect(titles).toEqual(colors);
    });
  }

  /** Bấm 1 màu trong bộ lọc "Màu sắc" (theo title) và kiểm tra có dấu tích. */
  async selectColorFilter(color: string) {
    await this.step(`Lọc màu "${color}"`, async () => {
      await this.listing.colorButton(color).click();
      await expect(this.listing.colorButton(color).locator('svg')).toBeVisible();
    });
  }

  /** Kiểm tra giá trị mặc định 2 ô khoảng giá "Từ" / "Đến". */
  async verifyPriceInputs(from: string, to: string) {
    await this.step(`Kiểm tra khoảng giá mặc định ${from} - ${to}`, async () => {
      await expect(this.listing.priceFrom).toHaveValue(from);
      await expect(this.listing.priceTo).toHaveValue(to);
    });
  }

  /** Nhập khoảng giá "Từ" - "Đến" (vd: "300000", "600000"); bộ lọc áp dụng khi rời ô nhập. */
  async setPriceRange(from: string, to: string) {
    await this.step(`Lọc giá ${from} - ${to}`, async () => {
      // Mỗi ô gọi API riêng khi blur và app không hủy request cũ: nếu nhập liền 2 ô, response cũ
      // (chỉ có min_price) có thể về sau và ghi đè kết quả. Đợi từng request xong để test ổn định.
      const serverSide = !this.page.url().includes('/giam-gia'); // trang Giảm giá lọc phía client
      const applyAndWait = async (input: typeof this.listing.priceFrom, value: string, param: string) => {
        const response = serverSide
          ? this.page.waitForResponse((r) => r.url().includes('/api/products') && r.url().includes(param))
          : Promise.resolve();
        await input.fill(value);
        await input.blur();
        await response;
        await this.waitListingSettled();
      };
      await applyAndWait(this.listing.priceFrom, from, 'min_price=');
      await applyAndWait(this.listing.priceTo, to, 'max_price=');
    });
  }

  /** Kiểm tra mọi giá đang hiển thị nằm trong khoảng [min, max]. */
  async verifyPricesWithin(min: number, max: number) {
    await this.step(`Kiểm tra mọi giá trong khoảng ${min} - ${max}`, async () => {
      await expect
        .poll(
          async () => {
            await this.waitListingSettled();
            const prices = await this.readPrices(this.listing.cards, (c) => this.listing.cardPrice(c));
            return prices.filter((p) => p < min || p > max);
          },
          { timeout: 10_000, message: 'Có giá nằm ngoài khoảng lọc' },
        )
        .toEqual([]);
    });
  }

  /** Tick 1 mức "Phần trăm giảm" (tự mở nhóm lọc nếu đang đóng), vd: "Giảm 30%". */
  async selectDiscount(label: string) {
    await this.step(`Lọc "${label}"`, async () => {
      const toggle = this.listing.filterSectionToggle('Phần trăm giảm');
      if ((await toggle.textContent())?.includes('+')) await toggle.click();
      await this.listing.discountLabel(label).click();
      await expect(this.listing.discountCheckbox(label)).toBeChecked();
    });
  }

  /** Kiểm tra mọi thẻ đang hiển thị có nhãn giảm giá >= phần trăm cho trước. */
  async verifyDiscountAtLeast(percent: number) {
    await this.step(`Kiểm tra mọi sản phẩm giảm >= ${percent}%`, async () => {
      await expect
        .poll(
          async () => {
            await this.waitListingSettled();
            const bad: string[] = [];
            for (const card of await this.listing.cards.all()) {
              const badges = await this.listing.cardDiscountBadge(card).allTextContents();
              const value = badges.length ? toNumber(badges[0]) : 0;
              if (value < percent) bad.push(`${await this.listing.cardTitle(card).textContent()} (${value}%)`);
            }
            return bad;
          },
          { timeout: 10_000, message: `Có sản phẩm giảm ít hơn ${percent}%` },
        )
        .toEqual([]);
    });
  }

  /** Kiểm tra đã gọi API danh sách sản phẩm với các tham số query, vd: {"min_price":"300000"}. */
  async verifyListRequest(params: Record<string, string>) {
    await this.step(`Kiểm tra API danh sách được gọi với ${JSON.stringify(params)}`, async () => {
      const matches = () =>
        this.productRequests.some((u) => Object.entries(params).every(([k, v]) => u.searchParams.get(k) === v));
      await expect
        .poll(matches, {
          timeout: 5_000,
          message: `Không có request /api/products khớp ${JSON.stringify(params)}. Đã gọi:\n${this.productRequests
            .map((u) => u.pathname + u.search)
            .join('\n')}`,
        })
        .toBe(true);
    });
  }

  /** Kiểm tra danh sách có ít nhất 1 sản phẩm và dòng "Hiển thị n trên t" với n > 0. */
  async verifyProductsShown() {
    await this.step('Kiểm tra danh sách có sản phẩm', async () => {
      await expect(this.listing.countText).toHaveText(/^Hiển thị [1-9]\d* trên [1-9]\d* sản phẩm$/);
      await expect(this.listing.cards.first()).toBeVisible();
    });
  }

  /** Kiểm tra trạng thái rỗng của trang danh sách (thông báo + "Hiển thị 0 trên 0 sản phẩm"). */
  async verifyEmptyListing(text: string) {
    await this.step(`Kiểm tra danh sách rỗng: "${text}"`, async () => {
      await expect(this.listing.emptyState(text)).toBeVisible();
      await expect(this.listing.cards).toHaveCount(0);
      await expect(this.listing.countText).toHaveText('Hiển thị 0 trên 0 sản phẩm');
    });
  }

  /** Bấm số trang ở phân trang. */
  async goToPage(n: number) {
    await this.step(`Chuyển tới trang ${n}`, async () => {
      await this.listing.pageButton(n).click();
    });
  }

  /** Bấm nút trang sau (icon "navigate_next"). */
  async clickNextPage() {
    await this.step('Bấm trang sau', async () => {
      await this.listing.nextPageButton().click();
    });
  }

  /** Bấm nút "Xem thêm sản phẩm". */
  async clickLoadMore() {
    await this.step('Bấm "Xem thêm sản phẩm"', async () => {
      await this.listing.loadMoreButton.click();
    });
  }

  /** Rê chuột vào thẻ sản phẩm đầu tiên và bấm "Thêm vào giỏ" ở lớp phủ. */
  async addFirstCardToCart() {
    await this.step('Bấm "Thêm vào giỏ" trên thẻ đầu tiên', async () => {
      const card = await this.firstCard();
      await card.hover();
      await this.listing.cardAddToCart(card).click();
    });
  }

  /** Rê chuột vào thẻ sản phẩm đầu tiên và bấm "Xem chi tiết" ở lớp phủ. */
  async viewFirstCardDetail() {
    await this.step('Bấm "Xem chi tiết" trên thẻ đầu tiên', async () => {
      const card = await this.firstCard();
      await card.hover();
      await this.listing.cardViewDetail(card).click();
    });
  }

  /** Bấm nút tim (yêu thích) trên thẻ sản phẩm đầu tiên. */
  async clickFirstCardFavorite() {
    await this.step('Bấm nút yêu thích trên thẻ đầu tiên', async () => {
      const card = await this.firstCard();
      await card.hover();
      await this.listing.cardFavorite(card).click();
    });
  }

  /** Kiểm tra đã chuyển tới trang chi tiết của thẻ sản phẩm vừa thao tác. */
  async verifyOpenedLastCard() {
    await this.step(`Kiểm tra đã mở ${this.lastCardHref}`, async () => {
      expect(this.lastCardHref).toMatch(/^\/product\/.+/);
      await expect(this.page).toHaveURL(this.lastCardHref);
      await expect(this.po.product.title).toBeVisible();
    });
  }

  // ---------------------------------------------------------------------------
  // /search
  // ---------------------------------------------------------------------------

  /** Mở trang /search với query string (vd: "?category=vay", "" = tất cả) và chờ tải xong. */
  async openSearchResults(query: string) {
    await this.step(`Mở trang /search${query}`, async () => {
      await this.results.open(query);
      await expect(this.results.subtitle).not.toHaveText('Đang tải...');
    });
  }

  /** Kiểm tra tiêu đề h1 của trang /search. */
  async verifySearchTitle(heading: string) {
    await this.step(`Kiểm tra tiêu đề "${heading}"`, async () => {
      await expect(this.results.heading).toHaveText(heading);
    });
  }

  /** Kiểm tra breadcrumb trang /search theo thứ tự (bỏ icon). */
  async verifySearchBreadcrumbs(items: string[]) {
    await this.step(`Kiểm tra breadcrumb: ${items.join(' > ')}`, async () => {
      await expect(this.results.breadcrumb.locator(':scope > a, :scope > span:not(.material-symbols-outlined)')).toHaveText(items);
    });
  }

  /** Kiểm tra 1 mục breadcrumb là link trỏ đúng đường dẫn. */
  async verifySearchBreadcrumbLink(name: string, href: string) {
    await this.step(`Kiểm tra breadcrumb "${name}" -> ${href}`, async () => {
      await expect(this.results.breadcrumbLink(name)).toHaveAttribute('href', href);
    });
  }

  /** Kiểm tra dòng "{tổng} sản phẩm" và số thẻ trên trang (tối đa 12/trang). */
  async verifySearchSubtitleMatches() {
    await this.step('Kiểm tra "{tổng} sản phẩm" khớp danh sách', async () => {
      await expect(this.results.subtitle).toHaveText(/^\d+ sản phẩm$/);
      const total = toNumber((await this.results.subtitle.textContent()) ?? '');
      await expect(this.results.cards).toHaveCount(Math.min(total, 12));
    });
  }

  /** Kiểm tra chip bộ lọc đang áp dụng và link nút đóng (close). */
  async verifySearchChip(text: string, closeHref: string) {
    await this.step(`Kiểm tra chip "${text}" (đóng -> ${closeHref})`, async () => {
      await expect(this.results.chip(text)).toBeVisible();
      await expect(this.results.chipClose(text)).toHaveAttribute('href', closeHref);
    });
  }

  /** Bấm nút đóng (close) trên 1 chip bộ lọc. */
  async closeSearchChip(text: string) {
    await this.step(`Bỏ chip "${text}"`, async () => {
      await this.results.chipClose(text).click();
    });
  }

  /** Kiểm tra các lựa chọn sắp xếp của trang /search. */
  async verifySearchSortOptions(options: string[]) {
    await this.step(`Kiểm tra sắp xếp /search: ${options.join(' / ')}`, async () => {
      await expect(this.results.sortSelect.locator('option')).toHaveText(options);
    });
  }

  /** Chọn kiểu sắp xếp trên trang /search theo nhãn. */
  async sortSearchBy(option: string) {
    await this.step(`Sắp xếp /search theo "${option}"`, async () => {
      await this.results.sortSelect.selectOption({ label: option });
    });
  }

  /** Kiểm tra giá trên trang /search đã sắp xếp ("asc"/"desc"). */
  async verifySearchPricesSorted(order: 'asc' | 'desc') {
    await this.step(`Kiểm tra giá /search ${order === 'asc' ? 'tăng' : 'giảm'} dần`, async () => {
      await this.expectSorted(() => this.readPrices(this.results.cards, (c) => this.results.cardPrice(c)), order);
    });
  }

  /** Kiểm tra trạng thái rỗng của /search: tiêu đề, gợi ý và nút "Xem tất cả sản phẩm". */
  async verifySearchEmpty(hint: string) {
    await this.step(`Kiểm tra /search rỗng: "${hint}"`, async () => {
      await expect(this.results.emptyHeading).toBeVisible();
      await expect(this.results.emptyHint(hint)).toBeVisible();
      await expect(this.results.subtitle).toHaveText('0 sản phẩm');
      await expect(this.results.viewAllLink).toHaveAttribute('href', '/search');
      await expect(this.results.sortSelect).toHaveCount(0);
    });
  }

  /** Bấm "Xem tất cả sản phẩm" ở trạng thái rỗng. */
  async clickViewAllProducts() {
    await this.step('Bấm "Xem tất cả sản phẩm"', async () => {
      await this.results.viewAllLink.click();
    });
  }

  /** Kiểm tra trạng thái lỗi của /search: "Đã xảy ra lỗi" + thông báo + nút "Thử lại". */
  async verifySearchError(message: string) {
    await this.step(`Kiểm tra /search báo lỗi "${message}"`, async () => {
      await expect(this.results.errorHeading).toBeVisible();
      await expect(this.results.emptyHint(message)).toBeVisible();
      await expect(this.results.retryButton).toBeVisible();
    });
  }

  /** Bấm số trang trên phân trang của /search. */
  async goToSearchPage(n: number) {
    await this.step(`/search: chuyển tới trang ${n}`, async () => {
      await this.results.pageButton(n).click();
    });
  }

  /** Bấm nút trang sau (chevron_right) trên /search. */
  async clickSearchNextPage() {
    await this.step('/search: bấm trang sau', async () => {
      await this.results.nextPageButton().click();
    });
  }

  /** Kiểm tra trang hiện tại trên phân trang /search (nút được tô đỏ) và nút trang trước bật/tắt. */
  async verifySearchActivePage(n: number) {
    await this.step(`/search: kiểm tra đang ở trang ${n}`, async () => {
      await expect(this.results.pageButton(n)).toHaveClass(/bg-\[#DA291C\]/);
      await (n === 1 ? expect(this.results.prevPageButton()).toBeDisabled() : expect(this.results.prevPageButton()).toBeEnabled());
    });
  }

  /** Gõ từ khóa vào ô tìm kiếm header và chờ API gợi ý (/api/products/search) trả về đúng status. */
  async typeHeaderSearchExpectingStatus(keyword: string, status: number) {
    await this.step(`Gõ "${keyword}" ở header, API gợi ý trả ${status}`, async () => {
      const response = this.page.waitForResponse((r) => r.url().includes('/api/products/search'));
      await this.po.header.typeSearch(keyword);
      expect((await response).status()).toBe(status);
    });
  }

  /** Kiểm tra dropdown gợi ý tìm kiếm trên header KHÔNG hiển thị. */
  async verifyHeaderSuggestionsHidden() {
    await this.step('Kiểm tra không hiện dropdown gợi ý', async () => {
      await expect(this.po.header.searchSeeMore).toHaveCount(0);
      await expect(this.po.header.searchNoResult).toHaveCount(0);
    });
  }

  // ---------------------------------------------------------------------------
  // Nội bộ
  // ---------------------------------------------------------------------------

  private async waitListingSettled() {
    await expect(this.listing.countText).toBeVisible();
    await expect(this.listing.spinner).toHaveCount(0);
    await expect(this.listing.cards.first().or(this.page.locator('main').getByText(EMPTY_LISTING))).toBeVisible();
  }

  private async firstCard(): Promise<Locator> {
    await this.waitListingSettled();
    const card = this.listing.cards.first();
    this.lastCardHref = (await this.listing.cardLink(card).getAttribute('href')) ?? '';
    return card;
  }

  private async readPrices(cards: Locator, price: (card: Locator) => Locator): Promise<number[]> {
    const all = await cards.all();
    const values: number[] = [];
    for (const c of all) values.push(toNumber((await price(c).textContent()) ?? ''));
    return values;
  }

  private async expectSorted(read: () => Promise<number[]>, order: 'asc' | 'desc') {
    await expect
      .poll(
        async () => {
          const prices = await read();
          if (prices.length < 2) return `chỉ có ${prices.length} giá`;
          const sorted = [...prices].sort((a, b) => (order === 'asc' ? a - b : b - a));
          return prices.every((p, i) => p === sorted[i]) ? 'sorted' : prices.join(', ');
        },
        { timeout: 10_000, message: `Giá chưa sắp xếp ${order}` },
      )
      .toBe('sorted');
  }
}
