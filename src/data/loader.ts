import fs from 'node:fs';
import path from 'node:path';
import { env } from '@config/env';

/** Thư mục chứa toàn bộ dữ liệu test (JSON). */
export const DATA_DIR = path.resolve(__dirname, '../../test-data');

const cache = new Map<string, unknown>();

/**
 * Đọc dữ liệu JSON trong `test-data/`.
 *   loadData('auth/login.json')            -> cả file
 *   loadData('checkout/addresses.json#hcm') -> 1 nhánh (dùng dấu chấm cho nhánh lồng: `a.b.0`)
 * Luôn trả về bản sao để test không vô tình sửa dữ liệu dùng chung.
 */
export function loadData<T = unknown>(ref: string): T {
  const [file, pointer] = ref.split('#');
  if (!cache.has(file)) {
    const full = path.join(DATA_DIR, file);
    if (!fs.existsSync(full)) throw new Error(`Không tìm thấy file dữ liệu: test-data/${file}`);
    cache.set(file, JSON.parse(fs.readFileSync(full, 'utf8')));
  }
  const root = cache.get(file);
  return structuredClone(pointer ? getPath(root, pointer, ref) : root) as T;
}

/** Liệt kê file JSON trong 1 thư mục con của test-data (dùng cho kịch bản keyword-driven). */
export function listDataFiles(dir: string): string[] {
  return fs
    .readdirSync(path.join(DATA_DIR, dir))
    .filter((f) => f.endsWith('.json'))
    .sort()
    .map((f) => `${dir}/${f}`);
}

function getPath(obj: unknown, dotted: string, ref: string): unknown {
  let cur: any = obj;
  for (const key of dotted.split('.')) {
    if (cur === undefined || cur === null || !(key in Object(cur))) {
      throw new Error(`Không có dữ liệu "${dotted}" (tham chiếu: ${ref})`);
    }
    cur = cur[key];
  }
  return cur;
}

// ---------------------------------------------------------------------------
// Thay biến trong dữ liệu
// ---------------------------------------------------------------------------

export type DataContext = Record<string, unknown>;

/** Context mặc định: cấu hình môi trường (đọc từ .env / .env.prod). */
export function baseContext(): DataContext {
  return {
    env: {
      name: env.name,
      baseURL: env.baseURL,
      customer: env.customer,
      admin: env.admin,
    },
  };
}

const uid = () => `${Date.now()}${Math.floor(Math.random() * 1000)}`;

/**
 * Thay biến trong chuỗi / object / mảng (đệ quy):
 *   "${product.name}"              -> giá trị trong context (giữ nguyên kiểu nếu cả chuỗi là 1 biến)
 *   "Đã thêm \"${product.name}\""  -> nối chuỗi
 *   "${uid}"                       -> chuỗi số duy nhất mỗi lần gọi
 *   "@data:checkout/addresses.json#hcm" -> nạp dữ liệu từ file khác
 */
export function resolveData<T>(value: T, ctx: DataContext): T {
  if (typeof value === 'string') return resolveString(value, ctx) as T;
  if (Array.isArray(value)) return value.map((v) => resolveData(v, ctx)) as T;
  if (value && typeof value === 'object') {
    return Object.fromEntries(
      Object.entries(value as Record<string, unknown>).map(([k, v]) => [k, resolveData(v, ctx)]),
    ) as T;
  }
  return value;
}

function resolveString(s: string, ctx: DataContext): unknown {
  if (s.startsWith('@data:')) return resolveData(loadData(s.slice('@data:'.length)), ctx);
  const whole = s.match(/^\$\{([^}]+)\}$/);
  if (whole) return lookup(whole[1], ctx);
  return s.replace(/\$\{([^}]+)\}/g, (_, expr: string) => String(lookup(expr, ctx)));
}

function lookup(expr: string, ctx: DataContext): unknown {
  const key = expr.trim();
  if (key === 'uid') return uid();
  return getPath(ctx, key, `\${${key}}`);
}

/** Che mật khẩu trong chuỗi trước khi in ra report / tên step. */
export function maskSecrets(text: string): string {
  let out = text;
  for (const secret of [env.customer.password, env.admin.password]) {
    if (secret) out = out.split(secret).join('***');
  }
  return out;
}
