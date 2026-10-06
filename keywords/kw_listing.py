# THƯ VIỆN KEYWORD - NHÓM listing: trang danh sách sản phẩm Nam/Nữ/Trẻ em/Giảm giá,
# bộ lọc, sắp xếp, phân trang, trang /search.
import json
import re
from urllib.parse import parse_qs, urlparse

from playwright.sync_api import expect

from keywords.base_keywords import BaseKeywords, keyword
from pages.storefront.listing_page import ListingPage
from pages.storefront.search_results_page import SearchResultsPage
from utils.assertions import poll_until

EMPTY_LISTING = re.compile(r"^Không (tìm thấy|có) sản phẩm")
PRODUCTS_PATH = re.compile(r"/api/products(/kids)?$")


def to_number(text):
    """Đổi "1.234.000đ" -> 1234000."""
    digits = re.sub(r"[^\d]", "", text or "")
    return int(digits) if digits else 0


class ListingKeywords(BaseKeywords):
    group = "listing"

    def __init__(self, page, po, api, common=None):
        super().__init__(page, po, api, common)
        self._listing = ListingPage(page)
        self._results = SearchResultsPage(page)
        # URL các request GET danh sách sản phẩm (/api/products...) - để kiểm tra tham số lọc.
        self._product_requests = []
        # href của thẻ sản phẩm vừa thao tác (để kiểm tra điều hướng).
        self._last_card_href = ""
        page.on("request", self._on_request)

    def _on_request(self, request):
        url = urlparse(request.url)
        if request.method == "GET" and PRODUCTS_PATH.search(url.path):
            self._product_requests.append(url)

    # ---------------------------------------------------------------------------
    # /nam, /nu, /tre-em, /giam-gia
    # ---------------------------------------------------------------------------

    @keyword("openListing")
    def open_listing(self, path):
        """Mở trang danh sách (vd: "/nam") và chờ tải xong (có sản phẩm hoặc thông báo rỗng)."""
        with self.step(f"Mở trang danh sách {path}"):
            self._listing.open(path)
            self._wait_listing_settled()

    @keyword("verifyListingHeader")
    def verify_listing_header(self, heading, breadcrumb, description):
        """Kiểm tra đầu trang danh sách: breadcrumb "Trang chủ > {mục}", tiêu đề h1, đoạn mô tả."""
        with self.step(f'Kiểm tra đầu trang "{heading}"'):
            expect(self._listing.heading).to_have_text(heading)
            expect(self._listing.breadcrumb.get_by_role("link", name="Trang chủ")).to_have_attribute(
                "href", "/"
            )
            expect(self._listing.breadcrumb.locator("span").last).to_have_text(breadcrumb)
            expect(self.page.get_by_text(description)).to_be_visible()

    @keyword("verifyCountMatchesCards")
    def verify_count_matches_cards(self):
        """Kiểm tra dòng "Hiển thị n trên t sản phẩm": n = số thẻ đang hiển thị và n <= t."""
        with self.step('Kiểm tra "Hiển thị n trên t sản phẩm" khớp số thẻ'):
            self._wait_listing_settled()
            text = self._listing.count_text.text_content() or ""
            match = re.search(r"Hiển thị (\d+) trên (\d+)", text)
            assert match, f"Không đọc được số lượng: {text!r}"
            shown, total = int(match.group(1)), int(match.group(2))
            expect(self._listing.cards).to_have_count(shown)
            assert shown <= total, f"Số hiển thị lớn hơn tổng: shown={shown}, total={total}"

    @keyword("verifyCountText")
    def verify_count_text(self, text):
        """Kiểm tra chính xác dòng "Hiển thị n trên t sản phẩm"."""
        with self.step(f'Kiểm tra "{text}"'):
            expect(self._listing.count_text).to_have_text(text)

    @keyword("verifySortOptions")
    def verify_sort_options(self, options, selected):
        """Kiểm tra các lựa chọn sắp xếp (theo thứ tự) và lựa chọn đang được chọn."""
        with self.step(f'Kiểm tra sắp xếp: {" / ".join(options)} (đang chọn "{selected}")'):
            expect(self._listing.sort_select.locator("option")).to_have_text(options)
            value = self._listing.sort_select.input_value()
            expect(self._listing.sort_select.locator(f'option[value="{value}"]')).to_have_text(selected)

    @keyword("sortBy")
    def sort_by(self, option):
        """Chọn kiểu sắp xếp theo nhãn, vd: "Giá: Thấp → Cao"."""
        with self.step(f'Sắp xếp theo "{option}"'):
            self._listing.sort_select.select_option(label=option)

    @keyword("verifyPricesSorted")
    def verify_prices_sorted(self, order):
        """Kiểm tra giá trên các thẻ sản phẩm đã sắp xếp: "asc" tăng dần, "desc" giảm dần."""
        with self.step(f"Kiểm tra giá sắp xếp {'tăng' if order == 'asc' else 'giảm'} dần"):
            self._expect_sorted(
                lambda: self._read_prices(self._listing.cards, self._listing.card_price), order
            )

    @keyword("verifyCategoryOptions")
    def verify_category_options(self, names):
        """Kiểm tra các nút danh mục đang hiển thị trong bộ lọc (theo thứ tự)."""
        with self.step(f"Kiểm tra danh mục lọc: {', '.join(names)}"):
            expect(self._listing.category_buttons()).to_have_text(names)

    @keyword("showMoreCategories")
    def show_more_categories(self):
        """Bấm "Xem thêm +" trong nhóm danh mục để hiện các danh mục còn lại."""
        with self.step('Bấm "Xem thêm +" ở danh mục'):
            self._listing.show_more_categories.click()
            expect(self._listing.show_more_categories).to_be_hidden()

    @keyword("selectCategory")
    def select_category(self, name):
        """Bấm 1 danh mục trong bộ lọc và kiểm tra nút được đánh dấu chọn."""
        with self.step(f'Lọc danh mục "{name}"'):
            self._listing.category_button(name).click()
            expect(self._listing.category_button(name)).to_have_class(re.compile(r"font-semibold"))

    @keyword("verifySizeOptions")
    def verify_size_options(self, sizes):
        """Kiểm tra các nút size trong bộ lọc "Kích cỡ"."""
        with self.step(f"Kiểm tra size lọc: {', '.join(sizes)}"):
            expect(self._listing.size_buttons()).to_have_text(sizes)

    @keyword("selectSizeFilter")
    def select_size_filter(self, size):
        """Bấm 1 size trong bộ lọc "Kích cỡ"."""
        with self.step(f'Lọc size "{size}"'):
            self._listing.size_button(size).click()

    @keyword("verifyColorOptions")
    def verify_color_options(self, colors):
        """Kiểm tra các ô màu trong bộ lọc "Màu sắc" (theo thuộc tính title)."""
        with self.step(f"Kiểm tra màu lọc: {', '.join(colors)}"):
            titles = self._listing.color_buttons().evaluate_all(
                "els => els.map((e) => e.getAttribute('title'))"
            )
            assert titles == colors, f"Màu lọc: expected={colors!r}, actual={titles!r}"

    @keyword("selectColorFilter")
    def select_color_filter(self, color):
        """Bấm 1 màu trong bộ lọc "Màu sắc" (theo title) và kiểm tra có dấu tích."""
        with self.step(f'Lọc màu "{color}"'):
            self._listing.color_button(color).click()
            expect(self._listing.color_button(color).locator("svg")).to_be_visible()

    @keyword("verifyPriceInputs")
    def verify_price_inputs(self, from_value, to_value):
        """Kiểm tra giá trị mặc định 2 ô khoảng giá "Từ" / "Đến"."""
        with self.step(f"Kiểm tra khoảng giá mặc định {from_value} - {to_value}"):
            expect(self._listing.price_from).to_have_value(from_value)
            expect(self._listing.price_to).to_have_value(to_value)

    @keyword("setPriceRange")
    def set_price_range(self, from_value, to_value):
        """Nhập khoảng giá "Từ" - "Đến" (vd: "300000", "600000"); bộ lọc áp dụng khi rời ô nhập."""
        with self.step(f"Lọc giá {from_value} - {to_value}"):
            # Mỗi ô gọi API riêng khi blur và app không hủy request cũ: nếu nhập liền 2 ô, response cũ
            # (chỉ có min_price) có thể về sau và ghi đè kết quả. Đợi từng request xong để test ổn định.
            server_side = "/giam-gia" not in self.page.url  # trang Giảm giá lọc phía client

            def apply_and_wait(input_box, value, param):
                if server_side:
                    with self.page.expect_response(
                        lambda r: "/api/products" in r.url and param in r.url
                    ):
                        input_box.fill(value)
                        input_box.blur()
                else:
                    input_box.fill(value)
                    input_box.blur()
                self._wait_listing_settled()

            apply_and_wait(self._listing.price_from, from_value, "min_price=")
            apply_and_wait(self._listing.price_to, to_value, "max_price=")

    @keyword("verifyPricesWithin")
    def verify_prices_within(self, min_price, max_price):
        """Kiểm tra mọi giá đang hiển thị nằm trong khoảng [min, max]."""
        with self.step(f"Kiểm tra mọi giá trong khoảng {min_price} - {max_price}"):

            def outside():
                self._wait_listing_settled()
                prices = self._read_prices(self._listing.cards, self._listing.card_price)
                return [p for p in prices if p < min_price or p > max_price]

            self._poll_empty(outside, "Có giá nằm ngoài khoảng lọc")

    @keyword("selectDiscount")
    def select_discount(self, label):
        """Tick 1 mức "Phần trăm giảm" (tự mở nhóm lọc nếu đang đóng), vd: "Giảm 30%"."""
        with self.step(f'Lọc "{label}"'):
            toggle = self._listing.filter_section_toggle("Phần trăm giảm")
            if "+" in (toggle.text_content() or ""):
                toggle.click()
            self._listing.discount_label(label).click()
            expect(self._listing.discount_checkbox(label)).to_be_checked()

    @keyword("verifyDiscountAtLeast")
    def verify_discount_at_least(self, percent):
        """Kiểm tra mọi thẻ đang hiển thị có nhãn giảm giá >= phần trăm cho trước."""
        with self.step(f"Kiểm tra mọi sản phẩm giảm >= {percent}%"):

            def below():
                self._wait_listing_settled()
                bad = []
                for card in self._listing.cards.all():
                    badges = self._listing.card_discount_badge(card).all_text_contents()
                    value = to_number(badges[0]) if badges else 0
                    if value < percent:
                        bad.append(f"{self._listing.card_title(card).text_content()} ({value}%)")
                return bad

            self._poll_empty(below, f"Có sản phẩm giảm ít hơn {percent}%")

    @keyword("verifyListRequest")
    def verify_list_request(self, params):
        """Kiểm tra đã gọi API danh sách sản phẩm với các tham số query, vd: {"min_price":"300000"}."""
        params_text = json.dumps(params, ensure_ascii=False)
        with self.step(f"Kiểm tra API danh sách được gọi với {params_text}"):

            def matches():
                for url in self._product_requests:
                    query = parse_qs(url.query, keep_blank_values=True)
                    if all(query.get(k, [None])[0] == v for k, v in params.items()):
                        return True
                return False

            try:
                poll_until(matches, "", timeout=5_000)
            except AssertionError:
                called = "\n".join(
                    u.path + (f"?{u.query}" if u.query else "") for u in self._product_requests
                )
                raise AssertionError(
                    f"Không có request /api/products khớp {params_text}. Đã gọi:\n{called}"
                ) from None

    @keyword("verifyProductsShown")
    def verify_products_shown(self):
        """Kiểm tra danh sách có ít nhất 1 sản phẩm và dòng "Hiển thị n trên t" với n > 0."""
        with self.step("Kiểm tra danh sách có sản phẩm"):
            expect(self._listing.count_text).to_have_text(
                re.compile(r"^Hiển thị [1-9]\d* trên [1-9]\d* sản phẩm$")
            )
            expect(self._listing.cards.first).to_be_visible()

    @keyword("verifyEmptyListing")
    def verify_empty_listing(self, text):
        """Kiểm tra trạng thái rỗng của trang danh sách (thông báo + "Hiển thị 0 trên 0 sản phẩm")."""
        with self.step(f'Kiểm tra danh sách rỗng: "{text}"'):
            expect(self._listing.empty_state(text)).to_be_visible()
            expect(self._listing.cards).to_have_count(0)
            expect(self._listing.count_text).to_have_text("Hiển thị 0 trên 0 sản phẩm")

    @keyword("goToPage")
    def go_to_page(self, n):
        """Bấm số trang ở phân trang."""
        with self.step(f"Chuyển tới trang {n}"):
            self._listing.page_button(n).click()

    @keyword("clickNextPage")
    def click_next_page(self):
        """Bấm nút trang sau (icon "navigate_next")."""
        with self.step("Bấm trang sau"):
            self._listing.next_page_button().click()

    @keyword("clickLoadMore")
    def click_load_more(self):
        """Bấm nút "Xem thêm sản phẩm"."""
        with self.step('Bấm "Xem thêm sản phẩm"'):
            self._listing.load_more_button.click()

    @keyword("addFirstCardToCart")
    def add_first_card_to_cart(self):
        """Rê chuột vào thẻ sản phẩm đầu tiên và bấm "Thêm vào giỏ" ở lớp phủ."""
        with self.step('Bấm "Thêm vào giỏ" trên thẻ đầu tiên'):
            card = self._first_card()
            card.hover()
            self._listing.card_add_to_cart(card).click()

    @keyword("viewFirstCardDetail")
    def view_first_card_detail(self):
        """Rê chuột vào thẻ sản phẩm đầu tiên và bấm "Xem chi tiết" ở lớp phủ."""
        with self.step('Bấm "Xem chi tiết" trên thẻ đầu tiên'):
            card = self._first_card()
            card.hover()
            self._listing.card_view_detail(card).click()

    @keyword("clickFirstCardFavorite")
    def click_first_card_favorite(self):
        """Bấm nút tim (yêu thích) trên thẻ sản phẩm đầu tiên."""
        with self.step("Bấm nút yêu thích trên thẻ đầu tiên"):
            card = self._first_card()
            card.hover()
            self._listing.card_favorite(card).click()

    @keyword("verifyOpenedLastCard")
    def verify_opened_last_card(self):
        """Kiểm tra đã chuyển tới trang chi tiết của thẻ sản phẩm vừa thao tác."""
        with self.step(f"Kiểm tra đã mở {self._last_card_href}"):
            assert re.match(r"^/product/.+", self._last_card_href), (
                f"href thẻ sản phẩm không hợp lệ: {self._last_card_href!r}"
            )
            expect(self.page).to_have_url(self._last_card_href)
            expect(self.po.product.title).to_be_visible()

    # ---------------------------------------------------------------------------
    # /search
    # ---------------------------------------------------------------------------

    @keyword("openSearchResults")
    def open_search_results(self, query):
        """Mở trang /search với query string (vd: "?category=vay", "" = tất cả) và chờ tải xong."""
        with self.step(f"Mở trang /search{query}"):
            self._results.open(query)
            expect(self._results.subtitle).not_to_have_text("Đang tải...")

    @keyword("verifySearchTitle")
    def verify_search_title(self, heading):
        """Kiểm tra tiêu đề h1 của trang /search."""
        with self.step(f'Kiểm tra tiêu đề "{heading}"'):
            expect(self._results.heading).to_have_text(heading)

    @keyword("verifySearchBreadcrumbs")
    def verify_search_breadcrumbs(self, items):
        """Kiểm tra breadcrumb trang /search theo thứ tự (bỏ icon)."""
        with self.step(f"Kiểm tra breadcrumb: {' > '.join(items)}"):
            expect(
                self._results.breadcrumb.locator(
                    ":scope > a, :scope > span:not(.material-symbols-outlined)"
                )
            ).to_have_text(items)

    @keyword("verifySearchBreadcrumbLink")
    def verify_search_breadcrumb_link(self, name, href):
        """Kiểm tra 1 mục breadcrumb là link trỏ đúng đường dẫn."""
        with self.step(f'Kiểm tra breadcrumb "{name}" -> {href}'):
            expect(self._results.breadcrumb_link(name)).to_have_attribute("href", href)

    @keyword("verifySearchSubtitleMatches")
    def verify_search_subtitle_matches(self):
        """Kiểm tra dòng "{tổng} sản phẩm" và số thẻ trên trang (tối đa 12/trang)."""
        with self.step('Kiểm tra "{tổng} sản phẩm" khớp danh sách'):
            expect(self._results.subtitle).to_have_text(re.compile(r"^\d+ sản phẩm$"))
            total = to_number(self._results.subtitle.text_content() or "")
            expect(self._results.cards).to_have_count(min(total, 12))

    @keyword("verifySearchChip")
    def verify_search_chip(self, text, close_href):
        """Kiểm tra chip bộ lọc đang áp dụng và link nút đóng (close)."""
        with self.step(f'Kiểm tra chip "{text}" (đóng -> {close_href})'):
            expect(self._results.chip(text)).to_be_visible()
            expect(self._results.chip_close(text)).to_have_attribute("href", close_href)

    @keyword("closeSearchChip")
    def close_search_chip(self, text):
        """Bấm nút đóng (close) trên 1 chip bộ lọc."""
        with self.step(f'Bỏ chip "{text}"'):
            self._results.chip_close(text).click()

    @keyword("verifySearchSortOptions")
    def verify_search_sort_options(self, options):
        """Kiểm tra các lựa chọn sắp xếp của trang /search."""
        with self.step(f"Kiểm tra sắp xếp /search: {' / '.join(options)}"):
            expect(self._results.sort_select.locator("option")).to_have_text(options)

    @keyword("sortSearchBy")
    def sort_search_by(self, option):
        """Chọn kiểu sắp xếp trên trang /search theo nhãn."""
        with self.step(f'Sắp xếp /search theo "{option}"'):
            self._results.sort_select.select_option(label=option)

    @keyword("verifySearchPricesSorted")
    def verify_search_prices_sorted(self, order):
        """Kiểm tra giá trên trang /search đã sắp xếp ("asc"/"desc")."""
        with self.step(f"Kiểm tra giá /search {'tăng' if order == 'asc' else 'giảm'} dần"):
            self._expect_sorted(
                lambda: self._read_prices(self._results.cards, self._results.card_price), order
            )

    @keyword("verifySearchEmpty")
    def verify_search_empty(self, hint):
        """Kiểm tra trạng thái rỗng của /search: tiêu đề, gợi ý và nút "Xem tất cả sản phẩm"."""
        with self.step(f'Kiểm tra /search rỗng: "{hint}"'):
            expect(self._results.empty_heading).to_be_visible()
            expect(self._results.empty_hint(hint)).to_be_visible()
            expect(self._results.subtitle).to_have_text("0 sản phẩm")
            expect(self._results.view_all_link).to_have_attribute("href", "/search")
            expect(self._results.sort_select).to_have_count(0)

    @keyword("clickViewAllProducts")
    def click_view_all_products(self):
        """Bấm "Xem tất cả sản phẩm" ở trạng thái rỗng."""
        with self.step('Bấm "Xem tất cả sản phẩm"'):
            self._results.view_all_link.click()

    @keyword("verifySearchError")
    def verify_search_error(self, message):
        """Kiểm tra trạng thái lỗi của /search: "Đã xảy ra lỗi" + thông báo + nút "Thử lại"."""
        with self.step(f'Kiểm tra /search báo lỗi "{message}"'):
            expect(self._results.error_heading).to_be_visible()
            expect(self._results.empty_hint(message)).to_be_visible()
            expect(self._results.retry_button).to_be_visible()

    @keyword("goToSearchPage")
    def go_to_search_page(self, n):
        """Bấm số trang trên phân trang của /search."""
        with self.step(f"/search: chuyển tới trang {n}"):
            self._results.page_button(n).click()

    @keyword("clickSearchNextPage")
    def click_search_next_page(self):
        """Bấm nút trang sau (chevron_right) trên /search."""
        with self.step("/search: bấm trang sau"):
            self._results.next_page_button().click()

    @keyword("verifySearchActivePage")
    def verify_search_active_page(self, n):
        """Kiểm tra trang hiện tại trên phân trang /search (nút được tô đỏ) và nút trang trước bật/tắt."""
        with self.step(f"/search: kiểm tra đang ở trang {n}"):
            expect(self._results.page_button(n)).to_have_class(re.compile(r"bg-\[#DA291C\]"))
            if n == 1:
                expect(self._results.prev_page_button()).to_be_disabled()
            else:
                expect(self._results.prev_page_button()).to_be_enabled()

    @keyword("typeHeaderSearchExpectingStatus")
    def type_header_search_expecting_status(self, keyword_text, status):
        """Gõ từ khóa vào ô tìm kiếm header và chờ API gợi ý (/api/products/search) trả về đúng status."""
        with self.step(f'Gõ "{keyword_text}" ở header, API gợi ý trả {status}'):
            with self.page.expect_response(lambda r: "/api/products/search" in r.url) as info:
                self.po.header.type_search(keyword_text)
            actual = info.value.status
            assert actual == status, f"Status API gợi ý: expected={status}, actual={actual}"

    @keyword("verifyHeaderSuggestionsHidden")
    def verify_header_suggestions_hidden(self):
        """Kiểm tra dropdown gợi ý tìm kiếm trên header KHÔNG hiển thị."""
        with self.step("Kiểm tra không hiện dropdown gợi ý"):
            expect(self.po.header.search_see_more).to_have_count(0)
            expect(self.po.header.search_no_result).to_have_count(0)

    # ---------------------------------------------------------------------------
    # Nội bộ
    # ---------------------------------------------------------------------------

    def _wait_listing_settled(self):
        expect(self._listing.count_text).to_be_visible()
        expect(self._listing.spinner).to_have_count(0)
        expect(
            self._listing.cards.first.or_(self.page.locator("main").get_by_text(EMPTY_LISTING))
        ).to_be_visible()

    def _first_card(self):
        self._wait_listing_settled()
        card = self._listing.cards.first
        self._last_card_href = self._listing.card_link(card).get_attribute("href") or ""
        return card

    def _read_prices(self, cards, price):
        return [to_number(price(card).text_content() or "") for card in cards.all()]

    def _poll_empty(self, read, message, timeout=10_000):
        # Tương đương expect.poll(read).toEqual([]): báo kèm giá trị lần đọc cuối.
        last = {"value": None}

        def check():
            last["value"] = read()
            return last["value"] == []

        try:
            poll_until(check, message, timeout=timeout)
        except AssertionError:
            raise AssertionError(f"{message}: {last['value']!r} (sau {timeout}ms)") from None

    def _expect_sorted(self, read, order):
        last = {"value": None}

        def check():
            prices = read()
            if len(prices) < 2:
                last["value"] = f"chỉ có {len(prices)} giá"
                return False
            ordered = sorted(prices, reverse=order != "asc")
            last["value"] = "sorted" if prices == ordered else ", ".join(map(str, prices))
            return last["value"] == "sorted"

        try:
            poll_until(check, "", timeout=10_000)
        except AssertionError:
            raise AssertionError(f"Giá chưa sắp xếp {order}: {last['value']}") from None
