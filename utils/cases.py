# ============================================================
# CASE META: biến 1 test case dữ liệu thành pytest item.
# - id        -> id của pytest item (hiện trong report, chọn bằng -k)
# - requires  -> skip nếu thiếu điều kiện (tài khoản test, quyền ghi DB)
# - knownBug  -> xfail(strict=True): bug đã biết của app; nếu test PASS thì báo "bug đã sửa?"
# - tags      -> marker pytest, vd: "@smoke" -> pytest.mark.smoke
# ============================================================
import pytest

from config import ADMIN, ALLOW_WRITE, CUSTOMER

REQUIREMENTS = {
    "customer": lambda: None if CUSTOMER["email"] else "Cần E2E_CUSTOMER_EMAIL/PASSWORD",
    "admin": lambda: None if ADMIN["email"] else "Cần E2E_ADMIN_EMAIL/PASSWORD",
    "allowWrite": lambda: None if ALLOW_WRITE else "Cần E2E_ALLOW_WRITE=1 (ghi dữ liệu thật)",
}
TAG_MARKS = {"@smoke": pytest.mark.smoke, "@security": pytest.mark.security}


def missing_requirement(requires=None):
    """Lý do skip nếu thiếu điều kiện, None nếu đủ."""
    for name in requires or []:
        if name not in REQUIREMENTS:
            raise ValueError(f"requires không hợp lệ: {name!r}; chọn {sorted(REQUIREMENTS)}")
        reason = REQUIREMENTS[name]()
        if reason:
            return reason
    return None


def case_marks(case):
    marks = []
    reason = missing_requirement(case.get("requires"))
    if reason:
        marks.append(pytest.mark.skip(reason=reason))
    if case.get("knownBug"):
        marks.append(pytest.mark.xfail(strict=True, reason=f"BUG: {case['knownBug']}"))
    for tag in case.get("tags") or []:
        if tag not in TAG_MARKS:
            raise ValueError(f"Case {case.get('id')}: tag chưa khai báo: {tag}")
        marks.append(TAG_MARKS[tag])
    return marks


def case_param(case):
    """Một data row -> một pytest.param có id và marker riêng."""
    if not case.get("id"):
        raise ValueError(f"Case thiếu id: {case!r}")
    return pytest.param(case, id=case["id"], marks=case_marks(case))


def case_params(cases):
    params = [case_param(case) for case in cases]
    ids = [param.id for param in params]
    duplicates = sorted({case_id for case_id in ids if ids.count(case_id) > 1})
    if duplicates:
        raise ValueError(f"case id trùng: {duplicates}")
    return params


def case_title(case):
    """Tên hiển thị chuẩn cho 1 case dữ liệu: "[ID] Tiêu đề"."""
    return f"[{case['id']}] {case['title']}"


def known_bug(request, reason):
    """Đánh dấu bug đã biết ngay trong thân test (tương đương test.fail của Playwright TS)."""
    request.applymarker(pytest.mark.xfail(strict=True, reason=f"BUG: {reason}"))


def require(*requires):
    """Skip ngay trong thân test nếu thiếu điều kiện."""
    reason = missing_requirement(list(requires))
    if reason:
        pytest.skip(reason)
