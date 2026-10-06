# ============================================================
# Locator dùng chung cho bảng/modal của các trang quản trị (marketing + vận hành).
# Lưu ý: tiêu đề cột dùng CSS `uppercase` -> innerText bị viết hoa, phải đọc textContent.
# ============================================================
import re

from pages.admin.admin_ui import AdminUi


class AdminTable:
    def __init__(self, page):
        self.page = page
        self.ui = AdminUi(page)

    @property
    def table(self):
        """Bảng chính đầu tiên đang hiển thị trên trang."""
        return self.page.locator("table").filter(visible=True).first

    @property
    def header_cells(self):
        return self.table.locator("thead th")

    @property
    def rows(self):
        """Các dòng dữ liệu đang hiển thị của bảng chính."""
        return self.table.locator("tbody tr").filter(visible=True)

    def header_texts(self):
        """Tên cột (textContent, đã trim) của bảng chính."""
        return [text.strip() for text in self.header_cells.all_text_contents()]

    def row(self, text):
        """Dòng đầu tiên chứa text."""
        return self.ui.row(text).first

    def _column_index(self, header):
        headers = self.header_texts()
        for index, name in enumerate(headers):
            if name.lower() == header.lower():
                return index
        raise ValueError(f'Không có cột "{header}". Cột hiện có: {" | ".join(headers)}')

    def cell(self, row_text, header):
        """Ô của dòng chứa `row_text` tại cột có tên `header`."""
        return self.row(row_text).locator("td").nth(self._column_index(header))

    def cell_at(self, index, header):
        """Ô ở cột `header` của dòng thứ `index` (0 = dòng đầu)."""
        return self.rows.nth(index).locator("td").nth(self._column_index(header))

    def titled_buttons(self, row_text):
        """Các nút có thuộc tính title trong dòng chứa text."""
        return self.row(row_text).locator("button[title]")

    def modal(self, heading):
        """Modal (lớp phủ fixed) có tiêu đề `heading`."""
        return (
            self.page.locator("div.fixed.inset-0")
            .filter(has=self.page.get_by_role("heading", name=heading, exact=True))
            .last
        )

    def modal_button(self, heading, name):
        """Nút theo tên trong modal có tiêu đề `heading`."""
        return self.modal(heading).get_by_role("button", name=name, exact=True).first

    def stat_value(self, label):
        """Thẻ thống kê: đoạn giá trị ngay sau nhãn `label`."""
        pattern = re.compile(rf"^\s*{re.escape(label)}\s*$")
        return (
            self.page.locator("p")
            .filter(has_text=pattern, visible=True)
            .first.locator("xpath=following-sibling::p[1]")
        )

    def select_with_option(self, value):
        """Select (không có label) nhận diện qua 1 option value đặc trưng."""
        return (
            self.page.locator("select")
            .filter(has=self.page.locator(f'option[value="{value}"]'), visible=True)
            .first
        )
