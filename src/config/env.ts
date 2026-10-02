import path from 'node:path';
import dotenv from 'dotenv';

/**
 * Chọn môi trường bằng biến TEST_ENV:
 *   (không đặt) -> .env          (local: localhost:3000 + localhost:5000)
 *   prod        -> .env.prod     (https://dat-hoang-store.vercel.app)
 */
export const TEST_ENV = process.env.TEST_ENV || 'local';
const envFile = TEST_ENV === 'local' ? '.env' : `.env.${TEST_ENV}`;
dotenv.config({ path: path.resolve(__dirname, '../..', envFile) });

const flag = (name: string) => process.env[name] === '1' || process.env[name] === 'true';

const baseURL = process.env.BASE_URL || 'http://localhost:3000';
const isLocal = /^https?:\/\/(localhost|127\.0\.0\.1)(:\d+)?/.test(baseURL);

// Chặn ghi dữ liệu thật (tạo user, đơn hàng) lên môi trường không phải localhost,
// trừ khi xác nhận rõ ràng bằng E2E_ALLOW_WRITE_REMOTE=1.
const allowWrite = flag('E2E_ALLOW_WRITE') && (isLocal || flag('E2E_ALLOW_WRITE_REMOTE'));

export const env = {
  name: TEST_ENV,
  baseURL,
  isLocal,
  apiURL: (process.env.API_URL || 'http://localhost:5000/api').replace(/\/$/, ''),
  appDir:
    process.env.APP_DIR || '/Users/ccm/Documents/Dự án cá nhân/Web bán quần áo/Đồ án Quần áo',
  startServers: isLocal && flag('START_SERVERS'),
  allowWrite,
  isCI: !!process.env.CI,
  customer: {
    email: process.env.E2E_CUSTOMER_EMAIL || '',
    password: process.env.E2E_CUSTOMER_PASSWORD || '',
  },
  admin: {
    email: process.env.E2E_ADMIN_EMAIL || '',
    password: process.env.E2E_ADMIN_PASSWORD || '',
  },
};

/** Đường dẫn file storageState cho từng vai trò (sinh ra bởi tests/setup/auth.setup.ts). */
export const AUTH_FILES = {
  customer: path.resolve(__dirname, `../../.auth/${TEST_ENV}-customer.json`),
  admin: path.resolve(__dirname, `../../.auth/${TEST_ENV}-admin.json`),
};
