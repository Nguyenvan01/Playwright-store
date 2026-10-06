# ============================================================
# SINH TEST_CASES.md (danh mục test case + kết quả) từ Allure results của lần chạy gần nhất.
# Chạy sau 1 lần test:
#     .venv/bin/python scripts/gen_test_cases.py              (TEST_ENV=prod ... cho môi trường prod)
#     .venv/bin/python scripts/gen_test_cases.py --stdout     (in ra màn hình, không ghi file)
#     .venv/bin/python scripts/gen_test_cases.py --results DIR
# Nguồn: artifacts/<TEST_ENV>/allure-results/*-result.json. Allure giữ kết quả của nhiều lần chạy
# (và các lần rerun) trong cùng thư mục -> mỗi historyId chỉ giữ kết quả có `stop` mới nhất.
# ============================================================
import argparse
import json
import re
import sys
import unicodedata
from collections import Counter
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from config import TEST_ENV  # noqa: E402

DEFAULT_RESULTS = ROOT / "artifacts" / TEST_ENV / "allure-results"

# Đường dẫn test (bỏ tiền tố tests/) -> tên module. So khớp tiền tố DÀI nhất trước.
MODULES = {
    "api/test_health_api": "API - Health & Home",
    "api/test_products_api": "API - Sản phẩm",
    "api/test_public_api": "API - Lọc/Sắp xếp/Validate",
    "api/test_auth_api": "API - Xác thực & Bảo mật",
    "api/test_admin_api": "API - Quản trị",
    "e2e/smoke": "UI - Trang chủ & trang tĩnh",
    "e2e/auth": "UI - Đăng nhập / Đăng ký",
    "e2e/catalog": "UI - Danh mục, Tìm kiếm, Sản phẩm",
    "e2e/cart": "UI - Giỏ hàng",
    "e2e/checkout": "UI - Thanh toán",
    "e2e/account": "UI - Tài khoản khách hàng",
    "e2e/admin": "UI - Quản trị",
    "e2e/mobile": "UI - Mobile",
    "e2e/keyword_driven": "Kịch bản Keyword-driven",
    "e2e/storefront": "UI - Cửa hàng (trang chủ, danh sách, sản phẩm, blog, trang tĩnh)",
    "e2e/admin_catalog": "UI - Admin: Sản phẩm, Danh mục, Thương hiệu",
    "e2e/admin_sales": "UI - Admin: Layout, Dashboard, Đơn hàng, Khách hàng, Nhân viên",
    "e2e/admin_marketing": "UI - Admin: Khuyến mãi, Mã giảm giá, Đánh giá, Bài viết, Liên hệ",
    "e2e/admin_ops": "UI - Admin: Kho, Nhập hàng, Báo cáo, Cài đặt",
    "framework": "Framework - Logging & phân loại lỗi",
    "failure_demo": "Demo lỗi (evidence)",
}

PASSED, KNOWN_BUG, FAILED, SKIPPED, FIXED = "✅ Đạt", "🐞 Bug đã biết", "❌ Lỗi", "⏭️ Bỏ qua", "⚠️ Bug đã sửa?"
STATUSES = [PASSED, KNOWN_BUG, FAILED, SKIPPED, FIXED]
SECURITY = re.compile(r"@security|bảo mật|mật khẩu cứng|upload", re.IGNORECASE)
ANSI = re.compile(r"\x1b\[[\d;]*m")
CASE_ID = re.compile(r"^\[([\w-]+)\]\s*")


def load_latest_results(results_dir):
    """Đọc *-result.json, mỗi historyId chỉ giữ kết quả có `stop` mới nhất."""
    latest = {}
    for path in Path(results_dir).glob("*-result.json"):
        try:
            result = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            print(f"Bỏ qua {path.name}: {error}", file=sys.stderr)
            continue
        key = result.get("historyId") or result.get("testCaseId") or result.get("fullName") or path.name
        if key not in latest or (result.get("stop") or 0) > (latest[key].get("stop") or 0):
            latest[key] = result
    return list(latest.values())


def labels_of(result):
    labels = {}
    for label in result.get("labels") or []:
        labels.setdefault(label.get("name"), []).append(label.get("value"))
    return labels


def test_path(result, labels):
    """'tests.api.test_health_api' -> 'api/test_health_api' (từ label package hoặc fullName)."""
    dotted = (labels.get("package") or [""])[0] or (result.get("fullName") or "").split("#")[0]
    parts = dotted.split(".")
    if parts and parts[0] == "tests":
        parts = parts[1:]
    return "/".join(parts)


def module_of(path):
    for key in sorted(MODULES, key=len, reverse=True):
        if path == key or path.startswith(key + "/"):
            return MODULES[key]
    return path.rsplit("/", 1)[0] if "/" in path else path or "(khác)"


def project_of(labels):
    tags = set(labels.get("tag") or [])
    if "api" in tags:
        return "api"
    if "mobile" in tags:
        return "mobile"
    return "chromium"


def first_line(text, limit=120):
    lines = ANSI.sub("", text or "").strip().splitlines()
    return lines[0][:limit] if lines else ""


def classify(result):
    """(trạng thái hiển thị, ghi chú) theo quy ước pytest + allure-pytest."""
    status = result.get("status")
    message = ANSI.sub("", (result.get("statusDetails") or {}).get("message") or "").strip()
    if status == "skipped" and message.startswith("XFAIL"):
        # "XFAIL BUG: mô tả\n\n<exception>" -> "BUG: mô tả"
        return KNOWN_BUG, first_line(message[len("XFAIL"):].strip(), 500)
    if message.startswith("XPASS") or "XPASS(strict)" in message:
        return FIXED, first_line(message.replace("[XPASS(strict)]", "").replace("XPASS", "", 1).strip(), 500)
    if status == "skipped":
        return SKIPPED, re.sub(r"^.*?Skipped:\s*", "", first_line(message, 500))[:120]
    if status == "passed":
        return PASSED, ""
    if status == "failed" and not message:
        # xfail(strict=True) mà test PASS -> pytest báo FAILED "[XPASS(strict)]", allure không có message.
        return FIXED, "Test PASS dù đánh dấu xfail(strict) - kiểm tra lại bug"
    return FAILED, first_line(message)


def build_rows(results):
    rows = []
    for result in results:
        labels = labels_of(result)
        path = test_path(result, labels)
        status, note = classify(result)
        name = result.get("name") or ""
        match = CASE_ID.match(name)
        rows.append({
            "module": module_of(path),
            "id": match.group(1) if match else None,
            "project": project_of(labels),
            "security": "security" in (labels.get("tag") or []),
            "title": CASE_ID.sub("", name),
            "status": status,
            "note": note,
            "start": result.get("start") or 0,
        })
    order = list(MODULES.values())
    rows.sort(key=lambda r: (order.index(r["module"]) if r["module"] in order else len(order), r["module"], r["start"]))

    # Gán ID cho test chưa có [ID] trong tên
    counters = Counter()
    for row in rows:
        if row["id"]:
            continue
        project = {"api": "API", "mobile": "MOB"}.get(row["project"], "UI")
        plain = re.sub(r"^(API|UI) - ", "", row["module"])
        plain = unicodedata.normalize("NFD", plain)
        plain = "".join(ch for ch in plain if not unicodedata.combining(ch)).replace("đ", "d").replace("Đ", "D")
        initials = "".join(word[0].upper() for word in re.split(r"[^A-Za-z]+", plain) if word)[:4]
        prefix = f"{project}-{initials}"
        counters[prefix] += 1
        row["id"] = f"{prefix}-{counters[prefix]:02d}"
    return rows


def esc(text):
    return str(text).replace("|", "\\|")


def render(rows, env_name, started_ms):
    count = lambda rs, s: sum(1 for r in rs if r["status"] == s)  # noqa: E731
    modules = list(dict.fromkeys(r["module"] for r in rows))
    started = datetime.fromtimestamp(started_ms / 1000, ZoneInfo("Asia/Ho_Chi_Minh"))
    when = f"{started.hour}:{started:%M:%S} {started.day}/{started.month}/{started.year}"

    md = (
        "# Danh mục Test Case\n\n"
        f"> Tự sinh bởi `.venv/bin/python scripts/gen_test_cases.py` từ lần chạy **{env_name}** lúc {when}. Đừng sửa tay.\n\n"
    )
    md += f"## Tổng quan\n\n| Module | Tổng | {' | '.join(STATUSES)} |\n|---|---|{'|'.join('---' for _ in STATUSES)}|\n"
    for module in modules:
        rs = [r for r in rows if r["module"] == module]
        md += f"| {module} | {len(rs)} | {' | '.join(str(count(rs, s) or '') for s in STATUSES)} |\n"
    md += f"| **Tổng** | **{len(rows)}** | {' | '.join(f'**{count(rows, s)}**' for s in STATUSES)} |\n\n"
    md += (
        "Chú thích: 🐞 test đúng nhưng app còn bug (đánh dấu `xfail(strict=True)` / `knownBug`) · "
        "❌ test fail (gồm lỗ hổng bảo mật cố ý để đỏ) · ⏭️ thiếu điều kiện (tài khoản / quyền ghi DB) · "
        "⚠️ test PASS dù đánh dấu bug (bug có thể đã được sửa).\n\n"
    )

    # Tổng hợp bug: xfail (bug đã biết) + test bảo mật (marker security) đang fail
    bugs = [r for r in rows if r["status"] in (KNOWN_BUG, FIXED)]
    security = [r for r in rows if r["status"] == FAILED and (r["security"] or SECURITY.search(r["title"]))]
    md += (
        f"## Bug phát hiện\n\n**{len(bugs)}** test đang ghi nhận bug của app (`xfail`) "
        f"và **{len(security)}** test bảo mật đang fail.\n\n"
    )
    if security:
        md += "### ⚠️ Lỗ hổng bảo mật\n\n| ID | Test case |\n|---|---|\n"
        for r in security:
            md += f"| {r['id']} | {esc(r['title'])} |\n"
        md += "\n"
    by_desc = {}
    for r in bugs:
        key = re.sub(r"^BUG:\s*", "", r["note"]) or "(không mô tả)"
        by_desc.setdefault(key, {"module": r["module"], "ids": []})["ids"].append(r["id"])
    md += (
        f"### Bug chức năng / giao diện ({len(by_desc)} bug, gom theo mô tả)\n\n"
        "| # | Module | Bug | Test |\n|---|---|---|---|\n"
    )
    for i, (desc, v) in enumerate(sorted(by_desc.items(), key=lambda item: item[1]["module"]), 1):
        md += f"| {i} | {v['module']} | {esc(desc)} | {', '.join(v['ids'])} |\n"
    md += "\n"

    for module in modules:
        md += f"## {module}\n\n| ID | Test case | Project | Kết quả | Ghi chú |\n|---|---|---|---|---|\n"
        for r in (x for x in rows if x["module"] == module):
            md += f"| {r['id']} | {esc(r['title'])} | {r['project']} | {r['status']} | {esc(r['note'])} |\n"
        md += "\n"
    return md


def main(argv=None):
    parser = argparse.ArgumentParser(description="Sinh TEST_CASES.md từ Allure results.")
    parser.add_argument("--results", type=Path, default=DEFAULT_RESULTS, help="Thư mục allure-results")
    parser.add_argument("--stdout", action="store_true", help="In ra màn hình thay vì ghi TEST_CASES.md")
    args = parser.parse_args(argv)

    results = load_latest_results(args.results) if args.results.is_dir() else []
    if not results:
        print(f"Chưa có kết quả Allure trong {args.results} - hãy chạy test trước.", file=sys.stderr)
        return 1

    rows = build_rows(results)
    started = min((r.get("start") or 0) for r in results)
    md = render(rows, TEST_ENV, started)
    modules = len({r["module"] for r in rows})
    if args.stdout:
        print(md)
    else:
        (ROOT / "TEST_CASES.md").write_text(md, encoding="utf-8")
        print(f"TEST_CASES.md: {len(rows)} test case, {modules} module ({TEST_ENV})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
