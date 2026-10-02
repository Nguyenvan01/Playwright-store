import { Locator, Page } from '@playwright/test';
import { escapeRegex } from './cssText';

/** Trang /addresses (AddressesPage.jsx). Ô nhập không có label -> dùng placeholder; nút icon -> title. */
export class AddressesPage {
  readonly path = '/addresses';
  readonly heading: Locator;
  readonly subtitle: Locator;
  /** Nút "Thêm địa chỉ" trên tiêu đề (tên gồm chữ icon "add_location"). */
  readonly addButton: Locator;
  readonly emptyTitle: Locator;
  readonly emptyAddButton: Locator;
  readonly form: Locator;
  readonly formHeading: Locator;
  readonly fullName: Locator;
  readonly phone: Locator;
  readonly address: Locator;
  readonly ward: Locator;
  readonly district: Locator;
  readonly city: Locator;
  readonly defaultCheckbox: Locator;
  readonly submitButton: Locator;
  readonly cancelButton: Locator;
  readonly cards: Locator;
  readonly defaultBadges: Locator;
  readonly deleteModal: Locator;
  readonly confirmDeleteButton: Locator;
  readonly cancelDeleteButton: Locator;

  constructor(readonly page: Page) {
    this.heading = page.getByRole('heading', { level: 1, name: 'Địa chỉ' });
    this.subtitle = this.heading.locator('xpath=following-sibling::p[1]');
    this.addButton = page.getByRole('button', { name: 'add_location Thêm địa chỉ', exact: true });
    this.emptyTitle = page.getByText('Bạn chưa có địa chỉ nào', { exact: true });
    this.emptyAddButton = page.getByRole('button', { name: 'Thêm địa chỉ mới', exact: true });
    this.form = page.locator('main form');
    this.formHeading = page.getByRole('heading', { level: 2, name: /^(Thêm địa chỉ mới|Sửa địa chỉ)$/ });
    this.fullName = this.form.getByPlaceholder('Nguyễn Văn A');
    this.phone = this.form.getByPlaceholder('0912 345 678');
    this.address = this.form.getByPlaceholder('123 Đường ABC, Phường XYZ');
    this.ward = this.form.getByPlaceholder('Phường Bến Nghé');
    this.district = this.form.getByPlaceholder('Quận 1');
    this.city = this.form.locator('select');
    this.defaultCheckbox = this.form.getByRole('checkbox', { name: 'Đặt làm địa chỉ mặc định' });
    this.submitButton = this.form.locator('button[type="submit"]');
    this.cancelButton = this.form.getByRole('button', { name: 'Hủy', exact: true });
    this.cards = page.locator('main div.rounded-2xl').filter({ has: page.locator('button[title="Xóa"]') });
    this.defaultBadges = this.cards.getByText('Mặc định', { exact: true });
    this.deleteModal = page
      .locator('div.fixed.inset-0')
      .filter({ has: page.getByRole('heading', { level: 3, name: 'Xóa địa chỉ' }) });
    this.confirmDeleteButton = this.deleteModal.getByRole('button', { name: /^(Xóa địa chỉ|Đang xóa\.\.\.)$/ });
    this.cancelDeleteButton = this.deleteModal.getByRole('button', { name: 'Hủy', exact: true });
  }

  card(name: string): Locator {
    return this.cards.filter({ has: this.page.locator('p.font-semibold', { hasText: new RegExp(`^${escapeRegex(name)}$`) }) });
  }

  /** Dòng tên người nhận (+ badge "Mặc định" nếu có). */
  nameRow(name: string): Locator {
    return this.card(name).locator('div:has(> p.font-semibold)');
  }

  defaultBadge(name: string): Locator {
    return this.card(name).getByText('Mặc định', { exact: true });
  }

  setDefaultButton(name: string): Locator {
    return this.card(name).getByTitle('Đặt làm mặc định');
  }

  editButton(name: string): Locator {
    return this.card(name).getByTitle('Sửa', { exact: true });
  }

  deleteButton(name: string): Locator {
    return this.card(name).getByTitle('Xóa', { exact: true });
  }

  fieldError(message: string): Locator {
    return this.form.getByText(message, { exact: true });
  }
}
