# Gom toàn bộ Page Object của 1 `page` - tầng Keyword dùng qua đây (k.po.header, k.po.cart...).
from pages.account_pages import OrdersPage, ProfilePage, WishlistPage
from pages.admin.admin_layout import AdminLayout
from pages.admin.admin_login_page import AdminLoginPage
from pages.admin.admin_ui import AdminUi
from pages.category_page import CategoryPage
from pages.checkout_page import CheckoutPage
from pages.components.cart_drawer import CartDrawer
from pages.components.header import Header
from pages.home_page import HomePage
from pages.login_page import LoginPage
from pages.order_success_page import OrderSuccessPage
from pages.product_detail_page import ProductDetailPage
from pages.search_page import SearchPage


class PageObjects:
    def __init__(self, page):
        self.page = page
        self.header = Header(page)
        self.cart = CartDrawer(page)
        self.home = HomePage(page)
        self.login = LoginPage(page)
        self.search = SearchPage(page)
        self.product = ProductDetailPage(page)
        self.checkout = CheckoutPage(page)
        self.order_success = OrderSuccessPage(page)
        self.profile = ProfilePage(page)
        self.orders = OrdersPage(page)
        self.wishlist = WishlistPage(page)
        self.admin_login = AdminLoginPage(page)
        self.admin_layout = AdminLayout(page)
        self.admin_ui = AdminUi(page)

    def category(self, path):
        return CategoryPage(self.page, path)
