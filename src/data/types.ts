import type { CartItem, ShippingInfo } from './factories';

/** Các trường chung của 1 test case data-driven. */
export interface DataCase {
  id: string;
  title: string;
  /** Có giá trị -> đánh dấu test.fail (bug đã biết của app). */
  knownBug?: string;
  /** Điều kiện chạy: thiếu thì test tự skip. */
  requires?: Requirement[];
  tags?: string[];
}

export type Requirement = 'customer' | 'admin' | 'allowWrite';

export interface LoginValidationCase extends DataCase {
  identifier: string;
  password: string;
  errors: string[];
}

export interface LoginServerErrorCase extends DataCase {
  identifier: string;
  password: string;
  error: string;
}

export interface LoginData {
  validation: LoginValidationCase[];
  wrongCredentials: LoginServerErrorCase[];
  mockUser: { id: number; name: string; email: string; phone: string };
}

export interface RegisterForm {
  name: string;
  email: string;
  phone: string;
  password: string;
  confirmPassword?: string;
}

export interface RegisterData {
  validation: (DataCase & { form: RegisterForm; errors: string[] })[];
  serverErrors: (DataCase & { status: number; message: string })[];
}

export interface CategoryCase {
  nav: string;
  path: string;
  heading: string;
}

export interface SearchData {
  suggestions: (DataCase & { keyword: string; expectSuggestion: string })[];
  resultPage: (DataCase & { keyword: string; expectHeading: string })[];
  noResult: (DataCase & { keyword: string })[];
}

export interface CartData {
  twoItems: Partial<CartItem>[];
  expectedSubtotal: string;
}

export type AddressBook = Record<string, ShippingInfo>;

export interface CheckoutCase extends DataCase {
  address: string;
  shippingMethod: 'standard' | 'express';
  payment: 'cod' | 'bank' | 'vnpay' | 'momo';
  expected: { heading: string; shippingFee: number; paymentStatus: 'paid' | 'unpaid' };
}

export interface CheckoutData {
  cartItem: Partial<CartItem>;
  orders: CheckoutCase[];
  incomplete: (DataCase & { missing: keyof ShippingInfo })[];
  serverErrors: (DataCase & { status: number; message: string })[];
}

export interface StaticPage {
  path: string;
  title: string;
}

export interface AdminMenuItem {
  label: string;
  path: string;
}

export interface ApiEndpointsData {
  customerProtected: string[];
  adminProtected: string[];
  adminBackdoorPasswords: string[];
}

/** 1 bước trong kịch bản keyword-driven. */
export interface ScenarioStep {
  /** Tên keyword dạng `nhóm.hàm`, vd: `cart.increaseQuantity`. */
  keyword: string;
  /** Danh sách tham số theo thứ tự, vd: ["Áo thun E2E", 2]. Hỗ trợ biến ${...} và @data:. */
  args?: unknown[];
  /** Dùng khi keyword chỉ nhận 1 tham số (kể cả tham số là mảng/object), vd: "@data:cart/items.json#twoItems". */
  arg?: unknown;
  /** Mô tả thêm cho bước (hiển thị trong report). */
  note?: string;
}

export interface Scenario extends DataCase {
  steps: ScenarioStep[];
}
