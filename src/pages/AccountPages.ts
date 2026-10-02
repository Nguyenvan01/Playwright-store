import { Locator, Page } from '@playwright/test';
import { BasePage } from './BasePage';
import { Header } from './components/Header';
import { cssText, escapeRegex } from './account/cssText';

/**
 * Trang /profile (ProfilePage.jsx).
 * Lưu ý: mở trực tiếp /profile bị crash (bug) -> vào qua menu tài khoản trên header.
 * Ô nhập không gắn label -> định vị qua đoạn chữ nhãn đứng ngay trước (FieldLabel <p>).
 */
export class ProfilePage extends BasePage {
  readonly path = '/profile';
  readonly header: Header;
  readonly accountInfoHeading: Locator;
  readonly heading: Locator;
  readonly editButton: Locator;
  readonly changePasswordButton: Locator;
  /** Khối "Thông tin tài khoản" (xem + sửa). */
  readonly accountInfo: Locator;
  readonly nameInput: Locator;
  readonly emailInput: Locator;
  readonly phoneInput: Locator;
  readonly birthDateInput: Locator;
  readonly genderSelect: Locator;
  readonly saveButton: Locator;
  readonly cancelEditButton: Locator;
  readonly defaultAddressSection: Locator;
  readonly updateAddressLink: Locator;
  /** Dải 4 ô thống kê (Tổng đơn hàng, Đơn đang xử lý...). */
  readonly summary: Locator;
  readonly recentOrdersSection: Locator;
  readonly recentFavoritesSection: Locator;

  constructor(page: Page) {
    super(page);
    this.header = new Header(page);
    this.accountInfoHeading = page.getByRole('heading', { name: 'Thông tin tài khoản' });
    this.heading = page.getByRole('heading', { level: 1, name: 'Hồ sơ cá nhân' });
    this.editButton = page.getByRole('button', { name: 'Chỉnh sửa', exact: true });
    this.changePasswordButton = page.getByRole('button', { name: 'Đổi mật khẩu', exact: true });
    // AccountLayout bọc nội dung trong 1 <section> ngoài cùng -> lấy section trong cùng (.last()).
    this.accountInfo = page.locator('section').filter({ has: this.accountInfoHeading }).last();
    this.nameInput = this.accountInfo.locator('p:text-is("Họ và tên *") + input');
    this.emailInput = this.accountInfo.locator('p:text-is("Email") + input');
    this.phoneInput = this.accountInfo.locator('p:text-is("Số điện thoại") + input');
    this.birthDateInput = this.accountInfo.getByPlaceholder('1995-05-15');
    this.genderSelect = this.accountInfo.locator('p:text-is("Giới tính") + select');
    this.saveButton = this.accountInfo.getByRole('button', { name: /^(Lưu thay đổi|Đang lưu\.\.\.)$/ });
    this.cancelEditButton = this.accountInfo.getByRole('button', { name: 'Hủy', exact: true });
    this.defaultAddressSection = page
      .locator('section')
      .filter({ has: page.getByRole('heading', { name: 'Địa chỉ giao hàng mặc định' }) })
      .last();
    this.updateAddressLink = this.defaultAddressSection.getByRole('link', { name: 'Cập nhật địa chỉ' });
    this.summary = page.locator('main div.grid').filter({ has: page.locator('p:text-is("Tổng đơn hàng")') });
    this.recentOrdersSection = page
      .locator('section')
      .filter({ has: page.getByRole('heading', { name: 'Đơn hàng gần đây' }) })
      .last();
    this.recentFavoritesSection = page
      .locator('section')
      .filter({ has: page.getByRole('heading', { name: 'Sản phẩm yêu thích gần đây' }) })
      .last();
  }

  /** Giá trị hiển thị của 1 trường ở chế độ xem, vd: fieldValue("Email"). */
  fieldValue(label: string): Locator {
    return this.accountInfo.locator(`p:text-is("${cssText(label)}") + p`);
  }

  /** Giá trị 1 ô thống kê, vd: summaryValue("Tổng đơn hàng"). */
  summaryValue(label: string): Locator {
    return this.summary.locator(`p:text-is("${cssText(label)}") + p`);
  }
}

/** Trang /orders (OrdersPage.jsx + OrderListItem.jsx). */
export class OrdersPage extends BasePage {
  readonly path = '/orders';
  readonly searchInput: Locator;
  readonly heading: Locator;
  /** Mỗi đơn là 1 <article>. */
  readonly orderItems: Locator;

  constructor(page: Page) {
    super(page);
    this.searchInput = page.getByPlaceholder('Tìm theo mã đơn hàng...');
    this.heading = page.getByRole('heading', { level: 1, name: 'Đơn hàng của tôi' });
    this.orderItems = page.locator('main article');
  }

  /** Ô thống kê (nút) có nhãn + số đếm, vd: statButton("Đã hủy") -> "Đã hủy 1". */
  statButton(label: string): Locator {
    return this.page.getByRole('button', { name: new RegExp(`^${escapeRegex(label)} [\\d.]+$`) });
  }

  /** Số đếm bên dưới nhãn của ô thống kê. */
  statCount(label: string): Locator {
    return this.statButton(label).locator('p').nth(1);
  }

  /** Tab lọc trạng thái (tên khớp tuyệt đối để không nhầm với ô thống kê). */
  tab(label: string): Locator {
    return this.page.getByRole('button', { name: label, exact: true });
  }

  orderItem(code: string): Locator {
    return this.orderItems.filter({ has: this.page.getByRole('link', { name: code, exact: true }) });
  }

  statusBadge(code: string): Locator {
    return this.orderItem(code).locator('span.rounded-full');
  }

  cancelButton(code: string): Locator {
    return this.orderItem(code).getByRole('button', { name: /^(Hủy đơn|Đang hủy\.\.\.)$/ });
  }

  detailLink(code: string): Locator {
    return this.orderItem(code).getByRole('link', { name: 'Xem chi tiết', exact: true });
  }

  emptyState(title: string): Locator {
    return this.page.locator('main').getByText(title, { exact: true });
  }
}

/** Trang /favorites (WishlistPage.jsx + FavoriteProductCard.jsx). */
export class WishlistPage extends BasePage {
  readonly path = '/favorites';
  readonly heading: Locator;
  /** Chỉ hiển thị khi danh sách yêu thích có sản phẩm. */
  readonly searchInput: Locator;
  readonly emptyState: Locator;
  readonly countMeta: Locator;
  readonly sortSelect: Locator;
  readonly cards: Locator;
  readonly cardNames: Locator;
  readonly noMatch: Locator;
  /** Nút trái tim trên trang danh mục (MenPage.jsx) - chỉ để trang trí, không gọi API. */
  readonly listingHeartButtons: Locator;

  constructor(page: Page) {
    super(page);
    this.heading = page.getByRole('heading', { level: 1, name: 'Danh sách yêu thích' });
    this.searchInput = page.getByPlaceholder('Tìm sản phẩm yêu thích...');
    this.emptyState = page.getByText('Bạn chưa có sản phẩm yêu thích');
    this.countMeta = page.locator('main').getByText(/^[\d.]+ sản phẩm yêu thích$/);
    this.sortSelect = page.locator('main select');
    this.cards = page.locator('main article');
    this.cardNames = this.cards.locator('h3');
    this.noMatch = page.locator('main').getByText('Không tìm thấy sản phẩm phù hợp', { exact: true });
    this.listingHeartButtons = page.locator('main').getByRole('button', { name: 'favorite', exact: true });
  }

  card(name: string): Locator {
    return this.cards.filter({ has: this.page.getByRole('heading', { name, exact: true }) });
  }

  removeButton(name: string): Locator {
    return this.card(name).getByRole('button', { name: 'Bỏ yêu thích' });
  }

  addToCartButton(name: string): Locator {
    return this.card(name).getByRole('button', { name: /^(Thêm vào giỏ hàng|Đang thêm\.\.\.)$/ });
  }

  outOfStockOverlay(name: string): Locator {
    return this.card(name).getByText('Hết hàng', { exact: true });
  }
}
