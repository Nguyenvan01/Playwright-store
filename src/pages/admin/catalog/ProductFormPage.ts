import { Locator, Page } from '@playwright/test';

/** Form thêm / sửa sản phẩm (/admin/products/create, /admin/products/edit/:id). Ô nhập dùng AdminUi.field(label). */
export class ProductFormPage {
  readonly createPath = '/admin/products/create';
  readonly form: Locator;
  readonly submitButton: Locator;
  readonly backButton: Locator;
  readonly errorBox: Locator;
  readonly loadingText: Locator;
  readonly variantToggle: Locator;
  readonly variantBuilder: Locator;
  readonly generateButton: Locator;
  readonly variantRows: Locator;
  readonly imageUrlInput: Locator;
  readonly imageTiles: Locator;
  readonly mainImageBadge: Locator;
  readonly fileInput: Locator;

  constructor(readonly page: Page) {
    this.form = page.locator('main form');
    this.submitButton = this.form.locator('button[type="submit"]');
    this.backButton = page.getByRole('button', { name: 'Quay lại', exact: true });
    this.errorBox = this.form.locator('> div.bg-red-50');
    this.loadingText = page.getByText('Đang tải dữ liệu...', { exact: true });
    this.variantToggle = page.getByRole('button', { name: /^(\+ Tạo biến thể|Tắt chế độ)$/ });
    this.variantBuilder = this.section('Biến thể').locator('div.bg-gray-50.rounded-lg');
    this.generateButton = this.variantBuilder.getByRole('button', { name: /^Tạo \d+ biến thể$/ });
    this.variantRows = this.section('Biến thể').locator('div.grid.grid-cols-6').filter({ has: page.locator('input') });
    this.imageUrlInput = page.getByPlaceholder('Dán URL ảnh...', { exact: true });
    this.imageTiles = this.section('Hình ảnh').locator('div.aspect-square.group');
    this.mainImageBadge = this.section('Hình ảnh').getByText('Ảnh chính', { exact: true });
    this.fileInput = this.section('Hình ảnh').locator('input[type="file"]');
  }

  /** Khối có tiêu đề h3, vd: "Thông tin sản phẩm", "Biến thể", "Hình ảnh". */
  section(title: string): Locator {
    return this.page
      .locator('main form div.rounded-xl')
      .filter({ has: this.page.getByRole('heading', { name: title, exact: true }) })
      .first();
  }

  sizeButton(name: string): Locator {
    return this.variantBuilder.getByRole('button', { name, exact: true });
  }

  colorButton(name: string): Locator {
    return this.variantBuilder.getByRole('button', { name, exact: true });
  }

  variantCell(index: number, col: 'size' | 'color'): Locator {
    return this.variantRows.nth(index).locator('span').nth(col === 'size' ? 0 : 1);
  }

  variantSku(index: number): Locator {
    return this.variantRows.nth(index).locator('input').first();
  }

  variantRemove(index: number): Locator {
    return this.variantRows.nth(index).getByRole('button');
  }

  imageRemove(index: number): Locator {
    return this.imageTiles.nth(index).getByRole('button');
  }
}
