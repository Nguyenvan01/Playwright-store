import type { DataCase } from './types';

/** Kiểu dữ liệu cho test-data/admin-catalog/*.json (sản phẩm, form sản phẩm, danh mục, thương hiệu). */

export type FormValues = Record<string, string | number | boolean>;

export interface CatalogCategory {
  id: number;
  name: string;
  slug: string;
  description?: string | null;
  icon?: string;
  sort_order?: number;
  is_featured: boolean;
  is_active: boolean;
}

export interface CatalogBrand {
  id: number;
  name: string;
  slug: string;
  description?: string | null;
  logo?: string;
  is_featured: boolean;
  is_active: boolean;
}

export interface CatalogProduct {
  id: number;
  name: string;
  slug: string;
  sku: string;
  price: number;
  stock: number;
  total_sold: number;
  is_featured: boolean;
  is_active: boolean;
  category_id: number;
  brand_id: number;
  category_name: string;
  brand_name: string;
  image: string | null;
  [key: string]: unknown;
}

/** Dữ liệu giả cho GET /admin/products, /admin/products/:id, /admin/categories, /admin/brands. */
export interface CatalogFixture {
  categories?: CatalogCategory[];
  brands?: CatalogBrand[];
  products?: CatalogProduct[];
  productDetails?: Record<string, Record<string, unknown>>;
  /** Ghi đè tổng số sản phẩm (để có nhiều trang) - danh sách trả về vẫn là `products`. */
  productsTotal?: number;
}

export interface ProductRowExpect {
  name: string;
  brand: string;
  sku: string;
  category: string;
  price: string;
  stock: string;
  sold: string;
  featured: boolean;
  active: boolean;
  lowStock?: boolean;
}

export interface ProductFilterCase extends DataCase {
  search?: string;
  category?: string;
  brand?: string;
  request: Record<string, string>;
  rows: string[];
  hidden: string[];
}

export interface ProductFeaturedCase extends DataCase {
  product: string;
  productId: number;
  before: string;
  after: string;
  toast: string;
  status?: number;
}

export interface ProductStatusCase extends DataCase {
  product: string;
  productId: number;
  before: boolean;
  after: boolean;
  toast: string;
  status?: number;
}

export interface ProductDeleteCase extends DataCase {
  product: string;
  productId: number;
  status: number;
  toast: string;
  removed: boolean;
}

export interface ProductsData {
  headers: string[];
  rows: ProductRowExpect[];
  filters: ProductFilterCase[];
  featured: ProductFeaturedCase[];
  status: ProductStatusCase[];
  delete: ProductDeleteCase[];
  deleteModal: { heading: string; message: string };
  bulk: { select: string[]; text: string; allText: string };
  pagination: { total: number; first: string; second: string };
  viewLink: { product: string; href: string };
  editLink: { product: string; path: string };
}

export interface VariantRowExpect {
  size: string;
  color: string;
  sku: string;
}

export interface ProductFormData {
  validation: (DataCase & { fields: FormValues; error: string })[];
  slugs: (DataCase & { name: string; slug: string })[];
  variants: {
    sku: string;
    price: string;
    sizes: string[];
    colors: string[];
    buttonBefore: string;
    buttonAfter: string;
    rows: VariantRowExpect[];
  };
  images: { urls: string[]; mainBadge: string };
  create: {
    fields: FormValues;
    imageUrl: string;
    slug: string;
    payload: Record<string, unknown>;
    response: unknown;
    toast: string;
    error: { status: number; message: string };
  };
  edit: {
    id: number;
    path: string;
    product: string;
    prefill: Record<string, string>;
    variantCount: number;
    imageCount: number;
    change: FormValues;
    payload: Record<string, unknown>;
    toast: string;
    fromListBug: string;
  };
  upload: { fileName: string; response: unknown; knownBug: string };
}

export interface TaxonomySearchCase extends DataCase {
  text: string;
  visible: string[];
  hidden: string[];
  empty?: boolean;
}

/** 1 loại trang lưới thẻ: danh mục hoặc thương hiệu. */
export interface TaxonomyEntity {
  key: 'category' | 'brand';
  label: string;
  path: string;
  title: string;
  api: 'categories' | 'brands';
  fixture: 'categories' | 'brands';
  responseKey: string;
  searchPlaceholder: string;
  addButton: string;
  addHeading: string;
  editHeading: string;
  nameLabel: string;
  empty: string;
  deleteMessage: string;
  toasts: {
    created: string;
    updated: string;
    saveFailed: string;
    deleted: string;
    toggled: string;
    toggleFailed: string;
  };
  searches: TaxonomySearchCase[];
  create: { form: FormValues; payload: Record<string, unknown>; response: unknown; name: string };
  edit: {
    target: string;
    id: number;
    prefill: Record<string, string>;
    form: FormValues;
    payload: Record<string, unknown>;
    response: unknown;
    name: string;
    description: string;
  };
  delete: { target: string; id: number; errorMessage: string };
  toggle: { target: string; id: number; payload: Record<string, unknown> };
  featured: { target: string; knownBug: string };
  slugAutofill?: (DataCase & { name: string; slug: string })[];
}
