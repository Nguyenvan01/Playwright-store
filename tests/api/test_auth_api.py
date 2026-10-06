# ============================================================
# TEST: API - XÁC THỰC KHÁCH HÀNG, PHÂN QUYỀN ENDPOINT, ĐĂNG NHẬP ADMIN
# Mục tiêu: validate đăng nhập/đăng ký, endpoint bảo vệ trả 401 khi thiếu/sai token,
#           token khách không vào được API admin, không có mật khẩu cứng (backdoor) cho admin
# Dữ liệu: data/api/endpoints.json (customerProtected, adminProtected, adminBackdoorPasswords)
# API cần quan sát: fixture api (post, get, register_customer, customer_login)
# Kết quả mong đợi: status + message đúng; đăng ký thật chỉ chạy khi E2E_ALLOW_WRITE=1
# ============================================================
import allure
import pytest

from config import ADMIN, CUSTOMER
from utils.cases import require
from utils.data_loader import load_data
from utils.factories import build_customer
from utils.messages import MSG

ENDPOINTS = load_data("api/endpoints.json")
PROTECTED = ENDPOINTS["customerProtected"] + ENDPOINTS["adminProtected"]


class TestCustomerAuth:
    """API - Xác thực khách hàng"""

    def test_login_missing_fields(self, api):
        """Đăng nhập thiếu thông tin trả 400"""
        res = api.post("/auth/login", {"email": ""})
        assert res.status == 400, f"expected=400, actual={res.status}"

    def test_login_wrong_password(self, api):
        """Đăng nhập sai mật khẩu trả 401"""
        res = api.post("/auth/login", {"email": "khong-ton-tai@example.com", "password": "sai-mat-khau"})
        assert res.status == 401, f"expected=401, actual={res.status}"
        message = res.json().get("message")
        expected = MSG["login"]["wrongCredentials"]
        assert message == expected, f"message: expected={expected!r}, actual={message!r}"

    def test_register_missing_fields(self, api):
        """Đăng ký thiếu trường bắt buộc trả 400"""
        res = api.post("/auth/register", {"email": "a@example.com"})
        assert res.status == 400, f"expected=400, actual={res.status}"

    def test_register_invalid_email(self, api):
        """Đăng ký email sai định dạng trả 400"""
        res = api.post("/auth/register", build_customer(email="khong-phai-email"))
        assert res.status == 400, f"expected=400, actual={res.status}"

    def test_register_then_duplicate(self, api):
        """Đăng ký thành công rồi đăng ký trùng email trả 409"""
        require("allowWrite")
        customer = build_customer()

        created = api.register_customer(customer)
        assert created["token"], "Đăng ký không trả token"

        dup = api.post("/auth/register", customer)
        assert dup.status == 409, f"Đăng ký trùng: expected=409, actual={dup.status}"
        message = dup.json().get("message")
        expected = MSG["register"]["emailTaken"]
        assert message == expected, f"message: expected={expected!r}, actual={message!r}"

        login = api.customer_login(customer["email"], customer["password"])
        assert login["token"], "Đăng nhập bằng tài khoản vừa tạo không trả token"


@pytest.mark.security
class TestEndpointAuthorization:
    """API - Phân quyền endpoint (data-driven)"""

    @pytest.mark.parametrize("path", PROTECTED, ids=PROTECTED)
    def test_protected_without_token(self, api, path):
        """GET {path} không có token trả 401"""
        allure.dynamic.title(f"GET {path} không có token trả 401")
        res = api.get(path)
        assert res.status == 401, f"{path}: expected=401, actual={res.status}"

    def test_customer_token_cannot_access_admin(self, api):
        """Token khách hàng không truy cập được API admin"""
        require("customer")
        token = api.customer_login(CUSTOMER["email"], CUSTOMER["password"])["token"]
        for path in ENDPOINTS["adminProtected"]:
            res = api.get(path, headers={"Authorization": f"Bearer {token}"})
            assert res.status in (401, 403), f"{path}: expected 401/403, actual={res.status}"

    def test_forged_token_rejected(self, api):
        """Token giả mạo bị từ chối"""
        res = api.get("/admin/dashboard", headers={"Authorization": "Bearer abc.def.ghi"})
        assert res.status == 401, f"expected=401, actual={res.status}"


@pytest.mark.security
class TestAdminLogin:
    """API - Đăng nhập admin"""

    def test_admin_wrong_password(self, api):
        """Sai mật khẩu trả 401"""
        res = api.post("/admin/login", {"email": "admin@clothing-store.vn", "password": "sai-mat-khau-e2e"})
        assert res.status == 401, f"expected=401, actual={res.status}"

    # Backend đang chấp nhận mật khẩu cứng cho MỌI tài khoản admin
    # (backend/src/controllers/adminController.js -> adminLogin). Test này sẽ FAIL cho tới khi gỡ bỏ.
    @pytest.mark.parametrize("backdoor", ENDPOINTS["adminBackdoorPasswords"])
    def test_no_backdoor_password(self, api, backdoor):
        """Không được đăng nhập admin bằng mật khẩu cứng "{backdoor}\""""
        allure.dynamic.title(f'Không được đăng nhập admin bằng mật khẩu cứng "{backdoor}"')
        email = ADMIN["email"] or "admin@clothing-store.vn"
        if ADMIN["password"] == backdoor:
            pytest.skip("Mật khẩu thật trùng mật khẩu demo")
        res = api.post("/admin/login", {"email": email, "password": backdoor})
        assert res.status == 401, f"Backend chấp nhận mật khẩu cứng - lỗ hổng bảo mật: expected=401, actual={res.status}"
