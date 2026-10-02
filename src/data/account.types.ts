import type { DataCase } from './types';
import type { PaymentMethod } from '@pages/CheckoutPage';

/** Dữ liệu API thô (giữ nguyên shape backend trả về) - dùng làm response cho mockGet/mockWrite. */
export type ApiRecord = Record<string, unknown>;

// ---------------------------------------------------------------------------
// Hồ sơ cá nhân (test-data/account/profile.json)
// ---------------------------------------------------------------------------

/** Form chỉnh sửa hồ sơ (chỉ các trường muốn nhập). gender: male | female | other | "". */
export interface ProfileForm {
  name?: string;
  phone?: string;
  birthDate?: string;
  gender?: string;
}

/** Form đổi mật khẩu. */
export interface PasswordForm {
  currentPassword: string;
  newPassword: string;
  confirmPassword: string;
}

export interface ProfileDisplayCase extends DataCase {
  /** Key trong `responses` (GET /api/profile). */
  response: string;
  /** Nhãn trường -> giá trị hiển thị ở chế độ xem. */
  expected: Record<string, string>;
}

export interface ProfileEditCase extends DataCase {
  form: ProfileForm;
  /** Body PUT /api/profile mong đợi. */
  expectedBody: Record<string, unknown>;
  expectedView: Record<string, string>;
}

export interface PasswordValidationCase extends DataCase {
  form: PasswordForm;
  error: string;
}

export interface PasswordServerErrorCase extends DataCase {
  form: PasswordForm;
  status: number;
  message: string;
}

export interface ProfileData {
  responses: Record<string, ApiRecord>;
  display: ProfileDisplayCase[];
  edit: ProfileEditCase[];
  editServerError: DataCase & { form: ProfileForm; status: number; message: string };
  password: {
    validation: PasswordValidationCase[];
    serverErrors: PasswordServerErrorCase[];
    success: PasswordForm;
  };
  /** Thống kê trên trang hồ sơ khi mock orders/wishlist/addresses chuẩn. */
  summary: Record<string, string>;
  recentOrders: string[];
  recentFavorites: string[];
  defaultAddressText: string[];
  /** Kịch bản keyword-driven KD-ACC-11. */
  scenario: { form: ProfileForm; updateResponse: ApiRecord };
}

// ---------------------------------------------------------------------------
// Đơn hàng (test-data/account/orders.json)
// ---------------------------------------------------------------------------

export interface OrderTabCase extends DataCase {
  tab: string;
  expected: string[];
}

export interface OrderStatCase extends DataCase {
  stat: string;
  expected: string[];
}

export interface OrderSearchCase extends DataCase {
  query: string;
  expected: string[];
}

export interface OrderLabelCase extends DataCase {
  code: string;
  status: string;
  texts: string[];
}

export interface OrderCancelButtonCase extends DataCase {
  code: string;
  cancelable: boolean;
}

export interface OrdersData {
  list: ApiRecord;
  empty: ApiRecord;
  /** Trang 1 (limit 10) của tài khoản có 12 đơn - dùng cho trang hồ sơ. */
  profileFirstPage: ApiRecord;
  profileTotalOrders: string;
  stats: Record<string, number>;
  allCodes: string[];
  tabs: OrderTabCase[];
  statButtons: OrderStatCase[];
  search: OrderSearchCase[];
  noMatchMessage: string;
  emptyMessage: string;
  labels: OrderLabelCase[];
  cancelButtons: OrderCancelButtonCase[];
  cancel: {
    pendingCode: string;
    pendingId: number;
    reason: string;
    response: ApiRecord;
    errorResponse: ApiRecord;
    errorStatus: number;
    statsAfter: Record<string, number>;
    confirmedCode: string;
  };
}

// ---------------------------------------------------------------------------
// Chi tiết đơn hàng (test-data/account/order-detail.json)
// ---------------------------------------------------------------------------

export interface OrderDetailStatusCase extends DataCase {
  status: string;
  statusLabel: string;
  cancelable: boolean;
}

export interface OrderDetailView {
  heading: string;
  status: string;
  payment: string;
  orderInfo: Record<string, string>;
  shippingInfo: Record<string, string>;
  itemsHeading: string;
  items: { name: string; texts: string[] }[];
  totals: Record<string, string>;
}

export interface OrderDetailData {
  /** Response GET /api/orders/:id - đơn chờ xác nhận, giao nhanh, có mã giảm giá. */
  pending: ApiRecord;
  pendingView: OrderDetailView;
  /** Đơn đã giao, giao tiêu chuẩn, có mã vận đơn, không giảm giá. */
  delivered: ApiRecord;
  deliveredView: OrderDetailView;
  /** Đơn trả hàng + thanh toán 1 phần (so sánh nhãn với trang danh sách). */
  returned: ApiRecord;
  returnedExpected: { status: string; payment: string };
  statuses: OrderDetailStatusCase[];
  cancel: { reason: string; response: ApiRecord; errorStatus: number; errorResponse: ApiRecord };
  errors: (DataCase & { status: number; response: ApiRecord; message: string })[];
}

// ---------------------------------------------------------------------------
// Yêu thích (test-data/account/wishlist.json)
// ---------------------------------------------------------------------------

export type WishlistSort = 'recent' | 'price_asc' | 'price_desc';

export interface WishlistSortCase extends DataCase {
  sort: WishlistSort;
  expected: string[];
}

export interface WishlistSearchCase extends DataCase {
  query: string;
  expected: string[];
}

export interface WishlistAvailabilityCase extends DataCase {
  name: string;
  available: boolean;
  texts: string[];
}

export interface WishlistData {
  response: ApiRecord;
  empty: ApiRecord;
  count: number;
  recentOrder: string[];
  sort: WishlistSortCase[];
  search: WishlistSearchCase[];
  availability: WishlistAvailabilityCase[];
  remove: { name: string; productId: number; remaining: string[]; errorStatus: number; errorResponse: ApiRecord };
  addSimple: { name: string; toast: string };
  addWithVariants: { name: string; slug: string };
  heart: { listingPath: string };
}

// ---------------------------------------------------------------------------
// Địa chỉ (test-data/account/addresses.json)
// ---------------------------------------------------------------------------

/** Form địa chỉ (city = tên tỉnh/thành, vd: "Hồ Chí Minh"). */
export interface AddressForm {
  fullName?: string;
  phone?: string;
  address?: string;
  ward?: string;
  district?: string;
  city?: string;
  isDefault?: boolean;
}

export interface AddressValidationCase extends DataCase {
  /** Ghi đè lên `validForm`. */
  form: AddressForm;
  errors: string[];
}

export interface AddressesData {
  list: ApiRecord;
  empty: ApiRecord;
  names: string[];
  defaultName: string;
  otherName: string;
  otherId: number;
  defaultId: number;
  cardTexts: Record<string, string[]>;
  validForm: AddressForm;
  validation: AddressValidationCase[];
  create: { form: AddressForm; response: ApiRecord; cardTexts: string[] };
  /** Response khi thêm địa chỉ đầu tiên (backend tự đặt làm mặc định). */
  createFirst: ApiRecord;
  createDefault: { form: AddressForm; response: ApiRecord };
  edit: { name: string; expectedForm: AddressForm; changes: AddressForm; response: ApiRecord; newName: string };
  setDefault: { response: ApiRecord };
  delete: { response: ApiRecord; dialogText: string };
  serverError: DataCase & { status: number; response: ApiRecord; message: string };
}

// ---------------------------------------------------------------------------
// Thanh toán khi đã đăng nhập (test-data/account/checkout.json)
// ---------------------------------------------------------------------------

export interface CheckoutPrefillCase extends DataCase {
  user: ApiRecord;
  expected: { firstName: string; lastName: string; phone: string };
}

export interface CheckoutPaymentCase extends DataCase {
  payment: PaymentMethod;
  expectedPayload: Record<string, unknown>;
}

export interface AccountCheckoutData {
  user: ApiRecord;
  cartItem: ApiRecord;
  address: string;
  prefill: CheckoutPrefillCase[];
  payments: CheckoutPaymentCase[];
  createResponse: ApiRecord;
  orderNumber: string;
  success: {
    heading: string;
    payment: Record<string, string>;
    recipient: Record<string, string>;
    totals: Record<string, string>;
    codStatusExpected: string;
  };
  ordersAfter: ApiRecord;
}

// ---------------------------------------------------------------------------
// Chuyển hướng khi chưa đăng nhập (test-data/account/redirects.json)
// ---------------------------------------------------------------------------

export interface RedirectCase extends DataCase {
  path: string;
  expected: string;
}

export interface RedirectsData {
  protectedRoutes: RedirectCase[];
  loginReturn: DataCase & { cartItem: ApiRecord; expected: string };
}
