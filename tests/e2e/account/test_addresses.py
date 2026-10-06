# ============================================================
# TEST: SỔ ĐỊA CHỈ
# Mục tiêu: màn hình trống, danh sách, validate form, thêm / sửa / xóa / đặt mặc định
# Dữ liệu: data/account/addresses.json (mock GET /api/addresses)
# Kết quả mong đợi: thẻ địa chỉ + badge mặc định đúng; mọi thao tác ghi đều mock + kiểm tra payload
# ============================================================
import pytest

from tests.e2e.account.support import API
from utils.cases import case_params, known_bug
from utils.data_loader import load_data

DATA = load_data("account/addresses.json")
CREATED = DATA["create"]["form"]

pytestmark = pytest.mark.role("customer")


class TestAddressesEmpty:
    """Sổ địa chỉ - Chưa có địa chỉ"""

    @pytest.fixture(autouse=True)
    def opened_empty(self, k):
        k.common.mock_get(API["addresses"], DATA["empty"])
        k.account.open_addresses()

    def test_empty_state(self, k):
        """[ACC-ADR-E01] Hiển thị màn hình trống"""
        k.account.verify_addresses_empty()

    def test_add_first_address(self, k):
        """[ACC-ADR-E02] Thêm địa chỉ đầu tiên từ màn hình trống: server đặt làm mặc định"""
        k.common.mock_write("POST", API["addresses"], DATA["createFirst"], 201)
        k.account.open_add_address_from_empty_state()
        k.account.verify_address_form_open("Thêm địa chỉ mới")
        k.account.fill_address_form(CREATED)
        k.account.submit_address_form()
        k.common.verify_request("POST", "/api/addresses", {**CREATED})
        k.account.verify_address_form_closed()
        k.account.verify_address_list([str(CREATED["fullName"])])
        k.account.verify_address_default(str(CREATED["fullName"]), True)


class TestAddressesList:
    """Sổ địa chỉ - Có địa chỉ"""

    @pytest.fixture(autouse=True)
    def opened_list(self, k):
        k.common.mock_get(API["addresses"], DATA["list"])
        k.account.open_addresses()
        k.account.verify_address_list(DATA["names"])

    @pytest.mark.smoke
    def test_cards_and_default(self, k):
        """[ACC-ADR-01] Danh sách địa chỉ: thông tin thẻ và địa chỉ mặc định"""
        for name, texts in DATA["cardTexts"].items():
            k.account.verify_address_card(name, texts)
        k.account.verify_address_default(DATA["defaultName"], True)
        k.account.verify_address_default(DATA["otherName"], False)
        k.account.verify_default_badge_count(1)

    @pytest.mark.parametrize("case", case_params(DATA["validation"]))
    def test_form_validation(self, k, case):
        """Validate form thêm địa chỉ (data-driven)"""
        k.common.mock_write("POST", API["addresses"], DATA["create"]["response"], 201)
        k.account.open_add_address_form()
        k.account.fill_address_form({**DATA["validForm"], **case["form"]})
        k.account.submit_address_form()
        k.account.verify_address_form_errors(case["errors"])
        k.common.verify_no_request("POST", "/api/addresses")

    @pytest.mark.smoke
    def test_add_address(self, k):
        """[ACC-ADR-02] Thêm địa chỉ mới (SĐT có khoảng trắng hợp lệ): gửi đúng payload, hiện thẻ mới"""
        k.common.mock_write("POST", API["addresses"], DATA["create"]["response"], 201)
        k.account.open_add_address_form()
        k.account.fill_address_form(CREATED)
        k.account.submit_address_form()
        k.common.verify_request("POST", "/api/addresses", {**CREATED})
        k.account.verify_address_form_closed()
        k.account.verify_address_list([str(CREATED["fullName"]), *DATA["names"]])
        k.account.verify_address_card(str(CREATED["fullName"]), DATA["create"]["cardTexts"])
        k.account.verify_address_default(str(CREATED["fullName"]), False)

    def test_add_default_address(self, k, request):
        """[ACC-ADR-03] Thêm địa chỉ mặc định mới: chỉ còn 1 badge Mặc định"""
        known_bug(
            request,
            "AddressesPage.jsx:218 thêm địa chỉ mặc định vào đầu danh sách nhưng không bỏ is_default "
            'của địa chỉ cũ (backend đã bỏ) -> 2 badge "Mặc định"',
        )
        form = DATA["createDefault"]["form"]
        k.common.mock_write("POST", API["addresses"], DATA["createDefault"]["response"], 201)
        k.account.open_add_address_form()
        k.account.fill_address_form(form)
        k.account.submit_address_form()
        k.common.verify_request("POST", "/api/addresses", {"isDefault": True})
        k.account.verify_address_default(str(form["fullName"]), True)
        k.account.verify_default_badge_count(1)

    def test_cancel_add_form(self, k):
        """[ACC-ADR-04] Hủy form thêm: đóng form, không gửi request"""
        k.common.mock_write("POST", API["addresses"], DATA["create"]["response"], 201)
        k.account.open_add_address_form()
        k.account.fill_address_form(CREATED)
        k.account.cancel_address_form()
        k.account.verify_address_form_closed()
        k.common.verify_no_request("POST", "/api/addresses")
        k.account.verify_address_list(DATA["names"])

    def test_edit_address(self, k):
        """[ACC-ADR-05] Sửa địa chỉ: form điền sẵn, gửi PUT, thẻ cập nhật"""
        e = DATA["edit"]
        k.common.mock_write("PUT", API["address"], e["response"])
        k.account.edit_address(e["name"])
        k.account.verify_address_form_open("Sửa địa chỉ")
        k.account.verify_address_form_values(e["expectedForm"])
        k.account.fill_address_form(e["changes"])
        k.account.submit_address_form()
        k.common.verify_request(
            "PUT",
            f"/api/addresses/{DATA['otherId']}",
            {**e["expectedForm"], **e["changes"], "isDefault": False},
        )
        k.account.verify_address_form_closed()
        k.account.verify_address_list([DATA["defaultName"], e["newName"]])
        k.account.verify_address_card(e["newName"], [str(e["changes"]["address"])])

    def test_set_default(self, k):
        """[ACC-ADR-06] Đặt làm mặc định: gửi PUT isDefault, badge chuyển sang địa chỉ mới"""
        k.common.mock_write("PUT", API["address"], DATA["setDefault"]["response"])
        k.account.set_default_address(DATA["otherName"])
        k.common.verify_request("PUT", f"/api/addresses/{DATA['otherId']}", {"isDefault": True})
        k.account.verify_address_default(DATA["otherName"], True)
        k.account.verify_address_default(DATA["defaultName"], False)
        k.account.verify_default_badge_count(1)

    def test_no_stray_zero_after_set_default(self, k, request):
        """[ACC-ADR-07] Sau khi đổi mặc định, thẻ địa chỉ không hiện ký tự "0" thừa"""
        known_bug(
            request,
            "AddressesPage.jsx:226 đặt is_default = 0 (số) và dòng 331 render {addr.is_default && ...} "
            '-> React in ra chữ "0" cạnh tên người nhận',
        )
        k.common.mock_write("PUT", API["address"], DATA["setDefault"]["response"])
        k.account.set_default_address(DATA["otherName"])
        k.account.verify_address_default(DATA["otherName"], True)
        k.account.verify_address_name_row(DATA["otherName"], True)
        k.account.verify_address_name_row(DATA["defaultName"], False)

    def test_delete_address(self, k):
        """[ACC-ADR-08] Xóa địa chỉ: hộp xác nhận, gửi DELETE, thẻ biến mất"""
        k.common.mock_write("DELETE", API["address"], DATA["delete"]["response"])
        k.account.delete_address(DATA["otherName"])
        k.account.verify_delete_address_dialog(DATA["delete"]["dialogText"])
        k.account.confirm_delete_address()
        k.common.verify_request("DELETE", f"/api/addresses/{DATA['otherId']}")
        k.account.verify_address_list([DATA["defaultName"]])

    def test_cancel_delete(self, k):
        """[ACC-ADR-09] Hủy xóa: không gửi request, danh sách giữ nguyên"""
        k.common.mock_write("DELETE", API["address"], DATA["delete"]["response"])
        k.account.delete_address(DATA["otherName"])
        k.account.cancel_delete_address()
        k.common.verify_no_request("DELETE", "/api/addresses")
        k.account.verify_address_list(DATA["names"])

    def test_delete_default_address(self, k, request):
        """[ACC-ADR-10] Xóa địa chỉ mặc định: địa chỉ còn lại được hiển thị là mặc định"""
        known_bug(
            request,
            "AddressesPage.jsx:235 chỉ lọc bỏ địa chỉ đã xóa, không tải lại danh sách; backend "
            "(customerController.js deleteAddress) đã chuyển mặc định sang địa chỉ khác nhưng UI không "
            'có badge "Mặc định" nào',
        )
        k.common.mock_write("DELETE", API["address"], DATA["delete"]["response"])
        k.account.delete_address(DATA["defaultName"])
        k.account.confirm_delete_address()
        k.common.verify_request("DELETE", f"/api/addresses/{DATA['defaultId']}")
        k.account.verify_address_list([DATA["otherName"]])
        k.account.verify_address_default(DATA["otherName"], True)

    @pytest.mark.parametrize("case", case_params([DATA["serverError"]]))
    def test_server_error(self, k, case):
        """Lỗi server khi thêm địa chỉ hiển thị thông báo lỗi"""
        k.common.mock_write("POST", API["addresses"], case["response"], case["status"])
        k.account.open_add_address_form()
        k.account.fill_address_form(CREATED)
        k.account.submit_address_form()
        k.common.verify_request("POST", "/api/addresses")
        k.common.verify_text_visible(case["message"])
