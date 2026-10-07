# ============================================================
# PYTEST LIFECYCLE
# - pytest_configure: tạo thư mục evidence, cấu hình log, JUnit, Allure, trace, retry.
# - Fixture tạo browser context riêng cho mỗi test (pytest-playwright), set timeout, chặn ghi DB.
# - Hook thu evidence khi call FAIL: screenshot + HTML + URL + category.
# - Lỗi evidence chỉ ghi WARNING, không che lỗi test gốc.
# - Không log password, token hoặc dữ liệu bí mật.
# ============================================================
import json
import logging
import os
import subprocess
import time
import urllib.request
from datetime import datetime
from urllib.parse import urlparse

import allure
import pytest
from playwright.sync_api import expect

from config import (
    ACTION_TIMEOUT,
    ADMIN,
    ALLOW_WRITE,
    API_URL,
    APP_DIR,
    ARTIFACTS_DIR,
    AUTH_FILES,
    BASE_URL,
    CUSTOMER,
    DESKTOP_VIEWPORT,
    EXPECT_TIMEOUT,
    IS_CI,
    IS_LOCAL,
    LOCALE,
    NAVIGATION_TIMEOUT,
    START_SERVERS,
    TEST_ENV,
    TIMEZONE,
)
from keywords import Keywords
from utils.api_client import ApiClient
from utils.assertions import current_page
from utils.artifact_manager import create_artifact_layout, safe_artifact_name
from utils.cases import case_title
from utils.data_loader import base_context
from utils.error_classifier import classify_report_text
from utils.factories import build_customer
from utils.logging_config import LOGGER_NAME, configure_logging, current_tc_id, event_context
from utils.storage import STORAGE_KEYS, has_admin_auth, has_customer_auth, write_storage_state

# Request ghi vẫn cho đi qua (đăng nhập/đăng xuất không đổi dữ liệu).
WRITE_ALLOWLIST = ("/api/auth/login", "/api/admin/login", "/api/admin/logout")
ROLE_CHECKS = {
    "customer": (has_customer_auth, "Chưa có tài khoản test (xem .env)"),
    "admin": (has_admin_auth, "Cần E2E_ADMIN_EMAIL/PASSWORD trong .env"),
}


def _worker_id(config):
    return getattr(config, "workerinput", {}).get("workerid", "")


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    # Tiến trình chính sinh run_id; worker xdist kế thừa qua biến môi trường.
    run_id = os.environ.setdefault("E2E_RUN_ID", datetime.now().strftime("%Y%m%d_%H%M%S"))
    layout = create_artifact_layout(ARTIFACTS_DIR, run_id)
    worker = _worker_id(config)
    logger, log_path = configure_logging(
        layout.logs, f"{run_id}_{worker}" if worker else run_id
    )
    config._e2e_layout = layout
    config._e2e_log_path = log_path

    # Báo cáo mặc định (người dùng truyền tham số riêng thì giữ nguyên).
    if not config.option.xmlpath:
        config.option.xmlpath = str(layout.junit / "results.xml")
    if hasattr(config.option, "allure_report_dir") and not config.option.allure_report_dir:
        config.option.allure_report_dir = str(layout.allure_results)
    if config.option.tracing == "off":
        config.option.tracing = "retain-on-failure"
    if config.option.video == "off":
        config.option.video = "retain-on-failure"
    if config.option.output == "test-results":
        config.option.output = str(layout.traces)
    # Môi trường remote (Vercel serverless) có thể cold start -> cho retry.
    rerun_given = any(arg.startswith("--reruns") for arg in config.invocation_params.args)
    if hasattr(config.option, "reruns") and not rerun_given:
        config.option.reruns = 2 if IS_CI else (0 if IS_LOCAL else 1)
    if os.getenv("SLOW_MO") and not config.option.slowmo:
        config.option.slowmo = float(os.environ["SLOW_MO"])

    expect.set_options(timeout=EXPECT_TIMEOUT)
    logger.info(
        f"Bắt đầu pytest session; env={TEST_ENV}, base_url={BASE_URL}, allow_write={ALLOW_WRITE}",
        extra=event_context(action="pytest_session", result="START"),
    )


def pytest_collection_modifyitems(config, items):
    """Gắn marker theo thư mục: tests/api -> api, tests/e2e/mobile -> mobile, tests/e2e -> e2e."""
    for item in items:
        path = item.path.as_posix()
        if "/tests/api/" in path:
            item.add_marker(pytest.mark.api)
        elif "/tests/e2e/mobile/" in path:
            item.add_marker(pytest.mark.mobile)
        elif "/tests/e2e/" in path:
            item.add_marker(pytest.mark.e2e)
        if "/tests/e2e/keyword_driven/" in path:
            item.add_marker(pytest.mark.keyword)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Thu bằng chứng đúng một lần ở call phase và giữ nguyên kết quả report."""
    outcome = yield
    report = outcome.get_result()
    setattr(item, "rep_" + report.when, report)
    if report.when != "call" or not report.failed:
        return

    category = classify_report_text(report.longreprtext)
    report.user_properties.append(("error_category", category))
    logger = logging.getLogger(LOGGER_NAME)
    logger.error(
        f"Pytest item thất bại; category={category}",
        extra=event_context(tc_id=item.name, action="pytest_report", result="FAIL"),
    )
    allure.dynamic.label("error_category", category)
    allure.attach(category, "error-category", allure.attachment_type.TEXT)

    page = item.funcargs.get("page") if hasattr(item, "funcargs") else None
    if page is None or page.is_closed():
        return
    layout = item.config._e2e_layout
    name = safe_artifact_name(item.nodeid)
    try:
        screenshot = page.screenshot(full_page=True)
        screenshot_path = layout.screenshots / f"{name}.png"
        screenshot_path.write_bytes(screenshot)
        allure.attach(screenshot, "failure-screenshot", allure.attachment_type.PNG)

        source = page.content()
        source_path = layout.page_sources / f"{name}.html"
        source_path.write_text(source, encoding="utf-8")
        allure.attach(source, "page-source", allure.attachment_type.HTML)
        allure.attach(page.url, "current-url", allure.attachment_type.TEXT)
        logger.info(
            f"Đã lưu evidence: {screenshot_path.name}, {source_path.name}",
            extra=event_context(tc_id=item.name, action="collect_evidence", result="PASS"),
        )
    except Exception as evidence_error:
        logger.warning(
            f"Không thu được đầy đủ evidence: {evidence_error}",
            extra=event_context(tc_id=item.name, action="collect_evidence", result="WARNING"),
        )


def pytest_sessionfinish(session, exitstatus):
    logging.getLogger(LOGGER_NAME).info(
        f"Kết thúc pytest session; exitstatus={exitstatus}",
        extra=event_context(action="pytest_session", result="END"),
    )


# ---------------------------------------------------------------------------
# Ngữ cảnh test: TC_ID cho log, tiêu đề Allure
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def _test_context(request):
    """TC_ID = id của data case (nếu có) hoặc tên test; tiêu đề Allure lấy từ case/docstring."""
    params = getattr(getattr(request.node, "callspec", None), "params", {})
    case = params.get("case")
    if isinstance(case, dict) and case.get("id") and case.get("title"):
        tc_id, title = case["id"], case_title(case)
    else:
        doc = (request.function.__doc__ or "").strip().splitlines()
        tc_id, title = request.node.name, doc[0] if doc else None
    if title:
        allure.dynamic.title(title)
    allure.dynamic.parameter("env", TEST_ENV)
    token = current_tc_id.set(tc_id)
    yield
    current_tc_id.reset(token)


# ---------------------------------------------------------------------------
# Web server local (START_SERVERS=1): tự chạy `npm run dev` cho backend + frontend
# ---------------------------------------------------------------------------

def _is_up(url):
    try:
        with urllib.request.urlopen(url, timeout=2):
            return True
    except Exception:
        return False


@pytest.fixture(scope="session", autouse=True)
def _web_servers():
    """Chạy song song (-n) thì nên bật server trước; fixture chỉ tự bật khi server chưa chạy."""
    if not START_SERVERS:
        yield
        return
    processes = []
    for folder, url in ((f"{APP_DIR}/backend", f"{API_URL}/health"), (f"{APP_DIR}/frontend", BASE_URL)):
        if _is_up(url):
            continue  # reuseExistingServer
        processes.append(subprocess.Popen(["npm", "--prefix", folder, "run", "dev"]))
        deadline = time.monotonic() + 120
        while not _is_up(url):
            if time.monotonic() > deadline:
                raise RuntimeError(f"Server không lên sau 120s: {url}")
            time.sleep(1)
    yield
    for process in processes:
        process.terminate()


# ---------------------------------------------------------------------------
# Đăng nhập sẵn: đăng nhập qua API (nhanh, ổn định) rồi ghi token vào storageState.
# Nếu không có tài khoản -> ghi state rỗng, các test liên quan sẽ tự skip.
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def auth_states(playwright):
    request = playwright.request.new_context()
    try:
        api = ApiClient(request)
        if CUSTOMER["email"] and CUSTOMER["password"]:
            auth = api.customer_login(CUSTOMER["email"], CUSTOMER["password"])
        elif ALLOW_WRITE:
            auth = api.register_customer(build_customer())
        else:
            auth = None
        write_storage_state(
            AUTH_FILES["customer"],
            {
                STORAGE_KEYS["customerToken"]: auth["token"],
                STORAGE_KEYS["customerUser"]: json.dumps(auth["user"], ensure_ascii=False),
            }
            if auth
            else {},
        )

        if ADMIN["email"] and ADMIN["password"]:
            admin = api.admin_login(ADMIN["email"], ADMIN["password"])
            write_storage_state(AUTH_FILES["admin"], {STORAGE_KEYS["adminToken"]: admin["token"]})
        else:
            write_storage_state(AUTH_FILES["admin"], {})
    finally:
        request.dispose()
    return AUTH_FILES


# ---------------------------------------------------------------------------
# Browser context / page
# ---------------------------------------------------------------------------

@pytest.fixture
def browser_context_args(browser_context_args, request):
    """Mở rộng context mặc định của pytest-playwright: base_url, locale, viewport, phiên đăng nhập.
    Phiên đăng nhập chọn bằng marker: @pytest.mark.role("customer") hoặc pytestmark = ...("admin")."""
    args = {
        **browser_context_args,
        "base_url": BASE_URL,
        "locale": LOCALE,
        "timezone_id": TIMEZONE,
    }
    if "viewport" not in browser_context_args:
        args["viewport"] = DESKTOP_VIEWPORT
    marker = request.node.get_closest_marker("role")
    if marker:
        role = marker.args[0]
        if role not in ROLE_CHECKS:
            raise ValueError(f"role không hợp lệ: {role!r}")
        request.getfixturevalue("auth_states")
        check, reason = ROLE_CHECKS[role]
        if not check():
            pytest.skip(reason)
        args["storage_state"] = str(AUTH_FILES[role])
    return args


@pytest.fixture
def context(new_context):
    context = new_context()
    context.set_default_timeout(ACTION_TIMEOUT)
    context.set_default_navigation_timeout(NAVIGATION_TIMEOUT)
    return context


@pytest.fixture
def page(context, request):
    """Page mới cho mỗi test. Khi E2E_ALLOW_WRITE=0: chặn mọi request ghi dữ liệu thật.
    Guard đăng ký TRƯỚC mọi mock trong test -> mock của test (đăng ký sau) luôn được ưu tiên."""
    page = context.new_page()
    blocked = []
    if not ALLOW_WRITE:
        def guard(route):
            req = route.request
            path = urlparse(req.url).path
            if req.method in ("GET", "OPTIONS") or path.endswith(WRITE_ALLOWLIST):
                return route.fallback()
            blocked.append(f"{req.method} {path}")
            route.fulfill(status=418, json={"success": False, "message": "[E2E] Đã chặn ghi dữ liệu thật"})

        page.route("**/api/**", guard)
    token = current_page.set(page)
    yield page
    current_page.reset(token)
    if blocked:
        request.node.user_properties.append(("write-blocked", ", ".join(blocked)))
        allure.attach("\n".join(blocked), "write-blocked", allure.attachment_type.TEXT)


# ---------------------------------------------------------------------------
# Fixture nghiệp vụ
# ---------------------------------------------------------------------------

@pytest.fixture
def api(playwright):
    """ApiClient gọi backend Express (không cần browser)."""
    request = playwright.request.new_context()
    yield ApiClient(request)
    request.dispose()


@pytest.fixture
def k(page, api):
    """Thư viện keyword (tầng nghiệp vụ) - cách viết test chính."""
    return Keywords(page, api)


@pytest.fixture
def po(k):
    """Page Object - dùng khi cần locator trực tiếp trong test."""
    return k.po


@pytest.fixture(scope="session")
def purchasable(playwright):
    """1 sản phẩm thật (lấy qua API) có size còn hàng - dùng chung trong cả worker."""
    request = playwright.request.new_context()
    try:
        return ApiClient(request).find_purchasable_product()
    finally:
        request.dispose()


@pytest.fixture
def ctx(purchasable):
    """Context thay biến ${...} cho dữ liệu: env, product, size, productFirstWord."""
    product = purchasable["product"]
    return {
        **base_context(),
        "product": product,
        "size": purchasable["size"],
        "productFirstWord": product["name"].split(" ")[0],
    }
