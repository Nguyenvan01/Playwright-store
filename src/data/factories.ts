/** Sinh dữ liệu test ngẫu nhiên, không trùng giữa các lần chạy. */
const uid = () => `${Date.now()}${Math.floor(Math.random() * 1000)}`;

export interface CustomerData {
  name: string;
  email: string;
  phone: string;
  password: string;
}

export function buildCustomer(overrides: Partial<CustomerData> = {}): CustomerData {
  const id = uid();
  return {
    name: `E2E Tester ${id.slice(-4)}`,
    email: `e2e.${id}@example.com`,
    phone: `09${id.slice(-8)}`,
    password: 'E2e@123456',
    ...overrides,
  };
}

export interface ShippingInfo {
  firstName: string;
  lastName: string;
  phone: string;
  city: string; // value của <option>, vd: 'hcm'
  district: string; // vd: 'quan-1'
  ward?: string; // vd: 'phuong-1'
  address: string;
}

export function buildShippingInfo(overrides: Partial<ShippingInfo> = {}): ShippingInfo {
  return {
    firstName: 'Nguyễn',
    lastName: 'Kiểm Thử',
    phone: '0912345678',
    city: 'hcm',
    district: 'quan-1',
    ward: 'phuong-1',
    address: '123 Lê Lợi',
    ...overrides,
  };
}

/** Item đúng định dạng CartContext lưu trong localStorage `clothing_store_cart`. */
export interface CartItem {
  id: string;
  product_id: number;
  variant_id: number | null;
  name: string;
  slug: string;
  price: number;
  compare_price: number | null;
  image: string | null;
  quantity: number;
  size: string | null;
  color: string | null;
}

export function buildCartItem(overrides: Partial<CartItem> = {}): CartItem {
  const productId = overrides.product_id ?? 1;
  return {
    id: `${productId}-M-default-${uid()}`,
    product_id: productId,
    variant_id: null,
    name: 'Áo thun E2E',
    slug: 'ao-thun-e2e',
    price: 199000,
    compare_price: null,
    image: null,
    quantity: 1,
    size: 'M',
    color: null,
    ...overrides,
  };
}
