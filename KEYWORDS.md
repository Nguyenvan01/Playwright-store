# Danh mục Keyword

> File tự sinh bởi `.venv/bin/python scripts/gen_keywords_doc.py` — đừng sửa tay.

Dùng trong code (pytest): `k.<nhóm>.<keyword_snake_case>(...)`, vd: `k.cart.verify_cart_badge(2)` · Dùng trong kịch bản Excel: cột `keyword` = `<nhóm>.<keywordCamelCase>`, vd: `cart.verifyCartBadge`.

Kịch bản nằm trong `data/scenarios/*.xlsx`, mỗi file có 2 sheet:

- `TestSteps`: `template_id | step | keyword | args | note` — `args` là mảng JSON, vd: `[2]`, `["${product.name}", "M"]`.
- `TestData`: `case_id | template_id | title | tags | requires | known_bug | <cột placeholder>` — mỗi dòng là 1 test case, giá trị cột placeholder thay vào placeholder `{tên_cột}` trong `args` lúc collection; `${...}` là biến runtime.

## common

| Keyword | Python | Tham số | Mô tả |
|---|---|---|---|
| `common.goto` | `k.common.goto(path)` | `path` | Mở 1 đường dẫn bất kỳ, vd: "/about". |
| `common.reload` | `k.common.reload()` | — | Tải lại trang hiện tại. |
| `common.verifyUrl` | `k.common.verify_url(path)` | `path` | Kiểm tra URL hiện tại đúng đường dẫn, vd: "/profile". |
| `common.verifyUrlMatches` | `k.common.verify_url_matches(pattern)` | `pattern` | Kiểm tra URL khớp biểu thức chính quy, vd: "/product/.+". |
| `common.verifyToast` | `k.common.verify_toast(text)` | `text` | Kiểm tra có toast chứa nội dung. |
| `common.verifyTextVisible` | `k.common.verify_text_visible(text)` | `text` | Kiểm tra 1 đoạn chữ đang hiển thị trên trang. |
| `common.verifyLayoutLoaded` | `k.common.verify_layout_loaded()` | — | Kiểm tra trang có header và footer (trang khách hàng tải thành công). |
| `common.verifyNoPageErrors` | `k.common.verify_no_page_errors()` | — | Kiểm tra không phát sinh lỗi JavaScript nào kể từ đầu test. |
| `common.verifyNoHorizontalOverflow` | `k.common.verify_no_horizontal_overflow()` | — | Kiểm tra trang không bị tràn ngang (responsive). |
| `common.mockApi` | `k.common.mock_api(url_pattern, response)` | `url_pattern, response` | Giả lập 1 API theo mẫu URL (glob của Playwright), trả về status + json. |
| `common.mockWrite` | `k.common.mock_write(method, url_pattern, json_body, status)` | `method, url_pattern, json_body=None, status=200` | Giả lập API ghi (POST/PUT/DELETE) theo mẫu URL, trả về json; lưu lại request để kiểm tra. |
| `common.verifyRequest` | `k.common.verify_request(method, path_part, expected_body)` | `method, path_part, expected_body=None` | Kiểm tra đã gửi request (method + đường dẫn chứa pathPart), body chứa các trường mong đợi. |
| `common.mockGet` | `k.common.mock_get(url_pattern, json_body, status)` | `url_pattern, json_body, status=200` | Giả lập API GET (dữ liệu mẫu cho trang cần data, vd: danh sách đơn hàng). Chỉ chặn method GET. |
| `common.acceptNextDialog` | `k.common.accept_next_dialog(accept)` | `accept=True` | Tự động bấm OK (true) hoặc Hủy (false) cho hộp thoại window.confirm/alert tiếp theo. |
| `common.verifyNoRequest` | `k.common.verify_no_request(method, path_part)` | `method, path_part` | Kiểm tra KHÔNG có request ghi nào (method + đường dẫn) được gửi. |

## auth

| Keyword | Python | Tham số | Mô tả |
|---|---|---|---|
| `auth.openLogin` | `k.auth.open_login()` | — | Mở trang đăng nhập khách hàng. |
| `auth.login` | `k.auth.login(identifier, password)` | `identifier, password` | Nhập email/SĐT + mật khẩu và bấm ĐĂNG NHẬP. |
| `auth.loginAsCustomer` | `k.auth.login_as_customer()` | — | Đăng nhập bằng tài khoản khách hàng test trong .env và chờ vào trang hồ sơ. |
| `auth.restoreSession` | `k.auth.restore_session(role)` | `role` | Đăng nhập sẵn qua API (không qua UI) - phải gọi TRƯỚC lần mở trang đầu tiên. |
| `auth.openRegisterForm` | `k.auth.open_register_form()` | — | Chuyển form sang chế độ Đăng ký. |
| `auth.submitRegisterForm` | `k.auth.submit_register_form(form)` | `form` | Điền form đăng ký và bấm TẠO TÀI KHOẢN (form phải đang mở). |
| `auth.verifyFieldErrors` | `k.auth.verify_field_errors(messages)` | `messages` | Kiểm tra các thông báo lỗi dưới từng ô nhập. |
| `auth.verifyGeneralError` | `k.auth.verify_general_error(message)` | `message` | Kiểm tra thông báo lỗi chung (lỗi từ server) trên form đăng nhập/đăng ký. |
| `auth.loginExpectingError` | `k.auth.login_expecting_error(identifier, password, message)` | `identifier, password, message` | Đăng nhập sai và kiểm tra thông báo lỗi vẫn hiển thị (trang không bị reload). |
| `auth.mockLoginSuccess` | `k.auth.mock_login_success(user)` | `user` | Giả lập API đăng nhập thành công với user cho trước (kèm các API trang hồ sơ). |
| `auth.mockRegisterError` | `k.auth.mock_register_error(status, message)` | `status, message` | Giả lập API đăng ký trả lỗi (status + message). |
| `auth.togglePassword` | `k.auth.toggle_password(expect_visible)` | `expect_visible` | Bấm nút hiện/ẩn mật khẩu và kiểm tra trạng thái hiển thị. |
| `auth.verifyLoggedInAs` | `k.auth.verify_logged_in_as(email)` | `email` | Kiểm tra menu tài khoản trên header hiển thị đúng email. |
| `auth.logout` | `k.auth.logout()` | — | Đăng xuất qua menu tài khoản trên header. |
| `auth.verifyLoggedOut` | `k.auth.verify_logged_out()` | — | Kiểm tra đã đăng xuất: về trang chủ, có link đăng nhập, token bị xóa. |
| `auth.verifyStoredToken` | `k.auth.verify_stored_token(expected)` | `expected` | Kiểm tra token khách hàng trong localStorage bằng giá trị mong đợi. |

## catalog

| Keyword | Python | Tham số | Mô tả |
|---|---|---|---|
| `catalog.openHome` | `k.catalog.open_home()` | — | Mở trang chủ và chờ danh sách sản phẩm. |
| `catalog.verifyHomeLoaded` | `k.catalog.verify_home_loaded()` | — | Kiểm tra trang chủ: logo, ô tìm kiếm, khối SẢN PHẨM MỚI, footer. |
| `catalog.clickLogo` | `k.catalog.click_logo()` | — | Bấm logo trên header. |
| `catalog.verifyMenuLink` | `k.catalog.verify_menu_link(nav, path)` | `nav, path` | Kiểm tra link danh mục trên menu trỏ đúng đường dẫn. |
| `catalog.openCategoryFromMenu` | `k.catalog.open_category_from_menu(nav)` | `nav` | Bấm 1 danh mục trên menu header, vd: "NAM". |
| `catalog.openCategoryFromMobileMenu` | `k.catalog.open_category_from_mobile_menu(nav)` | `nav` | Mở menu mobile (hamburger) và bấm 1 danh mục. |
| `catalog.verifyCategoryPage` | `k.catalog.verify_category_page(path, heading)` | `path, heading` | Kiểm tra đang ở trang danh mục (URL + tiêu đề) và có sản phẩm hoặc thông báo rỗng. |
| `catalog.openFirstProductInList` | `k.catalog.open_first_product_in_list()` | — | Bấm sản phẩm đầu tiên trong danh sách đang hiển thị và chờ trang chi tiết. |
| `catalog.openProduct` | `k.catalog.open_product(slug)` | `slug` | Mở trang chi tiết sản phẩm theo slug. |
| `catalog.verifyProductTitle` | `k.catalog.verify_product_title(name)` | `name` | Kiểm tra tên sản phẩm trên trang chi tiết. |
| `catalog.verifySizeCount` | `k.catalog.verify_size_count(count)` | `count` | Kiểm tra số nút size trên trang chi tiết. |
| `catalog.selectSize` | `k.catalog.select_size(label)` | `label=None` | Chọn size (để trống = size còn hàng đầu tiên). |
| `catalog.verifySizeWarning` | `k.catalog.verify_size_warning(visible)` | `visible` | Kiểm tra cảnh báo "Vui lòng chọn kích cỡ" hiện/ẩn. |
| `catalog.addToCart` | `k.catalog.add_to_cart(size)` | `size=None` | Chọn size (nếu có) rồi bấm "Thêm vào giỏ hàng". |
| `catalog.verifyProductNotFound` | `k.catalog.verify_product_not_found()` | — | Kiểm tra trang "Không tìm thấy sản phẩm". |
| `catalog.typeSearch` | `k.catalog.type_search(keyword_text)` | `keyword_text` | Gõ từ khóa vào ô tìm kiếm trên header (chưa Enter). |
| `catalog.verifySearchSuggestion` | `k.catalog.verify_search_suggestion(name)` | `name` | Kiểm tra dropdown gợi ý có sản phẩm. |
| `catalog.clickSearchSuggestion` | `k.catalog.click_search_suggestion(name)` | `name` | Bấm 1 sản phẩm trong dropdown gợi ý. |
| `catalog.verifyNoSearchSuggestion` | `k.catalog.verify_no_search_suggestion()` | — | Kiểm tra dropdown báo không có kết quả. |
| `catalog.submitSearch` | `k.catalog.submit_search(keyword_text)` | `keyword_text` | Gõ từ khóa vào ô tìm kiếm và nhấn Enter. |
| `catalog.openSearchPage` | `k.catalog.open_search_page(keyword_text)` | `keyword_text` | Mở thẳng trang kết quả /search?q=... |
| `catalog.verifySearchResults` | `k.catalog.verify_search_results(heading)` | `heading` | Kiểm tra trang kết quả tìm kiếm có tiêu đề và ít nhất 1 sản phẩm. |
| `catalog.verifyNoSearchResults` | `k.catalog.verify_no_search_results()` | — | Kiểm tra trang kết quả tìm kiếm rỗng. |

## listing

| Keyword | Python | Tham số | Mô tả |
|---|---|---|---|
| `listing.openListing` | `k.listing.open_listing(path)` | `path` | Mở trang danh sách (vd: "/nam") và chờ tải xong (có sản phẩm hoặc thông báo rỗng). |
| `listing.verifyListingHeader` | `k.listing.verify_listing_header(heading, breadcrumb, description)` | `heading, breadcrumb, description` | Kiểm tra đầu trang danh sách: breadcrumb "Trang chủ > {mục}", tiêu đề h1, đoạn mô tả. |
| `listing.verifyCountMatchesCards` | `k.listing.verify_count_matches_cards()` | — | Kiểm tra dòng "Hiển thị n trên t sản phẩm": n = số thẻ đang hiển thị và n <= t. |
| `listing.verifyCountText` | `k.listing.verify_count_text(text)` | `text` | Kiểm tra chính xác dòng "Hiển thị n trên t sản phẩm". |
| `listing.verifySortOptions` | `k.listing.verify_sort_options(options, selected)` | `options, selected` | Kiểm tra các lựa chọn sắp xếp (theo thứ tự) và lựa chọn đang được chọn. |
| `listing.sortBy` | `k.listing.sort_by(option)` | `option` | Chọn kiểu sắp xếp theo nhãn, vd: "Giá: Thấp → Cao". |
| `listing.verifyPricesSorted` | `k.listing.verify_prices_sorted(order)` | `order` | Kiểm tra giá trên các thẻ sản phẩm đã sắp xếp: "asc" tăng dần, "desc" giảm dần. |
| `listing.verifyCategoryOptions` | `k.listing.verify_category_options(names)` | `names` | Kiểm tra các nút danh mục đang hiển thị trong bộ lọc (theo thứ tự). |
| `listing.showMoreCategories` | `k.listing.show_more_categories()` | — | Bấm "Xem thêm +" trong nhóm danh mục để hiện các danh mục còn lại. |
| `listing.selectCategory` | `k.listing.select_category(name)` | `name` | Bấm 1 danh mục trong bộ lọc và kiểm tra nút được đánh dấu chọn. |
| `listing.verifySizeOptions` | `k.listing.verify_size_options(sizes)` | `sizes` | Kiểm tra các nút size trong bộ lọc "Kích cỡ". |
| `listing.selectSizeFilter` | `k.listing.select_size_filter(size)` | `size` | Bấm 1 size trong bộ lọc "Kích cỡ". |
| `listing.verifyColorOptions` | `k.listing.verify_color_options(colors)` | `colors` | Kiểm tra các ô màu trong bộ lọc "Màu sắc" (theo thuộc tính title). |
| `listing.selectColorFilter` | `k.listing.select_color_filter(color)` | `color` | Bấm 1 màu trong bộ lọc "Màu sắc" (theo title) và kiểm tra có dấu tích. |
| `listing.verifyPriceInputs` | `k.listing.verify_price_inputs(from_value, to_value)` | `from_value, to_value` | Kiểm tra giá trị mặc định 2 ô khoảng giá "Từ" / "Đến". |
| `listing.setPriceRange` | `k.listing.set_price_range(from_value, to_value)` | `from_value, to_value` | Nhập khoảng giá "Từ" - "Đến" (vd: "300000", "600000"); bộ lọc áp dụng khi rời ô nhập. |
| `listing.verifyPricesWithin` | `k.listing.verify_prices_within(min_price, max_price)` | `min_price, max_price` | Kiểm tra mọi giá đang hiển thị nằm trong khoảng [min, max]. |
| `listing.selectDiscount` | `k.listing.select_discount(label)` | `label` | Tick 1 mức "Phần trăm giảm" (tự mở nhóm lọc nếu đang đóng), vd: "Giảm 30%". |
| `listing.verifyDiscountAtLeast` | `k.listing.verify_discount_at_least(percent)` | `percent` | Kiểm tra mọi thẻ đang hiển thị có nhãn giảm giá >= phần trăm cho trước. |
| `listing.verifyListRequest` | `k.listing.verify_list_request(params)` | `params` | Kiểm tra đã gọi API danh sách sản phẩm với các tham số query, vd: {"min_price":"300000"}. |
| `listing.verifyProductsShown` | `k.listing.verify_products_shown()` | — | Kiểm tra danh sách có ít nhất 1 sản phẩm và dòng "Hiển thị n trên t" với n > 0. |
| `listing.verifyEmptyListing` | `k.listing.verify_empty_listing(text)` | `text` | Kiểm tra trạng thái rỗng của trang danh sách (thông báo + "Hiển thị 0 trên 0 sản phẩm"). |
| `listing.goToPage` | `k.listing.go_to_page(n)` | `n` | Bấm số trang ở phân trang. |
| `listing.clickNextPage` | `k.listing.click_next_page()` | — | Bấm nút trang sau (icon "navigate_next"). |
| `listing.clickLoadMore` | `k.listing.click_load_more()` | — | Bấm nút "Xem thêm sản phẩm". |
| `listing.addFirstCardToCart` | `k.listing.add_first_card_to_cart()` | — | Rê chuột vào thẻ sản phẩm đầu tiên và bấm "Thêm vào giỏ" ở lớp phủ. |
| `listing.viewFirstCardDetail` | `k.listing.view_first_card_detail()` | — | Rê chuột vào thẻ sản phẩm đầu tiên và bấm "Xem chi tiết" ở lớp phủ. |
| `listing.clickFirstCardFavorite` | `k.listing.click_first_card_favorite()` | — | Bấm nút tim (yêu thích) trên thẻ sản phẩm đầu tiên. |
| `listing.verifyOpenedLastCard` | `k.listing.verify_opened_last_card()` | — | Kiểm tra đã chuyển tới trang chi tiết của thẻ sản phẩm vừa thao tác. |
| `listing.openSearchResults` | `k.listing.open_search_results(query)` | `query` | Mở trang /search với query string (vd: "?category=vay", "" = tất cả) và chờ tải xong. |
| `listing.verifySearchTitle` | `k.listing.verify_search_title(heading)` | `heading` | Kiểm tra tiêu đề h1 của trang /search. |
| `listing.verifySearchBreadcrumbs` | `k.listing.verify_search_breadcrumbs(items)` | `items` | Kiểm tra breadcrumb trang /search theo thứ tự (bỏ icon). |
| `listing.verifySearchBreadcrumbLink` | `k.listing.verify_search_breadcrumb_link(name, href)` | `name, href` | Kiểm tra 1 mục breadcrumb là link trỏ đúng đường dẫn. |
| `listing.verifySearchSubtitleMatches` | `k.listing.verify_search_subtitle_matches()` | — | Kiểm tra dòng "{tổng} sản phẩm" và số thẻ trên trang (tối đa 12/trang). |
| `listing.verifySearchChip` | `k.listing.verify_search_chip(text, close_href)` | `text, close_href` | Kiểm tra chip bộ lọc đang áp dụng và link nút đóng (close). |
| `listing.closeSearchChip` | `k.listing.close_search_chip(text)` | `text` | Bấm nút đóng (close) trên 1 chip bộ lọc. |
| `listing.verifySearchSortOptions` | `k.listing.verify_search_sort_options(options)` | `options` | Kiểm tra các lựa chọn sắp xếp của trang /search. |
| `listing.sortSearchBy` | `k.listing.sort_search_by(option)` | `option` | Chọn kiểu sắp xếp trên trang /search theo nhãn. |
| `listing.verifySearchPricesSorted` | `k.listing.verify_search_prices_sorted(order)` | `order` | Kiểm tra giá trên trang /search đã sắp xếp ("asc"/"desc"). |
| `listing.verifySearchEmpty` | `k.listing.verify_search_empty(hint)` | `hint` | Kiểm tra trạng thái rỗng của /search: tiêu đề, gợi ý và nút "Xem tất cả sản phẩm". |
| `listing.clickViewAllProducts` | `k.listing.click_view_all_products()` | — | Bấm "Xem tất cả sản phẩm" ở trạng thái rỗng. |
| `listing.verifySearchError` | `k.listing.verify_search_error(message)` | `message` | Kiểm tra trạng thái lỗi của /search: "Đã xảy ra lỗi" + thông báo + nút "Thử lại". |
| `listing.goToSearchPage` | `k.listing.go_to_search_page(n)` | `n` | Bấm số trang trên phân trang của /search. |
| `listing.clickSearchNextPage` | `k.listing.click_search_next_page()` | — | Bấm nút trang sau (chevron_right) trên /search. |
| `listing.verifySearchActivePage` | `k.listing.verify_search_active_page(n)` | `n` | Kiểm tra trang hiện tại trên phân trang /search (nút được tô đỏ) và nút trang trước bật/tắt. |
| `listing.typeHeaderSearchExpectingStatus` | `k.listing.type_header_search_expecting_status(keyword_text, status)` | `keyword_text, status` | Gõ từ khóa vào ô tìm kiếm header và chờ API gợi ý (/api/products/search) trả về đúng status. |
| `listing.verifyHeaderSuggestionsHidden` | `k.listing.verify_header_suggestions_hidden()` | — | Kiểm tra dropdown gợi ý tìm kiếm trên header KHÔNG hiển thị. |

## product

| Keyword | Python | Tham số | Mô tả |
|---|---|---|---|
| `product.mockProductDetail` | `k.product.mock_product_detail(slug, response)` | `slug, response` | Mock GET /api/products/{slug} bằng dữ liệu cho trước (shape { success, data }). |
| `product.openProductPage` | `k.product.open_product_page(slug)` | `slug` | Mở trang chi tiết /product/{slug} và chờ tên sản phẩm hiển thị. |
| `product.verifyBreadcrumb` | `k.product.verify_breadcrumb(title)` | `title` | Kiểm tra breadcrumb "Trang chủ \| {tên sản phẩm}". |
| `product.clickBreadcrumbHome` | `k.product.click_breadcrumb_home()` | — | Bấm "Trang chủ" trên breadcrumb. |
| `product.verifyGallery` | `k.product.verify_gallery(count)` | `count` | Kiểm tra bộ ảnh: số thumbnail ("Thumbnail 1..n") và bộ đếm "1/n". |
| `product.clickThumbnail` | `k.product.click_thumbnail(n)` | `n` | Bấm thumbnail thứ n (đánh số từ 1). |
| `product.clickNextImage` | `k.product.click_next_image()` | — | Bấm nút mũi tên chuyển ảnh tiếp theo trên ảnh chính. |
| `product.verifyCurrentImage` | `k.product.verify_current_image(n, total)` | `n, total` | Kiểm tra ảnh chính đang là ảnh thứ n: bộ đếm "n/tổng", thumbnail n được viền, cùng nguồn ảnh. |
| `product.verifyNextImageHidden` | `k.product.verify_next_image_hidden()` | — | Kiểm tra nút ảnh tiếp theo bị ẩn (đang ở ảnh cuối). |
| `product.verifyColorOptions` | `k.product.verify_color_options(colors)` | `colors` | Kiểm tra các ô màu (theo title) và màu đang chọn mặc định (màu đầu tiên). |
| `product.selectColor` | `k.product.select_color(color)` | `color` | Chọn 1 màu (theo title) và kiểm tra tên màu hiển thị cạnh "Màu sắc:". |
| `product.verifySku` | `k.product.verify_sku(sku)` | `sku` | Kiểm tra dòng "SKU: ..." và nút "Copy". |
| `product.copySku` | `k.product.copy_sku()` | — | Bấm "Copy" mã SKU. |
| `product.verifySkuCopied` | `k.product.verify_sku_copied(sku)` | `sku` | Kiểm tra đã copy SKU: nút đổi thành "Đã copy", clipboard chứa SKU, sau 2 giây trở lại "Copy". |
| `product.verifyPrice` | `k.product.verify_price(price)` | `price` | Kiểm tra giá bán hiển thị đúng định dạng, vd: "449.000đ". |
| `product.verifyComparePrice` | `k.product.verify_compare_price(compare_price, discount)` | `compare_price, discount` | Kiểm tra giá gốc gạch ngang và nhãn phần trăm giảm, vd: "599.000đ", "-25%". |
| `product.verifyDiscountBadge` | `k.product.verify_discount_badge(discount)` | `discount` | Kiểm tra nhãn phần trăm giảm cạnh giá, vd: "-25%". |
| `product.toggleAccordion` | `k.product.toggle_accordion(title)` | `title` | Bấm tiêu đề 1 accordion: "Mô tả" / "Chất liệu" / "Hướng dẫn sử dụng". |
| `product.verifyOpenAccordion` | `k.product.verify_open_accordion(title, all_titles)` | `title, all_titles` | Kiểm tra chỉ đúng 1 accordion đang mở (title), các accordion còn lại đóng; title rỗng = tất cả đóng. |
| `product.verifyAccordionContent` | `k.product.verify_accordion_content(title, lines)` | `title, lines` | Kiểm tra nội dung trong 1 accordion (các dòng/đoạn). |
| `product.verifyServices` | `k.product.verify_services(services)` | `services` | Kiểm tra danh sách dịch vụ dưới nút mua (tiêu đề + mô tả). |
| `product.verifyServiceText` | `k.product.verify_service_text(title, desc)` | `title, desc` | Kiểm tra mô tả của 1 dịch vụ, vd: "Miễn phí giao hàng" -> "Với đơn hàng trên 500.000đ.". |
| `product.verifyRelatedProduct` | `k.product.verify_related_product(name)` | `name` | Kiểm tra khối "SẢN PHẨM CÙNG PHONG CÁCH" có sản phẩm theo tên. |
| `product.openRelatedProduct` | `k.product.open_related_product(name)` | `name` | Bấm 1 sản phẩm trong "SẢN PHẨM CÙNG PHONG CÁCH". |
| `product.verifyReviewLoginPrompt` | `k.product.verify_review_login_prompt()` | — | Kiểm tra khách chưa đăng nhập: chỉ thấy lời nhắc đăng nhập để đánh giá. |
| `product.clickReviewLogin` | `k.product.click_review_login()` | — | Bấm "Đăng nhập" trong khối đánh giá. |
| `product.openReviewForm` | `k.product.open_review_form()` | — | Bấm "Viết đánh giá" và kiểm tra form hiện ra. |
| `product.fillReview` | `k.product.fill_review(stars, content)` | `stars, content` | Chọn số sao (0 = bỏ qua) và nhập nội dung đánh giá. |
| `product.submitReview` | `k.product.submit_review()` | — | Bấm "Gửi đánh giá". |
| `product.verifyReviewErrors` | `k.product.verify_review_errors(messages)` | `messages` | Kiểm tra các thông báo lỗi dưới form đánh giá (đúng và đủ). |
| `product.cancelReview` | `k.product.cancel_review()` | — | Bấm "Hủy" trên form đánh giá. |
| `product.closeReviewForm` | `k.product.close_review_form()` | — | Bấm nút "×" đóng form đánh giá. |
| `product.verifyReviewFormClosed` | `k.product.verify_review_form_closed()` | — | Kiểm tra form đánh giá đã đóng và nút "Viết đánh giá" hiện lại. |

## content

| Keyword | Python | Tham số | Mô tả |
|---|---|---|---|
| `content.mockHomeData` | `k.content.mock_home_data(response)` | `response` | Mock GET /api/home bằng dữ liệu cho trước (voucher có "expiresInDays" được đổi thành ngày hết hạn tính từ hôm nay). |
| `content.openHomePage` | `k.content.open_home_page()` | — | Mở trang chủ và chờ khối SẢN PHẨM MỚI hiển thị (không yêu cầu có sản phẩm). |
| `content.verifyHomeSections` | `k.content.verify_home_sections(titles)` | `titles` | Kiểm tra trang chủ có đủ các khối theo tiêu đề h2, đúng thứ tự. |
| `content.verifyBannerSlideCount` | `k.content.verify_banner_slide_count(count)` | `count` | Kiểm tra số slide banner và số chấm điều hướng. |
| `content.verifyActiveBannerSlide` | `k.content.verify_active_banner_slide(slide)` | `slide` | Kiểm tra slide banner đang hiển thị (đánh số từ 1). |
| `content.clickBannerArrow` | `k.content.click_banner_arrow(direction)` | `direction` | Bấm nút mũi tên banner: "next" hoặc "prev". |
| `content.clickBannerDot` | `k.content.click_banner_dot(slide)` | `slide` | Bấm chấm điều hướng banner thứ n (đánh số từ 1). |
| `content.freezeClock` | `k.content.freeze_clock()` | — | Cố định đồng hồ trình duyệt (banner không tự chuyển slide) - gọi TRƯỚC khi mở trang. |
| `content.verifyBannerAutoplay` | `k.content.verify_banner_autoplay(to_slide)` | `to_slide` | Cho đồng hồ (đã cố định bằng freezeClock) chạy 4 giây và kiểm tra banner tự chuyển sang slide kế tiếp. |
| `content.verifyBannerSlideLinks` | `k.content.verify_banner_slide_links(hrefs)` | `hrefs` | Kiểm tra link (href) của từng slide banner theo thứ tự. |
| `content.verifyBannerOverlay` | `k.content.verify_banner_overlay(slide, title, href)` | `slide, title, href` | Kiểm tra chữ đè trên slide banner (đánh số từ 1): tiêu đề + nút "Khám phá ngay" trỏ đúng link. |
| `content.verifyVoucher` | `k.content.verify_voucher(voucher)` | `voucher` | Kiểm tra 1 thẻ voucher trong khối "ƯU ĐÃI NỔI BẬT" (tiêu đề, mô tả, điều kiện, hạn dùng). |
| `content.useVoucher` | `k.content.use_voucher(title)` | `title` | Bấm "Dùng mã" của 1 voucher. |
| `content.verifyPendingVoucher` | `k.content.verify_pending_voucher(code)` | `code` | Kiểm tra mã voucher đã được lưu tạm vào sessionStorage (pendingVoucher). |
| `content.verifyNoVoucherSection` | `k.content.verify_no_voucher_section()` | — | Kiểm tra khối "ƯU ĐÃI NỔI BẬT" bị ẩn (không có voucher). |
| `content.verifyNewProductTabs` | `k.content.verify_new_product_tabs(tabs)` | `tabs` | Kiểm tra các tab của khối SẢN PHẨM MỚI, tab đầu đang được chọn. |
| `content.selectNewProductTab` | `k.content.select_new_product_tab(tab)` | `tab` | Bấm 1 tab trong khối SẢN PHẨM MỚI. |
| `content.verifyNewProductsFiltered` | `k.content.verify_new_products_filtered(tab, visible, hidden)` | `tab, visible, hidden` | Kiểm tra tab được chọn và danh sách SẢN PHẨM MỚI đã lọc: có sản phẩm visible, không còn sản phẩm hidden. |
| `content.verifyNewProductCount` | `k.content.verify_new_product_count(count)` | `count` | Kiểm tra số thẻ sản phẩm trong carousel SẢN PHẨM MỚI. |
| `content.scrollNewProducts` | `k.content.scroll_new_products(direction)` | `direction` | Bấm mũi tên carousel SẢN PHẨM MỚI ("next"/"prev") và kiểm tra danh sách cuộn đúng chiều. |
| `content.verifyPromoBlock` | `k.content.verify_promo_block(title, description, card_count)` | `title, description, card_count` | Kiểm tra khối HOMEWEAR/T-SHIRT/VÁY: mô tả và số thẻ sản phẩm (tối đa 4). |
| `content.verifyCollection` | `k.content.verify_collection(title, cta_text, href)` | `title, cta_text, href` | Kiểm tra 1 ô bộ sưu tập: tiêu đề, chữ trên nút CTA và link. |
| `content.verifyCLive` | `k.content.verify_c_live(texts)` | `texts` | Kiểm tra khối C-LIVE: tiêu đề, ảnh và các đoạn chữ. |
| `content.verifyHomeNews` | `k.content.verify_home_news(featured_title, secondary_count)` | `featured_title, secondary_count` | Kiểm tra khối "Tin tức thời trang": bài nổi bật + số bài phụ + nút "Xem thêm". |
| `content.verifyHomeNewsLink` | `k.content.verify_home_news_link(title, slug)` | `title, slug` | Kiểm tra link bài nổi bật trong khối Tin tức trỏ tới /blog/{slug}. |
| `content.verifyHomeNewsEmpty` | `k.content.verify_home_news_empty()` | — | Kiểm tra khối Tin tức hiển thị trạng thái rỗng và ẩn nút "Xem thêm". |
| `content.clickHomeNewsSeeMore` | `k.content.click_home_news_see_more()` | — | Bấm "Xem thêm" của khối Tin tức thời trang. |
| `content.clickHomeLink` | `k.content.click_home_link(link, section)` | `link, section=None` | Bấm 1 link trên trang chủ theo tên; section = tiêu đề khối chứa link (để trống = khối SẢN PHẨM MỚI). |
| `content.verifyPageRendered` | `k.content.verify_page_rendered()` | — | Kiểm tra trang đích đã render nội dung (có header, footer) - không phải trang trắng. |
| `content.quickAddToCart` | `k.content.quick_add_to_cart(product_name)` | `product_name` | Bấm icon thêm nhanh vào giỏ trên thẻ sản phẩm (ProductCard) theo tên. |
| `content.verifyStoredCartItemHasSize` | `k.content.verify_stored_cart_item_has_size(product_name)` | `product_name` | Kiểm tra sản phẩm trong giỏ (localStorage) đã có size được chọn. |
| `content.subscribeNewsletter` | `k.content.subscribe_newsletter(email)` | `email` | Nhập email vào khối "Đăng ký nhận tin" và bấm "Đăng ký". |
| `content.verifyNewsletterThanks` | `k.content.verify_newsletter_thanks()` | — | Kiểm tra hiện "Cảm ơn bạn đã đăng ký!" rồi form tự hiện lại sau khoảng 4 giây. |
| `content.verifyNewsletterBlocked` | `k.content.verify_newsletter_blocked(validity)` | `validity` | Kiểm tra trình duyệt chặn gửi form nhận tin (HTML5 validation), vd: "valueMissing", "typeMismatch". |
| `content.verifyFooterContent` | `k.content.verify_footer_content(headings, links)` | `headings, links` | Kiểm tra footer: các tiêu đề cột, link và dòng bản quyền. |
| `content.verifyFooterLink` | `k.content.verify_footer_link(name, href)` | `name, href` | Kiểm tra 1 link footer trỏ đúng đường dẫn. |
| `content.verifyFooterHasLinkTo` | `k.content.verify_footer_has_link_to(href)` | `href` | Kiểm tra footer có ít nhất 1 link trỏ tới đường dẫn. |
| `content.mockBlogData` | `k.content.mock_blog_data(response)` | `response` | Mock API blog: danh sách GET /api/news và chi tiết GET /api/news/:slug (404 nếu slug không có trong danh sách). |
| `content.openBlog` | `k.content.open_blog()` | — | Mở trang /blog và chờ danh sách bài viết tải xong. |
| `content.verifyBlogLoaded` | `k.content.verify_blog_loaded()` | — | Kiểm tra trang Blog: tiêu đề, mô tả và có ít nhất 1 bài viết. |
| `content.verifyBlogPills` | `k.content.verify_blog_pills(pills)` | `pills` | Kiểm tra các nút danh mục (pill) trên trang Blog theo thứ tự. |
| `content.filterBlogByCategory` | `k.content.filter_blog_by_category(category)` | `category` | Bấm 1 danh mục (pill) trên trang Blog. |
| `content.verifyBlogTitles` | `k.content.verify_blog_titles(titles)` | `titles` | Kiểm tra danh sách bài viết đang hiển thị đúng các tiêu đề (theo thứ tự). |
| `content.verifyBlogCategoryOfCards` | `k.content.verify_blog_category_of_cards(category)` | `category` | Kiểm tra mọi bài viết đang hiển thị đều thuộc danh mục. |
| `content.verifyBlogEmpty` | `k.content.verify_blog_empty()` | — | Kiểm tra trang Blog báo không có bài viết. |
| `content.openBlogArticle` | `k.content.open_blog_article(title)` | `title` | Bấm 1 bài viết trên trang Blog theo tiêu đề. |
| `content.openBlogArticleBySlug` | `k.content.open_blog_article_by_slug(slug)` | `slug` | Mở thẳng trang chi tiết bài viết /blog/{slug}. |
| `content.verifyBlogArticle` | `k.content.verify_blog_article(c)` | `c` | Kiểm tra trang chi tiết bài viết: URL, tiêu đề, danh mục, tác giả, lượt xem, tag, bài liên quan. |
| `content.clickBackToBlog` | `k.content.click_back_to_blog()` | — | Bấm "Quay lại Blog" trên trang chi tiết bài viết. |
| `content.openRelatedArticle` | `k.content.open_related_article(title)` | `title` | Bấm 1 bài trong "Bài viết liên quan". |
| `content.subscribeBlogNewsletterWithoutReload` | `k.content.subscribe_blog_newsletter_without_reload(email)` | `email` | Đăng ký nhận tin ở trang Blog và kiểm tra trang KHÔNG bị tải lại (form phải được xử lý bằng JS). |
| `content.verifyPageHeadings` | `k.content.verify_page_headings(h1, h2, h3)` | `h1, h2, h3` | Kiểm tra các tiêu đề trong <main>: h1 đúng, h2/h3 chứa đủ các mục (theo thứ tự). |
| `content.verifyMainContains` | `k.content.verify_main_contains(texts)` | `texts` | Kiểm tra <main> có chứa các đoạn chữ. |
| `content.verifyBlockContains` | `k.content.verify_block_contains(heading, text)` | `heading, text` | Kiểm tra khối có tiêu đề h3 (vd: thẻ "Giao hàng nhanh") chứa đoạn chữ. |
| `content.verifyMainNotMatching` | `k.content.verify_main_not_matching(pattern)` | `pattern` | Kiểm tra <main> KHÔNG chứa chuỗi khớp biểu thức chính quy (vd: ký tự Cyrillic). |
| `content.verifyNotFoundPage` | `k.content.verify_not_found_page(message)` | `message` | Kiểm tra route không tồn tại hiển thị trang báo lỗi (thông báo + layout). |

## cart

| Keyword | Python | Tham số | Mô tả |
|---|---|---|---|
| `cart.seedCart` | `k.cart.seed_cart(items)` | `items` | Đặt sẵn sản phẩm vào giỏ (localStorage) - gọi TRƯỚC lần mở trang đầu tiên. |
| `cart.openCart` | `k.cart.open_cart()` | — | Bấm icon giỏ hàng để mở drawer. |
| `cart.closeCart` | `k.cart.close_cart()` | — | Đóng drawer bằng nút X. |
| `cart.closeCartWithEsc` | `k.cart.close_cart_with_esc()` | — | Đóng drawer bằng phím ESC. |
| `cart.verifyCartBadge` | `k.cart.verify_cart_badge(count)` | `count` | Kiểm tra số trên icon giỏ hàng (0 = không hiện badge). |
| `cart.verifyCartEmpty` | `k.cart.verify_cart_empty()` | — | Kiểm tra drawer hiển thị "Giỏ hàng trống". |
| `cart.verifyCartItemCount` | `k.cart.verify_cart_item_count(count)` | `count` | Kiểm tra số dòng sản phẩm trong drawer (và tiêu đề "Giỏ hàng (n)"). |
| `cart.verifyCartItem` | `k.cart.verify_cart_item(name, contains_text)` | `name, contains_text=None` | Kiểm tra 1 sản phẩm có trong giỏ, có thể kèm đoạn chữ (vd: size). |
| `cart.increaseQuantity` | `k.cart.increase_quantity(name, times)` | `name, times=1` | Bấm "+" số lần cho 1 sản phẩm. |
| `cart.decreaseQuantity` | `k.cart.decrease_quantity(name, times)` | `name, times=1` | Bấm "-" số lần cho 1 sản phẩm. |
| `cart.verifyQuantity` | `k.cart.verify_quantity(name, quantity)` | `name, quantity` | Kiểm tra số lượng hiển thị của 1 sản phẩm. |
| `cart.verifyDecreaseDisabled` | `k.cart.verify_decrease_disabled(name)` | `name` | Kiểm tra nút "-" bị khóa (số lượng = 1). |
| `cart.removeItem` | `k.cart.remove_item(name)` | `name` | Xóa 1 sản phẩm khỏi giỏ. |
| `cart.selectAll` | `k.cart.select_all(checked)` | `checked` | Tick / bỏ tick "Chọn tất cả". |
| `cart.verifyAllSelected` | `k.cart.verify_all_selected(checked)` | `checked` | Kiểm tra trạng thái ô "Chọn tất cả". |
| `cart.verifySubtotal` | `k.cart.verify_subtotal(amount)` | `amount` | Kiểm tra dòng Tạm tính chứa số tiền, vd: "550.000". |
| `cart.verifyCheckoutEnabled` | `k.cart.verify_checkout_enabled(enabled)` | `enabled` | Kiểm tra nút THANH TOÁN bật/tắt. |
| `cart.proceedToCheckout` | `k.cart.proceed_to_checkout()` | — | Bấm THANH TOÁN trong drawer và chờ sang /checkout. |
| `cart.verifyStoredItemCount` | `k.cart.verify_stored_item_count(count)` | `count` | Kiểm tra số dòng sản phẩm lưu trong localStorage. |
| `cart.verifyStoredQuantity` | `k.cart.verify_stored_quantity(name, quantity)` | `name, quantity` | Kiểm tra số lượng của 1 sản phẩm lưu trong localStorage. |

## checkout

| Keyword | Python | Tham số | Mô tả |
|---|---|---|---|
| `checkout.openCheckout` | `k.checkout.open_checkout()` | — | Mở trang thanh toán. |
| `checkout.verifyEmptyCheckout` | `k.checkout.verify_empty_checkout()` | — | Kiểm tra trang thanh toán báo giỏ trống, không có nút Thanh toán. |
| `checkout.verifyProductInCheckout` | `k.checkout.verify_product_in_checkout(name)` | `name` | Kiểm tra sản phẩm hiển thị trong khối sản phẩm của trang thanh toán. |
| `checkout.verifyGuestLoginPrompt` | `k.checkout.verify_guest_login_prompt()` | — | Kiểm tra nút "Đăng nhập / Đăng ký" cho khách vãng lai. |
| `checkout.fillShipping` | `k.checkout.fill_shipping(info)` | `info` | Điền thông tin giao hàng (dùng dữ liệu checkout/addresses.json). |
| `checkout.clearShippingField` | `k.checkout.clear_shipping_field(field)` | `field` | Xóa nội dung 1 ô trong form giao hàng: firstName \| lastName \| phone \| address. |
| `checkout.chooseShipping` | `k.checkout.choose_shipping(method)` | `method` | Chọn phương thức giao hàng: standard \| express. |
| `checkout.choosePayment` | `k.checkout.choose_payment(method)` | `method` | Chọn phương thức thanh toán: cod \| bank \| vnpay \| momo. |
| `checkout.verifySubmitEnabled` | `k.checkout.verify_submit_enabled(enabled)` | `enabled` | Kiểm tra nút Thanh toán bật/tắt. |
| `checkout.verifySummaryContains` | `k.checkout.verify_summary_contains(text)` | `text` | Kiểm tra khối tóm tắt đơn hàng chứa đoạn chữ / số tiền. |
| `checkout.mockCreateOrder` | `k.checkout.mock_create_order(options)` | `options=None` | Giả lập API tạo đơn: thành công (orderNumber) hoặc lỗi (status + message). Lưu lại payload gửi lên. |
| `checkout.placeOrder` | `k.checkout.place_order()` | — | Bấm nút Thanh toán. |
| `checkout.verifyOrderSuccess` | `k.checkout.verify_order_success(heading, order_number)` | `heading, order_number=None` | Kiểm tra trang đặt hàng thành công: tiêu đề + mã đơn (nếu có). |
| `checkout.verifyLastOrderPayload` | `k.checkout.verify_last_order_payload(expected)` | `expected` | Kiểm tra payload đơn hàng gửi lên backend chứa các trường mong đợi. |
| `checkout.verifyStillOnCheckout` | `k.checkout.verify_still_on_checkout()` | — | Kiểm tra vẫn ở trang thanh toán (đặt hàng thất bại). |
| `checkout.verifyOrderSuccessWithoutData` | `k.checkout.verify_order_success_without_data()` | — | Mở /order-success trực tiếp và kiểm tra báo không có dữ liệu đơn. |

## account

| Keyword | Python | Tham số | Mô tả |
|---|---|---|---|
| `account.openAccountMenuLink` | `k.account.open_account_menu_link(name)` | `name` | Mở menu tài khoản trên header và bấm 1 mục: "Hồ sơ cá nhân" \| "Đơn hàng của tôi" \| "Yêu thích". |
| `account.clickAccountIcon` | `k.account.click_account_icon()` | — | Bấm icon tài khoản khi chưa đăng nhập (dẫn tới /login). |
| `account.openProfile` | `k.account.open_profile()` | — | Mở trực tiếp trang hồ sơ /profile. |
| `account.verifyProfileLoaded` | `k.account.verify_profile_loaded()` | — | Kiểm tra trang hồ sơ hiển thị khối "Thông tin tài khoản". |
| `account.openOrders` | `k.account.open_orders()` | — | Mở trực tiếp trang đơn hàng /orders. |
| `account.verifyOrdersLoaded` | `k.account.verify_orders_loaded()` | — | Kiểm tra trang đơn hàng tải xong (có ô tìm theo mã đơn). |
| `account.verifyWishlistLoaded` | `k.account.verify_wishlist_loaded()` | — | Kiểm tra trang yêu thích tải xong (có tiêu đề + danh sách hoặc thông báo rỗng). |
| `account.openProfileFromMenu` | `k.account.open_profile_from_menu()` | — | Vào trang hồ sơ đúng cách người dùng làm: trang chủ -> menu tài khoản -> "Hồ sơ cá nhân" (tránh bug F5 /profile). |
| `account.openWishlist` | `k.account.open_wishlist()` | — | Mở trực tiếp trang yêu thích /favorites và chờ tải xong. |
| `account.openAddresses` | `k.account.open_addresses()` | — | Mở trực tiếp trang sổ địa chỉ /addresses và chờ tải xong. |
| `account.openOrderDetail` | `k.account.open_order_detail(id)` | `id` | Mở trực tiếp trang chi tiết đơn /orders/:id. |
| `account.clickSidebarLink` | `k.account.click_sidebar_link(label)` | `label` | Bấm 1 link trên sidebar tài khoản, vd: "Đơn hàng của tôi", "Sổ địa chỉ". |
| `account.logoutFromSidebar` | `k.account.logout_from_sidebar()` | — | Đăng xuất bằng nút "Đăng xuất" trên sidebar tài khoản. |
| `account.seedStoredUser` | `k.account.seed_stored_user(user)` | `user` | Thay thông tin user đang lưu (localStorage) bằng user cho trước - gọi TRƯỚC lần mở trang đầu tiên. |
| `account.verifyProfileFields` | `k.account.verify_profile_fields(fields)` | `fields` | Kiểm tra các trường ở chế độ xem hồ sơ: { "Họ và tên": "...", "Giới tính": "Nữ" }. |
| `account.startEditProfile` | `k.account.start_edit_profile()` | — | Bấm "Chỉnh sửa" để chuyển hồ sơ sang chế độ sửa. |
| `account.fillProfileForm` | `k.account.fill_profile_form(form)` | `form` | Điền form sửa hồ sơ (chỉ các trường có trong dữ liệu); gender: male \| female \| other. |
| `account.verifyProfileForm` | `k.account.verify_profile_form(form)` | `form` | Kiểm tra giá trị đang có trong form sửa hồ sơ. |
| `account.verifyProfileEmailLocked` | `k.account.verify_profile_email_locked(email)` | `email` | Kiểm tra ô Email trong form sửa bị khóa và hiển thị đúng email. |
| `account.saveProfile` | `k.account.save_profile()` | — | Bấm "Lưu thay đổi" trong form sửa hồ sơ. |
| `account.cancelEditProfile` | `k.account.cancel_edit_profile()` | — | Bấm "Hủy" để thoát chế độ sửa hồ sơ. |
| `account.verifyProfileEditing` | `k.account.verify_profile_editing(editing)` | `editing` | Kiểm tra hồ sơ đang ở chế độ sửa (true) hay chế độ xem (false). |
| `account.openChangePassword` | `k.account.open_change_password()` | — | Bấm "Đổi mật khẩu" và chờ modal mở. |
| `account.fillChangePassword` | `k.account.fill_change_password(form)` | `form` | Điền 3 ô trong modal đổi mật khẩu (hiện tại, mới, xác nhận). |
| `account.submitChangePassword` | `k.account.submit_change_password()` | — | Bấm "Xác nhận" trong modal đổi mật khẩu. |
| `account.verifyChangePasswordError` | `k.account.verify_change_password_error(message)` | `message` | Kiểm tra thông báo lỗi trong modal đổi mật khẩu. |
| `account.verifyChangePasswordClosed` | `k.account.verify_change_password_closed()` | — | Kiểm tra modal đổi mật khẩu đã đóng. |
| `account.cancelChangePassword` | `k.account.cancel_change_password()` | — | Bấm "Hủy" ở cuối modal đổi mật khẩu. |
| `account.closeChangePassword` | `k.account.close_change_password()` | — | Bấm nút chữ "Đóng" ở góc trên modal đổi mật khẩu. |
| `account.verifyChangePasswordFormEmpty` | `k.account.verify_change_password_form_empty()` | — | Kiểm tra modal đổi mật khẩu đang mở với form trống, không có lỗi cũ. |
| `account.verifyProfileSummary` | `k.account.verify_profile_summary(stats)` | `stats` | Kiểm tra dải thống kê trên trang hồ sơ: { "Tổng đơn hàng": "7", ... }. |
| `account.verifyRecentOrders` | `k.account.verify_recent_orders(codes)` | `codes` | Kiểm tra khối "Đơn hàng gần đây" hiển thị đúng các mã đơn theo thứ tự ([] = thông báo chưa có đơn). |
| `account.verifyRecentFavorites` | `k.account.verify_recent_favorites(names)` | `names` | Kiểm tra khối "Sản phẩm yêu thích gần đây" hiển thị đúng tên theo thứ tự ([] = thông báo trống). |
| `account.verifyDefaultAddress` | `k.account.verify_default_address(texts)` | `texts` | Kiểm tra khối "Địa chỉ giao hàng mặc định" chứa các đoạn chữ. |
| `account.clickUpdateAddress` | `k.account.click_update_address()` | — | Bấm "Cập nhật địa chỉ" trên hồ sơ và chờ sang /addresses. |
| `account.verifyOrderStats` | `k.account.verify_order_stats(stats)` | `stats` | Kiểm tra số đếm trên các ô thống kê: { "Tất cả đơn": 7, "Đã hủy": 1 }. |
| `account.filterOrdersByStatus` | `k.account.filter_orders_by_status(tab)` | `tab` | Bấm tab lọc trạng thái đơn, vd: "Chờ xác nhận". |
| `account.clickOrderStat` | `k.account.click_order_stat(label)` | `label` | Bấm 1 ô thống kê để lọc nhanh, vd: "Đã hủy". |
| `account.searchOrders` | `k.account.search_orders(query)` | `query` | Gõ vào ô "Tìm theo mã đơn hàng...". |
| `account.verifyOrderList` | `k.account.verify_order_list(codes)` | `codes` | Kiểm tra danh sách đơn hiển thị đúng các mã đơn theo thứ tự. |
| `account.verifyOrdersEmpty` | `k.account.verify_orders_empty(message)` | `message` | Kiểm tra trang đơn hàng hiển thị thông báo rỗng, vd: "Bạn chưa có đơn hàng nào". |
| `account.verifyOrderItem` | `k.account.verify_order_item(code, texts)` | `code, texts` | Kiểm tra 1 đơn trong danh sách chứa các đoạn chữ (ngày, số lượng, thanh toán, tổng tiền...). |
| `account.verifyOrderStatus` | `k.account.verify_order_status(code, label)` | `code, label` | Kiểm tra nhãn trạng thái của 1 đơn trong danh sách. |
| `account.verifyOrderCancelable` | `k.account.verify_order_cancelable(code, cancelable)` | `code, cancelable` | Kiểm tra đơn trong danh sách có (true) / không có (false) nút "Hủy đơn". |
| `account.cancelOrderFromList` | `k.account.cancel_order_from_list(code)` | `code` | Bấm "Hủy đơn" của 1 đơn trong danh sách (app không hỏi xác nhận). |
| `account.openOrderFromList` | `k.account.open_order_from_list(code)` | `code` | Bấm "Xem chi tiết" của 1 đơn và chờ sang trang chi tiết. |
| `account.verifyOrderDetailHeading` | `k.account.verify_order_detail_heading(heading)` | `heading` | Kiểm tra tiêu đề trang chi tiết đơn, vd: "Chi tiết đơn hàng #ORD000107". |
| `account.verifyOrderDetailStatus` | `k.account.verify_order_detail_status(status, payment)` | `status, payment` | Kiểm tra 2 ô trạng thái đơn hàng + trạng thái thanh toán ở đầu trang chi tiết. |
| `account.verifyOrderDetailInfo` | `k.account.verify_order_detail_info(section, rows)` | `section, rows` | Kiểm tra các dòng "nhãn: giá trị" trong 1 khối, vd: ("Thông tin giao hàng", { "Người nhận": "..." }). |
| `account.verifyOrderDetailItems` | `k.account.verify_order_detail_items(heading, names)` | `heading, names` | Kiểm tra tiêu đề khối sản phẩm (vd: "Sản phẩm đã đặt (2)") và tên sản phẩm theo thứ tự. |
| `account.verifyOrderDetailItem` | `k.account.verify_order_detail_item(name, texts)` | `name, texts` | Kiểm tra 1 dòng sản phẩm trong đơn chứa các đoạn chữ (màu, size, SKU, giá, số lượng). |
| `account.verifyOrderDetailTotals` | `k.account.verify_order_detail_totals(rows)` | `rows` | Kiểm tra khối "Chi tiết thanh toán": { "Tạm tính": "480.000đ", "Phí vận chuyển": "Miễn phí", ... }. |
| `account.verifyOrderDetailCancelable` | `k.account.verify_order_detail_cancelable(cancelable)` | `cancelable` | Kiểm tra trang chi tiết có (true) / không có (false) nút "Hủy đơn hàng". |
| `account.openCancelOrderDialog` | `k.account.open_cancel_order_dialog()` | — | Bấm "Hủy đơn hàng" và chờ hộp xác nhận hiện ra. |
| `account.confirmCancelOrder` | `k.account.confirm_cancel_order(reason)` | `reason=''` | Nhập lý do (để trống = không nhập) rồi bấm "Xác nhận hủy". |
| `account.closeCancelOrderDialog` | `k.account.close_cancel_order_dialog()` | — | Bấm "Đóng" trên hộp xác nhận hủy đơn. |
| `account.verifyCancelOrderDialog` | `k.account.verify_cancel_order_dialog(open)` | `open` | Kiểm tra hộp xác nhận hủy đơn đang mở (true) / đã đóng (false). |
| `account.verifyOrderDetailError` | `k.account.verify_order_detail_error(message)` | `message` | Kiểm tra trang chi tiết đơn báo lỗi (thông báo + nút "Quay lại đơn hàng"). |
| `account.backToOrdersFromError` | `k.account.back_to_orders_from_error()` | — | Bấm "Quay lại đơn hàng" trên màn hình lỗi và chờ về /orders. |
| `account.goBackFromOrderDetail` | `k.account.go_back_from_order_detail()` | — | Bấm nút "Quay lại" ở góc trên trang chi tiết đơn và chờ về /orders. |
| `account.verifyWishlistCount` | `k.account.verify_wishlist_count(count)` | `count` | Kiểm tra dòng "<N> sản phẩm yêu thích" dưới tiêu đề. |
| `account.verifyWishlistProducts` | `k.account.verify_wishlist_products(names)` | `names` | Kiểm tra danh sách thẻ sản phẩm yêu thích đúng tên + đúng thứ tự. |
| `account.searchWishlist` | `k.account.search_wishlist(query)` | `query` | Gõ vào ô "Tìm sản phẩm yêu thích...". |
| `account.sortWishlist` | `k.account.sort_wishlist(sort)` | `sort` | Chọn cách sắp xếp: recent \| price_asc \| price_desc. |
| `account.removeFromWishlist` | `k.account.remove_from_wishlist(name)` | `name` | Bấm trái tim "Bỏ yêu thích" trên thẻ sản phẩm. |
| `account.addWishlistItemToCart` | `k.account.add_wishlist_item_to_cart(name)` | `name` | Bấm "Thêm vào giỏ hàng" trên thẻ sản phẩm yêu thích. |
| `account.verifyWishlistItem` | `k.account.verify_wishlist_item(name, texts)` | `name, texts` | Kiểm tra thẻ sản phẩm yêu thích chứa các đoạn chữ (danh mục, giá, % giảm, tình trạng...). |
| `account.verifyWishlistItemAvailable` | `k.account.verify_wishlist_item_available(name, available)` | `name, available` | Kiểm tra sản phẩm còn hàng (nút thêm giỏ bật) hay hết hàng (nhãn "Hết hàng", nút tắt). |
| `account.verifyWishlistNoMatch` | `k.account.verify_wishlist_no_match()` | — | Kiểm tra thông báo "Không tìm thấy sản phẩm phù hợp" khi lọc/tìm không ra. |
| `account.verifyWishlistEmpty` | `k.account.verify_wishlist_empty()` | — | Kiểm tra trang yêu thích trống ("Bạn chưa có sản phẩm yêu thích", 0 sản phẩm). |
| `account.favoriteFromListing` | `k.account.favorite_from_listing(path)` | `path` | Mở trang danh mục và bấm nút trái tim (yêu thích) của sản phẩm đầu tiên. |
| `account.verifyAddressesEmpty` | `k.account.verify_addresses_empty()` | — | Kiểm tra trang địa chỉ trống ("Bạn chưa có địa chỉ nào"). |
| `account.openAddAddressForm` | `k.account.open_add_address_form()` | — | Bấm nút "Thêm địa chỉ" trên tiêu đề và chờ form "Thêm địa chỉ mới". |
| `account.openAddAddressFromEmptyState` | `k.account.open_add_address_from_empty_state()` | — | Bấm "Thêm địa chỉ mới" ở màn hình trống và chờ form mở. |
| `account.fillAddressForm` | `k.account.fill_address_form(form)` | `form` | Điền form địa chỉ (chỉ các trường có trong dữ liệu); city = tên tỉnh, vd: "Hồ Chí Minh". |
| `account.submitAddressForm` | `k.account.submit_address_form()` | — | Bấm nút lưu của form địa chỉ ("Thêm địa chỉ" / "Lưu thay đổi"). |
| `account.cancelAddressForm` | `k.account.cancel_address_form()` | — | Bấm "Hủy" để đóng form địa chỉ. |
| `account.verifyAddressFormErrors` | `k.account.verify_address_form_errors(messages)` | `messages` | Kiểm tra các thông báo lỗi dưới ô nhập của form địa chỉ. |
| `account.verifyAddressFormOpen` | `k.account.verify_address_form_open(heading)` | `heading` | Kiểm tra form địa chỉ đang mở với tiêu đề: "Thêm địa chỉ mới" \| "Sửa địa chỉ". |
| `account.verifyAddressFormClosed` | `k.account.verify_address_form_closed()` | — | Kiểm tra form địa chỉ đã đóng. |
| `account.verifyAddressFormValues` | `k.account.verify_address_form_values(form)` | `form` | Kiểm tra giá trị đang có trong form địa chỉ. |
| `account.verifyAddressList` | `k.account.verify_address_list(names)` | `names` | Kiểm tra danh sách thẻ địa chỉ (tên người nhận theo thứ tự) và dòng "<N> địa chỉ đã lưu". |
| `account.verifyAddressCard` | `k.account.verify_address_card(name, texts)` | `name, texts` | Kiểm tra thẻ địa chỉ của người nhận chứa các đoạn chữ (SĐT, địa chỉ đầy đủ...). |
| `account.verifyAddressDefault` | `k.account.verify_address_default(name, is_default)` | `name, is_default` | Kiểm tra địa chỉ là mặc định (badge "Mặc định", không có nút đặt mặc định) hay không. |
| `account.verifyAddressNameRow` | `k.account.verify_address_name_row(name, is_default)` | `name, is_default` | Kiểm tra dòng tên trên thẻ địa chỉ chỉ gồm tên (+ "Mặc định" nếu là mặc định), không có ký tự thừa. |
| `account.verifyDefaultBadgeCount` | `k.account.verify_default_badge_count(count)` | `count` | Kiểm tra số badge "Mặc định" trên toàn trang địa chỉ. |
| `account.editAddress` | `k.account.edit_address(name)` | `name` | Bấm nút "Sửa" trên thẻ địa chỉ và chờ form "Sửa địa chỉ". |
| `account.setDefaultAddress` | `k.account.set_default_address(name)` | `name` | Bấm nút "Đặt làm mặc định" trên thẻ địa chỉ. |
| `account.deleteAddress` | `k.account.delete_address(name)` | `name` | Bấm nút "Xóa" trên thẻ địa chỉ và chờ hộp xác nhận "Xóa địa chỉ". |
| `account.confirmDeleteAddress` | `k.account.confirm_delete_address()` | — | Bấm "Xóa địa chỉ" trong hộp xác nhận. |
| `account.cancelDeleteAddress` | `k.account.cancel_delete_address()` | — | Bấm "Hủy" trong hộp xác nhận xóa địa chỉ và chờ hộp đóng. |
| `account.verifyDeleteAddressDialog` | `k.account.verify_delete_address_dialog(text)` | `text` | Kiểm tra hộp xác nhận xóa địa chỉ chứa đoạn chữ, vd: câu hỏi kèm địa chỉ. |
| `account.verifyCheckoutAccount` | `k.account.verify_checkout_account(name, email)` | `name, email` | Kiểm tra trang thanh toán hiển thị tài khoản đang đăng nhập (tên + email), không có nút đăng nhập. |
| `account.verifyCheckoutPrefill` | `k.account.verify_checkout_prefill(expected)` | `expected` | Kiểm tra form giao hàng được điền sẵn từ tài khoản: { firstName, lastName, phone }. |
| `account.logoutOnCheckout` | `k.account.logout_on_checkout()` | — | Bấm "Đăng xuất" trong khối tài khoản trên trang thanh toán. |
| `account.verifyCheckoutGuestMode` | `k.account.verify_checkout_guest_mode()` | — | Kiểm tra trang thanh toán chuyển về chế độ khách vãng lai (vẫn ở /checkout, token bị xóa). |
| `account.goToLoginFromCheckout` | `k.account.go_to_login_from_checkout()` | — | Bấm "Đăng nhập / Đăng ký" trên trang thanh toán và chờ sang /login. |
| `account.verifyOrderSuccessNumber` | `k.account.verify_order_success_number(order_number)` | `order_number` | Kiểm tra mã đơn hiển thị cạnh "Mã đơn hàng:" trên trang đặt hàng thành công. |
| `account.verifyOrderSuccessInfo` | `k.account.verify_order_success_info(section, rows)` | `section, rows` | Kiểm tra các dòng trong 1 khối trang thành công: "Thông tin thanh toán" \| "Người nhận" \| "Chi tiết thanh toán". |
| `account.verifyOrderSuccessLinks` | `k.account.verify_order_success_links()` | — | Kiểm tra trang thành công có 2 link "Tiếp tục mua sắm" (về /) và link "Xem đơn hàng" (tới /orders). |
| `account.openOrdersFromSuccess` | `k.account.open_orders_from_success()` | — | Bấm "Xem đơn hàng" trên trang thành công và chờ sang /orders. |

## admin

| Keyword | Python | Tham số | Mô tả |
|---|---|---|---|
| `admin.openAdminLogin` | `k.admin.open_admin_login()` | — | Mở trang đăng nhập quản trị. |
| `admin.loginAdmin` | `k.admin.login_admin(email, password)` | `email, password` | Nhập email + mật khẩu admin và bấm Đăng nhập. |
| `admin.loginAsAdmin` | `k.admin.login_as_admin()` | — | Đăng nhập bằng tài khoản admin test trong .env và chờ vào Dashboard. |
| `admin.loginAdminExpectingError` | `k.admin.login_admin_expecting_error(email, password, message)` | `email, password, message` | Đăng nhập admin sai và kiểm tra thông báo lỗi vẫn hiển thị (không reload). |
| `admin.verifyOnAdminLogin` | `k.admin.verify_on_admin_login()` | — | Kiểm tra đang ở trang đăng nhập admin (bị chặn khi chưa đăng nhập). |
| `admin.backToStore` | `k.admin.back_to_store()` | — | Bấm "Quay về cửa hàng" trên trang đăng nhập admin. |
| `admin.openDashboard` | `k.admin.open_dashboard()` | — | Mở trang quản trị /admin (cần đã đăng nhập) và chờ sidebar. |
| `admin.navigateMenu` | `k.admin.navigate_menu(label)` | `label` | Bấm 1 mục trên sidebar quản trị, vd: "Sản phẩm". |
| `admin.openAdminPage` | `k.admin.open_admin_page(path, title)` | `path, title` | Mở 1 trang quản trị theo đường dẫn và kiểm tra tiêu đề trên header. |
| `admin.verifyHeaderTitle` | `k.admin.verify_header_title(title)` | `title` | Kiểm tra tiêu đề trang trên header admin. |
| `admin.verifyTableHeaders` | `k.admin.verify_table_headers(headers)` | `headers` | Kiểm tra bảng có đủ các cột (theo thứ tự). |
| `admin.searchList` | `k.admin.search_list(placeholder, text)` | `placeholder, text` | Gõ vào ô tìm kiếm có placeholder cho trước. |
| `admin.clickButton` | `k.admin.click_button(name)` | `name` | Bấm 1 nút theo tên hiển thị (ưu tiên nút trong modal đang mở). |
| `admin.clickRowAction` | `k.admin.click_row_action(row_text, title)` | `row_text, title` | Bấm nút hành động (title) trên dòng chứa text, vd: ("Áo thun", "Sửa"). |
| `admin.verifyRow` | `k.admin.verify_row(text, visible)` | `text, visible=True` | Kiểm tra có/không có dòng chứa text trong bảng. |
| `admin.fillForm` | `k.admin.fill_form(fields)` | `fields` | Điền form theo label: chuỗi -> input/textarea/select (value hoặc label option), boolean -> checkbox. |
| `admin.verifyFieldValue` | `k.admin.verify_field_value(label, value)` | `label, value` | Kiểm tra giá trị hiện tại của 1 ô trong form (theo label). |
| `admin.verifyModalOpen` | `k.admin.verify_modal_open(heading)` | `heading` | Kiểm tra modal/khối có tiêu đề đang hiển thị. |
| `admin.verifyModalClosed` | `k.admin.verify_modal_closed(heading)` | `heading` | Kiểm tra modal/khối có tiêu đề đã đóng. |
| `admin.verifyAdminPage` | `k.admin.verify_admin_page(path)` | `path` | Kiểm tra đang ở 1 trang quản trị (URL + tiêu đề trang). |

## adminCatalog

| Keyword | Python | Tham số | Mô tả |
|---|---|---|---|
| `adminCatalog.mockCatalogApi` | `k.admin_catalog.mock_catalog_api(fixture)` | `fixture` | Mock GET /admin/products (lọc search/category/brand), /admin/products/:id, /admin/categories, /admin/brands. |
| `adminCatalog.verifyApiRequested` | `k.admin_catalog.verify_api_requested(path, params)` | `path, params=None` | Kiểm tra trình duyệt đã gọi GET tới đường dẫn (vd: "/admin/products") với đủ tham số query. |
| `adminCatalog.verifyColumns` | `k.admin_catalog.verify_columns(headers)` | `headers` | Kiểm tra tiêu đề cột bảng theo nội dung gốc (bỏ qua CSS uppercase), đúng thứ tự. |
| `adminCatalog.verifyProductCountAtLeast` | `k.admin_catalog.verify_product_count_at_least(minimum)` | `minimum` | Kiểm tra bảng sản phẩm có ít nhất `min` dòng dữ liệu. |
| `adminCatalog.verifyProductRows` | `k.admin_catalog.verify_product_rows(rows)` | `rows` | Kiểm tra từng dòng sản phẩm: thương hiệu, SKU, danh mục, giá, tồn kho (đỏ khi <= 5), đã bán, nổi bật, trạng thái. |
| `adminCatalog.verifyProductListed` | `k.admin_catalog.verify_product_listed(name, visible)` | `name, visible=True` | Kiểm tra có/không có dòng sản phẩm theo tên chính xác. |
| `adminCatalog.searchProducts` | `k.admin_catalog.search_products(text)` | `text` | Gõ từ khóa vào ô tìm sản phẩm. |
| `adminCatalog.filterProductsByCategory` | `k.admin_catalog.filter_products_by_category(label)` | `label` | Chọn lọc danh mục theo tên hiển thị. |
| `adminCatalog.filterProductsByBrand` | `k.admin_catalog.filter_products_by_brand(label)` | `label` | Chọn lọc thương hiệu theo tên hiển thị. |
| `adminCatalog.clickProductFeatured` | `k.admin_catalog.click_product_featured(name)` | `name` | Bấm nút ngôi sao (nổi bật) trên dòng sản phẩm. |
| `adminCatalog.verifyProductFeaturedTitle` | `k.admin_catalog.verify_product_featured_title(name, title)` | `name, title` | Kiểm tra title nút ngôi sao: "Đánh dấu nổi bật" (chưa nổi bật) hoặc "Bỏ nổi bật". |
| `adminCatalog.clickProductStatus` | `k.admin_catalog.click_product_status(name)` | `name` | Bấm nút gạt trạng thái bán trên dòng sản phẩm. |
| `adminCatalog.verifyProductActive` | `k.admin_catalog.verify_product_active(name, active)` | `name, active` | Kiểm tra nút gạt trạng thái bán đang bật (xanh) hay tắt (xám). |
| `adminCatalog.clickProductAction` | `k.admin_catalog.click_product_action(name, title)` | `name, title` | Bấm nút hành động "Xem" / "Sửa" / "Xóa" trên dòng sản phẩm. |
| `adminCatalog.verifyProductViewLink` | `k.admin_catalog.verify_product_view_link(name, href)` | `name, href` | Kiểm tra link "Xem" của sản phẩm trỏ tới trang chi tiết ngoài cửa hàng. |
| `adminCatalog.verifyDeleteProductModal` | `k.admin_catalog.verify_delete_product_modal(heading, message)` | `heading, message` | Kiểm tra modal xóa sản phẩm đang mở với tiêu đề + nội dung cảnh báo. |
| `adminCatalog.selectProducts` | `k.admin_catalog.select_products(names)` | `names` | Tích chọn các dòng sản phẩm theo tên. |
| `adminCatalog.selectAllProducts` | `k.admin_catalog.select_all_products()` | — | Tích ô chọn tất cả trên đầu bảng sản phẩm. |
| `adminCatalog.verifyBulkSelection` | `k.admin_catalog.verify_bulk_selection(text)` | `text` | Kiểm tra thanh thao tác hàng loạt "{n} sản phẩm được chọn" (null = ẩn). |
| `adminCatalog.clickBulkDelete` | `k.admin_catalog.click_bulk_delete()` | — | Bấm "Xóa đã chọn" trên thanh thao tác hàng loạt. |
| `adminCatalog.verifyProductsPagination` | `k.admin_catalog.verify_products_pagination(text)` | `text` | Kiểm tra dòng phân trang sản phẩm, vd: "Trang 1 trên 3" (null = không có phân trang). |
| `adminCatalog.verifyProductsPaginationFirstPage` | `k.admin_catalog.verify_products_pagination_first_page()` | — | Kiểm tra dòng phân trang sản phẩm khớp mẫu "Trang 1 trên N". |
| `adminCatalog.goToProductsPage` | `k.admin_catalog.go_to_products_page(n)` | `n` | Bấm số trang trên phân trang sản phẩm. |
| `adminCatalog.clickAddProduct` | `k.admin_catalog.click_add_product()` | — | Bấm "Thêm sản phẩm" trên trang danh sách. |
| `adminCatalog.verifyProductFormReady` | `k.admin_catalog.verify_product_form_ready(submit_label)` | `submit_label` | Chờ form sản phẩm tải xong (hết "Đang tải dữ liệu...") và kiểm tra nhãn nút lưu. |
| `adminCatalog.submitProductForm` | `k.admin_catalog.submit_product_form()` | — | Bấm nút lưu form sản phẩm ("Tạo sản phẩm" / "Cập nhật"). |
| `adminCatalog.verifyProductFormError` | `k.admin_catalog.verify_product_form_error(text)` | `text` | Kiểm tra hộp lỗi đỏ trên form sản phẩm. |
| `adminCatalog.clickBackToProducts` | `k.admin_catalog.click_back_to_products()` | — | Bấm "Quay lại" trên form sản phẩm. |
| `adminCatalog.toggleVariantBuilder` | `k.admin_catalog.toggle_variant_builder()` | — | Bấm "+ Tạo biến thể" / "Tắt chế độ" trong khối Biến thể. |
| `adminCatalog.verifyVariantToggleLabel` | `k.admin_catalog.verify_variant_toggle_label(label)` | `label` | Kiểm tra nhãn nút bật/tắt chế độ tạo biến thể. |
| `adminCatalog.selectVariantSizes` | `k.admin_catalog.select_variant_sizes(sizes)` | `sizes` | Chọn các size trong chế độ tạo biến thể (vd: ["S", "M"]). |
| `adminCatalog.selectVariantColors` | `k.admin_catalog.select_variant_colors(colors)` | `colors` | Chọn các màu trong chế độ tạo biến thể (vd: ["Đen", "Trắng"]). |
| `adminCatalog.verifyGenerateVariantsButton` | `k.admin_catalog.verify_generate_variants_button(label, enabled)` | `label, enabled` | Kiểm tra nút "Tạo {n} biến thể" (nhãn + bật/tắt). |
| `adminCatalog.generateVariants` | `k.admin_catalog.generate_variants()` | — | Bấm "Tạo {n} biến thể". |
| `adminCatalog.verifyVariantRows` | `k.admin_catalog.verify_variant_rows(rows)` | `rows` | Kiểm tra lưới biến thể: size, màu, SKU từng dòng (đúng thứ tự). |
| `adminCatalog.verifyVariantCount` | `k.admin_catalog.verify_variant_count(count)` | `count` | Kiểm tra số dòng biến thể. |
| `adminCatalog.removeVariant` | `k.admin_catalog.remove_variant(index)` | `index` | Xóa dòng biến thể thứ `index` (bắt đầu từ 0). |
| `adminCatalog.addImageUrl` | `k.admin_catalog.add_image_url(url)` | `url` | Dán URL ảnh vào ô "Dán URL ảnh..." và nhấn Enter. |
| `adminCatalog.verifyImageCount` | `k.admin_catalog.verify_image_count(count)` | `count` | Kiểm tra số ảnh trong khối Hình ảnh và nhãn "Ảnh chính" (ảnh đầu tiên). |
| `adminCatalog.removeImage` | `k.admin_catalog.remove_image(index)` | `index` | Rê chuột vào ảnh thứ `index` và bấm nút X để xóa. |
| `adminCatalog.uploadProductImage` | `k.admin_catalog.upload_product_image(file_name, response)` | `file_name, response` | Mock POST /api/admin/upload (ghi lại header Authorization) rồi chọn 1 ảnh PNG để tải lên. |
| `adminCatalog.verifyUploadUsedAdminToken` | `k.admin_catalog.verify_upload_used_admin_token()` | — | Kiểm tra request tải ảnh gửi đúng token admin (Bearer + admin_token trong localStorage). |
| `adminCatalog.verifyCardCountAtLeast` | `k.admin_catalog.verify_card_count_at_least(minimum)` | `minimum` | Kiểm tra có ít nhất `min` thẻ (danh mục / thương hiệu). |
| `adminCatalog.verifyCards` | `k.admin_catalog.verify_cards(visible, hidden)` | `visible, hidden=None` | Kiểm tra các thẻ hiển thị (`visible`) và không hiển thị (`hidden`) theo tên. |
| `adminCatalog.verifyCardsEmpty` | `k.admin_catalog.verify_cards_empty(text)` | `text` | Kiểm tra lưới thẻ trống với thông báo, vd: "Không tìm thấy danh mục". |
| `adminCatalog.clickCardEdit` | `k.admin_catalog.click_card_edit(name)` | `name` | Rê chuột vào thẻ rồi bấm icon Sửa (icon ẩn tới khi hover, không có tên). |
| `adminCatalog.clickCardDelete` | `k.admin_catalog.click_card_delete(name)` | `name` | Rê chuột vào thẻ rồi bấm icon Xóa (icon ẩn tới khi hover, không có tên). |
| `adminCatalog.clickCardToggle` | `k.admin_catalog.click_card_toggle(name)` | `name` | Bấm nút gạt Hoạt động trên thẻ. |
| `adminCatalog.verifyCardActive` | `k.admin_catalog.verify_card_active(name, active)` | `name, active` | Kiểm tra nút gạt Hoạt động trên thẻ đang bật (xanh) hay tắt (xám). |
| `adminCatalog.verifyCardFeatured` | `k.admin_catalog.verify_card_featured(name, featured)` | `name, featured` | Kiểm tra thẻ có/không có nhãn "Nổi bật". |
| `adminCatalog.verifyCardDetails` | `k.admin_catalog.verify_card_details(name, slug, description)` | `name, slug, description=None` | Kiểm tra slug (/{slug}) và mô tả hiển thị trên thẻ. |
| `adminCatalog.verifyDeleteConfirmMessage` | `k.admin_catalog.verify_delete_confirm_message(message)` | `message` | Kiểm tra nội dung modal "Xác nhận xóa". |

## adminSales

| Keyword | Python | Tham số | Mô tả |
|---|---|---|---|
| `adminSales.mockOrdersApi` | `k.admin_sales.mock_orders_api(fixture)` | `fixture` | Mock GET /admin/orders (lọc search/status/payment_status), /admin/orders/stats và /admin/orders/:id. |
| `adminSales.mockCustomersApi` | `k.admin_sales.mock_customers_api(fixture)` | `fixture` | Mock GET /admin/customers (lọc search) và /admin/customers/:id. |
| `adminSales.mockEmployeesApi` | `k.admin_sales.mock_employees_api(fixture)` | `fixture` | Mock GET /admin/employees (lọc search theo tên/email). |
| `adminSales.verifyApiRequested` | `k.admin_sales.verify_api_requested(path, params)` | `path, params=None` | Kiểm tra trình duyệt đã gọi GET tới đường dẫn (vd: "/admin/orders") với đủ tham số query. |
| `adminSales.verifyColumns` | `k.admin_sales.verify_columns(headers)` | `headers` | Kiểm tra tiêu đề cột bảng theo nội dung gốc (bỏ qua CSS uppercase), đúng thứ tự. |
| `adminSales.verifyApiRequestCount` | `k.admin_sales.verify_api_request_count(path, min_count)` | `path, min_count` | Kiểm tra số request GET tới đường dẫn đạt ít nhất `min` lần. |
| `adminSales.toggleSidebar` | `k.admin_sales.toggle_sidebar()` | — | Bấm nút thu gọn / mở rộng sidebar. |
| `adminSales.verifySidebarCollapsed` | `k.admin_sales.verify_sidebar_collapsed(collapsed)` | `collapsed` | Kiểm tra sidebar đang thu gọn (72px, ẩn chữ menu) hoặc mở rộng (260px). |
| `adminSales.verifyActiveMenu` | `k.admin_sales.verify_active_menu(label)` | `label` | Kiểm tra chỉ có đúng 1 mục sidebar đang sáng và đó là `label`. |
| `adminSales.clickViewStore` | `k.admin_sales.click_view_store()` | — | Bấm "Xem cửa hàng" ở chân sidebar. |
| `adminSales.logout` | `k.admin_sales.logout(source)` | `source` | Đăng xuất từ chân sidebar ("sidebar") hoặc menu người dùng trên header ("menu"). |
| `adminSales.verifySidebarUser` | `k.admin_sales.verify_sidebar_user(name, role)` | `name, role` | Kiểm tra khối người dùng ở chân sidebar (tên + vai trò). |
| `adminSales.openUserMenu` | `k.admin_sales.open_user_menu()` | — | Mở menu người dùng trên header. |
| `adminSales.verifyUserMenu` | `k.admin_sales.verify_user_menu(name, email, role)` | `name, email, role` | Kiểm tra nút người dùng và menu thả xuống hiển thị tên, email, 3 mục. |
| `adminSales.chooseUserMenuItem` | `k.admin_sales.choose_user_menu_item(label)` | `label` | Bấm 1 mục trong menu người dùng ("Tổng quan" / "Cài đặt" / "Đăng xuất"). |
| `adminSales.clickOutsideUserMenu` | `k.admin_sales.click_outside_user_menu()` | — | Bấm ra ngoài menu người dùng (vào tiêu đề trang) để đóng menu. |
| `adminSales.verifyUserMenuOpen` | `k.admin_sales.verify_user_menu_open(is_open)` | `is_open` | Kiểm tra menu người dùng đang mở/đóng. |
| `adminSales.openNotifications` | `k.admin_sales.open_notifications()` | — | Bấm chuông thông báo để mở panel. |
| `adminSales.closeNotifications` | `k.admin_sales.close_notifications(via)` | `via='button'` | Đóng panel thông báo bằng nút X ("button") hoặc bấm ra ngoài ("overlay"). |
| `adminSales.verifyNotificationPanelOpen` | `k.admin_sales.verify_notification_panel_open(is_open)` | `is_open` | Kiểm tra panel thông báo đang mở / đã đóng. |
| `adminSales.verifyNotificationBadge` | `k.admin_sales.verify_notification_badge(expected)` | `expected` | Kiểm tra số trên chuông (null = không hiển thị số). |
| `adminSales.verifyNotificationPanel` | `k.admin_sales.verify_notification_panel(expected)` | `expected` | Kiểm tra panel: danh sách tiêu đề thông báo, thanh thống kê và dòng "{n} thông báo". |
| `adminSales.verifyNotificationsEmpty` | `k.admin_sales.verify_notifications_empty()` | — | Kiểm tra panel trống: "Không có thông báo nào" và "0 thông báo". |
| `adminSales.verifyNotificationVisible` | `k.admin_sales.verify_notification_visible(title, visible)` | `title, visible=True` | Kiểm tra có/không có thông báo theo tiêu đề trong panel. |
| `adminSales.clickNotification` | `k.admin_sales.click_notification(title)` | `title` | Bấm 1 thông báo theo tiêu đề. |
| `adminSales.verifyNewNotificationChip` | `k.admin_sales.verify_new_notification_chip(text)` | `text` | Kiểm tra nhãn "{n} mới" cạnh tiêu đề panel (null = không có). |
| `adminSales.markAllNotificationsRead` | `k.admin_sales.mark_all_notifications_read()` | — | Bấm "Đánh dấu đã đọc" trong panel thông báo. |
| `adminSales.refreshNotifications` | `k.admin_sales.refresh_notifications()` | — | Bấm nút "Làm mới" trong panel thông báo và kiểm tra API thông báo được gọi lại. |
| `adminSales.clickViewAllOrders` | `k.admin_sales.click_view_all_orders()` | — | Bấm "Xem tất cả đơn hàng" ở chân panel thông báo. |
| `adminSales.verifyStatCardLabels` | `k.admin_sales.verify_stat_card_labels(labels)` | `labels` | Kiểm tra 4 thẻ thống kê hiển thị đúng nhãn (theo thứ tự). |
| `adminSales.verifyStatCards` | `k.admin_sales.verify_stat_cards(cards)` | `cards` | Kiểm tra giá trị / dòng phụ / % thay đổi của các thẻ thống kê. |
| `adminSales.verifyStatCardHasNoChange` | `k.admin_sales.verify_stat_card_has_no_change(label)` | `label` | Kiểm tra thẻ thống kê KHÔNG hiển thị huy hiệu % tăng/giảm. |
| `adminSales.verifyDashboardSections` | `k.admin_sales.verify_dashboard_sections(titles)` | `titles` | Kiểm tra các khối tiêu đề trên dashboard. |
| `adminSales.verifyOrderStatusBreakdown` | `k.admin_sales.verify_order_status_breakdown(values)` | `values` | Kiểm tra số lượng đơn theo từng trạng thái (khối "Đơn hàng theo trạng thái"). |
| `adminSales.verifyRecentOrders` | `k.admin_sales.verify_recent_orders(orders)` | `orders` | Kiểm tra danh sách "Đơn hàng gần đây" (mã, khách, tổng tiền, trạng thái). |
| `adminSales.verifyTopProducts` | `k.admin_sales.verify_top_products(products)` | `products` | Kiểm tra danh sách "Sản phẩm bán chạy" (tên + số đã bán, theo thứ tự). |
| `adminSales.verifyQuickCards` | `k.admin_sales.verify_quick_cards(cards)` | `cards` | Kiểm tra giá trị các thẻ thao tác nhanh cuối dashboard. |
| `adminSales.clickDashboardLink` | `k.admin_sales.click_dashboard_link(label, section)` | `label, section=None` | Bấm 1 link trên dashboard; `section` dùng khi trùng tên (vd: "Xem tất cả"). |
| `adminSales.verifyChartTicks` | `k.admin_sales.verify_chart_ticks(ticks)` | `ticks` | Kiểm tra nhãn trục X của biểu đồ doanh thu. |
| `adminSales.verifyChartSeries` | `k.admin_sales.verify_chart_series(points)` | `points` | Kiểm tra biểu đồ vẽ vùng doanh thu + đường đơn hàng với `points` điểm dữ liệu. |
| `adminSales.selectRevenueRange` | `k.admin_sales.select_revenue_range(option)` | `option` | Chọn khoảng thời gian cho biểu đồ doanh thu, vd: "30 ngày qua". |
| `adminSales.verifyOrderStatusCards` | `k.admin_sales.verify_order_status_cards(counts)` | `counts` | Kiểm tra số lượng trên 7 thẻ trạng thái đơn hàng. |
| `adminSales.clickOrderStatusCard` | `k.admin_sales.click_order_status_card(label)` | `label` | Bấm 1 thẻ trạng thái đơn hàng (bật/tắt lọc). |
| `adminSales.verifyOrderStatusCardActive` | `k.admin_sales.verify_order_status_card_active(label, active)` | `label, active` | Kiểm tra thẻ trạng thái đang được chọn (viền đỏ) hay không. |
| `adminSales.searchOrders` | `k.admin_sales.search_orders(text)` | `text` | Gõ từ khóa vào ô tìm đơn hàng. |
| `adminSales.filterOrdersByStatus` | `k.admin_sales.filter_orders_by_status(value)` | `value` | Chọn lọc trạng thái đơn (value: pending, confirmed... hoặc "" = tất cả). |
| `adminSales.filterOrdersByPayment` | `k.admin_sales.filter_orders_by_payment(value)` | `value` | Chọn lọc trạng thái thanh toán (value: unpaid, paid, partially_paid, refunded). |
| `adminSales.filterOrdersByDate` | `k.admin_sales.filter_orders_by_date(date_from, date_to)` | `date_from, date_to` | Mở "Bộ lọc" và nhập khoảng ngày (yyyy-mm-dd). |
| `adminSales.clearOrderFilters` | `k.admin_sales.clear_order_filters()` | — | Bấm "Bộ lọc" rồi "Xóa bộ lọc". |
| `adminSales.verifyOrderFilters` | `k.admin_sales.verify_order_filters(expected)` | `expected` | Kiểm tra giá trị hiện tại của ô tìm kiếm, lọc trạng thái, lọc thanh toán. |
| `adminSales.verifyOrderRows` | `k.admin_sales.verify_order_rows(numbers)` | `numbers` | Kiểm tra bảng đơn hàng hiển thị đúng các mã đơn (theo thứ tự). |
| `adminSales.verifyOrderRow` | `k.admin_sales.verify_order_row(row)` | `row` | Kiểm tra 1 dòng đơn hàng: khách, số sản phẩm, tổng tiền, thanh toán, trạng thái. |
| `adminSales.verifyOrderRowStatus` | `k.admin_sales.verify_order_row_status(number, label)` | `number, label` | Kiểm tra trạng thái hiển thị trên dòng đơn hàng. |
| `adminSales.verifyOrdersEmpty` | `k.admin_sales.verify_orders_empty()` | — | Kiểm tra bảng trống "Không có đơn hàng nào" và "0 đơn hàng". |
| `adminSales.openOrderDetail` | `k.admin_sales.open_order_detail(number)` | `number` | Bấm "Xem chi tiết" trên dòng đơn hàng và chờ modal chi tiết. |
| `adminSales.closeOrderDetail` | `k.admin_sales.close_order_detail()` | — | Đóng modal chi tiết đơn (nút X). |
| `adminSales.verifyOrderDetail` | `k.admin_sales.verify_order_detail(d)` | `d` | Kiểm tra nội dung modal chi tiết đơn: người nhận, địa chỉ, thông tin, sản phẩm, tổng tiền, lịch sử. |
| `adminSales.verifyOrderStatusButtons` | `k.admin_sales.verify_order_status_buttons(labels)` | `labels` | Kiểm tra các nút chuyển trạng thái trong modal chi tiết ([] = không có khối cập nhật trạng thái). |
| `adminSales.clickOrderStatusButton` | `k.admin_sales.click_order_status_button(label)` | `label` | Bấm 1 nút chuyển trạng thái trong modal chi tiết đơn. |
| `adminSales.verifyOrderDetailStatus` | `k.admin_sales.verify_order_detail_status(label)` | `label` | Kiểm tra huy hiệu trạng thái trên đầu modal chi tiết. |
| `adminSales.verifyOrderProcessingWarning` | `k.admin_sales.verify_order_processing_warning(visible)` | `visible` | Kiểm tra hiện/ẩn cảnh báo "Lưu ý khi xử lý" (đơn đang giao/đã giao). |
| `adminSales.changeOrderPayment` | `k.admin_sales.change_order_payment(value)` | `value` | Chọn trạng thái thanh toán trong modal chi tiết (value: paid, unpaid, partially_paid). |
| `adminSales.verifyOrderDetailPayment` | `k.admin_sales.verify_order_detail_payment(label, editable)` | `label, editable` | Kiểm tra trạng thái thanh toán trên modal chi tiết và khối "Cập nhật thanh toán" có hiện không. |
| `adminSales.verifyOrderCancelAction` | `k.admin_sales.verify_order_cancel_action(number, visible)` | `number, visible` | Kiểm tra dòng đơn có/không có nút "Hủy đơn". |
| `adminSales.openCancelOrder` | `k.admin_sales.open_cancel_order(number)` | `number` | Bấm nút "Hủy đơn" trên dòng đơn hàng và chờ modal "Hủy đơn hàng". |
| `adminSales.fillCancelReason` | `k.admin_sales.fill_cancel_reason(reason)` | `reason` | Nhập lý do hủy đơn trong modal "Hủy đơn hàng". |
| `adminSales.verifyCancelNotes` | `k.admin_sales.verify_cancel_notes(notes)` | `notes` | Kiểm tra các ghi chú (hoàn tiền / hoàn điểm) trong modal hủy đơn. |
| `adminSales.goToPage` | `k.admin_sales.go_to_page(n)` | `n` | Bấm số trang trên thanh phân trang. |
| `adminSales.clickNextPage` | `k.admin_sales.click_next_page()` | — | Bấm nút trang sau (mũi tên phải / "Sau"). |
| `adminSales.verifyPaginationText` | `k.admin_sales.verify_pagination_text(text)` | `text` | Kiểm tra dòng chữ phân trang, vd: "Trang 1 / 3 — 45 đơn hàng". |
| `adminSales.verifyPageButton` | `k.admin_sales.verify_page_button(n, visible)` | `n, visible=True` | Kiểm tra có/không có nút số trang. |
| `adminSales.verifyFieldErrors` | `k.admin_sales.verify_field_errors(heading, errors)` | `heading, errors` | Kiểm tra danh sách lỗi dưới ô nhập trong modal có tiêu đề `heading` (đúng thứ tự, [] = không lỗi). |
| `adminSales.verifyModalText` | `k.admin_sales.verify_modal_text(heading, text)` | `heading, text` | Kiểm tra modal có tiêu đề `heading` chứa đoạn chữ. |
| `adminSales.verifyFieldPlaceholder` | `k.admin_sales.verify_field_placeholder(label, placeholder)` | `label, placeholder` | Kiểm tra placeholder của ô nhập theo label. |
| `adminSales.verifyCustomerRow` | `k.admin_sales.verify_customer_row(row)` | `row` | Kiểm tra dòng khách hàng: trạng thái, tổng chi tiêu, điểm. |
| `adminSales.verifyCustomerDetail` | `k.admin_sales.verify_customer_detail(d)` | `d` | Kiểm tra modal "Chi tiết khách hàng": tên, email, số liệu, thông tin, đơn gần đây. |
| `adminSales.verifyCustomerRecentOrderStatuses` | `k.admin_sales.verify_customer_recent_order_statuses(labels)` | `labels` | Kiểm tra nhãn trạng thái của các đơn gần đây trong modal "Chi tiết khách hàng" (đúng thứ tự). |
| `adminSales.verifyCustomerDeleteWarning` | `k.admin_sales.verify_customer_delete_warning(text)` | `text` | Kiểm tra cảnh báo "khách đã có đơn -> khóa thay vì xóa" trong modal xóa (null = không có). |
| `adminSales.verifyPersonRow` | `k.admin_sales.verify_person_row(name, visible)` | `name, visible=True` | Kiểm tra có/không có dòng (khách hàng / nhân viên) theo tên chính xác. |
| `adminSales.verifyEmployeesHeading` | `k.admin_sales.verify_employees_heading(text)` | `text` | Kiểm tra tiêu đề "Tài khoản nhân viên" trên trang nhân viên. |
| `adminSales.verifyEmployeeRole` | `k.admin_sales.verify_employee_role(name, label)` | `name, label` | Kiểm tra nhãn vai trò của nhân viên. |
| `adminSales.clickEmployeeAction` | `k.admin_sales.click_employee_action(name, action)` | `name, action` | Bấm nút trên dòng nhân viên: "Sửa", "Xóa" (icon không title) hoặc "Trạng thái" (nút gạt). |
| `adminSales.verifyEmployeeActive` | `k.admin_sales.verify_employee_active(name, active)` | `name, active` | Kiểm tra nút gạt trạng thái nhân viên đang bật (xanh) hay tắt (xám). |
| `adminSales.verifyEmployeeEmailNativeInvalid` | `k.admin_sales.verify_employee_email_native_invalid(editing)` | `editing=False` | Kiểm tra ô Email trong form nhân viên bị trình duyệt đánh dấu không hợp lệ (chặn submit). |

## adminMarketing

| Keyword | Python | Tham số | Mô tả |
|---|---|---|---|
| `adminMarketing.verifyColumns` | `k.admin_marketing.verify_columns(headers)` | `headers` | Kiểm tra bảng chính có đúng các cột theo thứ tự (đọc textContent, bỏ qua CSS viết hoa). |
| `adminMarketing.verifyRowCells` | `k.admin_marketing.verify_row_cells(row_text, cells)` | `row_text, cells` | Kiểm tra các ô của dòng chứa text theo tên cột, vd: {"Trạng thái": "Hết hạn"}. |
| `adminMarketing.verifyCellPattern` | `k.admin_marketing.verify_cell_pattern(row_index, column, pattern)` | `row_index, column, pattern` | Kiểm tra ô ở cột `column` của dòng thứ `rowIndex` (0 = đầu) khớp biểu thức chính quy. |
| `adminMarketing.verifySelectedOption` | `k.admin_marketing.verify_selected_option(label, text)` | `label, text` | Kiểm tra chữ hiển thị của option đang chọn trong select (theo label của ô). |
| `adminMarketing.verifyRowCount` | `k.admin_marketing.verify_row_count(count)` | `count` | Kiểm tra số dòng dữ liệu đang hiển thị trong bảng chính. |
| `adminMarketing.verifyRowsAtLeast` | `k.admin_marketing.verify_rows_at_least(min_count)` | `min_count` | Kiểm tra bảng có ít nhất `min` dòng dữ liệu thật (không phải dòng trạng thái rỗng). |
| `adminMarketing.verifyRowActions` | `k.admin_marketing.verify_row_actions(row_text, titles)` | `row_text, titles` | Kiểm tra dòng chứa text có đúng các nút hành động (theo title, đúng thứ tự). |
| `adminMarketing.verifyVisibleRows` | `k.admin_marketing.verify_visible_rows(visible, hidden)` | `visible, hidden=None` | Kiểm tra các dòng hiển thị/không hiển thị sau khi tìm kiếm hoặc lọc. |
| `adminMarketing.verifyModalText` | `k.admin_marketing.verify_modal_text(heading, texts)` | `heading, texts` | Kiểm tra modal có tiêu đề `heading` đang mở và chứa các đoạn text. |
| `adminMarketing.clickModalButton` | `k.admin_marketing.click_modal_button(heading, name)` | `heading, name` | Bấm nút theo tên bên trong modal có tiêu đề `heading`. |
| `adminMarketing.verifyListQuery` | `k.admin_marketing.verify_list_query(path_part, params)` | `path_part, params` | Kiểm tra request GET danh sách gần nhất (qua API giả lập) có các tham số; null = không gửi tham số đó. |
| `adminMarketing.mockPromotionList` | `k.admin_marketing.mock_promotion_list(promotions)` | `promotions` | Giả lập danh sách + chi tiết khuyến mãi; startOffset/endOffset đổi thành ngày so với hôm nay. |
| `adminMarketing.openPromotions` | `k.admin_marketing.open_promotions()` | — | Mở trang Khuyến mãi và chờ danh sách tải xong. |
| `adminMarketing.openCreatePromotion` | `k.admin_marketing.open_create_promotion()` | — | Bấm "Thêm khuyến mãi" và chờ modal tạo mới. |
| `adminMarketing.mockCouponList` | `k.admin_marketing.mock_coupon_list(coupons)` | `coupons` | Giả lập API GET danh sách mã giảm giá. |
| `adminMarketing.openCoupons` | `k.admin_marketing.open_coupons()` | — | Mở trang Mã giảm giá và chờ danh sách tải xong. |
| `adminMarketing.openCreateCoupon` | `k.admin_marketing.open_create_coupon()` | — | Bấm "Thêm mã" và chờ modal "Thêm mã giảm giá". |
| `adminMarketing.clickCouponEdit` | `k.admin_marketing.click_coupon_edit(code)` | `code` | Bấm nút sửa (icon không tên) trên dòng mã giảm giá. |
| `adminMarketing.clickCouponDelete` | `k.admin_marketing.click_coupon_delete(code)` | `code` | Bấm nút xóa (icon không tên) trên dòng mã giảm giá. |
| `adminMarketing.toggleCoupon` | `k.admin_marketing.toggle_coupon(code, column)` | `code, column` | Bấm nút bật/tắt ở cột "Công khai" hoặc "Trạng thái" của mã giảm giá. |
| `adminMarketing.verifyCouponToggle` | `k.admin_marketing.verify_coupon_toggle(code, column, on)` | `code, column, on` | Kiểm tra nút bật/tắt ở cột của mã giảm giá đang bật (xanh) hay tắt (xám). |
| `adminMarketing.mockReviewList` | `k.admin_marketing.mock_review_list(reviews)` | `reviews` | Giả lập API GET đánh giá: lọc theo tham số status/rating như server. |
| `adminMarketing.openReviews` | `k.admin_marketing.open_reviews()` | — | Mở trang Đánh giá và chờ danh sách tải xong. |
| `adminMarketing.filterReviewStatus` | `k.admin_marketing.filter_review_status(value)` | `value` | Chọn bộ lọc trạng thái đánh giá (all, pending, approved, hidden). |
| `adminMarketing.filterReviewRating` | `k.admin_marketing.filter_review_rating(value)` | `value` | Chọn bộ lọc số sao (all, 5, 4, 3, 2, 1). |
| `adminMarketing.mockBlogList` | `k.admin_marketing.mock_blog_list(posts)` | `posts` | Giả lập API GET danh sách bài viết. |
| `adminMarketing.openBlog` | `k.admin_marketing.open_blog()` | — | Mở trang Bài viết và chờ danh sách tải xong. |
| `adminMarketing.openCreateBlog` | `k.admin_marketing.open_create_blog()` | — | Bấm "Thêm bài viết" và chờ modal tạo mới. |
| `adminMarketing.setBlogImage` | `k.admin_marketing.set_blog_image(url, error)` | `url, error=''` | Nhập URL ảnh bài viết và kiểm tra ảnh xem trước hoặc thông báo lỗi ảnh. |
| `adminMarketing.mockContactList` | `k.admin_marketing.mock_contact_list(contacts)` | `contacts` | Giả lập API GET liên hệ: lọc theo tham số status như server. |
| `adminMarketing.openContacts` | `k.admin_marketing.open_contacts()` | — | Mở trang Liên hệ và chờ danh sách tải xong. |
| `adminMarketing.filterContactStatus` | `k.admin_marketing.filter_contact_status(value)` | `value` | Chọn bộ lọc trạng thái liên hệ (all, pending, processed). |

## adminOps

| Keyword | Python | Tham số | Mô tả |
|---|---|---|---|
| `adminOps.verifyColumns` | `k.admin_ops.verify_columns(headers)` | `headers` | Kiểm tra bảng chính có đúng các cột theo thứ tự (đọc textContent, bỏ qua CSS viết hoa). |
| `adminOps.verifyRowCells` | `k.admin_ops.verify_row_cells(row_text, cells)` | `row_text, cells` | Kiểm tra các ô của dòng chứa text theo tên cột, vd: {"Tồn kho": "3"}. |
| `adminOps.verifyRowCount` | `k.admin_ops.verify_row_count(count)` | `count` | Kiểm tra số dòng dữ liệu đang hiển thị trong bảng chính. |
| `adminOps.verifyRowsAtLeast` | `k.admin_ops.verify_rows_at_least(minimum)` | `minimum` | Kiểm tra bảng có ít nhất `min` dòng dữ liệu thật (không phải dòng trạng thái rỗng). |
| `adminOps.verifyRowActions` | `k.admin_ops.verify_row_actions(row_text, titles)` | `row_text, titles` | Kiểm tra dòng chứa text có đúng các nút hành động (theo title, đúng thứ tự). |
| `adminOps.verifyVisibleRows` | `k.admin_ops.verify_visible_rows(visible, hidden)` | `visible, hidden=None` | Kiểm tra các dòng hiển thị/không hiển thị sau khi tìm kiếm hoặc lọc. |
| `adminOps.verifyModalText` | `k.admin_ops.verify_modal_text(heading, texts)` | `heading, texts` | Kiểm tra modal có tiêu đề `heading` đang mở và chứa các đoạn text. |
| `adminOps.clickModalButton` | `k.admin_ops.click_modal_button(heading, name)` | `heading, name` | Bấm nút theo tên bên trong modal có tiêu đề `heading`. |
| `adminOps.verifyStatCards` | `k.admin_ops.verify_stat_cards(cards)` | `cards` | Kiểm tra các thẻ thống kê (nhãn -> giá trị), vd: {"Tổng đơn": "3"}. |
| `adminOps.verifyListQuery` | `k.admin_ops.verify_list_query(path_part, params)` | `path_part, params` | Kiểm tra request GET gần nhất (qua API giả lập) có các tham số; null = không gửi tham số đó. |
| `adminOps.mockWarehouse` | `k.admin_ops.mock_warehouse(data)` | `data` | Giả lập API kho hàng: lọc sản phẩm theo tham số filter (all, low, out) như server. |
| `adminOps.openWarehouse` | `k.admin_ops.open_warehouse()` | — | Mở trang Kho hàng và chờ bảng tải xong. |
| `adminOps.selectWarehouseTab` | `k.admin_ops.select_warehouse_tab(label)` | `label` | Bấm tab lọc kho ("Tất cả", "Sắp hết", "Hết hàng") và chờ bảng tải lại. |
| `adminOps.verifyWarehouseTabBadge` | `k.admin_ops.verify_warehouse_tab_badge(label, count)` | `label, count` | Kiểm tra số đếm trên tab kho; null = không hiển thị số. |
| `adminOps.verifyWarehouseStatsMatchList` | `k.admin_ops.verify_warehouse_stats_match_list()` | — | Kiểm tra thẻ "Tổng sản phẩm" bằng số dòng của tab "Tất cả" (dữ liệu thật). |
| `adminOps.mockImportData` | `k.admin_ops.mock_import_data(data)` | `data` | Giả lập toàn bộ API GET của trang Nhập hàng (đơn nhập lọc theo status/supplier_id/search, NCC, kho, sản phẩm, chi tiết). |
| `adminOps.openImport` | `k.admin_ops.open_import()` | — | Mở trang Nhập hàng và chờ bảng tải xong. |
| `adminOps.filterImportStatus` | `k.admin_ops.filter_import_status(value)` | `value` | Lọc đơn nhập theo trạng thái (draft, processing, partial_received, received, cancelled; rỗng = tất cả). |
| `adminOps.filterImportSupplier` | `k.admin_ops.filter_import_supplier(name)` | `name` | Lọc đơn nhập theo tên nhà cung cấp (rỗng = tất cả). |
| `adminOps.openCreateImport` | `k.admin_ops.open_create_import()` | — | Bấm "Tạo đơn nhập hàng" và chờ modal tạo đơn. |
| `adminOps.addImportItemRow` | `k.admin_ops.add_import_item_row()` | — | Bấm "Thêm sản phẩm" để thêm 1 dòng sản phẩm nhập. |
| `adminOps.fillImportItem` | `k.admin_ops.fill_import_item(index, item)` | `index, item` | Điền dòng sản phẩm nhập thứ `index` (0 = dòng đầu): sản phẩm, biến thể, số lượng, đơn giá, ghi chú. |
| `adminOps.verifyImportTotals` | `k.admin_ops.verify_import_totals(index, line_total, grand_total)` | `index, line_total, grand_total` | Kiểm tra thành tiền dòng `index` và "Tổng tiền nhập" trong modal tạo đơn. |
| `adminOps.setReceiveQuantities` | `k.admin_ops.set_receive_quantities(quantities)` | `quantities` | Nhập "SL thực nhận" cho từng dòng trong modal Nhận hàng. |
| `adminOps.mockReportsOverview` | `k.admin_ops.mock_reports_overview(overview)` | `overview` | Giả lập API tổng quan báo cáo (ghi lại tham số period/start_date/end_date). |
| `adminOps.openReports` | `k.admin_ops.open_reports()` | — | Mở trang Báo cáo và chờ thẻ tổng quan tải xong. |
| `adminOps.selectReportPeriod` | `k.admin_ops.select_report_period(value)` | `value` | Chọn kỳ báo cáo theo value (today, last7days, last30days, thisMonth, custom). |
| `adminOps.applyCustomRange` | `k.admin_ops.apply_custom_range(start, end)` | `start, end` | Ở kỳ "Tùy chọn": nhập từ ngày, đến ngày (YYYY-MM-DD) và bấm "Lọc". |
| `adminOps.verifyCustomRangeDefaults` | `k.admin_ops.verify_custom_range_defaults()` | — | Kiểm tra kỳ "Tùy chọn" mặc định: từ ngày 1 tháng này đến hôm nay (giờ VN). |
| `adminOps.verifyReportSection` | `k.admin_ops.verify_report_section(heading, rows, first_row)` | `heading, rows, first_row` | Kiểm tra bảng trong khối báo cáo có số dòng và dòng đầu chứa các text. |
| `adminOps.verifyReportSectionText` | `k.admin_ops.verify_report_section_text(heading, texts)` | `heading, texts` | Kiểm tra khối báo cáo (theo tiêu đề h2) chứa các đoạn text. |
| `adminOps.exportReport` | `k.admin_ops.export_report(file_pattern, lines)` | `file_pattern, lines` | Bấm "Xuất báo cáo", kiểm tra tên file CSV (regex), BOM UTF-8 và các dòng nội dung. |
| `adminOps.mockSettings` | `k.admin_ops.mock_settings(settings)` | `settings` | Giả lập API GET cài đặt website. |
| `adminOps.openSettings` | `k.admin_ops.open_settings()` | — | Mở trang Cài đặt và chờ dữ liệu tải xong. |
| `adminOps.openSettingsTab` | `k.admin_ops.open_settings_tab(label)` | `label` | Bấm 1 tab cài đặt, vd: "Bán hàng". |
| `adminOps.verifySettingsFields` | `k.admin_ops.verify_settings_fields(labels)` | `labels` | Kiểm tra tab đang mở có đúng các nhãn ô nhập (theo thứ tự). |
| `adminOps.verifyCheckboxes` | `k.admin_ops.verify_checkboxes(states)` | `states` | Kiểm tra trạng thái các checkbox theo nhãn, vd: {"Cho phép COD": true}. |
| `adminOps.saveSettings` | `k.admin_ops.save_settings()` | — | Bấm "Lưu cài đặt". |

