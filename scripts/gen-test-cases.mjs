// Sinh TEST_CASES.md (danh mục test case + kết quả) từ reports/<env>/results.json
// Chạy sau 1 lần test: npm run docs:testcases  (hoặc TEST_ENV=prod npm run docs:testcases)
import fs from 'node:fs';
import path from 'node:path';

const root = path.resolve(import.meta.dirname, '..');
const envName = process.env.TEST_ENV || 'local';
const file = path.join(root, 'reports', envName, 'results.json');
if (!fs.existsSync(file)) {
  console.error(`Chưa có ${path.relative(root, file)} - hãy chạy test trước.`);
  process.exit(1);
}
const report = JSON.parse(fs.readFileSync(file, 'utf8'));

const MODULES = {
  'api/health': 'API - Health & Home', 'api/products': 'API - Sản phẩm', 'api/public': 'API - Lọc/Sắp xếp/Validate',
  'api/auth': 'API - Xác thực & Bảo mật', 'api/admin': 'API - Quản trị',
  'e2e/smoke': 'UI - Trang chủ & trang tĩnh', 'e2e/auth': 'UI - Đăng nhập / Đăng ký', 'e2e/catalog': 'UI - Danh mục, Tìm kiếm, Sản phẩm',
  'e2e/cart': 'UI - Giỏ hàng', 'e2e/checkout': 'UI - Thanh toán', 'e2e/account': 'UI - Tài khoản khách hàng',
  'e2e/admin': 'UI - Quản trị', 'e2e/mobile': 'UI - Mobile', 'e2e/keyword-driven': 'Kịch bản Keyword-driven',
  'e2e/storefront': 'UI - Cửa hàng (trang chủ, danh sách, sản phẩm, blog, trang tĩnh)',
  'e2e/admin-catalog': 'UI - Admin: Sản phẩm, Danh mục, Thương hiệu',
  'e2e/admin-sales': 'UI - Admin: Layout, Dashboard, Đơn hàng, Khách hàng, Nhân viên',
  'e2e/admin-marketing': 'UI - Admin: Khuyến mãi, Mã giảm giá, Đánh giá, Bài viết, Liên hệ',
  'e2e/admin-ops': 'UI - Admin: Kho, Nhập hàng, Báo cáo, Cài đặt',
  'setup': 'Setup',
};
const moduleOf = (f) => {
  // So khớp tiền tố DÀI nhất trước (vd: 'e2e/admin-sales' trước 'e2e/admin')
  const key = Object.keys(MODULES).sort((a, b) => b.length - a.length).find((k) => f.replace(/\\/g, '/').startsWith(k + '/') || f.replace(/\\/g, '/').startsWith(k));
  return key ? MODULES[key] : path.dirname(f);
};

const rows = [];
const walk = (suite, parents) => {
  const titles = suite.title && !suite.title.endsWith('.ts') ? [...parents, suite.title] : parents;
  for (const spec of suite.specs ?? []) {
    for (const t of spec.tests) {
      if (t.projectName === 'setup') continue;
      const last = t.results.at(-1);
      const knownBug = t.annotations.find((a) => a.type === 'fail')?.description;
      const skipReason = t.annotations.find((a) => a.type === 'skip')?.description;
      let status;
      if (!last || last.status === 'skipped') status = '⏭️ Bỏ qua';
      else if (t.expectedStatus === 'failed' && last.status === 'failed') status = '🐞 Bug đã biết';
      else if (t.expectedStatus === 'failed' && last.status === 'passed') status = '⚠️ Bug đã sửa?';
      else if (last.status === 'passed') status = '✅ Đạt';
      else status = '❌ Lỗi';
      const id = spec.title.match(/^\[([\w-]+)\]/)?.[1];
      rows.push({
        module: moduleOf(spec.file), id, project: t.projectName,
        title: [...titles.slice(1), spec.title.replace(/^\[[\w-]+\]\s*/, '')].join(' › '),
        status, note: knownBug ?? (status === '❌ Lỗi' ? (last?.error?.message ?? '').split('\n')[0].replace(/\u001b\[\d+m/g, '').slice(0, 120) : skipReason ?? ''),
      });
    }
  }
  for (const s of suite.suites ?? []) walk(s, titles);
};
for (const s of report.suites) walk(s, []);

// Gán ID cho test chưa có [ID] trong tên
const counters = {};
for (const r of rows) {
  if (r.id) continue;
  const prefix = (r.project === 'api' ? 'API' : r.project === 'mobile' ? 'MOB' : 'UI') + '-' +
    r.module.replace(/^(API|UI) - /, '').normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/đ/gi, 'd')
      .split(/[^A-Za-z]+/).filter(Boolean).map((w) => w[0].toUpperCase()).join('').slice(0, 4);
  counters[prefix] = (counters[prefix] ?? 0) + 1;
  r.id = `${prefix}-${String(counters[prefix]).padStart(2, '0')}`;
}

const count = (rs, s) => rs.filter((r) => r.status === s).length;
const STATUSES = ['✅ Đạt', '🐞 Bug đã biết', '❌ Lỗi', '⏭️ Bỏ qua', '⚠️ Bug đã sửa?'];
const modules = [...new Set(rows.map((r) => r.module))];
const esc = (s) => String(s).replace(/\|/g, '\\|');

let md = `# Danh mục Test Case\n\n> Tự sinh bởi \`npm run docs:testcases\` từ lần chạy **${envName}** lúc ${new Date(report.stats.startTime).toLocaleString('vi-VN', { timeZone: 'Asia/Ho_Chi_Minh' })}. Đừng sửa tay.\n\n`;
md += `## Tổng quan\n\n| Module | Tổng | ${STATUSES.join(' | ')} |\n|---|---|${STATUSES.map(() => '---').join('|')}|\n`;
for (const m of modules) {
  const rs = rows.filter((r) => r.module === m);
  md += `| ${m} | ${rs.length} | ${STATUSES.map((s) => count(rs, s) || '').join(' | ')} |\n`;
}
md += `| **Tổng** | **${rows.length}** | ${STATUSES.map((s) => `**${count(rows, s)}**`).join(' | ')} |\n\n`;
md += `Chú thích: 🐞 test đúng nhưng app còn bug (đánh dấu \`test.fail\`) · ❌ test fail (gồm lỗ hổng bảo mật cố ý để đỏ) · ⏭️ thiếu điều kiện (tài khoản / quyền ghi DB).\n\n`;
// Tổng hợp bug: test.fail (bug đã biết) + test bảo mật đang fail
const bugs = rows.filter((r) => r.status === '🐞 Bug đã biết' || r.status === '⚠️ Bug đã sửa?');
const security = rows.filter((r) => r.status === '❌ Lỗi' && /@security|bảo mật|mật khẩu cứng|upload/i.test(r.title));
md += `## Bug phát hiện\n\n**${bugs.length}** test đang ghi nhận bug của app (\`test.fail\`) và **${security.length}** test bảo mật đang fail.\n\n`;
if (security.length) {
  md += `### ⚠️ Lỗ hổng bảo mật\n\n| ID | Test case |\n|---|---|\n`;
  for (const r of security) md += `| ${r.id} | ${esc(r.title)} |\n`;
  md += '\n';
}
const byDesc = new Map();
for (const r of bugs) {
  const key = r.note.replace(/^BUG:\s*/, '') || '(không mô tả)';
  if (!byDesc.has(key)) byDesc.set(key, { module: r.module, ids: [] });
  byDesc.get(key).ids.push(r.id);
}
md += `### Bug chức năng / giao diện (${byDesc.size} bug, gom theo mô tả)\n\n| # | Module | Bug | Test |\n|---|---|---|---|\n`;
[...byDesc.entries()].sort((a, b) => a[1].module.localeCompare(b[1].module)).forEach(([desc, v], i) => {
  md += `| ${i + 1} | ${v.module} | ${esc(desc)} | ${v.ids.join(', ')} |\n`;
});
md += '\n';

for (const m of modules) {
  md += `## ${m}\n\n| ID | Test case | Project | Kết quả | Ghi chú |\n|---|---|---|---|---|\n`;
  for (const r of rows.filter((x) => x.module === m)) {
    md += `| ${r.id} | ${esc(r.title)} | ${r.project} | ${r.status} | ${esc(r.note)} |\n`;
  }
  md += '\n';
}
fs.writeFileSync(path.join(root, 'TEST_CASES.md'), md);
console.log(`TEST_CASES.md: ${rows.length} test case, ${modules.length} module (${envName})`);
