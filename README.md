# cloth-store-e2e

Bộ test tự động (Playwright + TypeScript) cho website bán quần áo **Đạt Hoàng**
(`Web bán quần áo/Đồ án Quần áo` — React/Vite :3000 + Express API :5000).

> Đưa dự án lên GitHub / cài trên máy khác: xem [HUONG_DAN_GITHUB.md](HUONG_DAN_GITHUB.md).

## Cài đặt

```bash
npm install
npx playwright install chromium
cp .env.example .env            # local
cp .env.prod.example .env.prod  # production
```

## Chạy test

Mở app trước (hoặc đặt `START_SERVERS=1` trong `.env` để Playwright tự bật):

```bash
# terminal 1: cd "<APP_DIR>/backend"  && npm run dev
# terminal 2: cd "<APP_DIR>/frontend" && npm run dev
```

| Lệnh | Mô tả |
|---|---|
| `npm test` | Chạy toàn bộ (api + chromium + mobile) |
| `npm run test:smoke` | Chỉ các test gắn tag `@smoke` |
| `npm run test:api` | Chỉ test REST API |
| `npm run test:keyword` | Chỉ các kịch bản keyword-driven (`test-data/scenarios`) |
| `npm run test:e2e` | UI test trên Desktop Chrome |
| `npm run test:mobile` | UI test trên Pixel 7 |
| `npm run test:headed` | Chạy có hiện trình duyệt |
| `npm run test:ui` | Playwright UI mode (debug trực quan) |
| `npm run report` | Mở báo cáo HTML (`reports/local/html`) |
| `npm run codegen` | Ghi thao tác để sinh code locator |

### Chạy trên production (Vercel)

Site: https://dat-hoang-store.vercel.app — cấu hình trong `.env.prod` (copy từ `.env.prod.example`).

| Lệnh | Mô tả |
|---|---|
| `npm run test:prod` | Toàn bộ suite trên production |
| `npm run test:prod:smoke` | Chỉ `@smoke` — dùng sau mỗi lần deploy |
| `npm run test:prod:api` | Chỉ test API production |
| `npm run test:prod:keyword` | Kịch bản keyword-driven trên production |
| `npm run test:prod:watch` | **Xem trực tiếp**: mở Chrome, chạy lần lượt, mỗi thao tác chậm 0,6s |
| `npm run test:prod:headed` | Hiện trình duyệt, chạy lần lượt từng test |
| `npm run test:prod:ui` | Playwright UI mode: chọn test, xem từng bước, time-travel |
| `npm run test:prod:debug` | Playwright Inspector: chạy từng bước một |

Thêm `SLOW_MO=500` phía trước để chậm lại cho dễ nhìn, vd: `SLOW_MO=500 npm run test:prod:headed -- tests/e2e/cart`.
| `npm run report:prod` | Báo cáo HTML (`reports/prod/html`) |
| `npm run docs:testcases` | Sinh `TEST_CASES.md` (danh mục test case + kết quả) từ lần chạy gần nhất (`TEST_ENV=prod npm run docs:testcases` cho production) |

Môi trường chọn bằng biến `TEST_ENV` (`local` mặc định → `.env`, `prod` → `.env.prod`).
Mỗi môi trường có storageState (`.auth/<env>-*.json`) và thư mục báo cáo riêng.

Khi chạy trên production:
- **Không ghi dữ liệu**: `E2E_ALLOW_WRITE=1` bị bỏ qua với URL không phải localhost, trừ khi đặt thêm
  `E2E_ALLOW_WRITE_REMOTE=1`. Tạo đơn / đăng ký luôn được mock bằng `page.route`.
- Dùng **tài khoản test riêng**, không dùng tài khoản khách thật.
- Test vẫn mở trang sản phẩm thật → `view_count` của sản phẩm tăng nhẹ.
- Retry 1 lần và timeout 45s để chịu cold start của serverless.

Chạy 1 file / 1 test: `npx playwright test tests/e2e/cart -g "Xóa sản phẩm"`.

## Kiến trúc: POM + Keyword + Data

```
           test-data/*.json  ──────────────┐   (Data: test case, dữ liệu, kịch bản)
                  │                         │
   tests/**/*.spec.ts  (data-driven)   test-data/scenarios/*.json  (keyword-driven)
                  │                         │  src/engine/runner.ts
                  └──────────┬──────────────┘
                             ▼
             src/keywords/  — k.auth.login(), k.cart.increaseQuantity()...   (Keyword: bước nghiệp vụ)
                             ▼
             src/pages/     — LoginPage, CartDrawer, Header...               (POM: locator + thao tác nhỏ)
                             ▼
                        Playwright
```

| Tầng | Thư mục | Chứa gì | Không chứa |
|---|---|---|---|
| **POM** | `src/pages/` | Locator, thao tác nguyên tử (fill, click 1 nút) | Assertion nghiệp vụ, dữ liệu test |
| **Keyword** | `src/keywords/` | Bước nghiệp vụ + kiểm tra, mỗi keyword = 1 `test.step` trong report | Locator thô, dữ liệu cứng |
| **Data** | `test-data/` | Test case, dữ liệu đầu vào, kết quả mong đợi, kịch bản | Code |
| **Engine** | `src/engine/` | Chạy kịch bản JSON, skip/known-bug theo dữ liệu | — |

Danh mục đầy đủ **101 keyword**: [KEYWORDS.md](KEYWORDS.md) (tự sinh: `npm run docs:keywords`).

### Cấu trúc thư mục

```
.claude/skills/playwright-skill/  # Claude Code skill (lackeyjb/playwright-skill v5.0.0, MIT)
playwright.config.ts              # projects: setup, api, chromium, mobile
.env / .env.prod (+ .example)     # URL, tài khoản test, cờ ghi DB theo môi trường
KEYWORDS.md                       # danh mục keyword (tự sinh)
scripts/gen-keywords-doc.mjs      # sinh KEYWORDS.md từ JSDoc
src/
  config/env.ts                   # đọc .env theo TEST_ENV, chặn ghi DB remote
  api/ApiClient.ts                # gọi backend (chuẩn bị dữ liệu, API test)
  pages/                          # ① POM — PageObjects.ts gom tất cả page object
  keywords/                       # ② Keyword — common, auth, catalog, cart, checkout, account, admin
  engine/                         #    cases.ts (skip/knownBug), registry.ts, runner.ts
  data/                           # ③ loader.ts (đọc JSON + thay biến), types.ts, factories.ts, routes.ts, messages.ts
  fixtures/index.ts               # fixture: k (keywords), ctx (biến dữ liệu), api, page objects, purchasable
  utils/storage.ts                # localStorage, storageState, detectReload
test-data/                        # mỗi khu vực 1 thư mục: storefront/ account/ admin-*/ api/ ...
  auth/        login.json, register.json
  catalog/     categories.json, search.json
  cart/        items.json
  checkout/    addresses.json, checkout.json
  admin/       menu.json
  common/      static-pages.json
  api/         endpoints.json
  scenarios/   01-shopping.json, 02-account.json, 03-admin.json   # keyword-driven
tests/
  setup/       auth.setup.ts
  api/         *.api.spec.ts                                      # health, sản phẩm, lọc/sắp xếp, auth, admin
  e2e/         smoke/ auth/ catalog/ cart/ checkout/ mobile/       # luồng chính
               storefront/                                        # trang chủ, danh sách, tìm kiếm, sản phẩm, blog, trang tĩnh
               account/                                           # hồ sơ, đơn hàng, yêu thích, địa chỉ, checkout đã đăng nhập
               admin/ admin-catalog/ admin-sales/ admin-marketing/ admin-ops/   # 16 trang quản trị
               keyword-driven/scenarios.spec.ts                   # chạy toàn bộ test-data/scenarios
```

### Viết test — 3 cách

**1. Thêm dữ liệu cho test có sẵn (không cần code).** Thêm 1 phần tử vào file JSON tương ứng, vd. `test-data/auth/login.json`:

```json
{ "id": "LOGIN-V06", "title": "Email có khoảng trắng", "identifier": "a b@x.com", "password": "123456",
  "errors": ["Email hoặc số điện thoại không hợp lệ"] }
```

Mỗi case có thể có: `tags` (`["@smoke"]`), `requires` (`customer` | `admin` | `allowWrite` → thiếu thì skip),
`knownBug` (mô tả bug → `test.fail`).

**2. Kịch bản keyword-driven (không cần code).** Thêm vào `test-data/scenarios/*.json` (hoặc tạo file mới):

```json
{
  "id": "KD-SHOP-05",
  "title": "Thêm sản phẩm rồi xóa khỏi giỏ",
  "tags": ["@smoke"],
  "steps": [
    { "keyword": "catalog.openProduct", "arg": "${product.slug}" },
    { "keyword": "catalog.addToCart", "arg": "${size.label}" },
    { "keyword": "cart.openCart" },
    { "keyword": "cart.removeItem", "arg": "${product.name}" },
    { "keyword": "cart.verifyCartEmpty" }
  ]
}
```

- `"arg"`: keyword nhận 1 tham số (kể cả mảng/object). `"args": [a, b]`: nhiều tham số theo thứ tự.
- Keyword sai tên → báo lỗi ngay trước khi chạy, kèm danh sách keyword hợp lệ.

**3. Spec bằng code** khi cần logic phức tạp — vẫn dùng keyword + data:

```ts
import { test } from '@fixtures';
import { loadData } from '@data/loader';
import { applyCaseMeta, caseTitle } from '@engine/cases';

for (const c of loadData<MyCase[]>('my/feature.json')) {
  test(caseTitle(c), async ({ k, ctx }) => {
    applyCaseMeta(c);
    await k.catalog.openHome();
    // ...
  });
}
```

### Biến trong dữ liệu

| Cú pháp | Giá trị |
|---|---|
| `${product.name}`, `${product.slug}`, `${size.label}` | Sản phẩm thật còn hàng, lấy qua API lúc chạy |
| `${productFirstWord}` | Từ đầu tiên trong tên sản phẩm |
| `${env.customer.email}`, `${env.customer.password}`, `${env.admin.*}` | Tài khoản test trong `.env*` |
| `${uid}` | Chuỗi số duy nhất (email không trùng...) |
| `"@data:checkout/addresses.json#hcm"` | Nạp dữ liệu từ file khác (cả giá trị phải là chuỗi này) |

Mật khẩu luôn được che `***` trong tên step của report.

### Thêm keyword mới

1. (Nếu cần) thêm locator vào Page Object trong `src/pages/`.
2. Thêm method vào nhóm phù hợp trong `src/keywords/` — **bắt buộc 1 dòng JSDoc** `/** ... */` và bọc thân trong `this.step(...)`.
3. `npm run docs:keywords` để cập nhật `KEYWORDS.md` (script báo lỗi nếu thiếu JSDoc).

Keyword mới tự dùng được trong kịch bản JSON với tên `nhóm.tênHàm`, không cần đăng ký.

## Quy ước

- **Import** qua alias: `@fixtures`, `@keywords/*`, `@engine/*`, `@pages/*`, `@data/*`, `@api/*`, `@utils/*`, `@config/*`.
- **Import `test, expect` từ `@fixtures`**. Thân test ưu tiên gọi keyword (`k`), chỉ dùng page object trực tiếp cho assertion đặc thù.
- **Locator chỉ khai báo trong POM**, ưu tiên `getByRole` / `getByLabel` / `getByPlaceholder`.
  Một số nút icon của app chưa có `aria-label` (giỏ hàng, tài khoản, menu mobile) nên tạm nhận diện qua SVG —
  nên bổ sung `aria-label` hoặc `data-testid` trong app rồi cập nhật `Header.ts`.
- **Dữ liệu và kết quả mong đợi** để trong `test-data/`, không viết cứng trong spec.
- **Tag**: `@smoke`, `@api`, `@security`, `@mobile` → lọc bằng `--grep`.
- **Đăng nhập**: dùng `test.use({ storageState: AUTH_FILES.customer })`, hoặc keyword `auth.restoreSession` trong kịch bản.
- **Dữ liệu ghi** (đăng ký, tạo đơn, thêm/sửa/xóa admin...) luôn được **mock** bằng `k.common.mockWrite(...)`,
  kiểm tra payload bằng `k.common.verifyRequest(...)`. Trang cần dữ liệu mà production chưa có (đơn hàng, đánh giá,
  liên hệ...) dùng `k.common.mockGet(...)` với dữ liệu mẫu trong `test-data/`.
- **Lưới an toàn `writeGuard`** (fixture tự động): khi `E2E_ALLOW_WRITE=0`, mọi request POST/PUT/DELETE tới `/api/**`
  không được mock (trừ đăng nhập/đăng xuất) đều bị chặn và trả 418 — test quên mock sẽ fail chứ không ghi vào DB thật.
  Backend local dùng chung DB với production — chỉ bật `E2E_ALLOW_WRITE=1` khi dùng DB test riêng.
- **Bug đã biết**: `knownBug` trong JSON hoặc `test.fail(true, 'BUG: ...')` trong code. Khi bug được sửa,
  Playwright báo *"Expected to fail, but passed"* → xóa đánh dấu.

## Danh mục test case & bug

Toàn bộ test case (ID, module, kết quả) và **danh sách bug đã phát hiện** nằm trong [TEST_CASES.md](TEST_CASES.md),
tự sinh từ lần chạy gần nhất:

```bash
npm run test:prod && TEST_ENV=prod npm run docs:testcases
```

### ⚠️ Lỗ hổng bảo mật — test `@security` cố ý để FAIL (không dùng `test.fail`)

1. **Mật khẩu cứng admin**: backend chấp nhận `admin123` / `manager123` / `staff123` cho **mọi tài khoản admin**
   (`backend/src/controllers/adminController.js` → `adminLogin`, và `backend/src/routes/adminAuth.js`).
   Đã xác nhận trên production. Sửa: gỡ đoạn `plainValid`, chỉ dùng `bcrypt.compare`.
2. **Upload không cần đăng nhập**: `POST /api/admin/upload` khai báo trước `router.use(authMiddleware)`
   (`backend/src/routes/admin.js:20`). Sửa: chuyển route xuống dưới `authMiddleware`.

Các vấn đề phân quyền khác (không kiểm thử tự động vì cần ghi dữ liệu thật): không có kiểm tra quyền theo vai trò
(nhân viên `staff`/`warehouse` làm được mọi thứ, kể cả tạo admin); API tạo/sửa nhân viên trả về cả hash mật khẩu
(`SELECT *`); tạo khách hàng với mật khẩu `admin123`/`manager123`/`staff123` thì lưu **plaintext**.
