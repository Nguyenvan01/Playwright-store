import { Locator, Page } from '@playwright/test';
import { modalByHeading, paginationBar } from '../sales/AdminApiMock';

/**
 * Trang danh sách sản phẩm (/admin/products).
 * Cột: 0 checkbox, 1 Sản phẩm, 2 SKU, 3 Danh mục, 4 Giá, 5 Tồn kho, 6 Đã bán, 7 Nổi bật, 8 Trạng thái, 9 Thao tác.
 */
export class ProductsListPage {
  readonly path = '/admin/products';
  readonly searchInput: Locator;
  readonly categorySelect: Locator;
  readonly brandSelect: Locator;
  readonly addLink: Locator;
  readonly dataRows: Locator;
  readonly headerCheckbox: Locator;
  readonly bulkBarText: Locator;
  readonly bulkDeleteButton: Locator;
  readonly paginationText: Locator;
  readonly deleteModal: Locator;

  constructor(readonly page: Page) {
    this.searchInput = page.getByPlaceholder('Tìm kiếm sản phẩm, SKU...', { exact: true });
    this.categorySelect = page.locator('select').filter({ has: page.locator('option', { hasText: 'Tất cả danh mục' }) });
    this.brandSelect = page.locator('select').filter({ has: page.locator('option', { hasText: 'Tất cả thương hiệu' }) });
    this.addLink = page.getByRole('link', { name: 'Thêm sản phẩm', exact: true });
    // Dòng dữ liệu thật (có checkbox) - bỏ qua dòng skeleton lúc đang tải
    this.dataRows = page.locator('tbody tr').filter({ has: page.getByRole('checkbox') });
    this.headerCheckbox = page.locator('thead').getByRole('checkbox');
    this.bulkBarText = page.getByText(/^\d+ sản phẩm được chọn$/);
    this.bulkDeleteButton = page.getByRole('button', { name: 'Xóa đã chọn', exact: true });
    this.paginationText = page.getByText(/^Trang \d+ trên \d+$/);
    this.deleteModal = modalByHeading(page, 'Xóa sản phẩm?');
  }

  row(name: string): Locator {
    return this.page.locator('tbody tr').filter({ has: this.page.getByText(name, { exact: true }) }).first();
  }

  rows(name: string): Locator {
    return this.page.locator('tbody tr').filter({ has: this.page.getByText(name, { exact: true }) });
  }

  cell(name: string, index: number): Locator {
    return this.row(name).locator('td').nth(index);
  }

  rowCheckbox(name: string): Locator {
    return this.row(name).getByRole('checkbox');
  }

  /** Nút ngôi sao (title "Đánh dấu nổi bật" / "Bỏ nổi bật"). */
  featuredButton(name: string): Locator {
    return this.cell(name, 7).getByRole('button');
  }

  /** Nút gạt trạng thái bán (không có title/tên). */
  statusButton(name: string): Locator {
    return this.cell(name, 8).getByRole('button');
  }

  action(name: string, title: 'Xem' | 'Sửa' | 'Xóa'): Locator {
    return this.cell(name, 9).getByTitle(title, { exact: true });
  }

  get pagination(): Locator {
    return paginationBar(this.page);
  }

  pageButton(n: number): Locator {
    return this.pagination.getByRole('button', { name: String(n), exact: true });
  }

  get nextPageButton(): Locator {
    return this.pagination.getByRole('button').last();
  }
}
