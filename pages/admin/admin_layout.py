# Khung trang quản trị: sidebar + header có tiêu đề trang.
from pages.base_page import BasePage


class AdminLayout(BasePage):
    path = "/admin"

    def __init__(self, page):
        super().__init__(page)
        self.sidebar = page.locator("aside").first
        self.page_title = page.locator("header h1")

    def menu_link(self, label):
        return self.sidebar.get_by_role("link", name=label, exact=True)

    def navigate_to(self, label):
        self.menu_link(label).click()
