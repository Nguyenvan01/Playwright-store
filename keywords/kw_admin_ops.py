# THƯ VIỆN KEYWORD - NHÓM adminOps: quản trị vận hành (kho hàng, nhập hàng, báo cáo, cài đặt).
import json
import re
from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse

from playwright.sync_api import expect

from keywords.base_keywords import BaseKeywords, keyword
from pages.admin.marketing.admin_table import AdminTable
from pages.admin.ops.import_page import ImportPage
from pages.admin.ops.reports_page import ReportsPage
from pages.admin.ops.settings_page import SettingsPage
from pages.admin.ops.warehouse_page import WarehousePage
from pages.admin.sales.admin_api_mock import query_of_url
from utils.assertions import poll_until


def vn_today():
    """Ngày YYYY-MM-DD theo giờ Việt Nam (UTC+7)."""
    return (datetime.now(timezone.utc) + timedelta(hours=7)).strftime("%Y-%m-%d")


class AdminOpsKeywords(BaseKeywords):
    group = "adminOps"

    def __init__(self, page, po, api, common=None):
        super().__init__(page, po, api, common)
        self.table = AdminTable(page)
        self.warehouse = WarehousePage(page)
        self.imports = ImportPage(page)
        self.reports = ReportsPage(page)
        self.settings = SettingsPage(page)
        # URL các request GET đã đi qua API giả lập (để kiểm tra tham số lọc).
        self.list_queries = []

    def _fake_get(self, url_glob, json_factory):
        """Giả lập API GET: trả json theo query string và ghi lại URL đã gọi."""

        def handle(route):
            request = route.request
            if request.method != "GET":
                return route.fallback()
            url = request.url
            self.list_queries.append(url)
            body = json_factory(query_of_url(url), urlparse(url))
            if body is None:
                route.fulfill(status=404, json={"success": False})
            else:
                route.fulfill(status=200, json=body)

        self.page.route(url_glob, handle)

    # ---------------------------------------------------------------------------
    # Dùng chung cho các trang vận hành
    # ---------------------------------------------------------------------------

    @keyword("verifyColumns")
    def verify_columns(self, headers):
        """Kiểm tra bảng chính có đúng các cột theo thứ tự (đọc textContent, bỏ qua CSS viết hoa)."""
        with self.step(f"Kiểm tra cột: {' | '.join(headers)}"):
            expect(self.table.header_cells.first).to_be_visible()
            actual = self.table.header_texts()
            assert actual == headers, f"Cột bảng: expected={headers!r}, actual={actual!r}"

    @keyword("verifyRowCells")
    def verify_row_cells(self, row_text, cells):
        """Kiểm tra các ô của dòng chứa text theo tên cột, vd: {"Tồn kho": "3"}."""
        with self.step(f'Kiểm tra dòng "{row_text}": {json.dumps(cells, ensure_ascii=False)}'):
            expect(self.table.row(row_text)).to_be_visible()
            for header, value in cells.items():
                cell = self.table.cell(row_text, header)
                if value == "":
                    expect(cell).to_have_text("")
                else:
                    expect(cell).to_contain_text(value)

    @keyword("verifyRowCount")
    def verify_row_count(self, count):
        """Kiểm tra số dòng dữ liệu đang hiển thị trong bảng chính."""
        with self.step(f"Kiểm tra bảng có {count} dòng"):
            expect(self.table.rows).to_have_count(count)

    @keyword("verifyRowsAtLeast")
    def verify_rows_at_least(self, minimum):
        """Kiểm tra bảng có ít nhất `min` dòng dữ liệu thật (không phải dòng trạng thái rỗng)."""
        with self.step(f"Kiểm tra bảng có ít nhất {minimum} dòng"):
            expect(self.table.rows.first).to_be_visible()
            expect(self.table.rows.locator("td[colspan]")).to_have_count(0)
            count = self.table.rows.count()
            assert count >= minimum, f"Số dòng: expected>={minimum}, actual={count}"

    @keyword("verifyRowActions")
    def verify_row_actions(self, row_text, titles):
        """Kiểm tra dòng chứa text có đúng các nút hành động (theo title, đúng thứ tự)."""
        with self.step(f"Kiểm tra nút trên dòng \"{row_text}\": {', '.join(titles)}"):
            buttons = self.table.titled_buttons(row_text)
            expect(buttons).to_have_count(len(titles))
            actual = buttons.evaluate_all("els => els.map((e) => e.getAttribute('title'))")
            assert actual == titles, f"Nút trên dòng {row_text!r}: expected={titles!r}, actual={actual!r}"

    @keyword("verifyVisibleRows")
    def verify_visible_rows(self, visible, hidden=None):
        """Kiểm tra các dòng hiển thị/không hiển thị sau khi tìm kiếm hoặc lọc."""
        hidden = hidden or []
        with self.step(f"Kiểm tra hiển thị [{', '.join(visible)}], ẩn [{', '.join(hidden)}]"):
            for text in visible:
                expect(self.table.ui.row(text).first).to_be_visible()
            for text in hidden:
                expect(self.table.ui.row(text)).to_have_count(0)

    @keyword("verifyModalText")
    def verify_modal_text(self, heading, texts):
        """Kiểm tra modal có tiêu đề `heading` đang mở và chứa các đoạn text."""
        with self.step(f"Kiểm tra modal \"{heading}\" chứa: {' | '.join(texts)}"):
            modal = self.table.modal(heading)
            expect(modal).to_be_visible()
            for text in texts:
                expect(modal).to_contain_text(text)

    @keyword("clickModalButton")
    def click_modal_button(self, heading, name):
        """Bấm nút theo tên bên trong modal có tiêu đề `heading`."""
        with self.step(f'Modal "{heading}" -> bấm "{name}"'):
            self.table.modal_button(heading, name).click()

    @keyword("verifyStatCards")
    def verify_stat_cards(self, cards):
        """Kiểm tra các thẻ thống kê (nhãn -> giá trị), vd: {"Tổng đơn": "3"}."""
        with self.step(f"Kiểm tra thẻ thống kê {json.dumps(cards, ensure_ascii=False)}"):
            for label, value in cards.items():
                expect(self.table.stat_value(label)).to_have_text(value)

    @keyword("verifyListQuery")
    def verify_list_query(self, path_part, params):
        """Kiểm tra request GET gần nhất (qua API giả lập) có các tham số; null = không gửi tham số đó."""
        with self.step(f"Kiểm tra GET {path_part} có {json.dumps(params, ensure_ascii=False)}"):

            def last_query():
                last = next(
                    (u for u in reversed(self.list_queries) if path_part in urlparse(u).path), None
                )
                if last is None:
                    return "chưa có request"
                query = query_of_url(last)
                return {key: query.get(key) for key in params}

            try:
                poll_until(lambda: last_query() == params, "")
            except AssertionError:
                raise AssertionError(
                    f"GET {path_part}: expected={params!r}, actual={last_query()!r}"
                ) from None

    # ---------------------------------------------------------------------------
    # Kho hàng
    # ---------------------------------------------------------------------------

    @keyword("mockWarehouse")
    def mock_warehouse(self, data):
        """Giả lập API kho hàng: lọc sản phẩm theo tham số filter (all, low, out) như server."""
        with self.step(f"Mock kho hàng {len(data['products'])} sản phẩm"):

            def respond(q, _url):
                selected = q.get("filter")
                if selected == "low":
                    products = [p for p in data["products"] if 0 < p["stock"] <= 5]
                elif selected == "out":
                    products = [p for p in data["products"] if p["stock"] == 0]
                else:
                    products = list(data["products"])
                return {"stats": data["stats"], "products": products}

            self._fake_get("**/api/admin/warehouse*", respond)

    @keyword("openWarehouse")
    def open_warehouse(self):
        """Mở trang Kho hàng và chờ bảng tải xong."""
        with self.step("Mở trang Kho hàng"):
            self.page.goto(self.warehouse.path)
            expect(self.po.admin_ui.page_title).to_have_text("Kho hàng")
            expect(self.warehouse.list_ready).to_be_visible()

    @keyword("selectWarehouseTab")
    def select_warehouse_tab(self, label):
        """Bấm tab lọc kho ("Tất cả", "Sắp hết", "Hết hàng") và chờ bảng tải lại."""
        with self.step(f'Chọn tab kho "{label}"'):
            self.warehouse.tab(label).click()
            expect(self.warehouse.tab(label)).to_have_class(re.compile(r"bg-red-600"))
            expect(self.warehouse.list_ready).to_be_visible()

    @keyword("verifyWarehouseTabBadge")
    def verify_warehouse_tab_badge(self, label, count):
        """Kiểm tra số đếm trên tab kho; null = không hiển thị số."""
        with self.step(f"Kiểm tra tab \"{label}\" có số {'(không có)' if count is None else count}"):
            if count is None:
                expect(self.warehouse.tab_badge(label)).to_have_count(0)
            else:
                expect(self.warehouse.tab_badge(label)).to_have_text(str(count))

    @keyword("verifyWarehouseStatsMatchList")
    def verify_warehouse_stats_match_list(self):
        """Kiểm tra thẻ "Tổng sản phẩm" bằng số dòng của tab "Tất cả" (dữ liệu thật)."""
        with self.step('Kiểm tra "Tổng sản phẩm" khớp số dòng trong bảng'):
            expect(self.table.rows.first).to_be_visible()
            rows = self.table.rows.count()
            expect(self.table.stat_value("Tổng sản phẩm")).to_have_text(str(rows))

    # ---------------------------------------------------------------------------
    # Nhập hàng
    # ---------------------------------------------------------------------------

    @keyword("mockImportData")
    def mock_import_data(self, data):
        """Giả lập toàn bộ API GET của trang Nhập hàng (đơn nhập lọc theo status/supplier_id/search, NCC, kho, sản phẩm, chi tiết)."""
        with self.step(f"Mock trang Nhập hàng ({len(data['imports'])} đơn)"):

            def list_imports(q, _url):
                search = (q.get("search") or "").lower()
                found = [
                    i
                    for i in data["imports"]
                    if (not q.get("status") or i["status"] == q.get("status"))
                    and (not q.get("supplier_id") or str(i["supplier_id"]) == q.get("supplier_id"))
                    and (
                        not search
                        or search in i["code"].lower()
                        or search in i["supplier_name"].lower()
                    )
                ]
                return {"success": True, "imports": found, "orders": found}

            def import_detail(_q, url):
                last = url.path.split("/")[-1]
                found = next((i for i in data["imports"] if str(i["id"]) == last), None)
                return {"success": True, "import": found, "order": found} if found else None

            self._fake_get("**/api/admin/imports*", list_imports)
            self._fake_get("**/api/admin/imports/*", import_detail)
            self._fake_get("**/api/admin/suppliers", lambda q, u: {"success": True, "suppliers": data["suppliers"]})
            self._fake_get("**/api/admin/warehouses", lambda q, u: {"success": True, "warehouses": data["warehouses"]})
            self._fake_get("**/api/admin/products/options", lambda q, u: {"success": True, "products": data["products"]})

    @keyword("openImport")
    def open_import(self):
        """Mở trang Nhập hàng và chờ bảng tải xong."""
        with self.step("Mở trang Nhập hàng"):
            self.page.goto(self.imports.path)
            expect(self.po.admin_ui.page_title).to_have_text("Nhập hàng")
            expect(self.imports.page_heading).to_have_text("Nhập hàng")
            expect(self.imports.list_ready).to_be_visible()

    @keyword("filterImportStatus")
    def filter_import_status(self, value):
        """Lọc đơn nhập theo trạng thái (draft, processing, partial_received, received, cancelled; rỗng = tất cả)."""
        with self.step(f'Lọc đơn nhập theo trạng thái "{value}"'):
            self.imports.status_filter.select_option(value)

    @keyword("filterImportSupplier")
    def filter_import_supplier(self, name):
        """Lọc đơn nhập theo tên nhà cung cấp (rỗng = tất cả)."""
        with self.step(f'Lọc đơn nhập theo NCC "{name}"'):
            if name:
                self.imports.supplier_filter.select_option(label=name)
            else:
                self.imports.supplier_filter.select_option(value="")

    @keyword("openCreateImport")
    def open_create_import(self):
        """Bấm "Tạo đơn nhập hàng" và chờ modal tạo đơn."""
        with self.step('Mở form "Tạo đơn nhập hàng"'):
            self.imports.create_button.click()
            expect(self.imports.create_modal).to_be_visible()
            expect(self.imports.item_product(0).locator("option")).not_to_have_count(1)

    @keyword("addImportItemRow")
    def add_import_item_row(self):
        """Bấm "Thêm sản phẩm" để thêm 1 dòng sản phẩm nhập."""
        with self.step("Thêm dòng sản phẩm nhập"):
            rows = self.imports.create_modal.locator("table tbody tr")
            before = rows.count()
            self.imports.create_modal.get_by_role("button", name="Thêm sản phẩm", exact=True).click()
            expect(rows).to_have_count(before + 1)

    @keyword("fillImportItem")
    def fill_import_item(self, index, item):
        """Điền dòng sản phẩm nhập thứ `index` (0 = dòng đầu): sản phẩm, biến thể, số lượng, đơn giá, ghi chú."""
        with self.step(f"Điền dòng sản phẩm nhập #{index + 1}: {json.dumps(item, ensure_ascii=False)}"):
            if "product" in item:
                self.imports.item_product(index).select_option(label=item["product"])
            if "variant" in item:
                self.imports.item_variant(index).select_option(label=item["variant"])
            if "quantity" in item:
                self.imports.item_input(index, 1).fill(str(item["quantity"]))
            if "unitCost" in item:
                self.imports.item_input(index, 2).fill(str(item["unitCost"]))
            if "note" in item:
                self.imports.item_input(index, 3).fill(item["note"])

    @keyword("verifyImportTotals")
    def verify_import_totals(self, index, line_total, grand_total):
        """Kiểm tra thành tiền dòng `index` và "Tổng tiền nhập" trong modal tạo đơn."""
        with self.step(f"Kiểm tra thành tiền {line_total}, tổng tiền nhập {grand_total}"):
            expect(self.imports.item_line_total(index)).to_have_text(line_total)
            expect(self.imports.grand_total).to_have_text(grand_total)

    @keyword("setReceiveQuantities")
    def set_receive_quantities(self, quantities):
        """Nhập "SL thực nhận" cho từng dòng trong modal Nhận hàng."""
        with self.step(f"Nhập SL thực nhận: {', '.join(str(q) for q in quantities)}"):
            for i, qty in enumerate(quantities):
                self.imports.receive_input(i).fill(str(qty))

    # ---------------------------------------------------------------------------
    # Báo cáo
    # ---------------------------------------------------------------------------

    @keyword("mockReportsOverview")
    def mock_reports_overview(self, overview):
        """Giả lập API tổng quan báo cáo (ghi lại tham số period/start_date/end_date)."""
        with self.step("Mock API báo cáo tổng quan"):
            self._fake_get("**/api/admin/reports/overview*", lambda q, u: {"success": True, "overview": overview})

    @keyword("openReports")
    def open_reports(self):
        """Mở trang Báo cáo và chờ thẻ tổng quan tải xong."""
        with self.step("Mở trang Báo cáo"):
            self.page.goto(self.reports.path)
            expect(self.po.admin_ui.page_title).to_have_text("Báo cáo")
            expect(self.reports.page_heading).to_have_text("Báo cáo")
            expect(self.table.stat_value("Doanh thu")).to_be_visible()

    @keyword("selectReportPeriod")
    def select_report_period(self, value):
        """Chọn kỳ báo cáo theo value (today, last7days, last30days, thisMonth, custom)."""
        with self.step(f'Chọn kỳ báo cáo "{value}"'):
            self.reports.period_select.select_option(value)

    @keyword("applyCustomRange")
    def apply_custom_range(self, start, end):
        """Ở kỳ "Tùy chọn": nhập từ ngày, đến ngày (YYYY-MM-DD) và bấm "Lọc"."""
        with self.step(f"Lọc báo cáo từ {start} đến {end}"):
            self.reports.date_inputs.nth(0).fill(start)
            self.reports.date_inputs.nth(1).fill(end)
            self.reports.filter_button.click()

    @keyword("verifyCustomRangeDefaults")
    def verify_custom_range_defaults(self):
        """Kiểm tra kỳ "Tùy chọn" mặc định: từ ngày 1 tháng này đến hôm nay (giờ VN)."""
        with self.step('Kiểm tra khoảng ngày mặc định của kỳ "Tùy chọn"'):
            today = vn_today()
            expect(self.reports.filter_button).to_be_visible()
            expect(self.reports.date_inputs.nth(1)).to_have_value(today)
            expect(self.reports.date_inputs.nth(0)).to_have_value(f"{today[:8]}01")

    @keyword("verifyReportSection")
    def verify_report_section(self, heading, rows, first_row):
        """Kiểm tra bảng trong khối báo cáo có số dòng và dòng đầu chứa các text."""
        with self.step(f'Kiểm tra khối "{heading}" có {rows} dòng'):
            expect(self.reports.section_rows(heading)).to_have_count(rows)
            for text in first_row:
                expect(self.reports.section_rows(heading).first).to_contain_text(text)

    @keyword("verifyReportSectionText")
    def verify_report_section_text(self, heading, texts):
        """Kiểm tra khối báo cáo (theo tiêu đề h2) chứa các đoạn text."""
        with self.step(f"Kiểm tra khối \"{heading}\" chứa: {' | '.join(texts)}"):
            for text in texts:
                expect(self.reports.section(heading)).to_contain_text(text)

    @keyword("exportReport")
    def export_report(self, file_pattern, lines):
        """Bấm "Xuất báo cáo", kiểm tra tên file CSV (regex), BOM UTF-8 và các dòng nội dung."""
        with self.step(f"Xuất báo cáo CSV /{file_pattern}/"):
            with self.page.expect_download() as info:
                self.reports.export_button.click()
            download = info.value
            name = download.suggested_filename
            assert re.search(file_pattern, name), f"Tên file CSV: expected=/{file_pattern}/, actual={name!r}"
            with open(download.path(), encoding="utf-8") as file:
                content = file.read()
            first = ord(content[0]) if content else None
            assert first == 0xFEFF, f"File CSV thiếu BOM UTF-8: expected=0xfeff, actual={first!r}"
            for line in lines:
                assert line in content, f"File CSV thiếu dòng: expected={line!r}"

    # ---------------------------------------------------------------------------
    # Cài đặt
    # ---------------------------------------------------------------------------

    @keyword("mockSettings")
    def mock_settings(self, settings):
        """Giả lập API GET cài đặt website."""
        with self.step("Mock API GET cài đặt"):
            self._fake_get("**/api/admin/settings", lambda q, u: {"success": True, "settings": settings})

    @keyword("openSettings")
    def open_settings(self):
        """Mở trang Cài đặt và chờ dữ liệu tải xong."""
        with self.step("Mở trang Cài đặt"):
            self.page.goto(self.settings.path)
            expect(self.po.admin_ui.page_title).to_have_text("Cài đặt")
            expect(self.settings.page_heading).to_have_text("Cài đặt")
            expect(self.settings.panel_ready).to_be_visible()

    @keyword("openSettingsTab")
    def open_settings_tab(self, label):
        """Bấm 1 tab cài đặt, vd: "Bán hàng"."""
        with self.step(f'Mở tab cài đặt "{label}"'):
            self.settings.tab(label).click()
            expect(self.settings.panel).to_contain_text(label)

    @keyword("verifySettingsFields")
    def verify_settings_fields(self, labels):
        """Kiểm tra tab đang mở có đúng các nhãn ô nhập (theo thứ tự)."""
        with self.step(f"Kiểm tra ô nhập: {' | '.join(labels)}"):
            expect(self.settings.field_labels).to_have_count(len(labels))
            actual = [t.strip() for t in self.settings.field_labels.all_text_contents()]
            assert actual == labels, f"Nhãn ô nhập: expected={labels!r}, actual={actual!r}"

    @keyword("verifyCheckboxes")
    def verify_checkboxes(self, states):
        """Kiểm tra trạng thái các checkbox theo nhãn, vd: {"Cho phép COD": true}."""
        with self.step(f"Kiểm tra checkbox {json.dumps(states, ensure_ascii=False)}"):
            for label, checked in states.items():
                if checked:
                    expect(self.po.admin_ui.checkbox(label)).to_be_checked()
                else:
                    expect(self.po.admin_ui.checkbox(label)).not_to_be_checked()

    @keyword("saveSettings")
    def save_settings(self):
        """Bấm "Lưu cài đặt"."""
        with self.step('Bấm "Lưu cài đặt"'):
            self.settings.save_button.click()
