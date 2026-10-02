import { APIRequestContext, APIResponse, expect } from '@playwright/test';
import { env } from '@config/env';
import type { CustomerData } from '@data/factories';

export interface Product {
  id: number;
  name: string;
  slug: string;
  price: number | string;
  compare_price?: number | string | null;
  image_url?: string;
  [key: string]: unknown;
}

export interface ProductSize {
  id?: number;
  name?: string;
  code?: string;
  /** Text hiển thị trên nút size - frontend dùng `code || name`. */
  label: string;
  disabled?: boolean;
}

export interface ProductDetail extends Product {
  sizes: ProductSize[];
  colors: Array<{ id: number | string; name: string }>;
  variants: unknown[];
}

export interface AuthResult {
  token: string;
  user: Record<string, unknown>;
}

/**
 * Wrapper mỏng quanh `request` của Playwright để gọi backend Express.
 * Dùng trong API test và để chuẩn bị dữ liệu (lấy sản phẩm thật, đăng nhập lấy token...).
 */
export class ApiClient {
  constructor(private readonly request: APIRequestContext, private readonly baseURL = env.apiURL) {}

  url(path: string) {
    return `${this.baseURL}${path.startsWith('/') ? path : `/${path}`}`;
  }

  get(path: string, options?: Parameters<APIRequestContext['get']>[1]) {
    return this.request.get(this.url(path), options);
  }

  post(path: string, data?: unknown, token?: string) {
    return this.request.post(this.url(path), {
      data,
      headers: token ? { Authorization: `Bearer ${token}` } : undefined,
    });
  }

  async json<T = any>(res: APIResponse): Promise<T> {
    return (await res.json()) as T;
  }

  // ---------- Catalog ----------
  async listProducts(params: Record<string, string | number> = {}): Promise<Product[]> {
    const qs = new URLSearchParams(Object.entries(params).map(([k, v]) => [k, String(v)])).toString();
    const res = await this.get(`/products${qs ? `?${qs}` : ''}`);
    expect(res, `GET /products lỗi ${res.status()}`).toBeOK();
    const body = await res.json();
    return body.data.products as Product[];
  }

  async getProduct(slug: string): Promise<ProductDetail> {
    const res = await this.get(`/products/${slug}`);
    expect(res, `GET /products/${slug} lỗi ${res.status()}`).toBeOK();
    const data = (await res.json()).data as ProductDetail;
    data.sizes = (data.sizes ?? []).map((s) => ({ ...s, label: s.label ?? s.code ?? s.name ?? '' }));
    return data;
  }

  /** Tìm 1 sản phẩm thật có ít nhất 1 size còn hàng để dùng cho test UI. */
  async findPurchasableProduct(): Promise<{ product: ProductDetail; size: ProductSize }> {
    const products = await this.listProducts({ limit: 20 });
    for (const p of products) {
      const detail = await this.getProduct(p.slug);
      const size = detail.sizes?.find((s) => !s.disabled);
      if (size) return { product: detail, size };
    }
    throw new Error('Không tìm thấy sản phẩm nào có size còn hàng trong DB.');
  }

  // ---------- Auth ----------
  async customerLogin(email: string, password: string): Promise<AuthResult> {
    const res = await this.post('/auth/login', { email, password });
    expect(res, `Đăng nhập khách hàng ${email} thất bại: ${res.status()}`).toBeOK();
    const body = await res.json();
    return { token: body.token, user: body.user };
  }

  async registerCustomer(customer: CustomerData): Promise<AuthResult> {
    const res = await this.post('/auth/register', customer);
    expect(res.status(), `Đăng ký ${customer.email}: ${await res.text()}`).toBe(201);
    const body = await res.json();
    return { token: body.token, user: body.user };
  }

  async adminLogin(email: string, password: string): Promise<AuthResult> {
    const res = await this.post('/admin/login', { email, password });
    expect(res, `Đăng nhập admin ${email} thất bại: ${res.status()}`).toBeOK();
    const body = await res.json();
    return { token: body.token, user: body.user };
  }
}
