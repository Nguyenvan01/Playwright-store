# ============================================================
# Tiện ích dùng chung cho các trang quản trị (nhóm sales + catalog):
#  - ghi lại request GET /api/admin/* để kiểm tra tham số lọc/phân trang,
#  - trả JSON cho route GET (mock dữ liệu đọc, KHÔNG đụng tới request ghi),
#  - locator modal / phân trang (app không dùng role=dialog).
# ============================================================
import json
import re
from urllib.parse import parse_qs, urlparse


class AdminRequestLog:
    def __init__(self, page):
        self.urls = []
        page.on("request", self._on_request)

    def _on_request(self, request):
        if request.method == "GET" and "/api/admin/" in request.url:
            self.urls.append(request.url)

    def has(self, path, params=None):
        """Có request GET tới đường dẫn kết thúc bằng `path` và chứa đủ các tham số query."""
        params = params or {}
        for url in self.urls:
            parsed = urlparse(url)
            query = query_of_url(url)
            if parsed.path.endswith(path) and all(
                query.get(k) == _js_str(v) for k, v in params.items()
            ):
                return True
        return False

    def count(self, path):
        """Số request GET tới đường dẫn kết thúc bằng `path`."""
        return sum(1 for url in self.urls if urlparse(url).path.endswith(path))

    def describe(self):
        return json.dumps(
            [urlparse(u).path + (f"?{urlparse(u).query}" if urlparse(u).query else "") for u in self.urls],
            ensure_ascii=False,
        )


def _js_str(value):
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def fulfill_get(route, json_factory, status=200):
    """Trả JSON cho request GET; request khác (POST/PUT/DELETE) chuyển tiếp cho mockWrite / writeGuard."""
    if route.request.method != "GET":
        return route.fallback()
    return route.fulfill(status=status, json=json_factory())


def query_of_url(url):
    """Tham số query dạng {key: giá trị đầu tiên} (giống URLSearchParams.get)."""
    return {k: v[0] for k, v in parse_qs(urlparse(url).query, keep_blank_values=True).items()}


def query_of(route):
    """Tham số query của request đang bị chặn."""
    return query_of_url(route.request.url)


def includes_ci(value, needle):
    """So khớp không phân biệt hoa thường."""
    return needle.lower() in ("" if value is None else str(value)).lower()


def modal_by_heading(page, heading):
    """Modal của app: lớp phủ `div.fixed.inset-0` chứa tiêu đề h3 (không có role=dialog)."""
    exact = isinstance(heading, str)
    return (
        page.locator("div.fixed.inset-0")
        .filter(has=page.get_by_role("heading", name=heading, exact=exact))
        .last
    )


def pagination_bar(page):
    """Thanh phân trang cuối bảng (có dòng "Trang ...")."""
    return page.locator("div.border-t").filter(has=page.get_by_text(re.compile(r"^Trang \d+"))).last
