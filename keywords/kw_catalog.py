# THƯ VIỆN KEYWORD - NHÓM catalog: trang chủ, menu danh mục, chi tiết sản phẩm, tìm kiếm.
import re

from playwright.sync_api import expect

from keywords.base_keywords import BaseKeywords, keyword


class CatalogKeywords(BaseKeywords):
    group = "catalog"

    @keyword("openHome")
    def open_home(self):
        """Mở trang chủ và chờ danh sách sản phẩm."""
        with self.step("Mở trang chủ"):
            self.po.home.goto()
            expect(self.po.home.product_cards.first).to_be_visible()

    @keyword("verifyHomeLoaded")
    def verify_home_loaded(self):
        """Kiểm tra trang chủ: logo, ô tìm kiếm, khối SẢN PHẨM MỚI, footer."""
        with self.step("Kiểm tra trang chủ hiển thị đầy đủ"):
            home = self.po.home
            expect(home.header.logo).to_be_visible()
            expect(home.header.search_input).to_be_visible()
            expect(home.new_products_heading).to_be_visible()
            expect(home.footer).to_be_visible()

    @keyword("clickLogo")
    def click_logo(self):
        """Bấm logo trên header."""
        with self.step("Bấm logo"):
            self.po.header.logo.click()

    @keyword("verifyMenuLink")
    def verify_menu_link(self, nav, path):
        """Kiểm tra link danh mục trên menu trỏ đúng đường dẫn."""
        with self.step(f'Kiểm tra menu "{nav}" -> {path}'):
            expect(self.po.header.nav_link(nav)).to_have_attribute("href", path)

    @keyword("openCategoryFromMenu")
    def open_category_from_menu(self, nav):
        """Bấm 1 danh mục trên menu header, vd: "NAM"."""
        with self.step(f'Mở danh mục "{nav}" từ menu'):
            self.po.header.nav_link(nav).click()

    @keyword("openCategoryFromMobileMenu")
    def open_category_from_mobile_menu(self, nav):
        """Mở menu mobile (hamburger) và bấm 1 danh mục."""
        with self.step(f'Mở danh mục "{nav}" từ menu mobile'):
            self.po.header.mobile_menu_toggle.click()
            self.po.header.mobile_nav_link(nav).click()

    @keyword("verifyCategoryPage")
    def verify_category_page(self, path, heading):
        """Kiểm tra đang ở trang danh mục (URL + tiêu đề) và có sản phẩm hoặc thông báo rỗng."""
        with self.step(f'Kiểm tra trang danh mục {path} "{heading}"'):
            category = self.po.category(path)
            expect(self.page).to_have_url(path)
            expect(category.heading).to_have_text(heading)
            expect(category.product_links.first.or_(category.empty_state)).to_be_visible()

    @keyword("openFirstProductInList")
    def open_first_product_in_list(self):
        """Bấm sản phẩm đầu tiên trong danh sách đang hiển thị và chờ trang chi tiết."""
        with self.step("Mở sản phẩm đầu tiên trong danh sách"):
            self.page.locator('a[href^="/product/"]').filter(visible=True).first.click()
            expect(self.page).to_have_url(re.compile(r"/product/.+"))
            expect(self.po.product.title).to_be_visible()

    @keyword("openProduct")
    def open_product(self, slug):
        """Mở trang chi tiết sản phẩm theo slug."""
        with self.step(f'Mở sản phẩm "{slug}"'):
            self.po.product.open(slug)

    @keyword("verifyProductTitle")
    def verify_product_title(self, name):
        """Kiểm tra tên sản phẩm trên trang chi tiết."""
        with self.step(f'Kiểm tra tên sản phẩm "{name}"'):
            expect(self.po.product.title).to_have_text(name)

    @keyword("verifySizeCount")
    def verify_size_count(self, count):
        """Kiểm tra số nút size trên trang chi tiết."""
        with self.step(f"Kiểm tra có {count} size"):
            expect(self.po.product.size_buttons).to_have_count(count)

    @keyword("selectSize")
    def select_size(self, label=None):
        """Chọn size (để trống = size còn hàng đầu tiên)."""
        with self.step(f"Chọn size {label if label is not None else '(đầu tiên còn hàng)'}"):
            self.po.product.select_size(label)

    @keyword("verifySizeWarning")
    def verify_size_warning(self, visible):
        """Kiểm tra cảnh báo "Vui lòng chọn kích cỡ" hiện/ẩn."""
        with self.step(f"Kiểm tra cảnh báo chọn size {'hiện' if visible else 'ẩn'}"):
            warning = self.po.product.size_warning
            if visible:
                expect(warning).to_be_visible()
            else:
                expect(warning).to_be_hidden()

    @keyword("addToCart")
    def add_to_cart(self, size=None):
        """Chọn size (nếu có) rồi bấm "Thêm vào giỏ hàng"."""
        with self.step(f"Thêm vào giỏ hàng{f' (size {size})' if size else ''}"):
            if size:
                self.po.product.select_size(size)
            self.po.product.add_to_cart_button.click()

    @keyword("verifyProductNotFound")
    def verify_product_not_found(self):
        """Kiểm tra trang "Không tìm thấy sản phẩm"."""
        with self.step('Kiểm tra hiển thị "Không tìm thấy sản phẩm"'):
            expect(self.po.product.not_found).to_be_visible()

    @keyword("typeSearch")
    def type_search(self, keyword_text):
        """Gõ từ khóa vào ô tìm kiếm trên header (chưa Enter)."""
        with self.step(f'Gõ tìm kiếm "{keyword_text}"'):
            self.po.header.type_search(keyword_text)

    @keyword("verifySearchSuggestion")
    def verify_search_suggestion(self, name):
        """Kiểm tra dropdown gợi ý có sản phẩm."""
        with self.step(f'Kiểm tra gợi ý có "{name}"'):
            expect(self.po.header.search_result(name).first).to_be_visible()
            expect(self.po.header.search_see_more).to_be_visible()

    @keyword("clickSearchSuggestion")
    def click_search_suggestion(self, name):
        """Bấm 1 sản phẩm trong dropdown gợi ý."""
        with self.step(f'Bấm gợi ý "{name}"'):
            self.po.header.search_result(name).first.click()

    @keyword("verifyNoSearchSuggestion")
    def verify_no_search_suggestion(self):
        """Kiểm tra dropdown báo không có kết quả."""
        with self.step("Kiểm tra gợi ý báo không có kết quả"):
            expect(self.po.header.search_no_result).to_be_visible()

    @keyword("submitSearch")
    def submit_search(self, keyword_text):
        """Gõ từ khóa vào ô tìm kiếm và nhấn Enter."""
        with self.step(f'Tìm kiếm "{keyword_text}" + Enter'):
            self.po.header.submit_search(keyword_text)

    @keyword("openSearchPage")
    def open_search_page(self, keyword_text):
        """Mở thẳng trang kết quả /search?q=..."""
        with self.step(f'Mở trang tìm kiếm "{keyword_text}"'):
            self.po.search.search(keyword_text)

    @keyword("verifySearchResults")
    def verify_search_results(self, heading):
        """Kiểm tra trang kết quả tìm kiếm có tiêu đề và ít nhất 1 sản phẩm."""
        with self.step(f'Kiểm tra trang kết quả "{heading}"'):
            expect(self.page).to_have_url(re.compile(r"/search\?q="))
            expect(self.po.search.heading).to_have_text(heading)
            expect(self.po.search.product_links.first).to_be_visible()

    @keyword("verifyNoSearchResults")
    def verify_no_search_results(self):
        """Kiểm tra trang kết quả tìm kiếm rỗng."""
        with self.step("Kiểm tra trang kết quả rỗng"):
            expect(self.po.search.no_result).to_be_visible()
