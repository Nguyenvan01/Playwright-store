# Form thêm / sửa sản phẩm (/admin/products/create, /admin/products/edit/:id). Ô nhập dùng AdminUi.field(label).
import re


class ProductFormPage:
    create_path = "/admin/products/create"

    def __init__(self, page):
        self.page = page
        self.form = page.locator("main form")
        self.submit_button = self.form.locator('button[type="submit"]')
        self.back_button = page.get_by_role("button", name="Quay lại", exact=True)
        self.error_box = self.form.locator("> div.bg-red-50")
        self.loading_text = page.get_by_text("Đang tải dữ liệu...", exact=True)
        self.variant_toggle = page.get_by_role("button", name=re.compile(r"^(\+ Tạo biến thể|Tắt chế độ)$"))
        self.variant_builder = self.section("Biến thể").locator("div.bg-gray-50.rounded-lg")
        self.generate_button = self.variant_builder.get_by_role("button", name=re.compile(r"^Tạo \d+ biến thể$"))
        self.variant_rows = (
            self.section("Biến thể").locator("div.grid.grid-cols-6").filter(has=page.locator("input"))
        )
        self.image_url_input = page.get_by_placeholder("Dán URL ảnh...", exact=True)
        self.image_tiles = self.section("Hình ảnh").locator("div.aspect-square.group")
        self.main_image_badge = self.section("Hình ảnh").get_by_text("Ảnh chính", exact=True)
        self.file_input = self.section("Hình ảnh").locator('input[type="file"]')

    def section(self, title):
        """Khối có tiêu đề h3, vd: "Thông tin sản phẩm", "Biến thể", "Hình ảnh"."""
        return (
            self.page.locator("main form div.rounded-xl")
            .filter(has=self.page.get_by_role("heading", name=title, exact=True))
            .first
        )

    def size_button(self, name):
        return self.variant_builder.get_by_role("button", name=name, exact=True)

    def color_button(self, name):
        return self.variant_builder.get_by_role("button", name=name, exact=True)

    def variant_cell(self, index, col):
        """col: "size" hoặc "color"."""
        return self.variant_rows.nth(index).locator("span").nth(0 if col == "size" else 1)

    def variant_sku(self, index):
        return self.variant_rows.nth(index).locator("input").first

    def variant_remove(self, index):
        return self.variant_rows.nth(index).get_by_role("button")

    def image_remove(self, index):
        return self.image_tiles.nth(index).get_by_role("button")
