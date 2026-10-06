# Trang quản trị Đánh giá (/admin/reviews).
from pages.admin.marketing.admin_table import AdminTable


class ReviewsPage(AdminTable):
    path = "/admin/reviews"
    search_placeholder = "Tìm khách hàng, sản phẩm, nội dung..."

    @property
    def page_heading(self):
        """Tiêu đề riêng của trang (h1 trong main, trùng chữ với h1 trên header)."""
        return self.page.locator("main h1")

    @property
    def status_select(self):
        return self.select_with_option("pending")

    @property
    def rating_select(self):
        return self.select_with_option("5")

    @property
    def list_ready(self):
        """Hết skeleton: có dòng dữ liệu hoặc dòng trạng thái rỗng."""
        return self.table.locator("tbody tr td p, tbody tr td button").first
