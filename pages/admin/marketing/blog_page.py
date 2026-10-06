# Trang quản trị Bài viết (/admin/blog).
from pages.admin.marketing.admin_table import AdminTable


class BlogPage(AdminTable):
    path = "/admin/blog"
    search_placeholder = "Tìm theo tiêu đề, slug, mô tả..."

    @property
    def page_heading(self):
        return self.page.locator("main h1")

    @property
    def add_button(self):
        return self.page.get_by_role("button", name="Thêm bài viết", exact=True)

    @property
    def image_url_input(self):
        return self.page.get_by_placeholder("Dán URL ảnh...", exact=True)

    @property
    def image_preview(self):
        return self.page.get_by_role("img", name="Xem trước ảnh bài viết")

    @property
    def list_ready(self):
        return self.table.locator("tbody tr td p, tbody tr td button").first
