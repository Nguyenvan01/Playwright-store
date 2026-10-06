# Trang Tổng quan (/admin): thẻ thống kê, biểu đồ, đơn gần đây, sản phẩm bán chạy, thẻ thao tác nhanh.

CHART_SECTION = "Doanh thu & Đơn hàng"


class DashboardPage:
    path = "/admin"

    def __init__(self, page):
        self.page = page
        # Lưới 4 thẻ thống kê đầu trang.
        self.stats_grid = page.locator("main div.grid").first

    def stat_card(self, label):
        return self.stats_grid.locator("> div").filter(has=self.page.get_by_text(label, exact=True))

    def stat_value(self, label):
        return self.stat_card(label).locator("p.text-2xl")

    def stat_change(self, label):
        """Huy hiệu % tăng/giảm trên thẻ thống kê."""
        return self.stat_card(label).locator("div.rounded-full")

    def stat_sub(self, label):
        return self.stat_card(label).locator("p.text-xs")

    def section(self, title):
        """Khối nội dung có tiêu đề h3."""
        return (
            self.page.locator("main div.rounded-xl")
            .filter(has=self.page.get_by_role("heading", name=title, exact=True))
            .first
        )

    def section_heading(self, title):
        return self.page.get_by_role("heading", name=title, exact=True)

    def status_value(self, label):
        """Giá trị của 1 trạng thái trong khối "Đơn hàng theo trạng thái"."""
        return (
            self.section("Đơn hàng theo trạng thái")
            .locator("div.flex.justify-between")
            .filter(has=self.page.get_by_text(label, exact=True))
            .locator("span")
            .last
        )

    def section_rows(self, title):
        """Các dòng trong khối danh sách (đơn gần đây / sản phẩm bán chạy)."""
        return self.section(title).locator("div.divide-y > div")

    def section_link(self, title, label):
        return self.section(title).get_by_role("link", name=label, exact=True)

    def quick_card(self, title):
        """Thẻ thao tác nhanh cuối trang, vd: "Đơn hàng chờ xử lý"."""
        return self.page.locator("main div.group.rounded-xl").filter(
            has=self.page.get_by_text(title, exact=True)
        )

    def quick_card_value(self, title):
        return self.quick_card(title).locator("p.text-2xl")

    def quick_link(self, label):
        return self.page.locator("main div.group.rounded-xl").get_by_role("link", name=label, exact=True)

    @property
    def range_select(self):
        return self.section(CHART_SECTION).locator("select")

    @property
    def chart_ticks(self):
        return self.section(CHART_SECTION).locator(
            ".recharts-xAxis-tick-labels .recharts-cartesian-axis-tick-value"
        )

    @property
    def chart_lines(self):
        return self.section(CHART_SECTION).locator("g.recharts-line")

    @property
    def chart_areas(self):
        return self.section(CHART_SECTION).locator("g.recharts-area")

    @property
    def chart_line_dots(self):
        return self.section(CHART_SECTION).locator("circle.recharts-line-dot")
