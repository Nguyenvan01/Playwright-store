# ============================================================
# HYBRID BINDING: ghép template với MỘT dòng TestData, không mở browser.
# WHY: KDT cũ lặp toàn bộ bước cho từng bộ input. Hybrid giữ một template dùng lại.
# Placeholder {cot} phải chiếm TOÀN BỘ 1 phần tử chuỗi trong args, vd: ["{size}", 2].
# Chuỗi ${...} là biến runtime -> driver script thay lúc chạy, binding không đụng tới.
# ============================================================
import json
import re

from drivers.driver_script import FIELDS, validate_steps
from keywords import KEYWORD_MAP

TEMPLATE_FIELDS = (FIELDS - {"case_id"}) | {"template_id"}
PLACEHOLDER = re.compile(r"\{([A-Za-z_][A-Za-z0-9_]*)\}")
META_FIELDS = {"case_id", "template_id", "title", "tags", "requires", "known_bug"}


def parse_args(text, where):
    """Ô args trong Excel: rỗng -> [], còn lại phải là mảng JSON."""
    if text.strip() == "":
        return []
    try:
        value = json.loads(text)
    except ValueError as error:
        raise ValueError(f"{where}: args không phải JSON hợp lệ: {text!r}") from error
    if not isinstance(value, list):
        raise ValueError(f"{where}: args phải là mảng JSON, vd: [\"Áo thun\", 2]")
    return value


def _placeholders(value, where):
    """Liệt kê placeholder {cot} trong args (đệ quy)."""
    if isinstance(value, str):
        match = PLACEHOLDER.fullmatch(value)
        if match:
            return [match.group(1)]
        stripped = re.sub(r"\$\{[^}]*\}", "", value)
        if "{" in stripped or "}" in stripped:
            raise ValueError(f"{where}: placeholder phải chiếm toàn phần tử: {value!r}")
        return []
    if isinstance(value, list):
        return [name for item in value for name in _placeholders(item, where)]
    if isinstance(value, dict):
        return [name for item in value.values() for name in _placeholders(item, where)]
    return []


def _bind(value, case):
    if isinstance(value, str):
        match = PLACEHOLDER.fullmatch(value)
        return case[match.group(1)] if match else value
    if isinstance(value, list):
        return [_bind(item, case) for item in value]
    if isinstance(value, dict):
        return {key: _bind(item, case) for key, item in value.items()}
    return value


def validate_template(template):
    """Kiểm tra cấu trúc trước binding; giá trị runtime được kiểm tra lúc chạy."""
    if not isinstance(template, list) or not template:
        raise ValueError("Template không có bước")
    template_id = template[0].get("template_id") if isinstance(template[0], dict) else None
    for number, row in enumerate(template, 1):
        where = f"Template {template_id} bước {number}"
        if not isinstance(row, dict) or set(row) != TEMPLATE_FIELDS:
            raise ValueError(f"{where}: sai schema")
        if not template_id or row["template_id"] != template_id or row["step"] != str(number):
            raise ValueError(f"{where}: sai template_id hoặc thứ tự step")
        if row["keyword"] not in KEYWORD_MAP:
            raise ValueError(f"Keyword chưa khai báo: {row['keyword']}")
        if not isinstance(row["args"], list):
            raise ValueError(f"{where}: args phải là mảng")
        _placeholders(row["args"], where)
    return template


def bind_template(template, case):
    """Trả list bước MỚI; không sửa template hoặc case của lần chạy sau."""
    validate_template(template)
    if not isinstance(case, dict) or any(not isinstance(v, str) for v in case.values()):
        raise ValueError("Case phải là dictionary chứa các giá trị chuỗi")
    if not case.get("case_id") or case.get("template_id") != template[0]["template_id"]:
        raise ValueError("case_id rỗng hoặc template_id không khớp")
    steps = []
    for template_row in template:
        where = f"Case {case['case_id']} bước {template_row['step']}"
        for name in _placeholders(template_row["args"], where):
            if name in META_FIELDS or name not in case:
                raise ValueError(f"Case {case['case_id']}: thiếu placeholder {name}")
        row = {key: value for key, value in template_row.items() if key != "template_id"}
        row["case_id"] = case["case_id"]
        row["args"] = _bind(template_row["args"], case)
        steps.append(row)
    return validate_steps(steps)
