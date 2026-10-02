import { Locator, Page } from '@playwright/test';
import { modalByHeading, paginationBar } from './AdminApiMock';

/** Phần chung của trang Khách hàng / Nhân viên: bảng, modal, lỗi field, phân trang. */
abstract class PeopleListPage {
  constructor(readonly page: Page) {}

  row(name: string): Locator {
    return this.page.locator('tbody tr').filter({ has: this.page.getByText(name, { exact: true }) }).first();
  }

  rows(name: string): Locator {
    return this.page.locator('tbody tr').filter({ has: this.page.getByText(name, { exact: true }) });
  }

  cell(name: string, index: number): Locator {
    return this.row(name).locator('td').nth(index);
  }

  modal(heading: string): Locator {
    return modalByHeading(this.page, heading);
  }

  /** Thông báo lỗi dưới các ô nhập trong modal đang mở (chữ đỏ). */
  fieldErrors(heading: string): Locator {
    return this.modal(heading).locator('p.text-red-500');
  }

  get pagination(): Locator {
    return paginationBar(this.page);
  }

  get paginationText(): Locator {
    return this.pagination.getByText(/^Trang \d+/);
  }

  pageButton(n: number): Locator {
    return this.pagination.getByRole('button', { name: String(n), exact: true });
  }

  get nextPageButton(): Locator {
    return this.pagination.getByRole('button').last();
  }
}

/** Trang Khách hàng (/admin/customers). Cột: 0 Khách hàng, 1 Liên hệ, 2 Đơn hàng, 3 Tổng chi tiêu, 4 Điểm, 5 Trạng thái, 6 Thao tác. */
export class CustomersPage extends PeopleListPage {
  readonly path = '/admin/customers';
  readonly searchPlaceholder = 'Tìm theo tên, email, SĐT...';

  statusBadge(name: string): Locator {
    return this.cell(name, 5).locator('span');
  }

  /** Giá trị 1 dòng "Nhãn: giá trị" trong modal Chi tiết khách hàng. */
  detailValue(label: string): Locator {
    return this.modal('Chi tiết khách hàng')
      .locator('div.flex.justify-between')
      .filter({ has: this.page.getByText(label, { exact: true }) })
      .locator('span')
      .last();
  }

  /** Ô số liệu (Đơn hàng / Tổng chi tiêu) trong modal chi tiết. */
  detailStat(label: string): Locator {
    return this.modal('Chi tiết khách hàng')
      .locator('div.rounded-lg.text-center')
      .filter({ has: this.page.getByText(label, { exact: true }) })
      .locator('p')
      .last();
  }

  get detailRecentOrders(): Locator {
    return this.modal('Chi tiết khách hàng').locator('div.space-y-2 > div.rounded-lg');
  }

  get deleteWarning(): Locator {
    return this.modal('Xác nhận xóa').locator('p.text-orange-500');
  }
}

/** Trang Nhân viên (/admin/employees). Cột: 0 Nhân viên, 1 Email, 2 Điện thoại, 3 Vai trò, 4 Ngày tạo, 5 Trạng thái, 6 Thao tác. */
export class EmployeesPage extends PeopleListPage {
  readonly path = '/admin/employees';
  readonly searchPlaceholder = 'Tìm theo tên, email...';
  readonly heading: Locator;

  constructor(page: Page) {
    super(page);
    this.heading = page.getByRole('heading', { name: 'Tài khoản nhân viên', exact: true });
  }

  roleBadge(name: string): Locator {
    return this.cell(name, 3).locator('span');
  }

  /** Nút gạt trạng thái (không có tên) ở cột Trạng thái. */
  toggleButton(name: string): Locator {
    return this.cell(name, 5).getByRole('button');
  }

  /** Nút Sửa (icon, không có title) - nút đầu tiên ở cột Thao tác. */
  editButton(name: string): Locator {
    return this.cell(name, 6).getByRole('button').first();
  }

  /** Nút Xóa/Vô hiệu hóa (icon, không có title) - nút thứ 2 ở cột Thao tác. */
  deleteButton(name: string): Locator {
    return this.cell(name, 6).getByRole('button').nth(1);
  }

  formModal(editing: boolean): Locator {
    return this.modal(editing ? 'Cập nhật nhân viên' : 'Thêm nhân viên mới');
  }

  /** Ô Email trong form nhân viên (input type=email có kiểm tra native của trình duyệt). */
  emailInput(editing = false): Locator {
    return this.formModal(editing).locator('input[type="email"]');
  }
}
