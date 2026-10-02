import { Locator, Page } from '@playwright/test';

/** Các phần mở rộng của trang chi tiết sản phẩm (pages/ProductDetailPage.jsx). */
export class ProductExtrasPage {
  readonly breadcrumb: Locator;
  readonly breadcrumbHome: Locator;
  readonly thumbnails: Locator;
  readonly mainImage: Locator;
  readonly imageCounter: Locator;
  readonly nextImageButton: Locator;
  readonly colorButtons: Locator;
  readonly selectedColorName: Locator;
  readonly sku: Locator;
  readonly copySkuButton: Locator;
  readonly price: Locator;
  readonly comparePrice: Locator;
  readonly discountBadge: Locator;
  readonly serviceItems: Locator;
  readonly reviewsHeading: Locator;
  readonly reviewsSection: Locator;
  readonly loginPrompt: Locator;
  readonly reviewLoginLink: Locator;
  readonly writeReviewButton: Locator;
  readonly reviewForm: Locator;
  readonly reviewFormTitle: Locator;
  readonly reviewStars: Locator;
  readonly reviewContent: Locator;
  readonly submitReviewButton: Locator;
  readonly cancelReviewButton: Locator;
  readonly closeReviewButton: Locator;
  readonly relatedHeading: Locator;
  readonly relatedSection: Locator;
  readonly relatedItems: Locator;

  constructor(readonly page: Page) {
    this.breadcrumb = page.locator('nav.breadcrumb');
    this.breadcrumbHome = this.breadcrumb.getByRole('link', { name: 'Trang chủ' });
    this.thumbnails = page.locator('.thumbnail-list button');
    this.mainImage = page.locator('img.main-product-image');
    this.imageCounter = page.locator('.image-counter');
    this.nextImageButton = page.locator('button.next-image-button');
    this.colorButtons = page.locator('.color-selector button[title]');
    this.selectedColorName = page.locator('.color-selector').getByText('Màu sắc:').locator('xpath=following-sibling::span[1]');
    this.sku = page.locator('.product-sku');
    this.copySkuButton = page.locator('button.copy-sku');
    this.price = page.locator('.product-price');
    this.comparePrice = page.locator('.product-price + span.line-through');
    this.discountBadge = page.locator('.product-info').getByText(/^-\d+%$/);
    this.serviceItems = page.locator('.service-list .service-item');

    this.reviewsHeading = page.getByRole('heading', { name: 'ĐÁNH GIÁ SẢN PHẨM' });
    this.reviewsSection = page.locator('section').filter({ has: this.reviewsHeading });
    this.loginPrompt = this.reviewsSection.getByText('Vui lòng đăng nhập để đánh giá sản phẩm');
    this.reviewLoginLink = this.reviewsSection.getByRole('link', { name: 'Đăng nhập' });
    this.writeReviewButton = this.reviewsSection.getByRole('button', { name: 'Viết đánh giá' });
    this.reviewFormTitle = this.reviewsSection.getByRole('heading', { name: 'VIẾT ĐÁNH GIÁ CỦA BẠN' });
    this.reviewForm = this.reviewsSection
      .locator('div.mb-8')
      .filter({ has: page.getByRole('heading', { name: 'VIẾT ĐÁNH GIÁ CỦA BẠN' }) });
    this.reviewStars = this.reviewForm.locator('button[type="button"]');
    this.reviewContent = this.reviewForm.getByPlaceholder('Chia sẻ trải nghiệm của bạn về sản phẩm này...');
    this.submitReviewButton = this.reviewForm.getByRole('button', { name: /Gửi đánh giá|Đang gửi\.\.\./ });
    this.cancelReviewButton = this.reviewForm.getByRole('button', { name: 'Hủy', exact: true });
    this.closeReviewButton = this.reviewForm.getByRole('button', { name: '×', exact: true });

    this.relatedHeading = page.getByRole('heading', { name: 'SẢN PHẨM CÙNG PHONG CÁCH' });
    this.relatedSection = page.locator('section').filter({ has: this.relatedHeading });
    this.relatedItems = this.relatedSection.locator('a[href^="/product/"]');
  }

  async open(slug: string) {
    await this.page.goto(`/product/${slug}`);
  }

  thumbnail(n: number): Locator {
    return this.page.getByRole('button', { name: `Thumbnail ${n}`, exact: true });
  }

  colorButton(name: string): Locator {
    return this.page.locator(`.color-selector button[title="${name}"]`);
  }

  copyLabel(text: 'Copy' | 'Đã copy'): Locator {
    return this.copySkuButton.getByText(text, { exact: true });
  }

  /** Nút tiêu đề accordion: "Mô tả" / "Chất liệu" / "Hướng dẫn sử dụng". */
  accordionHeader(title: string): Locator {
    return this.page.locator('.product-accordion button.accordion-header').filter({ hasText: title });
  }

  /** Dấu hiệu mở/đóng ("—" đang mở, "+" đang đóng) bên phải tiêu đề accordion. */
  accordionIndicator(title: string): Locator {
    return this.accordionHeader(title).locator('span').nth(1);
  }

  /** Vùng nội dung của 1 accordion (đóng = max-h-0). */
  accordionPanel(title: string): Locator {
    const header = this.page.locator('button.accordion-header', { hasText: title });
    return this.page.locator('.product-accordion .accordion-item').filter({ has: header }).locator(':scope > div');
  }

  serviceItem(title: string): Locator {
    return this.serviceItems.filter({ hasText: title });
  }

  reviewError(message: string): Locator {
    return this.reviewForm.locator('p.text-red-500', { hasText: message });
  }

  relatedItem(name: string): Locator {
    return this.relatedItems.filter({ has: this.page.locator('h4', { hasText: name }) });
  }
}
