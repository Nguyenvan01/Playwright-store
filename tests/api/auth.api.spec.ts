import { test, expect } from '@fixtures';
import { env } from '@config/env';
import { buildCustomer } from '@data/factories';
import { loadData } from '@data/loader';
import { MSG } from '@data/messages';
import type { ApiEndpointsData } from '@data/types';
import { applyCaseMeta } from '@engine/cases';

const endpoints = loadData<ApiEndpointsData>('api/endpoints.json');

test.describe('API - Xác thực khách hàng @api', () => {
  test('Đăng nhập thiếu thông tin trả 400', async ({ api }) => {
    const res = await api.post('/auth/login', { email: '' });
    expect(res.status()).toBe(400);
  });

  test('Đăng nhập sai mật khẩu trả 401', async ({ api }) => {
    const res = await api.post('/auth/login', { email: 'khong-ton-tai@example.com', password: 'sai-mat-khau' });
    expect(res.status()).toBe(401);
    expect((await res.json()).message).toBe(MSG.login.wrongCredentials);
  });

  test('Đăng ký thiếu trường bắt buộc trả 400', async ({ api }) => {
    const res = await api.post('/auth/register', { email: 'a@example.com' });
    expect(res.status()).toBe(400);
  });

  test('Đăng ký email sai định dạng trả 400', async ({ api }) => {
    const res = await api.post('/auth/register', buildCustomer({ email: 'khong-phai-email' }));
    expect(res.status()).toBe(400);
  });

  test('Đăng ký thành công rồi đăng ký trùng email trả 409', async ({ api }) => {
    applyCaseMeta({ id: 'API-REG', title: '', requires: ['allowWrite'] });
    const customer = buildCustomer();

    const created = await api.registerCustomer(customer);
    expect(created.token).toBeTruthy();

    const dup = await api.post('/auth/register', customer);
    expect(dup.status()).toBe(409);
    expect((await dup.json()).message).toBe(MSG.register.emailTaken);

    const login = await api.customerLogin(customer.email, customer.password);
    expect(login.token).toBeTruthy();
  });
});

test.describe('API - Phân quyền endpoint (data-driven) @api @security', () => {
  for (const path of [...endpoints.customerProtected, ...endpoints.adminProtected]) {
    test(`GET ${path} không có token trả 401`, async ({ api }) => {
      expect((await api.get(path)).status()).toBe(401);
    });
  }

  test('Token khách hàng không truy cập được API admin', async ({ api }) => {
    applyCaseMeta({ id: 'API-ROLE', title: '', requires: ['customer'] });
    const { token } = await api.customerLogin(env.customer.email, env.customer.password);
    for (const path of endpoints.adminProtected) {
      const res = await api.get(path, { headers: { Authorization: `Bearer ${token}` } });
      expect([401, 403], path).toContain(res.status());
    }
  });

  test('Token giả mạo bị từ chối', async ({ api }) => {
    const res = await api.get('/admin/dashboard', { headers: { Authorization: 'Bearer abc.def.ghi' } });
    expect(res.status()).toBe(401);
  });
});

test.describe('API - Đăng nhập admin @api @security', () => {
  test('Sai mật khẩu trả 401', async ({ api }) => {
    const res = await api.post('/admin/login', { email: 'admin@clothing-store.vn', password: 'sai-mat-khau-e2e' });
    expect(res.status()).toBe(401);
  });

  // Backend đang chấp nhận mật khẩu cứng cho MỌI tài khoản admin
  // (backend/src/controllers/adminController.js -> adminLogin). Test này sẽ FAIL cho tới khi gỡ bỏ.
  for (const backdoor of endpoints.adminBackdoorPasswords) {
    test(`Không được đăng nhập admin bằng mật khẩu cứng "${backdoor}"`, async ({ api }) => {
      const email = env.admin.email || 'admin@clothing-store.vn';
      test.skip(env.admin.password === backdoor, 'Mật khẩu thật trùng mật khẩu demo');
      const res = await api.post('/admin/login', { email, password: backdoor });
      expect(res.status(), 'Backend chấp nhận mật khẩu cứng - lỗ hổng bảo mật').toBe(401);
    });
  }
});
