import { expect } from '@playwright/test';
import { ProductExtrasPage } from '@pages/storefront/ProductExtrasPage';
import { BaseKeywords } from './BaseKeywords';

/** Trang chi tiết sản phẩm mở rộng: ảnh, màu, SKU, accordion, đánh giá, sản phẩm liên quan. */
export class ProductKeywords extends BaseKeywords {
  private readonly pdp = new ProductExtrasPage(this.page);

  /** Mock GET /api/products/{slug} bằng dữ liệu cho trước (shape { success, data }). */
  async mockProductDetail(slug: string, response: { success: boolean; data: Record<string, unknown> }) {
    await this.step(`Mock chi tiết sản phẩm "${slug}"`, async () => {
      await this.page.route(`**/api/products/${slug}`, (route) =>
        route.request().method() === 'GET' ? route.fulfill({ json: response }) : route.fallback(),
      );
    });
  }

  /** Mở trang chi tiết /product/{slug} và chờ tên sản phẩm hiển thị. */
  async openProductPage(slug: string) {
    await this.step(`Mở trang chi tiết "${slug}"`, async () => {
      await this.pdp.open(slug);
      await expect(this.po.product.title).toBeVisible();
    });
  }

  /** Kiểm tra breadcrumb "Trang chủ | {tên sản phẩm}". */
  async verifyBreadcrumb(title: string) {
    await this.step(`Kiểm tra breadcrumb "Trang chủ | ${title}"`, async () => {
      await expect(this.pdp.breadcrumb).toHaveText(`Trang chủ|${title}`, { useInnerText: false });
      await expect(this.pdp.breadcrumbHome).toHaveAttribute('href', '/');
    });
  }

  /** Bấm "Trang chủ" trên breadcrumb. */
  async clickBreadcrumbHome() {
    await this.step('Bấm "Trang chủ" trên breadcrumb', async () => {
      await this.pdp.breadcrumbHome.click();
    });
  }

  /** Kiểm tra bộ ảnh: số thumbnail ("Thumbnail 1..n") và bộ đếm "1/n". */
  async verifyGallery(count: number) {
    await this.step(`Kiểm tra bộ ảnh có ${count} ảnh`, async () => {
      await expect(this.pdp.thumbnails).toHaveCount(count);
      for (let i = 1; i <= count; i++) await expect(this.pdp.thumbnail(i)).toBeVisible();
      await expect(this.pdp.imageCounter).toHaveText(`1/${count}`);
      await expect(this.pdp.nextImageButton).toBeVisible();
    });
  }

  /** Bấm thumbnail thứ n (đánh số từ 1). */
  async clickThumbnail(n: number) {
    await this.step(`Bấm Thumbnail ${n}`, async () => {
      await this.pdp.thumbnail(n).click();
    });
  }

  /** Bấm nút mũi tên chuyển ảnh tiếp theo trên ảnh chính. */
  async clickNextImage() {
    await this.step('Bấm ảnh tiếp theo', async () => {
      await this.pdp.nextImageButton.click();
    });
  }

  /** Kiểm tra ảnh chính đang là ảnh thứ n: bộ đếm "n/tổng", thumbnail n được viền, cùng nguồn ảnh. */
  async verifyCurrentImage(n: number, total: number) {
    await this.step(`Kiểm tra đang xem ảnh ${n}/${total}`, async () => {
      await expect(this.pdp.imageCounter).toHaveText(`${n}/${total}`);
      await expect(this.pdp.thumbnails.nth(n - 1)).toHaveClass(/border-\[#2f3a45\]/);
      const src = await this.pdp.thumbnail(n).locator('img').getAttribute('src');
      await expect(this.pdp.mainImage).toHaveAttribute('src', src ?? '');
    });
  }

  /** Kiểm tra nút ảnh tiếp theo bị ẩn (đang ở ảnh cuối). */
  async verifyNextImageHidden() {
    await this.step('Kiểm tra ẩn nút ảnh tiếp theo ở ảnh cuối', async () => {
      await expect(this.pdp.nextImageButton).toHaveCount(0);
    });
  }

  /** Kiểm tra các ô màu (theo title) và màu đang chọn mặc định (màu đầu tiên). */
  async verifyColorOptions(colors: string[]) {
    await this.step(`Kiểm tra màu: ${colors.join(', ')}`, async () => {
      const titles = await this.pdp.colorButtons.evaluateAll((els) => els.map((e) => e.getAttribute('title')));
      expect(titles).toEqual(colors);
      await expect(this.pdp.selectedColorName).toHaveText(colors[0]);
    });
  }

  /** Chọn 1 màu (theo title) và kiểm tra tên màu hiển thị cạnh "Màu sắc:". */
  async selectColor(color: string) {
    await this.step(`Chọn màu "${color}"`, async () => {
      await this.pdp.colorButton(color).click();
      await expect(this.pdp.selectedColorName).toHaveText(color);
      await expect(this.pdp.colorButton(color)).toHaveClass(/ring-\[#d71920\]/);
    });
  }

  /** Kiểm tra dòng "SKU: ..." và nút "Copy". */
  async verifySku(sku: string) {
    await this.step(`Kiểm tra SKU ${sku}`, async () => {
      await expect(this.pdp.sku).toHaveText(`SKU: ${sku}`);
      await expect(this.pdp.copyLabel('Copy')).toBeVisible();
    });
  }

  /** Bấm "Copy" mã SKU. */
  async copySku() {
    await this.step('Bấm Copy SKU', async () => {
      await this.pdp.copySkuButton.click();
    });
  }

  /** Kiểm tra đã copy SKU: nút đổi thành "Đã copy", clipboard chứa SKU, sau 2 giây trở lại "Copy". */
  async verifySkuCopied(sku: string) {
    await this.step(`Kiểm tra đã copy SKU ${sku}`, async () => {
      await expect(this.pdp.copyLabel('Đã copy')).toBeVisible();
      await expect.poll(() => this.page.evaluate(() => navigator.clipboard.readText())).toBe(sku);
      await expect(this.pdp.copyLabel('Copy')).toBeVisible({ timeout: 5_000 });
    });
  }

  /** Kiểm tra giá bán hiển thị đúng định dạng, vd: "449.000đ". */
  async verifyPrice(price: string) {
    await this.step(`Kiểm tra giá "${price}"`, async () => {
      await expect(this.pdp.price).toHaveText(price);
    });
  }

  /** Kiểm tra giá gốc gạch ngang và nhãn phần trăm giảm, vd: "599.000đ", "-25%". */
  async verifyComparePrice(comparePrice: string, discount: string) {
    await this.step(`Kiểm tra giá gốc "${comparePrice}" và giảm "${discount}"`, async () => {
      await expect(this.pdp.comparePrice).toHaveText(comparePrice);
      await expect(this.pdp.discountBadge).toHaveText(discount);
    });
  }

  /** Kiểm tra nhãn phần trăm giảm cạnh giá, vd: "-25%". */
  async verifyDiscountBadge(discount: string) {
    await this.step(`Kiểm tra nhãn giảm "${discount}"`, async () => {
      await expect(this.pdp.discountBadge).toHaveText(discount);
      await expect(this.pdp.comparePrice).toBeVisible();
    });
  }

  /** Bấm tiêu đề 1 accordion: "Mô tả" / "Chất liệu" / "Hướng dẫn sử dụng". */
  async toggleAccordion(title: string) {
    await this.step(`Bấm accordion "${title}"`, async () => {
      await this.pdp.accordionHeader(title).click();
    });
  }

  /** Kiểm tra chỉ đúng 1 accordion đang mở (title), các accordion còn lại đóng; title rỗng = tất cả đóng. */
  async verifyOpenAccordion(title: string, all: string[]) {
    await this.step(`Kiểm tra accordion đang mở: "${title || '(không)'}"`, async () => {
      for (const t of all) {
        const open = t === title;
        await expect(this.pdp.accordionIndicator(t)).toHaveText(open ? '—' : '+');
        await expect(this.pdp.accordionPanel(t)).toHaveClass(open ? /max-h-\[500px\]/ : /max-h-0/);
      }
    });
  }

  /** Kiểm tra nội dung trong 1 accordion (các dòng/đoạn). */
  async verifyAccordionContent(title: string, lines: string[]) {
    await this.step(`Kiểm tra nội dung "${title}"`, async () => {
      await expect(this.pdp.accordionPanel(title).locator('p, li')).toHaveText(lines);
    });
  }

  /** Kiểm tra danh sách dịch vụ dưới nút mua (tiêu đề + mô tả). */
  async verifyServices(services: { title: string; desc: string }[]) {
    await this.step(`Kiểm tra ${services.length} dịch vụ`, async () => {
      await expect(this.pdp.serviceItems).toHaveCount(services.length);
      for (const s of services) await expect(this.pdp.serviceItem(s.title)).toContainText(s.desc);
    });
  }

  /** Kiểm tra mô tả của 1 dịch vụ, vd: "Miễn phí giao hàng" -> "Với đơn hàng trên 500.000đ." */
  async verifyServiceText(title: string, desc: string) {
    await this.step(`Kiểm tra dịch vụ "${title}": "${desc}"`, async () => {
      await expect(this.pdp.serviceItem(title).locator('div.text-xs')).toHaveText(desc);
    });
  }

  /** Kiểm tra khối "SẢN PHẨM CÙNG PHONG CÁCH" có sản phẩm theo tên. */
  async verifyRelatedProduct(name: string) {
    await this.step(`Kiểm tra sản phẩm cùng phong cách "${name}"`, async () => {
      await expect(this.pdp.relatedHeading).toBeVisible();
      await expect(this.pdp.relatedItem(name)).toBeVisible();
    });
  }

  /** Bấm 1 sản phẩm trong "SẢN PHẨM CÙNG PHONG CÁCH". */
  async openRelatedProduct(name: string) {
    await this.step(`Mở sản phẩm cùng phong cách "${name}"`, async () => {
      await this.pdp.relatedItem(name).click();
    });
  }

  /** Kiểm tra khách chưa đăng nhập: chỉ thấy lời nhắc đăng nhập để đánh giá. */
  async verifyReviewLoginPrompt() {
    await this.step('Kiểm tra lời nhắc "Vui lòng đăng nhập để đánh giá sản phẩm"', async () => {
      await expect(this.pdp.loginPrompt).toBeVisible();
      await expect(this.pdp.reviewLoginLink).toHaveAttribute('href', '/login');
      await expect(this.pdp.writeReviewButton).toHaveCount(0);
    });
  }

  /** Bấm "Đăng nhập" trong khối đánh giá. */
  async clickReviewLogin() {
    await this.step('Bấm "Đăng nhập" ở khối đánh giá', async () => {
      await this.pdp.reviewLoginLink.click();
    });
  }

  /** Bấm "Viết đánh giá" và kiểm tra form hiện ra. */
  async openReviewForm() {
    await this.step('Mở form "Viết đánh giá"', async () => {
      await this.pdp.writeReviewButton.click();
      await expect(this.pdp.reviewFormTitle).toBeVisible();
      await expect(this.pdp.reviewStars).toHaveCount(5);
    });
  }

  /** Chọn số sao (0 = bỏ qua) và nhập nội dung đánh giá. */
  async fillReview(stars: number, content: string) {
    await this.step(`Nhập đánh giá ${stars} sao: "${content}"`, async () => {
      if (stars > 0) await this.pdp.reviewStars.nth(stars - 1).click();
      await this.pdp.reviewContent.fill(content);
    });
  }

  /** Bấm "Gửi đánh giá". */
  async submitReview() {
    await this.step('Bấm "Gửi đánh giá"', async () => {
      await this.pdp.submitReviewButton.click();
    });
  }

  /** Kiểm tra các thông báo lỗi dưới form đánh giá (đúng và đủ). */
  async verifyReviewErrors(messages: string[]) {
    await this.step(`Kiểm tra lỗi form đánh giá: ${messages.join(' | ')}`, async () => {
      for (const m of messages) await expect(this.pdp.reviewError(m)).toBeVisible();
      await expect(this.pdp.reviewForm.locator('p.text-red-500')).toHaveCount(messages.length);
    });
  }

  /** Bấm "Hủy" trên form đánh giá. */
  async cancelReview() {
    await this.step('Bấm "Hủy" form đánh giá', async () => {
      await this.pdp.cancelReviewButton.click();
    });
  }

  /** Bấm nút "×" đóng form đánh giá. */
  async closeReviewForm() {
    await this.step('Bấm "×" đóng form đánh giá', async () => {
      await this.pdp.closeReviewButton.click();
    });
  }

  /** Kiểm tra form đánh giá đã đóng và nút "Viết đánh giá" hiện lại. */
  async verifyReviewFormClosed() {
    await this.step('Kiểm tra form đánh giá đã đóng', async () => {
      await expect(this.pdp.reviewFormTitle).toHaveCount(0);
      await expect(this.pdp.writeReviewButton).toBeVisible();
    });
  }
}
