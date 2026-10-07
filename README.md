# cloth-store-e2e — Hybrid Test Automation Framework (Python + Playwright)

Bộ test tự động cho website bán quần áo **Đạt Hoàng**
(`Web bán quần áo/Đồ án Quần áo` — React/Vite :3000 + Express API :5000).

Framework theo mô hình **Hybrid**: POM + Keyword-Driven + Data-Driven, bổ sung logging có cấu trúc,
taxonomy lỗi, failure evidence, JUnit XML và Allure reporting.

> Đưa dự án lên GitHub / cài trên máy khác: xem [HUONG_DAN_GITHUB.md](HUONG_DAN_GITHUB.md).

## Luồng thực thi

```text
data/scenarios/*.xlsx (TestSteps + TestData) → hybrid_reader → template_binding → pytest item
data/**/*.json (data-driven)                 → load_data → case_params          → pytest item
                                                                                     ↓
fixture (page, k, ctx) → Driver Script / test → keyword → POM → Playwright → browser
                              │                    │                 │
                              ├→ structured log    ├→ Allure step    └→ auto-wait + expect
                              ↓
                        pytest failure hook
                              ↓
          screenshot + page source + URL + trace + video + error category
                              ↓
                      JUnit XML + Allure Results
```

| Tầng | Thư mục | Chứa gì | Không chứa |
|---|---|---|---|
| **POM** | `pages/` | Locator, thao tác nguyên tử (fill, click 1 nút) | Assertion nghiệp vụ, dữ liệu test |
| **Keyword** | `keywords/` | Bước nghiệp vụ + kiểm tra; mỗi keyword = 1 Allure step + 1 dòng log | Locator thô, dữ liệu cứng |
| **Driver Script** | `drivers/` | Chạy kịch bản đã binding, log từng bước, phân loại lỗi rồi ném lại | Logic nghiệp vụ |
| **Data** | `data/` | Test case, đầu vào, kết quả mong đợi, kịch bản Excel | Code |
| **Utils** | `utils/` | Logging, taxonomy lỗi, evidence, đọc Excel/JSON, binding, API client | — |

Danh mục đầy đủ **553 keyword**: [KEYWORDS.md](KEYWORDS.md) (tự sinh: `python scripts/gen_keywords_doc.py`).

## Cấu trúc thư mục

```text
config.py                       # đọc .env theo TEST_ENV, URL, tài khoản test, timeout, chặn ghi DB remote
pytest.ini                      # marker, thư mục test, mẫu tên file
requirements.txt
drivers/driver_script.py        # validate_steps + execute_steps cho kịch bản keyword-driven
keywords/                       # kw_common, kw_auth, kw_catalog, kw_cart, kw_checkout, kw_account,
                                # kw_listing, kw_product, kw_content, kw_admin, kw_admin_catalog,
                                # kw_admin_sales, kw_admin_marketing, kw_admin_ops
  base_keywords.py              # BaseKeywords, @keyword, self.step()
  __init__.py                   # Keywords (fixture k) + KEYWORD_MAP (registry tường minh)
pages/                          # POM: page_objects.py gom tất cả; components/ storefront/ account/ admin/
utils/
  logging_config.py             # TC_ID | Step | Action | Target | Result, TEST_LOG_LEVEL
  error_classifier.py           # taxonomy lỗi dùng chung cho log / JUnit / Allure
  artifact_manager.py           # thư mục evidence theo run_id, tên file an toàn
  hybrid_reader.py              # đọc TestSteps/TestData từ Excel
  template_binding.py           # gắn {placeholder} của 1 dòng TestData vào template
  data_loader.py                # load_data (JSON), resolve_data (${...}, @data:), mask_secrets
  cases.py                      # case_params: requires -> skip, knownBug -> xfail, tags -> marker
  api_client.py, storage.py, factories.py, assertions.py, routes.py, messages.py
data/                           # mỗi khu vực 1 thư mục JSON: auth/ catalog/ cart/ checkout/ account/ admin-*/ api/ ...
  scenarios/*.xlsx              # kịch bản keyword-driven (Hybrid)
tests/
  conftest.py                   # lifecycle: log, evidence hook, browser context, write guard, fixture
  framework/                    # unit test của framework (không cần app): logging, taxonomy, hợp đồng Hybrid
  api/                          # REST API: health, sản phẩm, lọc/sắp xếp, auth, admin
  e2e/                          # UI: smoke/ auth/ catalog/ cart/ checkout/ mobile/ storefront/ account/
                                #     admin/ admin_catalog/ admin_sales/ admin_marketing/ admin_ops/
    keyword_driven/             # chạy toàn bộ data/scenarios/*.xlsx
  failure_demo/                 # demo cố tình FAIL để quan sát evidence (không nằm trong suite mặc định)
scripts/                        # gen_keywords_doc.py, gen_test_cases.py
artifacts/<env>/                # logs/ screenshots/ page_sources/ traces/ junit/ allure-results/ (không commit)
```

## Môi trường

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m playwright install chromium
cp .env.prod.example .env.prod  # production (mặc định) - điền tài khoản test
cp .env.example .env            # local (tuỳ chọn)
```

Allure CLI cài riêng (`brew install allure`) để chuyển `allure-results` thành báo cáo HTML.

**Mặc định test chạy trên web thật https://dat-hoang-store.vercel.app** (`TEST_ENV=prod` → `.env.prod`).
Muốn chạy trên máy local thì đặt `TEST_ENV=local` (→ `.env`, localhost:3000 + localhost:5000).
Mỗi môi trường có storageState (`.auth/<env>-*.json`) và thư mục `artifacts/<env>/` riêng.

## Cách chạy

Từ thư mục project (`py` = `.venv/bin/python`), mọi lệnh dưới đây chạy trên https://dat-hoang-store.vercel.app:

| Lệnh | Mô tả |
|---|---|
| `py -m pytest --collect-only -q` | Kiểm tra dữ liệu + thu thập test, không mở browser |
| `py -m pytest` | Toàn bộ suite (framework + api + e2e + mobile) |
| `py -m pytest -m smoke` | Chỉ test `smoke` |
| `py -m pytest -m core` | Unit test framework (không cần app) |
| `py -m pytest -m api` / `-m e2e` / `-m mobile` / `-m keyword` | Theo nhóm |
| `py -m pytest -n auto` | Chạy song song (pytest-xdist) |
| `py -m pytest --headed --slowmo 600 -n 0` | Hiện trình duyệt, chậm 0,6s/thao tác để quan sát |
| `PWDEBUG=1 py -m pytest tests/e2e/cart -k remove` | Playwright Inspector, chạy từng bước |
| `py -m pytest tests/e2e/cart -k "remove_item"` | Chạy 1 test |
| `py -m pytest tests/e2e/keyword_driven -k KD-SHOP-02` | Chạy 1 kịch bản Excel theo case_id |

Chạy trên máy local thay vì web thật (mở app trước, hoặc đặt `START_SERVERS=1` trong `.env` để framework tự bật):

```bash
# terminal 1: cd "<APP_DIR>/backend"  && npm run dev
# terminal 2: cd "<APP_DIR>/frontend" && npm run dev
TEST_ENV=local py -m pytest -m smoke
```

### Chạy tự động trên GitHub Actions

[.github/workflows/e2e.yml](.github/workflows/e2e.yml) chạy toàn bộ suite (trừ nhóm `security`) trên
https://dat-hoang-store.vercel.app mỗi khi **push** hoặc mở **PR** vào `main`. Chạy tay một nhóm khác:
tab **Actions → E2E production → Run workflow**, nhập marker (vd `smoke`, `security`).

- Tài khoản test lấy từ GitHub Secrets: `E2E_CUSTOMER_EMAIL`, `E2E_CUSTOMER_PASSWORD`, `E2E_ADMIN_EMAIL`,
  `E2E_ADMIN_PASSWORD` (thiếu secret → test cần đăng nhập tự skip).
- Kết quả: bảng tóm tắt ở trang của lần chạy; JUnit, Allure, log, ảnh, trace tải ở mục **Artifacts**.

Đổi mức log:

```bash
TEST_LOG_LEVEL=DEBUG py -m pytest -m smoke   # DEBUG ghi cả lúc bắt đầu mỗi keyword
```

Demo chủ đích FAIL (offline, không cần app):

```bash
py -m pytest tests/failure_demo/demo_failure_evidence.py
```

Báo cáo:

```bash
allure generate artifacts/prod/allure-results -o artifacts/prod/allure-report --clean
allure open artifacts/prod/allure-report
py scripts/gen_test_cases.py            # TEST_CASES.md từ lần chạy gần nhất
py scripts/gen_keywords_doc.py          # KEYWORDS.md
```

Khi chạy trên production:
- **Không ghi dữ liệu**: `E2E_ALLOW_WRITE=1` bị bỏ qua với URL không phải localhost, trừ khi đặt thêm
  `E2E_ALLOW_WRITE_REMOTE=1`. Tạo đơn / đăng ký luôn được mock bằng `page.route`.
- Dùng **tài khoản test riêng**, không dùng tài khoản khách thật.
- Test vẫn mở trang sản phẩm thật → `view_count` của sản phẩm tăng nhẹ.
- Retry 1 lần (pytest-rerunfailures) và timeout rộng hơn để chịu cold start của serverless.

## Quy tắc lỗi và bằng chứng

- Driver Script thêm `case_id`, step, keyword, args và error category vào exception (`add_note`) rồi `raise` lại.
- Keyword log `START/PASS/FAIL` kèm category; không bắt lỗi để trả boolean.
- Pytest hook là đầu mối duy nhất chụp screenshot và page source; pytest-playwright giữ trace + video khi FAIL.
- Fixture `page` là đầu mối duy nhất mở/đóng browser context.
- Lỗi thu evidence chỉ được ghi WARNING, không che traceback của test.
- Không log password, token hoặc dữ liệu bí mật (`mask_secrets` che mật khẩu trong tên step và log).

Taxonomy lỗi: `ASSERTION_FAILED`, `TIMEOUT`, `LOCATOR_AMBIGUOUS`, `NETWORK_ERROR`, `BROWSER_CLOSED`,
`PLAYWRIGHT_ERROR`, `DATA_OR_CONTRACT_ERROR`, `UNEXPECTED_ERROR`.

## Viết test — 3 cách

**1. Thêm dữ liệu cho test có sẵn (không cần code).** Thêm 1 phần tử vào file JSON tương ứng, vd. `data/auth/login.json`:

```json
{ "id": "LOGIN-V06", "title": "Email có khoảng trắng", "identifier": "a b@x.com", "password": "123456",
  "errors": ["Email hoặc số điện thoại không hợp lệ"] }
```

Mỗi case có thể có: `tags` (`["@smoke"]`), `requires` (`customer` | `admin` | `allowWrite` → thiếu thì skip),
`knownBug` (mô tả bug → `xfail(strict=True)`).

**2. Kịch bản keyword-driven trong Excel (không cần code).** Mỗi file `data/scenarios/*.xlsx` có 2 sheet:

| Sheet | Cột |
|---|---|
| `TestSteps` (template) | `template_id` \| `step` (1, 2, 3... liên tục) \| `keyword` (`nhóm.tênKeyword`) \| `args` (mảng JSON) \| `note` |
| `TestData` (1 dòng = 1 test) | `case_id` \| `template_id` \| `title` \| `tags` \| `requires` \| `known_bug` \| cột placeholder... |

```text
TestSteps:  T-REMOVE | 1 | catalog.openProduct | ["${product.slug}"]
            T-REMOVE | 2 | catalog.addToCart   | ["{size}"]
            T-REMOVE | 3 | cart.openCart       |
            T-REMOVE | 4 | cart.removeItem     | ["${product.name}"]
            T-REMOVE | 5 | cart.verifyCartEmpty|
TestData:   KD-SHOP-05 | T-REMOVE | Thêm rồi xóa khỏi giỏ | @smoke | | | ${size.label}   ← cột "size"
```

- `{cot}`: gắn từ dòng TestData lúc collection (phải chiếm toàn bộ 1 phần tử của `args`).
  Một template + nhiều dòng TestData = nhiều test, không lặp lại các bước.
- `${...}`: biến runtime (xem bảng dưới), thay lúc chạy.
- Keyword sai tên, step sai thứ tự, args không phải JSON, placeholder thiếu → báo lỗi lúc collection,
  trước khi mở browser. Kịch bản phải có ít nhất 1 bước kiểm tra (`verify*`).

**3. Test bằng code** khi cần logic phức tạp — vẫn dùng keyword + data:

```python
from utils.cases import case_params
from utils.data_loader import load_data

@pytest.mark.parametrize("case", case_params(load_data("my/feature.json")))
def test_feature(k, case):
    k.catalog.open_home()
    ...
```

### Biến trong dữ liệu

| Cú pháp | Giá trị |
|---|---|
| `${product.name}`, `${product.slug}`, `${size.label}` | Sản phẩm thật còn hàng, lấy qua API lúc chạy |
| `${productFirstWord}` | Từ đầu tiên trong tên sản phẩm |
| `${env.customer.email}`, `${env.customer.password}`, `${env.admin.*}` | Tài khoản test trong `.env*` |
| `${uid}` | Chuỗi số duy nhất (email không trùng...) |
| `"@data:checkout/addresses.json#hcm"` | Nạp dữ liệu từ file khác (cả giá trị phải là chuỗi này) |

### Thêm keyword mới

1. (Nếu cần) thêm locator vào Page Object trong `pages/`.
2. Thêm method vào nhóm phù hợp trong `keywords/kw_*.py`: decorator `@keyword("tenCamelCase")`,
   **docstring 1 dòng** tiếng Việt và thân bọc trong `with self.step(...)`.
3. `python scripts/gen_keywords_doc.py` để cập nhật `KEYWORDS.md`.

## Quy ước

- Thân test ưu tiên gọi keyword (`k`), chỉ dùng page object (`po`) trực tiếp cho assertion đặc thù.
  Docstring dòng đầu của test = tiêu đề tiếng Việt hiển thị trong Allure.
- **Locator chỉ khai báo trong POM**, ưu tiên `get_by_role` / `get_by_label` / `get_by_placeholder`.
  Một số nút icon của app chưa có `aria-label` (giỏ hàng, tài khoản, menu mobile) nên tạm nhận diện qua SVG —
  nên bổ sung `aria-label` hoặc `data-testid` trong app rồi cập nhật `pages/components/header.py`.
- **Dữ liệu và kết quả mong đợi** để trong `data/`, không viết cứng trong test.
- **Marker**: `smoke`, `security`, `api`, `e2e`, `mobile`, `keyword`, `core` → lọc bằng `-m`.
- **Đăng nhập**: `pytestmark = pytest.mark.role("customer")` (hoặc `"admin"`) — conftest đăng nhập qua API 1 lần,
  thiếu tài khoản thì skip. Trong kịch bản Excel dùng keyword `auth.restoreSession`.
- **Dữ liệu ghi** (đăng ký, tạo đơn, thêm/sửa/xóa admin...) luôn được **mock** bằng `k.common.mock_write(...)`,
  kiểm tra payload bằng `k.common.verify_request(...)`. Trang cần dữ liệu mà production chưa có dùng
  `k.common.mock_get(...)` với dữ liệu mẫu trong `data/`.
- **Lưới an toàn write guard** (trong fixture `page`): khi `E2E_ALLOW_WRITE=0`, mọi request POST/PUT/DELETE tới
  `/api/**` không được mock (trừ đăng nhập/đăng xuất) đều bị chặn và trả 418 — test quên mock sẽ fail chứ không ghi
  vào DB thật. Backend local dùng chung DB với production — chỉ bật `E2E_ALLOW_WRITE=1` khi dùng DB test riêng.
- **Bug đã biết**: `knownBug` trong dữ liệu hoặc `known_bug(request, "...")` trong code → `xfail(strict=True)`.
  Khi bug được sửa, pytest báo `XPASS(strict)` → xóa đánh dấu.

## Danh mục test case & bug

Toàn bộ test case (ID, module, kết quả) và **danh sách bug đã phát hiện** nằm trong [TEST_CASES.md](TEST_CASES.md),
tự sinh từ lần chạy gần nhất:

```bash
py -m pytest && py scripts/gen_test_cases.py
```

### ⚠️ Lỗ hổng bảo mật — test security cố ý để FAIL (không đánh dấu xfail)

1. **Mật khẩu cứng admin**: backend chấp nhận `admin123` / `manager123` / `staff123` cho **mọi tài khoản admin**
   (`backend/src/controllers/adminController.js` → `adminLogin`, và `backend/src/routes/adminAuth.js`).
   Đã xác nhận trên production. Sửa: gỡ đoạn `plainValid`, chỉ dùng `bcrypt.compare`.
2. **Upload không cần đăng nhập**: `POST /api/admin/upload` khai báo trước `router.use(authMiddleware)`
   (`backend/src/routes/admin.js:20`). Sửa: chuyển route xuống dưới `authMiddleware`.

Các vấn đề phân quyền khác (không kiểm thử tự động vì cần ghi dữ liệu thật): không có kiểm tra quyền theo vai trò
(nhân viên `staff`/`warehouse` làm được mọi thứ, kể cả tạo admin); API tạo/sửa nhân viên trả về cả hash mật khẩu
(`SELECT *`); tạo khách hàng với mật khẩu `admin123`/`manager123`/`staff123` thì lưu **plaintext**.
