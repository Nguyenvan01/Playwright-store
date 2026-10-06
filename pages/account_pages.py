# Trang tài khoản khách hàng: hồ sơ (/profile), đơn hàng (/orders), yêu thích (/favorites).
import re

from pages.account.css_text import css_text, escape_regex
from pages.base_page import BasePage
from pages.components.header import Header


class ProfilePage(BasePage):
    """Trang /profile (ProfilePage.jsx).
    Lưu ý: mở trực tiếp /profile bị crash (bug) -> vào qua menu tài khoản trên header.
    Ô nhập không gắn label -> định vị qua đoạn chữ nhãn đứng ngay trước (FieldLabel <p>)."""

    path = "/profile"

    def __init__(self, page):
        super().__init__(page)
        self.header = Header(page)
        self.account_info_heading = page.get_by_role("heading", name="Thông tin tài khoản")
        self.heading = page.get_by_role("heading", level=1, name="Hồ sơ cá nhân")
        self.edit_button = page.get_by_role("button", name="Chỉnh sửa", exact=True)
        self.change_password_button = page.get_by_role("button", name="Đổi mật khẩu", exact=True)
        # Khối "Thông tin tài khoản" (xem + sửa).
        # AccountLayout bọc nội dung trong 1 <section> ngoài cùng -> lấy section trong cùng (.last).
        self.account_info = page.locator("section").filter(has=self.account_info_heading).last
        self.name_input = self.account_info.locator('p:text-is("Họ và tên *") + input')
        self.email_input = self.account_info.locator('p:text-is("Email") + input')
        self.phone_input = self.account_info.locator('p:text-is("Số điện thoại") + input')
        self.birth_date_input = self.account_info.get_by_placeholder("1995-05-15")
        self.gender_select = self.account_info.locator('p:text-is("Giới tính") + select')
        self.save_button = self.account_info.get_by_role(
            "button", name=re.compile(r"^(Lưu thay đổi|Đang lưu\.\.\.)$")
        )
        self.cancel_edit_button = self.account_info.get_by_role("button", name="Hủy", exact=True)
        self.default_address_section = (
            page.locator("section")
            .filter(has=page.get_by_role("heading", name="Địa chỉ giao hàng mặc định"))
            .last
        )
        self.update_address_link = self.default_address_section.get_by_role("link", name="Cập nhật địa chỉ")
        # Dải 4 ô thống kê (Tổng đơn hàng, Đơn đang xử lý...).
        self.summary = page.locator("main div.grid").filter(has=page.locator('p:text-is("Tổng đơn hàng")'))
        self.recent_orders_section = (
            page.locator("section").filter(has=page.get_by_role("heading", name="Đơn hàng gần đây")).last
        )
        self.recent_favorites_section = (
            page.locator("section")
            .filter(has=page.get_by_role("heading", name="Sản phẩm yêu thích gần đây"))
            .last
        )

    def field_value(self, label):
        """Giá trị hiển thị của 1 trường ở chế độ xem, vd: field_value("Email")."""
        return self.account_info.locator(f'p:text-is("{css_text(label)}") + p')

    def summary_value(self, label):
        """Giá trị 1 ô thống kê, vd: summary_value("Tổng đơn hàng")."""
        return self.summary.locator(f'p:text-is("{css_text(label)}") + p')


class OrdersPage(BasePage):
    """Trang /orders (OrdersPage.jsx + OrderListItem.jsx)."""

    path = "/orders"

    def __init__(self, page):
        super().__init__(page)
        self.search_input = page.get_by_placeholder("Tìm theo mã đơn hàng...")
        self.heading = page.get_by_role("heading", level=1, name="Đơn hàng của tôi")
        # Mỗi đơn là 1 <article>.
        self.order_items = page.locator("main article")

    def stat_button(self, label):
        """Ô thống kê (nút) có nhãn + số đếm, vd: stat_button("Đã hủy") -> "Đã hủy 1"."""
        return self.page.get_by_role("button", name=re.compile(rf"^{escape_regex(label)} [\d.]+$"))

    def stat_count(self, label):
        """Số đếm bên dưới nhãn của ô thống kê."""
        return self.stat_button(label).locator("p").nth(1)

    def tab(self, label):
        """Tab lọc trạng thái (tên khớp tuyệt đối để không nhầm với ô thống kê)."""
        return self.page.get_by_role("button", name=label, exact=True)

    def order_item(self, code):
        return self.order_items.filter(has=self.page.get_by_role("link", name=code, exact=True))

    def status_badge(self, code):
        return self.order_item(code).locator("span.rounded-full")

    def cancel_button(self, code):
        return self.order_item(code).get_by_role("button", name=re.compile(r"^(Hủy đơn|Đang hủy\.\.\.)$"))

    def detail_link(self, code):
        return self.order_item(code).get_by_role("link", name="Xem chi tiết", exact=True)

    def empty_state(self, title):
        return self.page.locator("main").get_by_text(title, exact=True)


class WishlistPage(BasePage):
    """Trang /favorites (WishlistPage.jsx + FavoriteProductCard.jsx)."""

    path = "/favorites"

    def __init__(self, page):
        super().__init__(page)
        self.heading = page.get_by_role("heading", level=1, name="Danh sách yêu thích")
        # Chỉ hiển thị khi danh sách yêu thích có sản phẩm.
        self.search_input = page.get_by_placeholder("Tìm sản phẩm yêu thích...")
        self.empty_state = page.get_by_text("Bạn chưa có sản phẩm yêu thích")
        self.count_meta = page.locator("main").get_by_text(re.compile(r"^[\d.]+ sản phẩm yêu thích$"))
        self.sort_select = page.locator("main select")
        self.cards = page.locator("main article")
        self.card_names = self.cards.locator("h3")
        self.no_match = page.locator("main").get_by_text("Không tìm thấy sản phẩm phù hợp", exact=True)
        # Nút trái tim trên trang danh mục (MenPage.jsx) - chỉ để trang trí, không gọi API.
        self.listing_heart_buttons = page.locator("main").get_by_role("button", name="favorite", exact=True)

    def card(self, name):
        return self.cards.filter(has=self.page.get_by_role("heading", name=name, exact=True))

    def remove_button(self, name):
        return self.card(name).get_by_role("button", name="Bỏ yêu thích")

    def add_to_cart_button(self, name):
        return self.card(name).get_by_role(
            "button", name=re.compile(r"^(Thêm vào giỏ hàng|Đang thêm\.\.\.)$")
        )

    def out_of_stock_overlay(self, name):
        return self.card(name).get_by_text("Hết hàng", exact=True)
