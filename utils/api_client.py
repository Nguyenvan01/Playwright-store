# ============================================================
# API CLIENT: wrapper mỏng quanh APIRequestContext để gọi backend Express.
# Dùng trong API test và để chuẩn bị dữ liệu (lấy sản phẩm thật, đăng nhập lấy token...).
# ============================================================
from urllib.parse import urlencode

from config import API_URL


class ApiClient:
    def __init__(self, request, base_url=API_URL):
        self.request = request
        self.base_url = base_url

    def url(self, path):
        return f"{self.base_url}{path if path.startswith('/') else '/' + path}"

    def get(self, path, **options):
        return self.request.get(self.url(path), **options)

    def post(self, path, data=None, token=None):
        headers = {"Authorization": f"Bearer {token}"} if token else None
        return self.request.post(self.url(path), data=data, headers=headers)

    @staticmethod
    def _ensure_ok(res, message):
        assert res.ok, f"{message}: {res.status}"

    # ---------- Catalog ----------
    def list_products(self, **params):
        qs = urlencode({k: str(v) for k, v in params.items()})
        res = self.get(f"/products{'?' + qs if qs else ''}")
        self._ensure_ok(res, "GET /products lỗi")
        return res.json()["data"]["products"]

    def get_product(self, slug):
        res = self.get(f"/products/{slug}")
        self._ensure_ok(res, f"GET /products/{slug} lỗi")
        data = res.json()["data"]
        # Text hiển thị trên nút size - frontend dùng `code || name`.
        data["sizes"] = [
            {**s, "label": s.get("label") or s.get("code") or s.get("name") or ""}
            for s in data.get("sizes") or []
        ]
        return data

    def find_purchasable_product(self):
        """Tìm 1 sản phẩm thật có ít nhất 1 size còn hàng để dùng cho test UI."""
        for product in self.list_products(limit=20):
            detail = self.get_product(product["slug"])
            size = next((s for s in detail["sizes"] if not s.get("disabled")), None)
            if size:
                return {"product": detail, "size": size}
        raise ValueError("Không tìm thấy sản phẩm nào có size còn hàng trong DB.")

    # ---------- Auth ----------
    def customer_login(self, email, password):
        res = self.post("/auth/login", {"email": email, "password": password})
        self._ensure_ok(res, f"Đăng nhập khách hàng {email} thất bại")
        body = res.json()
        return {"token": body["token"], "user": body["user"]}

    def register_customer(self, customer):
        res = self.post("/auth/register", customer)
        assert res.status == 201, f"Đăng ký {customer['email']}: {res.text()}"
        body = res.json()
        return {"token": body["token"], "user": body["user"]}

    def admin_login(self, email, password):
        res = self.post("/admin/login", {"email": email, "password": password})
        self._ensure_ok(res, f"Đăng nhập admin {email} thất bại")
        body = res.json()
        return {"token": body["token"], "user": body["user"]}
