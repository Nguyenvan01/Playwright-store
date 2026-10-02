import { Page } from '@playwright/test';
import { ApiClient } from '@api/ApiClient';
import { PageObjects } from '@pages/PageObjects';
import { CommonKeywords } from './CommonKeywords';
import { AuthKeywords } from './AuthKeywords';
import { CatalogKeywords } from './CatalogKeywords';
import { CartKeywords } from './CartKeywords';
import { CheckoutKeywords } from './CheckoutKeywords';
import { AccountKeywords } from './AccountKeywords';
import { AdminKeywords } from './AdminKeywords';
import { ListingKeywords } from './ListingKeywords';
import { ProductKeywords } from './ProductKeywords';
import { ContentKeywords } from './ContentKeywords';
import { AdminCatalogKeywords } from './AdminCatalogKeywords';
import { AdminSalesKeywords } from './AdminSalesKeywords';
import { AdminMarketingKeywords } from './AdminMarketingKeywords';
import { AdminOpsKeywords } from './AdminOpsKeywords';

/**
 * Thư viện keyword (tầng nghiệp vụ). Dùng trong test qua fixture `k`:
 *   await k.catalog.openProduct(slug);
 *   await k.cart.verifyCartBadge(1);
 * Kịch bản JSON gọi cùng các keyword này bằng tên "nhóm.hàm", vd: "cart.verifyCartBadge".
 */
export class Keywords {
  readonly po: PageObjects;
  readonly common: CommonKeywords;
  readonly auth: AuthKeywords;
  readonly catalog: CatalogKeywords;
  readonly cart: CartKeywords;
  readonly checkout: CheckoutKeywords;
  readonly account: AccountKeywords;
  readonly admin: AdminKeywords;
  readonly listing: ListingKeywords;
  readonly product: ProductKeywords;
  readonly content: ContentKeywords;
  readonly adminCatalog: AdminCatalogKeywords;
  readonly adminSales: AdminSalesKeywords;
  readonly adminMarketing: AdminMarketingKeywords;
  readonly adminOps: AdminOpsKeywords;

  constructor(page: Page, api: ApiClient) {
    this.po = new PageObjects(page);
    this.common = new CommonKeywords(page, this.po, api);
    this.auth = new AuthKeywords(page, this.po, api);
    this.catalog = new CatalogKeywords(page, this.po, api);
    this.cart = new CartKeywords(page, this.po, api);
    this.checkout = new CheckoutKeywords(page, this.po, api);
    this.account = new AccountKeywords(page, this.po, api);
    this.admin = new AdminKeywords(page, this.po, api);
    this.listing = new ListingKeywords(page, this.po, api);
    this.product = new ProductKeywords(page, this.po, api);
    this.content = new ContentKeywords(page, this.po, api);
    this.adminCatalog = new AdminCatalogKeywords(page, this.po, api);
    this.adminSales = new AdminSalesKeywords(page, this.po, api);
    this.adminMarketing = new AdminMarketingKeywords(page, this.po, api);
    this.adminOps = new AdminOpsKeywords(page, this.po, api);
  }
}

/** Các nhóm keyword mà kịch bản JSON được phép gọi. */
export const KEYWORD_GROUPS = [
  'common', 'auth', 'catalog', 'listing', 'product', 'content', 'cart', 'checkout', 'account',
  'admin', 'adminCatalog', 'adminSales', 'adminMarketing', 'adminOps',
] as const;
export type KeywordGroup = (typeof KEYWORD_GROUPS)[number];
