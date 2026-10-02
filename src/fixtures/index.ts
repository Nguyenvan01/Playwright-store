import { test as base, expect } from '@playwright/test';
import { ApiClient, ProductDetail, ProductSize } from '@api/ApiClient';
import { Keywords } from '@keywords/index';
import { baseContext, DataContext } from '@data/loader';
import { env } from '@config/env';
import {
  HomePage,
  Header,
  CartDrawer,
  LoginPage,
  SearchPage,
  ProductDetailPage,
  CheckoutPage,
  OrderSuccessPage,
  ProfilePage,
  OrdersPage,
  WishlistPage,
  AdminLoginPage,
  AdminLayout,
} from '@pages/index';

type TestFixtures = {
  api: ApiClient;
  /** Thư viện keyword (tầng nghiệp vụ) - cách viết test chính. */
  k: Keywords;
  /** Context thay biến cho dữ liệu: env, product, size, productFirstWord. */
  ctx: DataContext;
  // Page Object - dùng khi cần locator trực tiếp trong test
  header: Header;
  cartDrawer: CartDrawer;
  homePage: HomePage;
  loginPage: LoginPage;
  searchPage: SearchPage;
  productPage: ProductDetailPage;
  checkoutPage: CheckoutPage;
  orderSuccessPage: OrderSuccessPage;
  profilePage: ProfilePage;
  ordersPage: OrdersPage;
  wishlistPage: WishlistPage;
  adminLoginPage: AdminLoginPage;
  adminLayout: AdminLayout;
};

type AutoFixtures = {
  /** Tự động: chặn mọi request ghi dữ liệu thật khi E2E_ALLOW_WRITE=0. */
  writeGuard: string[];
};

/** Request ghi vẫn cho đi qua (đăng nhập/đăng xuất không đổi dữ liệu). */
const WRITE_ALLOWLIST = [/\/api\/auth\/login$/, /\/api\/admin\/login$/, /\/api\/admin\/logout$/];

type WorkerFixtures = {
  /** 1 sản phẩm thật (lấy qua API) có size còn hàng - dùng chung trong cả worker. */
  purchasable: { product: ProductDetail; size: ProductSize };
};

export const test = base.extend<TestFixtures & AutoFixtures, WorkerFixtures>({
  writeGuard: [
    async ({ page }, use, testInfo) => {
      const blocked: string[] = [];
      if (!env.allowWrite) {
        // Đăng ký TRƯỚC mọi mock trong test -> mock của test (đăng ký sau) luôn được ưu tiên.
        await page.route('**/api/**', async (route) => {
          const req = route.request();
          const url = new URL(req.url());
          if (req.method() === 'GET' || req.method() === 'OPTIONS' || WRITE_ALLOWLIST.some((r) => r.test(url.pathname))) {
            return route.fallback();
          }
          blocked.push(`${req.method()} ${url.pathname}`);
          await route.fulfill({ status: 418, json: { success: false, message: '[E2E] Đã chặn ghi dữ liệu thật' } });
        });
      }
      await use(blocked);
      if (blocked.length) {
        testInfo.annotations.push({ type: 'write-blocked', description: blocked.join(', ') });
      }
    },
    { auto: true },
  ],

  api: async ({ request }, use) => use(new ApiClient(request)),
  k: async ({ page, api }, use) => use(new Keywords(page, api)),
  ctx: async ({ purchasable }, use) =>
    use({
      ...baseContext(),
      product: purchasable.product,
      size: purchasable.size,
      productFirstWord: purchasable.product.name.split(' ')[0],
    }),

  header: async ({ page }, use) => use(new Header(page)),
  cartDrawer: async ({ page }, use) => use(new CartDrawer(page)),
  homePage: async ({ page }, use) => use(new HomePage(page)),
  loginPage: async ({ page }, use) => use(new LoginPage(page)),
  searchPage: async ({ page }, use) => use(new SearchPage(page)),
  productPage: async ({ page }, use) => use(new ProductDetailPage(page)),
  checkoutPage: async ({ page }, use) => use(new CheckoutPage(page)),
  orderSuccessPage: async ({ page }, use) => use(new OrderSuccessPage(page)),
  profilePage: async ({ page }, use) => use(new ProfilePage(page)),
  ordersPage: async ({ page }, use) => use(new OrdersPage(page)),
  wishlistPage: async ({ page }, use) => use(new WishlistPage(page)),
  adminLoginPage: async ({ page }, use) => use(new AdminLoginPage(page)),
  adminLayout: async ({ page }, use) => use(new AdminLayout(page)),

  purchasable: [
    async ({ playwright }, use) => {
      const request = await playwright.request.newContext();
      try {
        await use(await new ApiClient(request).findPurchasableProduct());
      } finally {
        await request.dispose();
      }
    },
    { scope: 'worker' },
  ],
});

export { expect };
