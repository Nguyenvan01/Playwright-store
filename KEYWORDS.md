# Danh mục Keyword

> File tự sinh bởi `npm run docs:keywords` — đừng sửa tay.

Dùng trong code: `await k.<nhóm>.<keyword>(...)` · Dùng trong kịch bản JSON: `{ "keyword": "<nhóm>.<keyword>", "arg": ... }` hoặc `"args": [...]`.

## common

| Keyword | Tham số | Mô tả |
|---|---|---|
| `common.goto` | `path: string` | Mở 1 đường dẫn bất kỳ, vd: "/about". |
| `common.reload` | — | Tải lại trang hiện tại. |
| `common.verifyUrl` | `path: string` | Kiểm tra URL hiện tại đúng đường dẫn, vd: "/profile". |
| `common.verifyUrlMatches` | `pattern: string` | Kiểm tra URL khớp biểu thức chính quy, vd: "/product/.+". |
| `common.verifyToast` | `text: string` | Kiểm tra có toast chứa nội dung. |
| `common.verifyTextVisible` | `text: string` | Kiểm tra 1 đoạn chữ đang hiển thị trên trang. |
| `common.verifyLayoutLoaded` | — | Kiểm tra trang có header và footer (trang khách hàng tải thành công). |
| `common.verifyNoPageErrors` | — | Kiểm tra không phát sinh lỗi JavaScript nào kể từ đầu test. |
| `common.verifyNoHorizontalOverflow` | — | Kiểm tra trang không bị tràn ngang (responsive). |
| `common.mockApi` | `urlPattern: string, response: { status?: number; json: unknown }` | Giả lập 1 API theo mẫu URL (glob của Playwright), trả về status + json. |
| `common.mockWrite` | `method: string, urlPattern: string, json: unknown = { success: true }, status = 200` | Giả lập API ghi (POST/PUT/DELETE) theo mẫu URL, trả về json; lưu lại request để kiểm tra. |
| `common.verifyRequest` | `method: string, pathPart: string, expectedBody?: Record<string, unknown>` | Kiểm tra đã gửi request (method + đường dẫn chứa pathPart), body chứa các trường mong đợi. |
| `common.mockGet` | `urlPattern: string, json: unknown, status = 200` | Giả lập API GET (dữ liệu mẫu cho trang cần data, vd: danh sách đơn hàng). Chỉ chặn method GET. |
| `common.acceptNextDialog` | `accept = true` | Tự động bấm OK (true) hoặc Hủy (false) cho hộp thoại window.confirm/alert tiếp theo. |
| `common.verifyNoRequest` | `method: string, pathPart: string` | Kiểm tra KHÔNG có request ghi nào (method + đường dẫn) được gửi. |

## auth

| Keyword | Tham số | Mô tả |
|---|---|---|
| `auth.openLogin` | — | Mở trang đăng nhập khách hàng. |
| `auth.login` | `identifier: string, password: string` | Nhập email/SĐT + mật khẩu và bấm ĐĂNG NHẬP. |
| `auth.loginAsCustomer` | — | Đăng nhập bằng tài khoản khách hàng test trong .env và chờ vào trang hồ sơ. |
| `auth.restoreSession` | `role: Role` | Đăng nhập sẵn qua API (không qua UI) - phải gọi TRƯỚC lần mở trang đầu tiên. |
| `auth.openRegisterForm` | — | Chuyển form sang chế độ Đăng ký. |
| `auth.submitRegisterForm` | `form: RegisterForm` | Điền form đăng ký và bấm TẠO TÀI KHOẢN (form phải đang mở). |
| `auth.verifyFieldErrors` | `messages: string[]` | Kiểm tra các thông báo lỗi dưới từng ô nhập. |
| `auth.verifyGeneralError` | `message: string` | Kiểm tra thông báo lỗi chung (lỗi từ server) trên form đăng nhập/đăng ký. |
| `auth.loginExpectingError` | `identifier: string, password: string, message: string` | Đăng nhập sai và kiểm tra thông báo lỗi vẫn hiển thị (trang không bị reload). |
| `auth.mockLoginSuccess` | `user: Record<string, unknown>` | Giả lập API đăng nhập thành công với user cho trước (kèm các API trang hồ sơ). |
| `auth.mockRegisterError` | `status: number, message: string` | Giả lập API đăng ký trả lỗi (status + message). |
| `auth.togglePassword` | `expectVisible: boolean` | Bấm nút hiện/ẩn mật khẩu và kiểm tra trạng thái hiển thị. |
| `auth.verifyLoggedInAs` | `email: string` | Kiểm tra menu tài khoản trên header hiển thị đúng email. |
| `auth.logout` | — | Đăng xuất qua menu tài khoản trên header. |
| `auth.verifyLoggedOut` | — | Kiểm tra đã đăng xuất: về trang chủ, có link đăng nhập, token bị xóa. |
| `auth.verifyStoredToken` | `expected: string` | Kiểm tra token khách hàng trong localStorage bằng giá trị mong đợi. |

## catalog

| Keyword | Tham số | Mô tả |
|---|---|---|
| `catalog.openHome` | — | Mở trang chủ và chờ danh sách sản phẩm. |
| `catalog.verifyHomeLoaded` | — | Kiểm tra trang chủ: logo, ô tìm kiếm, khối SẢN PHẨM MỚI, footer. |
| `catalog.clickLogo` | — | Bấm logo trên header. |
| `catalog.verifyMenuLink` | `nav: string, path: string` | Kiểm tra link danh mục trên menu trỏ đúng đường dẫn. |
| `catalog.openCategoryFromMenu` | `nav: string` | Bấm 1 danh mục trên menu header, vd: "NAM". |
| `catalog.openCategoryFromMobileMenu` | `nav: string` | Mở menu mobile (hamburger) và bấm 1 danh mục. |
| `catalog.verifyCategoryPage` | `path: string, heading: string` | Kiểm tra đang ở trang danh mục (URL + tiêu đề) và có sản phẩm hoặc thông báo rỗng. |
| `catalog.openFirstProductInList` | — | Bấm sản phẩm đầu tiên trong danh sách đang hiển thị và chờ trang chi tiết. |
| `catalog.openProduct` | `slug: string` | Mở trang chi tiết sản phẩm theo slug. |
| `catalog.verifyProductTitle` | `name: string` | Kiểm tra tên sản phẩm trên trang chi tiết. |
| `catalog.verifySizeCount` | `count: number` | Kiểm tra số nút size trên trang chi tiết. |
| `catalog.selectSize` | `label?: string` | Chọn size (để trống = size còn hàng đầu tiên). |
| `catalog.verifySizeWarning` | `visible: boolean` | Kiểm tra cảnh báo "Vui lòng chọn kích cỡ" hiện/ẩn. |
| `catalog.addToCart` | `size?: string` | Chọn size (nếu có) rồi bấm "Thêm vào giỏ hàng". |
| `catalog.verifyProductNotFound` | — | Kiểm tra trang "Không tìm thấy sản phẩm". |
| `catalog.typeSearch` | `keyword: string` | Gõ từ khóa vào ô tìm kiếm trên header (chưa Enter). |
| `catalog.verifySearchSuggestion` | `name: string` | Kiểm tra dropdown gợi ý có sản phẩm. |
| `catalog.clickSearchSuggestion` | `name: string` | Bấm 1 sản phẩm trong dropdown gợi ý. |
| `catalog.verifyNoSearchSuggestion` | — | Kiểm tra dropdown báo không có kết quả. |
| `catalog.submitSearch` | `keyword: string` | Gõ từ khóa vào ô tìm kiếm và nhấn Enter. |
| `catalog.openSearchPage` | `keyword: string` | Mở thẳng trang kết quả /search?q=... |
| `catalog.verifySearchResults` | `heading: string` | Kiểm tra trang kết quả tìm kiếm có tiêu đề và ít nhất 1 sản phẩm. |
| `catalog.verifyNoSearchResults` | — | Kiểm tra trang kết quả tìm kiếm rỗng. |

## listing

| Keyword | Tham số | Mô tả |
|---|---|---|
| `listing.openListing` | `path: string` | Mở trang danh sách (vd: "/nam") và chờ tải xong (có sản phẩm hoặc thông báo rỗng). |
| `listing.verifyListingHeader` | `heading: string, breadcrumb: string, description: string` | Kiểm tra đầu trang danh sách: breadcrumb "Trang chủ > {mục}", tiêu đề h1, đoạn mô tả. |
| `listing.verifyCountMatchesCards` | — | Kiểm tra dòng "Hiển thị n trên t sản phẩm": n = số thẻ đang hiển thị và n <= t. |
| `listing.verifyCountText` | `text: string` | Kiểm tra chính xác dòng "Hiển thị n trên t sản phẩm". |
| `listing.verifySortOptions` | `options: string[], selected: string` | Kiểm tra các lựa chọn sắp xếp (theo thứ tự) và lựa chọn đang được chọn. |
| `listing.sortBy` | `option: string` | Chọn kiểu sắp xếp theo nhãn, vd: "Giá: Thấp → Cao". |
| `listing.verifyPricesSorted` | `order: 'asc' \| 'desc'` | Kiểm tra giá trên các thẻ sản phẩm đã sắp xếp: "asc" tăng dần, "desc" giảm dần. |
| `listing.verifyCategoryOptions` | `names: string[]` | Kiểm tra các nút danh mục đang hiển thị trong bộ lọc (theo thứ tự). |
| `listing.showMoreCategories` | — | Bấm "Xem thêm +" trong nhóm danh mục để hiện các danh mục còn lại. |
| `listing.selectCategory` | `name: string` | Bấm 1 danh mục trong bộ lọc và kiểm tra nút được đánh dấu chọn. |
| `listing.verifySizeOptions` | `sizes: string[]` | Kiểm tra các nút size trong bộ lọc "Kích cỡ". |
| `listing.selectSizeFilter` | `size: string` | Bấm 1 size trong bộ lọc "Kích cỡ". |
| `listing.verifyColorOptions` | `colors: string[]` | Kiểm tra các ô màu trong bộ lọc "Màu sắc" (theo thuộc tính title). |
| `listing.selectColorFilter` | `color: string` | Bấm 1 màu trong bộ lọc "Màu sắc" (theo title) và kiểm tra có dấu tích. |
| `listing.verifyPriceInputs` | `from: string, to: string` | Kiểm tra giá trị mặc định 2 ô khoảng giá "Từ" / "Đến". |
| `listing.setPriceRange` | `from: string, to: string` | Nhập khoảng giá "Từ" - "Đến" (vd: "300000", "600000"); bộ lọc áp dụng khi rời ô nhập. |
| `listing.verifyPricesWithin` | `min: number, max: number` | Kiểm tra mọi giá đang hiển thị nằm trong khoảng [min, max]. |
| `listing.selectDiscount` | `label: string` | Tick 1 mức "Phần trăm giảm" (tự mở nhóm lọc nếu đang đóng), vd: "Giảm 30%". |
| `listing.verifyDiscountAtLeast` | `percent: number` | Kiểm tra mọi thẻ đang hiển thị có nhãn giảm giá >= phần trăm cho trước. |
| `listing.verifyListRequest` | `params: Record<string, string>` | Kiểm tra đã gọi API danh sách sản phẩm với các tham số query, vd: {"min_price":"300000"}. |
| `listing.verifyProductsShown` | — | Kiểm tra danh sách có ít nhất 1 sản phẩm và dòng "Hiển thị n trên t" với n > 0. |
| `listing.verifyEmptyListing` | `text: string` | Kiểm tra trạng thái rỗng của trang danh sách (thông báo + "Hiển thị 0 trên 0 sản phẩm"). |
| `listing.goToPage` | `n: number` | Bấm số trang ở phân trang. |
| `listing.clickNextPage` | — | Bấm nút trang sau (icon "navigate_next"). |
| `listing.clickLoadMore` | — | Bấm nút "Xem thêm sản phẩm". |
| `listing.addFirstCardToCart` | — | Rê chuột vào thẻ sản phẩm đầu tiên và bấm "Thêm vào giỏ" ở lớp phủ. |
| `listing.viewFirstCardDetail` | — | Rê chuột vào thẻ sản phẩm đầu tiên và bấm "Xem chi tiết" ở lớp phủ. |
| `listing.clickFirstCardFavorite` | — | Bấm nút tim (yêu thích) trên thẻ sản phẩm đầu tiên. |
| `listing.verifyOpenedLastCard` | — | Kiểm tra đã chuyển tới trang chi tiết của thẻ sản phẩm vừa thao tác. |
| `listing.openSearchResults` | `query: string` | Mở trang /search với query string (vd: "?category=vay", "" = tất cả) và chờ tải xong. |
| `listing.verifySearchTitle` | `heading: string` | Kiểm tra tiêu đề h1 của trang /search. |
| `listing.verifySearchBreadcrumbs` | `items: string[]` | Kiểm tra breadcrumb trang /search theo thứ tự (bỏ icon). |
| `listing.verifySearchBreadcrumbLink` | `name: string, href: string` | Kiểm tra 1 mục breadcrumb là link trỏ đúng đường dẫn. |
| `listing.verifySearchSubtitleMatches` | — | Kiểm tra dòng "{tổng} sản phẩm" và số thẻ trên trang (tối đa 12/trang). |
| `listing.verifySearchChip` | `text: string, closeHref: string` | Kiểm tra chip bộ lọc đang áp dụng và link nút đóng (close). |
| `listing.closeSearchChip` | `text: string` | Bấm nút đóng (close) trên 1 chip bộ lọc. |
| `listing.verifySearchSortOptions` | `options: string[]` | Kiểm tra các lựa chọn sắp xếp của trang /search. |
| `listing.sortSearchBy` | `option: string` | Chọn kiểu sắp xếp trên trang /search theo nhãn. |
| `listing.verifySearchPricesSorted` | `order: 'asc' \| 'desc'` | Kiểm tra giá trên trang /search đã sắp xếp ("asc"/"desc"). |
| `listing.verifySearchEmpty` | `hint: string` | Kiểm tra trạng thái rỗng của /search: tiêu đề, gợi ý và nút "Xem tất cả sản phẩm". |
| `listing.clickViewAllProducts` | — | Bấm "Xem tất cả sản phẩm" ở trạng thái rỗng. |
| `listing.verifySearchError` | `message: string` | Kiểm tra trạng thái lỗi của /search: "Đã xảy ra lỗi" + thông báo + nút "Thử lại". |
| `listing.goToSearchPage` | `n: number` | Bấm số trang trên phân trang của /search. |
| `listing.clickSearchNextPage` | — | Bấm nút trang sau (chevron_right) trên /search. |
| `listing.verifySearchActivePage` | `n: number` | Kiểm tra trang hiện tại trên phân trang /search (nút được tô đỏ) và nút trang trước bật/tắt. |
| `listing.typeHeaderSearchExpectingStatus` | `keyword: string, status: number` | Gõ từ khóa vào ô tìm kiếm header và chờ API gợi ý (/api/products/search) trả về đúng status. |
| `listing.verifyHeaderSuggestionsHidden` | — | Kiểm tra dropdown gợi ý tìm kiếm trên header KHÔNG hiển thị. |

## product

| Keyword | Tham số | Mô tả |
|---|---|---|
| `product.mockProductDetail` | `slug: string, response: { success: boolean; data: Record<string, unknown> }` | Mock GET /api/products/{slug} bằng dữ liệu cho trước (shape { success, data }). |
| `product.openProductPage` | `slug: string` | Mở trang chi tiết /product/{slug} và chờ tên sản phẩm hiển thị. |
| `product.verifyBreadcrumb` | `title: string` | Kiểm tra breadcrumb "Trang chủ \| {tên sản phẩm}". |
| `product.clickBreadcrumbHome` | — | Bấm "Trang chủ" trên breadcrumb. |
| `product.verifyGallery` | `count: number` | Kiểm tra bộ ảnh: số thumbnail ("Thumbnail 1..n") và bộ đếm "1/n". |
| `product.clickThumbnail` | `n: number` | Bấm thumbnail thứ n (đánh số từ 1). |
| `product.clickNextImage` | — | Bấm nút mũi tên chuyển ảnh tiếp theo trên ảnh chính. |
| `product.verifyCurrentImage` | `n: number, total: number` | Kiểm tra ảnh chính đang là ảnh thứ n: bộ đếm "n/tổng", thumbnail n được viền, cùng nguồn ảnh. |
| `product.verifyNextImageHidden` | — | Kiểm tra nút ảnh tiếp theo bị ẩn (đang ở ảnh cuối). |
| `product.verifyColorOptions` | `colors: string[]` | Kiểm tra các ô màu (theo title) và màu đang chọn mặc định (màu đầu tiên). |
| `product.selectColor` | `color: string` | Chọn 1 màu (theo title) và kiểm tra tên màu hiển thị cạnh "Màu sắc:". |
| `product.verifySku` | `sku: string` | Kiểm tra dòng "SKU: ..." và nút "Copy". |
| `product.copySku` | — | Bấm "Copy" mã SKU. |
| `product.verifySkuCopied` | `sku: string` | Kiểm tra đã copy SKU: nút đổi thành "Đã copy", clipboard chứa SKU, sau 2 giây trở lại "Copy". |
| `product.verifyPrice` | `price: string` | Kiểm tra giá bán hiển thị đúng định dạng, vd: "449.000đ". |
| `product.verifyComparePrice` | `comparePrice: string, discount: string` | Kiểm tra giá gốc gạch ngang và nhãn phần trăm giảm, vd: "599.000đ", "-25%". |
| `product.verifyDiscountBadge` | `discount: string` | Kiểm tra nhãn phần trăm giảm cạnh giá, vd: "-25%". |
| `product.toggleAccordion` | `title: string` | Bấm tiêu đề 1 accordion: "Mô tả" / "Chất liệu" / "Hướng dẫn sử dụng". |
| `product.verifyOpenAccordion` | `title: string, all: string[]` | Kiểm tra chỉ đúng 1 accordion đang mở (title), các accordion còn lại đóng; title rỗng = tất cả đóng. |
| `product.verifyAccordionContent` | `title: string, lines: string[]` | Kiểm tra nội dung trong 1 accordion (các dòng/đoạn). |
| `product.verifyServices` | `services: { title: string; desc: string }[]` | Kiểm tra danh sách dịch vụ dưới nút mua (tiêu đề + mô tả). |
| `product.verifyServiceText` | `title: string, desc: string` | Kiểm tra mô tả của 1 dịch vụ, vd: "Miễn phí giao hàng" -> "Với đơn hàng trên 500.000đ." |
| `product.verifyRelatedProduct` | `name: string` | Kiểm tra khối "SẢN PHẨM CÙNG PHONG CÁCH" có sản phẩm theo tên. |
| `product.openRelatedProduct` | `name: string` | Bấm 1 sản phẩm trong "SẢN PHẨM CÙNG PHONG CÁCH". |
| `product.verifyReviewLoginPrompt` | — | Kiểm tra khách chưa đăng nhập: chỉ thấy lời nhắc đăng nhập để đánh giá. |
| `product.clickReviewLogin` | — | Bấm "Đăng nhập" trong khối đánh giá. |
| `product.openReviewForm` | — | Bấm "Viết đánh giá" và kiểm tra form hiện ra. |
| `product.fillReview` | `stars: number, content: string` | Chọn số sao (0 = bỏ qua) và nhập nội dung đánh giá. |
| `product.submitReview` | — | Bấm "Gửi đánh giá". |
| `product.verifyReviewErrors` | `messages: string[]` | Kiểm tra các thông báo lỗi dưới form đánh giá (đúng và đủ). |
| `product.cancelReview` | — | Bấm "Hủy" trên form đánh giá. |
| `product.closeReviewForm` | — | Bấm nút "×" đóng form đánh giá. |
| `product.verifyReviewFormClosed` | — | Kiểm tra form đánh giá đã đóng và nút "Viết đánh giá" hiện lại. |

## content

| Keyword | Tham số | Mô tả |
|---|---|---|
| `content.mockHomeData` | `response: { success: boolean; data: Record<string, any> }` | Mock GET /api/home bằng dữ liệu cho trước (voucher có "expiresInDays" được đổi thành ngày hết hạn tính từ hôm nay). |
| `content.openHomePage` | — | Mở trang chủ và chờ khối SẢN PHẨM MỚI hiển thị (không yêu cầu có sản phẩm). |
| `content.verifyHomeSections` | `titles: string[]` | Kiểm tra trang chủ có đủ các khối theo tiêu đề h2, đúng thứ tự. |
| `content.verifyBannerSlideCount` | `count: number` | Kiểm tra số slide banner và số chấm điều hướng. |
| `content.verifyActiveBannerSlide` | `slide: number` | Kiểm tra slide banner đang hiển thị (đánh số từ 1). |
| `content.clickBannerArrow` | `direction: 'next' \| 'prev'` | Bấm nút mũi tên banner: "next" hoặc "prev". |
| `content.clickBannerDot` | `slide: number` | Bấm chấm điều hướng banner thứ n (đánh số từ 1). |
| `content.freezeClock` | — | Cố định đồng hồ trình duyệt (banner không tự chuyển slide) - gọi TRƯỚC khi mở trang. |
| `content.verifyBannerAutoplay` | `toSlide: number` | Cho đồng hồ (đã cố định bằng freezeClock) chạy 4 giây và kiểm tra banner tự chuyển sang slide kế tiếp. |
| `content.verifyBannerSlideLinks` | `hrefs: string[]` | Kiểm tra link (href) của từng slide banner theo thứ tự. |
| `content.verifyBannerOverlay` | `slide: number, title: string, href: string` | Kiểm tra chữ đè trên slide banner (đánh số từ 1): tiêu đề + nút "Khám phá ngay" trỏ đúng link. |
| `content.verifyVoucher` | `voucher: VoucherExpect` | Kiểm tra 1 thẻ voucher trong khối "ƯU ĐÃI NỔI BẬT" (tiêu đề, mô tả, điều kiện, hạn dùng). |
| `content.useVoucher` | `title: string` | Bấm "Dùng mã" của 1 voucher. |
| `content.verifyPendingVoucher` | `code: string` | Kiểm tra mã voucher đã được lưu tạm vào sessionStorage (pendingVoucher). |
| `content.verifyNoVoucherSection` | — | Kiểm tra khối "ƯU ĐÃI NỔI BẬT" bị ẩn (không có voucher). |
| `content.verifyNewProductTabs` | `tabs: string[]` | Kiểm tra các tab của khối SẢN PHẨM MỚI, tab đầu đang được chọn. |
| `content.selectNewProductTab` | `tab: string` | Bấm 1 tab trong khối SẢN PHẨM MỚI. |
| `content.verifyNewProductsFiltered` | `tab: string, visible: string, hidden: string` | Kiểm tra tab được chọn và danh sách SẢN PHẨM MỚI đã lọc: có sản phẩm visible, không còn sản phẩm hidden. |
| `content.verifyNewProductCount` | `count: number` | Kiểm tra số thẻ sản phẩm trong carousel SẢN PHẨM MỚI. |
| `content.scrollNewProducts` | `direction: 'next' \| 'prev'` | Bấm mũi tên carousel SẢN PHẨM MỚI ("next"/"prev") và kiểm tra danh sách cuộn đúng chiều. |
| `content.verifyPromoBlock` | `title: string, description: string, cardCount: number` | Kiểm tra khối HOMEWEAR/T-SHIRT/VÁY: mô tả và số thẻ sản phẩm (tối đa 4). |
| `content.verifyCollection` | `title: string, ctaText: string, href: string` | Kiểm tra 1 ô bộ sưu tập: tiêu đề, chữ trên nút CTA và link. |
| `content.verifyCLive` | `texts: string[]` | Kiểm tra khối C-LIVE: tiêu đề, ảnh và các đoạn chữ. |
| `content.verifyHomeNews` | `featuredTitle: string, secondaryCount: number` | Kiểm tra khối "Tin tức thời trang": bài nổi bật + số bài phụ + nút "Xem thêm". |
| `content.verifyHomeNewsLink` | `title: string, slug: string` | Kiểm tra link bài nổi bật trong khối Tin tức trỏ tới /blog/{slug}. |
| `content.verifyHomeNewsEmpty` | — | Kiểm tra khối Tin tức hiển thị trạng thái rỗng và ẩn nút "Xem thêm". |
| `content.clickHomeNewsSeeMore` | — | Bấm "Xem thêm" của khối Tin tức thời trang. |
| `content.clickHomeLink` | `link: string, section?: string` | Bấm 1 link trên trang chủ theo tên; section = tiêu đề khối chứa link (để trống = khối SẢN PHẨM MỚI). |
| `content.verifyPageRendered` | — | Kiểm tra trang đích đã render nội dung (có header, footer) - không phải trang trắng. |
| `content.quickAddToCart` | `productName: string` | Bấm icon thêm nhanh vào giỏ trên thẻ sản phẩm (ProductCard) theo tên. |
| `content.verifyStoredCartItemHasSize` | `productName: string` | Kiểm tra sản phẩm trong giỏ (localStorage) đã có size được chọn. |
| `content.subscribeNewsletter` | `email: string` | Nhập email vào khối "Đăng ký nhận tin" và bấm "Đăng ký". |
| `content.verifyNewsletterThanks` | — | Kiểm tra hiện "Cảm ơn bạn đã đăng ký!" rồi form tự hiện lại sau khoảng 4 giây. |
| `content.verifyNewsletterBlocked` | `validity: string` | Kiểm tra trình duyệt chặn gửi form nhận tin (HTML5 validation), vd: "valueMissing", "typeMismatch". |
| `content.verifyFooterContent` | `headings: string[], links: string[]` | Kiểm tra footer: các tiêu đề cột, link và dòng bản quyền. |
| `content.verifyFooterLink` | `name: string, href: string` | Kiểm tra 1 link footer trỏ đúng đường dẫn. |
| `content.verifyFooterHasLinkTo` | `href: string` | Kiểm tra footer có ít nhất 1 link trỏ tới đường dẫn. |
| `content.mockBlogData` | `response: { success: boolean; news: BlogArticle[] }` | Mock API blog: danh sách GET /api/news và chi tiết GET /api/news/:slug (404 nếu slug không có trong danh sách). |
| `content.openBlog` | — | Mở trang /blog và chờ danh sách bài viết tải xong. |
| `content.verifyBlogLoaded` | — | Kiểm tra trang Blog: tiêu đề, mô tả và có ít nhất 1 bài viết. |
| `content.verifyBlogPills` | `pills: string[]` | Kiểm tra các nút danh mục (pill) trên trang Blog theo thứ tự. |
| `content.filterBlogByCategory` | `category: string` | Bấm 1 danh mục (pill) trên trang Blog. |
| `content.verifyBlogTitles` | `titles: string[]` | Kiểm tra danh sách bài viết đang hiển thị đúng các tiêu đề (theo thứ tự). |
| `content.verifyBlogCategoryOfCards` | `category: string` | Kiểm tra mọi bài viết đang hiển thị đều thuộc danh mục. |
| `content.verifyBlogEmpty` | — | Kiểm tra trang Blog báo không có bài viết. |
| `content.openBlogArticle` | `title: string` | Bấm 1 bài viết trên trang Blog theo tiêu đề. |
| `content.openBlogArticleBySlug` | `slug: string` | Mở thẳng trang chi tiết bài viết /blog/{slug}. |
| `content.verifyBlogArticle` | `c: BlogArticleExpect` | Kiểm tra trang chi tiết bài viết: URL, tiêu đề, danh mục, tác giả, lượt xem, tag, bài liên quan. |
| `content.clickBackToBlog` | — | Bấm "Quay lại Blog" trên trang chi tiết bài viết. |
| `content.openRelatedArticle` | `title: string` | Bấm 1 bài trong "Bài viết liên quan". |
| `content.subscribeBlogNewsletterWithoutReload` | `email: string` | Đăng ký nhận tin ở trang Blog và kiểm tra trang KHÔNG bị tải lại (form phải được xử lý bằng JS). |
| `content.verifyPageHeadings` | `h1: string, h2: string[], h3: string[]` | Kiểm tra các tiêu đề trong <main>: h1 đúng, h2/h3 chứa đủ các mục (theo thứ tự). |
| `content.verifyMainContains` | `texts: string[]` | Kiểm tra <main> có chứa các đoạn chữ. |
| `content.verifyBlockContains` | `heading: string, text: string` | Kiểm tra khối có tiêu đề h3 (vd: thẻ "Giao hàng nhanh") chứa đoạn chữ. |
| `content.verifyMainNotMatching` | `pattern: string` | Kiểm tra <main> KHÔNG chứa chuỗi khớp biểu thức chính quy (vd: ký tự Cyrillic). |
| `content.verifyNotFoundPage` | `message: string` | Kiểm tra route không tồn tại hiển thị trang báo lỗi (thông báo + layout). |

## cart

| Keyword | Tham số | Mô tả |
|---|---|---|
| `cart.seedCart` | `items: Partial<CartItem>[]` | Đặt sẵn sản phẩm vào giỏ (localStorage) - gọi TRƯỚC lần mở trang đầu tiên. |
| `cart.openCart` | — | Bấm icon giỏ hàng để mở drawer. |
| `cart.closeCart` | — | Đóng drawer bằng nút X. |
| `cart.closeCartWithEsc` | — | Đóng drawer bằng phím ESC. |
| `cart.verifyCartBadge` | `count: number` | Kiểm tra số trên icon giỏ hàng (0 = không hiện badge). |
| `cart.verifyCartEmpty` | — | Kiểm tra drawer hiển thị "Giỏ hàng trống". |
| `cart.verifyCartItemCount` | `count: number` | Kiểm tra số dòng sản phẩm trong drawer (và tiêu đề "Giỏ hàng (n)"). |
| `cart.verifyCartItem` | `name: string, containsText?: string` | Kiểm tra 1 sản phẩm có trong giỏ, có thể kèm đoạn chữ (vd: size). |
| `cart.increaseQuantity` | `name: string, times = 1` | Bấm "+" số lần cho 1 sản phẩm. |
| `cart.decreaseQuantity` | `name: string, times = 1` | Bấm "-" số lần cho 1 sản phẩm. |
| `cart.verifyQuantity` | `name: string, quantity: number` | Kiểm tra số lượng hiển thị của 1 sản phẩm. |
| `cart.verifyDecreaseDisabled` | `name: string` | Kiểm tra nút "-" bị khóa (số lượng = 1). |
| `cart.removeItem` | `name: string` | Xóa 1 sản phẩm khỏi giỏ. |
| `cart.selectAll` | `checked: boolean` | Tick / bỏ tick "Chọn tất cả". |
| `cart.verifyAllSelected` | `checked: boolean` | Kiểm tra trạng thái ô "Chọn tất cả". |
| `cart.verifySubtotal` | `amount: string` | Kiểm tra dòng Tạm tính chứa số tiền, vd: "550.000". |
| `cart.verifyCheckoutEnabled` | `enabled: boolean` | Kiểm tra nút THANH TOÁN bật/tắt. |
| `cart.proceedToCheckout` | — | Bấm THANH TOÁN trong drawer và chờ sang /checkout. |
| `cart.verifyStoredItemCount` | `count: number` | Kiểm tra số dòng sản phẩm lưu trong localStorage. |
| `cart.verifyStoredQuantity` | `name: string, quantity: number` | Kiểm tra số lượng của 1 sản phẩm lưu trong localStorage. |

## checkout

| Keyword | Tham số | Mô tả |
|---|---|---|
| `checkout.openCheckout` | — | Mở trang thanh toán. |
| `checkout.verifyEmptyCheckout` | — | Kiểm tra trang thanh toán báo giỏ trống, không có nút Thanh toán. |
| `checkout.verifyProductInCheckout` | `name: string` | Kiểm tra sản phẩm hiển thị trong khối sản phẩm của trang thanh toán. |
| `checkout.verifyGuestLoginPrompt` | — | Kiểm tra nút "Đăng nhập / Đăng ký" cho khách vãng lai. |
| `checkout.fillShipping` | `info: ShippingInfo` | Điền thông tin giao hàng (dùng dữ liệu checkout/addresses.json). |
| `checkout.clearShippingField` | `field: 'firstName' \| 'lastName' \| 'phone' \| 'address'` | Xóa nội dung 1 ô trong form giao hàng: firstName \| lastName \| phone \| address. |
| `checkout.chooseShipping` | `method: ShippingMethod` | Chọn phương thức giao hàng: standard \| express. |
| `checkout.choosePayment` | `method: PaymentMethod` | Chọn phương thức thanh toán: cod \| bank \| vnpay \| momo. |
| `checkout.verifySubmitEnabled` | `enabled: boolean` | Kiểm tra nút Thanh toán bật/tắt. |
| `checkout.verifySummaryContains` | `text: string` | Kiểm tra khối tóm tắt đơn hàng chứa đoạn chữ / số tiền. |
| `checkout.mockCreateOrder` | `options: { orderNumber?: string; status?: number; message?: string } = {}` | Giả lập API tạo đơn: thành công (orderNumber) hoặc lỗi (status + message). Lưu lại payload gửi lên. |
| `checkout.placeOrder` | — | Bấm nút Thanh toán. |
| `checkout.verifyOrderSuccess` | `heading: string, orderNumber?: string` | Kiểm tra trang đặt hàng thành công: tiêu đề + mã đơn (nếu có). |
| `checkout.verifyLastOrderPayload` | `expected: Record<string, unknown>` | Kiểm tra payload đơn hàng gửi lên backend chứa các trường mong đợi. |
| `checkout.verifyStillOnCheckout` | — | Kiểm tra vẫn ở trang thanh toán (đặt hàng thất bại). |
| `checkout.verifyOrderSuccessWithoutData` | — | Mở /order-success trực tiếp và kiểm tra báo không có dữ liệu đơn. |

## account

| Keyword | Tham số | Mô tả |
|---|---|---|
| `account.openAccountMenuLink` | `name: string` | Mở menu tài khoản trên header và bấm 1 mục: "Hồ sơ cá nhân" \| "Đơn hàng của tôi" \| "Yêu thích". |
| `account.clickAccountIcon` | — | Bấm icon tài khoản khi chưa đăng nhập (dẫn tới /login). |
| `account.openProfile` | — | Mở trực tiếp trang hồ sơ /profile. |
| `account.verifyProfileLoaded` | — | Kiểm tra trang hồ sơ hiển thị khối "Thông tin tài khoản". |
| `account.openOrders` | — | Mở trực tiếp trang đơn hàng /orders. |
| `account.verifyOrdersLoaded` | — | Kiểm tra trang đơn hàng tải xong (có ô tìm theo mã đơn). |
| `account.verifyWishlistLoaded` | — | Kiểm tra trang yêu thích tải xong (có tiêu đề + danh sách hoặc thông báo rỗng). |
| `account.openProfileFromMenu` | — | Vào trang hồ sơ đúng cách người dùng làm: trang chủ -> menu tài khoản -> "Hồ sơ cá nhân" (tránh bug F5 /profile). |
| `account.openWishlist` | — | Mở trực tiếp trang yêu thích /favorites và chờ tải xong. |
| `account.openAddresses` | — | Mở trực tiếp trang sổ địa chỉ /addresses và chờ tải xong. |
| `account.openOrderDetail` | `id: string \| number` | Mở trực tiếp trang chi tiết đơn /orders/:id. |
| `account.clickSidebarLink` | `label: string` | Bấm 1 link trên sidebar tài khoản, vd: "Đơn hàng của tôi", "Sổ địa chỉ". |
| `account.logoutFromSidebar` | — | Đăng xuất bằng nút "Đăng xuất" trên sidebar tài khoản. |
| `account.seedStoredUser` | `user: Record<string, unknown>` | Thay thông tin user đang lưu (localStorage) bằng user cho trước - gọi TRƯỚC lần mở trang đầu tiên. |
| `account.verifyProfileFields` | `fields: Record<string, string>` | Kiểm tra các trường ở chế độ xem hồ sơ: { "Họ và tên": "...", "Giới tính": "Nữ" }. |
| `account.startEditProfile` | — | Bấm "Chỉnh sửa" để chuyển hồ sơ sang chế độ sửa. |
| `account.fillProfileForm` | `form: ProfileForm` | Điền form sửa hồ sơ (chỉ các trường có trong dữ liệu); gender: male \| female \| other. |
| `account.verifyProfileForm` | `form: ProfileForm` | Kiểm tra giá trị đang có trong form sửa hồ sơ. |
| `account.verifyProfileEmailLocked` | `email: string` | Kiểm tra ô Email trong form sửa bị khóa và hiển thị đúng email. |
| `account.saveProfile` | — | Bấm "Lưu thay đổi" trong form sửa hồ sơ. |
| `account.cancelEditProfile` | — | Bấm "Hủy" để thoát chế độ sửa hồ sơ. |
| `account.verifyProfileEditing` | `editing: boolean` | Kiểm tra hồ sơ đang ở chế độ sửa (true) hay chế độ xem (false). |
| `account.openChangePassword` | — | Bấm "Đổi mật khẩu" và chờ modal mở. |
| `account.fillChangePassword` | `form: PasswordForm` | Điền 3 ô trong modal đổi mật khẩu (hiện tại, mới, xác nhận). |
| `account.submitChangePassword` | — | Bấm "Xác nhận" trong modal đổi mật khẩu. |
| `account.verifyChangePasswordError` | `message: string` | Kiểm tra thông báo lỗi trong modal đổi mật khẩu. |
| `account.verifyChangePasswordClosed` | — | Kiểm tra modal đổi mật khẩu đã đóng. |
| `account.cancelChangePassword` | — | Bấm "Hủy" ở cuối modal đổi mật khẩu. |
| `account.closeChangePassword` | — | Bấm nút chữ "Đóng" ở góc trên modal đổi mật khẩu. |
| `account.verifyChangePasswordFormEmpty` | — | Kiểm tra modal đổi mật khẩu đang mở với form trống, không có lỗi cũ. |
| `account.verifyProfileSummary` | `stats: Record<string, string>` | Kiểm tra dải thống kê trên trang hồ sơ: { "Tổng đơn hàng": "7", ... }. |
| `account.verifyRecentOrders` | `codes: string[]` | Kiểm tra khối "Đơn hàng gần đây" hiển thị đúng các mã đơn theo thứ tự ([] = thông báo chưa có đơn). |
| `account.verifyRecentFavorites` | `names: string[]` | Kiểm tra khối "Sản phẩm yêu thích gần đây" hiển thị đúng tên theo thứ tự ([] = thông báo trống). |
| `account.verifyDefaultAddress` | `texts: string[]` | Kiểm tra khối "Địa chỉ giao hàng mặc định" chứa các đoạn chữ. |
| `account.clickUpdateAddress` | — | Bấm "Cập nhật địa chỉ" trên hồ sơ và chờ sang /addresses. |
| `account.verifyOrderStats` | `stats: Record<string, number>` | Kiểm tra số đếm trên các ô thống kê: { "Tất cả đơn": 7, "Đã hủy": 1 }. |
| `account.filterOrdersByStatus` | `tab: string` | Bấm tab lọc trạng thái đơn, vd: "Chờ xác nhận". |
| `account.clickOrderStat` | `label: string` | Bấm 1 ô thống kê để lọc nhanh, vd: "Đã hủy". |
| `account.searchOrders` | `query: string` | Gõ vào ô "Tìm theo mã đơn hàng...". |
| `account.verifyOrderList` | `codes: string[]` | Kiểm tra danh sách đơn hiển thị đúng các mã đơn theo thứ tự. |
| `account.verifyOrdersEmpty` | `message: string` | Kiểm tra trang đơn hàng hiển thị thông báo rỗng, vd: "Bạn chưa có đơn hàng nào". |
| `account.verifyOrderItem` | `code: string, texts: string[]` | Kiểm tra 1 đơn trong danh sách chứa các đoạn chữ (ngày, số lượng, thanh toán, tổng tiền...). |
| `account.verifyOrderStatus` | `code: string, label: string` | Kiểm tra nhãn trạng thái của 1 đơn trong danh sách. |
| `account.verifyOrderCancelable` | `code: string, cancelable: boolean` | Kiểm tra đơn trong danh sách có (true) / không có (false) nút "Hủy đơn". |
| `account.cancelOrderFromList` | `code: string` | Bấm "Hủy đơn" của 1 đơn trong danh sách (app không hỏi xác nhận). |
| `account.openOrderFromList` | `code: string` | Bấm "Xem chi tiết" của 1 đơn và chờ sang trang chi tiết. |
| `account.verifyOrderDetailHeading` | `heading: string` | Kiểm tra tiêu đề trang chi tiết đơn, vd: "Chi tiết đơn hàng #ORD000107". |
| `account.verifyOrderDetailStatus` | `status: string, payment: string` | Kiểm tra 2 ô trạng thái đơn hàng + trạng thái thanh toán ở đầu trang chi tiết. |
| `account.verifyOrderDetailInfo` | `section: string, rows: Record<string, string>` | Kiểm tra các dòng "nhãn: giá trị" trong 1 khối, vd: ("Thông tin giao hàng", { "Người nhận": "..." }). |
| `account.verifyOrderDetailItems` | `heading: string, names: string[]` | Kiểm tra tiêu đề khối sản phẩm (vd: "Sản phẩm đã đặt (2)") và tên sản phẩm theo thứ tự. |
| `account.verifyOrderDetailItem` | `name: string, texts: string[]` | Kiểm tra 1 dòng sản phẩm trong đơn chứa các đoạn chữ (màu, size, SKU, giá, số lượng). |
| `account.verifyOrderDetailTotals` | `rows: Record<string, string>` | Kiểm tra khối "Chi tiết thanh toán": { "Tạm tính": "480.000đ", "Phí vận chuyển": "Miễn phí", ... }. |
| `account.verifyOrderDetailCancelable` | `cancelable: boolean` | Kiểm tra trang chi tiết có (true) / không có (false) nút "Hủy đơn hàng". |
| `account.openCancelOrderDialog` | — | Bấm "Hủy đơn hàng" và chờ hộp xác nhận hiện ra. |
| `account.confirmCancelOrder` | `reason = ''` | Nhập lý do (để trống = không nhập) rồi bấm "Xác nhận hủy". |
| `account.closeCancelOrderDialog` | — | Bấm "Đóng" trên hộp xác nhận hủy đơn. |
| `account.verifyCancelOrderDialog` | `open: boolean` | Kiểm tra hộp xác nhận hủy đơn đang mở (true) / đã đóng (false). |
| `account.verifyOrderDetailError` | `message: string` | Kiểm tra trang chi tiết đơn báo lỗi (thông báo + nút "Quay lại đơn hàng"). |
| `account.backToOrdersFromError` | — | Bấm "Quay lại đơn hàng" trên màn hình lỗi và chờ về /orders. |
| `account.goBackFromOrderDetail` | — | Bấm nút "Quay lại" ở góc trên trang chi tiết đơn và chờ về /orders. |
| `account.verifyWishlistCount` | `count: number` | Kiểm tra dòng "<N> sản phẩm yêu thích" dưới tiêu đề. |
| `account.verifyWishlistProducts` | `names: string[]` | Kiểm tra danh sách thẻ sản phẩm yêu thích đúng tên + đúng thứ tự. |
| `account.searchWishlist` | `query: string` | Gõ vào ô "Tìm sản phẩm yêu thích...". |
| `account.sortWishlist` | `sort: WishlistSort` | Chọn cách sắp xếp: recent \| price_asc \| price_desc. |
| `account.removeFromWishlist` | `name: string` | Bấm trái tim "Bỏ yêu thích" trên thẻ sản phẩm. |
| `account.addWishlistItemToCart` | `name: string` | Bấm "Thêm vào giỏ hàng" trên thẻ sản phẩm yêu thích. |
| `account.verifyWishlistItem` | `name: string, texts: string[]` | Kiểm tra thẻ sản phẩm yêu thích chứa các đoạn chữ (danh mục, giá, % giảm, tình trạng...). |
| `account.verifyWishlistItemAvailable` | `name: string, available: boolean` | Kiểm tra sản phẩm còn hàng (nút thêm giỏ bật) hay hết hàng (nhãn "Hết hàng", nút tắt). |
| `account.verifyWishlistNoMatch` | — | Kiểm tra thông báo "Không tìm thấy sản phẩm phù hợp" khi lọc/tìm không ra. |
| `account.verifyWishlistEmpty` | — | Kiểm tra trang yêu thích trống ("Bạn chưa có sản phẩm yêu thích", 0 sản phẩm). |
| `account.favoriteFromListing` | `path: string` | Mở trang danh mục và bấm nút trái tim (yêu thích) của sản phẩm đầu tiên. |
| `account.verifyAddressesEmpty` | — | Kiểm tra trang địa chỉ trống ("Bạn chưa có địa chỉ nào"). |
| `account.openAddAddressForm` | — | Bấm nút "Thêm địa chỉ" trên tiêu đề và chờ form "Thêm địa chỉ mới". |
| `account.openAddAddressFromEmptyState` | — | Bấm "Thêm địa chỉ mới" ở màn hình trống và chờ form mở. |
| `account.fillAddressForm` | `form: AddressForm` | Điền form địa chỉ (chỉ các trường có trong dữ liệu); city = tên tỉnh, vd: "Hồ Chí Minh". |
| `account.submitAddressForm` | — | Bấm nút lưu của form địa chỉ ("Thêm địa chỉ" / "Lưu thay đổi"). |
| `account.cancelAddressForm` | — | Bấm "Hủy" để đóng form địa chỉ. |
| `account.verifyAddressFormErrors` | `messages: string[]` | Kiểm tra các thông báo lỗi dưới ô nhập của form địa chỉ. |
| `account.verifyAddressFormOpen` | `heading: string` | Kiểm tra form địa chỉ đang mở với tiêu đề: "Thêm địa chỉ mới" \| "Sửa địa chỉ". |
| `account.verifyAddressFormClosed` | — | Kiểm tra form địa chỉ đã đóng. |
| `account.verifyAddressFormValues` | `form: AddressForm` | Kiểm tra giá trị đang có trong form địa chỉ. |
| `account.verifyAddressList` | `names: string[]` | Kiểm tra danh sách thẻ địa chỉ (tên người nhận theo thứ tự) và dòng "<N> địa chỉ đã lưu". |
| `account.verifyAddressCard` | `name: string, texts: string[]` | Kiểm tra thẻ địa chỉ của người nhận chứa các đoạn chữ (SĐT, địa chỉ đầy đủ...). |
| `account.verifyAddressDefault` | `name: string, isDefault: boolean` | Kiểm tra địa chỉ là mặc định (badge "Mặc định", không có nút đặt mặc định) hay không. |
| `account.verifyAddressNameRow` | `name: string, isDefault: boolean` | Kiểm tra dòng tên trên thẻ địa chỉ chỉ gồm tên (+ "Mặc định" nếu là mặc định), không có ký tự thừa. |
| `account.verifyDefaultBadgeCount` | `count: number` | Kiểm tra số badge "Mặc định" trên toàn trang địa chỉ. |
| `account.editAddress` | `name: string` | Bấm nút "Sửa" trên thẻ địa chỉ và chờ form "Sửa địa chỉ". |
| `account.setDefaultAddress` | `name: string` | Bấm nút "Đặt làm mặc định" trên thẻ địa chỉ. |
| `account.deleteAddress` | `name: string` | Bấm nút "Xóa" trên thẻ địa chỉ và chờ hộp xác nhận "Xóa địa chỉ". |
| `account.confirmDeleteAddress` | — | Bấm "Xóa địa chỉ" trong hộp xác nhận. |
| `account.cancelDeleteAddress` | — | Bấm "Hủy" trong hộp xác nhận xóa địa chỉ và chờ hộp đóng. |
| `account.verifyDeleteAddressDialog` | `text: string` | Kiểm tra hộp xác nhận xóa địa chỉ chứa đoạn chữ, vd: câu hỏi kèm địa chỉ. |
| `account.verifyCheckoutAccount` | `name: string, email: string` | Kiểm tra trang thanh toán hiển thị tài khoản đang đăng nhập (tên + email), không có nút đăng nhập. |
| `account.verifyCheckoutPrefill` | `expected: { firstName: string; lastName: string; phone: string }` | Kiểm tra form giao hàng được điền sẵn từ tài khoản: { firstName, lastName, phone }. |
| `account.logoutOnCheckout` | — | Bấm "Đăng xuất" trong khối tài khoản trên trang thanh toán. |
| `account.verifyCheckoutGuestMode` | — | Kiểm tra trang thanh toán chuyển về chế độ khách vãng lai (vẫn ở /checkout, token bị xóa). |
| `account.goToLoginFromCheckout` | — | Bấm "Đăng nhập / Đăng ký" trên trang thanh toán và chờ sang /login. |
| `account.verifyOrderSuccessNumber` | `orderNumber: string` | Kiểm tra mã đơn hiển thị cạnh "Mã đơn hàng:" trên trang đặt hàng thành công. |
| `account.verifyOrderSuccessInfo` | `section: string, rows: Record<string, string>` | Kiểm tra các dòng trong 1 khối trang thành công: "Thông tin thanh toán" \| "Người nhận" \| "Chi tiết thanh toán". |
| `account.verifyOrderSuccessLinks` | — | Kiểm tra trang thành công có 2 link "Tiếp tục mua sắm" (về /) và link "Xem đơn hàng" (tới /orders). |
| `account.openOrdersFromSuccess` | — | Bấm "Xem đơn hàng" trên trang thành công và chờ sang /orders. |

## admin

| Keyword | Tham số | Mô tả |
|---|---|---|
| `admin.openAdminLogin` | — | Mở trang đăng nhập quản trị. |
| `admin.loginAdmin` | `email: string, password: string` | Nhập email + mật khẩu admin và bấm Đăng nhập. |
| `admin.loginAsAdmin` | — | Đăng nhập bằng tài khoản admin test trong .env và chờ vào Dashboard. |
| `admin.loginAdminExpectingError` | `email: string, password: string, message: string` | Đăng nhập admin sai và kiểm tra thông báo lỗi vẫn hiển thị (không reload). |
| `admin.verifyOnAdminLogin` | — | Kiểm tra đang ở trang đăng nhập admin (bị chặn khi chưa đăng nhập). |
| `admin.backToStore` | — | Bấm "Quay về cửa hàng" trên trang đăng nhập admin. |
| `admin.openDashboard` | — | Mở trang quản trị /admin (cần đã đăng nhập) và chờ sidebar. |
| `admin.navigateMenu` | `label: string` | Bấm 1 mục trên sidebar quản trị, vd: "Sản phẩm". |
| `admin.openAdminPage` | `path: string, title: string` | Mở 1 trang quản trị theo đường dẫn và kiểm tra tiêu đề trên header. |
| `admin.verifyHeaderTitle` | `title: string` | Kiểm tra tiêu đề trang trên header admin. |
| `admin.verifyTableHeaders` | `headers: string[]` | Kiểm tra bảng có đủ các cột (theo thứ tự). |
| `admin.searchList` | `placeholder: string, text: string` | Gõ vào ô tìm kiếm có placeholder cho trước. |
| `admin.clickButton` | `name: string` | Bấm 1 nút theo tên hiển thị (ưu tiên nút trong modal đang mở). |
| `admin.clickRowAction` | `rowText: string, title: string` | Bấm nút hành động (title) trên dòng chứa text, vd: ("Áo thun", "Sửa"). |
| `admin.verifyRow` | `text: string, visible = true` | Kiểm tra có/không có dòng chứa text trong bảng. |
| `admin.fillForm` | `fields: Record<string, string \| number \| boolean>` | Điền form theo label: chuỗi -> input/textarea/select (value hoặc label option), boolean -> checkbox. |
| `admin.verifyFieldValue` | `label: string, value: string` | Kiểm tra giá trị hiện tại của 1 ô trong form (theo label). |
| `admin.verifyModalOpen` | `heading: string` | Kiểm tra modal/khối có tiêu đề đang hiển thị. |
| `admin.verifyModalClosed` | `heading: string` | Kiểm tra modal/khối có tiêu đề đã đóng. |
| `admin.verifyAdminPage` | `path: string` | Kiểm tra đang ở 1 trang quản trị (URL + tiêu đề trang). |

## adminCatalog

| Keyword | Tham số | Mô tả |
|---|---|---|
| `adminCatalog.mockCatalogApi` | `fixture: CatalogFixture` | Mock GET /admin/products (lọc search/category/brand), /admin/products/:id, /admin/categories, /admin/brands. |
| `adminCatalog.verifyApiRequested` | `path: string, params: Record<string, string \| number> = {}` | Kiểm tra trình duyệt đã gọi GET tới đường dẫn (vd: "/admin/products") với đủ tham số query. |
| `adminCatalog.verifyColumns` | `headers: string[]` | Kiểm tra tiêu đề cột bảng theo nội dung gốc (bỏ qua CSS uppercase), đúng thứ tự. |
| `adminCatalog.verifyProductCountAtLeast` | `min: number` | Kiểm tra bảng sản phẩm có ít nhất `min` dòng dữ liệu. |
| `adminCatalog.verifyProductRows` | `rows: ProductRowExpect[]` | Kiểm tra từng dòng sản phẩm: thương hiệu, SKU, danh mục, giá, tồn kho (đỏ khi <= 5), đã bán, nổi bật, trạng thái. |
| `adminCatalog.verifyProductListed` | `name: string, visible = true` | Kiểm tra có/không có dòng sản phẩm theo tên chính xác. |
| `adminCatalog.searchProducts` | `text: string` | Gõ từ khóa vào ô tìm sản phẩm. |
| `adminCatalog.filterProductsByCategory` | `label: string` | Chọn lọc danh mục theo tên hiển thị. |
| `adminCatalog.filterProductsByBrand` | `label: string` | Chọn lọc thương hiệu theo tên hiển thị. |
| `adminCatalog.clickProductFeatured` | `name: string` | Bấm nút ngôi sao (nổi bật) trên dòng sản phẩm. |
| `adminCatalog.verifyProductFeaturedTitle` | `name: string, title: string` | Kiểm tra title nút ngôi sao: "Đánh dấu nổi bật" (chưa nổi bật) hoặc "Bỏ nổi bật". |
| `adminCatalog.clickProductStatus` | `name: string` | Bấm nút gạt trạng thái bán trên dòng sản phẩm. |
| `adminCatalog.verifyProductActive` | `name: string, active: boolean` | Kiểm tra nút gạt trạng thái bán đang bật (xanh) hay tắt (xám). |
| `adminCatalog.clickProductAction` | `name: string, title: 'Xem' \| 'Sửa' \| 'Xóa'` | Bấm nút hành động "Xem" / "Sửa" / "Xóa" trên dòng sản phẩm. |
| `adminCatalog.verifyProductViewLink` | `name: string, href: string` | Kiểm tra link "Xem" của sản phẩm trỏ tới trang chi tiết ngoài cửa hàng. |
| `adminCatalog.verifyDeleteProductModal` | `heading: string, message: string` | Kiểm tra modal xóa sản phẩm đang mở với tiêu đề + nội dung cảnh báo. |
| `adminCatalog.selectProducts` | `names: string[]` | Tích chọn các dòng sản phẩm theo tên. |
| `adminCatalog.selectAllProducts` | — | Tích ô chọn tất cả trên đầu bảng sản phẩm. |
| `adminCatalog.verifyBulkSelection` | `text: string \| null` | Kiểm tra thanh thao tác hàng loạt "{n} sản phẩm được chọn" (null = ẩn). |
| `adminCatalog.clickBulkDelete` | — | Bấm "Xóa đã chọn" trên thanh thao tác hàng loạt. |
| `adminCatalog.verifyProductsPagination` | `text: string \| null` | Kiểm tra dòng phân trang sản phẩm, vd: "Trang 1 trên 3" (null = không có phân trang). |
| `adminCatalog.verifyProductsPaginationFirstPage` | — | Kiểm tra dòng phân trang sản phẩm khớp mẫu "Trang 1 trên N". |
| `adminCatalog.goToProductsPage` | `n: number` | Bấm số trang trên phân trang sản phẩm. |
| `adminCatalog.clickAddProduct` | — | Bấm "Thêm sản phẩm" trên trang danh sách. |
| `adminCatalog.verifyProductFormReady` | `submitLabel: string` | Chờ form sản phẩm tải xong (hết "Đang tải dữ liệu...") và kiểm tra nhãn nút lưu. |
| `adminCatalog.submitProductForm` | — | Bấm nút lưu form sản phẩm ("Tạo sản phẩm" / "Cập nhật"). |
| `adminCatalog.verifyProductFormError` | `text: string` | Kiểm tra hộp lỗi đỏ trên form sản phẩm. |
| `adminCatalog.clickBackToProducts` | — | Bấm "Quay lại" trên form sản phẩm. |
| `adminCatalog.toggleVariantBuilder` | — | Bấm "+ Tạo biến thể" / "Tắt chế độ" trong khối Biến thể. |
| `adminCatalog.verifyVariantToggleLabel` | `label: string` | Kiểm tra nhãn nút bật/tắt chế độ tạo biến thể. |
| `adminCatalog.selectVariantSizes` | `sizes: string[]` | Chọn các size trong chế độ tạo biến thể (vd: ["S", "M"]). |
| `adminCatalog.selectVariantColors` | `colors: string[]` | Chọn các màu trong chế độ tạo biến thể (vd: ["Đen", "Trắng"]). |
| `adminCatalog.verifyGenerateVariantsButton` | `label: string, enabled: boolean` | Kiểm tra nút "Tạo {n} biến thể" (nhãn + bật/tắt). |
| `adminCatalog.generateVariants` | — | Bấm "Tạo {n} biến thể". |
| `adminCatalog.verifyVariantRows` | `rows: VariantRowExpect[]` | Kiểm tra lưới biến thể: size, màu, SKU từng dòng (đúng thứ tự). |
| `adminCatalog.verifyVariantCount` | `count: number` | Kiểm tra số dòng biến thể. |
| `adminCatalog.removeVariant` | `index: number` | Xóa dòng biến thể thứ `index` (bắt đầu từ 0). |
| `adminCatalog.addImageUrl` | `url: string` | Dán URL ảnh vào ô "Dán URL ảnh..." và nhấn Enter. |
| `adminCatalog.verifyImageCount` | `count: number` | Kiểm tra số ảnh trong khối Hình ảnh và nhãn "Ảnh chính" (ảnh đầu tiên). |
| `adminCatalog.removeImage` | `index: number` | Rê chuột vào ảnh thứ `index` và bấm nút X để xóa. |
| `adminCatalog.uploadProductImage` | `fileName: string, response: unknown` | Mock POST /api/admin/upload (ghi lại header Authorization) rồi chọn 1 ảnh PNG để tải lên. |
| `adminCatalog.verifyUploadUsedAdminToken` | — | Kiểm tra request tải ảnh gửi đúng token admin (Bearer + admin_token trong localStorage). |
| `adminCatalog.verifyCardCountAtLeast` | `min: number` | Kiểm tra có ít nhất `min` thẻ (danh mục / thương hiệu). |
| `adminCatalog.verifyCards` | `visible: string[], hidden: string[] = []` | Kiểm tra các thẻ hiển thị (`visible`) và không hiển thị (`hidden`) theo tên. |
| `adminCatalog.verifyCardsEmpty` | `text: string` | Kiểm tra lưới thẻ trống với thông báo, vd: "Không tìm thấy danh mục". |
| `adminCatalog.clickCardEdit` | `name: string` | Rê chuột vào thẻ rồi bấm icon Sửa (icon ẩn tới khi hover, không có tên). |
| `adminCatalog.clickCardDelete` | `name: string` | Rê chuột vào thẻ rồi bấm icon Xóa (icon ẩn tới khi hover, không có tên). |
| `adminCatalog.clickCardToggle` | `name: string` | Bấm nút gạt Hoạt động trên thẻ. |
| `adminCatalog.verifyCardActive` | `name: string, active: boolean` | Kiểm tra nút gạt Hoạt động trên thẻ đang bật (xanh) hay tắt (xám). |
| `adminCatalog.verifyCardFeatured` | `name: string, featured: boolean` | Kiểm tra thẻ có/không có nhãn "Nổi bật". |
| `adminCatalog.verifyCardDetails` | `name: string, slug: string, description?: string` | Kiểm tra slug (/{slug}) và mô tả hiển thị trên thẻ. |
| `adminCatalog.verifyDeleteConfirmMessage` | `message: string` | Kiểm tra nội dung modal "Xác nhận xóa". |

## adminSales

| Keyword | Tham số | Mô tả |
|---|---|---|
| `adminSales.mockOrdersApi` | `fixture: OrdersFixture` | Mock GET /admin/orders (lọc search/status/payment_status), /admin/orders/stats và /admin/orders/:id. |
| `adminSales.mockCustomersApi` | `fixture: { customers: CustomerRecord[]; details?: Record<string, Record<string, unknown>>; total?: number }` | Mock GET /admin/customers (lọc search) và /admin/customers/:id. |
| `adminSales.mockEmployeesApi` | `fixture: { employees: EmployeeRecord[]; total?: number }` | Mock GET /admin/employees (lọc search theo tên/email). |
| `adminSales.verifyApiRequested` | `path: string, params: Record<string, string \| number> = {}` | Kiểm tra trình duyệt đã gọi GET tới đường dẫn (vd: "/admin/orders") với đủ tham số query. |
| `adminSales.verifyColumns` | `headers: string[]` | Kiểm tra tiêu đề cột bảng theo nội dung gốc (bỏ qua CSS uppercase), đúng thứ tự. |
| `adminSales.verifyApiRequestCount` | `path: string, min: number` | Kiểm tra số request GET tới đường dẫn đạt ít nhất `min` lần. |
| `adminSales.toggleSidebar` | — | Bấm nút thu gọn / mở rộng sidebar. |
| `adminSales.verifySidebarCollapsed` | `collapsed: boolean` | Kiểm tra sidebar đang thu gọn (72px, ẩn chữ menu) hoặc mở rộng (260px). |
| `adminSales.verifyActiveMenu` | `label: string` | Kiểm tra chỉ có đúng 1 mục sidebar đang sáng và đó là `label`. |
| `adminSales.clickViewStore` | — | Bấm "Xem cửa hàng" ở chân sidebar. |
| `adminSales.logout` | `from: 'sidebar' \| 'menu'` | Đăng xuất từ chân sidebar ("sidebar") hoặc menu người dùng trên header ("menu"). |
| `adminSales.verifySidebarUser` | `name: string, role: string` | Kiểm tra khối người dùng ở chân sidebar (tên + vai trò). |
| `adminSales.openUserMenu` | — | Mở menu người dùng trên header. |
| `adminSales.verifyUserMenu` | `name: string, email: string, role: string` | Kiểm tra nút người dùng và menu thả xuống hiển thị tên, email, 3 mục. |
| `adminSales.chooseUserMenuItem` | `label: string` | Bấm 1 mục trong menu người dùng ("Tổng quan" / "Cài đặt" / "Đăng xuất"). |
| `adminSales.clickOutsideUserMenu` | — | Bấm ra ngoài menu người dùng (vào tiêu đề trang) để đóng menu. |
| `adminSales.verifyUserMenuOpen` | `open: boolean` | Kiểm tra menu người dùng đang mở/đóng. |
| `adminSales.openNotifications` | — | Bấm chuông thông báo để mở panel. |
| `adminSales.closeNotifications` | `via: 'button' \| 'overlay' = 'button'` | Đóng panel thông báo bằng nút X ("button") hoặc bấm ra ngoài ("overlay"). |
| `adminSales.verifyNotificationPanelOpen` | `open: boolean` | Kiểm tra panel thông báo đang mở / đã đóng. |
| `adminSales.verifyNotificationBadge` | `expected: string \| null` | Kiểm tra số trên chuông (null = không hiển thị số). |
| `adminSales.verifyNotificationPanel` | `expected: { items: string[]; stats: string[]; footer: string }` | Kiểm tra panel: danh sách tiêu đề thông báo, thanh thống kê và dòng "{n} thông báo". |
| `adminSales.verifyNotificationsEmpty` | — | Kiểm tra panel trống: "Không có thông báo nào" và "0 thông báo". |
| `adminSales.verifyNotificationVisible` | `title: string, visible = true` | Kiểm tra có/không có thông báo theo tiêu đề trong panel. |
| `adminSales.clickNotification` | `title: string` | Bấm 1 thông báo theo tiêu đề. |
| `adminSales.verifyNewNotificationChip` | `text: string \| null` | Kiểm tra nhãn "{n} mới" cạnh tiêu đề panel (null = không có). |
| `adminSales.markAllNotificationsRead` | — | Bấm "Đánh dấu đã đọc" trong panel thông báo. |
| `adminSales.refreshNotifications` | — | Bấm nút "Làm mới" trong panel thông báo và kiểm tra API thông báo được gọi lại. |
| `adminSales.clickViewAllOrders` | — | Bấm "Xem tất cả đơn hàng" ở chân panel thông báo. |
| `adminSales.verifyStatCardLabels` | `labels: string[]` | Kiểm tra 4 thẻ thống kê hiển thị đúng nhãn (theo thứ tự). |
| `adminSales.verifyStatCards` | `cards: StatCardExpect[]` | Kiểm tra giá trị / dòng phụ / % thay đổi của các thẻ thống kê. |
| `adminSales.verifyStatCardHasNoChange` | `label: string` | Kiểm tra thẻ thống kê KHÔNG hiển thị huy hiệu % tăng/giảm. |
| `adminSales.verifyDashboardSections` | `titles: string[]` | Kiểm tra các khối tiêu đề trên dashboard. |
| `adminSales.verifyOrderStatusBreakdown` | `values: Record<string, string>` | Kiểm tra số lượng đơn theo từng trạng thái (khối "Đơn hàng theo trạng thái"). |
| `adminSales.verifyRecentOrders` | `orders: { number: string; customer: string; total: string; status: string }[]` | Kiểm tra danh sách "Đơn hàng gần đây" (mã, khách, tổng tiền, trạng thái). |
| `adminSales.verifyTopProducts` | `products: { name: string; sold: string }[]` | Kiểm tra danh sách "Sản phẩm bán chạy" (tên + số đã bán, theo thứ tự). |
| `adminSales.verifyQuickCards` | `cards: { title: string; value: string }[]` | Kiểm tra giá trị các thẻ thao tác nhanh cuối dashboard. |
| `adminSales.clickDashboardLink` | `label: string, section?: string` | Bấm 1 link trên dashboard; `section` dùng khi trùng tên (vd: "Xem tất cả"). |
| `adminSales.verifyChartTicks` | `ticks: string[]` | Kiểm tra nhãn trục X của biểu đồ doanh thu. |
| `adminSales.verifyChartSeries` | `points: number` | Kiểm tra biểu đồ vẽ vùng doanh thu + đường đơn hàng với `points` điểm dữ liệu. |
| `adminSales.selectRevenueRange` | `option: string` | Chọn khoảng thời gian cho biểu đồ doanh thu, vd: "30 ngày qua". |
| `adminSales.verifyOrderStatusCards` | `counts: Record<string, string>` | Kiểm tra số lượng trên 7 thẻ trạng thái đơn hàng. |
| `adminSales.clickOrderStatusCard` | `label: string` | Bấm 1 thẻ trạng thái đơn hàng (bật/tắt lọc). |
| `adminSales.verifyOrderStatusCardActive` | `label: string, active: boolean` | Kiểm tra thẻ trạng thái đang được chọn (viền đỏ) hay không. |
| `adminSales.searchOrders` | `text: string` | Gõ từ khóa vào ô tìm đơn hàng. |
| `adminSales.filterOrdersByStatus` | `value: string` | Chọn lọc trạng thái đơn (value: pending, confirmed... hoặc "" = tất cả). |
| `adminSales.filterOrdersByPayment` | `value: string` | Chọn lọc trạng thái thanh toán (value: unpaid, paid, partially_paid, refunded). |
| `adminSales.filterOrdersByDate` | `from: string, to: string` | Mở "Bộ lọc" và nhập khoảng ngày (yyyy-mm-dd). |
| `adminSales.clearOrderFilters` | — | Bấm "Bộ lọc" rồi "Xóa bộ lọc". |
| `adminSales.verifyOrderFilters` | `expected: { search?: string; status?: string; payment?: string }` | Kiểm tra giá trị hiện tại của ô tìm kiếm, lọc trạng thái, lọc thanh toán. |
| `adminSales.verifyOrderRows` | `numbers: string[]` | Kiểm tra bảng đơn hàng hiển thị đúng các mã đơn (theo thứ tự). |
| `adminSales.verifyOrderRow` | `row: { number: string; customer: string; items: string; total: string; payment: string; status: string }` | Kiểm tra 1 dòng đơn hàng: khách, số sản phẩm, tổng tiền, thanh toán, trạng thái. |
| `adminSales.verifyOrderRowStatus` | `number: string, label: string` | Kiểm tra trạng thái hiển thị trên dòng đơn hàng. |
| `adminSales.verifyOrdersEmpty` | — | Kiểm tra bảng trống "Không có đơn hàng nào" và "0 đơn hàng". |
| `adminSales.openOrderDetail` | `number: string` | Bấm "Xem chi tiết" trên dòng đơn hàng và chờ modal chi tiết. |
| `adminSales.closeOrderDetail` | — | Đóng modal chi tiết đơn (nút X). |
| `adminSales.verifyOrderDetail` | `d: OrderDetailExpect` | Kiểm tra nội dung modal chi tiết đơn: người nhận, địa chỉ, thông tin, sản phẩm, tổng tiền, lịch sử. |
| `adminSales.verifyOrderStatusButtons` | `labels: string[]` | Kiểm tra các nút chuyển trạng thái trong modal chi tiết ([] = không có khối cập nhật trạng thái). |
| `adminSales.clickOrderStatusButton` | `label: string` | Bấm 1 nút chuyển trạng thái trong modal chi tiết đơn. |
| `adminSales.verifyOrderDetailStatus` | `label: string` | Kiểm tra huy hiệu trạng thái trên đầu modal chi tiết. |
| `adminSales.verifyOrderProcessingWarning` | `visible: boolean` | Kiểm tra hiện/ẩn cảnh báo "Lưu ý khi xử lý" (đơn đang giao/đã giao). |
| `adminSales.changeOrderPayment` | `value: string` | Chọn trạng thái thanh toán trong modal chi tiết (value: paid, unpaid, partially_paid). |
| `adminSales.verifyOrderDetailPayment` | `label: string, editable: boolean` | Kiểm tra trạng thái thanh toán trên modal chi tiết và khối "Cập nhật thanh toán" có hiện không. |
| `adminSales.verifyOrderCancelAction` | `number: string, visible: boolean` | Kiểm tra dòng đơn có/không có nút "Hủy đơn". |
| `adminSales.openCancelOrder` | `number: string` | Bấm nút "Hủy đơn" trên dòng đơn hàng và chờ modal "Hủy đơn hàng". |
| `adminSales.fillCancelReason` | `reason: string` | Nhập lý do hủy đơn trong modal "Hủy đơn hàng". |
| `adminSales.verifyCancelNotes` | `notes: string[]` | Kiểm tra các ghi chú (hoàn tiền / hoàn điểm) trong modal hủy đơn. |
| `adminSales.goToPage` | `n: number` | Bấm số trang trên thanh phân trang. |
| `adminSales.clickNextPage` | — | Bấm nút trang sau (mũi tên phải / "Sau"). |
| `adminSales.verifyPaginationText` | `text: string` | Kiểm tra dòng chữ phân trang, vd: "Trang 1 / 3 — 45 đơn hàng". |
| `adminSales.verifyPageButton` | `n: number, visible = true` | Kiểm tra có/không có nút số trang. |
| `adminSales.verifyFieldErrors` | `heading: string, errors: string[]` | Kiểm tra danh sách lỗi dưới ô nhập trong modal có tiêu đề `heading` (đúng thứ tự, [] = không lỗi). |
| `adminSales.verifyModalText` | `heading: string, text: string` | Kiểm tra modal có tiêu đề `heading` chứa đoạn chữ. |
| `adminSales.verifyFieldPlaceholder` | `label: string, placeholder: string` | Kiểm tra placeholder của ô nhập theo label. |
| `adminSales.verifyCustomerRow` | `row: { name: string; status: string; spent?: string; points?: string }` | Kiểm tra dòng khách hàng: trạng thái, tổng chi tiêu, điểm. |
| `adminSales.verifyCustomerDetail` | `d: { name: string; email: string; stats: Record<string, string>; values: Record<string, string>; recentOrders: string[]; }` | Kiểm tra modal "Chi tiết khách hàng": tên, email, số liệu, thông tin, đơn gần đây. |
| `adminSales.verifyCustomerRecentOrderStatuses` | `labels: string[]` | Kiểm tra nhãn trạng thái của các đơn gần đây trong modal "Chi tiết khách hàng" (đúng thứ tự). |
| `adminSales.verifyCustomerDeleteWarning` | `text: string \| null` | Kiểm tra cảnh báo "khách đã có đơn -> khóa thay vì xóa" trong modal xóa (null = không có). |
| `adminSales.verifyPersonRow` | `name: string, visible = true` | Kiểm tra có/không có dòng (khách hàng / nhân viên) theo tên chính xác. |
| `adminSales.verifyEmployeesHeading` | `text: string` | Kiểm tra tiêu đề "Tài khoản nhân viên" trên trang nhân viên. |
| `adminSales.verifyEmployeeRole` | `name: string, label: string` | Kiểm tra nhãn vai trò của nhân viên. |
| `adminSales.clickEmployeeAction` | `name: string, action: 'Sửa' \| 'Xóa' \| 'Trạng thái'` | Bấm nút trên dòng nhân viên: "Sửa", "Xóa" (icon không title) hoặc "Trạng thái" (nút gạt). |
| `adminSales.verifyEmployeeActive` | `name: string, active: boolean` | Kiểm tra nút gạt trạng thái nhân viên đang bật (xanh) hay tắt (xám). |
| `adminSales.verifyEmployeeEmailNativeInvalid` | `editing = false` | Kiểm tra ô Email trong form nhân viên bị trình duyệt đánh dấu không hợp lệ (chặn submit). |

## adminMarketing

| Keyword | Tham số | Mô tả |
|---|---|---|
| `adminMarketing.verifyColumns` | `headers: string[]` | Kiểm tra bảng chính có đúng các cột theo thứ tự (đọc textContent, bỏ qua CSS viết hoa). |
| `adminMarketing.verifyRowCells` | `rowText: string, cells: Record<string, string>` | Kiểm tra các ô của dòng chứa text theo tên cột, vd: {"Trạng thái": "Hết hạn"}. |
| `adminMarketing.verifyCellPattern` | `rowIndex: number, column: string, pattern: string` | Kiểm tra ô ở cột `column` của dòng thứ `rowIndex` (0 = đầu) khớp biểu thức chính quy. |
| `adminMarketing.verifySelectedOption` | `label: string, text: string` | Kiểm tra chữ hiển thị của option đang chọn trong select (theo label của ô). |
| `adminMarketing.verifyRowCount` | `count: number` | Kiểm tra số dòng dữ liệu đang hiển thị trong bảng chính. |
| `adminMarketing.verifyRowsAtLeast` | `min: number` | Kiểm tra bảng có ít nhất `min` dòng dữ liệu thật (không phải dòng trạng thái rỗng). |
| `adminMarketing.verifyRowActions` | `rowText: string, titles: string[]` | Kiểm tra dòng chứa text có đúng các nút hành động (theo title, đúng thứ tự). |
| `adminMarketing.verifyVisibleRows` | `visible: string[], hidden: string[] = []` | Kiểm tra các dòng hiển thị/không hiển thị sau khi tìm kiếm hoặc lọc. |
| `adminMarketing.verifyModalText` | `heading: string, texts: string[]` | Kiểm tra modal có tiêu đề `heading` đang mở và chứa các đoạn text. |
| `adminMarketing.clickModalButton` | `heading: string, name: string` | Bấm nút theo tên bên trong modal có tiêu đề `heading`. |
| `adminMarketing.verifyListQuery` | `pathPart: string, params: Record<string, string \| null>` | Kiểm tra request GET danh sách gần nhất (qua API giả lập) có các tham số; null = không gửi tham số đó. |
| `adminMarketing.mockPromotionList` | `promotions: PromotionMock[]` | Giả lập danh sách + chi tiết khuyến mãi; startOffset/endOffset đổi thành ngày so với hôm nay. |
| `adminMarketing.openPromotions` | — | Mở trang Khuyến mãi và chờ danh sách tải xong. |
| `adminMarketing.openCreatePromotion` | — | Bấm "Thêm khuyến mãi" và chờ modal tạo mới. |
| `adminMarketing.mockCouponList` | `coupons: CouponMock[]` | Giả lập API GET danh sách mã giảm giá. |
| `adminMarketing.openCoupons` | — | Mở trang Mã giảm giá và chờ danh sách tải xong. |
| `adminMarketing.openCreateCoupon` | — | Bấm "Thêm mã" và chờ modal "Thêm mã giảm giá". |
| `adminMarketing.clickCouponEdit` | `code: string` | Bấm nút sửa (icon không tên) trên dòng mã giảm giá. |
| `adminMarketing.clickCouponDelete` | `code: string` | Bấm nút xóa (icon không tên) trên dòng mã giảm giá. |
| `adminMarketing.toggleCoupon` | `code: string, column: string` | Bấm nút bật/tắt ở cột "Công khai" hoặc "Trạng thái" của mã giảm giá. |
| `adminMarketing.verifyCouponToggle` | `code: string, column: string, on: boolean` | Kiểm tra nút bật/tắt ở cột của mã giảm giá đang bật (xanh) hay tắt (xám). |
| `adminMarketing.mockReviewList` | `reviews: ReviewMock[]` | Giả lập API GET đánh giá: lọc theo tham số status/rating như server. |
| `adminMarketing.openReviews` | — | Mở trang Đánh giá và chờ danh sách tải xong. |
| `adminMarketing.filterReviewStatus` | `value: string` | Chọn bộ lọc trạng thái đánh giá (all, pending, approved, hidden). |
| `adminMarketing.filterReviewRating` | `value: string` | Chọn bộ lọc số sao (all, 5, 4, 3, 2, 1). |
| `adminMarketing.mockBlogList` | `posts: BlogMock[]` | Giả lập API GET danh sách bài viết. |
| `adminMarketing.openBlog` | — | Mở trang Bài viết và chờ danh sách tải xong. |
| `adminMarketing.openCreateBlog` | — | Bấm "Thêm bài viết" và chờ modal tạo mới. |
| `adminMarketing.setBlogImage` | `url: string, error = ''` | Nhập URL ảnh bài viết và kiểm tra ảnh xem trước hoặc thông báo lỗi ảnh. |
| `adminMarketing.mockContactList` | `contacts: ContactMock[]` | Giả lập API GET liên hệ: lọc theo tham số status như server. |
| `adminMarketing.openContacts` | — | Mở trang Liên hệ và chờ danh sách tải xong. |
| `adminMarketing.filterContactStatus` | `value: string` | Chọn bộ lọc trạng thái liên hệ (all, pending, processed). |

## adminOps

| Keyword | Tham số | Mô tả |
|---|---|---|
| `adminOps.verifyColumns` | `headers: string[]` | Kiểm tra bảng chính có đúng các cột theo thứ tự (đọc textContent, bỏ qua CSS viết hoa). |
| `adminOps.verifyRowCells` | `rowText: string, cells: Record<string, string>` | Kiểm tra các ô của dòng chứa text theo tên cột, vd: {"Tồn kho": "3"}. |
| `adminOps.verifyRowCount` | `count: number` | Kiểm tra số dòng dữ liệu đang hiển thị trong bảng chính. |
| `adminOps.verifyRowsAtLeast` | `min: number` | Kiểm tra bảng có ít nhất `min` dòng dữ liệu thật (không phải dòng trạng thái rỗng). |
| `adminOps.verifyRowActions` | `rowText: string, titles: string[]` | Kiểm tra dòng chứa text có đúng các nút hành động (theo title, đúng thứ tự). |
| `adminOps.verifyVisibleRows` | `visible: string[], hidden: string[] = []` | Kiểm tra các dòng hiển thị/không hiển thị sau khi tìm kiếm hoặc lọc. |
| `adminOps.verifyModalText` | `heading: string, texts: string[]` | Kiểm tra modal có tiêu đề `heading` đang mở và chứa các đoạn text. |
| `adminOps.clickModalButton` | `heading: string, name: string` | Bấm nút theo tên bên trong modal có tiêu đề `heading`. |
| `adminOps.verifyStatCards` | `cards: Record<string, string>` | Kiểm tra các thẻ thống kê (nhãn -> giá trị), vd: {"Tổng đơn": "3"}. |
| `adminOps.verifyListQuery` | `pathPart: string, params: Record<string, string \| null>` | Kiểm tra request GET gần nhất (qua API giả lập) có các tham số; null = không gửi tham số đó. |
| `adminOps.mockWarehouse` | `data: WarehouseMock` | Giả lập API kho hàng: lọc sản phẩm theo tham số filter (all, low, out) như server. |
| `adminOps.openWarehouse` | — | Mở trang Kho hàng và chờ bảng tải xong. |
| `adminOps.selectWarehouseTab` | `label: string` | Bấm tab lọc kho ("Tất cả", "Sắp hết", "Hết hàng") và chờ bảng tải lại. |
| `adminOps.verifyWarehouseTabBadge` | `label: string, count: number \| null` | Kiểm tra số đếm trên tab kho; null = không hiển thị số. |
| `adminOps.verifyWarehouseStatsMatchList` | — | Kiểm tra thẻ "Tổng sản phẩm" bằng số dòng của tab "Tất cả" (dữ liệu thật). |
| `adminOps.mockImportData` | `data: ImportMockData` | Giả lập toàn bộ API GET của trang Nhập hàng (đơn nhập lọc theo status/supplier_id/search, NCC, kho, sản phẩm, chi tiết). |
| `adminOps.openImport` | — | Mở trang Nhập hàng và chờ bảng tải xong. |
| `adminOps.filterImportStatus` | `value: string` | Lọc đơn nhập theo trạng thái (draft, processing, partial_received, received, cancelled; rỗng = tất cả). |
| `adminOps.filterImportSupplier` | `name: string` | Lọc đơn nhập theo tên nhà cung cấp (rỗng = tất cả). |
| `adminOps.openCreateImport` | — | Bấm "Tạo đơn nhập hàng" và chờ modal tạo đơn. |
| `adminOps.addImportItemRow` | — | Bấm "Thêm sản phẩm" để thêm 1 dòng sản phẩm nhập. |
| `adminOps.fillImportItem` | `index: number, item: ImportItemInput` | Điền dòng sản phẩm nhập thứ `index` (0 = dòng đầu): sản phẩm, biến thể, số lượng, đơn giá, ghi chú. |
| `adminOps.verifyImportTotals` | `index: number, lineTotal: string, grandTotal: string` | Kiểm tra thành tiền dòng `index` và "Tổng tiền nhập" trong modal tạo đơn. |
| `adminOps.setReceiveQuantities` | `quantities: number[]` | Nhập "SL thực nhận" cho từng dòng trong modal Nhận hàng. |
| `adminOps.mockReportsOverview` | `overview: ReportOverviewMock` | Giả lập API tổng quan báo cáo (ghi lại tham số period/start_date/end_date). |
| `adminOps.openReports` | — | Mở trang Báo cáo và chờ thẻ tổng quan tải xong. |
| `adminOps.selectReportPeriod` | `value: string` | Chọn kỳ báo cáo theo value (today, last7days, last30days, thisMonth, custom). |
| `adminOps.applyCustomRange` | `start: string, end: string` | Ở kỳ "Tùy chọn": nhập từ ngày, đến ngày (YYYY-MM-DD) và bấm "Lọc". |
| `adminOps.verifyCustomRangeDefaults` | — | Kiểm tra kỳ "Tùy chọn" mặc định: từ ngày 1 tháng này đến hôm nay (giờ VN). |
| `adminOps.verifyReportSection` | `heading: string, rows: number, firstRow: string[]` | Kiểm tra bảng trong khối báo cáo có số dòng và dòng đầu chứa các text. |
| `adminOps.verifyReportSectionText` | `heading: string, texts: string[]` | Kiểm tra khối báo cáo (theo tiêu đề h2) chứa các đoạn text. |
| `adminOps.exportReport` | `filePattern: string, lines: string[]` | Bấm "Xuất báo cáo", kiểm tra tên file CSV (regex), BOM UTF-8 và các dòng nội dung. |
| `adminOps.mockSettings` | `settings: Record<string, string>` | Giả lập API GET cài đặt website. |
| `adminOps.openSettings` | — | Mở trang Cài đặt và chờ dữ liệu tải xong. |
| `adminOps.openSettingsTab` | `label: string` | Bấm 1 tab cài đặt, vd: "Bán hàng". |
| `adminOps.verifySettingsFields` | `labels: string[]` | Kiểm tra tab đang mở có đúng các nhãn ô nhập (theo thứ tự). |
| `adminOps.verifyCheckboxes` | `states: Record<string, boolean>` | Kiểm tra trạng thái các checkbox theo nhãn, vd: {"Cho phép COD": true}. |
| `adminOps.saveSettings` | — | Bấm "Lưu cài đặt". |

