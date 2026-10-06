# THƯ VIỆN KEYWORD - NHÓM account: tài khoản khách hàng - hồ sơ, đổi mật khẩu, đơn hàng, chi tiết đơn,
# yêu thích, sổ địa chỉ, thanh toán khi đã đăng nhập, trang đặt hàng thành công.
# Lưu ý: mở trực tiếp /profile bị crash (bug) -> dùng open_profile_from_menu.
import json
import re

from playwright.sync_api import expect

from keywords.base_keywords import BaseKeywords, keyword
from pages.account.account_sidebar import AccountSidebar
from pages.account.addresses_page import AddressesPage
from pages.account.checkout_account_panel import CheckoutAccountPanel
from pages.account.css_text import escape_regex
from pages.account.order_detail_page import OrderDetailPage
from pages.account.order_success_details import OrderSuccessDetails
from pages.account.password_modal import PasswordModal
from utils.routes import ROUTES
from utils.storage import STORAGE_KEYS, init_script


def _vi_number(number):
    """Giống Number.toLocaleString('vi-VN'): 1234 -> "1.234"."""
    return f"{int(number):,}".replace(",", ".")


class AccountKeywords(BaseKeywords):
    group = "account"

    def __init__(self, page, po, api, common=None):
        super().__init__(page, po, api, common)
        self._password_modal = PasswordModal(page)
        self._sidebar = AccountSidebar(page)
        self._order_detail = OrderDetailPage(page)
        self._addresses = AddressesPage(page)
        self._checkout_account = CheckoutAccountPanel(page)
        self._order_success = OrderSuccessDetails(page)

    # -------------------------------------------------------------------------
    # Điều hướng
    # -------------------------------------------------------------------------

    @keyword("openAccountMenuLink")
    def open_account_menu_link(self, name):
        """Mở menu tài khoản trên header và bấm 1 mục: "Hồ sơ cá nhân" | "Đơn hàng của tôi" | "Yêu thích"."""
        with self.step(f'Menu tài khoản -> "{name}"'):
            link = self.po.header.root.get_by_role("link", name=name)
            # Nút menu là dạng bật/tắt: chỉ bấm khi menu đang đóng
            if not link.is_visible():
                self.po.header.user_menu_button.click()
            link.click()

    @keyword("clickAccountIcon")
    def click_account_icon(self):
        """Bấm icon tài khoản khi chưa đăng nhập (dẫn tới /login)."""
        with self.step("Bấm icon tài khoản"):
            self.po.header.login_link.click()

    @keyword("openProfile")
    def open_profile(self):
        """Mở trực tiếp trang hồ sơ /profile."""
        with self.step("Mở trang hồ sơ"):
            self.po.profile.goto()

    @keyword("verifyProfileLoaded")
    def verify_profile_loaded(self):
        """Kiểm tra trang hồ sơ hiển thị khối "Thông tin tài khoản"."""
        with self.step("Kiểm tra trang hồ sơ"):
            expect(self.po.profile.account_info_heading).to_be_visible()

    @keyword("openOrders")
    def open_orders(self):
        """Mở trực tiếp trang đơn hàng /orders."""
        with self.step("Mở trang đơn hàng"):
            self.po.orders.goto()

    @keyword("verifyOrdersLoaded")
    def verify_orders_loaded(self):
        """Kiểm tra trang đơn hàng tải xong (có ô tìm theo mã đơn)."""
        with self.step("Kiểm tra trang đơn hàng"):
            expect(self.po.orders.search_input).to_be_visible()

    @keyword("verifyWishlistLoaded")
    def verify_wishlist_loaded(self):
        """Kiểm tra trang yêu thích tải xong (có tiêu đề + danh sách hoặc thông báo rỗng)."""
        with self.step("Kiểm tra trang yêu thích"):
            w = self.po.wishlist
            expect(w.heading).to_be_visible()
            expect(w.search_input.or_(w.empty_state)).to_be_visible()

    @keyword("openProfileFromMenu")
    def open_profile_from_menu(self):
        """Vào trang hồ sơ đúng cách người dùng làm: trang chủ -> menu tài khoản -> "Hồ sơ cá nhân" (tránh bug F5 /profile)."""
        with self.step("Vào hồ sơ qua menu tài khoản"):
            self.page.goto(ROUTES["home"])
            self.po.header.user_menu_button.click()
            self.po.header.root.get_by_role("link", name="Hồ sơ cá nhân").click()
            expect(self.page).to_have_url(ROUTES["profile"])
            expect(self.po.profile.account_info_heading).to_be_visible()

    @keyword("openWishlist")
    def open_wishlist(self):
        """Mở trực tiếp trang yêu thích /favorites và chờ tải xong."""
        with self.step("Mở trang yêu thích"):
            self.po.wishlist.goto()
            expect(self.po.wishlist.heading).to_be_visible()

    @keyword("openAddresses")
    def open_addresses(self):
        """Mở trực tiếp trang sổ địa chỉ /addresses và chờ tải xong."""
        with self.step("Mở trang địa chỉ"):
            self.page.goto(ROUTES["addresses"])
            expect(self._addresses.heading).to_be_visible()
            expect(self.page.get_by_text("Đang tải địa chỉ...")).to_be_hidden()

    @keyword("openOrderDetail")
    def open_order_detail(self, id):
        """Mở trực tiếp trang chi tiết đơn /orders/:id."""
        with self.step(f"Mở chi tiết đơn #{id}"):
            self.page.goto(f"{ROUTES['orders']}/{id}")
            expect(self.page.get_by_text("Đang tải thông tin đơn hàng...")).to_be_hidden()

    @keyword("clickSidebarLink")
    def click_sidebar_link(self, label):
        """Bấm 1 link trên sidebar tài khoản, vd: "Đơn hàng của tôi", "Sổ địa chỉ"."""
        with self.step(f'Sidebar tài khoản -> "{label}"'):
            self._sidebar.link(label).click()

    @keyword("logoutFromSidebar")
    def logout_from_sidebar(self):
        """Đăng xuất bằng nút "Đăng xuất" trên sidebar tài khoản."""
        with self.step("Đăng xuất từ sidebar tài khoản"):
            self._sidebar.logout_button.click()

    @keyword("seedStoredUser")
    def seed_stored_user(self, user):
        """Thay thông tin user đang lưu (localStorage) bằng user cho trước - gọi TRƯỚC lần mở trang đầu tiên."""
        with self.step(f'Đặt sẵn user đăng nhập "{user.get("name")}"'):
            self.page.add_init_script(
                init_script(
                    """({ key, value }) => {
                      if (sessionStorage.getItem('__e2e_user_seeded')) return;
                      localStorage.setItem(key, value);
                      sessionStorage.setItem('__e2e_user_seeded', '1');
                    }""",
                    {"key": STORAGE_KEYS["customerUser"], "value": json.dumps(user, ensure_ascii=False)},
                )
            )

    # -------------------------------------------------------------------------
    # Hồ sơ cá nhân
    # -------------------------------------------------------------------------

    @keyword("verifyProfileFields")
    def verify_profile_fields(self, fields):
        """Kiểm tra các trường ở chế độ xem hồ sơ: { "Họ và tên": "...", "Giới tính": "Nữ" }."""
        with self.step(f"Kiểm tra thông tin hồ sơ: {', '.join(fields)}"):
            for label, value in fields.items():
                expect(self.po.profile.field_value(label), f'Trường "{label}"').to_have_text(value)

    @keyword("startEditProfile")
    def start_edit_profile(self):
        """Bấm "Chỉnh sửa" để chuyển hồ sơ sang chế độ sửa."""
        with self.step("Bấm Chỉnh sửa hồ sơ"):
            self.po.profile.edit_button.click()
            expect(self.po.profile.name_input).to_be_visible()

    @keyword("fillProfileForm")
    def fill_profile_form(self, form):
        """Điền form sửa hồ sơ (chỉ các trường có trong dữ liệu); gender: male | female | other."""
        with self.step(f"Điền form hồ sơ: {', '.join(form)}"):
            p = self.po.profile
            if "name" in form:
                p.name_input.fill(form["name"])
            if "phone" in form:
                p.phone_input.fill(form["phone"])
            if "birthDate" in form:
                p.birth_date_input.fill(form["birthDate"])
            if "gender" in form:
                p.gender_select.select_option(form["gender"])

    @keyword("verifyProfileForm")
    def verify_profile_form(self, form):
        """Kiểm tra giá trị đang có trong form sửa hồ sơ."""
        with self.step("Kiểm tra giá trị form hồ sơ"):
            p = self.po.profile
            if "name" in form:
                expect(p.name_input).to_have_value(form["name"])
            if "phone" in form:
                expect(p.phone_input).to_have_value(form["phone"])
            if "birthDate" in form:
                expect(p.birth_date_input).to_have_value(form["birthDate"])
            if "gender" in form:
                expect(p.gender_select).to_have_value(form["gender"])

    @keyword("verifyProfileEmailLocked")
    def verify_profile_email_locked(self, email):
        """Kiểm tra ô Email trong form sửa bị khóa và hiển thị đúng email."""
        with self.step(f"Kiểm tra ô Email bị khóa ({email})"):
            expect(self.po.profile.email_input).to_be_disabled()
            expect(self.po.profile.email_input).to_have_value(email)

    @keyword("saveProfile")
    def save_profile(self):
        """Bấm "Lưu thay đổi" trong form sửa hồ sơ."""
        with self.step("Bấm Lưu thay đổi hồ sơ"):
            self.po.profile.save_button.click()

    @keyword("cancelEditProfile")
    def cancel_edit_profile(self):
        """Bấm "Hủy" để thoát chế độ sửa hồ sơ."""
        with self.step("Bấm Hủy sửa hồ sơ"):
            self.po.profile.cancel_edit_button.click()

    @keyword("verifyProfileEditing")
    def verify_profile_editing(self, editing):
        """Kiểm tra hồ sơ đang ở chế độ sửa (true) hay chế độ xem (false)."""
        with self.step(f"Kiểm tra hồ sơ ở chế độ {'sửa' if editing else 'xem'}"):
            p = self.po.profile
            if editing:
                expect(p.name_input).to_be_visible()
                expect(p.edit_button).to_be_hidden()
            else:
                expect(p.edit_button).to_be_visible()
                expect(p.name_input).to_be_hidden()

    @keyword("openChangePassword")
    def open_change_password(self):
        """Bấm "Đổi mật khẩu" và chờ modal mở."""
        with self.step("Mở modal Đổi mật khẩu"):
            self.po.profile.change_password_button.click()
            expect(self._password_modal.heading).to_be_visible()

    @keyword("fillChangePassword")
    def fill_change_password(self, form):
        """Điền 3 ô trong modal đổi mật khẩu (hiện tại, mới, xác nhận)."""
        with self.step("Điền form đổi mật khẩu"):
            m = self._password_modal
            m.current_password.fill(form["currentPassword"])
            m.new_password.fill(form["newPassword"])
            m.confirm_password.fill(form["confirmPassword"])

    @keyword("submitChangePassword")
    def submit_change_password(self):
        """Bấm "Xác nhận" trong modal đổi mật khẩu."""
        with self.step("Bấm Xác nhận đổi mật khẩu"):
            self._password_modal.submit_button.click()

    @keyword("verifyChangePasswordError")
    def verify_change_password_error(self, message):
        """Kiểm tra thông báo lỗi trong modal đổi mật khẩu."""
        with self.step(f'Kiểm tra lỗi đổi mật khẩu "{message}"'):
            expect(self._password_modal.error).to_have_text(message)
            expect(self._password_modal.heading).to_be_visible()

    @keyword("verifyChangePasswordClosed")
    def verify_change_password_closed(self):
        """Kiểm tra modal đổi mật khẩu đã đóng."""
        with self.step("Kiểm tra modal Đổi mật khẩu đã đóng"):
            expect(self._password_modal.heading).to_be_hidden()

    @keyword("cancelChangePassword")
    def cancel_change_password(self):
        """Bấm "Hủy" ở cuối modal đổi mật khẩu."""
        with self.step("Bấm Hủy trong modal Đổi mật khẩu"):
            self._password_modal.cancel_button.click()

    @keyword("closeChangePassword")
    def close_change_password(self):
        """Bấm nút chữ "Đóng" ở góc trên modal đổi mật khẩu."""
        with self.step("Bấm Đóng modal Đổi mật khẩu"):
            self._password_modal.close_button.click()

    @keyword("verifyChangePasswordFormEmpty")
    def verify_change_password_form_empty(self):
        """Kiểm tra modal đổi mật khẩu đang mở với form trống, không có lỗi cũ."""
        with self.step("Kiểm tra form đổi mật khẩu trống"):
            m = self._password_modal
            expect(m.heading).to_be_visible()
            expect(m.current_password).to_have_value("")
            expect(m.new_password).to_have_value("")
            expect(m.confirm_password).to_have_value("")
            expect(m.error).to_be_hidden()

    @keyword("verifyProfileSummary")
    def verify_profile_summary(self, stats):
        """Kiểm tra dải thống kê trên trang hồ sơ: { "Tổng đơn hàng": "7", ... }."""
        with self.step(f"Kiểm tra thống kê hồ sơ: {json.dumps(stats, ensure_ascii=False)}"):
            for label, value in stats.items():
                expect(self.po.profile.summary_value(label), f'Ô "{label}"').to_have_text(value)

    @keyword("verifyRecentOrders")
    def verify_recent_orders(self, codes):
        """Kiểm tra khối "Đơn hàng gần đây" hiển thị đúng các mã đơn theo thứ tự ([] = thông báo chưa có đơn)."""
        with self.step(f"Kiểm tra đơn hàng gần đây: {', '.join(codes) or '(trống)'}"):
            section = self.po.profile.recent_orders_section
            if not codes:
                expect(section.get_by_text("Bạn chưa có đơn hàng nào", exact=True)).to_be_visible()
                return
            rows = section.locator("div.divide-y > div")
            expect(rows).to_have_count(len(codes))
            for i, code in enumerate(codes):
                expect(rows.nth(i)).to_contain_text(code)

    @keyword("verifyRecentFavorites")
    def verify_recent_favorites(self, names):
        """Kiểm tra khối "Sản phẩm yêu thích gần đây" hiển thị đúng tên theo thứ tự ([] = thông báo trống)."""
        with self.step(f"Kiểm tra yêu thích gần đây: {', '.join(names) or '(trống)'}"):
            section = self.po.profile.recent_favorites_section
            if not names:
                expect(
                    section.get_by_text("Bạn chưa lưu sản phẩm yêu thích nào", exact=True)
                ).to_be_visible()
                return
            items = section.locator("div.grid > div")
            expect(items).to_have_count(len(names))
            for i, name in enumerate(names):
                expect(items.nth(i)).to_contain_text(name)

    @keyword("verifyDefaultAddress")
    def verify_default_address(self, texts):
        """Kiểm tra khối "Địa chỉ giao hàng mặc định" chứa các đoạn chữ."""
        with self.step(f"Kiểm tra địa chỉ mặc định trên hồ sơ: {' | '.join(texts)}"):
            for t in texts:
                expect(self.po.profile.default_address_section).to_contain_text(t)

    @keyword("clickUpdateAddress")
    def click_update_address(self):
        """Bấm "Cập nhật địa chỉ" trên hồ sơ và chờ sang /addresses."""
        with self.step("Bấm Cập nhật địa chỉ"):
            self.po.profile.update_address_link.click()
            expect(self.page).to_have_url(ROUTES["addresses"])

    # -------------------------------------------------------------------------
    # Đơn hàng của tôi
    # -------------------------------------------------------------------------

    @keyword("verifyOrderStats")
    def verify_order_stats(self, stats):
        """Kiểm tra số đếm trên các ô thống kê: { "Tất cả đơn": 7, "Đã hủy": 1 }."""
        with self.step(f"Kiểm tra thống kê đơn: {json.dumps(stats, ensure_ascii=False)}"):
            for label, count in stats.items():
                expect(self.po.orders.stat_count(label), f'Ô "{label}"').to_have_text(_vi_number(count))

    @keyword("filterOrdersByStatus")
    def filter_orders_by_status(self, tab):
        """Bấm tab lọc trạng thái đơn, vd: "Chờ xác nhận"."""
        with self.step(f'Lọc đơn theo tab "{tab}"'):
            self.po.orders.tab(tab).click()
            expect(self.po.orders.tab(tab)).to_have_class(re.compile(r"bg-\[#d71920\]"))

    @keyword("clickOrderStat")
    def click_order_stat(self, label):
        """Bấm 1 ô thống kê để lọc nhanh, vd: "Đã hủy"."""
        with self.step(f'Bấm ô thống kê "{label}"'):
            self.po.orders.stat_button(label).click()

    @keyword("searchOrders")
    def search_orders(self, query):
        """Gõ vào ô "Tìm theo mã đơn hàng..."."""
        with self.step(f'Tìm đơn hàng "{query}"'):
            self.po.orders.search_input.fill(query)

    @keyword("verifyOrderList")
    def verify_order_list(self, codes):
        """Kiểm tra danh sách đơn hiển thị đúng các mã đơn theo thứ tự."""
        with self.step(f"Kiểm tra danh sách đơn: {', '.join(codes) or '(trống)'}"):
            expect(self.po.orders.order_items).to_have_count(len(codes))
            for i, code in enumerate(codes):
                expect(self.po.orders.order_items.nth(i)).to_contain_text(code)

    @keyword("verifyOrdersEmpty")
    def verify_orders_empty(self, message):
        """Kiểm tra trang đơn hàng hiển thị thông báo rỗng, vd: "Bạn chưa có đơn hàng nào"."""
        with self.step(f'Kiểm tra không có đơn: "{message}"'):
            expect(self.po.orders.empty_state(message)).to_be_visible()
            expect(self.po.orders.order_items).to_have_count(0)

    @keyword("verifyOrderItem")
    def verify_order_item(self, code, texts):
        """Kiểm tra 1 đơn trong danh sách chứa các đoạn chữ (ngày, số lượng, thanh toán, tổng tiền...)."""
        with self.step(f"Kiểm tra đơn {code}: {' | '.join(texts)}"):
            for t in texts:
                expect(self.po.orders.order_item(code)).to_contain_text(t)

    @keyword("verifyOrderStatus")
    def verify_order_status(self, code, label):
        """Kiểm tra nhãn trạng thái của 1 đơn trong danh sách."""
        with self.step(f'Kiểm tra đơn {code} có trạng thái "{label}"'):
            expect(self.po.orders.status_badge(code)).to_have_text(label)

    @keyword("verifyOrderCancelable")
    def verify_order_cancelable(self, code, cancelable):
        """Kiểm tra đơn trong danh sách có (true) / không có (false) nút "Hủy đơn"."""
        with self.step(f"Kiểm tra đơn {code} {'có' if cancelable else 'không có'} nút Hủy đơn"):
            expect(self.po.orders.order_item(code)).to_be_visible()
            expect(self.po.orders.cancel_button(code)).to_have_count(1 if cancelable else 0)

    @keyword("cancelOrderFromList")
    def cancel_order_from_list(self, code):
        """Bấm "Hủy đơn" của 1 đơn trong danh sách (app không hỏi xác nhận)."""
        with self.step(f"Hủy đơn {code} từ danh sách"):
            self.po.orders.cancel_button(code).click()

    @keyword("openOrderFromList")
    def open_order_from_list(self, code):
        """Bấm "Xem chi tiết" của 1 đơn và chờ sang trang chi tiết."""
        with self.step(f"Xem chi tiết đơn {code}"):
            self.po.orders.detail_link(code).click()
            expect(self.page).to_have_url(re.compile(r"/orders/\d+$"))
            expect(self.page.get_by_text("Đang tải thông tin đơn hàng...")).to_be_hidden()

    # -------------------------------------------------------------------------
    # Chi tiết đơn hàng
    # -------------------------------------------------------------------------

    @keyword("verifyOrderDetailHeading")
    def verify_order_detail_heading(self, heading):
        """Kiểm tra tiêu đề trang chi tiết đơn, vd: "Chi tiết đơn hàng #ORD000107"."""
        with self.step(f'Kiểm tra tiêu đề "{heading}"'):
            expect(self._order_detail.heading).to_have_text(heading)

    @keyword("verifyOrderDetailStatus")
    def verify_order_detail_status(self, status, payment):
        """Kiểm tra 2 ô trạng thái đơn hàng + trạng thái thanh toán ở đầu trang chi tiết."""
        with self.step(f'Kiểm tra trạng thái "{status}", thanh toán "{payment}"'):
            expect(self._order_detail.status_value).to_have_text(status)
            expect(self._order_detail.payment_status_value).to_have_text(payment)

    @keyword("verifyOrderDetailInfo")
    def verify_order_detail_info(self, section, rows):
        """Kiểm tra các dòng "nhãn: giá trị" trong 1 khối, vd: ("Thông tin giao hàng", { "Người nhận": "..." })."""
        with self.step(f'Kiểm tra khối "{section}"'):
            for label, value in rows.items():
                expect(self._order_detail.row_value(section, label), f'Dòng "{label}"').to_contain_text(value)

    @keyword("verifyOrderDetailItems")
    def verify_order_detail_items(self, heading, names):
        """Kiểm tra tiêu đề khối sản phẩm (vd: "Sản phẩm đã đặt (2)") và tên sản phẩm theo thứ tự."""
        with self.step(f"Kiểm tra {heading}: {', '.join(names)}"):
            expect(self._order_detail.items_heading).to_have_text(heading)
            expect(self._order_detail.item_rows).to_have_count(len(names))
            for i, name in enumerate(names):
                expect(self._order_detail.item_rows.nth(i)).to_contain_text(name)

    @keyword("verifyOrderDetailItem")
    def verify_order_detail_item(self, name, texts):
        """Kiểm tra 1 dòng sản phẩm trong đơn chứa các đoạn chữ (màu, size, SKU, giá, số lượng)."""
        with self.step(f'Kiểm tra sản phẩm "{name}" trong đơn'):
            for t in texts:
                expect(self._order_detail.item_row(name)).to_contain_text(t)

    @keyword("verifyOrderDetailTotals")
    def verify_order_detail_totals(self, rows):
        """Kiểm tra khối "Chi tiết thanh toán": { "Tạm tính": "480.000đ", "Phí vận chuyển": "Miễn phí", ... }."""
        with self.step("Kiểm tra Chi tiết thanh toán"):
            for label, value in rows.items():
                expect(
                    self._order_detail.row_value("Chi tiết thanh toán", label), f'Dòng "{label}"'
                ).to_have_text(value)

    @keyword("verifyOrderDetailCancelable")
    def verify_order_detail_cancelable(self, cancelable):
        """Kiểm tra trang chi tiết có (true) / không có (false) nút "Hủy đơn hàng"."""
        with self.step(f"Kiểm tra {'có' if cancelable else 'không có'} nút Hủy đơn hàng"):
            expect(self._order_detail.status_value).to_be_visible()
            expect(self._order_detail.cancel_button).to_have_count(1 if cancelable else 0)

    @keyword("openCancelOrderDialog")
    def open_cancel_order_dialog(self):
        """Bấm "Hủy đơn hàng" và chờ hộp xác nhận hiện ra."""
        with self.step("Mở hộp xác nhận hủy đơn"):
            self._order_detail.cancel_button.click()
            expect(self._order_detail.cancel_modal).to_be_visible()

    @keyword("confirmCancelOrder")
    def confirm_cancel_order(self, reason=""):
        """Nhập lý do (để trống = không nhập) rồi bấm "Xác nhận hủy"."""
        suffix = f' - lý do "{reason}"' if reason else ""
        with self.step(f"Xác nhận hủy đơn{suffix}"):
            if reason:
                self._order_detail.cancel_reason.fill(reason)
            self._order_detail.confirm_cancel_button.click()

    @keyword("closeCancelOrderDialog")
    def close_cancel_order_dialog(self):
        """Bấm "Đóng" trên hộp xác nhận hủy đơn."""
        with self.step("Đóng hộp xác nhận hủy đơn"):
            self._order_detail.close_cancel_button.click()

    @keyword("verifyCancelOrderDialog")
    def verify_cancel_order_dialog(self, open):
        """Kiểm tra hộp xác nhận hủy đơn đang mở (true) / đã đóng (false)."""
        with self.step(f"Kiểm tra hộp xác nhận hủy đơn {'đang mở' if open else 'đã đóng'}"):
            if open:
                expect(self._order_detail.cancel_modal).to_be_visible()
            else:
                expect(self._order_detail.cancel_modal).to_be_hidden()

    @keyword("verifyOrderDetailError")
    def verify_order_detail_error(self, message):
        """Kiểm tra trang chi tiết đơn báo lỗi (thông báo + nút "Quay lại đơn hàng")."""
        with self.step(f'Kiểm tra lỗi chi tiết đơn "{message}"'):
            expect(self._order_detail.message(message)).to_be_visible()
            expect(self._order_detail.back_to_orders_link).to_be_visible()

    @keyword("backToOrdersFromError")
    def back_to_orders_from_error(self):
        """Bấm "Quay lại đơn hàng" trên màn hình lỗi và chờ về /orders."""
        with self.step("Bấm Quay lại đơn hàng"):
            self._order_detail.back_to_orders_link.click()
            expect(self.page).to_have_url(ROUTES["orders"])

    @keyword("goBackFromOrderDetail")
    def go_back_from_order_detail(self):
        """Bấm nút "Quay lại" ở góc trên trang chi tiết đơn và chờ về /orders."""
        with self.step("Bấm Quay lại từ chi tiết đơn"):
            self._order_detail.back_link.click()
            expect(self.page).to_have_url(ROUTES["orders"])

    # -------------------------------------------------------------------------
    # Yêu thích
    # -------------------------------------------------------------------------

    @keyword("verifyWishlistCount")
    def verify_wishlist_count(self, count):
        """Kiểm tra dòng "<N> sản phẩm yêu thích" dưới tiêu đề."""
        with self.step(f"Kiểm tra có {count} sản phẩm yêu thích"):
            expect(self.po.wishlist.count_meta).to_have_text(f"{_vi_number(count)} sản phẩm yêu thích")

    @keyword("verifyWishlistProducts")
    def verify_wishlist_products(self, names):
        """Kiểm tra danh sách thẻ sản phẩm yêu thích đúng tên + đúng thứ tự."""
        with self.step(f"Kiểm tra sản phẩm yêu thích: {', '.join(names)}"):
            expect(self.po.wishlist.card_names).to_have_text(names)

    @keyword("searchWishlist")
    def search_wishlist(self, query):
        """Gõ vào ô "Tìm sản phẩm yêu thích..."."""
        with self.step(f'Tìm sản phẩm yêu thích "{query}"'):
            self.po.wishlist.search_input.fill(query)

    @keyword("sortWishlist")
    def sort_wishlist(self, sort):
        """Chọn cách sắp xếp: recent | price_asc | price_desc."""
        with self.step(f"Sắp xếp yêu thích theo {sort}"):
            self.po.wishlist.sort_select.select_option(sort)

    @keyword("removeFromWishlist")
    def remove_from_wishlist(self, name):
        """Bấm trái tim "Bỏ yêu thích" trên thẻ sản phẩm."""
        with self.step(f'Bỏ yêu thích "{name}"'):
            self.po.wishlist.remove_button(name).click()

    @keyword("addWishlistItemToCart")
    def add_wishlist_item_to_cart(self, name):
        """Bấm "Thêm vào giỏ hàng" trên thẻ sản phẩm yêu thích."""
        with self.step(f'Thêm "{name}" từ yêu thích vào giỏ'):
            self.po.wishlist.add_to_cart_button(name).click()

    @keyword("verifyWishlistItem")
    def verify_wishlist_item(self, name, texts):
        """Kiểm tra thẻ sản phẩm yêu thích chứa các đoạn chữ (danh mục, giá, % giảm, tình trạng...)."""
        with self.step(f"Kiểm tra thẻ \"{name}\": {' | '.join(texts)}"):
            for t in texts:
                expect(self.po.wishlist.card(name)).to_contain_text(t)

    @keyword("verifyWishlistItemAvailable")
    def verify_wishlist_item_available(self, name, available):
        """Kiểm tra sản phẩm còn hàng (nút thêm giỏ bật) hay hết hàng (nhãn "Hết hàng", nút tắt)."""
        with self.step(f"Kiểm tra \"{name}\" {'còn hàng' if available else 'hết hàng'}"):
            w = self.po.wishlist
            if available:
                expect(w.add_to_cart_button(name)).to_be_enabled()
                expect(w.out_of_stock_overlay(name)).to_be_hidden()
            else:
                expect(w.add_to_cart_button(name)).to_be_disabled()
                expect(w.out_of_stock_overlay(name)).to_be_visible()

    @keyword("verifyWishlistNoMatch")
    def verify_wishlist_no_match(self):
        """Kiểm tra thông báo "Không tìm thấy sản phẩm phù hợp" khi lọc/tìm không ra."""
        with self.step("Kiểm tra không có sản phẩm yêu thích phù hợp"):
            expect(self.po.wishlist.no_match).to_be_visible()
            expect(self.po.wishlist.cards).to_have_count(0)

    @keyword("verifyWishlistEmpty")
    def verify_wishlist_empty(self):
        """Kiểm tra trang yêu thích trống ("Bạn chưa có sản phẩm yêu thích", 0 sản phẩm)."""
        with self.step("Kiểm tra danh sách yêu thích trống"):
            expect(self.po.wishlist.empty_state).to_be_visible()
            expect(self.po.wishlist.count_meta).to_have_text("0 sản phẩm yêu thích")
            expect(self.po.wishlist.search_input).to_be_hidden()

    @keyword("favoriteFromListing")
    def favorite_from_listing(self, path):
        """Mở trang danh mục và bấm nút trái tim (yêu thích) của sản phẩm đầu tiên."""
        with self.step(f"Bấm trái tim sản phẩm đầu tiên trên {path}"):
            self.page.goto(path)
            self.po.wishlist.listing_heart_buttons.first.click()

    # -------------------------------------------------------------------------
    # Sổ địa chỉ
    # -------------------------------------------------------------------------

    @keyword("verifyAddressesEmpty")
    def verify_addresses_empty(self):
        """Kiểm tra trang địa chỉ trống ("Bạn chưa có địa chỉ nào")."""
        with self.step("Kiểm tra chưa có địa chỉ nào"):
            expect(self._addresses.empty_title).to_be_visible()
            expect(self._addresses.subtitle).to_have_text("Quản lý địa chỉ giao hàng của bạn")
            expect(self._addresses.cards).to_have_count(0)

    @keyword("openAddAddressForm")
    def open_add_address_form(self):
        """Bấm nút "Thêm địa chỉ" trên tiêu đề và chờ form "Thêm địa chỉ mới"."""
        with self.step("Mở form Thêm địa chỉ"):
            self._addresses.add_button.click()
            expect(self._addresses.form_heading).to_have_text("Thêm địa chỉ mới")

    @keyword("openAddAddressFromEmptyState")
    def open_add_address_from_empty_state(self):
        """Bấm "Thêm địa chỉ mới" ở màn hình trống và chờ form mở."""
        with self.step("Bấm Thêm địa chỉ mới (màn hình trống)"):
            self._addresses.empty_add_button.click()
            expect(self._addresses.form_heading).to_have_text("Thêm địa chỉ mới")

    @keyword("fillAddressForm")
    def fill_address_form(self, form):
        """Điền form địa chỉ (chỉ các trường có trong dữ liệu); city = tên tỉnh, vd: "Hồ Chí Minh"."""
        with self.step(f"Điền form địa chỉ: {', '.join(form)}"):
            a = self._addresses
            if "fullName" in form:
                a.full_name.fill(form["fullName"])
            if "phone" in form:
                a.phone.fill(form["phone"])
            if "address" in form:
                a.address.fill(form["address"])
            if "ward" in form:
                a.ward.fill(form["ward"])
            if "district" in form:
                a.district.fill(form["district"])
            if "city" in form:
                a.city.select_option(form["city"])
            if "isDefault" in form:
                a.default_checkbox.set_checked(form["isDefault"])

    @keyword("submitAddressForm")
    def submit_address_form(self):
        """Bấm nút lưu của form địa chỉ ("Thêm địa chỉ" / "Lưu thay đổi")."""
        with self.step("Bấm lưu form địa chỉ"):
            self._addresses.submit_button.click()

    @keyword("cancelAddressForm")
    def cancel_address_form(self):
        """Bấm "Hủy" để đóng form địa chỉ."""
        with self.step("Bấm Hủy form địa chỉ"):
            self._addresses.cancel_button.click()

    @keyword("verifyAddressFormErrors")
    def verify_address_form_errors(self, messages):
        """Kiểm tra các thông báo lỗi dưới ô nhập của form địa chỉ."""
        with self.step(f"Kiểm tra lỗi form địa chỉ: {' | '.join(messages)}"):
            for m in messages:
                expect(self._addresses.field_error(m)).to_be_visible()
            expect(self._addresses.form.locator("p.text-xs")).to_have_count(len(messages))

    @keyword("verifyAddressFormOpen")
    def verify_address_form_open(self, heading):
        """Kiểm tra form địa chỉ đang mở với tiêu đề: "Thêm địa chỉ mới" | "Sửa địa chỉ"."""
        with self.step(f'Kiểm tra form "{heading}" đang mở'):
            expect(self._addresses.form_heading).to_have_text(heading)
            expect(self._addresses.default_checkbox).to_have_count(0 if heading == "Sửa địa chỉ" else 1)

    @keyword("verifyAddressFormClosed")
    def verify_address_form_closed(self):
        """Kiểm tra form địa chỉ đã đóng."""
        with self.step("Kiểm tra form địa chỉ đã đóng"):
            expect(self._addresses.form).to_be_hidden()

    @keyword("verifyAddressFormValues")
    def verify_address_form_values(self, form):
        """Kiểm tra giá trị đang có trong form địa chỉ."""
        with self.step("Kiểm tra giá trị form địa chỉ"):
            a = self._addresses
            if "fullName" in form:
                expect(a.full_name).to_have_value(form["fullName"])
            if "phone" in form:
                expect(a.phone).to_have_value(form["phone"])
            if "address" in form:
                expect(a.address).to_have_value(form["address"])
            if "ward" in form:
                expect(a.ward).to_have_value(form["ward"])
            if "district" in form:
                expect(a.district).to_have_value(form["district"])
            if "city" in form:
                expect(a.city).to_have_value(form["city"])

    @keyword("verifyAddressList")
    def verify_address_list(self, names):
        """Kiểm tra danh sách thẻ địa chỉ (tên người nhận theo thứ tự) và dòng "<N> địa chỉ đã lưu"."""
        with self.step(f"Kiểm tra danh sách địa chỉ: {', '.join(names)}"):
            expect(self._addresses.cards.locator("p.font-semibold")).to_have_text(names)
            expect(self._addresses.subtitle).to_have_text(f"{len(names)} địa chỉ đã lưu")

    @keyword("verifyAddressCard")
    def verify_address_card(self, name, texts):
        """Kiểm tra thẻ địa chỉ của người nhận chứa các đoạn chữ (SĐT, địa chỉ đầy đủ...)."""
        with self.step(f'Kiểm tra thẻ địa chỉ "{name}"'):
            for t in texts:
                expect(self._addresses.card(name)).to_contain_text(t)

    @keyword("verifyAddressDefault")
    def verify_address_default(self, name, is_default):
        """Kiểm tra địa chỉ là mặc định (badge "Mặc định", không có nút đặt mặc định) hay không."""
        with self.step(f"Kiểm tra \"{name}\" {'là' if is_default else 'không là'} địa chỉ mặc định"):
            expect(self._addresses.card(name)).to_be_visible()
            expect(self._addresses.default_badge(name)).to_have_count(1 if is_default else 0)
            expect(self._addresses.set_default_button(name)).to_have_count(0 if is_default else 1)

    @keyword("verifyAddressNameRow")
    def verify_address_name_row(self, name, is_default):
        """Kiểm tra dòng tên trên thẻ địa chỉ chỉ gồm tên (+ "Mặc định" nếu là mặc định), không có ký tự thừa."""
        with self.step(f'Kiểm tra dòng tên thẻ "{name}" không có ký tự thừa'):
            expected = re.compile(rf"^{escape_regex(name)}\s*Mặc định$") if is_default else name
            expect(self._addresses.name_row(name)).to_have_text(expected)

    @keyword("verifyDefaultBadgeCount")
    def verify_default_badge_count(self, count):
        """Kiểm tra số badge "Mặc định" trên toàn trang địa chỉ."""
        with self.step(f"Kiểm tra có {count} badge Mặc định"):
            expect(self._addresses.cards.first).to_be_visible()
            expect(self._addresses.default_badges).to_have_count(count)

    @keyword("editAddress")
    def edit_address(self, name):
        """Bấm nút "Sửa" trên thẻ địa chỉ và chờ form "Sửa địa chỉ"."""
        with self.step(f'Sửa địa chỉ "{name}"'):
            self._addresses.edit_button(name).click()
            expect(self._addresses.form_heading).to_have_text("Sửa địa chỉ")

    @keyword("setDefaultAddress")
    def set_default_address(self, name):
        """Bấm nút "Đặt làm mặc định" trên thẻ địa chỉ."""
        with self.step(f'Đặt "{name}" làm địa chỉ mặc định'):
            self._addresses.set_default_button(name).click()

    @keyword("deleteAddress")
    def delete_address(self, name):
        """Bấm nút "Xóa" trên thẻ địa chỉ và chờ hộp xác nhận "Xóa địa chỉ"."""
        with self.step(f'Bấm Xóa địa chỉ "{name}"'):
            self._addresses.delete_button(name).click()
            expect(self._addresses.delete_modal).to_be_visible()

    @keyword("confirmDeleteAddress")
    def confirm_delete_address(self):
        """Bấm "Xóa địa chỉ" trong hộp xác nhận."""
        with self.step("Xác nhận xóa địa chỉ"):
            self._addresses.confirm_delete_button.click()

    @keyword("cancelDeleteAddress")
    def cancel_delete_address(self):
        """Bấm "Hủy" trong hộp xác nhận xóa địa chỉ và chờ hộp đóng."""
        with self.step("Hủy xóa địa chỉ"):
            self._addresses.cancel_delete_button.click()
            expect(self._addresses.delete_modal).to_be_hidden()

    @keyword("verifyDeleteAddressDialog")
    def verify_delete_address_dialog(self, text):
        """Kiểm tra hộp xác nhận xóa địa chỉ chứa đoạn chữ, vd: câu hỏi kèm địa chỉ."""
        with self.step(f'Kiểm tra hộp xác nhận xóa: "{text}"'):
            expect(self._addresses.delete_modal).to_contain_text(text)

    # -------------------------------------------------------------------------
    # Thanh toán khi đã đăng nhập + trang đặt hàng thành công
    # -------------------------------------------------------------------------

    @keyword("verifyCheckoutAccount")
    def verify_checkout_account(self, name, email):
        """Kiểm tra trang thanh toán hiển thị tài khoản đang đăng nhập (tên + email), không có nút đăng nhập."""
        with self.step(f'Kiểm tra thanh toán với tài khoản "{email}"'):
            expect(self._checkout_account.name).to_have_text(name)
            expect(self._checkout_account.email).to_have_text(email)
            expect(self.po.checkout.login_button).to_have_count(0)

    @keyword("verifyCheckoutPrefill")
    def verify_checkout_prefill(self, expected):
        """Kiểm tra form giao hàng được điền sẵn từ tài khoản: { firstName, lastName, phone }."""
        with self.step(
            f'Kiểm tra điền sẵn: Họ "{expected["firstName"]}", Tên "{expected["lastName"]}"'
        ):
            expect(self.po.checkout.last_name).to_have_value(expected["lastName"])
            expect(self.po.checkout.first_name).to_have_value(expected["firstName"])
            expect(self.po.checkout.phone).to_have_value(expected["phone"])

    @keyword("logoutOnCheckout")
    def logout_on_checkout(self):
        """Bấm "Đăng xuất" trong khối tài khoản trên trang thanh toán."""
        with self.step("Đăng xuất ngay trên trang thanh toán"):
            self._checkout_account.logout_button.click()

    @keyword("verifyCheckoutGuestMode")
    def verify_checkout_guest_mode(self):
        """Kiểm tra trang thanh toán chuyển về chế độ khách vãng lai (vẫn ở /checkout, token bị xóa)."""
        with self.step("Kiểm tra thanh toán ở chế độ khách vãng lai"):
            expect(self._checkout_account.root).to_be_hidden()
            expect(self.po.checkout.login_button).to_be_visible()
            expect(self.page).to_have_url(ROUTES["checkout"])
            token = self.page.evaluate("k => localStorage.getItem(k)", STORAGE_KEYS["customerToken"])
            assert token is None, f"Token khách hàng: expected=None, actual={token!r}"

    @keyword("goToLoginFromCheckout")
    def go_to_login_from_checkout(self):
        """Bấm "Đăng nhập / Đăng ký" trên trang thanh toán và chờ sang /login."""
        with self.step("Bấm Đăng nhập / Đăng ký trên trang thanh toán"):
            self.po.checkout.login_button.click()
            expect(self.page).to_have_url(ROUTES["login"])

    @keyword("verifyOrderSuccessNumber")
    def verify_order_success_number(self, order_number):
        """Kiểm tra mã đơn hiển thị cạnh "Mã đơn hàng:" trên trang đặt hàng thành công."""
        with self.step(f"Kiểm tra mã đơn {order_number}"):
            expect(self._order_success.order_number).to_have_text(order_number)

    @keyword("verifyOrderSuccessInfo")
    def verify_order_success_info(self, section, rows):
        """Kiểm tra các dòng trong 1 khối trang thành công: "Thông tin thanh toán" | "Người nhận" | "Chi tiết thanh toán"."""
        with self.step(f'Kiểm tra khối "{section}" trên trang thành công'):
            for label, value in rows.items():
                expect(self._order_success.row_value(section, label), f'Dòng "{label}"').to_have_text(value)

    @keyword("verifyOrderSuccessLinks")
    def verify_order_success_links(self):
        """Kiểm tra trang thành công có 2 link "Tiếp tục mua sắm" (về /) và link "Xem đơn hàng" (tới /orders)."""
        with self.step("Kiểm tra các link điều hướng trên trang thành công"):
            expect(self._order_success.continue_links).to_have_count(2)
            for link in self._order_success.continue_links.all():
                expect(link).to_have_attribute("href", "/")
            expect(self._order_success.view_orders_link).to_have_attribute("href", ROUTES["orders"])

    @keyword("openOrdersFromSuccess")
    def open_orders_from_success(self):
        """Bấm "Xem đơn hàng" trên trang thành công và chờ sang /orders."""
        with self.step("Bấm Xem đơn hàng"):
            self._order_success.view_orders_link.click()
            expect(self.page).to_have_url(ROUTES["orders"])
