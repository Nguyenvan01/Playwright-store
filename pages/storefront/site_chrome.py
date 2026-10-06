# Phần dùng chung cuối trang: khối "Đăng ký nhận tin" (components/Newsletter.jsx) và Footer.


class SiteChrome:
    def __init__(self, page):
        self.page = page
        self.newsletter = page.locator("section").filter(
            has=page.get_by_role("heading", name="Đăng ký nhận tin", exact=True)
        )
        self.newsletter_email = self.newsletter.get_by_placeholder("Nhập email của bạn")
        self.newsletter_submit = self.newsletter.get_by_role("button", name="Đăng ký")
        self.newsletter_thanks = self.newsletter.get_by_text("Cảm ơn bạn đã đăng ký!")
        self.footer = page.locator("footer")
        self.footer_copyright = self.footer.get_by_text("© 2026 Đạt Hoàng. All rights reserved.")
        # Vùng nội dung chính của trang (bỏ header/footer).
        self.main = page.locator("main")
        # Toàn bộ chữ trong <body> (dùng cho trang trắng / route không tồn tại).
        self.body = page.locator("body")

    def footer_heading(self, name):
        return self.footer.get_by_role("heading", name=name, exact=True)

    def footer_link(self, name):
        return self.footer.get_by_role("link", name=name, exact=True)

    def footer_link_to(self, href):
        return self.footer.locator(f'a[href="{href}"]')

    def main_headings(self, level):
        return self.main.locator(f"h{level}")
