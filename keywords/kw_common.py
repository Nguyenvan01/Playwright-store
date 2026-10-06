# THƯ VIỆN KEYWORD - NHÓM common: điều hướng, URL, toast, mock API, bắt request ghi.
import json
import re
from urllib.parse import urlparse

from playwright.sync_api import expect

from keywords.base_keywords import BaseKeywords, keyword
from utils.assertions import assert_subset, poll_until
from utils.storage import detect_reload


class CommonKeywords(BaseKeywords):
    group = "common"

    def __init__(self, page, po, api, common=None):
        super().__init__(page, po, api, common)
        self.page_errors = []
        # Các request đã bị mockWrite bắt lại (theo thứ tự): {method, path, body}.
        self.captured = []
        page.on("pageerror", lambda error: self.page_errors.append(str(error)))

    @keyword("goto")
    def goto(self, path):
        """Mở 1 đường dẫn bất kỳ, vd: "/about"."""
        with self.step(f"Mở trang {path}"):
            self.page.goto(path)

    @keyword("reload")
    def reload(self):
        """Tải lại trang hiện tại."""
        with self.step("Tải lại trang"):
            self.page.reload()

    @keyword("verifyUrl")
    def verify_url(self, path):
        """Kiểm tra URL hiện tại đúng đường dẫn, vd: "/profile"."""
        with self.step(f"Kiểm tra URL là {path}"):
            expect(self.page).to_have_url(path)

    @keyword("verifyUrlMatches")
    def verify_url_matches(self, pattern):
        """Kiểm tra URL khớp biểu thức chính quy, vd: "/product/.+"."""
        with self.step(f"Kiểm tra URL khớp /{pattern}/"):
            expect(self.page).to_have_url(re.compile(pattern))

    @keyword("verifyToast")
    def verify_toast(self, text):
        """Kiểm tra có toast chứa nội dung."""
        with self.step(f'Kiểm tra toast "{text}"'):
            expect(self.po.home.toast(text)).to_be_visible()

    @keyword("verifyTextVisible")
    def verify_text_visible(self, text):
        """Kiểm tra 1 đoạn chữ đang hiển thị trên trang."""
        with self.step(f'Kiểm tra hiển thị "{text}"'):
            expect(self.page.get_by_text(text).first).to_be_visible()

    @keyword("verifyLayoutLoaded")
    def verify_layout_loaded(self):
        """Kiểm tra trang có header và footer (trang khách hàng tải thành công)."""
        with self.step("Kiểm tra header và footer hiển thị"):
            expect(self.po.header.root).to_be_visible()
            expect(self.page.locator("footer")).to_be_visible()

    @keyword("verifyNoPageErrors")
    def verify_no_page_errors(self):
        """Kiểm tra không phát sinh lỗi JavaScript nào kể từ đầu test."""
        with self.step("Kiểm tra không có lỗi JavaScript"):
            assert self.page_errors == [], "\n".join(self.page_errors)

    @keyword("verifyNoHorizontalOverflow")
    def verify_no_horizontal_overflow(self):
        """Kiểm tra trang không bị tràn ngang (responsive)."""
        with self.step("Kiểm tra không tràn ngang"):
            overflow = self.page.evaluate(
                "() => document.documentElement.scrollWidth - document.documentElement.clientWidth"
            )
            assert overflow <= 1, f"Trang rộng hơn màn hình {overflow}px"

    @keyword("mockApi")
    def mock_api(self, url_pattern, response):
        """Giả lập 1 API theo mẫu URL (glob của Playwright), trả về status + json."""
        status = response.get("status", 200)
        with self.step(f"Mock API {url_pattern} -> {status}"):
            self.page.route(url_pattern, lambda route: route.fulfill(status=status, json=response["json"]))

    @keyword("mockWrite")
    def mock_write(self, method, url_pattern, json_body=None, status=200):
        """Giả lập API ghi (POST/PUT/DELETE) theo mẫu URL, trả về json; lưu lại request để kiểm tra."""
        json_body = {"success": True} if json_body is None else json_body

        def handle(route):
            request = route.request
            if request.method != method.upper():
                return route.fallback()
            try:
                body = request.post_data_json
            except (ValueError, TypeError):
                body = request.post_data
            self.captured.append(
                {"method": request.method, "path": urlparse(request.url).path, "body": body}
            )
            route.fulfill(status=status, json=json_body)

        with self.step(f"Mock {method} {url_pattern} -> {status}"):
            self.page.route(url_pattern, handle)

    def _matching(self, method, path_part):
        return [
            r for r in self.captured if r["method"] == method.upper() and path_part in r["path"]
        ]

    @keyword("verifyRequest")
    def verify_request(self, method, path_part, expected_body=None):
        """Kiểm tra đã gửi request (method + đường dẫn chứa pathPart), body chứa các trường mong đợi."""
        with self.step(f"Kiểm tra đã gửi {method} {path_part}"):
            self._wait_for_request(method, path_part)
            if expected_body is not None:
                assert_subset(self._matching(method, path_part)[-1]["body"], expected_body)

    def _wait_for_request(self, method, path_part):
        # Thông báo được tính lúc hết hạn để liệt kê đủ các request đã bắt.
        try:
            poll_until(lambda: self._matching(method, path_part), "")
        except AssertionError:
            seen = json.dumps([f"{r['method']} {r['path']}" for r in self.captured], ensure_ascii=False)
            raise AssertionError(f"Không thấy request {method} {path_part}. Đã bắt: {seen}") from None

    @keyword("mockGet")
    def mock_get(self, url_pattern, json_body, status=200):
        """Giả lập API GET (dữ liệu mẫu cho trang cần data, vd: danh sách đơn hàng). Chỉ chặn method GET."""
        with self.step(f"Mock GET {url_pattern} -> {status}"):
            self.page.route(
                url_pattern,
                lambda route: route.fulfill(status=status, json=json_body)
                if route.request.method == "GET"
                else route.fallback(),
            )

    @keyword("acceptNextDialog")
    def accept_next_dialog(self, accept=True):
        """Tự động bấm OK (true) hoặc Hủy (false) cho hộp thoại window.confirm/alert tiếp theo."""
        with self.step(f"{'Đồng ý' if accept else 'Hủy'} hộp thoại xác nhận tiếp theo"):
            self.page.once("dialog", lambda dialog: dialog.accept() if accept else dialog.dismiss())

    @keyword("verifyNoRequest")
    def verify_no_request(self, method, path_part):
        """Kiểm tra KHÔNG có request ghi nào (method + đường dẫn) được gửi."""
        with self.step(f"Kiểm tra KHÔNG gửi {method} {path_part}"):
            matched = self._matching(method, path_part)
            assert matched == [], f"Có request không mong đợi: {matched}"

    def watch_reload(self, timeout=3_000):
        """Bắt đầu theo dõi reload; gọi .reloaded() sau thao tác để kiểm tra (không phải keyword)."""
        return detect_reload(self.page, timeout)
