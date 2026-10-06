# ============================================================
# DEMO: HỢP ĐỒNG HYBRID (TEMPLATE + DATA ROW)
# Mục tiêu: phát hiện lỗi binding/join/schema TRƯỚC khi mở browser
# Kịch bản: template giỏ hàng viết ngay trong file; làm hỏng bản sao dữ liệu
# API cần quan sát: bind_template, build_cases, validate_steps, pytest.raises
# Kết quả mong đợi: lỗi bị từ chối với message cụ thể; ca hợp lệ không sửa template
# WHY: debug lỗi cấu hình dữ liệu tách biệt với lỗi ứng dụng
# ============================================================
from copy import deepcopy

import pytest

from drivers.driver_script import validate_steps
from utils.hybrid_reader import build_cases
from utils.template_binding import bind_template, parse_args

pytestmark = pytest.mark.core


def _step(number, keyword, args, note=""):
    return {"template_id": "T-CART", "step": str(number), "keyword": keyword, "args": args, "note": note}


# Dữ liệu viết ngay trong file để quan sát cơ chế; kịch bản thật nằm ở data/scenarios/*.xlsx.
TEMPLATE = [
    _step(1, "cart.seedCart", ["@data:cart/items.json#twoItems"]),
    _step(2, "common.goto", ["/"]),
    _step(3, "cart.openCart", []),
    _step(4, "cart.increaseQuantity", ["{item}", 2]),
    _step(5, "cart.verifyQuantity", ["{item}", "{expected_qty}"]),
    _step(6, "common.verifyToast", ['Đã thêm "${product.name}" vào giỏ hàng'], "biến runtime"),
]
CASE = {
    "case_id": "CART-01",
    "template_id": "T-CART",
    "title": "Tăng số lượng áo thun",
    "tags": "@smoke",
    "requires": "",
    "known_bug": "",
    "item": "Áo thun E2E",
    "expected_qty": "3",
}


def test_bind_one_case():
    steps = bind_template(TEMPLATE, CASE)
    assert steps[3]["args"] == ["Áo thun E2E", 2]
    assert steps[3]["case_id"] == "CART-01"
    # Binding không đụng biến runtime ${...}; driver script thay lúc chạy.
    assert steps[5]["args"] == ['Đã thêm "${product.name}" vào giỏ hàng']
    assert TEMPLATE[3]["args"] == ["{item}", 2]


def test_missing_placeholder():
    case = {key: value for key, value in CASE.items() if key != "item"}
    with pytest.raises(ValueError, match="thiếu placeholder item"):
        bind_template(TEMPLATE, case)


def test_unknown_template():
    with pytest.raises(ValueError, match="Template không tồn tại"):
        build_cases(TEMPLATE, [{**CASE, "template_id": "MISSING"}])


def test_duplicate_case_id():
    with pytest.raises(ValueError, match="trùng"):
        build_cases(TEMPLATE, [CASE, CASE.copy()])


def test_unused_template_is_rejected():
    other = [{**row, "template_id": "T-OTHER"} for row in TEMPLATE]
    with pytest.raises(ValueError, match="Template chưa có dữ liệu"):
        build_cases(TEMPLATE + other, [CASE])


def test_unknown_keyword_is_rejected():
    template = deepcopy(TEMPLATE)
    template[2]["keyword"] = "cart.openCartt"
    with pytest.raises(ValueError, match="Keyword chưa khai báo"):
        bind_template(template, CASE)


def test_wrong_step_order_is_rejected():
    template = deepcopy(TEMPLATE)
    template[1]["step"] = "5"
    with pytest.raises(ValueError, match="thứ tự step"):
        bind_template(template, CASE)


@pytest.mark.parametrize("value", ["{missing}", "{item", "size:{item}"])
def test_invalid_placeholder(value):
    template = deepcopy(TEMPLATE)
    template[3]["args"] = [value, 2]
    with pytest.raises(ValueError, match="[Pp]laceholder"):
        bind_template(template, CASE)


def test_scenario_needs_a_check_step():
    steps = bind_template(TEMPLATE, CASE)
    without_verify = [row for row in steps if not row["keyword"].split(".")[1].startswith("verify")]
    for number, row in enumerate(without_verify, 1):
        row["step"] = str(number)
    with pytest.raises(ValueError, match="bước kiểm tra"):
        validate_steps(without_verify)


def test_binding_is_independent():
    original = deepcopy(TEMPLATE)
    first = bind_template(TEMPLATE, CASE)
    second = bind_template(TEMPLATE, {**CASE, "case_id": "CART-02", "item": "Quần jean E2E"})
    first[3]["args"][0] = "999"
    assert second[3]["args"][0] == "Quần jean E2E"
    assert TEMPLATE == original


def test_join_does_not_cross_product():
    other = [{**row, "template_id": "T-OTHER"} for row in TEMPLATE]
    cases = build_cases(
        TEMPLATE + other, [CASE, {**CASE, "case_id": "OTHER-01", "template_id": "T-OTHER"}]
    )
    assert [case["id"] for case in cases] == ["CART-01", "OTHER-01"]
    assert cases[0]["tags"] == ["@smoke"]
    assert cases[0]["knownBug"] is None


@pytest.mark.parametrize(
    ("text", "expected"),
    [("", []), ('["Áo", 2]', ["Áo", 2]), ('[{"a": true}]', [{"a": True}])],
)
def test_parse_args(text, expected):
    assert parse_args(text, "test") == expected


@pytest.mark.parametrize("text", ['"Áo"', "[1,", "{}"])
def test_parse_args_rejects_non_array(text):
    with pytest.raises(ValueError, match="args"):
        parse_args(text, "test")
