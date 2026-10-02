// Sinh KEYWORDS.md từ JSDoc của các method trong src/keywords/*Keywords.ts
// Chạy: npm run docs:keywords
import fs from 'node:fs';
import path from 'node:path';

const root = path.resolve(import.meta.dirname, '..');
const dir = path.join(root, 'src/keywords');
const files = fs.readdirSync(dir).filter((f) => /^[A-Z]\w+Keywords\.ts$/.test(f) && f !== 'BaseKeywords.ts');
const order = ['Common', 'Auth', 'Catalog', 'Listing', 'Product', 'Content', 'Cart', 'Checkout', 'Account', 'Admin', 'AdminCatalog', 'AdminSales', 'AdminMarketing', 'AdminOps'];
files.sort((a, b) => order.indexOf(a.replace('Keywords.ts', '')) - order.indexOf(b.replace('Keywords.ts', '')));

const pattern = /\/\*\*\s*([^*]+?)\s*\*\/\s*\n\s*async\s+(\w+)\(([^)]*)\)/g;
let md = `# Danh mục Keyword\n\n> File tự sinh bởi \`npm run docs:keywords\` — đừng sửa tay.\n\n`;
md += 'Dùng trong code: `await k.<nhóm>.<keyword>(...)` · Dùng trong kịch bản JSON: `{ "keyword": "<nhóm>.<keyword>", "arg": ... }` hoặc `"args": [...]`.\n\n';
let total = 0;
const missing = [];

for (const file of files) {
  const raw = file.replace('Keywords.ts', '');
  const group = raw[0].toLowerCase() + raw.slice(1);
  const src = fs.readFileSync(path.join(dir, file), 'utf8');
  const documented = new Set();
  md += `## ${group}\n\n| Keyword | Tham số | Mô tả |\n|---|---|---|\n`;
  for (const [, doc, name, params] of src.matchAll(pattern)) {
    documented.add(name);
    const p = params.replace(/\s+/g, ' ').trim().replace(/\|/g, '\\|');
    md += `| \`${group}.${name}\` | ${p ? `\`${p}\`` : '—'} | ${doc.replace(/\|/g, '\\|')} |\n`;
    total++;
  }
  for (const [, name] of src.matchAll(/^\s+async\s+(\w+)\(/gm)) {
    if (!documented.has(name)) missing.push(`${group}.${name}`);
  }
  md += '\n';
}

fs.writeFileSync(path.join(root, 'KEYWORDS.md'), md);
console.log(`KEYWORDS.md: ${total} keyword`);
if (missing.length) {
  console.error(`Thiếu JSDoc 1 dòng cho: ${missing.join(', ')}`);
  process.exit(1);
}
