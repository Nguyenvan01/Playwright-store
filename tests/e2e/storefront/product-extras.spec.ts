import { test } from '@fixtures';
import { AUTH_FILES } from '@config/env';
import { loadData, resolveData } from '@data/loader';
import type { ProductExtrasData } from '@data/storefront.types';
import { applyCaseMeta, caseTitle } from '@engine/cases';
import { hasCustomerAuth } from '@utils/storage';

const data = loadData<ProductExtrasData>('storefront/product.json');
const e = data.expected;

/** Trang chi tiết dùng dữ liệu mock cố định (3 ảnh, 3 màu, có giá gốc, 1 sản phẩm liên quan là sản phẩm thật). */
test.beforeEach(async ({ k, ctx }) => {
  await k.product.mockProductDetail(data.mockSlug, resolveData(data.mockProduct, ctx));
  await k.product.openProductPage(data.mockSlug);
  await k.catalog.verifyProductTitle(e.title);
});

test.describe('Chi tiết sản phẩm: ảnh, màu, SKU, giá, accordion', () => {
  test('[SF-PDP-01] Breadcrumb "Trang chủ | tên sản phẩm" quay về trang chủ @smoke', async ({ k }) => {
    await k.product.verifyBreadcrumb(e.title);
    await k.product.clickBreadcrumbHome();
    await k.common.verifyUrl('/');
  });

  test('[SF-PDP-02] Bộ ảnh: thumbnail và bộ đếm ảnh', async ({ k }) => {
    await k.product.verifyGallery(e.imageCount);
    await k.product.verifyCurrentImage(1, e.imageCount);
    await k.product.clickThumbnail(3);
    await k.product.verifyCurrentImage(3, e.imageCount);
    await k.product.clickThumbnail(2);
    await k.product.verifyCurrentImage(2, e.imageCount);
  });

  test('[SF-PDP-03] Nút ảnh tiếp theo chuyển tới ảnh cuối rồi ẩn đi', async ({ k }) => {
    for (let i = 2; i <= e.imageCount; i++) {
      await k.product.clickNextImage();
      await k.product.verifyCurrentImage(i, e.imageCount);
    }
    await k.product.verifyNextImageHidden();
  });

  test('[SF-PDP-04] Chọn màu đổi tên màu đang chọn', async ({ k }) => {
    await k.product.verifyColorOptions(e.colors);
    await k.product.selectColor(e.colors[2]);
    await k.product.selectColor(e.colors[1]);
  });

  test.describe('Quyền clipboard', () => {
    test.use({ permissions: ['clipboard-read', 'clipboard-write'] });

    test('[SF-PDP-05] Copy SKU -> "Đã copy", clipboard chứa SKU, 2 giây sau trở lại "Copy"', async ({ k }) => {
      await k.product.verifySku(e.sku);
      await k.product.copySku();
      await k.product.verifySkuCopied(e.sku);
    });
  });

  test('[SF-PDP-06] Có giá gốc gạch ngang và nhãn phần trăm giảm', async ({ k }) => {
    await k.product.verifyDiscountBadge(e.discount);
  });

  test(caseTitle(data.priceBug), async ({ k }) => {
    applyCaseMeta(data.priceBug);
    await k.product.verifyPrice(data.priceBug.expected);
    await k.product.verifyComparePrice(e.comparePrice, e.discount);
  });

  test('[SF-PDP-08] Accordion: mặc định mở "Mô tả", chỉ mở 1 mục mỗi lúc, bấm lại thì đóng', async ({ k }) => {
    await k.product.verifyOpenAccordion('Mô tả', data.accordions);
    await k.product.verifyAccordionContent('Mô tả', e.description);
    await k.product.toggleAccordion('Chất liệu');
    await k.product.verifyOpenAccordion('Chất liệu', data.accordions);
    await k.product.verifyAccordionContent('Chất liệu', e.materials);
    await k.product.toggleAccordion('Hướng dẫn sử dụng');
    await k.product.verifyOpenAccordion('Hướng dẫn sử dụng', data.accordions);
    await k.product.verifyAccordionContent('Hướng dẫn sử dụng', e.care);
    await k.product.toggleAccordion('Hướng dẫn sử dụng');
    await k.product.verifyOpenAccordion('', data.accordions);
  });

  test('[SF-PDP-09] Danh sách dịch vụ: COD, miễn phí giao hàng, đổi hàng 30 ngày', async ({ k }) => {
    await k.product.verifyServices(e.services);
  });

  test(caseTitle(data.shippingThresholdBug), async ({ k }) => {
    applyCaseMeta(data.shippingThresholdBug);
    await k.product.verifyServiceText(data.shippingThresholdBug.service, data.shippingThresholdBug.expected);
  });

  test('[SF-PDP-11] "SẢN PHẨM CÙNG PHONG CÁCH" mở trang chi tiết sản phẩm liên quan', async ({ k, ctx }) => {
    const related = resolveData(e.relatedName, ctx);
    await k.product.verifyRelatedProduct(related);
    await k.product.openRelatedProduct(related);
    await k.common.verifyUrlMatches(`/product/${resolveData('${product.slug}', ctx)}$`);
    await k.catalog.verifyProductTitle(related);
  });

  test('[SF-PDP-12] Khách chưa đăng nhập chỉ thấy lời nhắc đăng nhập để đánh giá', async ({ k }) => {
    await k.product.verifyReviewLoginPrompt();
    await k.product.clickReviewLogin();
    await k.common.verifyUrl('/login');
  });
});

test.describe('Chi tiết sản phẩm: đánh giá (đã đăng nhập)', () => {
  test.use({ storageState: AUTH_FILES.customer });
  test.skip(() => !hasCustomerAuth(), 'Chưa có tài khoản test (xem .env)');

  test.beforeEach(async ({ k }) => {
    await k.common.mockWrite('POST', '**/api/reviews', { success: true, message: data.reviewSuccess.message });
    await k.product.openReviewForm();
  });

  for (const c of data.reviewValidation) {
    test(caseTitle(c), async ({ k }) => {
      applyCaseMeta(c);
      await k.product.fillReview(c.stars, c.content);
      await k.product.submitReview();
      await k.product.verifyReviewErrors(c.errors);
      await k.common.verifyNoRequest('POST', '/api/reviews');
    });
  }

  test(caseTitle(data.reviewSuccess), async ({ k }) => {
    const c = data.reviewSuccess;
    applyCaseMeta(c);
    await k.product.fillReview(c.stars, c.content);
    await k.product.submitReview();
    await k.common.verifyToast(c.message);
    await k.common.verifyRequest('POST', '/api/reviews', { product_id: data.mockProduct.data.id, rating: c.stars, content: c.content });
    await k.product.verifyReviewFormClosed();
  });

  for (const c of data.reviewServerErrors) {
    test(caseTitle(c), async ({ k }) => {
      applyCaseMeta(c);
      await k.common.mockWrite('POST', '**/api/reviews', { success: false, message: c.message }, c.status);
      await k.product.fillReview(c.stars, c.content);
      await k.product.submitReview();
      await k.common.verifyRequest('POST', '/api/reviews', { rating: c.stars, content: c.content });
      await k.common.verifyToast(c.toast);
    });
  }

  test('[SF-PDP-22] Bấm "Hủy" đóng form đánh giá, không gửi request', async ({ k }) => {
    await k.product.fillReview(4, 'Đang viết dở');
    await k.product.cancelReview();
    await k.product.verifyReviewFormClosed();
    await k.common.verifyNoRequest('POST', '/api/reviews');
  });

  test('[SF-PDP-23] Bấm "×" đóng form và xóa thông báo lỗi', async ({ k }) => {
    await k.product.submitReview();
    await k.product.verifyReviewErrors(['Vui lòng chọn số sao đánh giá.', 'Vui lòng nhập nội dung đánh giá.']);
    await k.product.closeReviewForm();
    await k.product.verifyReviewFormClosed();
    await k.product.openReviewForm();
    await k.product.verifyReviewErrors([]);
  });
});
