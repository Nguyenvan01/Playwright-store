# ============================================================
# TEST: TRANG CHỦ - CÁC KHỐI NỘI DUNG
# Mục tiêu: banner (slide, mũi tên, chấm, tự chuyển), ưu đãi, SẢN PHẨM MỚI, HOMEWEAR/T-SHIRT/VÁY,
#           bộ sưu tập, C-LIVE, tin tức, thêm nhanh vào giỏ, link chết; trường hợp API lỗi / rỗng
# Dữ liệu: data/storefront/home.json (mockHome = response GET /api/home cố định)
# API cần quan sát: k.content.*, k.common.mock_get / verify_url / verify_toast, k.cart.verify_cart_badge
# Kết quả mong đợi: các khối hiển thị đúng dữ liệu mock; bug đã biết được đánh dấu xfail
# ============================================================
import pytest

from utils.cases import case_params, known_bug
from utils.data_loader import load_data

DATA = load_data("storefront/home.json")
MOCK = DATA["mockHome"]
NEWS = MOCK["data"]["news"]


class TestHomeSections:
    """Trang chủ: các khối nội dung"""

    @pytest.mark.smoke
    def test_real_data_sections(self, k):
        """[SF-HOME-01] Dữ liệu thật: đủ các khối nội dung, không lỗi JavaScript"""
        k.content.open_home_page()
        k.content.verify_home_sections(DATA["sections"])
        k.content.verify_c_live(DATA["clive"])
        k.common.verify_no_page_errors()

    def test_home_api_error(self, k):
        """[SF-HOME-06] API /home lỗi 500: vẫn hiển thị banner mặc định, ẩn ưu đãi, tin tức rỗng"""
        k.common.mock_get("**/api/home", {"success": False, "message": "Lỗi server"}, 500)
        k.content.open_home_page()
        k.content.verify_banner_slide_count(DATA["defaultBannerCount"])
        k.content.verify_banner_slide_links(["/nam", "/homewear", "/nu"])
        k.content.verify_no_voucher_section()
        k.content.verify_new_product_count(0)
        k.content.verify_home_news_empty()


class TestHomeBanner:
    """Banner (mock, đồng hồ cố định để slide không tự chuyển giữa các bước)"""

    @pytest.fixture(autouse=True)
    def frozen_home(self, k):
        k.content.mock_home_data(MOCK)
        k.content.freeze_clock()
        k.content.open_home_page()

    def test_banner_slides(self, k):
        """[SF-HOME-02] Banner: 3 slide, slide 1 hiển thị trước, link mỗi slide theo link_url"""
        k.content.verify_banner_slide_count(len(MOCK["data"]["banners"]))
        k.content.verify_active_banner_slide(1)
        k.content.verify_banner_slide_links(DATA["banner"]["slideHrefs"])

    def test_banner_arrows(self, k):
        """[SF-HOME-03] Banner: mũi tên sau/trước chuyển slide và quay vòng"""
        k.content.click_banner_arrow("next")
        k.content.verify_active_banner_slide(2)
        k.content.click_banner_arrow("prev")
        k.content.verify_active_banner_slide(1)
        k.content.click_banner_arrow("prev")
        k.content.verify_active_banner_slide(3)

    def test_banner_dots(self, k):
        """[SF-HOME-04] Banner: bấm chấm điều hướng nhảy tới slide tương ứng"""
        k.content.click_banner_dot(3)
        k.content.verify_active_banner_slide(3)
        k.content.click_banner_dot(2)
        k.content.verify_active_banner_slide(2)

    def test_banner_autoplay(self, k):
        """[SF-HOME-05] Banner: tự chuyển slide sau khoảng 4 giây"""
        k.content.verify_active_banner_slide(1)
        k.content.verify_banner_autoplay(2)

    @pytest.mark.parametrize("case", case_params([DATA["banner"]["overlay"]]))
    def test_banner_overlay(self, k, case):
        """Chữ trên slide banner: nút "Khám phá ngay" dùng link_url của banner"""
        k.content.click_banner_dot(case["index"])
        k.content.verify_banner_overlay(
            case["index"], MOCK["data"]["banners"][case["index"] - 1]["title"], case["expectedHref"]
        )


class TestHomeMockData:
    """Dữ liệu mock cố định"""

    @pytest.fixture(autouse=True)
    def mocked_home(self, k):
        k.content.mock_home_data(MOCK)
        k.content.open_home_page()

    def test_vouchers(self, k):
        """[SF-HOME-08] Ưu đãi nổi bật: tiêu đề, mô tả, điều kiện, HSD / sắp hết hạn"""
        for voucher in DATA["vouchers"]:
            k.content.verify_voucher(voucher)

    def test_use_voucher(self, k):
        """[SF-HOME-09] "Dùng mã" lưu voucher chờ áp dụng và chuyển tới /nam"""
        voucher = DATA["vouchers"][0]
        k.content.use_voucher(voucher["title"])
        k.common.verify_url("/nam")
        k.content.verify_pending_voucher(voucher["code"])

    @pytest.mark.parametrize("case", case_params(DATA["tabCases"]))
    def test_new_product_tab_filter(self, k, case):
        """Tab SẢN PHẨM MỚI lọc sản phẩm (data-driven)"""
        k.content.select_new_product_tab(case["tab"])
        k.content.verify_new_products_filtered(case["tab"], case["visible"], case["hidden"])

    def test_new_products_carousel(self, k):
        """[SF-HOME-13] SẢN PHẨM MỚI: 5 tab, 8 sản phẩm, mũi tên cuộn carousel"""
        k.content.verify_new_product_tabs(DATA["tabs"])
        k.content.verify_new_product_count(len(MOCK["data"]["featuredProducts"]))
        k.content.scroll_new_products("next")
        k.content.scroll_new_products("prev")

    def test_promo_blocks(self, k):
        """[SF-HOME-14] Khối HOMEWEAR / T-SHIRT / VÁY: mô tả và tối đa 4 sản phẩm"""
        for block in DATA["promoBlocks"]:
            k.content.verify_promo_block(block["title"], block["description"], block["cardCount"])

    def test_clive(self, k):
        """[SF-HOME-15] Khối C-LIVE: tiêu đề, ảnh, lời mời tải app"""
        k.content.verify_c_live(DATA["clive"])

    def test_home_news(self, k):
        """[SF-HOME-16] Tin tức thời trang: 1 bài nổi bật + 4 bài phụ, "Xem thêm" tới /blog"""
        k.content.verify_home_news(NEWS[0]["title"], 4)
        k.content.verify_home_news_link(NEWS[0]["title"], NEWS[0]["slug"])
        k.content.click_home_news_see_more()
        k.common.verify_url("/blog")

    @pytest.mark.parametrize("case", case_params(DATA["collections"]))
    def test_collection(self, k, case):
        """Ô bộ sưu tập: tiêu đề, nút CTA và link (data-driven)"""
        k.content.verify_collection(case["titleText"], case["ctaText"], case["href"])

    def test_quick_add_to_cart(self, k):
        """[SF-HOME-20] Thêm nhanh vào giỏ từ thẻ sản phẩm: toast và badge giỏ hàng"""
        k.content.quick_add_to_cart(DATA["quickAdd"]["product"])
        k.common.verify_toast(DATA["quickAdd"]["toast"])
        k.cart.verify_cart_badge(1)

    def test_quick_add_keeps_size(self, k, request):
        """[SF-HOME-25] Thêm nhanh vào giỏ phải kèm size như trang chi tiết"""
        known_bug(
            request,
            "ProductCard.jsx:37 addItem(product, 1, null, null) -> sản phẩm vào giỏ không có size/màu",
        )
        k.content.quick_add_to_cart(DATA["quickAdd"]["product"])
        k.content.verify_stored_cart_item_has_size(DATA["quickAdd"]["product"])

    @pytest.mark.parametrize("case", case_params(DATA["deadLinks"]))
    def test_dead_link(self, k, case):
        """Link trên trang chủ dẫn tới trang có nội dung (data-driven)"""
        k.content.click_home_link(case["link"], case.get("section"))
        k.common.verify_url(case["href"])
        k.content.verify_page_rendered()


class TestHomeEmptyData:
    """Dữ liệu mock: trường hợp rỗng"""

    def test_no_vouchers(self, k):
        """[SF-HOME-10] Không có voucher -> ẩn khối ƯU ĐÃI NỔI BẬT"""
        k.content.mock_home_data({**MOCK, "data": {**MOCK["data"], "vouchers": []}})
        k.content.open_home_page()
        k.content.verify_no_voucher_section()

    def test_no_news(self, k):
        """[SF-HOME-19] Không có tin tức -> "Chưa có tin tức thời trang nào", ẩn "Xem thêm\""""
        k.content.mock_home_data({**MOCK, "data": {**MOCK["data"], "news": []}})
        k.content.open_home_page()
        k.content.verify_home_news_empty()
