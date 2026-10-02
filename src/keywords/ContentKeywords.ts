import { expect } from '@playwright/test';
import { HomeSections } from '@pages/storefront/HomeSections';
import { SiteChrome } from '@pages/storefront/SiteChrome';
import { BlogDetailPage, BlogListPage } from '@pages/storefront/BlogPages';
import type { BlogArticle, BlogArticleExpect } from '@data/storefront.types';
import { detectReload, readCart } from '@utils/storage';
import { BaseKeywords } from './BaseKeywords';

type VoucherExpect = { title: string; description: string; condition: string; validity: string };

/** Nội dung: các khối trang chủ, blog, trang tĩnh, footer, newsletter. */
export class ContentKeywords extends BaseKeywords {
  private readonly home = new HomeSections(this.page);
  private readonly chrome = new SiteChrome(this.page);
  private readonly blogList = new BlogListPage(this.page);
  private readonly blogDetail = new BlogDetailPage(this.page);

  // ---------------------------------------------------------------------------
  // Trang chủ
  // ---------------------------------------------------------------------------

  /** Mock GET /api/home bằng dữ liệu cho trước (voucher có "expiresInDays" được đổi thành ngày hết hạn tính từ hôm nay). */
  async mockHomeData(response: { success: boolean; data: Record<string, any> }) {
    await this.step('Mock dữ liệu trang chủ (GET /api/home)', async () => {
      const body = structuredClone(response);
      for (const v of body.data?.vouchers ?? []) {
        if (typeof v.expiresInDays === 'number') {
          v.expiry = new Date(Date.now() + v.expiresInDays * 86_400_000).toISOString();
          v.valid_until = v.expiry;
        }
      }
      await this.page.route('**/api/home', (route) =>
        route.request().method() === 'GET' ? route.fulfill({ json: body }) : route.fallback(),
      );
    });
  }

  /** Mở trang chủ và chờ khối SẢN PHẨM MỚI hiển thị (không yêu cầu có sản phẩm). */
  async openHomePage() {
    await this.step('Mở trang chủ (chờ các khối nội dung)', async () => {
      await this.page.goto('/');
      await expect(this.home.newProductsHeading).toBeVisible();
    });
  }

  /** Kiểm tra trang chủ có đủ các khối theo tiêu đề h2, đúng thứ tự. */
  async verifyHomeSections(titles: string[]) {
    await this.step(`Kiểm tra ${titles.length} khối nội dung trang chủ`, async () => {
      await expect(this.page.locator('main h2').filter({ visible: true })).toContainText(titles);
    });
  }

  /** Kiểm tra số slide banner và số chấm điều hướng. */
  async verifyBannerSlideCount(count: number) {
    await this.step(`Kiểm tra banner có ${count} slide`, async () => {
      await expect(this.home.bannerSlides).toHaveCount(count);
      await expect(this.home.bannerDots).toHaveCount(count);
    });
  }

  /** Kiểm tra slide banner đang hiển thị (đánh số từ 1). */
  async verifyActiveBannerSlide(slide: number) {
    await this.step(`Kiểm tra banner đang ở slide ${slide}`, async () => {
      await expect(this.home.bannerSlides.nth(slide - 1)).toHaveClass(/opacity-100/);
      await expect(this.home.activeSlide()).toHaveCount(1);
      await expect(this.home.bannerDots.nth(slide - 1)).toHaveClass(/w-8/);
    });
  }

  /** Bấm nút mũi tên banner: "next" hoặc "prev". */
  async clickBannerArrow(direction: 'next' | 'prev') {
    await this.step(`Bấm mũi tên banner ${direction === 'next' ? 'sau' : 'trước'}`, async () => {
      await (direction === 'next' ? this.home.bannerNext : this.home.bannerPrev).click();
    });
  }

  /** Bấm chấm điều hướng banner thứ n (đánh số từ 1). */
  async clickBannerDot(slide: number) {
    await this.step(`Bấm chấm banner số ${slide}`, async () => {
      await this.home.bannerDots.nth(slide - 1).click();
    });
  }

  /** Cố định đồng hồ trình duyệt (banner không tự chuyển slide) - gọi TRƯỚC khi mở trang. */
  async freezeClock() {
    await this.step('Cố định đồng hồ trình duyệt', async () => {
      await this.page.clock.install();
    });
  }

  /** Cho đồng hồ (đã cố định bằng freezeClock) chạy 4 giây và kiểm tra banner tự chuyển sang slide kế tiếp. */
  async verifyBannerAutoplay(toSlide: number) {
    await this.step(`Kiểm tra banner tự chuyển sang slide ${toSlide} sau 4 giây`, async () => {
      await expect(this.home.bannerSlides.nth(toSlide - 1)).not.toHaveClass(/opacity-100/);
      await this.page.clock.runFor(4_100);
      await expect(this.home.bannerSlides.nth(toSlide - 1)).toHaveClass(/opacity-100/);
    });
  }

  /** Kiểm tra link (href) của từng slide banner theo thứ tự. */
  async verifyBannerSlideLinks(hrefs: string[]) {
    await this.step(`Kiểm tra link các slide banner: ${hrefs.join(', ')}`, async () => {
      for (const [i, href] of hrefs.entries()) {
        await expect(this.home.bannerSlides.nth(i)).toHaveAttribute('href', href);
      }
    });
  }

  /** Kiểm tra chữ đè trên slide banner (đánh số từ 1): tiêu đề + nút "Khám phá ngay" trỏ đúng link. */
  async verifyBannerOverlay(slide: number, title: string, href: string) {
    await this.step(`Kiểm tra chữ trên slide ${slide}: "${title}" -> ${href}`, async () => {
      await expect(this.home.bannerOverlayTitle(slide - 1)).toHaveText(title);
      await expect(this.home.bannerOverlayCta(slide - 1)).toHaveAttribute('href', href);
    });
  }

  /** Kiểm tra 1 thẻ voucher trong khối "ƯU ĐÃI NỔI BẬT" (tiêu đề, mô tả, điều kiện, hạn dùng). */
  async verifyVoucher(voucher: VoucherExpect) {
    await this.step(`Kiểm tra voucher "${voucher.title}"`, async () => {
      const card = this.home.voucherCard(voucher.title);
      await expect(card).toHaveCount(1);
      await expect(card).toContainText(voucher.description);
      await expect(card).toContainText(voucher.condition);
      await expect(card).toContainText(voucher.validity);
      await expect(card.getByRole('button', { name: 'Dùng mã' })).toBeVisible();
    });
  }

  /** Bấm "Dùng mã" của 1 voucher. */
  async useVoucher(title: string) {
    await this.step(`Bấm "Dùng mã" voucher "${title}"`, async () => {
      await this.home.voucherCard(title).getByRole('button', { name: 'Dùng mã' }).click();
    });
  }

  /** Kiểm tra mã voucher đã được lưu tạm vào sessionStorage (pendingVoucher). */
  async verifyPendingVoucher(code: string) {
    await this.step(`Kiểm tra voucher chờ áp dụng = ${code}`, async () => {
      await expect
        .poll(() => this.page.evaluate(() => JSON.parse(sessionStorage.getItem('pendingVoucher') || 'null')?.code ?? null))
        .toBe(code);
    });
  }

  /** Kiểm tra khối "ƯU ĐÃI NỔI BẬT" bị ẩn (không có voucher). */
  async verifyNoVoucherSection() {
    await this.step('Kiểm tra không hiển thị khối ƯU ĐÃI NỔI BẬT', async () => {
      await expect(this.home.voucherHeading).toHaveCount(0);
    });
  }

  /** Kiểm tra các tab của khối SẢN PHẨM MỚI, tab đầu đang được chọn. */
  async verifyNewProductTabs(tabs: string[]) {
    await this.step(`Kiểm tra tab SẢN PHẨM MỚI: ${tabs.join(', ')}`, async () => {
      await expect(this.home.newProductsTabs).toHaveText(tabs);
      await expect(this.home.newProductsTab(tabs[0])).toHaveClass(/text-\[#DA291C\]/);
    });
  }

  /** Bấm 1 tab trong khối SẢN PHẨM MỚI. */
  async selectNewProductTab(tab: string) {
    await this.step(`Chọn tab "${tab}" ở SẢN PHẨM MỚI`, async () => {
      await this.home.newProductsTab(tab).click();
    });
  }

  /** Kiểm tra tab được chọn và danh sách SẢN PHẨM MỚI đã lọc: có sản phẩm visible, không còn sản phẩm hidden. */
  async verifyNewProductsFiltered(tab: string, visible: string, hidden: string) {
    await this.step(`Kiểm tra tab "${tab}" lọc sản phẩm: có "${visible}", không có "${hidden}"`, async () => {
      await expect(this.home.newProductsTab(tab)).toHaveClass(/text-\[#DA291C\]/, { timeout: 3_000 });
      await expect(this.home.newProductCards().filter({ hasText: visible }).first()).toBeVisible();
      await expect(this.home.newProductCards().filter({ hasText: hidden })).toHaveCount(0, { timeout: 3_000 });
    });
  }

  /** Kiểm tra số thẻ sản phẩm trong carousel SẢN PHẨM MỚI. */
  async verifyNewProductCount(count: number) {
    await this.step(`Kiểm tra SẢN PHẨM MỚI có ${count} sản phẩm`, async () => {
      await expect(this.home.newProductCards()).toHaveCount(count);
    });
  }

  /** Bấm mũi tên carousel SẢN PHẨM MỚI ("next"/"prev") và kiểm tra danh sách cuộn đúng chiều. */
  async scrollNewProducts(direction: 'next' | 'prev') {
    await this.step(`Cuộn carousel SẢN PHẨM MỚI (${direction})`, async () => {
      const scroller = this.home.newProductsScroll;
      const before = await scroller.evaluate((el) => el.scrollLeft);
      await (direction === 'next' ? this.home.newProductsNext : this.home.newProductsPrev).click();
      await expect
        .poll(() => scroller.evaluate((el) => el.scrollLeft), { message: `scrollLeft phải ${direction === 'next' ? 'tăng' : 'giảm'} từ ${before}` })
        [direction === 'next' ? 'toBeGreaterThan' : 'toBeLessThan'](before);
    });
  }

  /** Kiểm tra khối HOMEWEAR/T-SHIRT/VÁY: mô tả và số thẻ sản phẩm (tối đa 4). */
  async verifyPromoBlock(title: string, description: string, cardCount: number) {
    await this.step(`Kiểm tra khối "${title}" (${cardCount} sản phẩm)`, async () => {
      const block = this.home.promoBlock(title);
      await expect(block.getByText(description)).toBeVisible();
      await expect(this.home.promoBlockCards(title)).toHaveCount(cardCount);
      await expect(this.home.promoBlockLink(title, 'Khám phá ngay')).toBeVisible();
      await expect(block.getByRole('link', { name: 'Xem tất cả' })).toBeVisible();
    });
  }

  /** Kiểm tra 1 ô bộ sưu tập: tiêu đề, chữ trên nút CTA và link. */
  async verifyCollection(title: string, ctaText: string, href: string) {
    await this.step(`Kiểm tra bộ sưu tập "${title}" -> nút "${ctaText}" (${href})`, async () => {
      await expect(this.home.collectionTile(title)).toBeVisible();
      await expect(this.home.collectionCta(title)).toHaveAttribute('href', href);
      await expect(this.home.collectionCta(title)).toHaveText(ctaText);
    });
  }

  /** Kiểm tra khối C-LIVE: tiêu đề, ảnh và các đoạn chữ. */
  async verifyCLive(texts: string[]) {
    await this.step('Kiểm tra khối C-LIVE', async () => {
      await expect(this.home.cliveHeading).toBeVisible();
      await expect(this.home.cliveImage).toBeVisible();
      for (const t of texts) await expect(this.page.getByText(t, { exact: true })).toBeVisible();
    });
  }

  /** Kiểm tra khối "Tin tức thời trang": bài nổi bật + số bài phụ + nút "Xem thêm". */
  async verifyHomeNews(featuredTitle: string, secondaryCount: number) {
    await this.step(`Kiểm tra Tin tức thời trang: "${featuredTitle}" + ${secondaryCount} bài`, async () => {
      await expect(this.home.blogFeaturedTitle).toHaveText(featuredTitle);
      await expect(this.home.blogSecondaryTitles).toHaveCount(secondaryCount);
      await expect(this.home.blogSeeMore).toBeVisible();
    });
  }

  /** Kiểm tra link bài nổi bật trong khối Tin tức trỏ tới /blog/{slug}. */
  async verifyHomeNewsLink(title: string, slug: string) {
    await this.step(`Kiểm tra tin "${title}" -> /blog/${slug}`, async () => {
      // Ảnh và tiêu đề là 2 link riêng, cả 2 phải trỏ tới bài viết
      const links = this.home.blogSection.getByRole('link', { name: title });
      await expect(links).toHaveCount(2);
      for (const link of await links.all()) await expect(link).toHaveAttribute('href', `/blog/${slug}`);
    });
  }

  /** Kiểm tra khối Tin tức hiển thị trạng thái rỗng và ẩn nút "Xem thêm". */
  async verifyHomeNewsEmpty() {
    await this.step('Kiểm tra khối Tin tức rỗng', async () => {
      await expect(this.home.blogEmpty).toBeVisible();
      await expect(this.home.blogSeeMore).toHaveCount(0);
    });
  }

  /** Bấm "Xem thêm" của khối Tin tức thời trang. */
  async clickHomeNewsSeeMore() {
    await this.step('Bấm "Xem thêm" khối Tin tức', async () => {
      await this.home.blogSeeMore.click();
    });
  }

  /** Bấm 1 link trên trang chủ theo tên; section = tiêu đề khối chứa link (để trống = khối SẢN PHẨM MỚI). */
  async clickHomeLink(link: string, section?: string) {
    await this.step(`Bấm link "${link}"${section ? ` trong khối ${section}` : ''}`, async () => {
      const target = section
        ? this.home.promoBlock(section).getByRole('link', { name: link, exact: true })
        : this.home.newProductsBlock.getByRole('link', { name: link });
      await target.first().click();
    });
  }

  /** Kiểm tra trang đích đã render nội dung (có header, footer) - không phải trang trắng. */
  async verifyPageRendered() {
    await this.step('Kiểm tra trang đích hiển thị nội dung (header + footer)', async () => {
      await expect(this.chrome.page.locator('header').first()).toBeVisible();
      await expect(this.chrome.footer).toBeVisible();
    });
  }

  /** Bấm icon thêm nhanh vào giỏ trên thẻ sản phẩm (ProductCard) theo tên. */
  async quickAddToCart(productName: string) {
    await this.step(`Thêm nhanh "${productName}" vào giỏ từ thẻ sản phẩm`, async () => {
      await this.home.productCard(productName).first().hover();
      await this.home.quickAddButton(productName).click();
    });
  }

  /** Kiểm tra sản phẩm trong giỏ (localStorage) đã có size được chọn. */
  async verifyStoredCartItemHasSize(productName: string) {
    await this.step(`Kiểm tra "${productName}" trong giỏ có size`, async () => {
      await expect.poll(async () => (await readCart(this.page)).some((i) => i.name === productName)).toBe(true);
      const item = (await readCart(this.page)).find((i) => i.name === productName);
      expect(item?.size, `Sản phẩm "${productName}" được thêm vào giỏ mà không có size`).toBeTruthy();
    });
  }

  // ---------------------------------------------------------------------------
  // Newsletter + Footer
  // ---------------------------------------------------------------------------

  /** Nhập email vào khối "Đăng ký nhận tin" và bấm "Đăng ký". */
  async subscribeNewsletter(email: string) {
    await this.step(`Đăng ký nhận tin với "${email}"`, async () => {
      await this.chrome.newsletterEmail.fill(email);
      await this.chrome.newsletterSubmit.click();
    });
  }

  /** Kiểm tra hiện "Cảm ơn bạn đã đăng ký!" rồi form tự hiện lại sau khoảng 4 giây. */
  async verifyNewsletterThanks() {
    await this.step('Kiểm tra cảm ơn đăng ký nhận tin và form hiện lại', async () => {
      await expect(this.chrome.newsletterThanks).toBeVisible();
      await expect(this.chrome.newsletterEmail).toBeHidden();
      await expect(this.chrome.newsletterThanks).toBeHidden({ timeout: 8_000 });
      await expect(this.chrome.newsletterEmail).toHaveValue(/.+/);
    });
  }

  /** Kiểm tra trình duyệt chặn gửi form nhận tin (HTML5 validation), vd: "valueMissing", "typeMismatch". */
  async verifyNewsletterBlocked(validity: string) {
    await this.step(`Kiểm tra form nhận tin bị chặn (${validity})`, async () => {
      const state = await this.chrome.newsletterEmail.evaluate(
        (el: HTMLInputElement, key) => ({ flag: (el.validity as any)[key], message: el.validationMessage }),
        validity,
      );
      expect(state.flag, `validity.${validity}`).toBe(true);
      expect(state.message).not.toBe('');
      await expect(this.chrome.newsletterThanks).toHaveCount(0);
    });
  }

  /** Kiểm tra footer: các tiêu đề cột, link và dòng bản quyền. */
  async verifyFooterContent(headings: string[], links: string[]) {
    await this.step('Kiểm tra nội dung footer', async () => {
      for (const h of headings) await expect(this.chrome.footerHeading(h)).toBeVisible();
      for (const l of links) await expect(this.chrome.footerLink(l)).toBeVisible();
      await expect(this.chrome.footerCopyright).toBeVisible();
    });
  }

  /** Kiểm tra 1 link footer trỏ đúng đường dẫn. */
  async verifyFooterLink(name: string, href: string) {
    await this.step(`Kiểm tra footer "${name}" -> ${href}`, async () => {
      await expect(this.chrome.footerLink(name)).toHaveAttribute('href', href);
    });
  }

  /** Kiểm tra footer có ít nhất 1 link trỏ tới đường dẫn. */
  async verifyFooterHasLinkTo(href: string) {
    await this.step(`Kiểm tra footer có link tới ${href}`, async () => {
      await expect(this.chrome.footerLinkTo(href).first()).toBeAttached();
    });
  }

  // ---------------------------------------------------------------------------
  // Blog
  // ---------------------------------------------------------------------------

  /** Mock API blog: danh sách GET /api/news và chi tiết GET /api/news/:slug (404 nếu slug không có trong danh sách). */
  async mockBlogData(response: { success: boolean; news: BlogArticle[] }) {
    await this.step(`Mock blog (${response.news.length} bài)`, async () => {
      await this.page.route('**/api/news?**', (route) =>
        route.request().method() === 'GET' ? route.fulfill({ json: response }) : route.fallback(),
      );
      await this.page.route('**/api/news/*', (route) => {
        if (route.request().method() !== 'GET') return route.fallback();
        const slug = decodeURIComponent(new URL(route.request().url()).pathname.split('/').pop() ?? '');
        const article = response.news.find((a) => a.slug === slug);
        return article
          ? route.fulfill({ json: { success: true, article } })
          : route.fulfill({ status: 404, json: { success: false, message: 'Không tìm thấy bài viết' } });
      });
    });
  }

  /** Mở trang /blog và chờ danh sách bài viết tải xong. */
  async openBlog() {
    await this.step('Mở trang Blog', async () => {
      await this.blogList.open();
      await expect(this.blogList.heading).toBeVisible();
      await expect(this.blogList.cards.first().or(this.blogList.emptyState)).toBeVisible();
    });
  }

  /** Kiểm tra trang Blog: tiêu đề, mô tả và có ít nhất 1 bài viết. */
  async verifyBlogLoaded() {
    await this.step('Kiểm tra trang Blog có bài viết', async () => {
      await expect(this.blogList.heading).toBeVisible();
      await expect(this.blogList.subtitle).toBeVisible();
      await expect(this.blogList.cards.first()).toBeVisible();
      await expect(this.blogList.pill('Tất cả')).toBeVisible();
    });
  }

  /** Kiểm tra các nút danh mục (pill) trên trang Blog theo thứ tự. */
  async verifyBlogPills(pills: string[]) {
    await this.step(`Kiểm tra danh mục blog: ${pills.join(', ')}`, async () => {
      await expect(this.blogList.categoryPills).toHaveText(pills);
    });
  }

  /** Bấm 1 danh mục (pill) trên trang Blog. */
  async filterBlogByCategory(category: string) {
    await this.step(`Lọc blog theo "${category}"`, async () => {
      await this.blogList.pill(category).click();
      await expect(this.blogList.pill(category)).toHaveClass(/bg-slate-900/);
    });
  }

  /** Kiểm tra danh sách bài viết đang hiển thị đúng các tiêu đề (theo thứ tự). */
  async verifyBlogTitles(titles: string[]) {
    await this.step(`Kiểm tra ${titles.length} bài viết hiển thị`, async () => {
      await expect(this.blogList.cards.locator('h2')).toHaveText(titles);
    });
  }

  /** Kiểm tra mọi bài viết đang hiển thị đều thuộc danh mục. */
  async verifyBlogCategoryOfCards(category: string) {
    await this.step(`Kiểm tra mọi bài thuộc danh mục "${category}"`, async () => {
      const count = await this.blogList.cards.count();
      expect(count).toBeGreaterThan(0);
      await expect(this.blogList.cardCategories()).toHaveText(Array(count).fill(category));
    });
  }

  /** Kiểm tra trang Blog báo không có bài viết. */
  async verifyBlogEmpty() {
    await this.step('Kiểm tra blog không có bài viết', async () => {
      await expect(this.blogList.emptyState).toBeVisible();
      await expect(this.blogList.cards).toHaveCount(0);
    });
  }

  /** Bấm 1 bài viết trên trang Blog theo tiêu đề. */
  async openBlogArticle(title: string) {
    await this.step(`Mở bài viết "${title}"`, async () => {
      await this.blogList.card(title).click();
      await expect(this.blogDetail.title).toHaveText(title);
    });
  }

  /** Mở thẳng trang chi tiết bài viết /blog/{slug}. */
  async openBlogArticleBySlug(slug: string) {
    await this.step(`Mở /blog/${slug}`, async () => {
      await this.blogDetail.open(slug);
    });
  }

  /** Kiểm tra trang chi tiết bài viết: URL, tiêu đề, danh mục, tác giả, lượt xem, tag, bài liên quan. */
  async verifyBlogArticle(c: BlogArticleExpect) {
    await this.step(`Kiểm tra chi tiết bài "${c.titleText}"`, async () => {
      await expect(this.page).toHaveURL(`/blog/${c.slug}`);
      await expect(this.blogDetail.title).toHaveText(c.titleText);
      await expect(this.blogDetail.backLink).toHaveAttribute('href', '/blog');
      await expect(this.blogDetail.categoryBadge).toHaveText(c.category);
      await expect(this.blogDetail.author).toHaveText(c.author);
      await expect(this.blogDetail.viewCount).toHaveText(new RegExp(`${c.views} lượt xem$`));
      if (c.articleTags.length) {
        for (const t of c.articleTags) await expect(this.blogDetail.tag(t)).toBeVisible();
      } else {
        await expect(this.blogDetail.tagsSection).toHaveCount(0);
      }
      if (c.related.length) {
        await expect(this.blogDetail.relatedCards.locator('h3')).toHaveText(c.related);
      } else {
        await expect(this.blogDetail.relatedHeading).toHaveCount(0);
      }
      if (c.fallback) await expect(this.blogDetail.contentFallback).toBeVisible();
    });
  }

  /** Bấm "Quay lại Blog" trên trang chi tiết bài viết. */
  async clickBackToBlog() {
    await this.step('Bấm "Quay lại Blog"', async () => {
      await this.blogDetail.backLink.click();
      await expect(this.blogList.heading).toBeVisible();
    });
  }

  /** Bấm 1 bài trong "Bài viết liên quan". */
  async openRelatedArticle(title: string) {
    await this.step(`Mở bài liên quan "${title}"`, async () => {
      await this.blogDetail.relatedCard(title).click();
      await expect(this.blogDetail.title).toHaveText(title);
    });
  }

  /** Đăng ký nhận tin ở trang Blog và kiểm tra trang KHÔNG bị tải lại (form phải được xử lý bằng JS). */
  async subscribeBlogNewsletterWithoutReload(email: string) {
    await this.step(`Đăng ký nhận tin trên Blog với "${email}" (không reload)`, async () => {
      await this.blogList.newsletterEmail.fill(email);
      const reloaded = detectReload(this.page, 4_000);
      await this.blogList.newsletterSubmit.click();
      expect(await reloaded, 'Form nhận tin ở /blog làm tải lại trang (thiếu onSubmit)').toBe(false);
      await expect(this.blogList.newsletterEmail).toHaveValue(email);
    });
  }

  // ---------------------------------------------------------------------------
  // Trang tĩnh / route không tồn tại
  // ---------------------------------------------------------------------------

  /** Kiểm tra các tiêu đề trong <main>: h1 đúng, h2/h3 chứa đủ các mục (theo thứ tự). */
  async verifyPageHeadings(h1: string, h2: string[], h3: string[]) {
    await this.step(`Kiểm tra tiêu đề trang "${h1}"`, async () => {
      await expect(this.chrome.mainHeadings(1)).toHaveText([h1]);
      if (h2.length) await expect(this.chrome.mainHeadings(2)).toContainText(h2);
      if (h3.length) await expect(this.chrome.mainHeadings(3)).toContainText(h3);
    });
  }

  /** Kiểm tra <main> có chứa các đoạn chữ. */
  async verifyMainContains(texts: string[]) {
    await this.step(`Kiểm tra nội dung có ${texts.length} đoạn chữ`, async () => {
      for (const t of texts) await expect(this.chrome.main).toContainText(t);
    });
  }

  /** Kiểm tra khối có tiêu đề h3 (vd: thẻ "Giao hàng nhanh") chứa đoạn chữ. */
  async verifyBlockContains(heading: string, text: string) {
    await this.step(`Kiểm tra khối "${heading}" chứa "${text}"`, async () => {
      const block = this.chrome.main.locator('h3', { hasText: heading }).first().locator('xpath=..');
      await expect(block).toContainText(text);
    });
  }

  /** Kiểm tra <main> KHÔNG chứa chuỗi khớp biểu thức chính quy (vd: ký tự Cyrillic). */
  async verifyMainNotMatching(pattern: string) {
    await this.step(`Kiểm tra nội dung không khớp /${pattern}/`, async () => {
      await expect(this.chrome.main).toBeVisible();
      await expect(this.chrome.main).not.toContainText(new RegExp(pattern));
    });
  }

  /** Kiểm tra route không tồn tại hiển thị trang báo lỗi (thông báo + layout). */
  async verifyNotFoundPage(message: string) {
    await this.step(`Kiểm tra trang "không tìm thấy": "${message}"`, async () => {
      await expect(this.chrome.body).toContainText(message);
      await expect(this.page.locator('header').first()).toBeVisible();
    });
  }
}
