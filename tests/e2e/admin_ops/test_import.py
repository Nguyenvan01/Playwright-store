# ============================================================
# TEST: QUẢN TRỊ - NHẬP HÀNG (API GIẢ LẬP)
# Mục tiêu: hiển thị bảng + thống kê, lọc/tìm phía server, kiểm tra form tạo đơn, tính tiền,
#           tạo đơn (mock POST), xem chi tiết, nhận hàng, hủy đơn
# Dữ liệu: data/admin-ops/import.json (mock API + case + expected)
# Trang Nhập hàng có lỗi vòng lặp tải lại (toast tạo lại mỗi lần render -> effect gọi lại API),
# nên MỌI request GET đều được giả lập để không gọi liên tục lên production.
# API cần quan sát: k.admin_ops.*, k.admin.fill_form / click_row_action, k.common.mock_write / verify_request
# Kết quả mong đợi: payload POST/DELETE đúng (mock, không ghi DB), toast + modal đúng trạng thái
# ============================================================
import pytest

from utils.cases import case_params
from utils.data_loader import load_data

D = load_data("admin-ops/import.json")
SEARCH = "Tìm mã đơn, nhà cung cấp..."
LIST_API = "**/api/admin/imports"
ITEM_API = "**/api/admin/imports/*"
CREATE = "Tạo đơn nhập hàng"
CODES = [i["code"] for i in D["mock"]["imports"]]

pytestmark = pytest.mark.role("admin")


def fill_create_form(k, form, items, payment=None):
    """Mở form tạo đơn và điền: thông tin chung -> các dòng sản phẩm -> thanh toán."""
    k.admin_ops.open_create_import()
    if form:
        k.admin.fill_form(form)
    for i, item in enumerate(items):
        if i > 0:
            k.admin_ops.add_import_item_row()
        k.admin_ops.fill_import_item(i, item)
    if payment:
        k.admin.fill_form(payment)


@pytest.fixture(autouse=True)
def mock_import(k):
    k.admin_ops.mock_import_data(D["mock"])


class TestImport:
    """Quản trị - Nhập hàng (API giả lập)"""

    @pytest.mark.smoke
    def test_page_loads(self, k):
        """[ADO-IMP-01] Trang tải: tiêu đề, đủ cột, thẻ thống kê"""
        k.admin_ops.open_import()
        k.admin_ops.verify_columns(D["headers"])
        k.admin_ops.verify_row_count(len(D["mock"]["imports"]))
        k.admin_ops.verify_stat_cards(D["statCards"])
        k.common.verify_no_page_errors()

    @pytest.mark.parametrize("case", case_params(D["rows"]))
    def test_row_display(self, k, case):
        """Hiển thị dòng + nút theo trạng thái (data-driven)"""
        k.admin_ops.open_import()
        k.admin_ops.verify_row_cells(case["rowText"], case["expected"])
        k.admin_ops.verify_row_actions(case["rowText"], case["actions"])

    @pytest.mark.parametrize("case", case_params(D["filters"]))
    def test_server_filter(self, k, case):
        """Lọc / tìm kiếm phía server (data-driven)"""
        k.admin_ops.open_import()
        if case["action"] == "status":
            k.admin_ops.filter_import_status(case["value"])
        if case["action"] == "supplier":
            k.admin_ops.filter_import_supplier(case["value"])
        if case["action"] == "search":
            k.admin.search_list(SEARCH, case["value"])
        k.admin_ops.verify_list_query("/admin/imports", case["query"])
        k.admin_ops.verify_visible_rows(case["visible"], [c for c in CODES if c not in case["visible"]])
        if case.get("emptyText"):
            k.common.verify_text_visible(case["emptyText"])

    @pytest.mark.parametrize("case", case_params(D["validation"]))
    def test_create_validation(self, k, case):
        """Form tạo đơn - kiểm tra dữ liệu (data-driven)"""
        k.common.mock_write("POST", LIST_API, {"success": True})
        k.admin_ops.open_import()
        fill_create_form(k, case["form"], case["items"])
        k.admin_ops.click_modal_button(CREATE, "Tạo đơn nhập hàng")
        k.common.verify_toast(case["toast"])
        k.admin.verify_modal_open(CREATE)
        k.common.verify_no_request("POST", "/admin/imports")

    @pytest.mark.parametrize("case", case_params([D["totals"]]))
    def test_totals(self, k, case):
        """Tính thành tiền và tổng tiền nhập"""
        k.admin_ops.open_import()
        fill_create_form(k, case["form"], case["items"])
        k.admin_ops.verify_import_totals(0, case["lineTotal"], case["grandTotal"])

    @pytest.mark.parametrize("case", case_params(D["create"]))
    def test_create_success(self, k, case):
        """Tạo đơn thành công (data-driven, mock POST)"""
        k.common.mock_write("POST", LIST_API, {"success": True, "import": {"id": 99}})
        k.admin_ops.open_import()
        fill_create_form(k, case["form"], case["items"], case.get("payment"))
        k.admin_ops.click_modal_button(CREATE, case["button"])
        k.common.verify_request("POST", "/admin/imports", case["expectedPayload"])
        k.common.verify_toast(case["toast"])
        k.admin.verify_modal_closed(CREATE)

    @pytest.mark.parametrize("case", case_params([D["createError"]]))
    def test_create_server_error(self, k, case):
        """Server từ chối tạo đơn"""
        k.common.mock_write("POST", LIST_API, {"success": False, "message": case["message"]}, case["status"])
        k.admin_ops.open_import()
        fill_create_form(k, case["form"], case["items"])
        k.admin_ops.click_modal_button(CREATE, "Tạo đơn nhập hàng")
        k.common.verify_toast(case["message"])
        k.admin.verify_modal_open(CREATE)

    def test_view_detail(self, k):
        """[ADO-IMP-02] Xem chi tiết đơn nhập"""
        k.admin_ops.open_import()
        k.admin.click_row_action(D["detail"]["rowText"], "Xem chi tiết")
        k.admin_ops.verify_modal_text("Chi tiết đơn nhập hàng", D["detail"]["texts"])
        k.admin_ops.verify_list_query(f"/admin/imports/{D['detail']['id']}", {})

    @pytest.mark.parametrize("case", case_params(D["receive"]["cases"]))
    def test_receive(self, k, case):
        """Nhận hàng (data-driven)"""
        receive = D["receive"]
        k.common.mock_write("POST", f"{ITEM_API}/receive", {"success": True})
        k.admin_ops.open_import()
        k.admin.click_row_action(receive["rowText"], "Nhận hàng")
        k.admin_ops.verify_modal_text("Nhận hàng", [receive["rowText"]])
        k.admin_ops.set_receive_quantities(case["quantities"])
        k.admin_ops.click_modal_button("Nhận hàng", "Xác nhận nhận hàng")
        k.common.verify_toast(case["toast"])
        if case.get("expectedPayload"):
            k.common.verify_request("POST", f"/admin/imports/{receive['id']}/receive", case["expectedPayload"])
            k.admin.verify_modal_closed("Nhận hàng")
        else:
            k.common.verify_no_request("POST", "/receive")

    def test_cancel_accept_dialog(self, k):
        """[ADO-IMP-03] Hủy đơn: đồng ý hộp thoại gửi DELETE (mock)"""
        k.common.mock_write("DELETE", ITEM_API, {"success": True})
        k.admin_ops.open_import()
        k.common.accept_next_dialog(True)
        k.admin.click_row_action(D["cancel"]["rowText"], "Hủy đơn")
        k.common.verify_request("DELETE", f"/admin/imports/{D['cancel']['id']}")
        k.common.verify_toast(D["cancel"]["toast"])

    def test_cancel_dismiss_dialog(self, k):
        """[ADO-IMP-05] Hủy đơn: bấm Hủy trên hộp thoại không gửi DELETE"""
        k.common.mock_write("DELETE", ITEM_API, {"success": True})
        k.admin_ops.open_import()
        k.common.accept_next_dialog(False)
        k.admin.click_row_action(D["cancel"]["rowText"], "Hủy đơn")
        k.admin_ops.verify_row_cells(D["cancel"]["rowText"], {"Trạng thái": "Đang xử lý"})
        k.common.verify_no_request("DELETE", "/admin/imports")
