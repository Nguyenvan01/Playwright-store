# ============================================================
# TEST: ADMIN - KHÁCH HÀNG
# Mục tiêu: bảng, tìm kiếm, thêm/sửa (validate + mock ghi), chi tiết, xóa, phân trang
# Dữ liệu: data/admin-sales/customers.json
# Danh sách khách hàng được mock (không phụ thuộc / không lộ dữ liệu khách thật); mọi thao tác ghi đều mock.
# Kết quả mong đợi: lỗi form đúng thứ tự; request ghi đúng payload; toast + bảng cập nhật
# ============================================================
import pytest
from playwright.sync_api import expect

from utils.cases import case_params, known_bug
from utils.data_loader import load_data

DATA = load_data("admin-sales/customers.json")
ADD = "Thêm khách hàng"
EDIT = "Cập nhật khách hàng"

pytestmark = pytest.mark.role("admin")


@pytest.fixture(autouse=True)
def customers_page(k):
    k.admin_sales.mock_customers_api(DATA["fixture"])
    k.admin.open_admin_page("/admin/customers", "Khách hàng")


class TestCustomers:
    """Admin - Khách hàng"""

    @pytest.mark.smoke
    def test_table(self, k):
        """[ADS-CUS-01] Bảng khách hàng: đủ cột, trạng thái, chi tiêu, điểm"""
        k.admin_sales.verify_columns(DATA["headers"])
        for row in DATA["rows"]:
            k.admin_sales.verify_customer_row(row)

    def test_search(self, k):
        """[ADS-CUS-02] Tìm khách hàng gửi từ khóa lên API và lọc bảng"""
        search = DATA["search"]
        k.admin.search_list("Tìm theo tên, email, SĐT...", search["text"])
        k.admin_sales.verify_api_requested("/admin/customers", {"search": search["text"], "page": 1})
        for name in search["rows"]:
            k.admin_sales.verify_person_row(name)
        for name in search["hidden"]:
            k.admin_sales.verify_person_row(name, False)

    def test_add_duplicate_email(self, k):
        """[ADS-CUS-07] Server báo "Email đã tồn tại." -> toast lỗi, modal vẫn mở"""
        add = DATA["add"]
        k.common.mock_write(
            "POST",
            "**/api/admin/customers",
            {"success": False, "message": add["error"]["message"]},
            add["error"]["status"],
        )
        k.admin.click_button(ADD)
        k.admin.fill_form(add["form"])
        k.admin.click_button("Lưu")
        k.common.verify_request("POST", "/admin/customers", add["payload"])
        k.common.verify_toast(add["error"]["message"])
        k.admin.verify_modal_open(ADD)

    def test_detail_modal(self, k):
        """[ADS-CUS-09] Modal chi tiết khách hàng (GET /admin/customers/:id)"""
        k.admin.click_row_action(DATA["detail"]["customer"], "Chi tiết")
        k.admin.verify_modal_open("Chi tiết khách hàng")
        k.admin_sales.verify_api_requested("/admin/customers/9601")
        k.admin_sales.verify_customer_detail(DATA["detail"])

    def test_recent_order_statuses(self, k, request):
        """[ADS-CUS-13] Đơn gần đây trong chi tiết khách hiển thị trạng thái tiếng Việt"""
        known_bug(request, DATA["detail"]["statusBug"])
        k.admin.click_row_action(DATA["detail"]["customer"], "Chi tiết")
        k.admin_sales.verify_customer_detail(DATA["detail"])
        k.admin_sales.verify_customer_recent_order_statuses(DATA["detail"]["recentStatuses"])


class TestAddCustomer:
    """Admin - Khách hàng: Thêm khách hàng"""

    @pytest.fixture(autouse=True)
    def add_modal(self, k):
        k.common.mock_write("POST", "**/api/admin/customers", DATA["add"]["response"])
        k.admin.click_button(ADD)
        k.admin.verify_modal_open(ADD)

    @pytest.mark.parametrize("case", case_params(DATA["addValidation"]))
    def test_add_validation(self, k, case):
        if case["form"]:
            k.admin.fill_form(case["form"])
        k.admin.click_button("Lưu")
        k.admin_sales.verify_field_errors(ADD, case["errors"])
        k.common.verify_no_request("POST", "/admin/customers")

    def test_placeholders_and_password_hint(self, k):
        """[ADS-CUS-03] Form thêm có placeholder và gợi ý mật khẩu mặc định"""
        k.admin_sales.verify_field_placeholder("Họ và tên", "Nguyễn Văn A")
        k.admin_sales.verify_field_placeholder("Email", "email@example.com")
        k.admin_sales.verify_field_placeholder("Số điện thoại", "0912345678")
        k.admin_sales.verify_modal_text(ADD, DATA["add"]["passwordHint"])

    def test_add_valid_customer(self, k):
        """[ADS-CUS-04] Thêm khách hợp lệ (mock POST) -> toast, đóng modal, dòng mới đầu bảng"""
        add = DATA["add"]
        k.admin.fill_form(add["form"])
        k.admin.click_button("Lưu")
        k.common.verify_request("POST", "/admin/customers", add["payload"])
        k.common.verify_toast(add["toast"])
        k.admin.verify_modal_closed(ADD)
        k.admin_sales.verify_person_row(add["form"]["Họ và tên"])

    def test_errors_clear_after_fix(self, k):
        """[ADS-CUS-05] Lỗi sửa xong ô nhập thì thông báo lỗi biến mất"""
        k.admin.click_button("Lưu")
        k.admin_sales.verify_field_errors(ADD, ["Họ và tên không được để trống.", "Email không được để trống."])
        k.admin.fill_form({"Họ và tên": "Khách E2E"})
        k.admin_sales.verify_field_errors(ADD, ["Email không được để trống."])

    def test_cancel_add(self, k):
        """[ADS-CUS-06] "Hủy" đóng modal, không gửi request"""
        k.admin.fill_form(DATA["add"]["form"])
        k.admin.click_button("Hủy")
        k.admin.verify_modal_closed(ADD)
        k.common.verify_no_request("POST", "/admin/customers")


class TestEditCustomer:
    """Admin - Khách hàng: Sửa khách hàng"""

    def test_edit_customer(self, k):
        """[ADS-CUS-08] Form sửa điền sẵn dữ liệu; lưu gửi PUT đúng payload (mock) và cập nhật dòng"""
        e = DATA["edit"]
        k.common.mock_write("PUT", f"**/api/admin/customers/{e['id']}", e["response"])
        k.admin.click_row_action(e["customer"], "Sửa")
        k.admin.verify_modal_open(EDIT)
        for label, value in e["prefill"].items():
            k.admin.verify_field_value(label, value)
        k.admin.fill_form(e["form"])
        k.admin.click_button("Lưu")
        k.common.verify_request("PUT", f"/admin/customers/{e['id']}", e["payload"])
        body = k.common.captured[-1]["body"] if k.common.captured else None
        assert "password" not in (body or {}), (
            f"Không đổi mật khẩu thì không gửi password: actual body={body!r}"
        )
        k.common.verify_toast(e["toast"])
        k.admin.verify_modal_closed(EDIT)
        k.admin_sales.verify_customer_row({"name": e["newName"], "status": e["status"]})

    @pytest.mark.parametrize("case", case_params(DATA["editValidation"]))
    def test_edit_validation(self, k, case):
        k.common.mock_write("PUT", "**/api/admin/customers/*", {"success": True, "customer": {}})
        k.admin.click_row_action(case["customer"], "Sửa")
        k.admin.fill_form(case["form"])
        k.admin.click_button("Lưu")
        k.admin_sales.verify_field_errors(EDIT, case["errors"])
        k.common.verify_no_request("PUT", "/admin/customers/")


class TestDeleteCustomer:
    """Admin - Khách hàng: Xóa khách hàng (mock DELETE, data-driven)"""

    def test_delete_modal_cancel(self, k, page):
        """[ADS-CUS-10] Modal xác nhận xóa: nội dung + "Hủy" không gửi request"""
        k.common.mock_write("DELETE", "**/api/admin/customers/*", {"success": True})
        k.admin.click_row_action("Trần Thị Kiểm Thử", "Xóa")
        k.admin_sales.verify_modal_text("Xác nhận xóa", "Hành động này không thể hoàn tác")
        k.admin_sales.verify_customer_delete_warning(None)
        expect(page.get_by_text(DATA["deleteText"])).to_be_visible()
        k.admin.click_button("Hủy")
        k.admin.verify_modal_closed("Xác nhận xóa")
        k.common.verify_no_request("DELETE", "/admin/customers/")
        k.admin_sales.verify_person_row("Trần Thị Kiểm Thử")

    @pytest.mark.parametrize("case", case_params(DATA["delete"]))
    def test_delete(self, k, case):
        k.common.mock_write(
            "DELETE",
            f"**/api/admin/customers/{case['customerId']}",
            case["response"],
            case.get("status", 200),
        )
        k.admin.click_row_action(case["customer"], "Xóa")
        k.admin_sales.verify_customer_delete_warning(case.get("warning"))
        k.admin.click_button("Xóa")
        k.common.verify_request("DELETE", f"/admin/customers/{case['customerId']}")
        k.common.verify_toast(case["toast"])
        k.admin.verify_modal_closed("Xác nhận xóa")
        k.admin_sales.verify_person_row(case["customer"], not case.get("removed"))
        if case.get("rowStatus"):
            k.admin_sales.verify_customer_row({"name": case["customer"], "status": case["rowStatus"]})


class TestCustomersPagination:
    """Admin - Khách hàng: Phân trang (20 khách/trang)"""

    @pytest.fixture(autouse=True)
    def many_customers(self, k):
        k.admin_sales.mock_customers_api({**DATA["fixture"], "total": DATA["pagination"]["total"]})
        k.common.reload()

    def test_go_to_page_2(self, k):
        """[ADS-CUS-11] Bấm trang 2 gọi API page=2"""
        k.admin_sales.verify_pagination_text("Trang 1 / 8")
        k.admin_sales.go_to_page(2)
        k.admin_sales.verify_api_requested("/admin/customers", {"page": 2})
        k.admin_sales.verify_pagination_text("Trang 2 / 8")

    def test_page_buttons_shift(self, k, request):
        """[ADS-CUS-12] Sang trang 6 thì dãy số trang dịch theo (hiện nút 6)"""
        known_bug(
            request,
            "AdminCustomers.jsx:271 dãy nút trang luôn là 1..5 (không dịch theo trang hiện tại) -> không bấm trực tiếp được trang 6-8",
        )
        p = DATA["pagination"]
        k.admin_sales.go_to_page(p["lastClicked"])
        k.admin_sales.click_next_page()
        k.admin_sales.verify_pagination_text(p["text"])
        k.admin_sales.verify_api_requested("/admin/customers", {"page": p["expectedPage"]})
        k.admin_sales.verify_page_button(p["expectedPage"])
