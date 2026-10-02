import type { DataCase } from './types';

/** Kiểu dữ liệu cho test-data/admin-sales/*.json (layout, dashboard, đơn hàng, khách hàng, nhân viên). */

export type FormValues = Record<string, string | number | boolean>;

// ---------------------------------------------------------------------------
// Layout / header / thông báo
// ---------------------------------------------------------------------------

export interface NotificationItem {
  id: string;
  type?: string;
  title: string;
  message: string;
  time: string | null;
  link: string;
  icon: string;
  color: string;
  urgent?: boolean;
  isNew?: boolean;
}

export interface NotificationsResponse {
  notifications: NotificationItem[];
  counts: Record<string, number>;
}

export interface LayoutData {
  profile: { success: boolean; user: { id: number; name: string; email: string; role: string } };
  titles: (DataCase & { path: string; expect: string })[];
  activeMenu: (DataCase & { path: string; active: string })[];
  userMenu: (DataCase & { from: string; item: string; path: string; pageTitle: string })[];
  notifications: {
    empty: NotificationsResponse;
    some: NotificationsResponse;
    panel: { items: string[]; stats: string[]; footer: string; newChip: string };
    badges: (DataCase & { response: 'empty' | 'some'; badge: string | null })[];
    clickItem: { title: string; path: string; pageTitle: string };
  };
}

// ---------------------------------------------------------------------------
// Dashboard
// ---------------------------------------------------------------------------

export interface StatCardExpect {
  label: string;
  value: string;
  sub?: string;
  change?: string;
}

export interface DashboardData {
  cardLabels: string[];
  sections: string[];
  response: Record<string, unknown>;
  expected: {
    cards: StatCardExpect[];
    statusBreakdown: Record<string, string>;
    recentOrders: { number: string; customer: string; total: string; status: string }[];
    topProducts: { name: string; sold: string }[];
    quickCards: { title: string; value: string }[];
    chartTicks: string[];
  };
  zeroCards: StatCardExpect[];
  links: (DataCase & { section?: string; label: string; path: string; pageTitle: string })[];
  fakeGrowth: (DataCase & { card: string })[];
  rangeOption: string;
}

// ---------------------------------------------------------------------------
// Đơn hàng
// ---------------------------------------------------------------------------

export interface OrderRecord {
  id: number;
  order_number: string;
  status: string;
  payment_status: string;
  [key: string]: unknown;
}

/** Dữ liệu giả cho GET /admin/orders, /admin/orders/stats, /admin/orders/:id. */
export interface OrdersFixture {
  stats?: Record<string, number>;
  orders: OrderRecord[];
  details?: Record<string, Record<string, unknown>>;
  /** Ghi đè tổng số đơn (để có nhiều trang). */
  total?: number;
}

export interface OrderTransitionCase extends DataCase {
  order: string;
  orderId: number;
  buttons: string[];
  click?: string;
  status?: string;
  label?: string;
  warning?: boolean;
}

export interface OrderFilterCase extends DataCase {
  search?: string;
  status?: string;
  payment?: string;
  card?: string;
  dateFrom?: string;
  dateTo?: string;
  request: Record<string, string>;
  rows?: string[];
  selectValue?: string;
}

export interface OrderDetailExpect {
  number: string;
  heading: string;
  status: string;
  payment: string;
  recipient: string;
  email: string;
  phone: string;
  address: string;
  info: Record<string, string>;
  items: { name: string; variant: string; qty: string; total: string }[];
  summary: Record<string, string>;
  logs: string[];
}

export interface OrdersData {
  fixture: OrdersFixture;
  headers: string[];
  statusCards: Record<string, string>;
  row: { number: string; customer: string; items: string; total: string; payment: string; status: string };
  detail: OrderDetailExpect;
  transitions: OrderTransitionCase[];
  filters: OrderFilterCase[];
  payment: { order: string; orderId: number; value: string; toast: string; label: string };
  cancel: {
    order: string;
    orderId: number;
    reason: string;
    refundNote: string;
    toast: string;
    pointsOrder: string;
    pointsNote: string;
    error: { status: number; message: string };
  };
  cancelAction: (DataCase & { order: string; visible: boolean })[];
  pagination: { total: number; text: string; page: number };
  pushNotification: { order: string; orderId: number; click: string; title: string };
}

// ---------------------------------------------------------------------------
// Khách hàng / Nhân viên
// ---------------------------------------------------------------------------

export interface PeopleFixture<T> {
  items: T[];
  details?: Record<string, Record<string, unknown>>;
  /** Ghi đè tổng số dòng (để có nhiều trang, mỗi trang 20). */
  total?: number;
}

export interface FormValidationCase extends DataCase {
  form: FormValues;
  errors: string[];
  nativeEmailInvalid?: boolean;
}

export interface CustomerRecord {
  id: number;
  name: string;
  email: string;
  [key: string]: unknown;
}

export interface CustomersData {
  fixture: { customers: CustomerRecord[]; details: Record<string, Record<string, unknown>> };
  headers: string[];
  rows: { name: string; status: string; spent: string; points: string }[];
  search: { text: string; rows: string[]; hidden: string[] };
  addValidation: FormValidationCase[];
  editValidation: (FormValidationCase & { customer: string })[];
  add: {
    form: FormValues;
    payload: Record<string, unknown>;
    response: unknown;
    toast: string;
    passwordHint: string;
    error: { status: number; message: string };
  };
  edit: {
    customer: string;
    id: number;
    prefill: Record<string, string>;
    form: FormValues;
    payload: Record<string, unknown>;
    response: unknown;
    newName: string;
    status: string;
    toast: string;
  };
  detail: {
    customer: string;
    name: string;
    email: string;
    stats: Record<string, string>;
    values: Record<string, string>;
    recentOrders: string[];
    recentStatuses: string[];
    statusBug: string;
  };
  delete: (DataCase & {
    customer: string;
    customerId: number;
    warning?: string;
    status: number;
    response: unknown;
    toast: string;
    removed: boolean;
    rowStatus?: string;
  })[];
  deleteText: string;
  pagination: { total: number; lastClicked: number; expectedPage: number; text: string };
}

export interface EmployeeRecord {
  id: number;
  name: string;
  email: string;
  role: string;
  [key: string]: unknown;
}

export interface EmployeesData {
  fixture: { employees: EmployeeRecord[] };
  heading: string;
  headers: string[];
  roles: { name: string; label: string }[];
  search: { text: string; request: Record<string, string>; rows: string[]; hidden: string[] };
  addValidation: FormValidationCase[];
  editValidation: (FormValidationCase & { employee: string })[];
  create: (DataCase & { form: FormValues; payload: Record<string, unknown>; response: unknown; name: string; roleLabel: string })[];
  createToast: string;
  edit: {
    employee: string;
    id: number;
    prefill: Record<string, string>;
    passwordPlaceholder: string;
    form: FormValues;
    payload: Record<string, unknown>;
    response: unknown;
    newName: string;
    roleLabel: string;
    toast: string;
    withPassword: { form: FormValues; payload: Record<string, unknown> };
  };
  delete: {
    employee: string;
    id: number;
    heading: string;
    message: string;
    backendStatus: number;
    backendResponse: { success: boolean; message: string };
    successToast: string;
  };
  toggle: { employee: string; id: number; toast: string; errorToast: string };
}
