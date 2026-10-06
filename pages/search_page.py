# Trang kết quả tìm kiếm /search?q=...
import re

from pages.base_page import BasePage
from pages.components.header import Header
from utils.routes import search_route


class SearchPage(BasePage):
    path = "/search"

    def __init__(self, page):
        super().__init__(page)
        self.header = Header(page)
        self.heading = page.get_by_role("heading", level=1)
        self.result_count = page.get_by_text(re.compile(r"^\d+ sản phẩm$"))
        self.product_links = page.locator('a[href^="/product/"]').filter(visible=True)
        self.no_result = page.get_by_role("heading", name="Không tìm thấy sản phẩm nào")

    def search(self, query):
        self.goto(search_route(query))
