import type { DataCase } from './types';
import type { FormFields, SearchCase } from './admin-marketing.types';

export interface WarehouseStats {
  totalProducts: number;
  totalStock: number;
  lowStock: number;
  outOfStock: number;
  totalValue: number;
}

export interface WarehouseProduct {
  id: number;
  name: string;
  sku: string;
  stock: number;
  price: number;
  cost_price: number | null;
  category_name: string;
}

export interface WarehouseMock {
  stats: WarehouseStats;
  products: WarehouseProduct[];
}

export interface WarehouseData {
  statLabels: string[];
  headers: string[];
  mock: WarehouseMock;
  statCards: Record<string, string>;
  rows: (DataCase & { rowText: string; expected: Record<string, string> })[];
  tabs: (DataCase & { tab: string; filter: string; visible: string[]; hidden: string[] })[];
  search: SearchCase[];
  tabBadges: (DataCase & { tab: string; badges: Record<string, number | null> })[];
  realStats: DataCase;
}

export interface ImportOrderMock {
  id: number;
  code: string;
  supplier_id: number;
  supplier_name: string;
  warehouse_name: string;
  order_date: string;
  expected_date?: string | null;
  total_amount: number;
  subtotal?: number;
  discount_amount?: number;
  shipping_fee?: number;
  paid_amount: number;
  payment_status: 'unpaid' | 'partial' | 'paid';
  status: 'draft' | 'processing' | 'partial_received' | 'received' | 'cancelled';
  note?: string;
  items?: {
    id: number;
    product_name: string;
    variant_name?: string;
    sku?: string;
    quantity_ordered: number;
    quantity_received: number;
    unit_cost: number;
    total_cost: number;
  }[];
}

export interface ImportMockData {
  imports: ImportOrderMock[];
  suppliers: { id: number; name: string }[];
  warehouses: { id: number; name: string }[];
  products: { id: number; name: string; sku: string; cost_price: number; variants: { id: number; name: string; sku: string }[] }[];
}

/** 1 dòng sản phẩm nhập trong form: product/variant là tên hiển thị trong select. */
export interface ImportItemInput {
  product?: string;
  variant?: string;
  quantity?: number | string;
  unitCost?: number | string;
  note?: string;
}

export interface ImportFormCase extends DataCase {
  form: FormFields;
  items: ImportItemInput[];
  toast: string;
}

export interface ImportData {
  headers: string[];
  mock: ImportMockData;
  statCards: Record<string, string>;
  rows: (DataCase & { rowText: string; expected: Record<string, string>; actions: string[] })[];
  filters: (DataCase & {
    action: 'status' | 'supplier' | 'search';
    value: string;
    query: Record<string, string | null>;
    visible: string[];
    emptyText?: string;
  })[];
  validation: ImportFormCase[];
  totals: DataCase & { form: FormFields; items: ImportItemInput[]; lineTotal: string; grandTotal: string };
  create: (DataCase & {
    form: FormFields;
    items: ImportItemInput[];
    payment?: FormFields;
    button: string;
    expectedPayload: Record<string, unknown>;
    toast: string;
  })[];
  createError: DataCase & { form: FormFields; items: ImportItemInput[]; status: number; message: string };
  detail: { rowText: string; id: number; texts: string[] };
  receive: {
    rowText: string;
    id: number;
    cases: (DataCase & { quantities: number[]; toast: string; expectedPayload?: Record<string, unknown> })[];
  };
  cancel: { rowText: string; id: number; toast: string };
}

export interface ReportOverviewMock {
  revenue: Record<string, unknown>;
  orders: Record<string, unknown>;
  products: Record<string, unknown>;
  customers: Record<string, unknown>;
}

export interface ReportsData {
  cardLabels: string[];
  sectionHeadings: string[];
  overview: ReportOverviewMock;
  emptyOverview: ReportOverviewMock;
  summaryCards: Record<string, string>;
  emptyCards: Record<string, string>;
  statusLegend: string[];
  sections: { heading: string; rows: number; firstRow: string[] }[];
  emptyTexts: Record<string, string>;
  periods: (DataCase & { value: string; label: string; apiPeriod: string })[];
  custom: DataCase & { start: string; end: string };
  customDefaults: DataCase;
  exports: (DataCase & { value: string; range?: { start: string; end: string }; filePattern: string; lines: string[] })[];
}

export interface SettingsData {
  mock: Record<string, string>;
  tabs: (DataCase & { tab: string; labels: string[] })[];
  validation: (DataCase & { form: FormFields; toast: string })[];
  loaded: DataCase & { fields: Record<string, string>; checkboxes: Record<string, boolean> };
  save: DataCase & { steps: { tab: string; form: FormFields }[]; expectedPayload: Record<string, unknown>; toast: string };
  serverError: DataCase & { status: number; message: string };
}
