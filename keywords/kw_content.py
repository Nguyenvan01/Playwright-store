# THƯ VIỆN KEYWORD - NHÓM content: các khối trang chủ, blog, trang tĩnh, footer, newsletter.
import copy
import re
from datetime import datetime, timedelta, timezone
from urllib.parse import unquote, urlparse

from playwright.sync_api import expect

from keywords.base_keywords import BaseKeywords, keyword
from pages.storefront.blog_pages import BlogDetailPage, BlogListPage
from pages.storefront.home_sections import HomeSections
from pages.storefront.site_chrome import SiteChrome
from utils.assertions import poll_until
from utils.storage import detect_reload, read_cart

ACTIVE_TAB = re.compile(r"text-\[#DA291C\]")


def _iso_in_days(days):
    # Giống new Date(Date.now() + n * 86_400_000).toISOString() của JS.
    moment = datetime.now(timezone.utc) + timedelta(days=days)
    return moment.isoformat(timespec="milliseconds").replace("+00:00", "Z")


class ContentKeywords(BaseKeywords):
    group = "content"

    def __init__(self, page, po, api, common=None):
        super().__init__(page, po, api, common)
        self._home = HomeSections(page)
        self._chrome = SiteChrome(page)
        self._blog_list = BlogListPage(page)
        self._blog_detail = BlogDetailPage(page)

    # ---------------------------------------------------------------------------
    # Trang chủ
    # ---------------------------------------------------------------------------

    @keyword("mockHomeData")
    def mock_home_data(self, response):
        """Mock GET /api/home bằng dữ liệu cho trước (voucher có "expiresInDays" được đổi thành ngày hết hạn tính từ hôm nay)."""
        with self.step("Mock dữ liệu trang chủ (GET /api/home)"):
            body = copy.deepcopy(response)
            for voucher in (body.get("data") or {}).get("vouchers") or []:
                days = voucher.get("expiresInDays")
                if isinstance(days, (int, float)) and not isinstance(days, bool):
                    voucher["expiry"] = _iso_in_days(days)
                    voucher["valid_until"] = voucher["expiry"]
            self.page.route(
                "**/api/home",
                lambda route: route.fulfill(json=body)
                if route.request.method == "GET"
                else route.fallback(),
            )

    @keyword("openHomePage")
    def open_home_page(self):
        """Mở trang chủ và chờ khối SẢN PHẨM MỚI hiển thị (không yêu cầu có sản phẩm)."""
        with self.step("Mở trang chủ (chờ các khối nội dung)"):
            self.page.goto("/")
            expect(self._home.new_products_heading).to_be_visible()

    @keyword("verifyHomeSections")
    def verify_home_sections(self, titles):
        """Kiểm tra trang chủ có đủ các khối theo tiêu đề h2, đúng thứ tự."""
        with self.step(f"Kiểm tra {len(titles)} khối nội dung trang chủ"):
            expect(self.page.locator("main h2").filter(visible=True)).to_contain_text(titles)

    @keyword("verifyBannerSlideCount")
    def verify_banner_slide_count(self, count):
        """Kiểm tra số slide banner và số chấm điều hướng."""
        with self.step(f"Kiểm tra banner có {count} slide"):
            expect(self._home.banner_slides).to_have_count(count)
            expect(self._home.banner_dots).to_have_count(count)

    @keyword("verifyActiveBannerSlide")
    def verify_active_banner_slide(self, slide):
        """Kiểm tra slide banner đang hiển thị (đánh số từ 1)."""
        with self.step(f"Kiểm tra banner đang ở slide {slide}"):
            expect(self._home.banner_slides.nth(slide - 1)).to_have_class(re.compile(r"opacity-100"))
            expect(self._home.active_slide()).to_have_count(1)
            expect(self._home.banner_dots.nth(slide - 1)).to_have_class(re.compile(r"w-8"))

    @keyword("clickBannerArrow")
    def click_banner_arrow(self, direction):
        """Bấm nút mũi tên banner: "next" hoặc "prev"."""
        with self.step(f"Bấm mũi tên banner {'sau' if direction == 'next' else 'trước'}"):
            (self._home.banner_next if direction == "next" else self._home.banner_prev).click()

    @keyword("clickBannerDot")
    def click_banner_dot(self, slide):
        """Bấm chấm điều hướng banner thứ n (đánh số từ 1)."""
        with self.step(f"Bấm chấm banner số {slide}"):
            self._home.banner_dots.nth(slide - 1).click()

    @keyword("freezeClock")
    def freeze_clock(self):
        """Cố định đồng hồ trình duyệt (banner không tự chuyển slide) - gọi TRƯỚC khi mở trang."""
        with self.step("Cố định đồng hồ trình duyệt"):
            self.page.clock.install()

    @keyword("verifyBannerAutoplay")
    def verify_banner_autoplay(self, to_slide):
        """Cho đồng hồ (đã cố định bằng freezeClock) chạy 4 giây và kiểm tra banner tự chuyển sang slide kế tiếp."""
        with self.step(f"Kiểm tra banner tự chuyển sang slide {to_slide} sau 4 giây"):
            target = self._home.banner_slides.nth(to_slide - 1)
            expect(target).not_to_have_class(re.compile(r"opacity-100"))
            self.page.clock.run_for(4_100)
            expect(target).to_have_class(re.compile(r"opacity-100"))

    @keyword("verifyBannerSlideLinks")
    def verify_banner_slide_links(self, hrefs):
        """Kiểm tra link (href) của từng slide banner theo thứ tự."""
        with self.step(f"Kiểm tra link các slide banner: {', '.join(hrefs)}"):
            for i, href in enumerate(hrefs):
                expect(self._home.banner_slides.nth(i)).to_have_attribute("href", href)

    @keyword("verifyBannerOverlay")
    def verify_banner_overlay(self, slide, title, href):
        """Kiểm tra chữ đè trên slide banner (đánh số từ 1): tiêu đề + nút "Khám phá ngay" trỏ đúng link."""
        with self.step(f'Kiểm tra chữ trên slide {slide}: "{title}" -> {href}'):
            expect(self._home.banner_overlay_title(slide - 1)).to_have_text(title)
            expect(self._home.banner_overlay_cta(slide - 1)).to_have_attribute("href", href)

    @keyword("verifyVoucher")
    def verify_voucher(self, voucher):
        """Kiểm tra 1 thẻ voucher trong khối "ƯU ĐÃI NỔI BẬT" (tiêu đề, mô tả, điều kiện, hạn dùng)."""
        with self.step(f'Kiểm tra voucher "{voucher["title"]}"'):
            card = self._home.voucher_card(voucher["title"])
            expect(card).to_have_count(1)
            expect(card).to_contain_text(voucher["description"])
            expect(card).to_contain_text(voucher["condition"])
            expect(card).to_contain_text(voucher["validity"])
            expect(card.get_by_role("button", name="Dùng mã")).to_be_visible()

    @keyword("useVoucher")
    def use_voucher(self, title):
        """Bấm "Dùng mã" của 1 voucher."""
        with self.step(f'Bấm "Dùng mã" voucher "{title}"'):
            self._home.voucher_card(title).get_by_role("button", name="Dùng mã").click()

    @keyword("verifyPendingVoucher")
    def verify_pending_voucher(self, code):
        """Kiểm tra mã voucher đã được lưu tạm vào sessionStorage (pendingVoucher)."""
        with self.step(f"Kiểm tra voucher chờ áp dụng = {code}"):
            poll_until(
                lambda: self.page.evaluate(
                    "() => JSON.parse(sessionStorage.getItem('pendingVoucher') || 'null')?.code ?? null"
                )
                == code,
                f"pendingVoucher.code khác {code!r}",
            )

    @keyword("verifyNoVoucherSection")
    def verify_no_voucher_section(self):
        """Kiểm tra khối "ƯU ĐÃI NỔI BẬT" bị ẩn (không có voucher)."""
        with self.step("Kiểm tra không hiển thị khối ƯU ĐÃI NỔI BẬT"):
            expect(self._home.voucher_heading).to_have_count(0)

    @keyword("verifyNewProductTabs")
    def verify_new_product_tabs(self, tabs):
        """Kiểm tra các tab của khối SẢN PHẨM MỚI, tab đầu đang được chọn."""
        with self.step(f"Kiểm tra tab SẢN PHẨM MỚI: {', '.join(tabs)}"):
            expect(self._home.new_products_tabs).to_have_text(tabs)
            expect(self._home.new_products_tab(tabs[0])).to_have_class(ACTIVE_TAB)

    @keyword("selectNewProductTab")
    def select_new_product_tab(self, tab):
        """Bấm 1 tab trong khối SẢN PHẨM MỚI."""
        with self.step(f'Chọn tab "{tab}" ở SẢN PHẨM MỚI'):
            self._home.new_products_tab(tab).click()

    @keyword("verifyNewProductsFiltered")
    def verify_new_products_filtered(self, tab, visible, hidden):
        """Kiểm tra tab được chọn và danh sách SẢN PHẨM MỚI đã lọc: có sản phẩm visible, không còn sản phẩm hidden."""
        with self.step(f'Kiểm tra tab "{tab}" lọc sản phẩm: có "{visible}", không có "{hidden}"'):
            expect(self._home.new_products_tab(tab)).to_have_class(ACTIVE_TAB, timeout=3_000)
            expect(self._home.new_product_cards().filter(has_text=visible).first).to_be_visible()
            expect(self._home.new_product_cards().filter(has_text=hidden)).to_have_count(
                0, timeout=3_000
            )

    @keyword("verifyNewProductCount")
    def verify_new_product_count(self, count):
        """Kiểm tra số thẻ sản phẩm trong carousel SẢN PHẨM MỚI."""
        with self.step(f"Kiểm tra SẢN PHẨM MỚI có {count} sản phẩm"):
            expect(self._home.new_product_cards()).to_have_count(count)

    @keyword("scrollNewProducts")
    def scroll_new_products(self, direction):
        """Bấm mũi tên carousel SẢN PHẨM MỚI ("next"/"prev") và kiểm tra danh sách cuộn đúng chiều."""
        with self.step(f"Cuộn carousel SẢN PHẨM MỚI ({direction})"):
            scroller = self._home.new_products_scroll
            before = scroller.evaluate("(el) => el.scrollLeft")
            forward = direction == "next"
            (self._home.new_products_next if forward else self._home.new_products_prev).click()

            def moved():
                now = scroller.evaluate("(el) => el.scrollLeft")
                return now > before if forward else now < before

            poll_until(moved, f"scrollLeft phải {'tăng' if forward else 'giảm'} từ {before}")

    @keyword("verifyPromoBlock")
    def verify_promo_block(self, title, description, card_count):
        """Kiểm tra khối HOMEWEAR/T-SHIRT/VÁY: mô tả và số thẻ sản phẩm (tối đa 4)."""
        with self.step(f'Kiểm tra khối "{title}" ({card_count} sản phẩm)'):
            block = self._home.promo_block(title)
            expect(block.get_by_text(description)).to_be_visible()
            expect(self._home.promo_block_cards(title)).to_have_count(card_count)
            expect(self._home.promo_block_link(title, "Khám phá ngay")).to_be_visible()
            expect(block.get_by_role("link", name="Xem tất cả")).to_be_visible()

    @keyword("verifyCollection")
    def verify_collection(self, title, cta_text, href):
        """Kiểm tra 1 ô bộ sưu tập: tiêu đề, chữ trên nút CTA và link."""
        with self.step(f'Kiểm tra bộ sưu tập "{title}" -> nút "{cta_text}" ({href})'):
            expect(self._home.collection_tile(title)).to_be_visible()
            expect(self._home.collection_cta(title)).to_have_attribute("href", href)
            expect(self._home.collection_cta(title)).to_have_text(cta_text)

    @keyword("verifyCLive")
    def verify_c_live(self, texts):
        """Kiểm tra khối C-LIVE: tiêu đề, ảnh và các đoạn chữ."""
        with self.step("Kiểm tra khối C-LIVE"):
            expect(self._home.clive_heading).to_be_visible()
            expect(self._home.clive_image).to_be_visible()
            for text in texts:
                expect(self.page.get_by_text(text, exact=True)).to_be_visible()

    @keyword("verifyHomeNews")
    def verify_home_news(self, featured_title, secondary_count):
        """Kiểm tra khối "Tin tức thời trang": bài nổi bật + số bài phụ + nút "Xem thêm"."""
        with self.step(f'Kiểm tra Tin tức thời trang: "{featured_title}" + {secondary_count} bài'):
            expect(self._home.blog_featured_title).to_have_text(featured_title)
            expect(self._home.blog_secondary_titles).to_have_count(secondary_count)
            expect(self._home.blog_see_more).to_be_visible()

    @keyword("verifyHomeNewsLink")
    def verify_home_news_link(self, title, slug):
        """Kiểm tra link bài nổi bật trong khối Tin tức trỏ tới /blog/{slug}."""
        with self.step(f'Kiểm tra tin "{title}" -> /blog/{slug}'):
            # Ảnh và tiêu đề là 2 link riêng, cả 2 phải trỏ tới bài viết
            links = self._home.blog_section.get_by_role("link", name=title)
            expect(links).to_have_count(2)
            for link in links.all():
                expect(link).to_have_attribute("href", f"/blog/{slug}")

    @keyword("verifyHomeNewsEmpty")
    def verify_home_news_empty(self):
        """Kiểm tra khối Tin tức hiển thị trạng thái rỗng và ẩn nút "Xem thêm"."""
        with self.step("Kiểm tra khối Tin tức rỗng"):
            expect(self._home.blog_empty).to_be_visible()
            expect(self._home.blog_see_more).to_have_count(0)

    @keyword("clickHomeNewsSeeMore")
    def click_home_news_see_more(self):
        """Bấm "Xem thêm" của khối Tin tức thời trang."""
        with self.step('Bấm "Xem thêm" khối Tin tức'):
            self._home.blog_see_more.click()

    @keyword("clickHomeLink")
    def click_home_link(self, link, section=None):
        """Bấm 1 link trên trang chủ theo tên; section = tiêu đề khối chứa link (để trống = khối SẢN PHẨM MỚI)."""
        suffix = f" trong khối {section}" if section else ""
        with self.step(f'Bấm link "{link}"{suffix}'):
            target = (
                self._home.promo_block(section).get_by_role("link", name=link, exact=True)
                if section
                else self._home.new_products_block.get_by_role("link", name=link)
            )
            target.first.click()

    @keyword("verifyPageRendered")
    def verify_page_rendered(self):
        """Kiểm tra trang đích đã render nội dung (có header, footer) - không phải trang trắng."""
        with self.step("Kiểm tra trang đích hiển thị nội dung (header + footer)"):
            expect(self._chrome.page.locator("header").first).to_be_visible()
            expect(self._chrome.footer).to_be_visible()

    @keyword("quickAddToCart")
    def quick_add_to_cart(self, product_name):
        """Bấm icon thêm nhanh vào giỏ trên thẻ sản phẩm (ProductCard) theo tên."""
        with self.step(f'Thêm nhanh "{product_name}" vào giỏ từ thẻ sản phẩm'):
            self._home.product_card(product_name).first.hover()
            self._home.quick_add_button(product_name).click()

    @keyword("verifyStoredCartItemHasSize")
    def verify_stored_cart_item_has_size(self, product_name):
        """Kiểm tra sản phẩm trong giỏ (localStorage) đã có size được chọn."""
        with self.step(f'Kiểm tra "{product_name}" trong giỏ có size'):
            poll_until(
                lambda: any(i.get("name") == product_name for i in read_cart(self.page)),
                f'Không thấy "{product_name}" trong giỏ (localStorage)',
            )
            item = next((i for i in read_cart(self.page) if i.get("name") == product_name), None)
            assert item and item.get("size"), (
                f'Sản phẩm "{product_name}" được thêm vào giỏ mà không có size: {item!r}'
            )

    # ---------------------------------------------------------------------------
    # Newsletter + Footer
    # ---------------------------------------------------------------------------

    @keyword("subscribeNewsletter")
    def subscribe_newsletter(self, email):
        """Nhập email vào khối "Đăng ký nhận tin" và bấm "Đăng ký"."""
        with self.step(f'Đăng ký nhận tin với "{email}"'):
            self._chrome.newsletter_email.fill(email)
            self._chrome.newsletter_submit.click()

    @keyword("verifyNewsletterThanks")
    def verify_newsletter_thanks(self):
        """Kiểm tra hiện "Cảm ơn bạn đã đăng ký!" rồi form tự hiện lại sau khoảng 4 giây."""
        with self.step("Kiểm tra cảm ơn đăng ký nhận tin và form hiện lại"):
            expect(self._chrome.newsletter_thanks).to_be_visible()
            expect(self._chrome.newsletter_email).to_be_hidden()
            expect(self._chrome.newsletter_thanks).to_be_hidden(timeout=8_000)
            expect(self._chrome.newsletter_email).to_have_value(re.compile(r".+"))

    @keyword("verifyNewsletterBlocked")
    def verify_newsletter_blocked(self, validity):
        """Kiểm tra trình duyệt chặn gửi form nhận tin (HTML5 validation), vd: "valueMissing", "typeMismatch"."""
        with self.step(f"Kiểm tra form nhận tin bị chặn ({validity})"):
            state = self._chrome.newsletter_email.evaluate(
                "(el, key) => ({ flag: el.validity[key], message: el.validationMessage })",
                validity,
            )
            assert state["flag"] is True, f"validity.{validity}: expected=True, actual={state['flag']!r}"
            assert state["message"] != "", "validationMessage rỗng"
            expect(self._chrome.newsletter_thanks).to_have_count(0)

    @keyword("verifyFooterContent")
    def verify_footer_content(self, headings, links):
        """Kiểm tra footer: các tiêu đề cột, link và dòng bản quyền."""
        with self.step("Kiểm tra nội dung footer"):
            for heading in headings:
                expect(self._chrome.footer_heading(heading)).to_be_visible()
            for link in links:
                expect(self._chrome.footer_link(link)).to_be_visible()
            expect(self._chrome.footer_copyright).to_be_visible()

    @keyword("verifyFooterLink")
    def verify_footer_link(self, name, href):
        """Kiểm tra 1 link footer trỏ đúng đường dẫn."""
        with self.step(f'Kiểm tra footer "{name}" -> {href}'):
            expect(self._chrome.footer_link(name)).to_have_attribute("href", href)

    @keyword("verifyFooterHasLinkTo")
    def verify_footer_has_link_to(self, href):
        """Kiểm tra footer có ít nhất 1 link trỏ tới đường dẫn."""
        with self.step(f"Kiểm tra footer có link tới {href}"):
            expect(self._chrome.footer_link_to(href).first).to_be_attached()

    # ---------------------------------------------------------------------------
    # Blog
    # ---------------------------------------------------------------------------

    @keyword("mockBlogData")
    def mock_blog_data(self, response):
        """Mock API blog: danh sách GET /api/news và chi tiết GET /api/news/:slug (404 nếu slug không có trong danh sách)."""
        with self.step(f"Mock blog ({len(response['news'])} bài)"):
            self.page.route(
                "**/api/news?**",
                lambda route: route.fulfill(json=response)
                if route.request.method == "GET"
                else route.fallback(),
            )

            def detail(route):
                if route.request.method != "GET":
                    return route.fallback()
                slug = unquote(urlparse(route.request.url).path.split("/")[-1])
                article = next((a for a in response["news"] if a["slug"] == slug), None)
                if article:
                    return route.fulfill(json={"success": True, "article": article})
                return route.fulfill(
                    status=404, json={"success": False, "message": "Không tìm thấy bài viết"}
                )

            self.page.route("**/api/news/*", detail)

    @keyword("openBlog")
    def open_blog(self):
        """Mở trang /blog và chờ danh sách bài viết tải xong."""
        with self.step("Mở trang Blog"):
            self._blog_list.open()
            expect(self._blog_list.heading).to_be_visible()
            expect(self._blog_list.cards.first.or_(self._blog_list.empty_state)).to_be_visible()

    @keyword("verifyBlogLoaded")
    def verify_blog_loaded(self):
        """Kiểm tra trang Blog: tiêu đề, mô tả và có ít nhất 1 bài viết."""
        with self.step("Kiểm tra trang Blog có bài viết"):
            expect(self._blog_list.heading).to_be_visible()
            expect(self._blog_list.subtitle).to_be_visible()
            expect(self._blog_list.cards.first).to_be_visible()
            expect(self._blog_list.pill("Tất cả")).to_be_visible()

    @keyword("verifyBlogPills")
    def verify_blog_pills(self, pills):
        """Kiểm tra các nút danh mục (pill) trên trang Blog theo thứ tự."""
        with self.step(f"Kiểm tra danh mục blog: {', '.join(pills)}"):
            expect(self._blog_list.category_pills).to_have_text(pills)

    @keyword("filterBlogByCategory")
    def filter_blog_by_category(self, category):
        """Bấm 1 danh mục (pill) trên trang Blog."""
        with self.step(f'Lọc blog theo "{category}"'):
            self._blog_list.pill(category).click()
            expect(self._blog_list.pill(category)).to_have_class(re.compile(r"bg-slate-900"))

    @keyword("verifyBlogTitles")
    def verify_blog_titles(self, titles):
        """Kiểm tra danh sách bài viết đang hiển thị đúng các tiêu đề (theo thứ tự)."""
        with self.step(f"Kiểm tra {len(titles)} bài viết hiển thị"):
            expect(self._blog_list.cards.locator("h2")).to_have_text(titles)

    @keyword("verifyBlogCategoryOfCards")
    def verify_blog_category_of_cards(self, category):
        """Kiểm tra mọi bài viết đang hiển thị đều thuộc danh mục."""
        with self.step(f'Kiểm tra mọi bài thuộc danh mục "{category}"'):
            count = self._blog_list.cards.count()
            assert count > 0, f"Không có bài viết nào: count={count}"
            expect(self._blog_list.card_categories()).to_have_text([category] * count)

    @keyword("verifyBlogEmpty")
    def verify_blog_empty(self):
        """Kiểm tra trang Blog báo không có bài viết."""
        with self.step("Kiểm tra blog không có bài viết"):
            expect(self._blog_list.empty_state).to_be_visible()
            expect(self._blog_list.cards).to_have_count(0)

    @keyword("openBlogArticle")
    def open_blog_article(self, title):
        """Bấm 1 bài viết trên trang Blog theo tiêu đề."""
        with self.step(f'Mở bài viết "{title}"'):
            self._blog_list.card(title).click()
            expect(self._blog_detail.title).to_have_text(title)

    @keyword("openBlogArticleBySlug")
    def open_blog_article_by_slug(self, slug):
        """Mở thẳng trang chi tiết bài viết /blog/{slug}."""
        with self.step(f"Mở /blog/{slug}"):
            self._blog_detail.open(slug)

    @keyword("verifyBlogArticle")
    def verify_blog_article(self, c):
        """Kiểm tra trang chi tiết bài viết: URL, tiêu đề, danh mục, tác giả, lượt xem, tag, bài liên quan."""
        with self.step(f'Kiểm tra chi tiết bài "{c["titleText"]}"'):
            expect(self.page).to_have_url(f"/blog/{c['slug']}")
            expect(self._blog_detail.title).to_have_text(c["titleText"])
            expect(self._blog_detail.back_link).to_have_attribute("href", "/blog")
            expect(self._blog_detail.category_badge).to_have_text(c["category"])
            expect(self._blog_detail.author).to_have_text(c["author"])
            expect(self._blog_detail.view_count).to_have_text(re.compile(f"{c['views']} lượt xem$"))
            if c["articleTags"]:
                for tag in c["articleTags"]:
                    expect(self._blog_detail.tag(tag)).to_be_visible()
            else:
                expect(self._blog_detail.tags_section).to_have_count(0)
            if c["related"]:
                expect(self._blog_detail.related_cards.locator("h3")).to_have_text(c["related"])
            else:
                expect(self._blog_detail.related_heading).to_have_count(0)
            if c.get("fallback"):
                expect(self._blog_detail.content_fallback).to_be_visible()

    @keyword("clickBackToBlog")
    def click_back_to_blog(self):
        """Bấm "Quay lại Blog" trên trang chi tiết bài viết."""
        with self.step('Bấm "Quay lại Blog"'):
            self._blog_detail.back_link.click()
            expect(self._blog_list.heading).to_be_visible()

    @keyword("openRelatedArticle")
    def open_related_article(self, title):
        """Bấm 1 bài trong "Bài viết liên quan"."""
        with self.step(f'Mở bài liên quan "{title}"'):
            self._blog_detail.related_card(title).click()
            expect(self._blog_detail.title).to_have_text(title)

    @keyword("subscribeBlogNewsletterWithoutReload")
    def subscribe_blog_newsletter_without_reload(self, email):
        """Đăng ký nhận tin ở trang Blog và kiểm tra trang KHÔNG bị tải lại (form phải được xử lý bằng JS)."""
        with self.step(f'Đăng ký nhận tin trên Blog với "{email}" (không reload)'):
            self._blog_list.newsletter_email.fill(email)
            watcher = detect_reload(self.page, 4_000)
            self._blog_list.newsletter_submit.click()
            assert watcher.reloaded() is False, (
                "Form nhận tin ở /blog làm tải lại trang (thiếu onSubmit)"
            )
            expect(self._blog_list.newsletter_email).to_have_value(email)

    # ---------------------------------------------------------------------------
    # Trang tĩnh / route không tồn tại
    # ---------------------------------------------------------------------------

    @keyword("verifyPageHeadings")
    def verify_page_headings(self, h1, h2, h3):
        """Kiểm tra các tiêu đề trong <main>: h1 đúng, h2/h3 chứa đủ các mục (theo thứ tự)."""
        with self.step(f'Kiểm tra tiêu đề trang "{h1}"'):
            expect(self._chrome.main_headings(1)).to_have_text([h1])
            if h2:
                expect(self._chrome.main_headings(2)).to_contain_text(h2)
            if h3:
                expect(self._chrome.main_headings(3)).to_contain_text(h3)

    @keyword("verifyMainContains")
    def verify_main_contains(self, texts):
        """Kiểm tra <main> có chứa các đoạn chữ."""
        with self.step(f"Kiểm tra nội dung có {len(texts)} đoạn chữ"):
            for text in texts:
                expect(self._chrome.main).to_contain_text(text)

    @keyword("verifyBlockContains")
    def verify_block_contains(self, heading, text):
        """Kiểm tra khối có tiêu đề h3 (vd: thẻ "Giao hàng nhanh") chứa đoạn chữ."""
        with self.step(f'Kiểm tra khối "{heading}" chứa "{text}"'):
            block = self._chrome.main.locator("h3", has_text=heading).first.locator("xpath=..")
            expect(block).to_contain_text(text)

    @keyword("verifyMainNotMatching")
    def verify_main_not_matching(self, pattern):
        """Kiểm tra <main> KHÔNG chứa chuỗi khớp biểu thức chính quy (vd: ký tự Cyrillic)."""
        with self.step(f"Kiểm tra nội dung không khớp /{pattern}/"):
            expect(self._chrome.main).to_be_visible()
            expect(self._chrome.main).not_to_contain_text(re.compile(pattern))

    @keyword("verifyNotFoundPage")
    def verify_not_found_page(self, message):
        """Kiểm tra route không tồn tại hiển thị trang báo lỗi (thông báo + layout)."""
        with self.step(f'Kiểm tra trang "không tìm thấy": "{message}"'):
            expect(self._chrome.body).to_contain_text(message)
            expect(self.page.locator("header").first).to_be_visible()
