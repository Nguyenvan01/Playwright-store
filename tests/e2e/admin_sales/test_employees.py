# ============================================================
# TEST: ADMIN - NHÂN VIÊN
# Mục tiêu: bảng, vai trò, tìm kiếm, thêm/sửa (validate + mock ghi), vô hiệu hóa, nút gạt trạng thái
# Dữ liệu: data/admin-sales/employees.json
# Danh sách nhân viên được mock; mọi thao tác ghi đều mock.
# Không test được an toàn (cần ghi thật lên API): backend updateEmployee bỏ qua email/password,
# không kiểm tra quyền theo vai trò, staff tạo được admin, response lộ hash mật khẩu.
# Kết quả mong đợi: lỗi form đúng; request ghi đúng payload; toast + bảng cập nhật
# ============================================================
import pytest
from playwright.sync_api import expect

from utils.cases import case_params, known_bug
from utils.data_loader import load_data

DATA = load_data("admin-sales/employees.json")
ADD = "Thêm nhân viên mới"
EDIT = "Cập nhật nhân viên"

pytestmark = pytest.mark.role("admin")


@pytest.fixture
def mocked_employees(k):
    """Mock danh sách nhân viên rồi mở trang Nhân viên."""
    k.admin_sales.mock_employees_api(DATA["fixture"])
    k.admin.open_admin_page("/admin/employees", "Nhân viên")


@pytest.mark.smoke
def test_real_employees_page(k):
    """[ADS-EMP-00] Trang nhân viên dữ liệu thật: tiêu đề và cột bảng"""
    k.admin.open_admin_page("/admin/employees", "Nhân viên")
    k.admin_sales.verify_employees_heading(DATA["heading"])
    k.admin_sales.verify_columns(DATA["headers"])
    k.admin_sales.verify_api_requested("/admin/employees", {"page": 1})


@pytest.mark.usefixtures("mocked_employees")
class TestEmployeesMocked:
    """Admin - Nhân viên: Dữ liệu mock"""

    def test_role_labels(self, k):
        """[ADS-EMP-01] Nhãn vai trò hiển thị tiếng Việt cho 4 vai trò"""
        for role in DATA["roles"]:
            k.admin_sales.verify_employee_role(role["name"], role["label"])
        k.admin_sales.verify_employee_active("Thủ Kho E2E", False)
        k.admin_sales.verify_employee_active("Nhân Viên E2E", True)

    def test_search(self, k):
        """[ADS-EMP-02] Tìm nhân viên gửi từ khóa lên API và lọc bảng"""
        search = DATA["search"]
        k.admin.search_list("Tìm theo tên, email...", search["text"])
        k.admin_sales.verify_api_requested("/admin/employees", search["request"])
        for name in search["rows"]:
            k.admin_sales.verify_person_row(name)
        for name in search["hidden"]:
            k.admin_sales.verify_person_row(name, False)

    @pytest.mark.parametrize("case", case_params(DATA["create"]))
    def test_create(self, k, case):
        k.common.mock_write("POST", "**/api/admin/employees", case["response"])
        k.admin.click_button("Thêm nhân viên")
        k.admin.fill_form(case["form"])
        k.admin.click_button("Lưu")
        k.common.verify_request("POST", "/admin/employees", case["payload"])
        k.common.verify_toast(DATA["createToast"])
        k.admin.verify_modal_closed(ADD)
        k.admin_sales.verify_employee_role(case["name"], case["roleLabel"])


@pytest.mark.usefixtures("mocked_employees")
class TestAddEmployee:
    """Admin - Nhân viên: Thêm nhân viên"""

    @pytest.fixture(autouse=True)
    def add_modal(self, k, mocked_employees):
        k.common.mock_write("POST", "**/api/admin/employees", {"success": True, "employee": {}})
        k.admin.click_button("Thêm nhân viên")
        k.admin.verify_modal_open(ADD)

    @pytest.mark.parametrize("case", case_params(DATA["addValidation"]))
    def test_add_validation(self, k, case):
        if case["form"]:
            k.admin.fill_form(case["form"])
        k.admin.click_button("Lưu")
        if case.get("nativeEmailInvalid"):
            k.admin_sales.verify_employee_email_native_invalid()
        k.admin_sales.verify_field_errors(ADD, case["errors"])
        k.common.verify_no_request("POST", "/admin/employees")

    def test_default_role_and_active(self, k, po):
        """[ADS-EMP-03] Mặc định vai trò "staff" và tài khoản hoạt động"""
        k.admin.verify_field_value("Vai trò", "staff")
        expect(po.admin_ui.checkbox("Tài khoản hoạt động")).to_be_checked()


@pytest.mark.usefixtures("mocked_employees")
class TestEditEmployee:
    """Admin - Nhân viên: Sửa nhân viên"""

    def test_edit_without_password(self, k):
        """[ADS-EMP-04] Form sửa điền sẵn; đổi tên + vai trò gửi PUT không kèm mật khẩu (mock)"""
        e = DATA["edit"]
        k.common.mock_write("PUT", f"**/api/admin/employees/{e['id']}", e["response"])
        k.admin_sales.click_employee_action(e["employee"], "Sửa")
        k.admin.verify_modal_open(EDIT)
        for label, value in e["prefill"].items():
            k.admin.verify_field_value(label, value)
        k.admin_sales.verify_field_placeholder("Mật khẩu", e["passwordPlaceholder"])
        k.admin.fill_form(e["form"])
        k.admin.click_button("Lưu")
        k.common.verify_request("PUT", f"/admin/employees/{e['id']}", e["payload"])
        body = k.common.captured[-1]["body"] if k.common.captured else None
        assert "password" not in (body or {}), (
            f"Không đổi mật khẩu thì không gửi password: actual body={body!r}"
        )
        k.common.verify_toast(e["toast"])
        k.admin.verify_modal_closed(EDIT)
        k.admin_sales.verify_employee_role(e["newName"], e["roleLabel"])

    def test_edit_with_password(self, k):
        """[ADS-EMP-05] Nhập mật khẩu mới khi sửa -> payload có password"""
        e = DATA["edit"]
        k.common.mock_write("PUT", f"**/api/admin/employees/{e['id']}", e["response"])
        k.admin_sales.click_employee_action(e["employee"], "Sửa")
        k.admin.fill_form(e["withPassword"]["form"])
        k.admin.click_button("Lưu")
        k.common.verify_request("PUT", f"/admin/employees/{e['id']}", e["withPassword"]["payload"])
        k.common.verify_toast(e["toast"])

    @pytest.mark.parametrize("case", case_params(DATA["editValidation"]))
    def test_edit_validation(self, k, case):
        k.common.mock_write("PUT", "**/api/admin/employees/*", {"success": True, "employee": {}})
        k.admin_sales.click_employee_action(case["employee"], "Sửa")
        k.admin.fill_form(case["form"])
        k.admin.click_button("Lưu")
        k.admin_sales.verify_field_errors(EDIT, case["errors"])
        k.common.verify_no_request("PUT", "/admin/employees/")


@pytest.mark.usefixtures("mocked_employees")
class TestDisableEmployee:
    """Admin - Nhân viên: Vô hiệu hóa (nút Xóa) - backend luôn trả 400"""

    @pytest.fixture(autouse=True)
    def mock_delete(self, k, mocked_employees):
        d = DATA["delete"]
        k.common.mock_write("DELETE", f"**/api/admin/employees/{d['id']}", d["backendResponse"], d["backendStatus"])

    def test_disable_modal_cancel(self, k, page):
        """[ADS-EMP-06] Modal "Xác nhận vô hiệu hóa" + "Hủy" không gửi request"""
        d = DATA["delete"]
        k.admin_sales.click_employee_action(d["employee"], "Xóa")
        k.admin.verify_modal_open(d["heading"])
        k.admin_sales.verify_modal_text(d["heading"], "Hành động này không thể hoàn tác")
        expect(page.get_by_text(d["message"])).to_be_visible()
        k.admin.click_button("Hủy")
        k.admin.verify_modal_closed(d["heading"])
        k.common.verify_no_request("DELETE", "/admin/employees/")

    def test_disable_backend_error(self, k):
        """[ADS-EMP-07] Xác nhận -> hiển thị lỗi backend, nhân viên vẫn trong bảng"""
        d = DATA["delete"]
        k.admin_sales.click_employee_action(d["employee"], "Xóa")
        k.admin.click_button("Xác nhận")
        k.common.verify_request("DELETE", f"/admin/employees/{d['id']}")
        k.common.verify_toast(d["backendResponse"]["message"])
        k.admin.verify_modal_closed(d["heading"])
        k.admin_sales.verify_person_row(d["employee"])

    def test_disable_success(self, k, request):
        """[ADS-EMP-08] Xác nhận vô hiệu hóa thành công"""
        known_bug(
            request,
            'adminController.deleteEmployee luôn trả 400 "Không thể xóa tài khoản nhân viên..." -> nút Xóa/Vô hiệu hóa ở AdminEmployees.jsx:112-121 không bao giờ thành công (phải dùng nút gạt)',
        )
        d = DATA["delete"]
        k.admin_sales.click_employee_action(d["employee"], "Xóa")
        k.admin.click_button("Xác nhận")
        k.common.verify_toast(d["successToast"])


@pytest.mark.usefixtures("mocked_employees")
class TestToggleEmployee:
    """Admin - Nhân viên: Nút gạt trạng thái (mock PUT /toggle)"""

    def test_toggle_off(self, k):
        """[ADS-EMP-09] Tắt tài khoản thành công -> toast + nút gạt xám"""
        t = DATA["toggle"]
        k.common.mock_write("PUT", f"**/api/admin/employees/{t['id']}/toggle", {"success": True})
        k.admin_sales.click_employee_action(t["employee"], "Trạng thái")
        k.common.verify_request("PUT", f"/admin/employees/{t['id']}/toggle")
        k.common.verify_toast(t["toast"])
        k.admin_sales.verify_employee_active(t["employee"], False)

    def test_toggle_api_error(self, k, request):
        """[ADS-EMP-10] API lỗi -> báo lỗi và giữ nguyên trạng thái"""
        known_bug(request, "AdminEmployees.jsx:65-67 nhánh catch vẫn đảo is_active nên nút gạt đổi màu dù API lỗi")
        t = DATA["toggle"]
        k.common.mock_write(
            "PUT", f"**/api/admin/employees/{t['id']}/toggle", {"success": False, "message": "Lỗi"}, 500
        )
        k.admin_sales.click_employee_action(t["employee"], "Trạng thái")
        k.common.verify_toast(t["errorToast"])
        k.admin_sales.verify_employee_active(t["employee"], True)
