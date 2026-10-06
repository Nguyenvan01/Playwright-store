# ============================================================
# SINH KEYWORDS.md từ registry keyword Python (keywords.GROUPS / KEYWORD_MAP).
# Mỗi keyword: tên trong kịch bản ("cart.verifyCartBadge"), cách gọi Python
# (k.cart.verify_cart_badge(count)) và mô tả = dòng đầu docstring của method.
# Chạy:
#     .venv/bin/python scripts/gen_keywords_doc.py            (ghi KEYWORDS.md)
#     .venv/bin/python scripts/gen_keywords_doc.py --stdout   (in ra màn hình, không ghi file)
# ============================================================
import argparse
import inspect
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from keywords import GROUPS, KEYWORD_MAP  # noqa: E402


def esc(text):
    return str(text).replace("|", "\\|")


def python_params(method):
    """Tham số của method (bỏ self), giữ giá trị mặc định: 'count', 'accept=True'."""
    params = list(inspect.signature(method).parameters.values())[1:]
    return ", ".join(str(p) for p in params)


def python_call(attr, method_name, method):
    """Cách gọi trong test: k.cart.verify_cart_badge(count)."""
    names = []
    for p in list(inspect.signature(method).parameters.values())[1:]:
        if p.kind is p.VAR_POSITIONAL:
            names.append(f"*{p.name}")
        elif p.kind is p.VAR_KEYWORD:
            names.append(f"**{p.name}")
        else:
            names.append(p.name)
    return f"k.{attr}.{method_name}({', '.join(names)})"


def build():
    md = "# Danh mục Keyword\n\n> File tự sinh bởi `.venv/bin/python scripts/gen_keywords_doc.py` — đừng sửa tay.\n\n"
    md += (
        "Dùng trong code (pytest): `k.<nhóm>.<keyword_snake_case>(...)`, vd: `k.cart.verify_cart_badge(2)` · "
        "Dùng trong kịch bản Excel: cột `keyword` = `<nhóm>.<keywordCamelCase>`, vd: `cart.verifyCartBadge`.\n\n"
        "Kịch bản nằm trong `data/scenarios/*.xlsx`, mỗi file có 2 sheet:\n\n"
        "- `TestSteps`: `template_id | step | keyword | args | note` — `args` là mảng JSON, vd: `[2]`, "
        "`[\"${product.name}\", \"M\"]`.\n"
        "- `TestData`: `case_id | template_id | title | tags | requires | known_bug | <cột placeholder>` — "
        "mỗi dòng là 1 test case, giá trị cột placeholder thay vào placeholder `{tên_cột}` trong `args` lúc collection; `${...}` là biến runtime.\n\n"
    )
    total = 0
    missing = []
    for attr, klass in GROUPS:
        group = klass.group
        md += f"## {group}\n\n| Keyword | Python | Tham số | Mô tả |\n|---|---|---|---|\n"
        for name, method_name in klass.keywords().items():
            method = getattr(klass, method_name)
            doc = (inspect.getdoc(method) or "").strip().splitlines()
            description = doc[0].strip() if doc else ""
            if not description:
                missing.append(f"{group}.{name}")
            params = python_params(method)
            md += (
                f"| `{group}.{name}` | `{esc(python_call(attr, method_name, method))}` | "
                f"{f'`{esc(params)}`' if params else '—'} | {esc(description) or '—'} |\n"
            )
            total += 1
        md += "\n"
    assert total == len(KEYWORD_MAP), f"Lệch registry: {total} != {len(KEYWORD_MAP)}"
    return md, total, missing


def main(argv=None):
    parser = argparse.ArgumentParser(description="Sinh KEYWORDS.md từ registry keyword.")
    parser.add_argument("--stdout", action="store_true", help="In ra màn hình thay vì ghi KEYWORDS.md")
    args = parser.parse_args(argv)

    md, total, missing = build()
    if args.stdout:
        print(md)
    else:
        (ROOT / "KEYWORDS.md").write_text(md, encoding="utf-8")
        print(f"KEYWORDS.md: {total} keyword")
    if missing:
        print(f"Thiếu docstring 1 dòng cho: {', '.join(missing)}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
