# Các trang danh mục: /nam, /nu, /tre-em, /giam-gia.
import re

from pages.base_page import BasePage
from pages.components.header import Header


class CategoryPage(BasePage):
    def __init__(self, page, path="/nam"):
        super().__init__(page)
        self.path = path
        self.header = Header(page)
        self.heading = page.get_by_role("heading", level=1)
        self.product_links = page.locator('a[href^="/product/"]').filter(visible=True)
        self.sort_select = page.locator("select").first
        self.empty_state = page.get_by_text(re.compile(r"Không tìm thấy sản phẩm"))
