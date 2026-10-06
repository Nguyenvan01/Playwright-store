# Trang quản trị Nhập hàng (/admin/import).
from pages.admin.marketing.admin_table import AdminTable


class ImportPage(AdminTable):
    path = "/admin/import"
    search_placeholder = "Tìm mã đơn, nhà cung cấp..."
    create_heading = "Tạo đơn nhập hàng"

    @property
    def page_heading(self):
        return self.page.locator("main h2").first

    @property
    def create_button(self):
        return self.page.get_by_role("button", name="Tạo đơn nhập hàng", exact=True).first

    @property
    def status_filter(self):
        return self.select_with_option("partial_received")

    @property
    def supplier_filter(self):
        """Select nhà cung cấp ở thanh lọc (option đầu "Tất cả NCC")."""
        return self.page.locator("select").filter(has_text="Tất cả NCC").first

    @property
    def create_modal(self):
        return self.modal(self.create_heading)

    def item_row(self, index):
        """Dòng sản phẩm thứ `index` trong bảng sản phẩm nhập của modal tạo đơn."""
        return self.create_modal.locator("table tbody tr").nth(index)

    def item_product(self, index):
        return self.item_row(index).locator("select").nth(0)

    def item_variant(self, index):
        return self.item_row(index).locator("select").nth(1)

    def item_input(self, index, position):
        """Các ô input của dòng: 0 = SKU, 1 = Số lượng, 2 = Đơn giá, 3 = Ghi chú."""
        return self.item_row(index).locator("input").nth(position)

    def item_line_total(self, index):
        """Thành tiền của dòng sản phẩm nhập."""
        return self.item_row(index).locator("td").nth(5)

    @property
    def grand_total(self):
        """Giá trị "Tổng tiền nhập" trong modal tạo đơn."""
        return self.create_modal.get_by_text("Tổng tiền nhập", exact=True).locator(
            "xpath=following-sibling::span[1]"
        )

    def receive_input(self, index):
        """Ô "SL thực nhận" của dòng thứ `index` trong modal Nhận hàng."""
        return self.modal("Nhận hàng").locator("table tbody tr").nth(index).locator("input")

    @property
    def list_ready(self):
        return self.table.locator("tbody tr td span, tbody tr td[colspan]").first
