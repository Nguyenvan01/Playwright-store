# ============================================================
# Trang danh sách sản phẩm (/admin/products).
# Cột: 0 checkbox, 1 Sản phẩm, 2 SKU, 3 Danh mục, 4 Giá, 5 Tồn kho, 6 Đã bán, 7 Nổi bật, 8 Trạng thái, 9 Thao tác.
# ============================================================
import re

from pages.admin.sales.admin_api_mock import modal_by_heading, pagination_bar


class ProductsListPage:
    path = "/admin/products"

    def __init__(self, page):
        self.page = page
        self.search_input = page.get_by_placeholder("Tìm kiếm sản phẩm, SKU...", exact=True)
        self.category_select = page.locator("select").filter(
            has=page.locator("option", has_text="Tất cả danh mục")
        )
        self.brand_select = page.locator("select").filter(
            has=page.locator("option", has_text="Tất cả thương hiệu")
        )
        self.add_link = page.get_by_role("link", name="Thêm sản phẩm", exact=True)
        # Dòng dữ liệu thật (có checkbox) - bỏ qua dòng skeleton lúc đang tải
        self.data_rows = page.locator("tbody tr").filter(has=page.get_by_role("checkbox"))
        self.header_checkbox = page.locator("thead").get_by_role("checkbox")
        self.bulk_bar_text = page.get_by_text(re.compile(r"^\d+ sản phẩm được chọn$"))
        self.bulk_delete_button = page.get_by_role("button", name="Xóa đã chọn", exact=True)
        self.pagination_text = page.get_by_text(re.compile(r"^Trang \d+ trên \d+$"))
        self.delete_modal = modal_by_heading(page, "Xóa sản phẩm?")

    def row(self, name):
        return self.rows(name).first

    def rows(self, name):
        return self.page.locator("tbody tr").filter(has=self.page.get_by_text(name, exact=True))

    def cell(self, name, index):
        return self.row(name).locator("td").nth(index)

    def row_checkbox(self, name):
        return self.row(name).get_by_role("checkbox")

    def featured_button(self, name):
        """Nút ngôi sao (title "Đánh dấu nổi bật" / "Bỏ nổi bật")."""
        return self.cell(name, 7).get_by_role("button")

    def status_button(self, name):
        """Nút gạt trạng thái bán (không có title/tên)."""
        return self.cell(name, 8).get_by_role("button")

    def action(self, name, title):
        """title: "Xem" | "Sửa" | "Xóa"."""
        return self.cell(name, 9).get_by_title(title, exact=True)

    @property
    def pagination(self):
        return pagination_bar(self.page)

    def page_button(self, n):
        return self.pagination.get_by_role("button", name=str(n), exact=True)

    @property
    def next_page_button(self):
        return self.pagination.get_by_role("button").last
