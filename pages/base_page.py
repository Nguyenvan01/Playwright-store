# POM CƠ SỞ: locator + thao tác nguyên tử; không chứa expected của ca kiểm thử.
class BasePage:
    # URL tương đối của trang (để trống nếu trang cần tham số, vd: product/:slug).
    path = ""

    def __init__(self, page):
        self.page = page
        # Vùng chứa toast (ToastContext) ở góc trên phải.
        self.toasts = page.locator("div.fixed.top-4.right-4")

    def goto(self, path=None):
        self.page.goto(path or self.path)

    def toast(self, message):
        return self.toasts.get_by_text(message)
