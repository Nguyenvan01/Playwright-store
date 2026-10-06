# ============================================================
# DATA LOADER: đọc dữ liệu JSON trong data/ và thay biến lúc chạy.
#   load_data("auth/login.json")              -> cả file
#   load_data("checkout/addresses.json#hcm")  -> 1 nhánh (nhánh lồng dùng dấu chấm: a.b.0)
# Luôn trả bản sao để test không vô tình sửa dữ liệu dùng chung.
# ============================================================
import json
import random
import re
import time
from copy import deepcopy

from config import ADMIN, BASE_URL, CUSTOMER, DATA_DIR, TEST_ENV

_cache = {}
_WHOLE_VAR = re.compile(r"^\$\{([^}]+)\}$")
_ANY_VAR = re.compile(r"\$\{([^}]+)\}")


def load_data(ref):
    file, _, pointer = ref.partition("#")
    if file not in _cache:
        full = DATA_DIR / file
        if not full.exists():
            raise ValueError(f"Không tìm thấy file dữ liệu: data/{file}")
        _cache[file] = json.loads(full.read_text(encoding="utf-8"))
    root = _cache[file]
    return deepcopy(get_path(root, pointer, ref) if pointer else root)


def list_data_files(directory, suffix=".json"):
    """Liệt kê file trong 1 thư mục con của data/, sắp theo tên."""
    return sorted(
        f"{directory}/{path.name}"
        for path in (DATA_DIR / directory).iterdir()
        if path.name.endswith(suffix) and not path.name.startswith("~$")
    )


def get_path(obj, dotted, ref):
    current = obj
    for key in dotted.split("."):
        if isinstance(current, list) and key.isdigit() and int(key) < len(current):
            current = current[int(key)]
        elif isinstance(current, dict) and key in current:
            current = current[key]
        else:
            raise ValueError(f'Không có dữ liệu "{dotted}" (tham chiếu: {ref})')
    return current


# ---------------------------------------------------------------------------
# Thay biến trong dữ liệu
# ---------------------------------------------------------------------------

def base_context():
    """Context mặc định: cấu hình môi trường (đọc từ .env / .env.prod)."""
    return {
        "env": {
            "name": TEST_ENV,
            "baseURL": BASE_URL,
            "customer": dict(CUSTOMER),
            "admin": dict(ADMIN),
        }
    }


def uid():
    return f"{int(time.time() * 1000)}{random.randint(0, 999)}"


def resolve_data(value, ctx):
    """Thay biến trong chuỗi / dict / list (đệ quy):
    "${product.name}"                  -> giá trị trong context (giữ kiểu nếu cả chuỗi là 1 biến)
    "Đã thêm \"${product.name}\""      -> nối chuỗi
    "${uid}"                           -> chuỗi số duy nhất mỗi lần gọi
    "@data:checkout/addresses.json#hcm" -> nạp dữ liệu từ file khác
    """
    if isinstance(value, str):
        return _resolve_string(value, ctx)
    if isinstance(value, list):
        return [resolve_data(item, ctx) for item in value]
    if isinstance(value, dict):
        return {key: resolve_data(item, ctx) for key, item in value.items()}
    return value


def _resolve_string(text, ctx):
    if text.startswith("@data:"):
        return resolve_data(load_data(text[len("@data:"):]), ctx)
    whole = _WHOLE_VAR.match(text)
    if whole:
        return _lookup(whole.group(1), ctx)
    return _ANY_VAR.sub(lambda m: _to_text(_lookup(m.group(1), ctx)), text)


def _to_text(value):
    # Giống String(x) của JS: true/false/null thay vì True/False/None.
    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        return "null"
    return str(value)


def _lookup(expr, ctx):
    key = expr.strip()
    if key == "uid":
        return uid()
    return get_path(ctx, key, f"${{{key}}}")


def mask_secrets(text):
    """Che mật khẩu trong chuỗi trước khi in ra log / report / tên step."""
    out = str(text)
    for secret in (CUSTOMER["password"], ADMIN["password"]):
        if secret:
            out = out.replace(secret, "***")
    return out
