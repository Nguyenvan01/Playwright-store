# ============================================================
# CẤU HÌNH DỰ ÁN: đường dẫn, môi trường, URL và timeout dùng chung.
# Chọn môi trường bằng biến TEST_ENV:
#   (không đặt) -> .env       (local: localhost:3000 + localhost:5000)
#   prod        -> .env.prod  (https://dat-hoang-store.vercel.app)
# Expected thuộc dữ liệu/đặc tả; cấu hình không được sửa expected để làm test xanh.
# ============================================================
import os
import re
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
SCENARIO_DIR = DATA_DIR / "scenarios"

TEST_ENV = os.getenv("TEST_ENV", "local")
load_dotenv(ROOT / (".env" if TEST_ENV == "local" else f".env.{TEST_ENV}"))

# Mỗi môi trường có thư mục báo cáo / evidence riêng.
ARTIFACTS_DIR = ROOT / "artifacts" / TEST_ENV


def _flag(name):
    return os.getenv(name, "") in {"1", "true"}


BASE_URL = os.getenv("BASE_URL") or "http://localhost:3000"
IS_LOCAL = bool(re.match(r"^https?://(localhost|127\.0\.0\.1)(:\d+)?", BASE_URL))
API_URL = (os.getenv("API_URL") or "http://localhost:5000/api").rstrip("/")
APP_DIR = os.getenv("APP_DIR") or "/Users/ccm/Documents/Dự án cá nhân/Web bán quần áo/Đồ án Quần áo"
START_SERVERS = IS_LOCAL and _flag("START_SERVERS")
IS_CI = bool(os.getenv("CI"))

# Chặn ghi dữ liệu thật (tạo user, đơn hàng) lên môi trường không phải localhost,
# trừ khi xác nhận rõ ràng bằng E2E_ALLOW_WRITE_REMOTE=1.
ALLOW_WRITE = _flag("E2E_ALLOW_WRITE") and (IS_LOCAL or _flag("E2E_ALLOW_WRITE_REMOTE"))

CUSTOMER = {
    "email": os.getenv("E2E_CUSTOMER_EMAIL", ""),
    "password": os.getenv("E2E_CUSTOMER_PASSWORD", ""),
}
ADMIN = {
    "email": os.getenv("E2E_ADMIN_EMAIL", ""),
    "password": os.getenv("E2E_ADMIN_PASSWORD", ""),
}

# File storageState cho từng vai trò (sinh bởi fixture auth_states trong tests/conftest.py).
AUTH_DIR = ROOT / ".auth"
AUTH_FILES = {
    "customer": AUTH_DIR / f"{TEST_ENV}-customer.json",
    "admin": AUTH_DIR / f"{TEST_ENV}-admin.json",
}

# Timeout (mili giây) theo quy ước của Playwright.
# Môi trường remote (Vercel serverless) có thể cold start -> nới timeout.
TEST_TIMEOUT = 30_000 if IS_LOCAL else 45_000
EXPECT_TIMEOUT = 7_000
ACTION_TIMEOUT = 10_000
NAVIGATION_TIMEOUT = 20_000

DESKTOP_VIEWPORT = {"width": 1440, "height": 900}
MOBILE_DEVICE = "Pixel 7"
LOCALE = "vi-VN"
TIMEZONE = "Asia/Ho_Chi_Minh"
