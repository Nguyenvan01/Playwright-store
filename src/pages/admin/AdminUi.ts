import { Locator, Page } from '@playwright/test';

const escapeRe = (s: string) => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');

/**
 * Locator dùng chung cho mọi trang quản trị.
 * Form admin dùng <label> KHÔNG gắn htmlFor -> tìm ô nhập đứng ngay sau label.
 */
export class AdminUi {
  constructor(readonly page: Page) {}

  /** Tiêu đề trang trên header admin. */
  get pageTitle(): Locator {
    return this.page.locator('header h1');
  }

  /** Ô input/select/textarea ngay sau <label> có text `label` (bỏ qua dấu * bắt buộc). */
  field(label: string): Locator {
    const re = new RegExp(`^\\s*${escapeRe(label.replace(/\s*\*\s*$/, ''))}\\s*\\*?\\s*$`);
    return this.page
      .locator('label')
      .filter({ hasText: re, visible: true })
      .first()
      .locator('xpath=following::*[self::input or self::select or self::textarea][1]');
  }

  /** Checkbox nằm trong <label> (vd: "Hoạt động", "Nổi bật"). */
  checkbox(label: string): Locator {
    return this.page.getByRole('checkbox', { name: label, exact: true }).filter({ visible: true }).first();
  }

  /** Nút theo tên hiển thị (lấy nút hiển thị cuối cùng - thường là nút trong modal đang mở). */
  button(name: string): Locator {
    return this.page.getByRole('button', { name, exact: true }).filter({ visible: true }).last();
  }

  heading(text: string): Locator {
    return this.page.getByRole('heading', { name: text, exact: true }).filter({ visible: true }).first();
  }

  /** Dòng trong bảng chứa text. */
  row(text: string): Locator {
    return this.page.locator('tbody tr').filter({ hasText: text, visible: true });
  }

  /** Nút hành động trong 1 dòng, nhận diện qua title (vd: "Sửa", "Xóa", "Xem chi tiết"). */
  rowAction(rowText: string, title: string): Locator {
    return this.row(rowText).first().getByTitle(title, { exact: true });
  }

  get tableHeaders(): Locator {
    return this.page.locator('thead th').filter({ visible: true });
  }
}
