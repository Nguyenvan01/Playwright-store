# Hướng dẫn đưa dự án lên GitHub

Tài liệu này hướng dẫn đưa bộ test `cloth-store-e2e` lên GitHub, cập nhật về sau, và cài lại trên máy khác.

## Trước khi bắt đầu

### Repo phải để PRIVATE

`README.md` và `TEST_CASES.md` mô tả chi tiết các lỗ hổng bảo mật **đang tồn tại trên site thật**
(https://dat-hoang-store.vercel.app), ví dụ mật khẩu cứng `admin123` đăng nhập được mọi tài khoản admin,
hoặc API upload không cần đăng nhập. Repo public đồng nghĩa với công khai cách tấn công site.
Chỉ chuyển sang public sau khi đã sửa hết các lỗ hổng.

### Những file KHÔNG được đưa lên

`.gitignore` đã loại sẵn các file sau. Không xóa các dòng này.

| File / thư mục | Lý do |
|---|---|
| `.env`, `.env.prod` | Chứa email + mật khẩu tài khoản test |
| `.auth/*.json` | Chứa token đăng nhập (customer, admin) |
| `.venv/` | Cài lại bằng `pip install -r requirements.txt` |
| `artifacts/` | Kết quả chạy test: log, ảnh, page source, video, trace, JUnit, Allure |

Các file mẫu `.env.example` và `.env.prod.example` (không có mật khẩu) **được** đưa lên để người khác biết cần cấu hình gì.

## Lần đầu: đưa dự án lên GitHub

### Bước 1 — Khai báo tên và email cho git (chỉ làm một lần trên mỗi máy)

```bash
git config --global user.name "Tên của bạn"
git config --global user.email "email-github-cua-ban@example.com"
```

### Bước 2 — Commit ở máy

```bash
cd "/Users/ccm/Documents/Dự án cá nhân/Playwright/cloth-store-e2e"
git init -b main
git add .
git status
```

Đọc kỹ danh sách `git status` in ra. **Không được** có `.env`, `.env.prod` hay `.auth/*.json`.
Nếu thấy, dừng lại và kiểm tra `.gitignore`. Nếu không thấy, commit:

```bash
git commit -m "Bộ test E2E Python + Playwright cho web bán quần áo Đạt Hoàng"
```

### Bước 3 — Tạo repo và đẩy lên

Chọn **một** trong hai cách.

#### Cách A: GitHub CLI (dễ nhất)

```bash
brew install gh                 # chỉ cần cài một lần
gh auth login                   # chọn GitHub.com → HTTPS → đăng nhập bằng trình duyệt
gh repo create cloth-store-e2e --private --source=. --push
```

Lệnh cuối tạo repo private tên `cloth-store-e2e` và đẩy code lên luôn.

#### Cách B: Qua trang web GitHub

1. Vào https://github.com/new
   - **Repository name:** `cloth-store-e2e`
   - Chọn **Private**
   - **Không** tick "Add a README file", "Add .gitignore", "Choose a license" (dự án đã có sẵn)
   - Bấm **Create repository**
2. Tạo token để đẩy code (GitHub không nhận mật khẩu đăng nhập khi push):
   - Vào https://github.com/settings/tokens → **Generate new token (classic)**
   - Tick quyền **`repo`**, đặt thời hạn, bấm Generate
   - Copy token ngay (chỉ hiện một lần)
3. Đẩy code (thay `<username>` bằng tài khoản GitHub của bạn):

   ```bash
   git remote add origin https://github.com/<username>/cloth-store-e2e.git
   git push -u origin main
   ```

   Khi hỏi **Username**, nhập tài khoản GitHub. Khi hỏi **Password**, dán **token** vừa tạo.

### Bước 4 — Kiểm tra trên GitHub

Mở repo trên trình duyệt và xác nhận:

- Có `README.md`, `TEST_CASES.md`, `KEYWORDS.md`, `config.py`, `keywords/`, `pages/`, `tests/`, `data/`
- **Không** có `.env.prod`, thư mục `.auth/` chỉ có `.gitkeep`
- Góc trên có nhãn **Private**

## Cập nhật về sau

(`py` = `.venv/bin/python`)

Mỗi khi thêm hoặc sửa test:

```bash
cd "/Users/ccm/Documents/Dự án cá nhân/Playwright/cloth-store-e2e"
py -m pytest --collect-only -q           # dữ liệu + import hợp lệ
py -m pytest -m core                      # unit test framework
git status                                # xem file thay đổi
git add .
git commit -m "Mô tả ngắn thay đổi, vd: Thêm test trang Khuyến mãi"
git push
```

Nên cập nhật tài liệu tự sinh trước khi commit:

```bash
py scripts/gen_keywords_doc.py                                          # KEYWORDS.md
py -m pytest; py scripts/gen_test_cases.py   # TEST_CASES.md (chạy toàn bộ test trên web thật)
```

## Cài lại trên máy khác

```bash
git clone https://github.com/<username>/cloth-store-e2e.git
cd cloth-store-e2e
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m playwright install chromium

cp .env.prod.example .env.prod     # cấu hình chạy web thật (mặc định)
cp .env.example .env               # cấu hình chạy local (tuỳ chọn)
```

Mở `.env.prod` và điền lại tài khoản test (lấy từ người quản lý dự án, **không** gửi qua chat công khai):

```
E2E_CUSTOMER_EMAIL=...
E2E_CUSTOMER_PASSWORD='...'
E2E_ADMIN_EMAIL=...
E2E_ADMIN_PASSWORD='...'
```

Mật khẩu có ký tự `#` thì **phải** bọc trong dấu nháy đơn `'...'`, nếu không dotenv sẽ cắt mất phần sau `#`.

Chạy thử:

```bash
.venv/bin/python -m pytest -m smoke   # chạy trên https://dat-hoang-store.vercel.app
```

## Test tự chạy khi push (GitHub Actions)

Workflow [.github/workflows/e2e.yml](.github/workflows/e2e.yml) chạy test trên https://dat-hoang-store.vercel.app
mỗi lần `git push` lên `main` (và mỗi PR vào `main`). Xem kết quả ở tab **Actions** của repo.

Khai báo tài khoản test **một lần** (không commit `.env.prod`), lấy giá trị từ `.env.prod` ở máy:

```bash
gh secret set E2E_CUSTOMER_EMAIL
gh secret set E2E_CUSTOMER_PASSWORD
gh secret set E2E_ADMIN_EMAIL
gh secret set E2E_ADMIN_PASSWORD
```

(mỗi lệnh hỏi giá trị, dán vào rồi Enter; hoặc vào **Settings → Secrets and variables → Actions → New repository secret**).

## Gặp lỗi thường gặp

| Lỗi | Cách xử lý |
|---|---|
| `remote: Support for password authentication was removed` | Dùng token (Cách B, bước 2) thay vì mật khẩu, hoặc dùng `gh auth login` |
| `remote origin already exists` | `git remote set-url origin https://github.com/<username>/cloth-store-e2e.git` |
| `Updates were rejected because the remote contains work...` | Repo trên GitHub đã có file (do tick "Add README"). Chạy `git pull origin main --allow-unrelated-histories`, rồi `git push` |
| Lỡ commit `.env.prod` | **Đổi mật khẩu 2 tài khoản test ngay**, rồi `git rm --cached .env.prod`, commit và push lại. File vẫn còn trong lịch sử git, nên đổi mật khẩu là bắt buộc |
| `py -m pytest` báo thiếu tài khoản, test bị bỏ qua | Chưa tạo hoặc chưa điền `.env.prod` (xem mục *Cài lại trên máy khác*) |
