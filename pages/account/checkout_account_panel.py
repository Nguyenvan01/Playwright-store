# Khối "Đăng nhập / Đăng ký" trên /checkout khi đã đăng nhập (CheckoutPage.jsx: .ck-auth-user).


class CheckoutAccountPanel:
    def __init__(self, page):
        self.page = page
        self.root = page.locator(".ck-auth-user")
        self.name = self.root.locator(".ck-auth-user-name")
        self.email = self.root.locator(".ck-auth-user-email")
        self.logout_button = self.root.get_by_role("button", name="Đăng xuất", exact=True)
