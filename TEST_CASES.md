# Danh mục Test Case

> Tự sinh bởi `npm run docs:testcases` từ lần chạy **prod** lúc 16:30:30 2/10/2026. Đừng sửa tay.

## Tổng quan

| Module | Tổng | ✅ Đạt | 🐞 Bug đã biết | ❌ Lỗi | ⏭️ Bỏ qua | ⚠️ Bug đã sửa? |
|---|---|---|---|---|---|---|
| UI - Tài khoản khách hàng | 134 | 113 | 20 |  | 1 |  |
| UI - Quản trị | 20 | 19 | 1 |  |  |  |
| UI - Admin: Sản phẩm, Danh mục, Thương hiệu | 71 | 56 | 15 |  |  |  |
| UI - Admin: Khuyến mãi, Mã giảm giá, Đánh giá, Bài viết, Liên hệ | 128 | 119 | 9 |  |  |  |
| UI - Admin: Kho, Nhập hàng, Báo cáo, Cài đặt | 72 | 69 | 3 |  |  |  |
| UI - Admin: Layout, Dashboard, Đơn hàng, Khách hàng, Nhân viên | 127 | 112 | 15 |  |  |  |
| UI - Đăng nhập / Đăng ký | 20 | 17 | 2 |  | 1 |  |
| UI - Giỏ hàng | 10 | 10 |  |  |  |  |
| UI - Danh mục, Tìm kiếm, Sản phẩm | 14 | 13 | 1 |  |  |  |
| UI - Thanh toán | 14 | 13 |  |  | 1 |  |
| Kịch bản Keyword-driven | 40 | 39 | 1 |  |  |  |
| UI - Trang chủ & trang tĩnh | 10 | 10 |  |  |  |  |
| UI - Cửa hàng (trang chủ, danh sách, sản phẩm, blog, trang tĩnh) | 149 | 114 | 35 |  |  |  |
| UI - Mobile | 3 | 1 | 2 |  |  |  |
| API - Quản trị | 44 | 41 | 1 | 1 | 1 |  |
| API - Xác thực & Bảo mật | 23 | 19 |  | 3 | 1 |  |
| API - Health & Home | 3 | 3 |  |  |  |  |
| API - Sản phẩm | 7 | 6 | 1 |  |  |  |
| API - Lọc/Sắp xếp/Validate | 10 | 8 | 2 |  |  |  |
| **Tổng** | **899** | **782** | **108** | **4** | **5** | **0** |

Chú thích: 🐞 test đúng nhưng app còn bug (đánh dấu `test.fail`) · ❌ test fail (gồm lỗ hổng bảo mật cố ý để đỏ) · ⏭️ thiếu điều kiện (tài khoản / quyền ghi DB).

## Bug phát hiện

**108** test đang ghi nhận bug của app (`test.fail`) và **4** test bảo mật đang fail.

### ⚠️ Lỗ hổng bảo mật

| ID | Test case |
|---|---|
| API-QT-01 | POST /admin/upload không có token phải trả 401 |
| API-XTBM-21 | Không được đăng nhập admin bằng mật khẩu cứng "admin123" |
| API-XTBM-22 | Không được đăng nhập admin bằng mật khẩu cứng "manager123" |
| API-XTBM-23 | Không được đăng nhập admin bằng mật khẩu cứng "staff123" |

### Bug chức năng / giao diện (99 bug, gom theo mô tả)

| # | Module | Bug | Test |
|---|---|---|---|
| 1 | API - Lọc/Sắp xếp/Validate | ORDER BY created_at không có cột phụ (id) -> sản phẩm trùng/thiếu giữa các trang | API-PUB-P01 |
| 2 | API - Lọc/Sắp xếp/Validate | Backend không validate page, trả 500 'Không thể tải danh sách sản phẩm' | API-PUB-V04 |
| 3 | API - Quản trị | Backend không validate id, trả 500 thay vì 400/404 | API-ADM-N08 |
| 4 | API - Sản phẩm | query dùng hàm HEX() của MySQL trên Postgres -> 500 "function hex(character varying) does not exist" | API-SP-06 |
| 5 | UI - Admin: Kho, Nhập hàng, Báo cáo, Cài đặt | AdminReports.jsx:53,129 dateOnly() dùng toISOString (UTC) -> ở UTC+7 ngày 1 của tháng thành ngày cuối tháng trước | ADO-RPT-B01 |
| 6 | UI - Admin: Kho, Nhập hàng, Báo cáo, Cài đặt | adminController.js:1638-1655 PostgreSQL trả alias không đặt trong ngoặc kép thành chữ thường (totalproducts...) nên destructuring { totalProducts, ... } luôn undefined -> các thẻ thống kê kho luôn 0 | ADO-WH-B03 |
| 7 | UI - Admin: Kho, Nhập hàng, Báo cáo, Cài đặt | AdminWarehouse.jsx:39-40,111-113 đếm số trên tab từ danh sách đang lọc -> ở tab 'Sắp hết' tab 'Tất cả' thành 2 và số của 'Hết hàng' biến mất | ADO-WH-B02 |
| 8 | UI - Admin: Khuyến mãi, Mã giảm giá, Đánh giá, Bài viết, Liên hệ | AdminBlog.jsx:151 khi tạo mới luôn slugify lại tiêu đề -> ghi đè slug người dùng đã nhập | ADM-BLG-G03 |
| 9 | UI - Admin: Khuyến mãi, Mã giảm giá, Đánh giá, Bài viết, Liên hệ | AdminContacts.jsx:179 chỉ xét ô tìm kiếm -> lọc rỗng vẫn hiện 'Chưa có liên hệ nào' | ADM-CTC-F03 |
| 10 | UI - Admin: Khuyến mãi, Mã giảm giá, Đánh giá, Bài viết, Liên hệ | AdminCoupons.jsx:51 đọc err.response.data.error trong khi backend trả 'message' -> luôn hiện 'Lưu mã giảm giá thất bại' | ADM-CPN-E01 |
| 11 | UI - Admin: Khuyến mãi, Mã giảm giá, Đánh giá, Bài viết, Liên hệ | AdminCoupons.jsx:55 đưa chuỗi ISO có giờ vào input type=date -> 2 ô ngày bị trống khi sửa | ADM-CPN-B03 |
| 12 | UI - Admin: Khuyến mãi, Mã giảm giá, Đánh giá, Bài viết, Liên hệ | AdminCoupons.jsx:180 option ghi 'Khách hàng mới' nhưng bảng (dòng 80) ghi 'Khách mới' | ADM-CPN-B04 |
| 13 | UI - Admin: Khuyến mãi, Mã giảm giá, Đánh giá, Bài viết, Liên hệ | adminController.js:1565-1592 getCoupons/createCoupon không đọc/lưu coupon_type -> cột "Loại" (AdminCoupons.jsx:128) luôn trống | ADM-CPN-B01 |
| 14 | UI - Admin: Khuyến mãi, Mã giảm giá, Đánh giá, Bài viết, Liên hệ | AdminCoupons.jsx:133 in thẳng chuỗi ISO (vd: 2026-09-11T14:23:39.773Z) thay vì định dạng ngày | ADM-CPN-B02 |
| 15 | UI - Admin: Khuyến mãi, Mã giảm giá, Đánh giá, Bài viết, Liên hệ | AdminPromotions.jsx:247 luôn hiện 'Không thể lưu khuyến mãi. Vui lòng kiểm tra lại thông tin.', bỏ qua message server trả về (vd: 'Slug khuyến mãi đã tồn tại.') | ADM-PRO-E01 |
| 16 | UI - Admin: Khuyến mãi, Mã giảm giá, Đánh giá, Bài viết, Liên hệ | AdminReviews.jsx:216 chỉ xét ô tìm kiếm -> lọc rỗng vẫn hiện 'Chưa có đánh giá nào' | ADM-REV-F05 |
| 17 | UI - Admin: Layout, Dashboard, Đơn hàng, Khách hàng, Nhân viên | AdminCustomers.jsx:526 hiển thị mã trạng thái thô ('pending', 'delivered') thay vì nhãn tiếng Việt như trang Đơn hàng | ADS-CUS-13 |
| 18 | UI - Admin: Layout, Dashboard, Đơn hàng, Khách hàng, Nhân viên | AdminCustomers.jsx:55 chỉ kiểm tra độ dài mật khẩu khi THÊM (isNew) - khi sửa vẫn gửi mật khẩu 3 ký tự lên server | ADS-CUS-EV03 |
| 19 | UI - Admin: Layout, Dashboard, Đơn hàng, Khách hàng, Nhân viên | AdminCustomers.jsx:271 dãy nút trang luôn là 1..5 (không dịch theo trang hiện tại) -> không bấm trực tiếp được trang 6-8 | ADS-CUS-12 |
| 20 | UI - Admin: Layout, Dashboard, Đơn hàng, Khách hàng, Nhân viên | AdminDashboard.jsx:227-232 - ô chọn "7 ngày qua/30 ngày qua/..." không có onChange, không gọi lại API | ADS-DASH-07 |
| 21 | UI - Admin: Layout, Dashboard, Đơn hàng, Khách hàng, Nhân viên | AdminDashboard.jsx:196 - change="+12%" viết cứng, API không trả tăng trưởng đơn hàng | ADS-DASH-G01 |
| 22 | UI - Admin: Layout, Dashboard, Đơn hàng, Khách hàng, Nhân viên | AdminDashboard.jsx:209 - change="+8%" viết cứng, API không trả tăng trưởng khách hàng | ADS-DASH-G02 |
| 23 | UI - Admin: Layout, Dashboard, Đơn hàng, Khách hàng, Nhân viên | AdminDashboard.jsx:384 link tới /admin/orders?status=pending nhưng AdminOrders.jsx:80-83 không đọc query string -> không lọc | ADS-DASH-L06 |
| 24 | UI - Admin: Layout, Dashboard, Đơn hàng, Khách hàng, Nhân viên | adminController.deleteEmployee luôn trả 400 "Không thể xóa tài khoản nhân viên..." -> nút Xóa/Vô hiệu hóa ở AdminEmployees.jsx:112-121 không bao giờ thành công (phải dùng nút gạt) | ADS-EMP-08 |
| 25 | UI - Admin: Layout, Dashboard, Đơn hàng, Khách hàng, Nhân viên | AdminEmployees.jsx:65-67 nhánh catch vẫn đảo is_active nên nút gạt đổi màu dù API lỗi | ADS-EMP-10 |
| 26 | UI - Admin: Layout, Dashboard, Đơn hàng, Khách hàng, Nhân viên | AdminLayout.jsx:11,31 - map tiêu đề dùng khóa '/admin/products/edit' nhưng route thật là '/admin/products/edit/:id' -> header hiển thị 'Admin' | ADS-LAY-T04 |
| 27 | UI - Admin: Layout, Dashboard, Đơn hàng, Khách hàng, Nhân viên | AdminHeader.jsx:34 - totalNotif cộng TẤT CẢ giá trị counts (all + newOrders + lowStock + ...) nên đếm gấp đôi: 3 thông báo hiển thị 6 | ADS-NOTI-B02 |
| 28 | UI - Admin: Layout, Dashboard, Đơn hàng, Khách hàng, Nhân viên | AdminOrders.jsx:409 hiện nút Hủy đơn cho đơn 'shipped' nhưng adminController.cancelOrder trả 400 'Không thể hủy đơn hàng ở trạng thái này' | ADS-ORD-CA03 |
| 29 | UI - Admin: Layout, Dashboard, Đơn hàng, Khách hàng, Nhân viên | AdminOrders.jsx:160-168 pushNotification() rồi gọi ngay fetchNotifications(true) -> NotificationContext.jsx:55 ghi đè bằng danh sách từ server nên thông báo vừa đẩy biến mất | ADS-ORD-09 |
| 30 | UI - Admin: Layout, Dashboard, Đơn hàng, Khách hàng, Nhân viên | AdminOrders.jsx:700 kiểm tra order.points_used nhưng API danh sách (adminController.getOrders) chỉ trả points_discount -> không bao giờ báo hoàn điểm | ADS-ORD-13 |
| 31 | UI - Admin: Layout, Dashboard, Đơn hàng, Khách hàng, Nhân viên | AdminOrders.jsx:125-130 useEffect tải đơn chỉ phụ thuộc [filters], đổi trang không gọi lại API | ADS-ORD-15 |
| 32 | UI - Admin: Sản phẩm, Danh mục, Thương hiệu | AdminProductForm.jsx:187 - upload gửi Authorization từ localStorage 'token' (không tồn tại ở phiên admin) thay vì 'admin_token' -> header 'Bearer null' | ADC-PF-05 |
| 33 | UI - Admin: Sản phẩm, Danh mục, Thương hiệu | AdminProductForm.jsx:154-158 - NFD không tách 'đ' nên bị thay bằng '-' -> slug 'ao-khoac-en' | ADC-PF-S03 |
| 34 | UI - Admin: Sản phẩm, Danh mục, Thương hiệu | AdminProductForm.jsx:154-158 - 'Đ' đầu tên bị bỏ -> slug 'am-du-tiec' | ADC-PF-S04 |
| 35 | UI - Admin: Sản phẩm, Danh mục, Thương hiệu | AdminProductForm.jsx:57-89 - khi bấm Sửa từ danh sách, form lấy dữ liệu dòng trong sessionStorage (thiếu description/material/gender/variants) và return trước khi tải danh mục/thương hiệu -> ô Danh mục trống và lưu sẽ ghi đè mô tả/chất liệu/giới tính | ADC-PF-08, ADC-PF-09 |
| 36 | UI - Admin: Sản phẩm, Danh mục, Thương hiệu | AdminProducts.jsx:90-91 - nhánh catch vẫn đảo is_featured nên UI hiển thị sai sau khi API lỗi | ADC-PRD-FT03 |
| 37 | UI - Admin: Sản phẩm, Danh mục, Thương hiệu | AdminProducts.jsx:79-80 - nhánh catch vẫn đảo is_active nên nút gạt đổi trạng thái dù API lỗi | ADC-PRD-S03 |
| 38 | UI - Admin: Sản phẩm, Danh mục, Thương hiệu | AdminProducts.jsx:170 nút "Xóa đã chọn" không có onClick -> bấm không làm gì | ADC-PRD-08 |
| 39 | UI - Admin: Sản phẩm, Danh mục, Thương hiệu | AdminCategories.jsx:57-59 - catch gọi setShowForm(false) nên modal đóng, mất dữ liệu vừa nhập | ADC-CAT-06 |
| 40 | UI - Admin: Sản phẩm, Danh mục, Thương hiệu | AdminCategories.jsx:36-38 - nhánh catch vẫn đảo trạng thái nên nút gạt đổi dù API lỗi | ADC-CAT-12 |
| 41 | UI - Admin: Sản phẩm, Danh mục, Thương hiệu | AdminCategories.jsx:115 - badge 'Nổi bật' so sánh is_featured === 1 nhưng API (Postgres) trả boolean true -> không bao giờ hiện | ADC-CAT-13 |
| 42 | UI - Admin: Sản phẩm, Danh mục, Thương hiệu | AdminBrands.jsx:57-59 - catch gọi setShowForm(false) nên modal đóng, mất dữ liệu vừa nhập | ADC-BRD-06 |
| 43 | UI - Admin: Sản phẩm, Danh mục, Thương hiệu | AdminBrands.jsx:36-38 - nhánh catch vẫn đảo trạng thái nên nút gạt đổi dù API lỗi | ADC-BRD-12 |
| 44 | UI - Admin: Sản phẩm, Danh mục, Thương hiệu | AdminBrands.jsx:111 - badge 'Nổi bật' so sánh is_featured === 1 nhưng API (Postgres) trả boolean true -> không bao giờ hiện | ADC-BRD-13 |
| 45 | UI - Admin: Sản phẩm, Danh mục, Thương hiệu | AdminBrands.jsx:138 - slug chỉ giữ [a-z0-9], không bỏ dấu tiếng Việt -> 'th-ng-hi-u-test' | ADC-BRD-SL02 |
| 46 | UI - Cửa hàng (trang chủ, danh sách, sản phẩm, blog, trang tĩnh) | BlogPage.jsx:139 <form> không có onSubmit -> bấm "Đăng ký" submit form GET, tải lại trang, không có phản hồi | SF-BLOG-11 |
| 47 | UI - Cửa hàng (trang chủ, danh sách, sản phẩm, blog, trang tĩnh) | Footer.jsx:37 mọi link dùng to="#" (render href="/") -> không tới trang Đổi trả | SF-FOOT-02 |
| 48 | UI - Cửa hàng (trang chủ, danh sách, sản phẩm, blog, trang tĩnh) | Footer.jsx:47 mọi link dùng to="#" (render href="/") -> không tới trang Giới thiệu | SF-FOOT-03 |
| 49 | UI - Cửa hàng (trang chủ, danh sách, sản phẩm, blog, trang tĩnh) | Footer.jsx:36 thiếu link tới /shipping (trang chỉ vào được bằng URL) | SF-FOOT-04 |
| 50 | UI - Cửa hàng (trang chủ, danh sách, sản phẩm, blog, trang tĩnh) | Footer.jsx:36 thiếu link tới /privacy (trang chỉ vào được bằng URL) | SF-FOOT-05 |
| 51 | UI - Cửa hàng (trang chủ, danh sách, sản phẩm, blog, trang tĩnh) | Banner.jsx:109 nút "Khám phá ngay" dùng banner.cta (API không có) -> luôn trỏ /nam thay vì link_url | SF-HOME-07 |
| 52 | UI - Cửa hàng (trang chủ, danh sách, sản phẩm, blog, trang tĩnh) | Home.jsx:76-87 các tab SẢN PHẨM MỚI không có onClick -> không đổi tab, không lọc | SF-HOME-11, SF-HOME-12 |
| 53 | UI - Cửa hàng (trang chủ, danh sách, sản phẩm, blog, trang tĩnh) | CollectionSection.jsx:54 đọc collection.ctaText nhưng API trả cta_text -> nút CTA trống chữ | SF-HOME-17, SF-HOME-18 |
| 54 | UI - Cửa hàng (trang chủ, danh sách, sản phẩm, blog, trang tĩnh) | ProductCard.jsx:37 addItem(product, 1, null, null) -> sản phẩm vào giỏ không có size/màu | SF-HOME-25 |
| 55 | UI - Cửa hàng (trang chủ, danh sách, sản phẩm, blog, trang tĩnh) | Home.jsx:69 href="/products" nhưng App.jsx không có route /products -> trang trắng | SF-HOME-21 |
| 56 | UI - Cửa hàng (trang chủ, danh sách, sản phẩm, blog, trang tĩnh) | Home.jsx:154 href="/homewear" không có route -> trang trắng | SF-HOME-22 |
| 57 | UI - Cửa hàng (trang chủ, danh sách, sản phẩm, blog, trang tĩnh) | Home.jsx:220 href="/products?category=tshirt" không có route /products -> trang trắng | SF-HOME-23 |
| 58 | UI - Cửa hàng (trang chủ, danh sách, sản phẩm, blog, trang tĩnh) | Home.jsx:246 href="/products?category=vay" không có route /products -> trang trắng | SF-HOME-24 |
| 59 | UI - Cửa hàng (trang chủ, danh sách, sản phẩm, blog, trang tĩnh) | ProductFilters.jsx handleApply gọi API mỗi lần blur, MenPage không hủy request cũ -> kết quả cũ ghi đè | SF-LST-RACE |
| 60 | UI - Cửa hàng (trang chủ, danh sách, sản phẩm, blog, trang tĩnh) | ProductFilters.jsx:88 SizeFilter gọi onChange(size.id) (chuỗi) thay vì mảng -> selectedSizes.join/.some lỗi; MenPage.jsx:144 không gửi request, danh sách rỗng | SF-LST-33 |
| 61 | UI - Cửa hàng (trang chủ, danh sách, sản phẩm, blog, trang tĩnh) | ProductFilters.jsx:88 SizeFilter gọi onChange(size.id) (chuỗi) thay vì mảng -> selectedSizes.join/.some lỗi; WomenPage.jsx không gửi request, danh sách rỗng | SF-LST-34 |
| 62 | UI - Cửa hàng (trang chủ, danh sách, sản phẩm, blog, trang tĩnh) | ProductFilters.jsx:88 SizeFilter gọi onChange(size.id) (chuỗi) thay vì mảng -> selectedSizes.join/.some lỗi; KidsPage.jsx:154 không gửi request, danh sách rỗng | SF-LST-35 |
| 63 | UI - Cửa hàng (trang chủ, danh sách, sản phẩm, blog, trang tĩnh) | ProductFilters.jsx:88 SizeFilter gọi onChange(size.id) (chuỗi) thay vì mảng -> selectedSizes.join/.some lỗi; SalePage.jsx:138 selectedSizes.some không phải hàm -> trang crash | SF-LST-36 |
| 64 | UI - Cửa hàng (trang chủ, danh sách, sản phẩm, blog, trang tĩnh) | MenPage.jsx:424 nút "Xem thêm sản phẩm" không có onClick | SF-LST-39 |
| 65 | UI - Cửa hàng (trang chủ, danh sách, sản phẩm, blog, trang tĩnh) | Nút yêu thích nằm trong <Link> và không có onClick -> bấm tim lại mở trang chi tiết, không thêm vào yêu thích | SF-LST-52, SF-LST-53, SF-LST-54, SF-LST-55 |
| 66 | UI - Cửa hàng (trang chủ, danh sách, sản phẩm, blog, trang tĩnh) | ProductDetailPage.jsx:449,453 formatPrice() đã thêm "đ" rồi JSX thêm " đ" -> hiển thị "449.000đ đ" | SF-PDP-07 |
| 67 | UI - Cửa hàng (trang chủ, danh sách, sản phẩm, blog, trang tĩnh) | ProductDetailPage.jsx:109 ghi "trên 599.000 đ" trong khi ShippingPage.jsx:91, CartPage.jsx:51 và cài đặt backend dùng 500.000đ | SF-PDP-10 |
| 68 | UI - Cửa hàng (trang chủ, danh sách, sản phẩm, blog, trang tĩnh) | ProductDetailPage.jsx:283 catch luôn hiện "Không thể gửi đánh giá. Vui lòng thử lại.", bỏ qua message của server | SF-PDP-18 |
| 69 | UI - Cửa hàng (trang chủ, danh sách, sản phẩm, blog, trang tĩnh) | ProductDetailPage.jsx:283 catch luôn hiện thông báo chung, bỏ qua message của server | SF-PDP-19 |
| 70 | UI - Cửa hàng (trang chủ, danh sách, sản phẩm, blog, trang tĩnh) | ProductDetailPage.jsx:255 cho phép >=5 ký tự nhưng customerController.js:890 yêu cầu >=10; và :283 nuốt message server | SF-PDP-20 |
| 71 | UI - Cửa hàng (trang chủ, danh sách, sản phẩm, blog, trang tĩnh) | ReturnsPage.jsx:21 "không có запаh hư" chứa chữ Nga (Cyrillic) trong câu tiếng Việt | SF-STAT-05 |
| 72 | UI - Cửa hàng (trang chủ, danh sách, sản phẩm, blog, trang tĩnh) | ShippingPage.jsx:11 ghi 35.000đ nhưng CheckoutPage.jsx:72 tính 30.000đ cho giao hàng nhanh (tiêu chuẩn miễn phí, trang ghi 25.000đ) | SF-STAT-06 |
| 73 | UI - Cửa hàng (trang chủ, danh sách, sản phẩm, blog, trang tĩnh) | App.jsx:75-129 không có <Route path="*"> -> trang trắng, không header/footer | SF-STAT-07 |
| 74 | UI - Cửa hàng (trang chủ, danh sách, sản phẩm, blog, trang tĩnh) | App.jsx:75-129 không có route /products và không có route "*" -> trang trắng | SF-STAT-08 |
| 75 | UI - Cửa hàng (trang chủ, danh sách, sản phẩm, blog, trang tĩnh) | App.jsx:75-129 không có route /collections/:slug và không có route "*" -> trang trắng | SF-STAT-09 |
| 76 | UI - Đăng nhập / Đăng ký | Interceptor 401 trong services/api.js reload sang /login nên thông báo lỗi bị mất | LOGIN-S01, LOGIN-S02, KD-ACC-03 |
| 77 | UI - Danh mục, Tìm kiếm, Sản phẩm | ProductDetailPage hiển thị mockProduct (sản phẩm giả) khi API trả 404 | UI-DMTK-06 |
| 78 | UI - Mobile | header tràn ngang trên mobile, nút menu nằm ngoài màn hình | MOB-M-02 |
| 79 | UI - Mobile | ô tìm kiếm w-48 cố định làm header rộng hơn màn hình (~64px) | MOB-M-03 |
| 80 | UI - Quản trị | interceptor 401 trong services/api.js reload sang /admin/login nên thông báo lỗi bị mất | UI-QT-02 |
| 81 | UI - Tài khoản khách hàng | profileToForm(null) ở lần render đầu -> crash 'Cannot read properties of null (reading name)' | UI-TKKH-02 |
| 82 | UI - Tài khoản khách hàng | AddressesPage.jsx:218 thêm địa chỉ mặc định vào đầu danh sách nhưng không bỏ is_default của địa chỉ cũ (backend đã bỏ) -> 2 badge "Mặc định" | ACC-ADR-03 |
| 83 | UI - Tài khoản khách hàng | AddressesPage.jsx:226 đặt is_default = 0 (số) và dòng 331 render {addr.is_default && ...} -> React in ra chữ "0" cạnh tên người nhận | ACC-ADR-07 |
| 84 | UI - Tài khoản khách hàng | AddressesPage.jsx:235 chỉ lọc bỏ địa chỉ đã xóa, không tải lại danh sách; backend (customerController.js deleteAddress) đã chuyển mặc định sang địa chỉ khác nhưng UI không có badge "Mặc định" nào | ACC-ADR-10 |
| 85 | UI - Tài khoản khách hàng | AddressesPage.jsx:220 - catch {} nuốt lỗi POST /addresses, form vẫn mở nhưng không có thông báo nào | ACC-ADR-E01 |
| 86 | UI - Tài khoản khách hàng | OrderSuccessPage.jsx:188 luôn ghi "Đã xác nhận" cho COD, trong khi backend tạo đơn với status "pending" (Chờ xác nhận) | ACC-CO-03 |
| 87 | UI - Tài khoản khách hàng | CheckoutPage.jsx:541 gửi payment_method 'bank' nhưng CHECK của orders.payment_method (database/schema.pg.sql:417) chỉ nhận 'bank_transfer' -> backend 500; CheckoutPage.jsx:169 còn đặt payment_status 'paid' khi chưa thanh toán | ACC-CO-M02 |
| 88 | UI - Tài khoản khách hàng | CheckoutPage.jsx:169 đặt payment_status 'paid' cho mọi phương thức khác COD ngay khi tạo đơn, trước khi khách thanh toán | ACC-CO-M03, ACC-CO-M04 |
| 89 | UI - Tài khoản khách hàng | OrderDetailPage.jsx:22,28 dùng nhãn "Trả hàng" / "Thanh toán 1 phần", khác accountUtils.js:36,42 của trang danh sách ("Đã trả hàng" / "Thanh toán một phần") | ACC-ODT-03 |
| 90 | UI - Tài khoản khách hàng | OrderDetailPage.jsx:156 - catch {} nuốt lỗi hủy đơn, hộp thoại vẫn mở và không có thông báo nào | ACC-ODT-07 |
| 91 | UI - Tài khoản khách hàng | OrderDetailPage.jsx:139-140 - mọi lỗi HTTP (kể cả 404 'Không tìm thấy đơn hàng' của backend) đều vào catch -> luôn hiện 'Không thể tải thông tin đơn hàng'; nhánh 'Không tìm thấy đơn hàng' (dòng 137) không bao giờ chạy | ACC-ODT-E01 |
| 92 | UI - Tài khoản khách hàng | OrdersPage.jsx:87-88 - lỗi POST /orders/:id/cancel chỉ gọi lại fetchOrders(), không hiển thị thông báo -> khách không biết vì sao hủy không được | ACC-ORD-C02 |
| 93 | UI - Tài khoản khách hàng | OrderListItem.jsx:25 chỉ cho hủy khi status = 'pending', trong khi backend (customerController.js cancelOrder) và OrderDetailPage.jsx:202 cho hủy cả 'confirmed' | ACC-ORD-B02 |
| 94 | UI - Tài khoản khách hàng | ProfilePage.jsx:252-253 - catch nuốt lỗi PUT /profile, chỉ reset form, không hiển thị thông báo nào | ACC-PRF-E03 |
| 95 | UI - Tài khoản khách hàng | ProfilePage.jsx:33-37 - PasswordModal luôn được mount, state form/error giữ nguyên khi đóng (chỉ reset sau khi đổi thành công) -> mở lại vẫn thấy mật khẩu cũ và lỗi cũ | ACC-PWD-03 |
| 96 | UI - Tài khoản khách hàng | ProfilePage.jsx:185 chỉ lấy 10 đơn (limit 10) và ProfileSummary.jsx:22 đếm orders.length thay vì pagination.total -> "Tổng đơn hàng" tối đa là 10 | ACC-PRF-S03 |
| 97 | UI - Tài khoản khách hàng | LoginPage.jsx:94 (và :25) luôn navigate('/profile'), bỏ qua location.state.from = '/checkout' mà CheckoutPage.jsx:330 truyền sang | ACC-RD-06 |
| 98 | UI - Tài khoản khách hàng | ProfilePage.jsx:165 useState(profileToForm(user)) với user = null ở lần render đầu (default param của profileToForm dòng 139 không áp dụng cho null) -> crash 'Cannot read properties of null', ErrorBoundary hiện 'Đã xảy ra lỗi' nên useEffect chuyển /login (dòng 170) không bao giờ chạy | ACC-RD-01 |
| 99 | UI - Tài khoản khách hàng | MenPage.jsx:391 (và KidsPage.jsx:347) - nút trái tim không có onClick, nằm trong <Link>; không nơi nào gọi POST /api/wishlist nên khách không thể thêm yêu thích | ACC-WL-H01 |

## UI - Tài khoản khách hàng

| ID | Test case | Project | Kết quả | Ghi chú |
|---|---|---|---|---|
| UI-TKKH-01 | Chưa đăng nhập: icon tài khoản dẫn tới trang đăng nhập | chromium | ✅ Đạt |  |
| UI-TKKH-02 | Mở trực tiếp /profile (F5, bookmark) hiển thị thông tin tài khoản | chromium | 🐞 Bug đã biết | BUG: profileToForm(null) ở lần render đầu -> crash 'Cannot read properties of null (reading name)' |
| UI-TKKH-03 | Vào hồ sơ qua menu tài khoản hiển thị thông tin @smoke | chromium | ✅ Đạt |  |
| UI-TKKH-04 | Vào /login khi đã đăng nhập sẽ chuyển sang /profile | chromium | ✅ Đạt |  |
| UI-TKKH-05 | Menu tài khoản điều hướng tới Đơn hàng và Yêu thích | chromium | ✅ Đạt |  |
| UI-TKKH-06 | Đăng xuất xóa token và về trang chủ | chromium | ✅ Đạt |  |
| ACC-ADR-E01 | Chưa có địa chỉ › Hiển thị màn hình trống | chromium | ✅ Đạt |  |
| ACC-ADR-E02 | Chưa có địa chỉ › Thêm địa chỉ đầu tiên từ màn hình trống: server đặt làm mặc định | chromium | ✅ Đạt |  |
| ACC-ADR-01 | Có địa chỉ › Danh sách địa chỉ: thông tin thẻ và địa chỉ mặc định @smoke | chromium | ✅ Đạt |  |
| ACC-ADR-02 | Có địa chỉ › Thêm địa chỉ mới (SĐT có khoảng trắng hợp lệ): gửi đúng payload, hiện thẻ mới @smoke | chromium | ✅ Đạt |  |
| ACC-ADR-03 | Có địa chỉ › Thêm địa chỉ mặc định mới: chỉ còn 1 badge Mặc định | chromium | 🐞 Bug đã biết | BUG: AddressesPage.jsx:218 thêm địa chỉ mặc định vào đầu danh sách nhưng không bỏ is_default của địa chỉ cũ (backend đã bỏ) -> 2 badge "Mặc định" |
| ACC-ADR-04 | Có địa chỉ › Hủy form thêm: đóng form, không gửi request | chromium | ✅ Đạt |  |
| ACC-ADR-05 | Có địa chỉ › Sửa địa chỉ: form điền sẵn, gửi PUT, thẻ cập nhật | chromium | ✅ Đạt |  |
| ACC-ADR-06 | Có địa chỉ › Đặt làm mặc định: gửi PUT isDefault, badge chuyển sang địa chỉ mới | chromium | ✅ Đạt |  |
| ACC-ADR-07 | Có địa chỉ › Sau khi đổi mặc định, thẻ địa chỉ không hiện ký tự "0" thừa | chromium | 🐞 Bug đã biết | BUG: AddressesPage.jsx:226 đặt is_default = 0 (số) và dòng 331 render {addr.is_default && ...} -> React in ra chữ "0" cạnh tên người nhận |
| ACC-ADR-08 | Có địa chỉ › Xóa địa chỉ: hộp xác nhận, gửi DELETE, thẻ biến mất | chromium | ✅ Đạt |  |
| ACC-ADR-09 | Có địa chỉ › Hủy xóa: không gửi request, danh sách giữ nguyên | chromium | ✅ Đạt |  |
| ACC-ADR-10 | Có địa chỉ › Xóa địa chỉ mặc định: địa chỉ còn lại được hiển thị là mặc định | chromium | 🐞 Bug đã biết | BUG: AddressesPage.jsx:235 chỉ lọc bỏ địa chỉ đã xóa, không tải lại danh sách; backend (customerController.js deleteAddress) đã chuyển mặc định sang địa chỉ khác nhưng UI không có badge "Mặc định" nào |
| ACC-ADR-E01 | Có địa chỉ › Lỗi server khi thêm địa chỉ hiển thị thông báo lỗi | chromium | 🐞 Bug đã biết | BUG: AddressesPage.jsx:220 - catch {} nuốt lỗi POST /addresses, form vẫn mở nhưng không có thông báo nào |
| ACC-ADR-V01 | Có địa chỉ › Validate form thêm địa chỉ (data-driven) › Bỏ trống toàn bộ trường bắt buộc | chromium | ✅ Đạt |  |
| ACC-ADR-V02 | Có địa chỉ › Validate form thêm địa chỉ (data-driven) › Họ tên chỉ có khoảng trắng | chromium | ✅ Đạt |  |
| ACC-ADR-V03 | Có địa chỉ › Validate form thêm địa chỉ (data-driven) › Số điện thoại quá ngắn | chromium | ✅ Đạt |  |
| ACC-ADR-V04 | Có địa chỉ › Validate form thêm địa chỉ (data-driven) › Số điện thoại không bắt đầu bằng 0 | chromium | ✅ Đạt |  |
| ACC-ADR-V05 | Có địa chỉ › Validate form thêm địa chỉ (data-driven) › Số điện thoại quá dài (12 số) | chromium | ✅ Đạt |  |
| ACC-ADR-V06 | Có địa chỉ › Validate form thêm địa chỉ (data-driven) › Chưa chọn tỉnh/thành phố | chromium | ✅ Đạt |  |
| ACC-CO-05 | Đặt hàng thật bằng Chuyển khoản ngân hàng (ghi DB) | chromium | ⏭️ Bỏ qua | Cần E2E_ALLOW_WRITE=1 (ghi dữ liệu thật) |
| ACC-CO-P01 | Điền sẵn thông tin từ tài khoản (data-driven) › Tên 3 từ: từ cuối vào ô Tên, phần còn lại vào ô Họ, điền sẵn SĐT | chromium | ✅ Đạt |  |
| ACC-CO-P02 | Điền sẵn thông tin từ tài khoản (data-driven) › Tên 4 từ, tài khoản chưa có SĐT -> ô SĐT trống | chromium | ✅ Đạt |  |
| ACC-CO-P03 | Điền sẵn thông tin từ tài khoản (data-driven) › Tên 1 từ -> chỉ điền ô Tên, ô Họ trống | chromium | ✅ Đạt |  |
| ACC-CO-01 | Có sản phẩm trong giỏ › Đăng xuất ngay trên trang thanh toán: chuyển sang chế độ khách, giữ giỏ hàng | chromium | ✅ Đạt |  |
| ACC-CO-02 | Có sản phẩm trong giỏ › Đặt hàng COD thành công: trang thành công hiển thị đủ thông tin @smoke | chromium | ✅ Đạt |  |
| ACC-CO-03 | Có sản phẩm trong giỏ › Trang thành công (COD) hiển thị đúng trạng thái đơn vừa tạo | chromium | 🐞 Bug đã biết | BUG: OrderSuccessPage.jsx:188 luôn ghi "Đã xác nhận" cho COD, trong khi backend tạo đơn với status "pending" (Chờ xác nhận) |
| ACC-CO-04 | Có sản phẩm trong giỏ › Từ trang thành công bấm Xem đơn hàng thấy đơn vừa đặt | chromium | ✅ Đạt |  |
| ACC-CO-M01 | Có sản phẩm trong giỏ › Payload tạo đơn theo phương thức thanh toán (mock, data-driven) › COD: payment_method cod, chưa thanh toán, gửi email tài khoản | chromium | ✅ Đạt |  |
| ACC-CO-M02 | Có sản phẩm trong giỏ › Payload tạo đơn theo phương thức thanh toán (mock, data-driven) › Chuyển khoản: gửi payment_method hợp lệ với DB (bank_transfer) và chưa thanh toán | chromium | 🐞 Bug đã biết | BUG: CheckoutPage.jsx:541 gửi payment_method 'bank' nhưng CHECK của orders.payment_method (database/schema.pg.sql:417) chỉ nhận 'bank_transfer' -> backend 500; CheckoutPage.jsx:169 còn đặt payment_status 'paid' khi chưa thanh toán |
| ACC-CO-M03 | Có sản phẩm trong giỏ › Payload tạo đơn theo phương thức thanh toán (mock, data-driven) › VNPay: đơn mới tạo phải ở trạng thái chưa thanh toán | chromium | 🐞 Bug đã biết | BUG: CheckoutPage.jsx:169 đặt payment_status 'paid' cho mọi phương thức khác COD ngay khi tạo đơn, trước khi khách thanh toán |
| ACC-CO-M04 | Có sản phẩm trong giỏ › Payload tạo đơn theo phương thức thanh toán (mock, data-driven) › MoMo: đơn mới tạo phải ở trạng thái chưa thanh toán | chromium | 🐞 Bug đã biết | BUG: CheckoutPage.jsx:169 đặt payment_status 'paid' cho mọi phương thức khác COD ngay khi tạo đơn, trước khi khách thanh toán |
| ACC-ODT-01 | Đơn chờ xác nhận: thông tin, sản phẩm, giảm giá, phí giao nhanh @smoke | chromium | ✅ Đạt |  |
| ACC-ODT-02 | Đơn đã giao: miễn phí vận chuyển, có mã vận đơn, không có dòng giảm giá | chromium | ✅ Đạt |  |
| ACC-ODT-03 | Nhãn trạng thái/thanh toán thống nhất với trang danh sách (trả hàng, thanh toán một phần) | chromium | 🐞 Bug đã biết | BUG: OrderDetailPage.jsx:22,28 dùng nhãn "Trả hàng" / "Thanh toán 1 phần", khác accountUtils.js:36,42 của trang danh sách ("Đã trả hàng" / "Thanh toán một phần") |
| ACC-ODT-08 | Màn hình lỗi: nút Quay lại đơn hàng về /orders | chromium | ✅ Đạt |  |
| ACC-ODT-09 | Nút Quay lại ở đầu trang chi tiết về danh sách đơn | chromium | ✅ Đạt |  |
| ACC-ODT-C01 | Nút Hủy đơn hàng theo trạng thái (data-driven) › Chờ xác nhận -> có nút Hủy đơn hàng | chromium | ✅ Đạt |  |
| ACC-ODT-C02 | Nút Hủy đơn hàng theo trạng thái (data-driven) › Đã xác nhận -> có nút Hủy đơn hàng | chromium | ✅ Đạt |  |
| ACC-ODT-C03 | Nút Hủy đơn hàng theo trạng thái (data-driven) › Đang xử lý -> không cho hủy | chromium | ✅ Đạt |  |
| ACC-ODT-C04 | Nút Hủy đơn hàng theo trạng thái (data-driven) › Đang giao -> không cho hủy | chromium | ✅ Đạt |  |
| ACC-ODT-C05 | Nút Hủy đơn hàng theo trạng thái (data-driven) › Đã giao -> không cho hủy | chromium | ✅ Đạt |  |
| ACC-ODT-C06 | Nút Hủy đơn hàng theo trạng thái (data-driven) › Đã hủy -> không cho hủy | chromium | ✅ Đạt |  |
| ACC-ODT-04 | Hủy đơn từ trang chi tiết › Hủy có lý do: gửi lý do, đóng hộp thoại, trạng thái thành Đã hủy | chromium | ✅ Đạt |  |
| ACC-ODT-05 | Hủy đơn từ trang chi tiết › Hủy không nhập lý do: gửi reason rỗng | chromium | ✅ Đạt |  |
| ACC-ODT-06 | Hủy đơn từ trang chi tiết › Đóng hộp xác nhận: không gửi request, đơn giữ nguyên | chromium | ✅ Đạt |  |
| ACC-ODT-07 | Hủy đơn từ trang chi tiết › Hủy thất bại hiển thị thông báo lỗi từ server | chromium | 🐞 Bug đã biết | BUG: OrderDetailPage.jsx:156 - catch {} nuốt lỗi hủy đơn, hộp thoại vẫn mở và không có thông báo nào |
| ACC-ODT-E01 | Lỗi tải đơn hàng (mock, data-driven) › Đơn không tồn tại (404) hiển thị Không tìm thấy đơn hàng | chromium | 🐞 Bug đã biết | BUG: OrderDetailPage.jsx:139-140 - mọi lỗi HTTP (kể cả 404 'Không tìm thấy đơn hàng' của backend) đều vào catch -> luôn hiện 'Không thể tải thông tin đơn hàng'; nhánh 'Không tìm thấy đơn hàng' (dòng 137) không bao giờ chạy |
| ACC-ODT-E02 | Lỗi tải đơn hàng (mock, data-driven) › Lỗi server (500) hiển thị Không thể tải thông tin đơn hàng | chromium | ✅ Đạt |  |
| ACC-ORD-E01 | Tài khoản chưa có đơn: thống kê 0 và thông báo trống | chromium | ✅ Đạt |  |
| ACC-ORD-01 | Có đơn hàng › Hiển thị thống kê và toàn bộ đơn (mới nhất trước) @smoke | chromium | ✅ Đạt |  |
| ACC-ORD-S05 | Có đơn hàng › Kết hợp tab và tìm kiếm: mã đúng nhưng khác trạng thái -> không có kết quả | chromium | ✅ Đạt |  |
| ACC-ORD-C01 | Có đơn hàng › Hủy đơn chờ xác nhận: gửi lý do mặc định, đổi trạng thái và thống kê @smoke | chromium | ✅ Đạt |  |
| ACC-ORD-C02 | Có đơn hàng › Hủy đơn thất bại hiển thị thông báo lỗi cho khách | chromium | 🐞 Bug đã biết | BUG: OrdersPage.jsx:87-88 - lỗi POST /orders/:id/cancel chỉ gọi lại fetchOrders(), không hiển thị thông báo -> khách không biết vì sao hủy không được |
| ACC-ORD-D01 | Có đơn hàng › Xem chi tiết từ danh sách mở đúng trang chi tiết đơn | chromium | ✅ Đạt |  |
| ACC-ORD-N01 | Có đơn hàng › Sidebar: chuyển sang Yêu thích rồi Hồ sơ (điều hướng trong app) | chromium | ✅ Đạt |  |
| ACC-ORD-N02 | Có đơn hàng › Đăng xuất từ sidebar về trang chủ và xóa token | chromium | ✅ Đạt |  |
| ACC-ORD-T01 | Có đơn hàng › Lọc theo tab trạng thái (data-driven) › Tab Tất cả hiển thị mọi đơn | chromium | ✅ Đạt |  |
| ACC-ORD-T02 | Có đơn hàng › Lọc theo tab trạng thái (data-driven) › Tab Chờ xác nhận | chromium | ✅ Đạt |  |
| ACC-ORD-T03 | Có đơn hàng › Lọc theo tab trạng thái (data-driven) › Tab Đã xác nhận | chromium | ✅ Đạt |  |
| ACC-ORD-T04 | Có đơn hàng › Lọc theo tab trạng thái (data-driven) › Tab Đang xử lý | chromium | ✅ Đạt |  |
| ACC-ORD-T05 | Có đơn hàng › Lọc theo tab trạng thái (data-driven) › Tab Đang giao | chromium | ✅ Đạt |  |
| ACC-ORD-T06 | Có đơn hàng › Lọc theo tab trạng thái (data-driven) › Tab Đã giao | chromium | ✅ Đạt |  |
| ACC-ORD-T07 | Có đơn hàng › Lọc theo tab trạng thái (data-driven) › Tab Đã hủy | chromium | ✅ Đạt |  |
| ACC-ORD-K01 | Có đơn hàng › Lọc bằng ô thống kê (data-driven) › Ô thống kê Đang giao lọc danh sách | chromium | ✅ Đạt |  |
| ACC-ORD-K02 | Có đơn hàng › Lọc bằng ô thống kê (data-driven) › Ô thống kê Đã hủy lọc danh sách | chromium | ✅ Đạt |  |
| ACC-ORD-S01 | Có đơn hàng › Tìm theo mã đơn (data-driven) › Tìm đúng mã đơn | chromium | ✅ Đạt |  |
| ACC-ORD-S02 | Có đơn hàng › Tìm theo mã đơn (data-driven) › Tìm không phân biệt hoa thường, theo 1 phần mã | chromium | ✅ Đạt |  |
| ACC-ORD-S03 | Có đơn hàng › Tìm theo mã đơn (data-driven) › Tìm có khoảng trắng đầu/cuối | chromium | ✅ Đạt |  |
| ACC-ORD-S04 | Có đơn hàng › Tìm theo mã đơn (data-driven) › Không có đơn phù hợp hiển thị thông báo | chromium | ✅ Đạt |  |
| ACC-ORD-L01 | Có đơn hàng › Thông tin từng đơn: nhãn trạng thái, thanh toán, vận chuyển (data-driven) › Đơn chờ xác nhận - COD, giao nhanh | chromium | ✅ Đạt |  |
| ACC-ORD-L02 | Có đơn hàng › Thông tin từng đơn: nhãn trạng thái, thanh toán, vận chuyển (data-driven) › Đơn đã xác nhận - VNPay đã thanh toán | chromium | ✅ Đạt |  |
| ACC-ORD-L03 | Có đơn hàng › Thông tin từng đơn: nhãn trạng thái, thanh toán, vận chuyển (data-driven) › Đơn đang xử lý - MoMo | chromium | ✅ Đạt |  |
| ACC-ORD-L04 | Có đơn hàng › Thông tin từng đơn: nhãn trạng thái, thanh toán, vận chuyển (data-driven) › Đơn đang giao - chuyển khoản, thanh toán một phần, chỉ hiện 2 tên sản phẩm | chromium | ✅ Đạt |  |
| ACC-ORD-L05 | Có đơn hàng › Thông tin từng đơn: nhãn trạng thái, thanh toán, vận chuyển (data-driven) › Đơn đã giao | chromium | ✅ Đạt |  |
| ACC-ORD-L06 | Có đơn hàng › Thông tin từng đơn: nhãn trạng thái, thanh toán, vận chuyển (data-driven) › Đơn đã hủy | chromium | ✅ Đạt |  |
| ACC-ORD-L07 | Có đơn hàng › Thông tin từng đơn: nhãn trạng thái, thanh toán, vận chuyển (data-driven) › Đơn trả hàng - đã hoàn tiền | chromium | ✅ Đạt |  |
| ACC-ORD-B01 | Có đơn hàng › Nút Hủy đơn theo trạng thái (data-driven) › Đơn Chờ xác nhận có nút Hủy đơn | chromium | ✅ Đạt |  |
| ACC-ORD-B02 | Có đơn hàng › Nút Hủy đơn theo trạng thái (data-driven) › Đơn Đã xác nhận có nút Hủy đơn (backend và trang chi tiết cho phép hủy) | chromium | 🐞 Bug đã biết | BUG: OrderListItem.jsx:25 chỉ cho hủy khi status = 'pending', trong khi backend (customerController.js cancelOrder) và OrderDetailPage.jsx:202 cho hủy cả 'confirmed' |
| ACC-ORD-B03 | Có đơn hàng › Nút Hủy đơn theo trạng thái (data-driven) › Đơn Đang xử lý không có nút Hủy đơn | chromium | ✅ Đạt |  |
| ACC-ORD-B04 | Có đơn hàng › Nút Hủy đơn theo trạng thái (data-driven) › Đơn Đang giao không có nút Hủy đơn | chromium | ✅ Đạt |  |
| ACC-ORD-B05 | Có đơn hàng › Nút Hủy đơn theo trạng thái (data-driven) › Đơn Đã giao không có nút Hủy đơn | chromium | ✅ Đạt |  |
| ACC-ORD-B06 | Có đơn hàng › Nút Hủy đơn theo trạng thái (data-driven) › Đơn Đã hủy không có nút Hủy đơn | chromium | ✅ Đạt |  |
| ACC-ORD-B07 | Có đơn hàng › Nút Hủy đơn theo trạng thái (data-driven) › Đơn Trả hàng không có nút Hủy đơn | chromium | ✅ Đạt |  |
| ACC-PRF-R01 | Dữ liệu thật: hồ sơ hiển thị email tài khoản test | chromium | ✅ Đạt |  |
| ACC-PRF-D01 | Hiển thị thông tin tài khoản (data-driven) › Hồ sơ đầy đủ: hạng Vàng, giới tính Nữ, điểm tích lũy @smoke | chromium | ✅ Đạt |  |
| ACC-PRF-D02 | Hiển thị thông tin tài khoản (data-driven) › Tài khoản mới: trường trống hiện Chưa cập nhật, hạng Đồng | chromium | ✅ Đạt |  |
| ACC-PRF-D03 | Hiển thị thông tin tài khoản (data-driven) › Hạng Bạch kim, giới tính Nam, điểm hàng chục nghìn | chromium | ✅ Đạt |  |
| ACC-PRF-E01 | Chỉnh sửa hồ sơ › Cập nhật họ tên, SĐT, ngày sinh, giới tính @smoke | chromium | ✅ Đạt |  |
| ACC-PRF-E02 | Chỉnh sửa hồ sơ › Xóa số điện thoại, đổi giới tính - các trường khác giữ nguyên | chromium | ✅ Đạt |  |
| ACC-PRF-E03 | Chỉnh sửa hồ sơ › Lỗi server khi lưu hồ sơ hiển thị thông báo lỗi | chromium | 🐞 Bug đã biết | BUG: ProfilePage.jsx:252-253 - catch nuốt lỗi PUT /profile, chỉ reset form, không hiển thị thông báo nào |
| ACC-PRF-E04 | Chỉnh sửa hồ sơ › Form sửa điền sẵn dữ liệu hiện tại, ô Email bị khóa | chromium | ✅ Đạt |  |
| ACC-PRF-E05 | Chỉnh sửa hồ sơ › Hủy sửa: không gửi request, giữ nguyên thông tin, mở lại form thấy giá trị cũ | chromium | ✅ Đạt |  |
| ACC-PWD-01 | Đổi mật khẩu › Đổi mật khẩu thành công: gửi đúng payload và đóng modal @smoke | chromium | ✅ Đạt |  |
| ACC-PWD-02 | Đổi mật khẩu › Nút Đóng và nút Hủy đều đóng modal, không gửi request | chromium | ✅ Đạt |  |
| ACC-PWD-03 | Đổi mật khẩu › Mở lại modal sau khi Hủy thì form trống, không còn lỗi cũ | chromium | 🐞 Bug đã biết | BUG: ProfilePage.jsx:33-37 - PasswordModal luôn được mount, state form/error giữ nguyên khi đóng (chỉ reset sau khi đổi thành công) -> mở lại vẫn thấy mật khẩu cũ và lỗi cũ |
| ACC-PWD-V01 | Đổi mật khẩu › Validate phía client (data-driven) › Mật khẩu mới dưới 6 ký tự | chromium | ✅ Đạt |  |
| ACC-PWD-V02 | Đổi mật khẩu › Validate phía client (data-driven) › Xác nhận mật khẩu không khớp | chromium | ✅ Đạt |  |
| ACC-PWD-V03 | Đổi mật khẩu › Validate phía client (data-driven) › Bỏ trống mật khẩu mới | chromium | ✅ Đạt |  |
| ACC-PWD-V04 | Đổi mật khẩu › Validate phía client (data-driven) › Vừa ngắn vừa không khớp -> báo lỗi độ dài trước | chromium | ✅ Đạt |  |
| ACC-PWD-S01 | Đổi mật khẩu › Lỗi từ server (mock, data-driven) › Sai mật khẩu hiện tại (400) | chromium | ✅ Đạt |  |
| ACC-PWD-S02 | Đổi mật khẩu › Lỗi từ server (mock, data-driven) › Bỏ trống mật khẩu hiện tại (400) | chromium | ✅ Đạt |  |
| ACC-PWD-S03 | Đổi mật khẩu › Lỗi từ server (mock, data-driven) › Lỗi server (500) | chromium | ✅ Đạt |  |
| ACC-PRF-S01 | Tổng quan tài khoản › Thống kê, đơn gần đây, yêu thích gần đây, địa chỉ mặc định @smoke | chromium | ✅ Đạt |  |
| ACC-PRF-S02 | Tổng quan tài khoản › Tài khoản chưa có dữ liệu: thống kê 0 và các thông báo trống | chromium | ✅ Đạt |  |
| ACC-PRF-S03 | Tổng quan tài khoản › Tổng đơn hàng đếm đủ mọi đơn (tài khoản có 12 đơn) | chromium | 🐞 Bug đã biết | BUG: ProfilePage.jsx:185 chỉ lấy 10 đơn (limit 10) và ProfileSummary.jsx:22 đếm orders.length thay vì pagination.total -> "Tổng đơn hàng" tối đa là 10 |
| ACC-PRF-S04 | Tổng quan tài khoản › Nút Cập nhật địa chỉ dẫn tới sổ địa chỉ | chromium | ✅ Đạt |  |
| ACC-RD-06 | Bấm Đăng nhập ở trang thanh toán, đăng nhập xong quay lại /checkout | chromium | 🐞 Bug đã biết | BUG: LoginPage.jsx:94 (và :25) luôn navigate('/profile'), bỏ qua location.state.from = '/checkout' mà CheckoutPage.jsx:330 truyền sang |
| ACC-RD-01 | Trang cần đăng nhập (data-driven) › Chưa đăng nhập mở /profile -> chuyển về /login | chromium | 🐞 Bug đã biết | BUG: ProfilePage.jsx:165 useState(profileToForm(user)) với user = null ở lần render đầu (default param của profileToForm dòng 139 không áp dụng cho null) -> crash 'Cannot read properties of null', ErrorBoundary hiện 'Đã xảy ra lỗi' nên useEffect chuyển /login (dòng 170) không bao giờ chạy |
| ACC-RD-02 | Trang cần đăng nhập (data-driven) › Chưa đăng nhập mở /orders -> chuyển về /login @smoke | chromium | ✅ Đạt |  |
| ACC-RD-03 | Trang cần đăng nhập (data-driven) › Chưa đăng nhập mở /favorites -> chuyển về /login | chromium | ✅ Đạt |  |
| ACC-RD-04 | Trang cần đăng nhập (data-driven) › Chưa đăng nhập mở /addresses -> chuyển về /login | chromium | ✅ Đạt |  |
| ACC-RD-05 | Trang cần đăng nhập (data-driven) › Chưa đăng nhập mở chi tiết đơn /orders/1 -> chuyển về /login | chromium | ✅ Đạt |  |
| ACC-WL-E01 | Chưa có sản phẩm yêu thích: thông báo trống, 0 sản phẩm | chromium | ✅ Đạt |  |
| ACC-WL-H01 | Bấm trái tim trên trang danh mục lưu sản phẩm vào yêu thích | chromium | 🐞 Bug đã biết | BUG: MenPage.jsx:391 (và KidsPage.jsx:347) - nút trái tim không có onClick, nằm trong <Link>; không nơi nào gọi POST /api/wishlist nên khách không thể thêm yêu thích |
| ACC-WL-01 | Có sản phẩm yêu thích › Hiển thị số lượng và danh sách (mới lưu trước) @smoke | chromium | ✅ Đạt |  |
| ACC-WL-R01 | Có sản phẩm yêu thích › Bỏ yêu thích: gửi DELETE đúng sản phẩm, cập nhật danh sách và số lượng | chromium | ✅ Đạt |  |
| ACC-WL-R02 | Có sản phẩm yêu thích › Bỏ yêu thích thất bại: sản phẩm được khôi phục | chromium | ✅ Đạt |  |
| ACC-WL-C01 | Có sản phẩm yêu thích › Thêm vào giỏ sản phẩm không có biến thể: toast + giỏ có 1 sản phẩm | chromium | ✅ Đạt |  |
| ACC-WL-C02 | Có sản phẩm yêu thích › Thêm vào giỏ sản phẩm có biến thể: chuyển sang trang sản phẩm để chọn size | chromium | ✅ Đạt |  |
| ACC-WL-O01 | Có sản phẩm yêu thích › Sắp xếp (data-driven) › Mặc định: mới lưu gần đây trước | chromium | ✅ Đạt |  |
| ACC-WL-O02 | Có sản phẩm yêu thích › Sắp xếp (data-driven) › Giá thấp đến cao | chromium | ✅ Đạt |  |
| ACC-WL-O03 | Có sản phẩm yêu thích › Sắp xếp (data-driven) › Giá cao đến thấp | chromium | ✅ Đạt |  |
| ACC-WL-S01 | Có sản phẩm yêu thích › Tìm kiếm (data-driven) › Tìm theo tên (không phân biệt hoa thường) | chromium | ✅ Đạt |  |
| ACC-WL-S02 | Có sản phẩm yêu thích › Tìm kiếm (data-driven) › Tìm theo danh mục | chromium | ✅ Đạt |  |
| ACC-WL-S03 | Có sản phẩm yêu thích › Tìm kiếm (data-driven) › Không có sản phẩm phù hợp | chromium | ✅ Đạt |  |
| ACC-WL-A01 | Có sản phẩm yêu thích › Tình trạng hàng + thông tin thẻ (data-driven) › Còn hàng, có giảm giá -> nút thêm giỏ bật, hiện % giảm | chromium | ✅ Đạt |  |
| ACC-WL-A02 | Có sản phẩm yêu thích › Tình trạng hàng + thông tin thẻ (data-driven) › Hết hàng (stock = 0) -> nút thêm giỏ tắt | chromium | ✅ Đạt |  |
| ACC-WL-A03 | Có sản phẩm yêu thích › Tình trạng hàng + thông tin thẻ (data-driven) › Sản phẩm ngừng bán (is_active = false) -> coi như hết hàng | chromium | ✅ Đạt |  |

## UI - Quản trị

| ID | Test case | Project | Kết quả | Ghi chú |
|---|---|---|---|---|
| UI-QT-01 | Chưa đăng nhập vào /admin bị chuyển về /admin/login @smoke | chromium | ✅ Đạt |  |
| UI-QT-02 | Sai mật khẩu hiển thị lỗi | chromium | 🐞 Bug đã biết | BUG: interceptor 401 trong services/api.js reload sang /admin/login nên thông báo lỗi bị mất |
| UI-QT-03 | Link "Quay về cửa hàng" về trang chủ | chromium | ✅ Đạt |  |
| UI-QT-04 | Đăng nhập thành công vào Dashboard | chromium | ✅ Đạt |  |
| UI-QT-05 | Menu "Tổng quan" mở /admin | chromium | ✅ Đạt |  |
| UI-QT-06 | Menu "Sản phẩm" mở /admin/products | chromium | ✅ Đạt |  |
| UI-QT-07 | Menu "Danh mục" mở /admin/categories | chromium | ✅ Đạt |  |
| UI-QT-08 | Menu "Thương hiệu" mở /admin/brands | chromium | ✅ Đạt |  |
| UI-QT-09 | Menu "Đơn hàng" mở /admin/orders | chromium | ✅ Đạt |  |
| UI-QT-10 | Menu "Khách hàng" mở /admin/customers | chromium | ✅ Đạt |  |
| UI-QT-11 | Menu "Nhân viên" mở /admin/employees | chromium | ✅ Đạt |  |
| UI-QT-12 | Menu "Khuyến mãi" mở /admin/promotions | chromium | ✅ Đạt |  |
| UI-QT-13 | Menu "Mã giảm giá" mở /admin/coupons | chromium | ✅ Đạt |  |
| UI-QT-14 | Menu "Kho hàng" mở /admin/warehouse | chromium | ✅ Đạt |  |
| UI-QT-15 | Menu "Nhập hàng" mở /admin/import | chromium | ✅ Đạt |  |
| UI-QT-16 | Menu "Đánh giá" mở /admin/reviews | chromium | ✅ Đạt |  |
| UI-QT-17 | Menu "Bài viết" mở /admin/blog | chromium | ✅ Đạt |  |
| UI-QT-18 | Menu "Báo cáo" mở /admin/reports | chromium | ✅ Đạt |  |
| UI-QT-19 | Menu "Liên hệ" mở /admin/contacts | chromium | ✅ Đạt |  |
| UI-QT-20 | Menu "Cài đặt" mở /admin/settings | chromium | ✅ Đạt |  |

## UI - Admin: Sản phẩm, Danh mục, Thương hiệu

| ID | Test case | Project | Kết quả | Ghi chú |
|---|---|---|---|---|
| ADC-PF-01 | Tạo sản phẩm › Tạo sản phẩm đầy đủ thông tin (mock POST) -> payload đúng, toast, về danh sách @smoke | chromium | ✅ Đạt |  |
| ADC-PF-02 | Tạo sản phẩm › Server báo lỗi -> hiện lỗi trên form + toast, ở lại trang | chromium | ✅ Đạt |  |
| ADC-PF-03 | Tạo sản phẩm › Tạo biến thể: chọn size x màu sinh lưới SKU, xóa 1 dòng, gửi kèm payload | chromium | ✅ Đạt |  |
| ADC-PF-04 | Tạo sản phẩm › Ảnh từ URL: thêm, bỏ trùng, ảnh đầu là "Ảnh chính", xóa ảnh | chromium | ✅ Đạt |  |
| ADC-PF-05 | Tạo sản phẩm › Tải ảnh lên gửi kèm token admin | chromium | 🐞 Bug đã biết | BUG: AdminProductForm.jsx:187 - upload gửi Authorization từ localStorage 'token' (không tồn tại ở phiên admin) thay vì 'admin_token' -> header 'Bearer null' |
| ADC-PF-06 | Tạo sản phẩm › "Quay lại" về danh sách sản phẩm, không gửi request | chromium | ✅ Đạt |  |
| ADC-PF-V01 | Tạo sản phẩm › Validate (data-driven) › Bỏ trống tên và giá @smoke | chromium | ✅ Đạt |  |
| ADC-PF-V02 | Tạo sản phẩm › Validate (data-driven) › Chỉ nhập tên, thiếu giá | chromium | ✅ Đạt |  |
| ADC-PF-V03 | Tạo sản phẩm › Validate (data-driven) › Chỉ nhập giá, thiếu tên | chromium | ✅ Đạt |  |
| ADC-PF-S01 | Tạo sản phẩm › Slug tự sinh từ tên (data-driven) › Tên có dấu thông thường | chromium | ✅ Đạt |  |
| ADC-PF-S02 | Tạo sản phẩm › Slug tự sinh từ tên (data-driven) › Ký tự đặc biệt và khoảng trắng kép | chromium | ✅ Đạt |  |
| ADC-PF-S03 | Tạo sản phẩm › Slug tự sinh từ tên (data-driven) › Tên có chữ 'đ' giữa từ | chromium | 🐞 Bug đã biết | BUG: AdminProductForm.jsx:154-158 - NFD không tách 'đ' nên bị thay bằng '-' -> slug 'ao-khoac-en' |
| ADC-PF-S04 | Tạo sản phẩm › Slug tự sinh từ tên (data-driven) › Tên bắt đầu bằng chữ 'Đ' | chromium | 🐞 Bug đã biết | BUG: AdminProductForm.jsx:154-158 - 'Đ' đầu tên bị bỏ -> slug 'am-du-tiec' |
| ADC-PF-07 | Sửa sản phẩm › Mở trực tiếp URL sửa: tải chi tiết, điền sẵn; lưu gửi PUT giữ nguyên mô tả/chất liệu (mock) | chromium | ✅ Đạt |  |
| ADC-PF-08 | Sửa sản phẩm › Bấm "Sửa" từ danh sách: danh mục được chọn sẵn | chromium | 🐞 Bug đã biết | BUG: AdminProductForm.jsx:57-89 - khi bấm Sửa từ danh sách, form lấy dữ liệu dòng trong sessionStorage (thiếu description/material/gender/variants) và return trước khi tải danh mục/thương hiệu -> ô Danh mục trống và lưu sẽ ghi đè mô tả/chất liệu/giới tính |
| ADC-PF-09 | Sửa sản phẩm › Bấm "Sửa" từ danh sách rồi lưu không làm mất mô tả/chất liệu/giới tính | chromium | 🐞 Bug đã biết | BUG: AdminProductForm.jsx:57-89 - khi bấm Sửa từ danh sách, form lấy dữ liệu dòng trong sessionStorage (thiếu description/material/gender/variants) và return trước khi tải danh mục/thương hiệu -> ô Danh mục trống và lưu sẽ ghi đè mô tả/chất liệu/giới tính |
| ADC-PRD-01 | Dữ liệu thật: có sản phẩm, đủ cột, phân trang 10/trang @smoke | chromium | ✅ Đạt |  |
| ADC-PRD-02 | "Thêm sản phẩm" mở form tạo mới | chromium | ✅ Đạt |  |
| ADC-PRD-09 | Phân trang: sang trang 2 gọi API page=2 | chromium | ✅ Đạt |  |
| ADC-PRD-03 | Dữ liệu mock › Mỗi dòng hiển thị đúng thương hiệu, SKU, danh mục, giá, tồn kho, đã bán, nổi bật, trạng thái | chromium | ✅ Đạt |  |
| ADC-PRD-04 | Dữ liệu mock › Link "Xem" trỏ tới trang sản phẩm ngoài cửa hàng | chromium | ✅ Đạt |  |
| ADC-PRD-05 | Dữ liệu mock › "Sửa" mở form chỉnh sửa của đúng sản phẩm | chromium | ✅ Đạt |  |
| ADC-PRD-F01 | Dữ liệu mock › Tìm kiếm & lọc (data-driven) › Tìm theo SKU | chromium | ✅ Đạt |  |
| ADC-PRD-F02 | Dữ liệu mock › Tìm kiếm & lọc (data-driven) › Tìm theo tên (không phân biệt hoa thường) | chromium | ✅ Đạt |  |
| ADC-PRD-F03 | Dữ liệu mock › Tìm kiếm & lọc (data-driven) › Lọc theo danh mục | chromium | ✅ Đạt |  |
| ADC-PRD-F04 | Dữ liệu mock › Tìm kiếm & lọc (data-driven) › Lọc theo thương hiệu | chromium | ✅ Đạt |  |
| ADC-PRD-FT01 | Dữ liệu mock › Nổi bật (mock PUT /toggle-featured, data-driven) › Đánh dấu nổi bật @smoke | chromium | ✅ Đạt |  |
| ADC-PRD-FT02 | Dữ liệu mock › Nổi bật (mock PUT /toggle-featured, data-driven) › Bỏ nổi bật | chromium | ✅ Đạt |  |
| ADC-PRD-FT03 | Dữ liệu mock › Nổi bật (mock PUT /toggle-featured, data-driven) › API lỗi -> báo lỗi và giữ nguyên trạng thái nổi bật | chromium | 🐞 Bug đã biết | BUG: AdminProducts.jsx:90-91 - nhánh catch vẫn đảo is_featured nên UI hiển thị sai sau khi API lỗi |
| ADC-PRD-S01 | Dữ liệu mock › Trạng thái bán (mock PUT /toggle, data-driven) › Tắt bán sản phẩm đang bán | chromium | ✅ Đạt |  |
| ADC-PRD-S02 | Dữ liệu mock › Trạng thái bán (mock PUT /toggle, data-driven) › Bật bán sản phẩm đang ngừng | chromium | ✅ Đạt |  |
| ADC-PRD-S03 | Dữ liệu mock › Trạng thái bán (mock PUT /toggle, data-driven) › API lỗi -> báo lỗi và giữ nguyên trạng thái bán | chromium | 🐞 Bug đã biết | BUG: AdminProducts.jsx:79-80 - nhánh catch vẫn đảo is_active nên nút gạt đổi trạng thái dù API lỗi |
| ADC-PRD-06 | Dữ liệu mock › Xóa sản phẩm (mock DELETE) › Modal "Xóa sản phẩm?" + "Hủy" không gửi request | chromium | ✅ Đạt |  |
| ADC-PRD-D01 | Dữ liệu mock › Xóa sản phẩm (mock DELETE) › Xóa sản phẩm thành công | chromium | ✅ Đạt |  |
| ADC-PRD-D02 | Dữ liệu mock › Xóa sản phẩm (mock DELETE) › Xóa lỗi -> báo lỗi và giữ dòng | chromium | ✅ Đạt |  |
| ADC-PRD-07 | Dữ liệu mock › Chọn nhiều › Chọn từng dòng / chọn tất cả hiển thị số sản phẩm được chọn | chromium | ✅ Đạt |  |
| ADC-PRD-08 | Dữ liệu mock › Chọn nhiều › "Xóa đã chọn" xóa các sản phẩm đã chọn | chromium | 🐞 Bug đã biết | BUG: AdminProducts.jsx:170 nút "Xóa đã chọn" không có onClick -> bấm không làm gì |
| ADC-CAT-01 | Dữ liệu thật: trang Danh mục có thẻ, ô tìm kiếm, nút thêm @smoke | chromium | ✅ Đạt |  |
| ADC-CAT-02 | Dữ liệu mock › Thẻ hiển thị tên, slug, mô tả và nút gạt theo dữ liệu | chromium | ✅ Đạt |  |
| ADC-CAT-03 | Dữ liệu mock › Thêm danh mục (mock POST) -> payload đúng, toast, thẻ mới | chromium | ✅ Đạt |  |
| ADC-CAT-04 | Dữ liệu mock › Bỏ trống tên -> trình duyệt chặn, không gửi request | chromium | ✅ Đạt |  |
| ADC-CAT-05 | Dữ liệu mock › "Hủy" đóng modal thêm, không gửi request | chromium | ✅ Đạt |  |
| ADC-CAT-06 | Dữ liệu mock › Lưu lỗi -> toast lỗi, modal vẫn mở giữ dữ liệu đã nhập | chromium | 🐞 Bug đã biết | BUG: AdminCategories.jsx:57-59 - catch gọi setShowForm(false) nên modal đóng, mất dữ liệu vừa nhập |
| ADC-CAT-07 | Dữ liệu mock › Sửa: modal điền sẵn dữ liệu, lưu gửi PUT (mock) và cập nhật thẻ | chromium | ✅ Đạt |  |
| ADC-CAT-08 | Dữ liệu mock › Xóa: modal xác nhận đúng tên; "Hủy" không gửi request | chromium | ✅ Đạt |  |
| ADC-CAT-09 | Dữ liệu mock › Xóa thành công (mock DELETE) -> toast, thẻ biến mất | chromium | ✅ Đạt |  |
| ADC-CAT-10 | Dữ liệu mock › Xóa bị server từ chối -> toast thông điệp server, thẻ còn nguyên | chromium | ✅ Đạt |  |
| ADC-CAT-11 | Dữ liệu mock › Gạt tắt Hoạt động (mock PUT) -> gửi is_active=false, toast | chromium | ✅ Đạt |  |
| ADC-CAT-12 | Dữ liệu mock › Gạt Hoạt động lỗi -> toast lỗi, giữ nguyên trạng thái | chromium | 🐞 Bug đã biết | BUG: AdminCategories.jsx:36-38 - nhánh catch vẫn đảo trạng thái nên nút gạt đổi dù API lỗi |
| ADC-CAT-13 | Dữ liệu mock › Danh mục nổi bật hiển thị nhãn "Nổi bật" | chromium | 🐞 Bug đã biết | BUG: AdminCategories.jsx:115 - badge 'Nổi bật' so sánh is_featured === 1 nhưng API (Postgres) trả boolean true -> không bao giờ hiện |
| ADC-CAT-SR01 | Dữ liệu mock › Tìm kiếm (data-driven) › Tìm danh mục theo tên | chromium | ✅ Đạt |  |
| ADC-CAT-SR02 | Dữ liệu mock › Tìm kiếm (data-driven) › Tìm danh mục theo slug | chromium | ✅ Đạt |  |
| ADC-CAT-SR03 | Dữ liệu mock › Tìm kiếm (data-driven) › Không có danh mục khớp | chromium | ✅ Đạt |  |
| ADC-BRD-01 | Dữ liệu thật: trang Thương hiệu có thẻ, ô tìm kiếm, nút thêm @smoke | chromium | ✅ Đạt |  |
| ADC-BRD-02 | Dữ liệu mock › Thẻ hiển thị tên, slug, mô tả và nút gạt theo dữ liệu | chromium | ✅ Đạt |  |
| ADC-BRD-03 | Dữ liệu mock › Thêm thương hiệu (mock POST) -> payload đúng, toast, thẻ mới | chromium | ✅ Đạt |  |
| ADC-BRD-04 | Dữ liệu mock › Bỏ trống tên -> trình duyệt chặn, không gửi request | chromium | ✅ Đạt |  |
| ADC-BRD-05 | Dữ liệu mock › "Hủy" đóng modal thêm, không gửi request | chromium | ✅ Đạt |  |
| ADC-BRD-06 | Dữ liệu mock › Lưu lỗi -> toast lỗi, modal vẫn mở giữ dữ liệu đã nhập | chromium | 🐞 Bug đã biết | BUG: AdminBrands.jsx:57-59 - catch gọi setShowForm(false) nên modal đóng, mất dữ liệu vừa nhập |
| ADC-BRD-07 | Dữ liệu mock › Sửa: modal điền sẵn dữ liệu, lưu gửi PUT (mock) và cập nhật thẻ | chromium | ✅ Đạt |  |
| ADC-BRD-08 | Dữ liệu mock › Xóa: modal xác nhận đúng tên; "Hủy" không gửi request | chromium | ✅ Đạt |  |
| ADC-BRD-09 | Dữ liệu mock › Xóa thành công (mock DELETE) -> toast, thẻ biến mất | chromium | ✅ Đạt |  |
| ADC-BRD-10 | Dữ liệu mock › Xóa bị server từ chối -> toast thông điệp server, thẻ còn nguyên | chromium | ✅ Đạt |  |
| ADC-BRD-11 | Dữ liệu mock › Gạt tắt Hoạt động (mock PUT) -> gửi is_active=false, toast | chromium | ✅ Đạt |  |
| ADC-BRD-12 | Dữ liệu mock › Gạt Hoạt động lỗi -> toast lỗi, giữ nguyên trạng thái | chromium | 🐞 Bug đã biết | BUG: AdminBrands.jsx:36-38 - nhánh catch vẫn đảo trạng thái nên nút gạt đổi dù API lỗi |
| ADC-BRD-13 | Dữ liệu mock › Thương hiệu nổi bật hiển thị nhãn "Nổi bật" | chromium | 🐞 Bug đã biết | BUG: AdminBrands.jsx:111 - badge 'Nổi bật' so sánh is_featured === 1 nhưng API (Postgres) trả boolean true -> không bao giờ hiện |
| ADC-BRD-SR01 | Dữ liệu mock › Tìm kiếm (data-driven) › Tìm thương hiệu theo tên | chromium | ✅ Đạt |  |
| ADC-BRD-SR02 | Dữ liệu mock › Tìm kiếm (data-driven) › Tìm thương hiệu theo slug | chromium | ✅ Đạt |  |
| ADC-BRD-SR03 | Dữ liệu mock › Tìm kiếm (data-driven) › Không có thương hiệu khớp | chromium | ✅ Đạt |  |
| ADC-BRD-SL01 | Dữ liệu mock › Slug tự sinh khi gõ tên (data-driven) › Slug tự sinh từ tên không dấu | chromium | ✅ Đạt |  |
| ADC-BRD-SL02 | Dữ liệu mock › Slug tự sinh khi gõ tên (data-driven) › Slug tự sinh từ tên tiếng Việt có dấu | chromium | 🐞 Bug đã biết | BUG: AdminBrands.jsx:138 - slug chỉ giữ [a-z0-9], không bỏ dấu tiếng Việt -> 'th-ng-hi-u-test' |

## UI - Admin: Khuyến mãi, Mã giảm giá, Đánh giá, Bài viết, Liên hệ

| ID | Test case | Project | Kết quả | Ghi chú |
|---|---|---|---|---|
| ADM-BLG-01 | Dữ liệu thật: đủ cột và có ít nhất 1 bài viết @smoke | chromium | ✅ Đạt |  |
| ADM-BLG-02 | Chưa có bài viết -> trạng thái rỗng | chromium | ✅ Đạt |  |
| ADM-BLG-03 | Thêm bài viết thành công gửi đúng dữ liệu, bài mới lên đầu (mock POST) @smoke | chromium | ✅ Đạt |  |
| ADM-BLG-04 | Sửa: form điền sẵn, giữ slug cũ khi đổi tiêu đề, gửi PUT đúng (mock) | chromium | ✅ Đạt |  |
| ADM-BLG-05 | Xem chi tiết bài viết | chromium | ✅ Đạt |  |
| ADM-BLG-06 | Xóa: bấm "Hủy" không gửi DELETE | chromium | ✅ Đạt |  |
| ADM-BLG-07 | Xóa: xác nhận gửi DELETE và bỏ dòng (mock) | chromium | ✅ Đạt |  |
| ADM-BLG-08 | Ảnh: URL hợp lệ hiện ảnh xem trước, URL hỏng hiện lỗi | chromium | ✅ Đạt |  |
| ADM-BLG-09 | Hủy form sửa rồi bấm "Thêm bài viết" -> form trống | chromium | ✅ Đạt |  |
| ADM-BLG-R01 | Hiển thị dòng (data-driven) › Bài hiển thị: mô tả, slug, ngày tạo, ảnh mặc định @smoke | chromium | ✅ Đạt |  |
| ADM-BLG-R02 | Hiển thị dòng (data-driven) › Bài nổi bật có nhãn "Nổi bật" | chromium | ✅ Đạt |  |
| ADM-BLG-R03 | Hiển thị dòng (data-driven) › Bài ẩn: trạng thái "Ẩn", nút "Hiển thị bài viết", mô tả mặc định | chromium | ✅ Đạt |  |
| ADM-BLG-Q01 | Tìm kiếm (data-driven) › Tìm theo tiêu đề | chromium | ✅ Đạt |  |
| ADM-BLG-Q02 | Tìm kiếm (data-driven) › Tìm theo slug | chromium | ✅ Đạt |  |
| ADM-BLG-Q03 | Tìm kiếm (data-driven) › Tìm theo mô tả ngắn | chromium | ✅ Đạt |  |
| ADM-BLG-Q04 | Tìm kiếm (data-driven) › Tìm không phân biệt hoa thường | chromium | ✅ Đạt |  |
| ADM-BLG-Q05 | Tìm kiếm (data-driven) › Không có kết quả -> thông báo không tìm thấy | chromium | ✅ Đạt |  |
| ADM-BLG-V01 | Form thêm - kiểm tra dữ liệu (data-driven) › Bỏ trống tiêu đề @smoke | chromium | ✅ Đạt |  |
| ADM-BLG-V02 | Form thêm - kiểm tra dữ liệu (data-driven) › Tiêu đề chỉ có khoảng trắng | chromium | ✅ Đạt |  |
| ADM-BLG-G01 | Slug (data-driven) › Slug tự sinh từ tiêu đề | chromium | ✅ Đạt |  |
| ADM-BLG-G02 | Slug (data-driven) › Slug nhập tay được chuẩn hóa | chromium | ✅ Đạt |  |
| ADM-BLG-G03 | Slug (data-driven) › Thêm mới: slug nhập tay được giữ khi sửa tiêu đề | chromium | 🐞 Bug đã biết | BUG: AdminBlog.jsx:151 khi tạo mới luôn slugify lại tiêu đề -> ghi đè slug người dùng đã nhập |
| ADM-BLG-T01 | Ẩn/Hiển thị, nổi bật trên dòng (data-driven) › Ẩn bài đang hiển thị (mock PUT) | chromium | ✅ Đạt |  |
| ADM-BLG-T02 | Ẩn/Hiển thị, nổi bật trên dòng (data-driven) › Hiển thị bài đang ẩn (mock PUT) | chromium | ✅ Đạt |  |
| ADM-BLG-T03 | Ẩn/Hiển thị, nổi bật trên dòng (data-driven) › Bật nổi bật (mock PUT) | chromium | ✅ Đạt |  |
| ADM-BLG-T04 | Ẩn/Hiển thị, nổi bật trên dòng (data-driven) › Tắt nổi bật (mock PUT) | chromium | ✅ Đạt |  |
| ADM-CTC-01 | Dữ liệu thật: trang tải được, đủ cột @smoke | chromium | ✅ Đạt |  |
| ADM-CTC-02 | Chưa có liên hệ -> trạng thái rỗng | chromium | ✅ Đạt |  |
| ADM-CTC-03 | API lỗi -> toast "Không thể tải danh sách liên hệ." | chromium | ✅ Đạt |  |
| ADM-CTC-04 | Xem chi tiết và đánh dấu đã xử lý trong modal (mock PUT) | chromium | ✅ Đạt |  |
| ADM-CTC-05 | Xóa: bấm "Hủy" không gửi DELETE | chromium | ✅ Đạt |  |
| ADM-CTC-06 | Xóa: xác nhận gửi DELETE và bỏ dòng (mock) | chromium | ✅ Đạt |  |
| ADM-CTC-R01 | Hiển thị dòng + nút theo trạng thái (data-driven) › Liên hệ chưa xử lý: đủ thông tin + nút đánh dấu đã xử lý @smoke | chromium | ✅ Đạt |  |
| ADM-CTC-R02 | Hiển thị dòng + nút theo trạng thái (data-driven) › Liên hệ đã xử lý: nút đánh dấu chưa xử lý | chromium | ✅ Đạt |  |
| ADM-CTC-R03 | Hiển thị dòng + nút theo trạng thái (data-driven) › Thiếu SĐT/chủ đề hiển thị giá trị mặc định | chromium | ✅ Đạt |  |
| ADM-CTC-Q01 | Tìm kiếm (data-driven) › Tìm theo họ tên | chromium | ✅ Đạt |  |
| ADM-CTC-Q02 | Tìm kiếm (data-driven) › Tìm theo email | chromium | ✅ Đạt |  |
| ADM-CTC-Q03 | Tìm kiếm (data-driven) › Tìm theo số điện thoại | chromium | ✅ Đạt |  |
| ADM-CTC-Q04 | Tìm kiếm (data-driven) › Tìm theo chủ đề | chromium | ✅ Đạt |  |
| ADM-CTC-Q05 | Tìm kiếm (data-driven) › Tìm theo nội dung, không phân biệt hoa thường | chromium | ✅ Đạt |  |
| ADM-CTC-Q06 | Tìm kiếm (data-driven) › Không có kết quả -> thông báo không tìm thấy | chromium | ✅ Đạt |  |
| ADM-CTC-F01 | Lọc trạng thái (data-driven) › Lọc "Chưa xử lý" gửi status=pending | chromium | ✅ Đạt |  |
| ADM-CTC-F02 | Lọc trạng thái (data-driven) › Lọc "Đã xử lý" gửi status=processed | chromium | ✅ Đạt |  |
| ADM-CTC-F03 | Lọc trạng thái (data-driven) › Bộ lọc không có kết quả -> báo "Không tìm thấy liên hệ phù hợp." | chromium | 🐞 Bug đã biết | BUG: AdminContacts.jsx:179 chỉ xét ô tìm kiếm -> lọc rỗng vẫn hiện 'Chưa có liên hệ nào' |
| ADM-CTC-A01 | Đổi trạng thái xử lý trên dòng (data-driven) › Đánh dấu đã xử lý (mock PUT) @smoke | chromium | ✅ Đạt |  |
| ADM-CTC-A02 | Đổi trạng thái xử lý trên dòng (data-driven) › Đánh dấu chưa xử lý (mock PUT) | chromium | ✅ Đạt |  |
| ADM-CPN-01 | Dữ liệu thật: đủ cột và có ít nhất 1 mã @smoke | chromium | ✅ Đạt |  |
| ADM-CPN-02 | Danh sách rỗng hiển thị "Chưa có mã giảm giá nào" | chromium | ✅ Đạt |  |
| ADM-CPN-03 | Mã tự viết hoa khi nhập | chromium | ✅ Đạt |  |
| ADM-CPN-04 | Thêm mã thành công gửi đúng dữ liệu và thêm dòng mới (mock POST) @smoke | chromium | ✅ Đạt |  |
| ADM-CPN-E01 | Server báo lỗi khi lưu -> hiện đúng thông báo của server | chromium | 🐞 Bug đã biết | BUG: AdminCoupons.jsx:51 đọc err.response.data.error trong khi backend trả 'message' -> luôn hiện 'Lưu mã giảm giá thất bại' |
| ADM-CPN-05 | Sửa: form điền sẵn, gửi PUT đúng và cập nhật dòng (mock) | chromium | ✅ Đạt |  |
| ADM-CPN-B03 | Sửa: ô "Từ ngày"/"Đến ngày" điền sẵn ngày hiệu lực | chromium | 🐞 Bug đã biết | BUG: AdminCoupons.jsx:55 đưa chuỗi ISO có giờ vào input type=date -> 2 ô ngày bị trống khi sửa |
| ADM-CPN-B04 | Nhãn loại first_order trong form khớp nhãn trong bảng ("Khách mới") | chromium | 🐞 Bug đã biết | BUG: AdminCoupons.jsx:180 option ghi 'Khách hàng mới' nhưng bảng (dòng 80) ghi 'Khách mới' |
| ADM-CPN-06 | Xóa: bấm "Hủy" không gửi DELETE | chromium | ✅ Đạt |  |
| ADM-CPN-07 | Xóa: xác nhận gửi DELETE đúng id và bỏ dòng (mock) | chromium | ✅ Đạt |  |
| ADM-CPN-B01 | Dữ liệu thật - định dạng cột › Dữ liệu thật: cột "Loại" hiển thị loại mã | chromium | 🐞 Bug đã biết | BUG: adminController.js:1565-1592 getCoupons/createCoupon không đọc/lưu coupon_type -> cột "Loại" (AdminCoupons.jsx:128) luôn trống |
| ADM-CPN-B02 | Dữ liệu thật - định dạng cột › Dữ liệu thật: cột "Hiệu lực" hiển thị ngày dd/mm/yyyy | chromium | 🐞 Bug đã biết | BUG: AdminCoupons.jsx:133 in thẳng chuỗi ISO (vd: 2026-09-11T14:23:39.773Z) thay vì định dạng ngày |
| ADM-CPN-D01 | Hiển thị dòng (data-driven) › Mã giảm %: hiển thị mã, tên, % và lượt dùng @smoke | chromium | ✅ Đạt |  |
| ADM-CPN-D02 | Hiển thị dòng (data-driven) › Mã giảm tiền, không giới hạn lượt: "30.000đ" và "5 / ∞" | chromium | ✅ Đạt |  |
| ADM-CPN-D03 | Hiển thị dòng (data-driven) › Loại first_order hiển thị "Khách mới" | chromium | ✅ Đạt |  |
| ADM-CPN-V01 | Trường bắt buộc (data-driven) › Bỏ trống Mã và Giá trị -> trình duyệt chặn, không gửi POST | chromium | ✅ Đạt |  |
| ADM-CPN-V02 | Trường bắt buộc (data-driven) › Có Mã nhưng bỏ trống Giá trị -> không gửi POST | chromium | ✅ Đạt |  |
| ADM-CPN-V03 | Trường bắt buộc (data-driven) › Có Giá trị nhưng bỏ trống Mã -> không gửi POST | chromium | ✅ Đạt |  |
| ADM-CPN-T01 | Bật/tắt Công khai - Trạng thái (data-driven) › Tắt "Công khai" gửi PUT is_public=false @smoke | chromium | ✅ Đạt |  |
| ADM-CPN-T02 | Bật/tắt Công khai - Trạng thái (data-driven) › Bật "Công khai" gửi PUT is_public=true | chromium | ✅ Đạt |  |
| ADM-CPN-T03 | Bật/tắt Công khai - Trạng thái (data-driven) › Bật "Trạng thái" gửi PUT is_active=true | chromium | ✅ Đạt |  |
| ADM-CPN-T04 | Bật/tắt Công khai - Trạng thái (data-driven) › Tắt "Trạng thái" gửi PUT is_active=false | chromium | ✅ Đạt |  |
| ADM-PRO-01 | Dữ liệu thật: đủ cột và có ít nhất 1 khuyến mãi @smoke | chromium | ✅ Đạt |  |
| ADM-PRO-02 | Danh sách rỗng hiển thị "Chưa có khuyến mãi nào" | chromium | ✅ Đạt |  |
| ADM-PRO-03 | API lỗi hiển thị "Không thể tải danh sách khuyến mãi." | chromium | ✅ Đạt |  |
| ADM-PRO-04 | Thêm khuyến mãi thành công gửi đúng dữ liệu (mock POST) @smoke | chromium | ✅ Đạt |  |
| ADM-PRO-E01 | Server báo lỗi khi lưu -> hiện đúng thông báo của server | chromium | 🐞 Bug đã biết | BUG: AdminPromotions.jsx:247 luôn hiện 'Không thể lưu khuyến mãi. Vui lòng kiểm tra lại thông tin.', bỏ qua message server trả về (vd: 'Slug khuyến mãi đã tồn tại.') |
| ADM-PRO-05 | Sửa: form điền sẵn dữ liệu và gửi PUT đúng (mock) | chromium | ✅ Đạt |  |
| ADM-PRO-06 | Xem chi tiết rồi bấm "Sửa" mở form sửa | chromium | ✅ Đạt |  |
| ADM-PRO-07 | Xóa: bấm "Hủy" đóng hộp xác nhận, không gửi DELETE | chromium | ✅ Đạt |  |
| ADM-PRO-08 | Xóa: xác nhận gửi DELETE đúng id và báo thành công (mock) | chromium | ✅ Đạt |  |
| ADM-PRO-09 | Đóng form bằng nút "Đóng" rồi mở lại -> form trống | chromium | ✅ Đạt |  |
| ADM-PRO-S01 | Trạng thái tính theo ngày (data-driven) › Đang trong hạn + bật -> "Đang hoạt động", giảm % @smoke | chromium | ✅ Đạt |  |
| ADM-PRO-S02 | Trạng thái tính theo ngày (data-driven) › Chưa tới ngày bắt đầu -> "Sắp diễn ra", giảm tiền | chromium | ✅ Đạt |  |
| ADM-PRO-S03 | Trạng thái tính theo ngày (data-driven) › Đã qua ngày kết thúc -> "Hết hạn" | chromium | ✅ Đạt |  |
| ADM-PRO-S04 | Trạng thái tính theo ngày (data-driven) › Đang trong hạn nhưng tắt -> "Tạm ẩn" | chromium | ✅ Đạt |  |
| ADM-PRO-S05 | Trạng thái tính theo ngày (data-driven) › Bắt đầu đúng hôm nay -> "Đang hoạt động" | chromium | ✅ Đạt |  |
| ADM-PRO-S06 | Trạng thái tính theo ngày (data-driven) › Kết thúc đúng hôm nay -> vẫn "Đang hoạt động" | chromium | ✅ Đạt |  |
| ADM-PRO-S07 | Trạng thái tính theo ngày (data-driven) › Tắt + đã hết hạn -> ưu tiên "Tạm ẩn" | chromium | ✅ Đạt |  |
| ADM-PRO-Q01 | Tìm kiếm (data-driven) › Tìm theo tên | chromium | ✅ Đạt |  |
| ADM-PRO-Q02 | Tìm kiếm (data-driven) › Tìm không dấu vẫn khớp tên có dấu | chromium | ✅ Đạt |  |
| ADM-PRO-Q03 | Tìm kiếm (data-driven) › Tìm theo mô tả | chromium | ✅ Đạt |  |
| ADM-PRO-Q04 | Tìm kiếm (data-driven) › Tìm theo trạng thái "Hết hạn" | chromium | ✅ Đạt |  |
| ADM-PRO-Q05 | Tìm kiếm (data-driven) › Tìm theo trạng thái "Tạm ẩn" | chromium | ✅ Đạt |  |
| ADM-PRO-Q06 | Tìm kiếm (data-driven) › Không có kết quả -> thông báo không tìm thấy | chromium | ✅ Đạt |  |
| ADM-PRO-V01 | Form thêm - kiểm tra dữ liệu (data-driven) › Bỏ trống tên | chromium | ✅ Đạt |  |
| ADM-PRO-V02 | Form thêm - kiểm tra dữ liệu (data-driven) › Tên chỉ có khoảng trắng | chromium | ✅ Đạt |  |
| ADM-PRO-V03 | Form thêm - kiểm tra dữ liệu (data-driven) › Bỏ trống giá trị giảm @smoke | chromium | ✅ Đạt |  |
| ADM-PRO-V04 | Form thêm - kiểm tra dữ liệu (data-driven) › Giá trị giảm = 0 | chromium | ✅ Đạt |  |
| ADM-PRO-V05 | Form thêm - kiểm tra dữ liệu (data-driven) › Giảm theo % vượt 100 | chromium | ✅ Đạt |  |
| ADM-PRO-V06 | Form thêm - kiểm tra dữ liệu (data-driven) › Giảm theo tiền > 100 hợp lệ, thiếu ngày bắt đầu | chromium | ✅ Đạt |  |
| ADM-PRO-V07 | Form thêm - kiểm tra dữ liệu (data-driven) › Thiếu ngày kết thúc | chromium | ✅ Đạt |  |
| ADM-PRO-V08 | Form thêm - kiểm tra dữ liệu (data-driven) › Ngày kết thúc trước ngày bắt đầu | chromium | ✅ Đạt |  |
| ADM-PRO-V09 | Form thêm - kiểm tra dữ liệu (data-driven) › Giảm đúng 100% vẫn qua bước kiểm tra %, dừng ở ngày | chromium | ✅ Đạt |  |
| ADM-PRO-V10 | Form thêm - kiểm tra dữ liệu (data-driven) › URL ảnh sai định dạng bị trình duyệt chặn (không gửi request) | chromium | ✅ Đạt |  |
| ADM-PRO-G01 | Slug tự sinh (data-driven) › Slug tự sinh từ tên (bỏ dấu, ký tự đặc biệt) | chromium | ✅ Đạt |  |
| ADM-PRO-G02 | Slug tự sinh (data-driven) › Slug tự đặt được giữ khi đổi tên | chromium | ✅ Đạt |  |
| ADM-PRO-G03 | Slug tự sinh (data-driven) › Slug nhập tay được chuẩn hóa | chromium | ✅ Đạt |  |
| ADM-REV-01 | Dữ liệu thật: trang tải được, đủ cột @smoke | chromium | ✅ Đạt |  |
| ADM-REV-02 | Chưa có đánh giá -> trạng thái rỗng | chromium | ✅ Đạt |  |
| ADM-REV-03 | API lỗi -> toast "Không thể tải danh sách đánh giá." | chromium | ✅ Đạt |  |
| ADM-REV-04 | Xem chi tiết và duyệt ngay trong modal (mock PUT) | chromium | ✅ Đạt |  |
| ADM-REV-05 | Xóa: bấm "Hủy" không gửi DELETE | chromium | ✅ Đạt |  |
| ADM-REV-06 | Xóa: xác nhận gửi DELETE và bỏ dòng (mock) | chromium | ✅ Đạt |  |
| ADM-REV-E01 | Server báo lỗi khi duyệt -> hiện thông báo của server | chromium | ✅ Đạt |  |
| ADM-REV-R01 | Hiển thị dòng + nút theo trạng thái (data-driven) › Đánh giá chờ duyệt: đủ thông tin + nút Xem/Duyệt/Ẩn/Xóa @smoke | chromium | ✅ Đạt |  |
| ADM-REV-R02 | Hiển thị dòng + nút theo trạng thái (data-driven) › Đánh giá đã duyệt: không còn nút Duyệt | chromium | ✅ Đạt |  |
| ADM-REV-R03 | Hiển thị dòng + nút theo trạng thái (data-driven) › Đánh giá đã ẩn: không còn nút Ẩn | chromium | ✅ Đạt |  |
| ADM-REV-Q01 | Tìm kiếm (data-driven) › Tìm theo tên khách hàng | chromium | ✅ Đạt |  |
| ADM-REV-Q02 | Tìm kiếm (data-driven) › Tìm theo tên sản phẩm | chromium | ✅ Đạt |  |
| ADM-REV-Q03 | Tìm kiếm (data-driven) › Tìm theo nội dung, không phân biệt hoa thường | chromium | ✅ Đạt |  |
| ADM-REV-Q04 | Tìm kiếm (data-driven) › Sản phẩm trùng tên trả về nhiều dòng | chromium | ✅ Đạt |  |
| ADM-REV-Q05 | Tìm kiếm (data-driven) › Không có kết quả -> thông báo không tìm thấy | chromium | ✅ Đạt |  |
| ADM-REV-F01 | Lọc trạng thái / số sao (data-driven) › Lọc "Chờ duyệt" gửi status=pending | chromium | ✅ Đạt |  |
| ADM-REV-F02 | Lọc trạng thái / số sao (data-driven) › Lọc "Đã duyệt" gửi status=approved | chromium | ✅ Đạt |  |
| ADM-REV-F03 | Lọc trạng thái / số sao (data-driven) › Lọc "1 sao" gửi rating=1 | chromium | ✅ Đạt |  |
| ADM-REV-F04 | Lọc trạng thái / số sao (data-driven) › Kết hợp "Chờ duyệt" + "5 sao" | chromium | ✅ Đạt |  |
| ADM-REV-F05 | Lọc trạng thái / số sao (data-driven) › Bộ lọc không có kết quả -> báo "Không tìm thấy đánh giá phù hợp." | chromium | 🐞 Bug đã biết | BUG: AdminReviews.jsx:216 chỉ xét ô tìm kiếm -> lọc rỗng vẫn hiện 'Chưa có đánh giá nào' |
| ADM-REV-A01 | Duyệt / Ẩn trên dòng (data-driven) › Duyệt đánh giá chờ duyệt (mock PUT) @smoke | chromium | ✅ Đạt |  |
| ADM-REV-A02 | Duyệt / Ẩn trên dòng (data-driven) › Ẩn đánh giá đã duyệt (mock PUT) | chromium | ✅ Đạt |  |
| ADM-REV-A03 | Duyệt / Ẩn trên dòng (data-driven) › Duyệt lại đánh giá đã ẩn (mock PUT) | chromium | ✅ Đạt |  |
| ADM-REV-A04 | Duyệt / Ẩn trên dòng (data-driven) › Ẩn đánh giá chờ duyệt (mock PUT) | chromium | ✅ Đạt |  |

## UI - Admin: Kho, Nhập hàng, Báo cáo, Cài đặt

| ID | Test case | Project | Kết quả | Ghi chú |
|---|---|---|---|---|
| ADO-IMP-01 | Trang tải: tiêu đề, đủ cột, thẻ thống kê @smoke | chromium | ✅ Đạt |  |
| ADO-IMP-04 | Tính thành tiền và tổng tiền nhập (chiết khấu, chi phí) | chromium | ✅ Đạt |  |
| ADO-IMP-E01 | Server từ chối tạo đơn -> hiện thông báo của server | chromium | ✅ Đạt |  |
| ADO-IMP-02 | Xem chi tiết đơn nhập | chromium | ✅ Đạt |  |
| ADO-IMP-03 | Hủy đơn: đồng ý hộp thoại gửi DELETE (mock) | chromium | ✅ Đạt |  |
| ADO-IMP-05 | Hủy đơn: bấm Hủy trên hộp thoại không gửi DELETE | chromium | ✅ Đạt |  |
| ADO-IMP-R01 | Hiển thị dòng + nút theo trạng thái (data-driven) › Đang xử lý: Xem chi tiết / Nhận hàng / Hủy đơn @smoke | chromium | ✅ Đạt |  |
| ADO-IMP-R02 | Hiển thị dòng + nút theo trạng thái (data-driven) › Đã nhận đủ: chỉ còn Xem chi tiết | chromium | ✅ Đạt |  |
| ADO-IMP-R03 | Hiển thị dòng + nút theo trạng thái (data-driven) › Nháp: Xem chi tiết / Hủy đơn, thanh toán một phần | chromium | ✅ Đạt |  |
| ADO-IMP-R04 | Hiển thị dòng + nút theo trạng thái (data-driven) › Đã hủy: chỉ còn Xem chi tiết | chromium | ✅ Đạt |  |
| ADO-IMP-R05 | Hiển thị dòng + nút theo trạng thái (data-driven) › Đã nhận một phần: Xem chi tiết / Nhận hàng | chromium | ✅ Đạt |  |
| ADO-IMP-F01 | Lọc / tìm kiếm phía server (data-driven) › Lọc trạng thái gửi status=processing | chromium | ✅ Đạt |  |
| ADO-IMP-F02 | Lọc / tìm kiếm phía server (data-driven) › Lọc nhà cung cấp gửi supplier_id | chromium | ✅ Đạt |  |
| ADO-IMP-F03 | Lọc / tìm kiếm phía server (data-driven) › Tìm mã đơn gửi search lên server | chromium | ✅ Đạt |  |
| ADO-IMP-F04 | Lọc / tìm kiếm phía server (data-driven) › Không có đơn phù hợp -> "Không có đơn nhập hàng nào" | chromium | ✅ Đạt |  |
| ADO-IMP-V01 | Form tạo đơn - kiểm tra dữ liệu (data-driven) › Chưa chọn nhà cung cấp @smoke | chromium | ✅ Đạt |  |
| ADO-IMP-V02 | Form tạo đơn - kiểm tra dữ liệu (data-driven) › Chưa chọn kho nhận | chromium | ✅ Đạt |  |
| ADO-IMP-V03 | Form tạo đơn - kiểm tra dữ liệu (data-driven) › Chưa có sản phẩm nhập | chromium | ✅ Đạt |  |
| ADO-IMP-V04 | Form tạo đơn - kiểm tra dữ liệu (data-driven) › Sản phẩm có biến thể nhưng chưa chọn biến thể | chromium | ✅ Đạt |  |
| ADO-IMP-V05 | Form tạo đơn - kiểm tra dữ liệu (data-driven) › Số lượng nhập = 0 | chromium | ✅ Đạt |  |
| ADO-IMP-V06 | Form tạo đơn - kiểm tra dữ liệu (data-driven) › Đơn giá nhập âm | chromium | ✅ Đạt |  |
| ADO-IMP-V07 | Form tạo đơn - kiểm tra dữ liệu (data-driven) › Trùng dòng cùng sản phẩm + biến thể | chromium | ✅ Đạt |  |
| ADO-IMP-V08 | Form tạo đơn - kiểm tra dữ liệu (data-driven) › Đã thanh toán lớn hơn tổng tiền | chromium | ✅ Đạt |  |
| ADO-IMP-C01 | Tạo đơn thành công (data-driven, mock POST) › "Tạo đơn nhập hàng" gửi POST status=processing (mock) @smoke | chromium | ✅ Đạt |  |
| ADO-IMP-C02 | Tạo đơn thành công (data-driven, mock POST) › "Lưu nháp" 2 biến thể cùng sản phẩm, đã thanh toán đủ (mock) | chromium | ✅ Đạt |  |
| ADO-IMP-N01 | Nhận hàng (data-driven) › Mọi dòng nhận 0 -> "Vui lòng nhập số lượng nhận." | chromium | ✅ Đạt |  |
| ADO-IMP-N02 | Nhận hàng (data-driven) › Nhận vượt số còn lại -> báo lỗi | chromium | ✅ Đạt |  |
| ADO-IMP-N03 | Nhận hàng (data-driven) › Nhận hàng hợp lệ gửi POST receive (mock) @smoke | chromium | ✅ Đạt |  |
| ADO-IMP-N04 | Nhận hàng (data-driven) › Dòng nhận 0 bị bỏ khỏi payload (mock) | chromium | ✅ Đạt |  |
| ADO-RPT-01 | Dữ liệu thật: đủ thẻ tổng quan và các khối báo cáo @smoke | chromium | ✅ Đạt |  |
| ADO-RPT-02 | Thẻ tổng quan, cảnh báo, biểu đồ trạng thái hiển thị đúng số liệu API | chromium | ✅ Đạt |  |
| ADO-RPT-03 | Bảng "Sản phẩm bán chạy" và "Khách hàng mua nhiều" | chromium | ✅ Đạt |  |
| ADO-RPT-04 | Không có dữ liệu: thẻ = 0 và các khối báo trống | chromium | ✅ Đạt |  |
| ADO-RPT-05 | API lỗi -> toast "Không thể tải dữ liệu báo cáo." | chromium | ✅ Đạt |  |
| ADO-RPT-C01 | "Tùy chọn" + "Lọc" gửi period=custom kèm start_date/end_date | chromium | ✅ Đạt |  |
| ADO-RPT-B01 | "Tùy chọn" mặc định từ ngày 1 tháng này đến hôm nay | chromium | 🐞 Bug đã biết | BUG: AdminReports.jsx:53,129 dateOnly() dùng toISOString (UTC) -> ở UTC+7 ngày 1 của tháng thành ngày cuối tháng trước |
| ADO-RPT-P01 | Chọn kỳ báo cáo (data-driven) › Mặc định "30 ngày qua" gửi period=30days @smoke | chromium | ✅ Đạt |  |
| ADO-RPT-P02 | Chọn kỳ báo cáo (data-driven) › "Hôm nay" gửi period=today | chromium | ✅ Đạt |  |
| ADO-RPT-P03 | Chọn kỳ báo cáo (data-driven) › "7 ngày qua" gửi period=7days | chromium | ✅ Đạt |  |
| ADO-RPT-P04 | Chọn kỳ báo cáo (data-driven) › "Tháng này" gửi period=month | chromium | ✅ Đạt |  |
| ADO-RPT-X01 | Xuất báo cáo CSV (data-driven) › Xuất CSV kỳ mặc định: tên file, BOM, số liệu @smoke | chromium | ✅ Đạt |  |
| ADO-RPT-X02 | Xuất báo cáo CSV (data-driven) › Xuất CSV kỳ "Tùy chọn" ghi đúng khoảng ngày | chromium | ✅ Đạt |  |
| ADO-RPT-X03 | Xuất báo cáo CSV (data-driven) › Xuất CSV kỳ "Hôm nay" | chromium | ✅ Đạt |  |
| ADO-SET-01 | Giá trị từ API được điền vào form (ô nhập + checkbox) | chromium | ✅ Đạt |  |
| ADO-SET-03 | API lỗi -> toast "Không thể tải cấu hình website." | chromium | ✅ Đạt |  |
| ADO-SET-02 | Sửa ở nhiều tab rồi "Lưu cài đặt" gửi PUT đủ thay đổi (mock) | chromium | ✅ Đạt |  |
| ADO-SET-E01 | Server báo lỗi khi lưu -> hiện thông báo của server | chromium | ✅ Đạt |  |
| ADO-SET-T01 | Các tab và ô nhập (data-driven, dữ liệu thật) › Tab "Thông tin cửa hàng" @smoke | chromium | ✅ Đạt |  |
| ADO-SET-T02 | Các tab và ô nhập (data-driven, dữ liệu thật) › Tab "Giao diện" | chromium | ✅ Đạt |  |
| ADO-SET-T03 | Các tab và ô nhập (data-driven, dữ liệu thật) › Tab "Bán hàng" | chromium | ✅ Đạt |  |
| ADO-SET-T04 | Các tab và ô nhập (data-driven, dữ liệu thật) › Tab "Mạng xã hội" | chromium | ✅ Đạt |  |
| ADO-SET-T05 | Các tab và ô nhập (data-driven, dữ liệu thật) › Tab "Chính sách" | chromium | ✅ Đạt |  |
| ADO-SET-V01 | Kiểm tra dữ liệu trước khi lưu (data-driven) › Xóa tên cửa hàng @smoke | chromium | ✅ Đạt |  |
| ADO-SET-V02 | Kiểm tra dữ liệu trước khi lưu (data-driven) › Tên cửa hàng chỉ có khoảng trắng | chromium | ✅ Đạt |  |
| ADO-SET-V03 | Kiểm tra dữ liệu trước khi lưu (data-driven) › Xóa email liên hệ | chromium | ✅ Đạt |  |
| ADO-SET-V04 | Kiểm tra dữ liệu trước khi lưu (data-driven) › Xóa cả tên và email -> báo tên trước | chromium | ✅ Đạt |  |
| ADO-WH-01 | Dữ liệu thật: thẻ thống kê, đủ cột, có sản phẩm @smoke | chromium | ✅ Đạt |  |
| ADO-WH-B03 | Dữ liệu thật: thẻ "Tổng sản phẩm" bằng số sản phẩm trong bảng | chromium | 🐞 Bug đã biết | BUG: adminController.js:1638-1655 PostgreSQL trả alias không đặt trong ngoặc kép thành chữ thường (totalproducts...) nên destructuring { totalProducts, ... } luôn undefined -> các thẻ thống kê kho luôn 0 |
| ADO-WH-02 | Thẻ thống kê hiển thị đúng số liệu API | chromium | ✅ Đạt |  |
| ADO-WH-R01 | Hiển thị dòng (data-driven) › Sắp hết: tồn 3, ngưỡng 5, giá vốn và giá trị @smoke | chromium | ✅ Đạt |  |
| ADO-WH-R02 | Hiển thị dòng (data-driven) › Chưa có giá vốn -> 0đ | chromium | ✅ Đạt |  |
| ADO-WH-R03 | Hiển thị dòng (data-driven) › Hết hàng: tồn 0, giá trị 0đ | chromium | ✅ Đạt |  |
| ADO-WH-T01 | Tab lọc tồn kho (data-driven) › Tab "Sắp hết" gửi filter=low, chỉ còn tồn 1-5 | chromium | ✅ Đạt |  |
| ADO-WH-T02 | Tab lọc tồn kho (data-driven) › Tab "Hết hàng" gửi filter=out, chỉ còn tồn 0 | chromium | ✅ Đạt |  |
| ADO-WH-T03 | Tab lọc tồn kho (data-driven) › Quay lại tab "Tất cả" gửi filter=all | chromium | ✅ Đạt |  |
| ADO-WH-Q01 | Tìm kiếm (data-driven) › Tìm theo tên sản phẩm | chromium | ✅ Đạt |  |
| ADO-WH-Q02 | Tìm kiếm (data-driven) › Tìm theo SKU (không phân biệt hoa thường) | chromium | ✅ Đạt |  |
| ADO-WH-Q03 | Tìm kiếm (data-driven) › Tìm theo danh mục | chromium | ✅ Đạt |  |
| ADO-WH-Q04 | Tìm kiếm (data-driven) › Tìm không dấu vẫn khớp tên có dấu | chromium | ✅ Đạt |  |
| ADO-WH-Q05 | Tìm kiếm (data-driven) › Không có kết quả -> "Không tìm thấy sản phẩm phù hợp." | chromium | ✅ Đạt |  |
| ADO-WH-B01 | Số đếm trên tab (data-driven) › Tab "Tất cả": số đếm trên 3 tab đúng | chromium | ✅ Đạt |  |
| ADO-WH-B02 | Số đếm trên tab (data-driven) › Tab "Sắp hết": số đếm các tab không đổi | chromium | 🐞 Bug đã biết | BUG: AdminWarehouse.jsx:39-40,111-113 đếm số trên tab từ danh sách đang lọc -> ở tab 'Sắp hết' tab 'Tất cả' thành 2 và số của 'Hết hàng' biến mất |

## UI - Admin: Layout, Dashboard, Đơn hàng, Khách hàng, Nhân viên

| ID | Test case | Project | Kết quả | Ghi chú |
|---|---|---|---|---|
| ADS-CUS-01 | Bảng khách hàng: đủ cột, trạng thái, chi tiêu, điểm @smoke | chromium | ✅ Đạt |  |
| ADS-CUS-02 | Tìm khách hàng gửi từ khóa lên API và lọc bảng | chromium | ✅ Đạt |  |
| ADS-CUS-07 | Server báo "Email đã tồn tại." -> toast lỗi, modal vẫn mở | chromium | ✅ Đạt |  |
| ADS-CUS-09 | Modal chi tiết khách hàng (GET /admin/customers/:id) | chromium | ✅ Đạt |  |
| ADS-CUS-13 | Đơn gần đây trong chi tiết khách hiển thị trạng thái tiếng Việt | chromium | 🐞 Bug đã biết | BUG: AdminCustomers.jsx:526 hiển thị mã trạng thái thô ('pending', 'delivered') thay vì nhãn tiếng Việt như trang Đơn hàng |
| ADS-CUS-V01 | Thêm khách hàng › Bỏ trống họ tên và email @smoke | chromium | ✅ Đạt |  |
| ADS-CUS-V02 | Thêm khách hàng › Họ tên chỉ có khoảng trắng | chromium | ✅ Đạt |  |
| ADS-CUS-V03 | Thêm khách hàng › Email thiếu @ | chromium | ✅ Đạt |  |
| ADS-CUS-V04 | Thêm khách hàng › Email thiếu tên miền cấp cao | chromium | ✅ Đạt |  |
| ADS-CUS-V05 | Thêm khách hàng › Số điện thoại không bắt đầu bằng 0 | chromium | ✅ Đạt |  |
| ADS-CUS-V06 | Thêm khách hàng › Số điện thoại quá ngắn | chromium | ✅ Đạt |  |
| ADS-CUS-V07 | Thêm khách hàng › Mật khẩu dưới 6 ký tự | chromium | ✅ Đạt |  |
| ADS-CUS-03 | Thêm khách hàng › Form thêm có placeholder và gợi ý mật khẩu mặc định | chromium | ✅ Đạt |  |
| ADS-CUS-04 | Thêm khách hàng › Thêm khách hợp lệ (mock POST) -> toast, đóng modal, dòng mới đầu bảng | chromium | ✅ Đạt |  |
| ADS-CUS-05 | Thêm khách hàng › Lỗi sửa xong ô nhập thì thông báo lỗi biến mất | chromium | ✅ Đạt |  |
| ADS-CUS-06 | Thêm khách hàng › "Hủy" đóng modal, không gửi request | chromium | ✅ Đạt |  |
| ADS-CUS-08 | Sửa khách hàng › Form sửa điền sẵn dữ liệu; lưu gửi PUT đúng payload (mock) và cập nhật dòng | chromium | ✅ Đạt |  |
| ADS-CUS-EV01 | Sửa khách hàng › Xóa trống họ tên khi sửa | chromium | ✅ Đạt |  |
| ADS-CUS-EV02 | Sửa khách hàng › Email sai định dạng khi sửa | chromium | ✅ Đạt |  |
| ADS-CUS-EV03 | Sửa khách hàng › Mật khẩu mới dưới 6 ký tự bị chặn ở client | chromium | 🐞 Bug đã biết | BUG: AdminCustomers.jsx:55 chỉ kiểm tra độ dài mật khẩu khi THÊM (isNew) - khi sửa vẫn gửi mật khẩu 3 ký tự lên server |
| ADS-CUS-10 | Xóa khách hàng (mock DELETE, data-driven) › Modal xác nhận xóa: nội dung + "Hủy" không gửi request | chromium | ✅ Đạt |  |
| ADS-CUS-D01 | Xóa khách hàng (mock DELETE, data-driven) › Xóa khách chưa có đơn -> xóa khỏi bảng | chromium | ✅ Đạt |  |
| ADS-CUS-D02 | Xóa khách hàng (mock DELETE, data-driven) › Xóa khách đã có đơn -> bị khóa thay vì xóa | chromium | ✅ Đạt |  |
| ADS-CUS-D03 | Xóa khách hàng (mock DELETE, data-driven) › Server lỗi khi xóa -> báo lỗi, giữ dòng | chromium | ✅ Đạt |  |
| ADS-CUS-11 | Phân trang (20 khách/trang) › Bấm trang 2 gọi API page=2 | chromium | ✅ Đạt |  |
| ADS-CUS-12 | Phân trang (20 khách/trang) › Sang trang 6 thì dãy số trang dịch theo (hiện nút 6) | chromium | 🐞 Bug đã biết | BUG: AdminCustomers.jsx:271 dãy nút trang luôn là 1..5 (không dịch theo trang hiện tại) -> không bấm trực tiếp được trang 6-8 |
| ADS-DASH-01 | Dashboard dữ liệu thật: đủ thẻ thống kê và các khối @smoke | chromium | ✅ Đạt |  |
| ADS-DASH-08 | API dashboard lỗi -> hiển thị 0, không crash | chromium | ✅ Đạt |  |
| ADS-DASH-02 | Hiển thị số liệu (mock GET /admin/dashboard) › Thẻ thống kê hiển thị đúng giá trị, dòng phụ và % doanh thu | chromium | ✅ Đạt |  |
| ADS-DASH-03 | Hiển thị số liệu (mock GET /admin/dashboard) › Khối "Đơn hàng theo trạng thái" đúng số lượng | chromium | ✅ Đạt |  |
| ADS-DASH-04 | Hiển thị số liệu (mock GET /admin/dashboard) › "Đơn hàng gần đây" và "Sản phẩm bán chạy" | chromium | ✅ Đạt |  |
| ADS-DASH-05 | Hiển thị số liệu (mock GET /admin/dashboard) › Thẻ thao tác nhanh hiển thị đúng số liệu | chromium | ✅ Đạt |  |
| ADS-DASH-06 | Hiển thị số liệu (mock GET /admin/dashboard) › Biểu đồ vẽ vùng doanh thu + đường đơn hàng theo dữ liệu tháng | chromium | ✅ Đạt |  |
| ADS-DASH-07 | Hiển thị số liệu (mock GET /admin/dashboard) › Đổi khoảng thời gian biểu đồ thì tải lại số liệu | chromium | 🐞 Bug đã biết | BUG: AdminDashboard.jsx:227-232 - ô chọn "7 ngày qua/30 ngày qua/..." không có onChange, không gọi lại API |
| ADS-DASH-G01 | Hiển thị số liệu (mock GET /admin/dashboard) › Thẻ 'Tổng đơn hàng' không hiển thị % tăng trưởng giả | chromium | 🐞 Bug đã biết | BUG: AdminDashboard.jsx:196 - change="+12%" viết cứng, API không trả tăng trưởng đơn hàng |
| ADS-DASH-G02 | Hiển thị số liệu (mock GET /admin/dashboard) › Thẻ 'Khách hàng' không hiển thị % tăng trưởng giả | chromium | 🐞 Bug đã biết | BUG: AdminDashboard.jsx:209 - change="+8%" viết cứng, API không trả tăng trưởng khách hàng |
| ADS-DASH-L01 | Link điều hướng (data-driven) › 'Xem tất cả' ở Đơn hàng gần đây -> /admin/orders | chromium | ✅ Đạt |  |
| ADS-DASH-L02 | Link điều hướng (data-driven) › 'Xem tất cả' ở Sản phẩm bán chạy -> /admin/products | chromium | ✅ Đạt |  |
| ADS-DASH-L03 | Link điều hướng (data-driven) › 'Xem kho hàng' -> /admin/warehouse | chromium | ✅ Đạt |  |
| ADS-DASH-L04 | Link điều hướng (data-driven) › 'Xử lý đơn hàng' -> /admin/orders?status=pending | chromium | ✅ Đạt |  |
| ADS-DASH-L05 | Link điều hướng (data-driven) › 'Xem báo cáo' -> /admin/reports | chromium | ✅ Đạt |  |
| ADS-DASH-L06 | Link điều hướng (data-driven) › "Xử lý đơn hàng" mở trang Đơn hàng đã lọc "Chờ xác nhận" | chromium | 🐞 Bug đã biết | BUG: AdminDashboard.jsx:384 link tới /admin/orders?status=pending nhưng AdminOrders.jsx:80-83 không đọc query string -> không lọc |
| ADS-EMP-00 | Trang nhân viên dữ liệu thật: tiêu đề và cột bảng @smoke | chromium | ✅ Đạt |  |
| ADS-EMP-01 | Dữ liệu mock › Nhãn vai trò hiển thị tiếng Việt cho 4 vai trò | chromium | ✅ Đạt |  |
| ADS-EMP-02 | Dữ liệu mock › Tìm nhân viên gửi từ khóa lên API và lọc bảng | chromium | ✅ Đạt |  |
| ADS-EMP-C01 | Dữ liệu mock › Thêm nhân viên kho | chromium | ✅ Đạt |  |
| ADS-EMP-C02 | Dữ liệu mock › Thêm quản lý (vai trò mặc định đổi sang Quản lý), tài khoản tắt | chromium | ✅ Đạt |  |
| ADS-EMP-V01 | Dữ liệu mock › Thêm nhân viên › Bỏ trống toàn bộ form @smoke | chromium | ✅ Đạt |  |
| ADS-EMP-V02 | Dữ liệu mock › Thêm nhân viên › Email 'a@b' (qua kiểm tra trình duyệt) bị app báo sai định dạng | chromium | ✅ Đạt |  |
| ADS-EMP-V03 | Dữ liệu mock › Thêm nhân viên › Email thiếu @ bị trình duyệt chặn trước khi submit | chromium | ✅ Đạt |  |
| ADS-EMP-V04 | Dữ liệu mock › Thêm nhân viên › Số điện thoại sai định dạng | chromium | ✅ Đạt |  |
| ADS-EMP-V05 | Dữ liệu mock › Thêm nhân viên › Mật khẩu dưới 6 ký tự | chromium | ✅ Đạt |  |
| ADS-EMP-03 | Dữ liệu mock › Thêm nhân viên › Mặc định vai trò "staff" và tài khoản hoạt động | chromium | ✅ Đạt |  |
| ADS-EMP-04 | Dữ liệu mock › Sửa nhân viên › Form sửa điền sẵn; đổi tên + vai trò gửi PUT không kèm mật khẩu (mock) | chromium | ✅ Đạt |  |
| ADS-EMP-05 | Dữ liệu mock › Sửa nhân viên › Nhập mật khẩu mới khi sửa -> payload có password | chromium | ✅ Đạt |  |
| ADS-EMP-EV01 | Dữ liệu mock › Sửa nhân viên › Mật khẩu mới dưới 6 ký tự khi sửa | chromium | ✅ Đạt |  |
| ADS-EMP-EV02 | Dữ liệu mock › Sửa nhân viên › Xóa trống họ tên khi sửa | chromium | ✅ Đạt |  |
| ADS-EMP-06 | Dữ liệu mock › Vô hiệu hóa (nút Xóa) - backend luôn trả 400 › Modal "Xác nhận vô hiệu hóa" + "Hủy" không gửi request | chromium | ✅ Đạt |  |
| ADS-EMP-07 | Dữ liệu mock › Vô hiệu hóa (nút Xóa) - backend luôn trả 400 › Xác nhận -> hiển thị lỗi backend, nhân viên vẫn trong bảng | chromium | ✅ Đạt |  |
| ADS-EMP-08 | Dữ liệu mock › Vô hiệu hóa (nút Xóa) - backend luôn trả 400 › Xác nhận vô hiệu hóa thành công | chromium | 🐞 Bug đã biết | BUG: adminController.deleteEmployee luôn trả 400 "Không thể xóa tài khoản nhân viên..." -> nút Xóa/Vô hiệu hóa ở AdminEmployees.jsx:112-121 không bao giờ thành công (phải dùng nút gạt) |
| ADS-EMP-09 | Dữ liệu mock › Nút gạt trạng thái (mock PUT /toggle) › Tắt tài khoản thành công -> toast + nút gạt xám | chromium | ✅ Đạt |  |
| ADS-EMP-10 | Dữ liệu mock › Nút gạt trạng thái (mock PUT /toggle) › API lỗi -> báo lỗi và giữ nguyên trạng thái | chromium | 🐞 Bug đã biết | BUG: AdminEmployees.jsx:65-67 nhánh catch vẫn đảo is_active nên nút gạt đổi màu dù API lỗi |
| ADS-LAY-T01 | Tiêu đề trang trên header (data-driven) › Tiêu đề trang Tổng quan @smoke | chromium | ✅ Đạt |  |
| ADS-LAY-T02 | Tiêu đề trang trên header (data-driven) › Tiêu đề trang Sản phẩm | chromium | ✅ Đạt |  |
| ADS-LAY-T03 | Tiêu đề trang trên header (data-driven) › Tiêu đề trang Thêm sản phẩm | chromium | ✅ Đạt |  |
| ADS-LAY-T04 | Tiêu đề trang trên header (data-driven) › Tiêu đề trang Chỉnh sửa sản phẩm | chromium | 🐞 Bug đã biết | BUG: AdminLayout.jsx:11,31 - map tiêu đề dùng khóa '/admin/products/edit' nhưng route thật là '/admin/products/edit/:id' -> header hiển thị 'Admin' |
| ADS-LAY-T05 | Tiêu đề trang trên header (data-driven) › Tiêu đề trang Danh mục | chromium | ✅ Đạt |  |
| ADS-LAY-T06 | Tiêu đề trang trên header (data-driven) › Tiêu đề trang Thương hiệu | chromium | ✅ Đạt |  |
| ADS-LAY-T07 | Tiêu đề trang trên header (data-driven) › Tiêu đề trang Đơn hàng | chromium | ✅ Đạt |  |
| ADS-LAY-T08 | Tiêu đề trang trên header (data-driven) › Tiêu đề trang Khách hàng | chromium | ✅ Đạt |  |
| ADS-LAY-T09 | Tiêu đề trang trên header (data-driven) › Tiêu đề trang Nhân viên | chromium | ✅ Đạt |  |
| ADS-LAY-S01 | Sidebar › Thu gọn rồi mở rộng sidebar @smoke | chromium | ✅ Đạt |  |
| ADS-LAY-A01 | Sidebar › Chỉ 'Tổng quan' sáng khi ở /admin | chromium | ✅ Đạt |  |
| ADS-LAY-A02 | Sidebar › Trang con /admin/products/create vẫn sáng mục 'Sản phẩm' | chromium | ✅ Đạt |  |
| ADS-LAY-A03 | Sidebar › Mục 'Khách hàng' sáng khi ở /admin/customers | chromium | ✅ Đạt |  |
| ADS-LAY-S02 | Sidebar › Chân sidebar hiển thị tên + vai trò tài khoản đang đăng nhập | chromium | ✅ Đạt |  |
| ADS-LAY-S03 | Sidebar › "Xem cửa hàng" về trang chủ | chromium | ✅ Đạt |  |
| ADS-LAY-S04 | Sidebar › "Đăng xuất" ở sidebar về trang đăng nhập admin | chromium | ✅ Đạt |  |
| ADS-LAY-U00 | Menu người dùng › Mở menu hiển thị tên, email và 3 mục; bấm ra ngoài thì đóng | chromium | ✅ Đạt |  |
| ADS-LAY-U01 | Menu người dùng › Menu người dùng -> Tổng quan | chromium | ✅ Đạt |  |
| ADS-LAY-U02 | Menu người dùng › Menu người dùng -> Cài đặt | chromium | ✅ Đạt |  |
| ADS-LAY-U03 | Menu người dùng › "Đăng xuất" trong menu người dùng về trang đăng nhập admin | chromium | ✅ Đạt |  |
| ADS-NOTI-B01 | Chuông thông báo (mock GET /admin/notifications) › Không có thông báo -> không hiện số trên chuông | chromium | ✅ Đạt |  |
| ADS-NOTI-B02 | Chuông thông báo (mock GET /admin/notifications) › Số trên chuông bằng tổng số thông báo @smoke | chromium | 🐞 Bug đã biết | BUG: AdminHeader.jsx:34 - totalNotif cộng TẤT CẢ giá trị counts (all + newOrders + lowStock + ...) nên đếm gấp đôi: 3 thông báo hiển thị 6 |
| ADS-NOTI-01 | Chuông thông báo (mock GET /admin/notifications) › Không có thông báo -> panel trống | chromium | ✅ Đạt |  |
| ADS-NOTI-02 | Chuông thông báo (mock GET /admin/notifications) › Panel hiển thị danh sách, thống kê và tổng số thông báo @smoke | chromium | ✅ Đạt |  |
| ADS-NOTI-03 | Chuông thông báo (mock GET /admin/notifications) › "Đánh dấu đã đọc" ẩn nhãn "n mới" | chromium | ✅ Đạt |  |
| ADS-NOTI-04 | Chuông thông báo (mock GET /admin/notifications) › Bấm 1 thông báo -> điều hướng theo link và đóng panel | chromium | ✅ Đạt |  |
| ADS-NOTI-05 | Chuông thông báo (mock GET /admin/notifications) › "Xem tất cả đơn hàng" -> /admin/orders | chromium | ✅ Đạt |  |
| ADS-NOTI-06 | Chuông thông báo (mock GET /admin/notifications) › "Làm mới" gọi lại API thông báo | chromium | ✅ Đạt |  |
| ADS-NOTI-07 | Chuông thông báo (mock GET /admin/notifications) › Đóng panel bằng nút X và bằng bấm ra ngoài | chromium | ✅ Đạt |  |
| ADS-ORD-01 | Không có đơn -> "Không có đơn hàng nào" | chromium | ✅ Đạt |  |
| ADS-ORD-02 | Danh sách & bộ lọc (mock dữ liệu) › Bảng đơn hàng: đủ cột, thẻ trạng thái và dữ liệu dòng @smoke | chromium | ✅ Đạt |  |
| ADS-ORD-F01 | Danh sách & bộ lọc (mock dữ liệu) › Tìm theo mã đơn | chromium | ✅ Đạt |  |
| ADS-ORD-F02 | Danh sách & bộ lọc (mock dữ liệu) › Tìm theo số điện thoại | chromium | ✅ Đạt |  |
| ADS-ORD-F03 | Danh sách & bộ lọc (mock dữ liệu) › Lọc trạng thái 'Đang giao' bằng ô chọn | chromium | ✅ Đạt |  |
| ADS-ORD-F04 | Danh sách & bộ lọc (mock dữ liệu) › Lọc 'Đã thanh toán' | chromium | ✅ Đạt |  |
| ADS-ORD-F05 | Danh sách & bộ lọc (mock dữ liệu) › Bấm thẻ 'Chờ xác nhận' lọc theo trạng thái | chromium | ✅ Đạt |  |
| ADS-ORD-F06 | Danh sách & bộ lọc (mock dữ liệu) › Lọc theo khoảng ngày | chromium | ✅ Đạt |  |
| ADS-ORD-03 | Danh sách & bộ lọc (mock dữ liệu) › Bấm lại thẻ trạng thái đang chọn -> bỏ lọc | chromium | ✅ Đạt |  |
| ADS-ORD-04 | Danh sách & bộ lọc (mock dữ liệu) › "Xóa bộ lọc" đưa mọi bộ lọc về mặc định | chromium | ✅ Đạt |  |
| ADS-ORD-CA01 | Danh sách & bộ lọc (mock dữ liệu) › Nút "Hủy đơn" trên dòng theo trạng thái (data-driven) › Đơn chờ xác nhận có nút Hủy đơn | chromium | ✅ Đạt |  |
| ADS-ORD-CA02 | Danh sách & bộ lọc (mock dữ liệu) › Nút "Hủy đơn" trên dòng theo trạng thái (data-driven) › Đơn đang xử lý có nút Hủy đơn | chromium | ✅ Đạt |  |
| ADS-ORD-CA03 | Danh sách & bộ lọc (mock dữ liệu) › Nút "Hủy đơn" trên dòng theo trạng thái (data-driven) › Đơn đang giao KHÔNG có nút Hủy đơn (backend không cho hủy) | chromium | 🐞 Bug đã biết | BUG: AdminOrders.jsx:409 hiện nút Hủy đơn cho đơn 'shipped' nhưng adminController.cancelOrder trả 400 'Không thể hủy đơn hàng ở trạng thái này' |
| ADS-ORD-CA04 | Danh sách & bộ lọc (mock dữ liệu) › Nút "Hủy đơn" trên dòng theo trạng thái (data-driven) › Đơn đã giao không có nút Hủy đơn | chromium | ✅ Đạt |  |
| ADS-ORD-CA05 | Danh sách & bộ lọc (mock dữ liệu) › Nút "Hủy đơn" trên dòng theo trạng thái (data-driven) › Đơn đã hủy không có nút Hủy đơn | chromium | ✅ Đạt |  |
| ADS-ORD-CA06 | Danh sách & bộ lọc (mock dữ liệu) › Nút "Hủy đơn" trên dòng theo trạng thái (data-driven) › Đơn trả hàng không có nút Hủy đơn | chromium | ✅ Đạt |  |
| ADS-ORD-05 | Chi tiết đơn hàng › Modal chi tiết hiển thị đủ người nhận, địa chỉ, sản phẩm, tổng tiền, lịch sử | chromium | ✅ Đạt |  |
| ADS-ORD-06 | Chi tiết đơn hàng › API đổi trạng thái lỗi -> báo lỗi server, giữ trạng thái cũ | chromium | ✅ Đạt |  |
| ADS-ORD-07 | Chi tiết đơn hàng › Cập nhật thanh toán "Đã thanh toán" (mock PUT) | chromium | ✅ Đạt |  |
| ADS-ORD-08 | Chi tiết đơn hàng › Đơn đã thanh toán không hiện khối "Cập nhật thanh toán" | chromium | ✅ Đạt |  |
| ADS-ORD-09 | Chi tiết đơn hàng › Thông báo "Đơn xác nhận" xuất hiện trong chuông sau khi xác nhận đơn | chromium | 🐞 Bug đã biết | BUG: AdminOrders.jsx:160-168 pushNotification() rồi gọi ngay fetchNotifications(true) -> NotificationContext.jsx:55 ghi đè bằng danh sách từ server nên thông báo vừa đẩy biến mất |
| ADS-ORD-ST01 | Chi tiết đơn hàng › Chuyển trạng thái đơn (data-driven, mock PUT) › Chờ xác nhận -> Xác nhận @smoke | chromium | ✅ Đạt |  |
| ADS-ORD-ST02 | Chi tiết đơn hàng › Chuyển trạng thái đơn (data-driven, mock PUT) › Chờ xác nhận -> Hủy đơn (nút trong chi tiết) | chromium | ✅ Đạt |  |
| ADS-ORD-ST03 | Chi tiết đơn hàng › Chuyển trạng thái đơn (data-driven, mock PUT) › Đã xác nhận -> Xử lý tiếp | chromium | ✅ Đạt |  |
| ADS-ORD-ST04 | Chi tiết đơn hàng › Chuyển trạng thái đơn (data-driven, mock PUT) › Đang xử lý -> Giao hàng | chromium | ✅ Đạt |  |
| ADS-ORD-ST05 | Chi tiết đơn hàng › Chuyển trạng thái đơn (data-driven, mock PUT) › Đang giao -> Đã nhận hàng | chromium | ✅ Đạt |  |
| ADS-ORD-ST06 | Chi tiết đơn hàng › Chuyển trạng thái đơn (data-driven, mock PUT) › Đang giao -> Yêu cầu trả | chromium | ✅ Đạt |  |
| ADS-ORD-ST07 | Chi tiết đơn hàng › Chuyển trạng thái đơn (data-driven, mock PUT) › Đã giao -> Yêu cầu trả | chromium | ✅ Đạt |  |
| ADS-ORD-ST08 | Chi tiết đơn hàng › Chuyển trạng thái đơn (data-driven, mock PUT) › Đơn đã hủy không còn nút chuyển trạng thái | chromium | ✅ Đạt |  |
| ADS-ORD-ST09 | Chi tiết đơn hàng › Chuyển trạng thái đơn (data-driven, mock PUT) › Đơn trả hàng không còn nút chuyển trạng thái | chromium | ✅ Đạt |  |
| ADS-ORD-10 | Hủy đơn từ bảng (mock POST /cancel) › Hủy đơn đã thanh toán có lý do -> gửi lý do, báo hoàn tiền, đơn thành "Đã hủy" @smoke | chromium | ✅ Đạt |  |
| ADS-ORD-11 | Hủy đơn từ bảng (mock POST /cancel) › "Đóng" modal hủy -> không gửi request, đơn giữ nguyên | chromium | ✅ Đạt |  |
| ADS-ORD-12 | Hủy đơn từ bảng (mock POST /cancel) › Server từ chối hủy -> báo lỗi, modal vẫn mở | chromium | ✅ Đạt |  |
| ADS-ORD-13 | Hủy đơn từ bảng (mock POST /cancel) › Đơn dùng điểm -> modal hủy báo hoàn điểm tích lũy | chromium | 🐞 Bug đã biết | BUG: AdminOrders.jsx:700 kiểm tra order.points_used nhưng API danh sách (adminController.getOrders) chỉ trả points_discount -> không bao giờ báo hoàn điểm |
| ADS-ORD-14 | Phân trang › Nhiều trang -> hiển thị "Trang 1 / 3 — 45 đơn hàng" | chromium | ✅ Đạt |  |
| ADS-ORD-15 | Phân trang › Bấm trang 2 tải dữ liệu trang 2 | chromium | 🐞 Bug đã biết | BUG: AdminOrders.jsx:125-130 useEffect tải đơn chỉ phụ thuộc [filters], đổi trang không gọi lại API |

## UI - Đăng nhập / Đăng ký

| ID | Test case | Project | Kết quả | Ghi chú |
|---|---|---|---|---|
| UI-DNDK-01 | Lỗi field biến mất khi người dùng nhập lại | chromium | ✅ Đạt |  |
| UI-DNDK-02 | Nút hiện/ẩn mật khẩu | chromium | ✅ Đạt |  |
| UI-DNDK-03 | Đăng nhập thành công (mock API) chuyển tới trang hồ sơ | chromium | ✅ Đạt |  |
| UI-DNDK-04 | Đăng nhập thành công với tài khoản thật @smoke | chromium | ✅ Đạt |  |
| LOGIN-V01 | Validate form (data-driven) › Bỏ trống email và mật khẩu @smoke | chromium | ✅ Đạt |  |
| LOGIN-V02 | Validate form (data-driven) › Email sai định dạng | chromium | ✅ Đạt |  |
| LOGIN-V03 | Validate form (data-driven) › Số điện thoại sai định dạng | chromium | ✅ Đạt |  |
| LOGIN-V04 | Validate form (data-driven) › Mật khẩu dưới 6 ký tự | chromium | ✅ Đạt |  |
| LOGIN-V05 | Validate form (data-driven) › SĐT hợp lệ nhưng bỏ trống mật khẩu | chromium | ✅ Đạt |  |
| LOGIN-S01 | Lỗi từ server (data-driven) › Email không tồn tại | chromium | 🐞 Bug đã biết | BUG: Interceptor 401 trong services/api.js reload sang /login nên thông báo lỗi bị mất |
| LOGIN-S02 | Lỗi từ server (data-driven) › Đúng email nhưng sai mật khẩu | chromium | 🐞 Bug đã biết | BUG: Interceptor 401 trong services/api.js reload sang /login nên thông báo lỗi bị mất |
| UI-DNDK-05 | Chuyển qua lại giữa Đăng nhập và Đăng ký | chromium | ✅ Đạt |  |
| UI-DNDK-06 | Đăng ký thành công tạo tài khoản thật | chromium | ⏭️ Bỏ qua | Cần E2E_ALLOW_WRITE=1 (ghi dữ liệu thật) |
| REG-V01 | Validate form (data-driven) › Bỏ trống toàn bộ form | chromium | ✅ Đạt |  |
| REG-V02 | Validate form (data-driven) › Mật khẩu xác nhận không khớp | chromium | ✅ Đạt |  |
| REG-V03 | Validate form (data-driven) › Mật khẩu dưới 6 ký tự | chromium | ✅ Đạt |  |
| REG-V04 | Validate form (data-driven) › Thiếu số điện thoại | chromium | ✅ Đạt |  |
| REG-V05 | Validate form (data-driven) › Thiếu họ tên | chromium | ✅ Đạt |  |
| REG-S01 | Lỗi từ server (mock, data-driven) › Email đã tồn tại (mock 409) | chromium | ✅ Đạt |  |
| REG-S02 | Lỗi từ server (mock, data-driven) › Email không hợp lệ theo server (mock 400) | chromium | ✅ Đạt |  |

## UI - Giỏ hàng

| ID | Test case | Project | Kết quả | Ghi chú |
|---|---|---|---|---|
| UI-GH-01 | Luồng thật: thêm sản phẩm từ trang chi tiết rồi xem trong giỏ @smoke | chromium | ✅ Đạt |  |
| UI-GH-02 | Giỏ hàng trống | chromium | ✅ Đạt |  |
| UI-GH-03 | Mở/đóng drawer bằng nút X và phím ESC | chromium | ✅ Đạt |  |
| UI-GH-04 | Có sẵn sản phẩm (cart/items.json) › Hiển thị số lượng và danh sách sản phẩm @smoke | chromium | ✅ Đạt |  |
| UI-GH-05 | Có sẵn sản phẩm (cart/items.json) › Tăng/giảm số lượng và lưu vào localStorage | chromium | ✅ Đạt |  |
| UI-GH-06 | Có sẵn sản phẩm (cart/items.json) › Không giảm được dưới 1 | chromium | ✅ Đạt |  |
| UI-GH-07 | Có sẵn sản phẩm (cart/items.json) › Xóa sản phẩm khỏi giỏ | chromium | ✅ Đạt |  |
| UI-GH-08 | Có sẵn sản phẩm (cart/items.json) › Mặc định chọn tất cả; bỏ chọn hết thì không thanh toán được | chromium | ✅ Đạt |  |
| UI-GH-09 | Có sẵn sản phẩm (cart/items.json) › Giỏ hàng được giữ sau khi reload | chromium | ✅ Đạt |  |
| UI-GH-10 | Có sẵn sản phẩm (cart/items.json) › Bấm THANH TOÁN chuyển tới trang checkout | chromium | ✅ Đạt |  |

## UI - Danh mục, Tìm kiếm, Sản phẩm

| ID | Test case | Project | Kết quả | Ghi chú |
|---|---|---|---|---|
| UI-DMTK-01 | Menu "NAM" mở /nam và hiển thị sản phẩm @smoke | chromium | ✅ Đạt |  |
| UI-DMTK-02 | Menu "NỮ" mở /nu và hiển thị sản phẩm @smoke | chromium | ✅ Đạt |  |
| UI-DMTK-03 | Menu "TRẺ EM" mở /tre-em và hiển thị sản phẩm @smoke | chromium | ✅ Đạt |  |
| UI-DMTK-04 | Menu "GIẢM GIÁ" mở /giam-gia và hiển thị sản phẩm @smoke | chromium | ✅ Đạt |  |
| UI-DMTK-05 | Click sản phẩm trong danh mục mở trang chi tiết | chromium | ✅ Đạt |  |
| UI-DMTK-06 | Slug không tồn tại hiển thị "Không tìm thấy sản phẩm" | chromium | 🐞 Bug đã biết | BUG: ProductDetailPage hiển thị mockProduct (sản phẩm giả) khi API trả 404 |
| UI-DMTK-07 | Hiển thị đầy đủ các size và cảnh báo chọn size @smoke | chromium | ✅ Đạt |  |
| UI-DMTK-08 | Chưa chọn size mà bấm thêm vào giỏ -> báo lỗi | chromium | ✅ Đạt |  |
| UI-DMTK-09 | Chọn size làm mất cảnh báo | chromium | ✅ Đạt |  |
| UI-DMTK-10 | Thêm vào giỏ thành công cập nhật badge giỏ hàng @smoke | chromium | ✅ Đạt |  |
| UI-DMTK-11 | Gợi ý: [SEARCH-01] Gõ tên đầy đủ hiện gợi ý đúng sản phẩm @smoke | chromium | ✅ Đạt |  |
| UI-DMTK-12 | Trang kết quả: [SEARCH-02] Enter với từ đầu tiên trong tên sản phẩm | chromium | ✅ Đạt |  |
| UI-DMTK-13 | Không có kết quả: [SEARCH-03] Chuỗi vô nghĩa | chromium | ✅ Đạt |  |
| UI-DMTK-14 | Không có kết quả: [SEARCH-04] Chuỗi số dài | chromium | ✅ Đạt |  |

## UI - Thanh toán

| ID | Test case | Project | Kết quả | Ghi chú |
|---|---|---|---|---|
| UI-TT-01 | Giỏ trống -> hiển thị thông báo, không có form | chromium | ✅ Đạt |  |
| UI-TT-02 | /order-success không có dữ liệu đơn | chromium | ✅ Đạt |  |
| UI-TT-03 | Đặt hàng thật end-to-end (ghi DB) | chromium | ⏭️ Bỏ qua | Cần E2E_ALLOW_WRITE=1 (ghi dữ liệu thật) |
| UI-TT-04 | Khách vãng lai, có sản phẩm trong giỏ › Hiển thị sản phẩm và nút Đăng nhập @smoke | chromium | ✅ Đạt |  |
| CO-01 | Khách vãng lai, có sản phẩm trong giỏ › Đặt hàng (mock API, data-driven) › COD + giao tiêu chuẩn (HCM) @smoke | chromium | ✅ Đạt |  |
| CO-02 | Khách vãng lai, có sản phẩm trong giỏ › Đặt hàng (mock API, data-driven) › Chuyển khoản + giao nhanh (Hà Nội) | chromium | ✅ Đạt |  |
| CO-03 | Khách vãng lai, có sản phẩm trong giỏ › Đặt hàng (mock API, data-driven) › VNPay + giao tiêu chuẩn (Đà Nẵng) | chromium | ✅ Đạt |  |
| CO-04 | Khách vãng lai, có sản phẩm trong giỏ › Đặt hàng (mock API, data-driven) › MoMo + giao nhanh (HCM) | chromium | ✅ Đạt |  |
| CO-V01 | Khách vãng lai, có sản phẩm trong giỏ › Thiếu thông tin bắt buộc (data-driven) › Thiếu họ | chromium | ✅ Đạt |  |
| CO-V02 | Khách vãng lai, có sản phẩm trong giỏ › Thiếu thông tin bắt buộc (data-driven) › Thiếu tên | chromium | ✅ Đạt |  |
| CO-V03 | Khách vãng lai, có sản phẩm trong giỏ › Thiếu thông tin bắt buộc (data-driven) › Thiếu số điện thoại | chromium | ✅ Đạt |  |
| CO-V04 | Khách vãng lai, có sản phẩm trong giỏ › Thiếu thông tin bắt buộc (data-driven) › Thiếu địa chỉ chi tiết | chromium | ✅ Đạt |  |
| CO-S01 | Khách vãng lai, có sản phẩm trong giỏ › Backend lỗi (mock, data-driven) › Hết hàng (400) | chromium | ✅ Đạt |  |
| CO-S02 | Khách vãng lai, có sản phẩm trong giỏ › Backend lỗi (mock, data-driven) › Lỗi server (500) | chromium | ✅ Đạt |  |

## Kịch bản Keyword-driven

| ID | Test case | Project | Kết quả | Ghi chú |
|---|---|---|---|---|
| KD-SHOP-01 | Khách vãng lai tìm sản phẩm, thêm vào giỏ và đặt hàng COD @smoke | chromium | ✅ Đạt |  |
| KD-SHOP-02 | Quản lý giỏ hàng: tăng, giảm, xóa, tạm tính | chromium | ✅ Đạt |  |
| KD-SHOP-03 | Duyệt danh mục Nữ và mở sản phẩm đầu tiên | chromium | ✅ Đạt |  |
| KD-SHOP-04 | Thanh toán bị khóa khi xóa số điện thoại | chromium | ✅ Đạt |  |
| KD-ACC-01 | Đăng nhập, xem đơn hàng, đăng xuất @smoke | chromium | ✅ Đạt |  |
| KD-ACC-02 | Khôi phục phiên qua API rồi vào trang Yêu thích | chromium | ✅ Đạt |  |
| KD-ACC-03 | Đăng nhập sai mật khẩu hiển thị lỗi | chromium | 🐞 Bug đã biết | BUG: Interceptor 401 trong services/api.js reload sang /login nên thông báo lỗi bị mất |
| KD-ACC-04 | Đăng ký: validate form trống | chromium | ✅ Đạt |  |
| KD-ADM-01 | Admin đăng nhập, xem Sản phẩm và Đơn hàng @smoke | chromium | ✅ Đạt |  |
| KD-ADM-02 | Chưa đăng nhập không vào được trang quản trị | chromium | ✅ Đạt |  |
| KD-SF-01 | Trang Giảm giá: sắp xếp giá tăng dần rồi xem chi tiết sản phẩm đầu tiên @smoke | chromium | ✅ Đạt |  |
| KD-SF-02 | Blog (mock): lọc danh mục, đọc bài, quay lại danh sách | chromium | ✅ Đạt |  |
| KD-SF-03 | Chi tiết sản phẩm (mock): xem ảnh, đổi màu, mở accordion, khách chưa đăng nhập không đánh giá được | chromium | ✅ Đạt |  |
| KD-SF-04 | Trang /search theo danh mục: chip lọc, bỏ chip, sắp xếp giá giảm dần | chromium | ✅ Đạt |  |
| KD-SF-05 | Trang chủ (mock): chuyển banner, dùng mã voucher, đăng ký nhận tin | chromium | ✅ Đạt |  |
| KD-ACC-11 | Hồ sơ: vào qua menu, sửa SĐT + giới tính (mock API) và kiểm tra hiển thị @smoke | chromium | ✅ Đạt |  |
| KD-ACC-12 | Đơn hàng: lọc Chờ xác nhận, mở chi tiết và hủy đơn có lý do (mock API) | chromium | ✅ Đạt |  |
| KD-ACC-13 | Sổ địa chỉ: thêm địa chỉ đầu tiên từ màn hình trống (mock API) | chromium | ✅ Đạt |  |
| KD-ACC-14 | Yêu thích: sắp xếp giá giảm dần rồi bỏ yêu thích 1 sản phẩm (mock API) | chromium | ✅ Đạt |  |
| KD-ACC-15 | Đã đăng nhập: thanh toán COD (mock tạo đơn) -> trang thành công -> Xem đơn hàng | chromium | ✅ Đạt |  |
| KD-ADC-01 | Admin xem danh sách sản phẩm thật rồi mở form thêm (validate trống) @smoke | chromium | ✅ Đạt |  |
| KD-ADC-02 | Thêm danh mục mới (mock POST) và thấy thẻ mới | chromium | ✅ Đạt |  |
| KD-ADC-03 | Tìm thương hiệu rồi tắt hoạt động (mock PUT) | chromium | ✅ Đạt |  |
| KD-ADC-04 | Tạo sản phẩm có 2 biến thể (mock POST) rồi về danh sách | chromium | ✅ Đạt |  |
| KD-ADS-01 | Dashboard hiển thị số liệu (mock) và đi tới Đơn hàng @smoke | chromium | ✅ Đạt |  |
| KD-ADS-02 | Xác nhận đơn hàng chờ xử lý (mock GET + PUT) | chromium | ✅ Đạt |  |
| KD-ADS-03 | Thêm khách hàng: lỗi validate rồi sửa và lưu (mock POST) | chromium | ✅ Đạt |  |
| KD-ADS-04 | Mở chuông thông báo (mock) và đi tới trang đánh giá | chromium | ✅ Đạt |  |
| KD-ADS-05 | Sửa vai trò nhân viên (mock PUT) rồi gạt tắt tài khoản (mock PUT) | chromium | ✅ Đạt |  |
| KD-ADM2-01 | Khuyến mãi: tìm không dấu và kiểm tra trạng thái tính theo ngày @smoke | chromium | ✅ Đạt |  |
| KD-ADM2-02 | Khuyến mãi: thêm mới gửi đúng dữ liệu (mock POST) | chromium | ✅ Đạt |  |
| KD-ADM2-03 | Mã giảm giá: tắt Công khai rồi xóa mã (mock PUT/DELETE) | chromium | ✅ Đạt |  |
| KD-ADM2-04 | Đánh giá: lọc chờ duyệt rồi duyệt 1 đánh giá (mock) | chromium | ✅ Đạt |  |
| KD-ADM2-05 | Bài viết: lưu khi thiếu tiêu đề bị chặn, không gửi request | chromium | ✅ Đạt |  |
| KD-ADM2-06 | Liên hệ: xem chi tiết và đánh dấu đã xử lý (mock PUT) | chromium | ✅ Đạt |  |
| KD-ADO-01 | Kho hàng: thẻ thống kê, tab Sắp hết và tìm kiếm @smoke | chromium | ✅ Đạt |  |
| KD-ADO-02 | Nhập hàng: tạo đơn nháp 2 biến thể (mock GET + POST) | chromium | ✅ Đạt |  |
| KD-ADO-03 | Nhập hàng: nhận hàng một phần rồi hủy đơn qua hộp thoại (mock) | chromium | ✅ Đạt |  |
| KD-ADO-04 | Báo cáo: đổi kỳ 7 ngày, lọc tùy chọn và xuất CSV | chromium | ✅ Đạt |  |
| KD-ADO-05 | Cài đặt: tắt COD, đổi phí ship rồi lưu (mock PUT) | chromium | ✅ Đạt |  |

## UI - Trang chủ & trang tĩnh

| ID | Test case | Project | Kết quả | Ghi chú |
|---|---|---|---|---|
| UI-TCTT-01 | Tải trang chủ, hiển thị header, sản phẩm và footer | chromium | ✅ Đạt |  |
| UI-TCTT-02 | Không có lỗi JavaScript khi tải trang chủ | chromium | ✅ Đạt |  |
| UI-TCTT-03 | Thanh điều hướng có đủ danh mục | chromium | ✅ Đạt |  |
| UI-TCTT-04 | Click logo quay về trang chủ | chromium | ✅ Đạt |  |
| UI-TCTT-05 | Click sản phẩm đầu tiên mở trang chi tiết | chromium | ✅ Đạt |  |
| UI-TCTT-06 | Giới thiệu (/about) tải thành công | chromium | ✅ Đạt |  |
| UI-TCTT-07 | Chính sách giao hàng (/shipping) tải thành công | chromium | ✅ Đạt |  |
| UI-TCTT-08 | Đổi trả (/returns) tải thành công | chromium | ✅ Đạt |  |
| UI-TCTT-09 | Bảo mật (/privacy) tải thành công | chromium | ✅ Đạt |  |
| UI-TCTT-10 | Blog (/blog) tải thành công | chromium | ✅ Đạt |  |

## UI - Cửa hàng (trang chủ, danh sách, sản phẩm, blog, trang tĩnh)

| ID | Test case | Project | Kết quả | Ghi chú |
|---|---|---|---|---|
| SF-BLOG-10 | Không có bài viết nào -> chỉ có "Tất cả" và thông báo trống | chromium | ✅ Đạt |  |
| SF-BLOG-01 | /blog hiển thị tiêu đề, danh mục và bài viết @smoke | chromium | ✅ Đạt |  |
| SF-BLOG-08 | Slug bài viết không tồn tại -> chuyển về /blog | chromium | ✅ Đạt |  |
| SF-BLOG-02 | Danh mục lấy từ bài viết, mặc định "Tất cả" hiển thị mọi bài | chromium | ✅ Đạt |  |
| SF-BLOG-03 | Lọc "Phối đồ" chỉ còn 2 bài Phối đồ | chromium | ✅ Đạt |  |
| SF-BLOG-04 | Lọc "Thuật ngữ - Kiến thức" chỉ còn 2 bài | chromium | ✅ Đạt |  |
| SF-BLOG-05 | Lọc "Xu hướng" chỉ còn 1 bài | chromium | ✅ Đạt |  |
| SF-BLOG-06 | Chi tiết bài đầy đủ: danh mục, tác giả, lượt xem, tag, bài liên quan | chromium | ✅ Đạt |  |
| SF-BLOG-07 | Chi tiết bài thiếu dữ liệu: tác giả mặc định, 0 lượt xem, nội dung đang cập nhật | chromium | ✅ Đạt |  |
| SF-BLOG-09 | Bài liên quan mở bài khác, "Quay lại Blog" về danh sách | chromium | ✅ Đạt |  |
| SF-BLOG-11 | Đăng ký nhận tin ở trang Blog không tải lại trang | chromium | 🐞 Bug đã biết | BUG: BlogPage.jsx:139 <form> không có onSubmit -> bấm "Đăng ký" submit form GET, tải lại trang, không có phản hồi |
| SF-FOOT-01 | Footer có đủ cột, link và dòng bản quyền | chromium | ✅ Đạt |  |
| SF-FOOT-02 | Footer "Chính sách đổi trả" trỏ tới /returns | chromium | 🐞 Bug đã biết | BUG: Footer.jsx:37 mọi link dùng to="#" (render href="/") -> không tới trang Đổi trả |
| SF-FOOT-03 | Footer "Giới thiệu" trỏ tới /about | chromium | 🐞 Bug đã biết | BUG: Footer.jsx:47 mọi link dùng to="#" (render href="/") -> không tới trang Giới thiệu |
| SF-FOOT-04 | Footer có link tới trang Chính sách giao hàng /shipping | chromium | 🐞 Bug đã biết | BUG: Footer.jsx:36 thiếu link tới /shipping (trang chỉ vào được bằng URL) |
| SF-FOOT-05 | Footer có link tới trang Chính sách bảo mật /privacy | chromium | 🐞 Bug đã biết | BUG: Footer.jsx:36 thiếu link tới /privacy (trang chỉ vào được bằng URL) |
| SF-NEWS-01 | Trang chủ: email hợp lệ -> "Cảm ơn bạn đã đăng ký!" @smoke | chromium | ✅ Đạt |  |
| SF-NEWS-02 | Trang chủ: bỏ trống email -> trình duyệt chặn | chromium | ✅ Đạt |  |
| SF-NEWS-03 | Trang chủ: email sai định dạng -> trình duyệt chặn | chromium | ✅ Đạt |  |
| SF-NEWS-04 | Trang Giới thiệu: email hợp lệ -> "Cảm ơn bạn đã đăng ký!" | chromium | ✅ Đạt |  |
| SF-NEWS-05 | Trang Nam: email thiếu tên miền -> trình duyệt chặn | chromium | ✅ Đạt |  |
| SF-HOME-01 | Dữ liệu thật: đủ các khối nội dung, không lỗi JavaScript @smoke | chromium | ✅ Đạt |  |
| SF-HOME-06 | API /home lỗi 500: vẫn hiển thị banner mặc định, ẩn ưu đãi, tin tức rỗng | chromium | ✅ Đạt |  |
| SF-HOME-02 | Banner (mock, đồng hồ cố định để slide không tự chuyển giữa các bước) › Banner: 3 slide, slide 1 hiển thị trước, link mỗi slide theo link_url | chromium | ✅ Đạt |  |
| SF-HOME-03 | Banner (mock, đồng hồ cố định để slide không tự chuyển giữa các bước) › Banner: mũi tên sau/trước chuyển slide và quay vòng | chromium | ✅ Đạt |  |
| SF-HOME-04 | Banner (mock, đồng hồ cố định để slide không tự chuyển giữa các bước) › Banner: bấm chấm điều hướng nhảy tới slide tương ứng | chromium | ✅ Đạt |  |
| SF-HOME-05 | Banner (mock, đồng hồ cố định để slide không tự chuyển giữa các bước) › Banner: tự chuyển slide sau khoảng 4 giây | chromium | ✅ Đạt |  |
| SF-HOME-07 | Banner (mock, đồng hồ cố định để slide không tự chuyển giữa các bước) › Chữ trên slide 3: nút "Khám phá ngay" dùng link_url của banner | chromium | 🐞 Bug đã biết | BUG: Banner.jsx:109 nút "Khám phá ngay" dùng banner.cta (API không có) -> luôn trỏ /nam thay vì link_url |
| SF-HOME-08 | Dữ liệu mock cố định › Ưu đãi nổi bật: tiêu đề, mô tả, điều kiện, HSD / sắp hết hạn | chromium | ✅ Đạt |  |
| SF-HOME-09 | Dữ liệu mock cố định › "Dùng mã" lưu voucher chờ áp dụng và chuyển tới /nam | chromium | ✅ Đạt |  |
| SF-HOME-11 | Dữ liệu mock cố định › Tab NAM lọc SẢN PHẨM MỚI chỉ còn sản phẩm nam | chromium | 🐞 Bug đã biết | BUG: Home.jsx:76-87 các tab SẢN PHẨM MỚI không có onClick -> không đổi tab, không lọc |
| SF-HOME-12 | Dữ liệu mock cố định › Tab NỮ lọc SẢN PHẨM MỚI chỉ còn sản phẩm nữ | chromium | 🐞 Bug đã biết | BUG: Home.jsx:76-87 các tab SẢN PHẨM MỚI không có onClick -> không đổi tab, không lọc |
| SF-HOME-13 | Dữ liệu mock cố định › SẢN PHẨM MỚI: 5 tab, 8 sản phẩm, mũi tên cuộn carousel | chromium | ✅ Đạt |  |
| SF-HOME-14 | Dữ liệu mock cố định › Khối HOMEWEAR / T-SHIRT / VÁY: mô tả và tối đa 4 sản phẩm | chromium | ✅ Đạt |  |
| SF-HOME-15 | Dữ liệu mock cố định › Khối C-LIVE: tiêu đề, ảnh, lời mời tải app | chromium | ✅ Đạt |  |
| SF-HOME-16 | Dữ liệu mock cố định › Tin tức thời trang: 1 bài nổi bật + 4 bài phụ, "Xem thêm" tới /blog | chromium | ✅ Đạt |  |
| SF-HOME-17 | Dữ liệu mock cố định › Bộ sưu tập DORAEMON có nút "Khám phá" | chromium | 🐞 Bug đã biết | BUG: CollectionSection.jsx:54 đọc collection.ctaText nhưng API trả cta_text -> nút CTA trống chữ |
| SF-HOME-18 | Dữ liệu mock cố định › Bộ sưu tập DISNEY có nút "Khám phá" | chromium | 🐞 Bug đã biết | BUG: CollectionSection.jsx:54 đọc collection.ctaText nhưng API trả cta_text -> nút CTA trống chữ |
| SF-HOME-20 | Dữ liệu mock cố định › Thêm nhanh vào giỏ từ thẻ sản phẩm: toast và badge giỏ hàng | chromium | ✅ Đạt |  |
| SF-HOME-25 | Dữ liệu mock cố định › Thêm nhanh vào giỏ phải kèm size như trang chi tiết | chromium | 🐞 Bug đã biết | BUG: ProductCard.jsx:37 addItem(product, 1, null, null) -> sản phẩm vào giỏ không có size/màu |
| SF-HOME-21 | Dữ liệu mock cố định › SẢN PHẨM MỚI: "Xem tất cả →" mở trang có nội dung | chromium | 🐞 Bug đã biết | BUG: Home.jsx:69 href="/products" nhưng App.jsx không có route /products -> trang trắng |
| SF-HOME-22 | Dữ liệu mock cố định › HOMEWEAR: "Khám phá ngay" mở trang có nội dung | chromium | 🐞 Bug đã biết | BUG: Home.jsx:154 href="/homewear" không có route -> trang trắng |
| SF-HOME-23 | Dữ liệu mock cố định › T-SHIRT: "Xem tất cả" mở trang có nội dung | chromium | 🐞 Bug đã biết | BUG: Home.jsx:220 href="/products?category=tshirt" không có route /products -> trang trắng |
| SF-HOME-24 | Dữ liệu mock cố định › VÁY: "Khám phá ngay" mở trang có nội dung | chromium | 🐞 Bug đã biết | BUG: Home.jsx:246 href="/products?category=vay" không có route /products -> trang trắng |
| SF-HOME-10 | Dữ liệu mock: trường hợp rỗng › Không có voucher -> ẩn khối ƯU ĐÃI NỔI BẬT | chromium | ✅ Đạt |  |
| SF-HOME-19 | Dữ liệu mock: trường hợp rỗng › Không có tin tức -> "Chưa có tin tức thời trang nào", ẩn "Xem thêm" | chromium | ✅ Đạt |  |
| SF-LST-RACE | Lọc giá: response cũ trả chậm không được ghi đè kết quả mới | chromium | 🐞 Bug đã biết | BUG: ProductFilters.jsx handleApply gọi API mỗi lần blur, MenPage không hủy request cũ -> kết quả cũ ghi đè |
| SF-LST-01 | Bố cục trang (dữ liệu thật) › Nam: tiêu đề, breadcrumb, số lượng, sắp xếp, bộ lọc mặc định @smoke | chromium | ✅ Đạt |  |
| SF-LST-02 | Bố cục trang (dữ liệu thật) › Nữ: tiêu đề, breadcrumb, số lượng, sắp xếp, bộ lọc mặc định | chromium | ✅ Đạt |  |
| SF-LST-03 | Bố cục trang (dữ liệu thật) › Trẻ em: tiêu đề, breadcrumb, số lượng, sắp xếp, bộ lọc mặc định | chromium | ✅ Đạt |  |
| SF-LST-04 | Bố cục trang (dữ liệu thật) › Giảm giá: tiêu đề, breadcrumb, số lượng, sắp xếp, bộ lọc mặc định | chromium | ✅ Đạt |  |
| SF-LST-56 | Bố cục trang (dữ liệu thật) › Giảm giá: "Xem thêm +" hiện đủ 8 danh mục | chromium | ✅ Đạt |  |
| SF-LST-05 | Sắp xếp theo giá (dữ liệu thật) › Nam: sắp xếp "Giá: Thấp → Cao" (dữ liệu thật) | chromium | ✅ Đạt |  |
| SF-LST-06 | Sắp xếp theo giá (dữ liệu thật) › Nam: sắp xếp "Giá: Cao → Thấp" (dữ liệu thật) | chromium | ✅ Đạt |  |
| SF-LST-07 | Sắp xếp theo giá (dữ liệu thật) › Nữ: sắp xếp "Giá: Thấp → Cao" (dữ liệu thật) | chromium | ✅ Đạt |  |
| SF-LST-08 | Sắp xếp theo giá (dữ liệu thật) › Nữ: sắp xếp "Giá: Cao → Thấp" (dữ liệu thật) | chromium | ✅ Đạt |  |
| SF-LST-09 | Sắp xếp theo giá (dữ liệu thật) › Trẻ em: sắp xếp "Giá: Thấp → Cao" (dữ liệu thật) | chromium | ✅ Đạt |  |
| SF-LST-10 | Sắp xếp theo giá (dữ liệu thật) › Trẻ em: sắp xếp "Giá: Cao → Thấp" (dữ liệu thật) | chromium | ✅ Đạt |  |
| SF-LST-11 | Sắp xếp theo giá (dữ liệu thật) › Giảm giá: sắp xếp "Giá: Thấp → Cao" (dữ liệu thật) | chromium | ✅ Đạt |  |
| SF-LST-12 | Sắp xếp theo giá (dữ liệu thật) › Giảm giá: sắp xếp "Giá: Cao → Thấp" (dữ liệu thật) | chromium | ✅ Đạt |  |
| SF-LST-13 | Trạng thái rỗng (mock API) › Nam: API trả rỗng -> thông báo không có sản phẩm (mock) | chromium | ✅ Đạt |  |
| SF-LST-14 | Trạng thái rỗng (mock API) › Nữ: API trả rỗng -> thông báo không có sản phẩm (mock) | chromium | ✅ Đạt |  |
| SF-LST-15 | Trạng thái rỗng (mock API) › Trẻ em: API trả rỗng -> thông báo không có sản phẩm (mock) | chromium | ✅ Đạt |  |
| SF-LST-16 | Trạng thái rỗng (mock API) › Giảm giá: API trả rỗng -> thông báo không có sản phẩm (mock) | chromium | ✅ Đạt |  |
| SF-LST-17 | Lọc danh mục (mock API) › Nam: lọc danh mục "Áo Polo" gửi category=ao-polo (mock) | chromium | ✅ Đạt |  |
| SF-LST-18 | Lọc danh mục (mock API) › Nữ: lọc danh mục "Váy" gửi category=vay (mock) | chromium | ✅ Đạt |  |
| SF-LST-19 | Lọc danh mục (mock API) › Trẻ em: lọc danh mục "Áo Trẻ Em" gửi category=ao-tre-em (mock) | chromium | ✅ Đạt |  |
| SF-LST-20 | Lọc danh mục (mock API) › Giảm giá: lọc danh mục "Áo Thun" còn 3 sản phẩm (mock, lọc phía trình duyệt) | chromium | ✅ Đạt |  |
| SF-LST-29 | Lọc màu (mock API) › Nam: lọc màu "Đen" gửi color=1 (mock) | chromium | ✅ Đạt |  |
| SF-LST-30 | Lọc màu (mock API) › Nữ: lọc màu "Hồng" gửi color=7 (mock) | chromium | ✅ Đạt |  |
| SF-LST-31 | Lọc màu (mock API) › Trẻ em: lọc màu "Đen" gửi color=den (mock) | chromium | ✅ Đạt |  |
| SF-LST-32 | Lọc màu (mock API) › Giảm giá: lọc màu "Đen" còn 5 sản phẩm (mock) | chromium | ✅ Đạt |  |
| SF-LST-21 | Lọc khoảng giá (dữ liệu thật) › Nam: lọc giá 300.000 - 600.000 (dữ liệu thật) | chromium | ✅ Đạt |  |
| SF-LST-22 | Lọc khoảng giá (dữ liệu thật) › Nữ: lọc giá 300.000 - 600.000 (dữ liệu thật) | chromium | ✅ Đạt |  |
| SF-LST-23 | Lọc khoảng giá (dữ liệu thật) › Trẻ em: lọc giá 300.000 - 600.000 (dữ liệu thật) | chromium | ✅ Đạt |  |
| SF-LST-24 | Lọc khoảng giá (dữ liệu thật) › Giảm giá: lọc giá 300.000 - 600.000 (dữ liệu thật) | chromium | ✅ Đạt |  |
| SF-LST-25 | Lọc phần trăm giảm (dữ liệu thật) › Nam: lọc "Giảm 30%" chỉ còn sản phẩm giảm >= 30% (dữ liệu thật) | chromium | ✅ Đạt |  |
| SF-LST-26 | Lọc phần trăm giảm (dữ liệu thật) › Nữ: lọc "Giảm 30%" chỉ còn sản phẩm giảm >= 30% (dữ liệu thật) | chromium | ✅ Đạt |  |
| SF-LST-27 | Lọc phần trăm giảm (dữ liệu thật) › Trẻ em: lọc "Giảm 30%" chỉ còn sản phẩm giảm >= 30% (dữ liệu thật) | chromium | ✅ Đạt |  |
| SF-LST-28 | Lọc phần trăm giảm (dữ liệu thật) › Giảm giá: lọc "Giảm 30%" chỉ còn sản phẩm giảm >= 30% (dữ liệu thật) | chromium | ✅ Đạt |  |
| SF-LST-33 | Lọc size (mock API) › Nam: lọc size M gửi size=M lên API | chromium | 🐞 Bug đã biết | BUG: ProductFilters.jsx:88 SizeFilter gọi onChange(size.id) (chuỗi) thay vì mảng -> selectedSizes.join/.some lỗi; MenPage.jsx:144 không gửi request, danh sách rỗng |
| SF-LST-34 | Lọc size (mock API) › Nữ: lọc size M gửi size=M lên API | chromium | 🐞 Bug đã biết | BUG: ProductFilters.jsx:88 SizeFilter gọi onChange(size.id) (chuỗi) thay vì mảng -> selectedSizes.join/.some lỗi; WomenPage.jsx không gửi request, danh sách rỗng |
| SF-LST-35 | Lọc size (mock API) › Trẻ em: lọc size M gửi size=M lên API | chromium | 🐞 Bug đã biết | BUG: ProductFilters.jsx:88 SizeFilter gọi onChange(size.id) (chuỗi) thay vì mảng -> selectedSizes.join/.some lỗi; KidsPage.jsx:154 không gửi request, danh sách rỗng |
| SF-LST-36 | Lọc size (mock API) › Giảm giá: lọc size M chỉ còn 5 sản phẩm có size M (mock) | chromium | 🐞 Bug đã biết | BUG: ProductFilters.jsx:88 SizeFilter gọi onChange(size.id) (chuỗi) thay vì mảng -> selectedSizes.join/.some lỗi; SalePage.jsx:138 selectedSizes.some không phải hàm -> trang crash |
| SF-LST-37 | Phân trang (mock API) › Nam: bấm trang 2 gửi page=2 (mock) | chromium | ✅ Đạt |  |
| SF-LST-38 | Phân trang (mock API) › Nam: bấm "trang sau" gửi page=2 (mock) | chromium | ✅ Đạt |  |
| SF-LST-39 | Phân trang (mock API) › Nam: "Xem thêm sản phẩm" tải trang tiếp theo | chromium | 🐞 Bug đã biết | BUG: MenPage.jsx:424 nút "Xem thêm sản phẩm" không có onClick |
| SF-LST-40 | Phân trang (mock API) › Nữ: "Xem thêm sản phẩm" tải trang tiếp theo (mock) | chromium | ✅ Đạt |  |
| SF-LST-41 | Phân trang (mock API) › Trẻ em: bấm trang 2 gửi page=2 (mock) | chromium | ✅ Đạt |  |
| SF-LST-42 | Phân trang (mock API) › Giảm giá: bấm trang 2 hiển thị 2 sản phẩm còn lại (mock) | chromium | ✅ Đạt |  |
| SF-LST-43 | Phân trang (mock API) › Giảm giá: bấm "trang sau" hiển thị trang 2 (mock) | chromium | ✅ Đạt |  |
| SF-LST-44 | Nút trên thẻ sản phẩm (dữ liệu thật) › Nam: "Thêm vào giỏ" trên thẻ -> nhắc chọn size và mở trang chi tiết @smoke | chromium | ✅ Đạt |  |
| SF-LST-45 | Nút trên thẻ sản phẩm (dữ liệu thật) › Nữ: "Thêm vào giỏ" trên thẻ -> nhắc chọn size và mở trang chi tiết | chromium | ✅ Đạt |  |
| SF-LST-46 | Nút trên thẻ sản phẩm (dữ liệu thật) › Trẻ em: "Thêm vào giỏ" trên thẻ -> nhắc chọn size và mở trang chi tiết | chromium | ✅ Đạt |  |
| SF-LST-47 | Nút trên thẻ sản phẩm (dữ liệu thật) › Giảm giá: "Thêm vào giỏ" trên thẻ -> nhắc chọn size và mở trang chi tiết | chromium | ✅ Đạt |  |
| SF-LST-48 | Nút trên thẻ sản phẩm (dữ liệu thật) › Nam: "Xem chi tiết" trên thẻ mở trang chi tiết | chromium | ✅ Đạt |  |
| SF-LST-49 | Nút trên thẻ sản phẩm (dữ liệu thật) › Nữ: "Xem chi tiết" trên thẻ mở trang chi tiết | chromium | ✅ Đạt |  |
| SF-LST-50 | Nút trên thẻ sản phẩm (dữ liệu thật) › Trẻ em: "Xem chi tiết" trên thẻ mở trang chi tiết | chromium | ✅ Đạt |  |
| SF-LST-51 | Nút trên thẻ sản phẩm (dữ liệu thật) › Giảm giá: "Xem chi tiết" trên thẻ mở trang chi tiết | chromium | ✅ Đạt |  |
| SF-LST-52 | Nút trên thẻ sản phẩm (dữ liệu thật) › Nam: bấm nút yêu thích không rời khỏi trang danh sách | chromium | 🐞 Bug đã biết | BUG: Nút yêu thích nằm trong <Link> và không có onClick -> bấm tim lại mở trang chi tiết, không thêm vào yêu thích |
| SF-LST-53 | Nút trên thẻ sản phẩm (dữ liệu thật) › Nữ: bấm nút yêu thích không rời khỏi trang danh sách | chromium | 🐞 Bug đã biết | BUG: Nút yêu thích nằm trong <Link> và không có onClick -> bấm tim lại mở trang chi tiết, không thêm vào yêu thích |
| SF-LST-54 | Nút trên thẻ sản phẩm (dữ liệu thật) › Trẻ em: bấm nút yêu thích không rời khỏi trang danh sách | chromium | 🐞 Bug đã biết | BUG: Nút yêu thích nằm trong <Link> và không có onClick -> bấm tim lại mở trang chi tiết, không thêm vào yêu thích |
| SF-LST-55 | Nút trên thẻ sản phẩm (dữ liệu thật) › Giảm giá: bấm nút yêu thích không rời khỏi trang danh sách | chromium | 🐞 Bug đã biết | BUG: Nút yêu thích nằm trong <Link> và không có onClick -> bấm tim lại mở trang chi tiết, không thêm vào yêu thích |
| SF-PDP-01 | Breadcrumb "Trang chủ \| tên sản phẩm" quay về trang chủ @smoke | chromium | ✅ Đạt |  |
| SF-PDP-02 | Bộ ảnh: thumbnail và bộ đếm ảnh | chromium | ✅ Đạt |  |
| SF-PDP-03 | Nút ảnh tiếp theo chuyển tới ảnh cuối rồi ẩn đi | chromium | ✅ Đạt |  |
| SF-PDP-04 | Chọn màu đổi tên màu đang chọn | chromium | ✅ Đạt |  |
| SF-PDP-06 | Có giá gốc gạch ngang và nhãn phần trăm giảm | chromium | ✅ Đạt |  |
| SF-PDP-07 | Giá bán và giá gốc hiển thị đúng định dạng "449.000đ" | chromium | 🐞 Bug đã biết | BUG: ProductDetailPage.jsx:449,453 formatPrice() đã thêm "đ" rồi JSX thêm " đ" -> hiển thị "449.000đ đ" |
| SF-PDP-08 | Accordion: mặc định mở "Mô tả", chỉ mở 1 mục mỗi lúc, bấm lại thì đóng | chromium | ✅ Đạt |  |
| SF-PDP-09 | Danh sách dịch vụ: COD, miễn phí giao hàng, đổi hàng 30 ngày | chromium | ✅ Đạt |  |
| SF-PDP-10 | Ngưỡng miễn phí giao hàng khớp chính sách (500.000đ như /shipping và giỏ hàng) | chromium | 🐞 Bug đã biết | BUG: ProductDetailPage.jsx:109 ghi "trên 599.000 đ" trong khi ShippingPage.jsx:91, CartPage.jsx:51 và cài đặt backend dùng 500.000đ |
| SF-PDP-11 | "SẢN PHẨM CÙNG PHONG CÁCH" mở trang chi tiết sản phẩm liên quan | chromium | ✅ Đạt |  |
| SF-PDP-12 | Khách chưa đăng nhập chỉ thấy lời nhắc đăng nhập để đánh giá | chromium | ✅ Đạt |  |
| SF-PDP-05 | Quyền clipboard › Copy SKU -> "Đã copy", clipboard chứa SKU, 2 giây sau trở lại "Copy" | chromium | ✅ Đạt |  |
| SF-PDP-13 | Đánh giá: bỏ trống sao và nội dung -> 2 lỗi | chromium | ✅ Đạt |  |
| SF-PDP-14 | Đánh giá: nội dung 3 ký tự -> tối thiểu 5 ký tự | chromium | ✅ Đạt |  |
| SF-PDP-15 | Đánh giá: có nội dung nhưng chưa chọn sao | chromium | ✅ Đạt |  |
| SF-PDP-16 | Đánh giá: nội dung toàn khoảng trắng bị coi là trống | chromium | ✅ Đạt |  |
| SF-PDP-17 | Gửi đánh giá hợp lệ (mock API) -> toast từ server, form đóng @smoke | chromium | ✅ Đạt |  |
| SF-PDP-18 | Server 403 (chưa mua hàng) -> hiển thị thông báo của server | chromium | 🐞 Bug đã biết | BUG: ProductDetailPage.jsx:283 catch luôn hiện "Không thể gửi đánh giá. Vui lòng thử lại.", bỏ qua message của server |
| SF-PDP-19 | Server 409 (đã đánh giá) -> hiển thị thông báo của server | chromium | 🐞 Bug đã biết | BUG: ProductDetailPage.jsx:283 catch luôn hiện thông báo chung, bỏ qua message của server |
| SF-PDP-20 | Nội dung 9 ký tự qua được form (>=5) nhưng server đòi >=10 -> hiển thị thông báo của server | chromium | 🐞 Bug đã biết | BUG: ProductDetailPage.jsx:255 cho phép >=5 ký tự nhưng customerController.js:890 yêu cầu >=10; và :283 nuốt message server |
| SF-PDP-21 | Server 500 -> thông báo chung "Không thể gửi đánh giá" | chromium | ✅ Đạt |  |
| SF-PDP-22 | Bấm "Hủy" đóng form đánh giá, không gửi request | chromium | ✅ Đạt |  |
| SF-PDP-23 | Bấm "×" đóng form và xóa thông báo lỗi | chromium | ✅ Đạt |  |
| SF-SRCH-14 | Gõ 1 ký tự: API gợi ý trả 400 nên không hiện dropdown, Enter vẫn ra trang kết quả có sản phẩm | chromium | ✅ Đạt |  |
| SF-SRCH-01 | Tiêu đề, breadcrumb, chip theo tham số (dữ liệu thật) › ?q= : tiêu đề "Kết quả tìm kiếm", breadcrumb Tìm kiếm, chip Tìm @smoke | chromium | ✅ Đạt |  |
| SF-SRCH-02 | Tiêu đề, breadcrumb, chip theo tham số (dữ liệu thật) › Không tham số: "Tất cả sản phẩm", breadcrumb Sản phẩm | chromium | ✅ Đạt |  |
| SF-SRCH-03 | Tiêu đề, breadcrumb, chip theo tham số (dữ liệu thật) › ?category= : tiêu đề từ slug, breadcrumb Sản phẩm > Vay, chip Danh mục | chromium | ✅ Đạt |  |
| SF-SRCH-04 | Tiêu đề, breadcrumb, chip theo tham số (dữ liệu thật) › ?brand= : tiêu đề từ slug, breadcrumb Thương hiệu > Canifa, chip Thương hiệu | chromium | ✅ Đạt |  |
| SF-SRCH-05 | Tiêu đề, breadcrumb, chip theo tham số (dữ liệu thật) › ?category= + ?q= : ưu tiên tiêu đề danh mục, chip Tìm đóng về lại danh mục | chromium | ✅ Đạt |  |
| SF-SRCH-06 | Tiêu đề, breadcrumb, chip theo tham số (dữ liệu thật) › Bỏ chip Danh mục quay về "Tất cả sản phẩm" | chromium | ✅ Đạt |  |
| SF-SRCH-07 | Sắp xếp theo giá (dữ liệu thật) › Sắp xếp "Giá: Thấp → Cao" (dữ liệu thật) | chromium | ✅ Đạt |  |
| SF-SRCH-08 | Sắp xếp theo giá (dữ liệu thật) › Sắp xếp "Giá: Cao → Thấp" theo thương hiệu (dữ liệu thật) | chromium | ✅ Đạt |  |
| SF-SRCH-09 | Không có kết quả / lỗi › Từ khóa không có kết quả: gợi ý đổi từ khóa + nút xem tất cả | chromium | ✅ Đạt |  |
| SF-SRCH-10 | Không có kết quả / lỗi › Danh mục không có sản phẩm: thông báo danh mục trống | chromium | ✅ Đạt |  |
| SF-SRCH-11 | Không có kết quả / lỗi › API lỗi 500: hiển thị "Đã xảy ra lỗi" và nút Thử lại (mock) | chromium | ✅ Đạt |  |
| SF-SRCH-12 | Phân trang (mock) › Phân trang: bấm trang 2 gửi page=2 (mock 4 trang) | chromium | ✅ Đạt |  |
| SF-SRCH-13 | Phân trang (mock) › Phân trang: bấm "chevron_right" sang trang 2 (mock 4 trang) | chromium | ✅ Đạt |  |
| SF-STAT-01 | Giới thiệu (/about): tiêu đề, câu chuyện, giá trị, số liệu @smoke | chromium | ✅ Đạt |  |
| SF-STAT-02 | Giao hàng (/shipping): hình thức giao hàng, miễn phí từ 500.000đ, câu hỏi thường gặp | chromium | ✅ Đạt |  |
| SF-STAT-03 | Đổi trả (/returns): quy định, sản phẩm không áp dụng, quy trình 4 bước | chromium | ✅ Đạt |  |
| SF-STAT-04 | Bảo mật (/privacy): 5 mục chính sách và thông tin liên hệ | chromium | ✅ Đạt |  |
| SF-STAT-05 | Đổi trả: nội dung không lẫn ký tự Cyrillic | chromium | 🐞 Bug đã biết | BUG: ReturnsPage.jsx:21 "không có запаh hư" chứa chữ Nga (Cyrillic) trong câu tiếng Việt |
| SF-STAT-06 | Giao hàng: phí "Giao hàng nhanh" khớp phí tính ở checkout (30.000đ) | chromium | 🐞 Bug đã biết | BUG: ShippingPage.jsx:11 ghi 35.000đ nhưng CheckoutPage.jsx:72 tính 30.000đ cho giao hàng nhanh (tiêu chuẩn miễn phí, trang ghi 25.000đ) |
| SF-STAT-07 | Đường dẫn không tồn tại hiển thị trang 404 | chromium | 🐞 Bug đã biết | BUG: App.jsx:75-129 không có <Route path="*"> -> trang trắng, không header/footer |
| SF-STAT-08 | /products (link "Xem tất cả" ở trang chủ) hiển thị trang 404 hoặc danh sách | chromium | 🐞 Bug đã biết | BUG: App.jsx:75-129 không có route /products và không có route "*" -> trang trắng |
| SF-STAT-09 | /collections/doraemon (nút bộ sưu tập) hiển thị trang 404 hoặc bộ sưu tập | chromium | 🐞 Bug đã biết | BUG: App.jsx:75-129 không có route /collections/:slug và không có route "*" -> trang trắng |

## UI - Mobile

| ID | Test case | Project | Kết quả | Ghi chú |
|---|---|---|---|---|
| MOB-M-01 | Trang chủ hiển thị, menu desktop bị ẩn | mobile | ✅ Đạt |  |
| MOB-M-02 | Mở menu mobile và điều hướng tới danh mục | mobile | 🐞 Bug đã biết | BUG: header tràn ngang trên mobile, nút menu nằm ngoài màn hình |
| MOB-M-03 | Không bị tràn ngang trên trang chủ | mobile | 🐞 Bug đã biết | BUG: ô tìm kiếm w-48 cố định làm header rộng hơn màn hình (~64px) |

## API - Quản trị

| ID | Test case | Project | Kết quả | Ghi chú |
|---|---|---|---|---|
| API-ADM-R01 | Danh sách / thống kê (data-driven) › Dashboard - GET /admin/dashboard | api | ✅ Đạt |  |
| API-ADM-R02 | Danh sách / thống kê (data-driven) › Thông báo - GET /admin/notifications | api | ✅ Đạt |  |
| API-ADM-R03 | Danh sách / thống kê (data-driven) › Danh sách sản phẩm - GET /admin/products?limit=5 | api | ✅ Đạt |  |
| API-ADM-R04 | Danh sách / thống kê (data-driven) › Danh sách size - GET /admin/sizes | api | ✅ Đạt |  |
| API-ADM-R05 | Danh sách / thống kê (data-driven) › Danh sách màu - GET /admin/colors | api | ✅ Đạt |  |
| API-ADM-R06 | Danh sách / thống kê (data-driven) › Tùy chọn sản phẩm - GET /admin/products/options | api | ✅ Đạt |  |
| API-ADM-R07 | Danh sách / thống kê (data-driven) › Danh mục - GET /admin/categories | api | ✅ Đạt |  |
| API-ADM-R08 | Danh sách / thống kê (data-driven) › Thương hiệu - GET /admin/brands | api | ✅ Đạt |  |
| API-ADM-R09 | Danh sách / thống kê (data-driven) › Thống kê đơn hàng - GET /admin/orders/stats | api | ✅ Đạt |  |
| API-ADM-R10 | Danh sách / thống kê (data-driven) › Danh sách đơn hàng - GET /admin/orders?limit=5 | api | ✅ Đạt |  |
| API-ADM-R11 | Danh sách / thống kê (data-driven) › Khách hàng - GET /admin/customers?limit=5 | api | ✅ Đạt |  |
| API-ADM-R12 | Danh sách / thống kê (data-driven) › Nhân viên - GET /admin/employees | api | ✅ Đạt |  |
| API-ADM-R13 | Danh sách / thống kê (data-driven) › Khuyến mãi - GET /admin/promotions | api | ✅ Đạt |  |
| API-ADM-R14 | Danh sách / thống kê (data-driven) › Mã giảm giá - GET /admin/coupons | api | ✅ Đạt |  |
| API-ADM-R15 | Danh sách / thống kê (data-driven) › Kho hàng - GET /admin/warehouse?limit=5 | api | ✅ Đạt |  |
| API-ADM-R16 | Danh sách / thống kê (data-driven) › Nhà cung cấp - GET /admin/suppliers | api | ✅ Đạt |  |
| API-ADM-R17 | Danh sách / thống kê (data-driven) › Danh sách kho - GET /admin/warehouses | api | ✅ Đạt |  |
| API-ADM-R18 | Danh sách / thống kê (data-driven) › Phiếu nhập - GET /admin/imports | api | ✅ Đạt |  |
| API-ADM-R19 | Danh sách / thống kê (data-driven) › Đơn đặt nhà cung cấp - GET /admin/supplier-orders | api | ✅ Đạt |  |
| API-ADM-R20 | Danh sách / thống kê (data-driven) › Đánh giá - GET /admin/reviews?limit=5 | api | ✅ Đạt |  |
| API-ADM-R21 | Danh sách / thống kê (data-driven) › Bài viết (blogs) - GET /admin/blogs | api | ✅ Đạt |  |
| API-ADM-R22 | Danh sách / thống kê (data-driven) › Bài viết (news) - GET /admin/news | api | ✅ Đạt |  |
| API-ADM-R23 | Danh sách / thống kê (data-driven) › Liên hệ - GET /admin/contacts | api | ✅ Đạt |  |
| API-ADM-R24 | Danh sách / thống kê (data-driven) › Báo cáo tổng quan - GET /admin/reports/overview | api | ✅ Đạt |  |
| API-ADM-R25 | Danh sách / thống kê (data-driven) › Báo cáo doanh thu - GET /admin/reports/revenue | api | ✅ Đạt |  |
| API-ADM-R26 | Danh sách / thống kê (data-driven) › Báo cáo đơn hàng - GET /admin/reports/orders | api | ✅ Đạt |  |
| API-ADM-R27 | Danh sách / thống kê (data-driven) › Báo cáo sản phẩm - GET /admin/reports/products | api | ✅ Đạt |  |
| API-ADM-R28 | Danh sách / thống kê (data-driven) › Báo cáo khách hàng - GET /admin/reports/customers | api | ✅ Đạt |  |
| API-ADM-R29 | Danh sách / thống kê (data-driven) › Cài đặt - GET /admin/settings | api | ✅ Đạt |  |
| API-ADM-R30 | Danh sách / thống kê (data-driven) › Hồ sơ admin - GET /admin/profile | api | ✅ Đạt |  |
| API-ADM-D01 | Chi tiết theo id (data-driven) › Chi tiết sản phẩm | api | ✅ Đạt |  |
| API-ADM-D02 | Chi tiết theo id (data-driven) › Chi tiết khách hàng | api | ✅ Đạt |  |
| API-ADM-D03 | Chi tiết theo id (data-driven) › Chi tiết khuyến mãi | api | ✅ Đạt |  |
| API-ADM-D04 | Chi tiết theo id (data-driven) › Chi tiết bài viết | api | ✅ Đạt |  |
| API-ADM-D05 | Chi tiết theo id (data-driven) › Chi tiết đơn hàng | api | ⏭️ Bỏ qua | Chưa có dữ liệu orders để kiểm tra |
| API-ADM-N01 | Id không tồn tại (data-driven) › Sản phẩm không tồn tại - GET /admin/products/99999999 | api | ✅ Đạt |  |
| API-ADM-N02 | Id không tồn tại (data-driven) › Khách hàng không tồn tại - GET /admin/customers/99999999 | api | ✅ Đạt |  |
| API-ADM-N03 | Id không tồn tại (data-driven) › Khuyến mãi không tồn tại - GET /admin/promotions/99999999 | api | ✅ Đạt |  |
| API-ADM-N04 | Id không tồn tại (data-driven) › Bài viết không tồn tại - GET /admin/blogs/99999999 | api | ✅ Đạt |  |
| API-ADM-N05 | Id không tồn tại (data-driven) › Đơn hàng không tồn tại - GET /admin/orders/99999999 | api | ✅ Đạt |  |
| API-ADM-N06 | Id không tồn tại (data-driven) › Đánh giá không tồn tại - GET /admin/reviews/99999999 | api | ✅ Đạt |  |
| API-ADM-N07 | Id không tồn tại (data-driven) › Liên hệ không tồn tại - GET /admin/contacts/99999999 | api | ✅ Đạt |  |
| API-ADM-N08 | Id không tồn tại (data-driven) › Id không phải số - GET /admin/products/abc | api | 🐞 Bug đã biết | BUG: Backend không validate id, trả 500 thay vì 400/404 |
| API-QT-01 | POST /admin/upload không có token phải trả 401 | api | ❌ Lỗi | Error: Endpoint upload xử lý request không cần đăng nhập |

## API - Xác thực & Bảo mật

| ID | Test case | Project | Kết quả | Ghi chú |
|---|---|---|---|---|
| API-XTBM-01 | Đăng nhập thiếu thông tin trả 400 | api | ✅ Đạt |  |
| API-XTBM-02 | Đăng nhập sai mật khẩu trả 401 | api | ✅ Đạt |  |
| API-XTBM-03 | Đăng ký thiếu trường bắt buộc trả 400 | api | ✅ Đạt |  |
| API-XTBM-04 | Đăng ký email sai định dạng trả 400 | api | ✅ Đạt |  |
| API-XTBM-05 | Đăng ký thành công rồi đăng ký trùng email trả 409 | api | ⏭️ Bỏ qua | Cần E2E_ALLOW_WRITE=1 (ghi dữ liệu thật) |
| API-XTBM-06 | GET /profile không có token trả 401 | api | ✅ Đạt |  |
| API-XTBM-07 | GET /orders không có token trả 401 | api | ✅ Đạt |  |
| API-XTBM-08 | GET /wishlist không có token trả 401 | api | ✅ Đạt |  |
| API-XTBM-09 | GET /addresses không có token trả 401 | api | ✅ Đạt |  |
| API-XTBM-10 | GET /admin/dashboard không có token trả 401 | api | ✅ Đạt |  |
| API-XTBM-11 | GET /admin/products không có token trả 401 | api | ✅ Đạt |  |
| API-XTBM-12 | GET /admin/orders không có token trả 401 | api | ✅ Đạt |  |
| API-XTBM-13 | GET /admin/customers không có token trả 401 | api | ✅ Đạt |  |
| API-XTBM-14 | GET /admin/employees không có token trả 401 | api | ✅ Đạt |  |
| API-XTBM-15 | GET /admin/settings không có token trả 401 | api | ✅ Đạt |  |
| API-XTBM-16 | GET /admin/reports/overview không có token trả 401 | api | ✅ Đạt |  |
| API-XTBM-17 | GET /admin/coupons không có token trả 401 | api | ✅ Đạt |  |
| API-XTBM-18 | Token khách hàng không truy cập được API admin | api | ✅ Đạt |  |
| API-XTBM-19 | Token giả mạo bị từ chối | api | ✅ Đạt |  |
| API-XTBM-20 | Sai mật khẩu trả 401 | api | ✅ Đạt |  |
| API-XTBM-21 | Không được đăng nhập admin bằng mật khẩu cứng "admin123" | api | ❌ Lỗi | Error: Backend chấp nhận mật khẩu cứng - lỗ hổng bảo mật |
| API-XTBM-22 | Không được đăng nhập admin bằng mật khẩu cứng "manager123" | api | ❌ Lỗi | Error: Backend chấp nhận mật khẩu cứng - lỗ hổng bảo mật |
| API-XTBM-23 | Không được đăng nhập admin bằng mật khẩu cứng "staff123" | api | ❌ Lỗi | Error: Backend chấp nhận mật khẩu cứng - lỗ hổng bảo mật |

## API - Health & Home

| ID | Test case | Project | Kết quả | Ghi chú |
|---|---|---|---|---|
| API-HH-01 | GET /health trả về 200 | api | ✅ Đạt |  |
| API-HH-02 | GET /home trả đủ các khối dữ liệu trang chủ | api | ✅ Đạt |  |
| API-HH-03 | Route không tồn tại trả 404 | api | ✅ Đạt |  |

## API - Sản phẩm

| ID | Test case | Project | Kết quả | Ghi chú |
|---|---|---|---|---|
| API-SP-01 | GET /products trả danh sách + phân trang | api | ✅ Đạt |  |
| API-SP-02 | GET /products/:slug trả chi tiết có sizes/colors/variants | api | ✅ Đạt |  |
| API-SP-03 | GET /products/:slug không tồn tại trả 404 | api | ✅ Đạt |  |
| API-SP-04 | GET /products/search tìm theo từ khóa | api | ✅ Đạt |  |
| API-SP-05 | GET /products/kids, /kids-categories hoạt động | api | ✅ Đạt |  |
| API-SP-06 | GET /products/suggested (gợi ý trong giỏ hàng) trả 200 | api | 🐞 Bug đã biết | BUG: query dùng hàm HEX() của MySQL trên Postgres -> 500 "function hex(character varying) does not exist" |
| API-SP-07 | GET /news trả danh sách bài viết đã publish | api | ✅ Đạt |  |

## API - Lọc/Sắp xếp/Validate

| ID | Test case | Project | Kết quả | Ghi chú |
|---|---|---|---|---|
| API-PUB-S01 | Sắp xếp giá tăng dần | api | ✅ Đạt |  |
| API-PUB-S02 | Sắp xếp giá giảm dần | api | ✅ Đạt |  |
| API-PUB-F01 | Lọc theo giới tính nam | api | ✅ Đạt |  |
| API-PUB-F02 | Lọc theo giới tính nữ | api | ✅ Đạt |  |
| API-PUB-F03 | Lọc theo danh mục tshirt | api | ✅ Đạt |  |
| API-PUB-P01 | Duyệt hết các trang: đủ sản phẩm, không trùng | api | 🐞 Bug đã biết | BUG: ORDER BY created_at không có cột phụ (id) -> sản phẩm trùng/thiếu giữa các trang |
| API-PUB-V01 | Tìm kiếm từ khóa rỗng | api | ✅ Đạt |  |
| API-PUB-V02 | Tìm kiếm từ khóa 1 ký tự | api | ✅ Đạt |  |
| API-PUB-V03 | Bài viết không tồn tại | api | ✅ Đạt |  |
| API-PUB-V04 | Trang âm (page=-1) phải báo lỗi tham số | api | 🐞 Bug đã biết | BUG: Backend không validate page, trả 500 'Không thể tải danh sách sản phẩm' |

