# Locator dùng chung cho mọi trang quản trị.
# Form admin dùng <label> KHÔNG gắn htmlFor -> tìm ô nhập đứng ngay sau label.
import re


class AdminUi:
    def __init__(self, page):
        self.page = page

    @property
    def page_title(self):
        """Tiêu đề trang trên header admin."""
        return self.page.locator("header h1")

    def field(self, label):
        """Ô input/select/textarea ngay sau <label> có text `label` (bỏ qua dấu * bắt buộc)."""
        clean = re.sub(r"\s*\*\s*$", "", label)
        pattern = re.compile(rf"^\s*{re.escape(clean)}\s*\*?\s*$")
        return (
            self.page.locator("label")
            .filter(has_text=pattern, visible=True)
            .first.locator("xpath=following::*[self::input or self::select or self::textarea][1]")
        )

    def checkbox(self, label):
        """Checkbox nằm trong <label> (vd: "Hoạt động", "Nổi bật")."""
        return self.page.get_by_role("checkbox", name=label, exact=True).filter(visible=True).first

    def button(self, name):
        """Nút theo tên hiển thị (nút hiển thị cuối cùng - thường là nút trong modal đang mở)."""
        return self.page.get_by_role("button", name=name, exact=True).filter(visible=True).last

    def heading(self, text):
        return self.page.get_by_role("heading", name=text, exact=True).filter(visible=True).first

    def row(self, text):
        """Dòng trong bảng chứa text."""
        return self.page.locator("tbody tr").filter(has_text=text, visible=True)

    def row_action(self, row_text, title):
        """Nút hành động trong 1 dòng, nhận diện qua title (vd: "Sửa", "Xóa", "Xem chi tiết")."""
        return self.row(row_text).first.get_by_title(title, exact=True)

    @property
    def table_headers(self):
        return self.page.locator("thead th").filter(visible=True)
