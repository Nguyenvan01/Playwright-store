# Modal "Đổi mật khẩu" trên trang hồ sơ (PasswordModal trong ProfilePage.jsx) - không có role=dialog.
import re


class PasswordModal:
    def __init__(self, page):
        self.page = page
        self.heading = page.get_by_role("heading", level=3, name="Đổi mật khẩu")
        self.root = page.locator("div.fixed.inset-0").filter(has=self.heading)
        self.current_password = self.root.get_by_placeholder("Nhập mật khẩu hiện tại")
        self.new_password = self.root.get_by_placeholder("Ít nhất 6 ký tự")
        self.confirm_password = self.root.get_by_placeholder("Nhập lại mật khẩu mới")
        self.submit_button = self.root.get_by_role("button", name=re.compile(r"^(Xác nhận|Đang xử lý\.\.\.)$"))
        self.cancel_button = self.root.get_by_role("button", name="Hủy", exact=True)
        # Nút chữ "Đóng" ở góc trên (khác nút nền mờ cũng có aria-label "Đóng").
        self.close_button = self.root.locator('button:text-is("Đóng")')
        self.backdrop = self.root.locator('button[aria-label="Đóng"]')
        self.error = self.root.locator("form .bg-red-50")
