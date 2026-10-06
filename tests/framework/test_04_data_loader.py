# ============================================================
# DEMO: DATA LOADER + CASE META
# Mục tiêu: thay biến ${...} / @data: đúng kiểu; case meta -> marker pytest
# Kết quả mong đợi: dữ liệu trả về là bản sao; requires -> skip; knownBug -> xfail strict
# ============================================================
import pytest

from utils.assertions import assert_subset, is_subset
from utils.cases import case_marks, case_params
from utils.data_loader import get_path, load_data, mask_secrets, resolve_data

pytestmark = pytest.mark.core

CTX = {"product": {"name": "Áo thun", "price": 199000, "sizes": [{"label": "M"}]}, "flag": True}


def test_load_data_returns_copy():
    first = load_data("cart/items.json")
    first["twoItems"].clear()
    assert len(load_data("cart/items.json")["twoItems"]) == 2


def test_load_data_pointer():
    assert load_data("cart/items.json#twoItems.0.name") == "Áo thun E2E"
    with pytest.raises(ValueError, match="Không có dữ liệu"):
        load_data("cart/items.json#missing")


def test_resolve_whole_variable_keeps_type():
    assert resolve_data("${product.price}", CTX) == 199000
    assert resolve_data("${product.sizes.0.label}", CTX) == "M"


def test_resolve_inline_variable_is_text():
    assert resolve_data('Đã thêm "${product.name}" (${flag})', CTX) == 'Đã thêm "Áo thun" (true)'


def test_resolve_nested_and_data_ref():
    value = resolve_data({"items": "@data:cart/items.json#twoItems", "name": ["${product.name}"]}, CTX)
    assert value["items"][1]["name"] == "Quần jean E2E"
    assert value["name"] == ["Áo thun"]


def test_resolve_unknown_variable():
    with pytest.raises(ValueError, match="product.color"):
        resolve_data("${product.color}", CTX)


def test_uid_is_unique():
    assert resolve_data("${uid}", {}) != resolve_data("${uid}", {})


def test_get_path_on_list():
    assert get_path([{"a": 1}], "0.a", "x") == 1


def test_mask_secrets_without_password_is_noop():
    assert mask_secrets("abc") == "abc"


def test_case_marks():
    marks = case_marks({"id": "X", "knownBug": "lỗi A", "tags": ["@smoke"]})
    names = [mark.name for mark in marks]
    assert names == ["xfail", "smoke"]
    assert marks[0].kwargs == {"strict": True, "reason": "BUG: lỗi A"}


def test_case_marks_rejects_unknown_requirement():
    with pytest.raises(ValueError, match="requires"):
        case_marks({"id": "X", "requires": ["root"]})


def test_case_params_rejects_duplicate_id():
    with pytest.raises(ValueError, match="trùng"):
        case_params([{"id": "A"}, {"id": "A"}])


def test_subset_matching():
    actual = {"payment_method": "cod", "items": [{"id": 1, "qty": 2}], "extra": 1}
    assert is_subset({"payment_method": "cod", "items": [{"id": 1}]}, actual)
    assert not is_subset({"payment_method": "bank"}, actual)
    with pytest.raises(AssertionError, match="expected subset"):
        assert_subset(actual, {"city": "hcm"})
