# ============================================================
# Trang dạng lưới thẻ: Danh mục (/admin/categories) và Thương hiệu (/admin/brands) - cùng cấu trúc.
# Nút Sửa / Xóa trên thẻ là icon KHÔNG có tên/title và ẩn (opacity-0) tới khi hover thẻ.
# Thứ tự nút trong thẻ: 0 Sửa, 1 Xóa, 2 gạt Hoạt động.
# ============================================================
from pages.admin.sales.admin_api_mock import modal_by_heading


class TaxonomyPage:
    def __init__(self, page):
        self.page = page
        self.cards = page.locator("main div.rounded-xl.group")
        self.card_names = self.cards.locator("h3")

    def card(self, name):
        return self.cards.filter(has=self.page.get_by_role("heading", name=name, exact=True))

    def edit_button(self, name):
        return self.card(name).get_by_role("button").nth(0)

    def delete_button(self, name):
        return self.card(name).get_by_role("button").nth(1)

    def toggle_button(self, name):
        return self.card(name).get_by_role("button").nth(2)

    def featured_badge(self, name):
        return self.card(name).get_by_text("Nổi bật", exact=True)

    def slug(self, name):
        return self.card(name).locator("p.font-mono")

    def modal(self, heading):
        return modal_by_heading(self.page, heading)

    @property
    def delete_modal(self):
        return modal_by_heading(self.page, "Xác nhận xóa")

    @property
    def delete_message(self):
        return self.delete_modal.locator("p.text-gray-600")
