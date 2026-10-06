# THƯ VIỆN KEYWORD - NHÓM adminMarketing: quản trị marketing/nội dung: khuyến mãi, mã giảm giá,
# đánh giá, bài viết, liên hệ.
import json
import re
from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse

from playwright.sync_api import expect

from keywords.base_keywords import BaseKeywords, keyword
from pages.admin.marketing.admin_table import AdminTable
from pages.admin.marketing.blog_page import BlogPage
from pages.admin.marketing.contacts_page import ContactsPage
from pages.admin.marketing.coupons_page import CouponsPage
from pages.admin.marketing.promotions_page import PromotionsPage
from pages.admin.marketing.reviews_page import ReviewsPage
from pages.admin.sales.admin_api_mock import query_of_url
from utils.assertions import poll_until


def vn_date(offset=0):
    """Ngày YYYY-MM-DD theo giờ Việt Nam (UTC+7), lệch `offset` ngày so với hôm nay."""
    return (datetime.now(timezone.utc) + timedelta(hours=7, days=offset)).strftime("%Y-%m-%d")


def _json(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def _to_number(text):
    try:
        return float(text)
    except (TypeError, ValueError):
        return None


class AdminMarketingKeywords(BaseKeywords):
    """Quản trị marketing/nội dung: khuyến mãi, mã giảm giá, đánh giá, bài viết, liên hệ."""

    group = "adminMarketing"

    def __init__(self, page, po, api, common=None):
        super().__init__(page, po, api, common)
        self._table = AdminTable(page)
        self._promotions = PromotionsPage(page)
        self._coupons = CouponsPage(page)
        self._reviews = ReviewsPage(page)
        self._blog = BlogPage(page)
        self._contacts = ContactsPage(page)
        # URL các request GET danh sách đã đi qua API giả lập (để kiểm tra tham số lọc).
        self._list_queries = []

    def _fake_list(self, url_glob, to_json, items, item_filter=None):
        """Giả lập API GET danh sách: lọc dữ liệu mẫu theo query string và ghi lại URL đã gọi."""

        def handle(route):
            request = route.request
            if request.method != "GET":
                return route.fallback()
            self._list_queries.append(request.url)
            query = query_of_url(request.url)
            result = [i for i in items if item_filter(i, query)] if item_filter else items
            route.fulfill(status=200, json=to_json(result))

        self.page.route(url_glob, handle)

    # ---------------------------------------------------------------------------
    # Dùng chung cho các trang marketing
    # ---------------------------------------------------------------------------

    @keyword("verifyColumns")
    def verify_columns(self, headers):
        """Kiểm tra bảng chính có đúng các cột theo thứ tự (đọc textContent, bỏ qua CSS viết hoa)."""
        with self.step(f"Kiểm tra cột: {' | '.join(headers)}"):
            expect(self._table.header_cells.first).to_be_visible()
            actual = self._table.header_texts()
            assert actual == list(headers), f"Cột bảng: expected={list(headers)!r}, actual={actual!r}"

    @keyword("verifyRowCells")
    def verify_row_cells(self, row_text, cells):
        """Kiểm tra các ô của dòng chứa text theo tên cột, vd: {"Trạng thái": "Hết hạn"}."""
        with self.step(f'Kiểm tra dòng "{row_text}": {_json(cells)}'):
            expect(self._table.row(row_text)).to_be_visible()
            for header, value in cells.items():
                cell = self._table.cell(row_text, header)
                if value == "":
                    expect(cell).to_have_text("")
                else:
                    expect(cell).to_contain_text(value)

    @keyword("verifyCellPattern")
    def verify_cell_pattern(self, row_index, column, pattern):
        """Kiểm tra ô ở cột `column` của dòng thứ `rowIndex` (0 = đầu) khớp biểu thức chính quy."""
        with self.step(f'Kiểm tra dòng #{row_index + 1}, cột "{column}" khớp /{pattern}/'):
            expect(self._table.rows.nth(row_index)).to_be_visible()
            expect(self._table.cell_at(row_index, column)).to_have_text(re.compile(pattern))

    @keyword("verifySelectedOption")
    def verify_selected_option(self, label, text):
        """Kiểm tra chữ hiển thị của option đang chọn trong select (theo label của ô)."""
        with self.step(f'Kiểm tra "{label}" đang chọn "{text}"'):
            select = self.po.admin_ui.field(label)

            def selected():
                return select.evaluate("(s) => s.selectedOptions[0]?.textContent?.trim()")

            try:
                poll_until(lambda: selected() == text, "")
            except AssertionError:
                raise AssertionError(
                    f'"{label}": expected={text!r}, actual={selected()!r}'
                ) from None

    @keyword("verifyRowCount")
    def verify_row_count(self, count):
        """Kiểm tra số dòng dữ liệu đang hiển thị trong bảng chính."""
        with self.step(f"Kiểm tra bảng có {count} dòng"):
            expect(self._table.rows).to_have_count(count)

    @keyword("verifyRowsAtLeast")
    def verify_rows_at_least(self, min_count):
        """Kiểm tra bảng có ít nhất `min` dòng dữ liệu thật (không phải dòng trạng thái rỗng)."""
        with self.step(f"Kiểm tra bảng có ít nhất {min_count} dòng"):
            expect(self._table.rows.first).to_be_visible()
            expect(self._table.rows.locator("td[colspan]")).to_have_count(0)
            actual = self._table.rows.count()
            assert actual >= min_count, f"Số dòng: expected>={min_count}, actual={actual}"

    @keyword("verifyRowActions")
    def verify_row_actions(self, row_text, titles):
        """Kiểm tra dòng chứa text có đúng các nút hành động (theo title, đúng thứ tự)."""
        with self.step(f'Kiểm tra nút trên dòng "{row_text}": {", ".join(titles)}'):
            buttons = self._table.titled_buttons(row_text)
            expect(buttons).to_have_count(len(titles))
            actual = buttons.evaluate_all("(els) => els.map((e) => e.getAttribute('title'))")
            assert actual == list(titles), f"Nút trên dòng: expected={list(titles)!r}, actual={actual!r}"

    @keyword("verifyVisibleRows")
    def verify_visible_rows(self, visible, hidden=None):
        """Kiểm tra các dòng hiển thị/không hiển thị sau khi tìm kiếm hoặc lọc."""
        hidden = hidden or []
        with self.step(f"Kiểm tra hiển thị [{', '.join(visible)}], ẩn [{', '.join(hidden)}]"):
            for text in visible:
                expect(self._table.ui.row(text).first).to_be_visible()
            for text in hidden:
                expect(self._table.ui.row(text)).to_have_count(0)

    @keyword("verifyModalText")
    def verify_modal_text(self, heading, texts):
        """Kiểm tra modal có tiêu đề `heading` đang mở và chứa các đoạn text."""
        with self.step(f'Kiểm tra modal "{heading}" chứa: {" | ".join(texts)}'):
            modal = self._table.modal(heading)
            expect(modal).to_be_visible()
            for text in texts:
                expect(modal).to_contain_text(text)

    @keyword("clickModalButton")
    def click_modal_button(self, heading, name):
        """Bấm nút theo tên bên trong modal có tiêu đề `heading`."""
        with self.step(f'Modal "{heading}" -> bấm "{name}"'):
            self._table.modal_button(heading, name).click()

    @keyword("verifyListQuery")
    def verify_list_query(self, path_part, params):
        """Kiểm tra request GET danh sách gần nhất (qua API giả lập) có các tham số; null = không gửi tham số đó."""
        with self.step(f"Kiểm tra GET {path_part} có {_json(params)}"):

            def actual():
                last = next(
                    (u for u in reversed(self._list_queries) if path_part in urlparse(u).path),
                    None,
                )
                if last is None:
                    return "chưa có request"
                query = query_of_url(last)
                return {key: query.get(key) for key in params}

            try:
                poll_until(lambda: actual() == params, "")
            except AssertionError:
                raise AssertionError(
                    f"GET {path_part}: expected={params!r}, actual={actual()!r}"
                ) from None

    # ---------------------------------------------------------------------------
    # Khuyến mãi
    # ---------------------------------------------------------------------------

    @keyword("mockPromotionList")
    def mock_promotion_list(self, promotions):
        """Giả lập danh sách + chi tiết khuyến mãi; startOffset/endOffset đổi thành ngày so với hôm nay."""
        with self.step(f"Mock danh sách {len(promotions)} khuyến mãi"):
            promotion_list = []
            for promotion in promotions:
                p = {k: v for k, v in promotion.items() if k not in ("startOffset", "endOffset")}
                start, end = promotion.get("startOffset"), promotion.get("endOffset")
                promotion_list.append(
                    {
                        **p,
                        "name": p.get("title"),
                        "start_date": (p.get("start_date") or "") if start is None else vn_date(start),
                        "end_date": (p.get("end_date") or "") if end is None else vn_date(end),
                    }
                )
            self._fake_list(
                "**/api/admin/promotions",
                lambda items: {"success": True, "promotions": items},
                promotion_list,
            )

            def detail(route):
                if route.request.method != "GET":
                    return route.fallback()
                promotion_id = _to_number(urlparse(route.request.url).path.split("/")[-1])
                found = next((p for p in promotion_list if p.get("id") == promotion_id), None)
                if found:
                    route.fulfill(json={"success": True, "promotion": found})
                else:
                    route.fulfill(status=404, json={"success": False})

            self.page.route("**/api/admin/promotions/*", detail)

    @keyword("openPromotions")
    def open_promotions(self):
        """Mở trang Khuyến mãi và chờ danh sách tải xong."""
        with self.step("Mở trang Khuyến mãi"):
            self.page.goto(self._promotions.path)
            expect(self.po.admin_ui.page_title).to_have_text("Khuyến mãi")
            expect(self._promotions.list_heading).to_be_visible()
            expect(self._promotions.list_ready).to_be_visible()

    @keyword("openCreatePromotion")
    def open_create_promotion(self):
        """Bấm "Thêm khuyến mãi" và chờ modal tạo mới."""
        with self.step('Mở form "Thêm khuyến mãi"'):
            self._promotions.add_button.click()
            expect(self._promotions.modal("Thêm khuyến mãi")).to_be_visible()

    # ---------------------------------------------------------------------------
    # Mã giảm giá
    # ---------------------------------------------------------------------------

    @keyword("mockCouponList")
    def mock_coupon_list(self, coupons):
        """Giả lập API GET danh sách mã giảm giá."""
        with self.step(f"Mock danh sách {len(coupons)} mã giảm giá"):
            self._fake_list("**/api/admin/coupons", lambda items: {"coupons": items}, coupons)

    @keyword("openCoupons")
    def open_coupons(self):
        """Mở trang Mã giảm giá và chờ danh sách tải xong."""
        with self.step("Mở trang Mã giảm giá"):
            self.page.goto(self._coupons.path)
            expect(self.po.admin_ui.page_title).to_have_text("Mã giảm giá")
            expect(self._coupons.list_ready).to_be_visible()

    @keyword("openCreateCoupon")
    def open_create_coupon(self):
        """Bấm "Thêm mã" và chờ modal "Thêm mã giảm giá"."""
        with self.step('Mở form "Thêm mã giảm giá"'):
            self._coupons.add_button.click()
            expect(self._coupons.modal("Thêm mã giảm giá")).to_be_visible()

    @keyword("clickCouponEdit")
    def click_coupon_edit(self, code):
        """Bấm nút sửa (icon không tên) trên dòng mã giảm giá."""
        with self.step(f'Sửa mã giảm giá "{code}"'):
            self._coupons.edit_button(code).click()
            expect(self._coupons.modal("Sửa mã giảm giá")).to_be_visible()

    @keyword("clickCouponDelete")
    def click_coupon_delete(self, code):
        """Bấm nút xóa (icon không tên) trên dòng mã giảm giá."""
        with self.step(f'Xóa mã giảm giá "{code}"'):
            self._coupons.delete_button(code).click()
            expect(self._coupons.modal("Xác nhận xóa")).to_be_visible()

    @keyword("toggleCoupon")
    def toggle_coupon(self, code, column):
        """Bấm nút bật/tắt ở cột "Công khai" hoặc "Trạng thái" của mã giảm giá."""
        with self.step(f'Bật/tắt "{column}" của mã "{code}"'):
            self._coupons.toggle_button(code, column).click()

    @keyword("verifyCouponToggle")
    def verify_coupon_toggle(self, code, column, on):
        """Kiểm tra nút bật/tắt ở cột của mã giảm giá đang bật (xanh) hay tắt (xám)."""
        with self.step(f"Kiểm tra \"{column}\" của mã \"{code}\" đang {'bật' if on else 'tắt'}"):
            button = self._coupons.toggle_button(code, column)
            expect(button).to_have_class(re.compile(r"text-green-500" if on else r"text-gray-300"))

    # ---------------------------------------------------------------------------
    # Đánh giá
    # ---------------------------------------------------------------------------

    @keyword("mockReviewList")
    def mock_review_list(self, reviews):
        """Giả lập API GET đánh giá: lọc theo tham số status/rating như server."""
        with self.step(f"Mock danh sách {len(reviews)} đánh giá"):
            self._fake_list(
                "**/api/admin/reviews*",
                lambda items: {
                    "success": True,
                    "reviews": items,
                    "total": len(items),
                    "totalPages": 1,
                    "page": 1,
                },
                reviews,
                lambda r, q: (not q.get("status") or r.get("status") == q.get("status"))
                and (not q.get("rating") or r.get("rating") == _to_number(q.get("rating"))),
            )

    @keyword("openReviews")
    def open_reviews(self):
        """Mở trang Đánh giá và chờ danh sách tải xong."""
        with self.step("Mở trang Đánh giá"):
            self.page.goto(self._reviews.path)
            expect(self.po.admin_ui.page_title).to_have_text("Đánh giá")
            expect(self._reviews.page_heading).to_have_text("Đánh giá")
            expect(self._reviews.list_ready).to_be_visible()

    @keyword("filterReviewStatus")
    def filter_review_status(self, value):
        """Chọn bộ lọc trạng thái đánh giá (all, pending, approved, hidden)."""
        with self.step(f'Lọc đánh giá theo trạng thái "{value}"'):
            self._reviews.status_select.select_option(value)
            expect(self._reviews.list_ready).to_be_visible()

    @keyword("filterReviewRating")
    def filter_review_rating(self, value):
        """Chọn bộ lọc số sao (all, 5, 4, 3, 2, 1)."""
        with self.step(f'Lọc đánh giá theo số sao "{value}"'):
            self._reviews.rating_select.select_option(value)
            expect(self._reviews.list_ready).to_be_visible()

    # ---------------------------------------------------------------------------
    # Bài viết
    # ---------------------------------------------------------------------------

    @keyword("mockBlogList")
    def mock_blog_list(self, posts):
        """Giả lập API GET danh sách bài viết."""
        with self.step(f"Mock danh sách {len(posts)} bài viết"):
            self._fake_list(
                "**/api/admin/blogs",
                lambda items: {"success": True, "blogs": items, "posts": items},
                posts,
            )

    @keyword("openBlog")
    def open_blog(self):
        """Mở trang Bài viết và chờ danh sách tải xong."""
        with self.step("Mở trang Bài viết"):
            self.page.goto(self._blog.path)
            expect(self.po.admin_ui.page_title).to_have_text("Bài viết")
            expect(self._blog.page_heading).to_have_text("Bài viết")
            expect(self._blog.list_ready).to_be_visible()

    @keyword("openCreateBlog")
    def open_create_blog(self):
        """Bấm "Thêm bài viết" và chờ modal tạo mới."""
        with self.step('Mở form "Thêm bài viết"'):
            self._blog.add_button.click()
            expect(self._blog.modal("Thêm bài viết")).to_be_visible()

    @keyword("setBlogImage")
    def set_blog_image(self, url, error=""):
        """Nhập URL ảnh bài viết và kiểm tra ảnh xem trước hoặc thông báo lỗi ảnh."""
        with self.step(f'Nhập URL ảnh "{url}"'):
            self._blog.image_url_input.fill(url)
            if error:
                expect(self.page.get_by_text(error, exact=True)).to_be_visible()
            else:
                expect(self._blog.image_preview).to_be_visible()

    # ---------------------------------------------------------------------------
    # Liên hệ
    # ---------------------------------------------------------------------------

    @keyword("mockContactList")
    def mock_contact_list(self, contacts):
        """Giả lập API GET liên hệ: lọc theo tham số status như server."""
        with self.step(f"Mock danh sách {len(contacts)} liên hệ"):
            self._fake_list(
                "**/api/admin/contacts*",
                lambda items: {"success": True, "contacts": items},
                contacts,
                lambda c, q: not q.get("status") or c.get("status") == q.get("status"),
            )

    @keyword("openContacts")
    def open_contacts(self):
        """Mở trang Liên hệ và chờ danh sách tải xong."""
        with self.step("Mở trang Liên hệ"):
            self.page.goto(self._contacts.path)
            expect(self.po.admin_ui.page_title).to_have_text("Liên hệ")
            expect(self._contacts.page_heading).to_have_text("Liên hệ")
            expect(self._contacts.list_ready).to_be_visible()

    @keyword("filterContactStatus")
    def filter_contact_status(self, value):
        """Chọn bộ lọc trạng thái liên hệ (all, pending, processed)."""
        with self.step(f'Lọc liên hệ theo trạng thái "{value}"'):
            self._contacts.status_select.select_option(value)
            expect(self._contacts.list_ready).to_be_visible()
