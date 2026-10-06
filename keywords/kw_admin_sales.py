# THƯ VIỆN KEYWORD - NHÓM adminSales: quản trị bán hàng: layout/header/thông báo, dashboard,
# đơn hàng, khách hàng, nhân viên.
import json
import math
import re
from urllib.parse import urlparse

from playwright.sync_api import expect

from keywords.base_keywords import BaseKeywords, keyword
from pages.admin.sales.admin_api_mock import AdminRequestLog, fulfill_get, includes_ci, query_of
from pages.admin.sales.admin_shell_page import AdminShellPage
from pages.admin.sales.dashboard_page import DashboardPage
from pages.admin.sales.orders_page import OrdersPage
from pages.admin.sales.people_pages import CustomersPage, EmployeesPage
from utils.assertions import poll_until

PAGE_SIZE = 20


def _total_pages(total):
    return math.ceil(total / PAGE_SIZE)


def _page_of(route):
    return int(query_of(route).get("page") or 1)


def _json(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


class AdminSalesKeywords(BaseKeywords):
    """Quản trị bán hàng: layout/header/thông báo, dashboard, đơn hàng, khách hàng, nhân viên."""

    group = "adminSales"

    def __init__(self, page, po, api, common=None):
        super().__init__(page, po, api, common)
        self._shell = AdminShellPage(page)
        self._dashboard = DashboardPage(page)
        self._orders = OrdersPage(page)
        self._customers = CustomersPage(page)
        self._employees = EmployeesPage(page)
        self._requests = AdminRequestLog(page)

    # ===========================================================================
    # Mock dữ liệu đọc (GET) - KHÔNG chặn request ghi
    # ===========================================================================

    @keyword("mockOrdersApi")
    def mock_orders_api(self, fixture):
        """Mock GET /admin/orders (lọc search/status/payment_status), /admin/orders/stats và /admin/orders/:id."""

        def handle(route):
            parts = urlparse(route.request.url).path.split("/admin/orders")
            seg = re.sub(r"^/", "", parts[1]) if len(parts) > 1 else ""
            if seg == "stats":
                return fulfill_get(route, lambda: {"stats": fixture.get("stats") or {}})
            if seg:
                order = next((o for o in fixture["orders"] if str(o["id"]) == seg), None)
                if order is None:
                    return fulfill_get(route, lambda: {"success": False, "message": "Không tìm thấy"}, 404)
                detail = (fixture.get("details") or {}).get(seg) or {}
                return fulfill_get(route, lambda: {"order": {**order, **detail}})
            q = query_of(route)
            search = q.get("search") or ""
            orders = [
                o
                for o in fixture["orders"]
                if (not q.get("status") or o.get("status") == q.get("status"))
                and (not q.get("payment_status") or o.get("payment_status") == q.get("payment_status"))
                and (
                    not search
                    or any(
                        includes_ci(o.get(k), search)
                        for k in ("order_number", "customer_name", "customer_phone", "customer_email")
                    )
                )
            ]
            total = fixture["total"] if fixture.get("total") is not None else len(orders)
            return fulfill_get(
                route,
                lambda: {
                    "orders": orders,
                    "total": total,
                    "totalPages": _total_pages(total),
                    "page": _page_of(route),
                    "stats": {},
                },
            )

        with self.step(f"Mock API đơn hàng ({len(fixture['orders'])} đơn)"):
            self.page.route(re.compile(r"/api/admin/orders(?:/([^/?#]+))?(?:\?.*)?$"), handle)

    @keyword("mockCustomersApi")
    def mock_customers_api(self, fixture):
        """Mock GET /admin/customers (lọc search) và /admin/customers/:id."""

        def handle(route):
            match = re.search(r"customers/(\d+)$", urlparse(route.request.url).path)
            if match:
                customer_id = match.group(1)
                customer = next((c for c in fixture["customers"] if str(c["id"]) == customer_id), None)
                detail = (fixture.get("details") or {}).get(customer_id) or {}
                return fulfill_get(
                    route, lambda: {"success": True, "customer": {**(customer or {}), **detail}}
                )
            search = query_of(route).get("search") or ""
            customers = [
                c
                for c in fixture["customers"]
                if not search or any(includes_ci(c.get(k), search) for k in ("name", "email", "phone"))
            ]
            total = fixture["total"] if fixture.get("total") is not None else len(customers)
            return fulfill_get(
                route,
                lambda: {
                    "success": True,
                    "customers": customers,
                    "total": total,
                    "totalPages": _total_pages(total),
                    "page": _page_of(route),
                },
            )

        with self.step(f"Mock API khách hàng ({len(fixture['customers'])} khách)"):
            self.page.route(re.compile(r"/api/admin/customers(?:/(\d+))?(?:\?.*)?$"), handle)

    @keyword("mockEmployeesApi")
    def mock_employees_api(self, fixture):
        """Mock GET /admin/employees (lọc search theo tên/email)."""

        def handle(route):
            search = query_of(route).get("search") or ""
            employees = [
                e
                for e in fixture["employees"]
                if not search or any(includes_ci(e.get(k), search) for k in ("name", "email"))
            ]
            total = fixture["total"] if fixture.get("total") is not None else len(employees)
            return fulfill_get(
                route,
                lambda: {
                    "employees": employees,
                    "total": total,
                    "totalPages": _total_pages(total),
                    "page": _page_of(route),
                },
            )

        with self.step(f"Mock API nhân viên ({len(fixture['employees'])} người)"):
            self.page.route(re.compile(r"/api/admin/employees(?:\?.*)?$"), handle)

    @keyword("verifyApiRequested")
    def verify_api_requested(self, path, params=None):
        """Kiểm tra trình duyệt đã gọi GET tới đường dẫn (vd: "/admin/orders") với đủ tham số query."""
        params = params or {}
        with self.step(f"Kiểm tra đã gọi GET {path} {_json(params)}"):
            try:
                poll_until(lambda: self._requests.has(path, params), "")
            except AssertionError:
                # Thông báo tính lúc hết hạn để liệt kê đủ các request đã gọi.
                raise AssertionError(
                    f"Không thấy GET {path} với {_json(params)}. Đã gọi: {self._requests.describe()}"
                ) from None

    @keyword("verifyColumns")
    def verify_columns(self, headers):
        """Kiểm tra tiêu đề cột bảng theo nội dung gốc (bỏ qua CSS uppercase), đúng thứ tự."""
        with self.step(f"Kiểm tra cột bảng: {' | '.join(headers)}"):
            ths = self.page.locator("main table").first.locator("thead th")
            expect(ths.first).to_be_visible()
            texts = [t.strip() for t in ths.all_text_contents() if t.strip()]
            assert texts == list(headers), f"Cột bảng: expected={list(headers)!r}, actual={texts!r}"

    @keyword("verifyApiRequestCount")
    def verify_api_request_count(self, path, min_count):
        """Kiểm tra số request GET tới đường dẫn đạt ít nhất `min` lần."""
        with self.step(f"Kiểm tra GET {path} được gọi >= {min_count} lần"):
            poll_until(
                lambda: self._requests.count(path) >= min_count,
                f"GET {path}: expected>={min_count}, actual={self._requests.count(path)}",
            )

    # ===========================================================================
    # Layout: sidebar / header / menu người dùng
    # ===========================================================================

    @keyword("toggleSidebar")
    def toggle_sidebar(self):
        """Bấm nút thu gọn / mở rộng sidebar."""
        with self.step("Bấm nút thu gọn/mở rộng sidebar"):
            self._shell.sidebar_toggle.click()

    @keyword("verifySidebarCollapsed")
    def verify_sidebar_collapsed(self, collapsed):
        """Kiểm tra sidebar đang thu gọn (72px, ẩn chữ menu) hoặc mở rộng (260px)."""
        with self.step(f"Kiểm tra sidebar {'thu gọn' if collapsed else 'mở rộng'}"):
            width = "72px" if collapsed else "260px"
            expect(self._shell.sidebar).to_have_class(re.compile(rf"w-\[{width}\]"))
            expect(self._shell.main).to_have_class(re.compile(rf"ml-\[{width}\]"))
            expect(self._shell.header).to_have_class(re.compile(rf"left-\[{width}\]"))
            label = self._shell.menu_nav.get_by_text("Sản phẩm", exact=True)
            if collapsed:
                expect(label).to_have_count(0)
                expect(self._shell.store_link.get_by_text("Xem cửa hàng")).to_have_count(0)
            else:
                expect(label).to_be_visible()
                expect(self._shell.store_link).to_have_text("Xem cửa hàng")

    @keyword("verifyActiveMenu")
    def verify_active_menu(self, label):
        """Kiểm tra chỉ có đúng 1 mục sidebar đang sáng và đó là `label`."""
        with self.step(f'Kiểm tra mục sidebar đang chọn là "{label}"'):
            expect(self._shell.active_menu_links).to_have_count(1)
            expect(self._shell.active_menu_links).to_have_text(label)
            expect(self._shell.menu_link(label)).to_have_class(re.compile(r"bg-\[#d71920\]"))

    @keyword("clickViewStore")
    def click_view_store(self):
        """Bấm "Xem cửa hàng" ở chân sidebar."""
        with self.step('Sidebar -> "Xem cửa hàng"'):
            self._shell.store_link.click()

    @keyword("logout")
    def logout(self, source):
        """Đăng xuất từ chân sidebar ("sidebar") hoặc menu người dùng trên header ("menu")."""
        with self.step(f"Đăng xuất từ {'sidebar' if source == 'sidebar' else 'menu người dùng'}"):
            if source == "sidebar":
                self._shell.sidebar_logout.click()
            else:
                self._shell.user_button.click()
                self._shell.user_menu_item("Đăng xuất").click()

    @keyword("verifySidebarUser")
    def verify_sidebar_user(self, name, role):
        """Kiểm tra khối người dùng ở chân sidebar (tên + vai trò)."""
        with self.step(f'Kiểm tra sidebar hiện "{name}" ({role})'):
            expect(self._shell.sidebar_user.locator("p").first).to_have_text(name)
            expect(self._shell.sidebar_user.locator("p").last).to_have_text(role)

    @keyword("openUserMenu")
    def open_user_menu(self):
        """Mở menu người dùng trên header."""
        with self.step("Mở menu người dùng"):
            self._shell.user_button.click()
            expect(self._shell.user_menu).to_be_visible()

    @keyword("verifyUserMenu")
    def verify_user_menu(self, name, email, role):
        """Kiểm tra nút người dùng và menu thả xuống hiển thị tên, email, 3 mục."""
        with self.step(f'Kiểm tra menu người dùng "{name}" <{email}>'):
            expect(self._shell.user_button).to_contain_text(name)
            expect(self._shell.user_button).to_contain_text(role)
            expect(self._shell.user_menu.locator("p").first).to_have_text(name)
            expect(self._shell.user_menu.locator("p").nth(1)).to_have_text(email)
            expect(self._shell.user_menu.get_by_role("button")).to_have_text(
                ["Tổng quan", "Cài đặt", "Đăng xuất"]
            )

    @keyword("chooseUserMenuItem")
    def choose_user_menu_item(self, label):
        """Bấm 1 mục trong menu người dùng ("Tổng quan" / "Cài đặt" / "Đăng xuất")."""
        with self.step(f'Menu người dùng -> "{label}"'):
            self._shell.user_menu_item(label).click()

    @keyword("clickOutsideUserMenu")
    def click_outside_user_menu(self):
        """Bấm ra ngoài menu người dùng (vào tiêu đề trang) để đóng menu."""
        with self.step("Bấm ra ngoài menu người dùng"):
            self._shell.page_title.click()

    @keyword("verifyUserMenuOpen")
    def verify_user_menu_open(self, is_open):
        """Kiểm tra menu người dùng đang mở/đóng."""
        with self.step(f"Kiểm tra menu người dùng {'đang mở' if is_open else 'đã đóng'}"):
            if is_open:
                expect(self._shell.user_menu).to_be_visible()
            else:
                expect(self._shell.user_menu).to_have_count(0)

    # ===========================================================================
    # Chuông thông báo
    # ===========================================================================

    @keyword("openNotifications")
    def open_notifications(self):
        """Bấm chuông thông báo để mở panel."""
        with self.step("Mở panel thông báo"):
            self._shell.bell_button.click()
            expect(self._shell.notification_panel.get_by_text("Thông báo", exact=True)).to_be_visible()

    @keyword("closeNotifications")
    def close_notifications(self, via="button"):
        """Đóng panel thông báo bằng nút X ("button") hoặc bấm ra ngoài ("overlay")."""
        with self.step(f"Đóng panel thông báo ({'nút X' if via == 'button' else 'bấm ra ngoài'})"):
            if via == "button":
                self._shell.close_panel_button.click()
            else:
                self._shell.notification_overlay.click(position={"x": 20, "y": 400})

    @keyword("verifyNotificationPanelOpen")
    def verify_notification_panel_open(self, is_open):
        """Kiểm tra panel thông báo đang mở / đã đóng."""
        with self.step(f"Kiểm tra panel thông báo {'đang mở' if is_open else 'đã đóng'}"):
            if is_open:
                expect(self._shell.notification_panel).to_be_visible()
            else:
                expect(self._shell.notification_panel).to_have_count(0)

    @keyword("verifyNotificationBadge")
    def verify_notification_badge(self, expected):
        """Kiểm tra số trên chuông (null = không hiển thị số)."""
        with self.step(f"Kiểm tra số trên chuông = {'(không có)' if expected is None else expected}"):
            if expected is None:
                expect(self._shell.bell_badge).to_have_count(0)
            else:
                expect(self._shell.bell_badge).to_have_text(expected)

    @keyword("verifyNotificationPanel")
    def verify_notification_panel(self, expected):
        """Kiểm tra panel: danh sách tiêu đề thông báo, thanh thống kê và dòng "{n} thông báo"."""
        with self.step(f"Kiểm tra panel có {len(expected['items'])} thông báo"):
            expect(self._shell.notification_items.locator("p.font-semibold")).to_have_text(expected["items"])
            expect(self._shell.notification_stats).to_have_text(expected["stats"])
            expect(self._shell.notification_footer_count).to_have_text(expected["footer"])
            expect(self._shell.view_all_orders_link).to_be_visible()

    @keyword("verifyNotificationsEmpty")
    def verify_notifications_empty(self):
        """Kiểm tra panel trống: "Không có thông báo nào" và "0 thông báo"."""
        with self.step('Kiểm tra panel "Không có thông báo nào"'):
            expect(self._shell.notification_empty).to_be_visible()
            expect(self._shell.notification_items).to_have_count(0)
            expect(self._shell.notification_footer_count).to_have_text("0 thông báo")
            expect(self._shell.notification_stats).to_have_count(0)

    @keyword("verifyNotificationVisible")
    def verify_notification_visible(self, title, visible=True):
        """Kiểm tra có/không có thông báo theo tiêu đề trong panel."""
        with self.step(f"Kiểm tra {'có' if visible else 'không có'} thông báo \"{title}\""):
            item = self._shell.notification_item(title)
            if visible:
                expect(item.first).to_be_visible()
            else:
                expect(item).to_have_count(0)

    @keyword("clickNotification")
    def click_notification(self, title):
        """Bấm 1 thông báo theo tiêu đề."""
        with self.step(f'Bấm thông báo "{title}"'):
            self._shell.notification_item(title).first.click()

    @keyword("verifyNewNotificationChip")
    def verify_new_notification_chip(self, text):
        """Kiểm tra nhãn "{n} mới" cạnh tiêu đề panel (null = không có)."""
        with self.step(f"Kiểm tra nhãn thông báo mới = {'(không có)' if text is None else text}"):
            if text is None:
                expect(self._shell.notification_new_chip).to_have_count(0)
                expect(self._shell.mark_all_read_button).to_have_count(0)
            else:
                expect(self._shell.notification_new_chip).to_have_text(text)
                expect(self._shell.mark_all_read_button).to_be_visible()

    @keyword("markAllNotificationsRead")
    def mark_all_notifications_read(self):
        """Bấm "Đánh dấu đã đọc" trong panel thông báo."""
        with self.step('Bấm "Đánh dấu đã đọc"'):
            self._shell.mark_all_read_button.click()

    @keyword("refreshNotifications")
    def refresh_notifications(self):
        """Bấm nút "Làm mới" trong panel thông báo và kiểm tra API thông báo được gọi lại."""
        with self.step('Bấm "Làm mới" thông báo'):
            before = self._requests.count("/admin/notifications")
            self._shell.refresh_button.click()
            poll_until(
                lambda: self._requests.count("/admin/notifications") > before,
                "Không gọi lại GET /admin/notifications",
            )

    @keyword("clickViewAllOrders")
    def click_view_all_orders(self):
        """Bấm "Xem tất cả đơn hàng" ở chân panel thông báo."""
        with self.step('Panel thông báo -> "Xem tất cả đơn hàng"'):
            self._shell.view_all_orders_link.click()

    # ===========================================================================
    # Dashboard
    # ===========================================================================

    @keyword("verifyStatCardLabels")
    def verify_stat_card_labels(self, labels):
        """Kiểm tra 4 thẻ thống kê hiển thị đúng nhãn (theo thứ tự)."""
        with self.step(f"Kiểm tra thẻ thống kê: {' | '.join(labels)}"):
            expect(self._dashboard.stats_grid.locator("> div p.text-sm")).to_have_text(labels)

    @keyword("verifyStatCards")
    def verify_stat_cards(self, cards):
        """Kiểm tra giá trị / dòng phụ / % thay đổi của các thẻ thống kê."""
        with self.step(f"Kiểm tra giá trị {len(cards)} thẻ thống kê"):
            for c in cards:
                expect(self._dashboard.stat_value(c["label"]), c["label"]).to_have_text(c["value"])
                if c.get("sub") is not None:
                    expect(self._dashboard.stat_sub(c["label"]), c["label"]).to_have_text(c["sub"])
                if c.get("change") is not None:
                    expect(self._dashboard.stat_change(c["label"]), c["label"]).to_have_text(c["change"])

    @keyword("verifyStatCardHasNoChange")
    def verify_stat_card_has_no_change(self, label):
        """Kiểm tra thẻ thống kê KHÔNG hiển thị huy hiệu % tăng/giảm."""
        with self.step(f'Kiểm tra thẻ "{label}" không có % tăng trưởng'):
            expect(self._dashboard.stat_value(label)).to_be_visible()
            expect(self._dashboard.stat_change(label)).to_have_count(0)

    @keyword("verifyDashboardSections")
    def verify_dashboard_sections(self, titles):
        """Kiểm tra các khối tiêu đề trên dashboard."""
        with self.step(f"Kiểm tra các khối: {' | '.join(titles)}"):
            for title in titles:
                expect(self._dashboard.section_heading(title)).to_be_visible()

    @keyword("verifyOrderStatusBreakdown")
    def verify_order_status_breakdown(self, values):
        """Kiểm tra số lượng đơn theo từng trạng thái (khối "Đơn hàng theo trạng thái")."""
        with self.step('Kiểm tra khối "Đơn hàng theo trạng thái"'):
            for label, value in values.items():
                expect(self._dashboard.status_value(label), label).to_have_text(value)

    @keyword("verifyRecentOrders")
    def verify_recent_orders(self, orders):
        """Kiểm tra danh sách "Đơn hàng gần đây" (mã, khách, tổng tiền, trạng thái)."""
        with self.step(f"Kiểm tra {len(orders)} đơn hàng gần đây"):
            rows = self._dashboard.section_rows("Đơn hàng gần đây")
            expect(rows).to_have_count(len(orders))
            for i, o in enumerate(orders):
                row = rows.nth(i)
                expect(row.locator("p").first).to_have_text(o["number"])
                expect(row).to_contain_text(o["customer"])
                expect(row).to_contain_text(o["total"])
                expect(row.locator("span.rounded-full")).to_have_text(o["status"])

    @keyword("verifyTopProducts")
    def verify_top_products(self, products):
        """Kiểm tra danh sách "Sản phẩm bán chạy" (tên + số đã bán, theo thứ tự)."""
        with self.step(f"Kiểm tra {len(products)} sản phẩm bán chạy"):
            rows = self._dashboard.section_rows("Sản phẩm bán chạy")
            expect(rows).to_have_count(len(products))
            for i, p in enumerate(products):
                expect(rows.nth(i)).to_contain_text(str(i + 1))
                expect(rows.nth(i).locator("p.truncate")).to_have_text(p["name"])
                expect(rows.nth(i)).to_contain_text(p["sold"])

    @keyword("verifyQuickCards")
    def verify_quick_cards(self, cards):
        """Kiểm tra giá trị các thẻ thao tác nhanh cuối dashboard."""
        with self.step(f"Kiểm tra {len(cards)} thẻ thao tác nhanh"):
            for c in cards:
                expect(self._dashboard.quick_card_value(c["title"]), c["title"]).to_have_text(c["value"])

    @keyword("clickDashboardLink")
    def click_dashboard_link(self, label, section=None):
        """Bấm 1 link trên dashboard; `section` dùng khi trùng tên (vd: "Xem tất cả")."""
        suffix = f" ({section})" if section else ""
        with self.step(f'Dashboard -> "{label}"{suffix}'):
            link = (
                self._dashboard.section_link(section, label)
                if section
                else self._dashboard.quick_link(label)
            )
            link.click()

    @keyword("verifyChartTicks")
    def verify_chart_ticks(self, ticks):
        """Kiểm tra nhãn trục X của biểu đồ doanh thu."""
        with self.step(f"Kiểm tra trục X biểu đồ: {', '.join(ticks)}"):
            expect(self._dashboard.chart_ticks).to_have_text(ticks)

    @keyword("verifyChartSeries")
    def verify_chart_series(self, points):
        """Kiểm tra biểu đồ vẽ vùng doanh thu + đường đơn hàng với `points` điểm dữ liệu."""
        with self.step(f"Kiểm tra biểu đồ có vùng doanh thu + đường đơn hàng ({points} điểm)"):
            expect(self._dashboard.chart_areas).to_have_count(1)
            expect(self._dashboard.chart_lines).to_have_count(1)
            expect(self._dashboard.chart_line_dots).to_have_count(points)

    @keyword("selectRevenueRange")
    def select_revenue_range(self, option):
        """Chọn khoảng thời gian cho biểu đồ doanh thu, vd: "30 ngày qua"."""
        with self.step(f'Chọn khoảng "{option}" cho biểu đồ'):
            self._dashboard.range_select.select_option(label=option)

    # ===========================================================================
    # Đơn hàng
    # ===========================================================================

    @keyword("verifyOrderStatusCards")
    def verify_order_status_cards(self, counts):
        """Kiểm tra số lượng trên 7 thẻ trạng thái đơn hàng."""
        with self.step("Kiểm tra thẻ trạng thái đơn hàng"):
            for label, count in counts.items():
                expect(self._orders.status_card_count(label), label).to_have_text(count)

    @keyword("clickOrderStatusCard")
    def click_order_status_card(self, label):
        """Bấm 1 thẻ trạng thái đơn hàng (bật/tắt lọc)."""
        with self.step(f'Bấm thẻ trạng thái "{label}"'):
            self._orders.status_card(label).click()

    @keyword("verifyOrderStatusCardActive")
    def verify_order_status_card_active(self, label, active):
        """Kiểm tra thẻ trạng thái đang được chọn (viền đỏ) hay không."""
        with self.step(f"Kiểm tra thẻ \"{label}\" {'đang chọn' if active else 'không chọn'}"):
            ring = re.compile(r"ring-2")
            if active:
                expect(self._orders.status_card(label)).to_have_class(ring)
            else:
                expect(self._orders.status_card(label)).not_to_have_class(ring)

    @keyword("searchOrders")
    def search_orders(self, text):
        """Gõ từ khóa vào ô tìm đơn hàng."""
        with self.step(f'Tìm đơn hàng "{text}"'):
            self._orders.search_input.fill(text)

    @keyword("filterOrdersByStatus")
    def filter_orders_by_status(self, value):
        """Chọn lọc trạng thái đơn (value: pending, confirmed... hoặc "" = tất cả)."""
        with self.step(f'Lọc trạng thái đơn = "{value}"'):
            self._orders.status_select.select_option(value)

    @keyword("filterOrdersByPayment")
    def filter_orders_by_payment(self, value):
        """Chọn lọc trạng thái thanh toán (value: unpaid, paid, partially_paid, refunded)."""
        with self.step(f'Lọc thanh toán = "{value}"'):
            self._orders.payment_select.select_option(value)

    @keyword("filterOrdersByDate")
    def filter_orders_by_date(self, date_from, date_to):
        """Mở "Bộ lọc" và nhập khoảng ngày (yyyy-mm-dd)."""
        with self.step(f"Lọc đơn từ {date_from} đến {date_to}"):
            if not self._orders.clear_filters_button.is_visible():
                self._orders.filters_button.click()
            self._orders.date_input("Từ ngày").fill(date_from)
            self._orders.date_input("Đến ngày").fill(date_to)

    @keyword("clearOrderFilters")
    def clear_order_filters(self):
        """Bấm "Bộ lọc" rồi "Xóa bộ lọc"."""
        with self.step("Xóa bộ lọc đơn hàng"):
            if not self._orders.clear_filters_button.is_visible():
                self._orders.filters_button.click()
            self._orders.clear_filters_button.click()

    @keyword("verifyOrderFilters")
    def verify_order_filters(self, expected):
        """Kiểm tra giá trị hiện tại của ô tìm kiếm, lọc trạng thái, lọc thanh toán."""
        with self.step(f"Kiểm tra bộ lọc đơn {_json(expected)}"):
            if expected.get("search") is not None:
                expect(self._orders.search_input).to_have_value(expected["search"])
            if expected.get("status") is not None:
                expect(self._orders.status_select).to_have_value(expected["status"])
            if expected.get("payment") is not None:
                expect(self._orders.payment_select).to_have_value(expected["payment"])

    @keyword("verifyOrderRows")
    def verify_order_rows(self, numbers):
        """Kiểm tra bảng đơn hàng hiển thị đúng các mã đơn (theo thứ tự)."""
        with self.step(f"Kiểm tra bảng đơn: {', '.join(numbers)}"):
            expect(self._orders.order_numbers).to_have_text(numbers)

    @keyword("verifyOrderRow")
    def verify_order_row(self, row):
        """Kiểm tra 1 dòng đơn hàng: khách, số sản phẩm, tổng tiền, thanh toán, trạng thái."""
        with self.step(f"Kiểm tra dòng đơn {row['number']}"):
            r = self._orders.row(row["number"])
            expect(r.locator("td").nth(1).locator("p").first).to_have_text(row["customer"])
            expect(r.locator("td").nth(3)).to_have_text(row["items"])
            expect(r.locator("td").nth(4)).to_have_text(row["total"])
            expect(self._orders.row_payment(row["number"])).to_have_text(row["payment"])
            expect(self._orders.row_status(row["number"])).to_have_text(row["status"])

    @keyword("verifyOrderRowStatus")
    def verify_order_row_status(self, number, label):
        """Kiểm tra trạng thái hiển thị trên dòng đơn hàng."""
        with self.step(f'Kiểm tra đơn {number} có trạng thái "{label}"'):
            expect(self._orders.row_status(number)).to_have_text(label)

    @keyword("verifyOrdersEmpty")
    def verify_orders_empty(self):
        """Kiểm tra bảng trống "Không có đơn hàng nào" và "0 đơn hàng"."""
        with self.step('Kiểm tra "Không có đơn hàng nào"'):
            expect(self._orders.empty_text).to_be_visible()
            expect(self._orders.total_text).to_have_text("0 đơn hàng")

    @keyword("openOrderDetail")
    def open_order_detail(self, number):
        """Bấm "Xem chi tiết" trên dòng đơn hàng và chờ modal chi tiết."""
        with self.step(f"Mở chi tiết đơn {number}"):
            self._orders.row_action(number, "Xem chi tiết").click()
            expect(self._orders.detail_heading).to_have_text(f"Chi tiết đơn hàng #{number}")

    @keyword("closeOrderDetail")
    def close_order_detail(self):
        """Đóng modal chi tiết đơn (nút X)."""
        with self.step("Đóng modal chi tiết đơn"):
            self._orders.detail_close_button.click()
            expect(self._orders.detail_modal).to_have_count(0)

    @keyword("verifyOrderDetail")
    def verify_order_detail(self, d):
        """Kiểm tra nội dung modal chi tiết đơn: người nhận, địa chỉ, thông tin, sản phẩm, tổng tiền, lịch sử."""
        with self.step(f"Kiểm tra chi tiết đơn {d['number']}"):
            m = self._orders.detail_modal
            expect(self._orders.detail_heading).to_have_text(d["heading"])
            expect(self._orders.detail_status_badge).to_have_text(d["status"])
            expect(self._orders.detail_payment_badge).to_have_text(d["payment"])
            recipient = self._orders.detail_block("Người nhận")
            expect(recipient).to_contain_text(d["recipient"])
            expect(recipient).to_contain_text(d["email"])
            expect(recipient).to_contain_text(d["phone"])
            expect(self._orders.detail_block("Địa chỉ giao hàng")).to_contain_text(d["address"])
            for label, value in d["info"].items():
                expect(self._orders.detail_info(label), label).to_have_text(value)
            expect(
                m.get_by_role("heading", name=f"Sản phẩm ({len(d['items'])})", exact=True)
            ).to_be_visible()
            expect(self._orders.detail_items).to_have_count(len(d["items"]))
            for i, item in enumerate(d["items"]):
                row = self._orders.detail_items.nth(i)
                expect(row).to_contain_text(item["name"])
                expect(row).to_contain_text(item["variant"])
                expect(row.locator("td").nth(1)).to_have_text(item["qty"])
                expect(row.locator("td").last).to_have_text(item["total"])
            for label, value in d["summary"].items():
                expect(self._orders.summary_value(label), label).to_have_text(value)
            expect(self._orders.detail_logs.locator("p.text-gray-700")).to_have_text(d["logs"])

    @keyword("verifyOrderStatusButtons")
    def verify_order_status_buttons(self, labels):
        """Kiểm tra các nút chuyển trạng thái trong modal chi tiết ([] = không có khối cập nhật trạng thái)."""
        with self.step(f"Kiểm tra nút trạng thái: {', '.join(labels) or '(không có)'}"):
            expect(self._orders.detail_heading).to_be_visible()
            if labels:
                expect(self._orders.status_buttons).to_have_text(labels)
            else:
                expect(self._orders.status_section).to_have_count(0)

    @keyword("clickOrderStatusButton")
    def click_order_status_button(self, label):
        """Bấm 1 nút chuyển trạng thái trong modal chi tiết đơn."""
        with self.step(f'Bấm nút trạng thái "{label}"'):
            self._orders.status_buttons.get_by_text(label, exact=True).click()

    @keyword("verifyOrderDetailStatus")
    def verify_order_detail_status(self, label):
        """Kiểm tra huy hiệu trạng thái trên đầu modal chi tiết."""
        with self.step(f'Kiểm tra modal chi tiết có trạng thái "{label}"'):
            expect(self._orders.detail_status_badge).to_have_text(label)

    @keyword("verifyOrderProcessingWarning")
    def verify_order_processing_warning(self, visible):
        """Kiểm tra hiện/ẩn cảnh báo "Lưu ý khi xử lý" (đơn đang giao/đã giao)."""
        with self.step(f"Kiểm tra {'có' if visible else 'không có'} \"Lưu ý khi xử lý\""):
            if visible:
                expect(self._orders.processing_warning).to_be_visible()
            else:
                expect(self._orders.processing_warning).to_have_count(0)

    @keyword("changeOrderPayment")
    def change_order_payment(self, value):
        """Chọn trạng thái thanh toán trong modal chi tiết (value: paid, unpaid, partially_paid)."""
        with self.step(f'Cập nhật thanh toán = "{value}"'):
            self._orders.detail_payment_select.select_option(value)

    @keyword("verifyOrderDetailPayment")
    def verify_order_detail_payment(self, label, editable):
        """Kiểm tra trạng thái thanh toán trên modal chi tiết và khối "Cập nhật thanh toán" có hiện không."""
        with self.step(f"Kiểm tra thanh toán \"{label}\" ({'còn' if editable else 'không còn'} cho sửa)"):
            expect(self._orders.detail_payment_badge).to_have_text(label)
            if editable:
                expect(self._orders.payment_section).to_be_visible()
            else:
                expect(self._orders.payment_section).to_have_count(0)

    @keyword("verifyOrderCancelAction")
    def verify_order_cancel_action(self, number, visible):
        """Kiểm tra dòng đơn có/không có nút "Hủy đơn"."""
        with self.step(f"Kiểm tra đơn {number} {'có' if visible else 'không có'} nút \"Hủy đơn\""):
            expect(self._orders.row_action(number, "Xem chi tiết")).to_be_visible()
            if visible:
                expect(self._orders.row_action(number, "Hủy đơn")).to_be_visible()
            else:
                expect(self._orders.row_action(number, "Hủy đơn")).to_have_count(0)

    @keyword("openCancelOrder")
    def open_cancel_order(self, number):
        """Bấm nút "Hủy đơn" trên dòng đơn hàng và chờ modal "Hủy đơn hàng"."""
        with self.step(f"Mở hủy đơn {number}"):
            self._orders.row_action(number, "Hủy đơn").click()
            expect(self._orders.cancel_modal).to_be_visible()

    @keyword("fillCancelReason")
    def fill_cancel_reason(self, reason):
        """Nhập lý do hủy đơn trong modal "Hủy đơn hàng"."""
        with self.step(f'Nhập lý do hủy "{reason}"'):
            self._orders.cancel_reason.fill(reason)

    @keyword("verifyCancelNotes")
    def verify_cancel_notes(self, notes):
        """Kiểm tra các ghi chú (hoàn tiền / hoàn điểm) trong modal hủy đơn."""
        with self.step(f"Kiểm tra ghi chú hủy đơn: {' | '.join(notes) or '(không có)'}"):
            expect(self._orders.cancel_modal).to_be_visible()
            expect(self._orders.cancel_notes).to_have_text(notes)

    # ===========================================================================
    # Phân trang (đơn hàng / khách hàng / nhân viên)
    # ===========================================================================

    @keyword("goToPage")
    def go_to_page(self, n):
        """Bấm số trang trên thanh phân trang."""
        with self.step(f"Bấm trang {n}"):
            self._orders.page_button(n).click()

    @keyword("clickNextPage")
    def click_next_page(self):
        """Bấm nút trang sau (mũi tên phải / "Sau")."""
        with self.step("Bấm trang sau"):
            self._customers.next_page_button.click()

    @keyword("verifyPaginationText")
    def verify_pagination_text(self, text):
        """Kiểm tra dòng chữ phân trang, vd: "Trang 1 / 3 — 45 đơn hàng"."""
        with self.step(f'Kiểm tra phân trang "{text}"'):
            expect(self._customers.pagination_text).to_have_text(text)

    @keyword("verifyPageButton")
    def verify_page_button(self, n, visible=True):
        """Kiểm tra có/không có nút số trang."""
        with self.step(f"Kiểm tra {'có' if visible else 'không có'} nút trang {n}"):
            if visible:
                expect(self._orders.page_button(n)).to_be_visible()
            else:
                expect(self._orders.page_button(n)).to_have_count(0)

    # ===========================================================================
    # Khách hàng / Nhân viên
    # ===========================================================================

    @keyword("verifyFieldErrors")
    def verify_field_errors(self, heading, errors):
        """Kiểm tra danh sách lỗi dưới ô nhập trong modal có tiêu đề `heading` (đúng thứ tự, [] = không lỗi)."""
        with self.step(f"Kiểm tra lỗi form \"{heading}\": {' | '.join(errors) or '(không có)'}"):
            expect(self._customers.modal(heading)).to_be_visible()
            expect(self._customers.field_errors(heading)).to_have_text(errors)

    @keyword("verifyModalText")
    def verify_modal_text(self, heading, text):
        """Kiểm tra modal có tiêu đề `heading` chứa đoạn chữ."""
        with self.step(f'Kiểm tra modal "{heading}" có "{text}"'):
            expect(self._customers.modal(heading).get_by_text(text, exact=True)).to_be_visible()

    @keyword("verifyFieldPlaceholder")
    def verify_field_placeholder(self, label, placeholder):
        """Kiểm tra placeholder của ô nhập theo label."""
        with self.step(f'Kiểm tra ô "{label}" có placeholder "{placeholder}"'):
            expect(self.po.admin_ui.field(label)).to_have_attribute("placeholder", placeholder)

    @keyword("verifyCustomerRow")
    def verify_customer_row(self, row):
        """Kiểm tra dòng khách hàng: trạng thái, tổng chi tiêu, điểm."""
        with self.step(f'Kiểm tra dòng khách "{row["name"]}"'):
            expect(self._customers.status_badge(row["name"])).to_have_text(row["status"])
            if row.get("spent"):
                expect(self._customers.cell(row["name"], 3)).to_have_text(row["spent"])
            if row.get("points"):
                expect(self._customers.cell(row["name"], 4)).to_have_text(row["points"])

    @keyword("verifyCustomerDetail")
    def verify_customer_detail(self, d):
        """Kiểm tra modal "Chi tiết khách hàng": tên, email, số liệu, thông tin, đơn gần đây."""
        with self.step(f'Kiểm tra chi tiết khách "{d["name"]}"'):
            m = self._customers.modal("Chi tiết khách hàng")
            expect(m.locator("p.font-bold").first).to_have_text(d["name"])
            expect(m.get_by_text(d["email"], exact=True)).to_be_visible()
            for label, value in d["stats"].items():
                expect(self._customers.detail_stat(label), label).to_have_text(value)
            for label, value in d["values"].items():
                expect(self._customers.detail_value(label), label).to_have_text(value)
            expect(
                self._customers.detail_recent_orders.locator("p.font-medium.text-gray-800")
            ).to_have_text(d["recentOrders"])

    @keyword("verifyCustomerRecentOrderStatuses")
    def verify_customer_recent_order_statuses(self, labels):
        """Kiểm tra nhãn trạng thái của các đơn gần đây trong modal "Chi tiết khách hàng" (đúng thứ tự)."""
        with self.step(f"Kiểm tra trạng thái đơn gần đây: {', '.join(labels)}"):
            expect(self._customers.detail_recent_orders.locator("p.text-xs.font-medium")).to_have_text(labels)

    @keyword("verifyCustomerDeleteWarning")
    def verify_customer_delete_warning(self, text):
        """Kiểm tra cảnh báo "khách đã có đơn -> khóa thay vì xóa" trong modal xóa (null = không có)."""
        with self.step(f"Kiểm tra cảnh báo xóa khách = {'(không có)' if text is None else text}"):
            expect(self._customers.modal("Xác nhận xóa")).to_be_visible()
            if text is None:
                expect(self._customers.delete_warning).to_have_count(0)
            else:
                expect(self._customers.delete_warning).to_have_text(text)

    @keyword("verifyPersonRow")
    def verify_person_row(self, name, visible=True):
        """Kiểm tra có/không có dòng (khách hàng / nhân viên) theo tên chính xác."""
        with self.step(f"Kiểm tra {'có' if visible else 'không có'} dòng \"{name}\""):
            if visible:
                expect(self._customers.row(name)).to_be_visible()
            else:
                expect(self._customers.rows(name)).to_have_count(0)

    @keyword("verifyEmployeesHeading")
    def verify_employees_heading(self, text):
        """Kiểm tra tiêu đề "Tài khoản nhân viên" trên trang nhân viên."""
        with self.step(f'Kiểm tra tiêu đề "{text}"'):
            expect(self.page.get_by_role("heading", name=text, exact=True)).to_be_visible()

    @keyword("verifyEmployeeRole")
    def verify_employee_role(self, name, label):
        """Kiểm tra nhãn vai trò của nhân viên."""
        with self.step(f'Kiểm tra "{name}" có vai trò "{label}"'):
            expect(self._employees.role_badge(name)).to_have_text(label)

    @keyword("clickEmployeeAction")
    def click_employee_action(self, name, action):
        """Bấm nút trên dòng nhân viên: "Sửa", "Xóa" (icon không title) hoặc "Trạng thái" (nút gạt)."""
        with self.step(f'Nhân viên "{name}" -> {action}'):
            if action == "Sửa":
                button = self._employees.edit_button(name)
            elif action == "Xóa":
                button = self._employees.delete_button(name)
            else:
                button = self._employees.toggle_button(name)
            button.click()

    @keyword("verifyEmployeeActive")
    def verify_employee_active(self, name, active):
        """Kiểm tra nút gạt trạng thái nhân viên đang bật (xanh) hay tắt (xám)."""
        with self.step(f"Kiểm tra \"{name}\" {'đang hoạt động' if active else 'bị vô hiệu'}"):
            expect(self._employees.toggle_button(name)).to_have_class(
                re.compile(r"text-green-500" if active else r"text-gray-300")
            )

    @keyword("verifyEmployeeEmailNativeInvalid")
    def verify_employee_email_native_invalid(self, editing=False):
        """Kiểm tra ô Email trong form nhân viên bị trình duyệt đánh dấu không hợp lệ (chặn submit)."""
        with self.step("Kiểm tra ô Email bị trình duyệt chặn (type=email)"):
            email_input = self._employees.email_input(editing)
            valid = email_input.evaluate("(el) => el.validity.valid")
            assert valid is False, f"validity.valid: expected=False, actual={valid!r}"
            message = email_input.evaluate("(el) => el.validationMessage")
            assert message != "", f"validationMessage: expected khác rỗng, actual={message!r}"
