import type { DataCase } from './types';

/** Khuyến mãi giả lập. `startOffset`/`endOffset` = số ngày so với hôm nay (giờ VN), thay cho start_date/end_date. */
export interface PromotionMock {
  id: number;
  title: string;
  slug?: string;
  description?: string;
  image_url?: string | null;
  discount_type: 'percentage' | 'fixed_amount';
  discount_value: number;
  start_date?: string;
  end_date?: string;
  startOffset?: number;
  endOffset?: number;
  is_active: boolean;
  is_featured: boolean;
}

/** Ô nhập form theo label: chuỗi/số -> input/select, boolean -> checkbox. */
export type FormFields = Record<string, string | number | boolean>;

export interface PromotionStatusCase extends DataCase {
  promotion: PromotionMock;
  expected: Record<string, string>;
}

export interface SearchCase extends DataCase {
  keyword: string;
  visible: string[];
  hidden: string[];
  emptyText?: string;
}

export interface FormValidationCase extends DataCase {
  form: FormFields;
  toast: string;
}

export interface PromotionsData {
  headers: string[];
  list: PromotionMock[];
  statusCases: PromotionStatusCase[];
  search: SearchCase[];
  validation: FormValidationCase[];
  invalidImage: DataCase & { form: FormFields };
  create: { form: FormFields; expectedPayload: Record<string, unknown>; toast: string };
  slugCases: (DataCase & { steps: FormFields[]; expectedSlug: string })[];
  edit: {
    title: string;
    prefilled: Record<string, string>;
    form: FormFields;
    expectedPayload: Record<string, unknown>;
    toast: string;
  };
  saveError: DataCase & { form: FormFields; status: number; message: string };
  view: { title: string; texts: string[] };
  remove: { title: string; toast: string };
}

export interface CouponMock {
  id: number;
  code: string;
  name?: string;
  description?: string;
  coupon_type?: string;
  discount_type: 'percentage' | 'fixed_amount';
  discount_value: number;
  max_discount_amount?: number | null;
  min_order_amount?: number | null;
  max_usage_total?: number | null;
  max_usage_per_user?: number;
  used_count?: number;
  valid_from?: string | null;
  valid_until?: string | null;
  is_active: boolean;
  is_public: boolean;
}

export interface CouponsData {
  headers: string[];
  list: CouponMock[];
  display: (DataCase & { code: string; expected: Record<string, string> })[];
  realDataChecks: (DataCase & { column: string; pattern: string })[];
  required: FormValidationCase[];
  create: {
    typedCode: string;
    expectedCode: string;
    form: FormFields;
    expectedPayload: Record<string, unknown>;
    toast: string;
  };
  saveError: DataCase & { form: FormFields; status: number; message: string };
  edit: {
    code: string;
    prefilled: Record<string, string>;
    form: FormFields;
    expectedPayload: Record<string, unknown>;
    toast: string;
  };
  editDates: DataCase & { code: string; prefilled: Record<string, string> };
  typeLabel: DataCase & { field: string; tableLabel: string; value: string };
  toggles: (DataCase & { code: string; column: string; field: string; from: boolean; toast: string })[];
  remove: { code: string; confirmText: string; toast: string };
}

export interface ReviewMock {
  id: number;
  user_name: string;
  user_email?: string;
  product_name: string;
  product_sku?: string;
  rating: number;
  content: string;
  status: 'pending' | 'approved' | 'hidden';
  created_at: string;
}

export interface ReviewsData {
  headers: string[];
  list: ReviewMock[];
  rows: (DataCase & { rowText: string; expected: Record<string, string>; actions: string[] })[];
  search: SearchCase[];
  filters: (DataCase & { status: string; rating: string; query: Record<string, string | null>; visible: string[]; emptyText?: string })[];
  statusActions: (DataCase & { rowText: string; action: string; reviewId: number; status: string; toast: string; badge: string })[];
  detail: { rowText: string; texts: string[]; approveButton: string; toast: string; badge: string };
  remove: { rowText: string; toast: string };
  updateError: DataCase & { rowText: string; status: number; message: string };
}

export interface BlogMock {
  id: number;
  title: string;
  slug: string;
  summary?: string;
  content?: string;
  thumbnail?: string;
  is_published: boolean;
  is_featured: boolean;
  created_at?: string;
}

export interface BlogData {
  headers: string[];
  list: BlogMock[];
  rows: (DataCase & { rowText: string; expected: Record<string, string>; actions: string[] })[];
  search: SearchCase[];
  validation: FormValidationCase[];
  create: { form: FormFields; expectedPayload: Record<string, unknown>; toast: string };
  slugCases: (DataCase & { steps: FormFields[]; expectedSlug: string })[];
  edit: {
    title: string;
    prefilled: Record<string, string>;
    form: FormFields;
    expectedPayload: Record<string, unknown>;
    toast: string;
  };
  toggles: (DataCase & { rowText: string; action: string; expectedPayload: Record<string, unknown>; toast: string; expected: Record<string, string> })[];
  view: { title: string; texts: string[] };
  remove: { title: string; toast: string };
  invalidImage: { url: string; error: string };
}

export interface ContactMock {
  id: number;
  name: string;
  email: string;
  phone: string;
  subject: string;
  message: string;
  status: 'pending' | 'processed';
  created_at: string;
}

export interface ContactsData {
  headers: string[];
  list: ContactMock[];
  rows: (DataCase & { rowText: string; expected: Record<string, string>; actions: string[] })[];
  search: SearchCase[];
  filters: (DataCase & { status: string; query: Record<string, string | null>; visible: string[]; emptyText?: string; list?: ContactMock[] })[];
  statusActions: (DataCase & { rowText: string; action: string; contactId: number; status: string; badge: string; actionsAfter: string[] })[];
  detail: { rowText: string; texts: string[]; button: string; badge: string };
  toast: string;
  remove: { rowText: string; toast: string };
}
