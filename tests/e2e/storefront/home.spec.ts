import { test } from '@fixtures';
import { loadData } from '@data/loader';
import type { HomeData } from '@data/storefront.types';
import { applyCaseMeta, caseTitle } from '@engine/cases';

const data = loadData<HomeData>('storefront/home.json');
const mock = data.mockHome;
const news = mock.data.news as { title: string; slug: string }[];

test.describe('Trang chủ: các khối nội dung', () => {
  test('[SF-HOME-01] Dữ liệu thật: đủ các khối nội dung, không lỗi JavaScript @smoke', async ({ k }) => {
    await k.content.openHomePage();
    await k.content.verifyHomeSections(data.sections);
    await k.content.verifyCLive(data.clive);
    await k.common.verifyNoPageErrors();
  });

  test('[SF-HOME-06] API /home lỗi 500: vẫn hiển thị banner mặc định, ẩn ưu đãi, tin tức rỗng', async ({ k }) => {
    await k.common.mockGet('**/api/home', { success: false, message: 'Lỗi server' }, 500);
    await k.content.openHomePage();
    await k.content.verifyBannerSlideCount(data.defaultBannerCount);
    await k.content.verifyBannerSlideLinks(['/nam', '/homewear', '/nu']);
    await k.content.verifyNoVoucherSection();
    await k.content.verifyNewProductCount(0);
    await k.content.verifyHomeNewsEmpty();
  });

  test.describe('Banner (mock, đồng hồ cố định để slide không tự chuyển giữa các bước)', () => {
    test.beforeEach(async ({ k }) => {
      await k.content.mockHomeData(mock);
      await k.content.freezeClock();
      await k.content.openHomePage();
    });

    test('[SF-HOME-02] Banner: 3 slide, slide 1 hiển thị trước, link mỗi slide theo link_url', async ({ k }) => {
      await k.content.verifyBannerSlideCount(mock.data.banners.length);
      await k.content.verifyActiveBannerSlide(1);
      await k.content.verifyBannerSlideLinks(data.banner.slideHrefs);
    });

    test('[SF-HOME-03] Banner: mũi tên sau/trước chuyển slide và quay vòng', async ({ k }) => {
      await k.content.clickBannerArrow('next');
      await k.content.verifyActiveBannerSlide(2);
      await k.content.clickBannerArrow('prev');
      await k.content.verifyActiveBannerSlide(1);
      await k.content.clickBannerArrow('prev');
      await k.content.verifyActiveBannerSlide(3);
    });

    test('[SF-HOME-04] Banner: bấm chấm điều hướng nhảy tới slide tương ứng', async ({ k }) => {
      await k.content.clickBannerDot(3);
      await k.content.verifyActiveBannerSlide(3);
      await k.content.clickBannerDot(2);
      await k.content.verifyActiveBannerSlide(2);
    });

    test('[SF-HOME-05] Banner: tự chuyển slide sau khoảng 4 giây', async ({ k }) => {
      await k.content.verifyActiveBannerSlide(1);
      await k.content.verifyBannerAutoplay(2);
    });

    test(caseTitle(data.banner.overlay), async ({ k }) => {
      const c = data.banner.overlay;
      applyCaseMeta(c);
      await k.content.clickBannerDot(c.index);
      await k.content.verifyBannerOverlay(c.index, mock.data.banners[c.index - 1].title, c.expectedHref);
    });
  });

  test.describe('Dữ liệu mock cố định', () => {
    test.beforeEach(async ({ k }) => {
      await k.content.mockHomeData(mock);
      await k.content.openHomePage();
    });

    test('[SF-HOME-08] Ưu đãi nổi bật: tiêu đề, mô tả, điều kiện, HSD / sắp hết hạn', async ({ k }) => {
      for (const v of data.vouchers) await k.content.verifyVoucher(v);
    });

    test('[SF-HOME-09] "Dùng mã" lưu voucher chờ áp dụng và chuyển tới /nam', async ({ k }) => {
      const v = data.vouchers[0];
      await k.content.useVoucher(v.title);
      await k.common.verifyUrl('/nam');
      await k.content.verifyPendingVoucher(v.code);
    });

    for (const c of data.tabCases) {
      test(caseTitle(c), async ({ k }) => {
        applyCaseMeta(c);
        await k.content.selectNewProductTab(c.tab);
        await k.content.verifyNewProductsFiltered(c.tab, c.visible, c.hidden);
      });
    }

    test('[SF-HOME-13] SẢN PHẨM MỚI: 5 tab, 8 sản phẩm, mũi tên cuộn carousel', async ({ k }) => {
      await k.content.verifyNewProductTabs(data.tabs);
      await k.content.verifyNewProductCount(mock.data.featuredProducts.length);
      await k.content.scrollNewProducts('next');
      await k.content.scrollNewProducts('prev');
    });

    test('[SF-HOME-14] Khối HOMEWEAR / T-SHIRT / VÁY: mô tả và tối đa 4 sản phẩm', async ({ k }) => {
      for (const b of data.promoBlocks) await k.content.verifyPromoBlock(b.title, b.description, b.cardCount);
    });

    test('[SF-HOME-15] Khối C-LIVE: tiêu đề, ảnh, lời mời tải app', async ({ k }) => {
      await k.content.verifyCLive(data.clive);
    });

    test('[SF-HOME-16] Tin tức thời trang: 1 bài nổi bật + 4 bài phụ, "Xem thêm" tới /blog', async ({ k }) => {
      await k.content.verifyHomeNews(news[0].title, 4);
      await k.content.verifyHomeNewsLink(news[0].title, news[0].slug);
      await k.content.clickHomeNewsSeeMore();
      await k.common.verifyUrl('/blog');
    });

    for (const c of data.collections) {
      test(caseTitle(c), async ({ k }) => {
        applyCaseMeta(c);
        await k.content.verifyCollection(c.titleText, c.ctaText, c.href);
      });
    }

    test('[SF-HOME-20] Thêm nhanh vào giỏ từ thẻ sản phẩm: toast và badge giỏ hàng', async ({ k }) => {
      await k.content.quickAddToCart(data.quickAdd.product);
      await k.common.verifyToast(data.quickAdd.toast);
      await k.cart.verifyCartBadge(1);
    });

    test('[SF-HOME-25] Thêm nhanh vào giỏ phải kèm size như trang chi tiết', async ({ k }) => {
      test.fail(true, 'BUG: ProductCard.jsx:37 addItem(product, 1, null, null) -> sản phẩm vào giỏ không có size/màu');
      await k.content.quickAddToCart(data.quickAdd.product);
      await k.content.verifyStoredCartItemHasSize(data.quickAdd.product);
    });

    for (const c of data.deadLinks) {
      test(caseTitle(c), async ({ k }) => {
        applyCaseMeta(c);
        await k.content.clickHomeLink(c.link, c.section);
        await k.common.verifyUrl(c.href);
        await k.content.verifyPageRendered();
      });
    }
  });

  test.describe('Dữ liệu mock: trường hợp rỗng', () => {
    test('[SF-HOME-10] Không có voucher -> ẩn khối ƯU ĐÃI NỔI BẬT', async ({ k }) => {
      await k.content.mockHomeData({ ...mock, data: { ...mock.data, vouchers: [] } });
      await k.content.openHomePage();
      await k.content.verifyNoVoucherSection();
    });

    test('[SF-HOME-19] Không có tin tức -> "Chưa có tin tức thời trang nào", ẩn "Xem thêm"', async ({ k }) => {
      await k.content.mockHomeData({ ...mock, data: { ...mock.data, news: [] } });
      await k.content.openHomePage();
      await k.content.verifyHomeNewsEmpty();
    });
  });
});
