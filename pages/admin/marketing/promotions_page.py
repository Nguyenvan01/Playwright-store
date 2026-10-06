# Trang quản trị Khuyến mãi (/admin/promotions) - có cả bảng desktop và thẻ mobile trong DOM.
from pages.admin.marketing.admin_table import AdminTable


class PromotionsPage(AdminTable):
    path = "/admin/promotions"
    search_placeholder = "Tìm theo tên, mô tả hoặc trạng thái"

    @property
    def list_heading(self):
        return self.page.get_by_role("heading", name="Danh sách khuyến mãi", exact=True)

    @property
    def add_button(self):
        """Nút "Thêm khuyến mãi" trên đầu trang (không phải nút trong trạng thái rỗng)."""
        return self.page.get_by_role("button", name="Thêm khuyến mãi", exact=True).first

    @property
    def list_ready(self):
        """Khung danh sách đã tải xong (bảng, trạng thái rỗng hoặc không tìm thấy)."""
        return (
            self.table.or_(self.page.get_by_role("heading", name="Chưa có khuyến mãi nào"))
            .or_(self.page.get_by_role("heading", name="Không tìm thấy khuyến mãi phù hợp."))
            .first
        )
