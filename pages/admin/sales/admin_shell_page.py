# ============================================================
# Khung trang quản trị: sidebar (thu gọn, menu, chân sidebar), header (tiêu đề, chuông thông báo,
# menu người dùng).
# Lưu ý: h1 header, link sidebar và nút trong menu người dùng trùng tên ("Tổng quan", "Cài đặt",
# "Đăng xuất") -> luôn scope theo vùng.
# ============================================================
import re


class AdminShellPage:
    def __init__(self, page):
        self.page = page
        self.sidebar = page.locator("aside").first
        self.header = page.locator("header").first
        self.main = page.locator("main").first
        self.page_title = self.header.locator("h1")
        # Nút thu gọn/mở rộng sidebar (icon chevron, không có tên) - nút đầu tiên trong sidebar.
        self.sidebar_toggle = self.sidebar.locator("button").first
        self.menu_nav = self.sidebar.locator("nav")
        self.active_menu_links = self.menu_nav.locator("a.bg-\\[\\#d71920\\]")
        self.store_link = self.sidebar.locator('a[href="/"]')
        self.sidebar_logout = self.sidebar.locator("div.border-t button")
        self.sidebar_user = self.sidebar.locator("div.border-t div.bg-gray-50")

        # Chuông thông báo (không có tên) - nút đầu tiên bên phải header.
        self.bell_button = self.header.get_by_role("button").first
        self.bell_badge = self.bell_button.locator("span")
        self.notification_panel = page.locator("div.fixed.top-16.right-6")
        self.notification_overlay = page.locator("div.fixed.inset-0.z-40")
        self.notification_empty = self.notification_panel.get_by_text("Không có thông báo nào", exact=True)
        self.notification_items = self.notification_panel.locator("div.cursor-pointer")
        self.notification_stats = self.notification_panel.locator("div.overflow-x-auto > span")
        self.notification_footer_count = self.notification_panel.get_by_text(re.compile(r"^\d+ thông báo$"))
        self.notification_new_chip = self.notification_panel.get_by_text(re.compile(r"^\d+ mới$"))
        self.mark_all_read_button = self.notification_panel.get_by_role(
            "button", name="Đánh dấu đã đọc", exact=True
        )
        self.refresh_button = self.notification_panel.get_by_title("Làm mới", exact=True)
        self.close_panel_button = (
            self.notification_panel.locator("div.border-b").first.get_by_role("button").last
        )
        self.view_all_orders_link = self.notification_panel.get_by_role(
            "link", name="Xem tất cả đơn hàng", exact=True
        )

        # Nút mở menu người dùng (avatar + tên) - nút thứ 2 bên phải header.
        self.user_button = self.header.get_by_role("button").nth(1)
        self.user_menu = self.header.locator("div.absolute.right-0.top-full")

    def menu_link(self, label):
        return self.menu_nav.get_by_role("link", name=label, exact=True)

    def notification_item(self, title):
        return self.notification_items.filter(has=self.page.get_by_text(title, exact=True))

    def user_menu_item(self, label):
        return self.user_menu.get_by_role("button", name=label, exact=True)
