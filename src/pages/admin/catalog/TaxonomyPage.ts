import { Locator, Page } from '@playwright/test';
import { modalByHeading } from '../sales/AdminApiMock';

/**
 * Trang dạng lưới thẻ: Danh mục (/admin/categories) và Thương hiệu (/admin/brands) - cùng cấu trúc.
 * Nút Sửa / Xóa trên thẻ là icon KHÔNG có tên/title và ẩn (opacity-0) tới khi hover thẻ.
 * Thứ tự nút trong thẻ: 0 Sửa, 1 Xóa, 2 gạt Hoạt động.
 */
export class TaxonomyPage {
  readonly cards: Locator;
  readonly cardNames: Locator;

  constructor(readonly page: Page) {
    this.cards = page.locator('main div.rounded-xl.group');
    this.cardNames = this.cards.locator('h3');
  }

  card(name: string): Locator {
    return this.cards.filter({ has: this.page.getByRole('heading', { name, exact: true }) });
  }

  editButton(name: string): Locator {
    return this.card(name).getByRole('button').nth(0);
  }

  deleteButton(name: string): Locator {
    return this.card(name).getByRole('button').nth(1);
  }

  toggleButton(name: string): Locator {
    return this.card(name).getByRole('button').nth(2);
  }

  featuredBadge(name: string): Locator {
    return this.card(name).getByText('Nổi bật', { exact: true });
  }

  slug(name: string): Locator {
    return this.card(name).locator('p.font-mono');
  }

  modal(heading: string): Locator {
    return modalByHeading(this.page, heading);
  }

  get deleteModal(): Locator {
    return modalByHeading(this.page, 'Xác nhận xóa');
  }

  get deleteMessage(): Locator {
    return this.deleteModal.locator('p.text-gray-600');
  }
}
