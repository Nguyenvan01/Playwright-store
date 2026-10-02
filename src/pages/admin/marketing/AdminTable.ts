import { Locator, Page } from '@playwright/test';
import { AdminUi } from '../AdminUi';

/**
 * Locator dùng chung cho bảng/modal của các trang quản trị (marketing + vận hành).
 * Lưu ý: tiêu đề cột dùng CSS `uppercase` -> innerText bị viết hoa, phải đọc textContent.
 */
export class AdminTable {
  readonly ui: AdminUi;

  constructor(readonly page: Page) {
    this.ui = new AdminUi(page);
  }

  /** Bảng chính đầu tiên đang hiển thị trên trang. */
  get table(): Locator {
    return this.page.locator('table').filter({ visible: true }).first();
  }

  get headerCells(): Locator {
    return this.table.locator('thead th');
  }

  /** Các dòng dữ liệu đang hiển thị của bảng chính. */
  get rows(): Locator {
    return this.table.locator('tbody tr').filter({ visible: true });
  }

  /** Tên cột (textContent, đã trim) của bảng chính. */
  async headerTexts(): Promise<string[]> {
    return (await this.headerCells.allTextContents()).map((t) => t.trim());
  }

  /** Dòng đầu tiên chứa text. */
  row(text: string): Locator {
    return this.ui.row(text).first();
  }

  /** Ô của dòng chứa `rowText` tại cột có tên `header`. */
  async cell(rowText: string, header: string): Promise<Locator> {
    const headers = await this.headerTexts();
    const idx = headers.findIndex((h) => h.toLowerCase() === header.toLowerCase());
    if (idx < 0) throw new Error(`Không có cột "${header}". Cột hiện có: ${headers.join(' | ')}`);
    return this.row(rowText).locator('td').nth(idx);
  }

  /** Ô ở cột `header` của dòng thứ `index` (0 = dòng đầu). */
  async cellAt(index: number, header: string): Promise<Locator> {
    const headers = await this.headerTexts();
    const idx = headers.findIndex((h) => h.toLowerCase() === header.toLowerCase());
    if (idx < 0) throw new Error(`Không có cột "${header}". Cột hiện có: ${headers.join(' | ')}`);
    return this.rows.nth(index).locator('td').nth(idx);
  }

  /** Các nút có thuộc tính title trong dòng chứa text. */
  titledButtons(rowText: string): Locator {
    return this.row(rowText).locator('button[title]');
  }

  /** Modal (lớp phủ fixed) có tiêu đề `heading`. */
  modal(heading: string): Locator {
    return this.page
      .locator('div.fixed.inset-0')
      .filter({ has: this.page.getByRole('heading', { name: heading, exact: true }) })
      .last();
  }

  /** Nút theo tên trong modal có tiêu đề `heading`. */
  modalButton(heading: string, name: string): Locator {
    return this.modal(heading).getByRole('button', { name, exact: true }).first();
  }

  /** Thẻ thống kê: đoạn giá trị ngay sau nhãn `label`. */
  statValue(label: string): Locator {
    return this.page
      .locator('p')
      .filter({ hasText: new RegExp(`^\\s*${label.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\s*$`), visible: true })
      .first()
      .locator('xpath=following-sibling::p[1]');
  }

  /** Select (không có label) nhận diện qua 1 option value đặc trưng. */
  selectWithOption(value: string): Locator {
    return this.page.locator('select').filter({ has: this.page.locator(`option[value="${value}"]`), visible: true }).first();
  }
}
