# Trang quản trị Kho hàng (/admin/warehouse).
import re

from pages.admin.marketing.admin_table import AdminTable


class WarehousePage(AdminTable):
    path = "/admin/warehouse"
    search_placeholder = "Tìm kiếm sản phẩm, SKU, danh mục..."

    def tab(self, label):
        """Nút tab lọc ("Tất cả", "Sắp hết", "Hết hàng") - tên nút có kèm số đếm."""
        return self.page.get_by_role("button", name=re.compile(rf"^{label}(\s+\d+)?$"))

    def tab_badge(self, label):
        """Số đếm (badge) trên tab."""
        return self.tab(label).locator("span")

    @property
    def empty_text(self):
        return self.page.get_by_text("Không tìm thấy sản phẩm phù hợp.", exact=True)

    @property
    def list_ready(self):
        """Hết skeleton: có tên sản phẩm hoặc dòng rỗng."""
        return self.table.locator("tbody tr td p, tbody tr td[colspan]").first
