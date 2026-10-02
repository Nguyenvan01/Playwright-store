import { Page } from '@playwright/test';
import { Header } from './components/Header';
import { CartDrawer } from './components/CartDrawer';
import { HomePage } from './HomePage';
import { LoginPage } from './LoginPage';
import { CategoryPage } from './CategoryPage';
import { SearchPage } from './SearchPage';
import { ProductDetailPage } from './ProductDetailPage';
import { CheckoutPage } from './CheckoutPage';
import { OrderSuccessPage } from './OrderSuccessPage';
import { ProfilePage, OrdersPage, WishlistPage } from './AccountPages';
import { AdminLoginPage } from './admin/AdminLoginPage';
import { AdminLayout } from './admin/AdminLayout';
import { AdminUi } from './admin/AdminUi';

/** Gom toàn bộ Page Object của 1 `page` - tầng Keyword dùng qua đây. */
export class PageObjects {
  readonly header: Header;
  readonly cart: CartDrawer;
  readonly home: HomePage;
  readonly login: LoginPage;
  readonly search: SearchPage;
  readonly product: ProductDetailPage;
  readonly checkout: CheckoutPage;
  readonly orderSuccess: OrderSuccessPage;
  readonly profile: ProfilePage;
  readonly orders: OrdersPage;
  readonly wishlist: WishlistPage;
  readonly adminLogin: AdminLoginPage;
  readonly adminLayout: AdminLayout;
  readonly adminUi: AdminUi;

  constructor(readonly page: Page) {
    this.header = new Header(page);
    this.cart = new CartDrawer(page);
    this.home = new HomePage(page);
    this.login = new LoginPage(page);
    this.search = new SearchPage(page);
    this.product = new ProductDetailPage(page);
    this.checkout = new CheckoutPage(page);
    this.orderSuccess = new OrderSuccessPage(page);
    this.profile = new ProfilePage(page);
    this.orders = new OrdersPage(page);
    this.wishlist = new WishlistPage(page);
    this.adminLogin = new AdminLoginPage(page);
    this.adminLayout = new AdminLayout(page);
    this.adminUi = new AdminUi(page);
  }

  category(path: string): CategoryPage {
    return new CategoryPage(this.page, path);
  }
}
