import { Page, expect } from '@playwright/test';
import type { ApiClient } from '@api/ApiClient';
import type { PageObjects } from '@pages/PageObjects';
import { AccountSidebar } from '@pages/account/AccountSidebar';
import { AddressesPage } from '@pages/account/AddressesPage';
import { CheckoutAccountPanel } from '@pages/account/CheckoutAccountPanel';
import { OrderDetailPage } from '@pages/account/OrderDetailPage';
import { OrderSuccessDetails } from '@pages/account/OrderSuccessDetails';
import { PasswordModal } from '@pages/account/PasswordModal';
import { escapeRegex } from '@pages/account/cssText';
import type { AddressForm, PasswordForm, ProfileForm, WishlistSort } from '@data/account.types';
import { ROUTES } from '@data/routes';
import { STORAGE_KEYS } from '@utils/storage';
import { BaseKeywords } from './BaseKeywords';

/**
 * Tài khoản khách hàng: hồ sơ, đổi mật khẩu, đơn hàng, chi tiết đơn, yêu thích, sổ địa chỉ,
 * thanh toán khi đã đăng nhập, trang đặt hàng thành công.
 * Lưu ý: mở trực tiếp /profile bị crash (bug) -> dùng openProfileFromMenu.
 */
export class AccountKeywords extends BaseKeywords {
  private readonly passwordModal: PasswordModal;
  private readonly sidebar: AccountSidebar;
  private readonly orderDetail: OrderDetailPage;
  private readonly addresses: AddressesPage;
  private readonly checkoutAccount: CheckoutAccountPanel;
  private readonly orderSuccess: OrderSuccessDetails;

  constructor(page: Page, po: PageObjects, api: ApiClient) {
    super(page, po, api);
    this.passwordModal = new PasswordModal(page);
    this.sidebar = new AccountSidebar(page);
    this.orderDetail = new OrderDetailPage(page);
    this.addresses = new AddressesPage(page);
    this.checkoutAccount = new CheckoutAccountPanel(page);
    this.orderSuccess = new OrderSuccessDetails(page);
  }

  // -------------------------------------------------------------------------
  // Điều hướng
  // -------------------------------------------------------------------------

  /** Mở menu tài khoản trên header và bấm 1 mục: "Hồ sơ cá nhân" | "Đơn hàng của tôi" | "Yêu thích". */
  async openAccountMenuLink(name: string) {
    await this.step(`Menu tài khoản -> "${name}"`, async () => {
      const link = this.po.header.root.getByRole('link', { name });
      // Nút menu là dạng bật/tắt: chỉ bấm khi menu đang đóng
      if (!(await link.isVisible())) await this.po.header.userMenuButton.click();
      await link.click();
    });
  }

  /** Bấm icon tài khoản khi chưa đăng nhập (dẫn tới /login). */
  async clickAccountIcon() {
    await this.step('Bấm icon tài khoản', async () => {
      await this.po.header.loginLink.click();
    });
  }

  /** Mở trực tiếp trang hồ sơ /profile. */
  async openProfile() {
    await this.step('Mở trang hồ sơ', async () => {
      await this.po.profile.goto();
    });
  }

  /** Kiểm tra trang hồ sơ hiển thị khối "Thông tin tài khoản". */
  async verifyProfileLoaded() {
    await this.step('Kiểm tra trang hồ sơ', async () => {
      await expect(this.po.profile.accountInfoHeading).toBeVisible();
    });
  }

  /** Mở trực tiếp trang đơn hàng /orders. */
  async openOrders() {
    await this.step('Mở trang đơn hàng', async () => {
      await this.po.orders.goto();
    });
  }

  /** Kiểm tra trang đơn hàng tải xong (có ô tìm theo mã đơn). */
  async verifyOrdersLoaded() {
    await this.step('Kiểm tra trang đơn hàng', async () => {
      await expect(this.po.orders.searchInput).toBeVisible();
    });
  }

  /** Kiểm tra trang yêu thích tải xong (có tiêu đề + danh sách hoặc thông báo rỗng). */
  async verifyWishlistLoaded() {
    await this.step('Kiểm tra trang yêu thích', async () => {
      const w = this.po.wishlist;
      await expect(w.heading).toBeVisible();
      await expect(w.searchInput.or(w.emptyState)).toBeVisible();
    });
  }

  /** Vào trang hồ sơ đúng cách người dùng làm: trang chủ -> menu tài khoản -> "Hồ sơ cá nhân" (tránh bug F5 /profile). */
  async openProfileFromMenu() {
    await this.step('Vào hồ sơ qua menu tài khoản', async () => {
      await this.page.goto(ROUTES.home);
      await this.po.header.userMenuButton.click();
      await this.po.header.root.getByRole('link', { name: 'Hồ sơ cá nhân' }).click();
      await expect(this.page).toHaveURL(ROUTES.profile);
      await expect(this.po.profile.accountInfoHeading).toBeVisible();
    });
  }

  /** Mở trực tiếp trang yêu thích /favorites và chờ tải xong. */
  async openWishlist() {
    await this.step('Mở trang yêu thích', async () => {
      await this.po.wishlist.goto();
      await expect(this.po.wishlist.heading).toBeVisible();
    });
  }

  /** Mở trực tiếp trang sổ địa chỉ /addresses và chờ tải xong. */
  async openAddresses() {
    await this.step('Mở trang địa chỉ', async () => {
      await this.page.goto(ROUTES.addresses);
      await expect(this.addresses.heading).toBeVisible();
      await expect(this.page.getByText('Đang tải địa chỉ...')).toBeHidden();
    });
  }

  /** Mở trực tiếp trang chi tiết đơn /orders/:id. */
  async openOrderDetail(id: string | number) {
    await this.step(`Mở chi tiết đơn #${id}`, async () => {
      await this.page.goto(`${ROUTES.orders}/${id}`);
      await expect(this.page.getByText('Đang tải thông tin đơn hàng...')).toBeHidden();
    });
  }

  /** Bấm 1 link trên sidebar tài khoản, vd: "Đơn hàng của tôi", "Sổ địa chỉ". */
  async clickSidebarLink(label: string) {
    await this.step(`Sidebar tài khoản -> "${label}"`, async () => {
      await this.sidebar.link(label).click();
    });
  }

  /** Đăng xuất bằng nút "Đăng xuất" trên sidebar tài khoản. */
  async logoutFromSidebar() {
    await this.step('Đăng xuất từ sidebar tài khoản', async () => {
      await this.sidebar.logoutButton.click();
    });
  }

  /** Thay thông tin user đang lưu (localStorage) bằng user cho trước - gọi TRƯỚC lần mở trang đầu tiên. */
  async seedStoredUser(user: Record<string, unknown>) {
    await this.step(`Đặt sẵn user đăng nhập "${String(user.name)}"`, async () => {
      await this.page.addInitScript(
        ({ key, value }) => {
          if (sessionStorage.getItem('__e2e_user_seeded')) return;
          localStorage.setItem(key, value);
          sessionStorage.setItem('__e2e_user_seeded', '1');
        },
        { key: STORAGE_KEYS.customerUser, value: JSON.stringify(user) },
      );
    });
  }

  // -------------------------------------------------------------------------
  // Hồ sơ cá nhân
  // -------------------------------------------------------------------------

  /** Kiểm tra các trường ở chế độ xem hồ sơ: { "Họ và tên": "...", "Giới tính": "Nữ" }. */
  async verifyProfileFields(fields: Record<string, string>) {
    await this.step(`Kiểm tra thông tin hồ sơ: ${Object.keys(fields).join(', ')}`, async () => {
      for (const [label, value] of Object.entries(fields)) {
        await expect(this.po.profile.fieldValue(label), `Trường "${label}"`).toHaveText(value);
      }
    });
  }

  /** Bấm "Chỉnh sửa" để chuyển hồ sơ sang chế độ sửa. */
  async startEditProfile() {
    await this.step('Bấm Chỉnh sửa hồ sơ', async () => {
      await this.po.profile.editButton.click();
      await expect(this.po.profile.nameInput).toBeVisible();
    });
  }

  /** Điền form sửa hồ sơ (chỉ các trường có trong dữ liệu); gender: male | female | other. */
  async fillProfileForm(form: ProfileForm) {
    await this.step(`Điền form hồ sơ: ${Object.keys(form).join(', ')}`, async () => {
      const p = this.po.profile;
      if (form.name !== undefined) await p.nameInput.fill(form.name);
      if (form.phone !== undefined) await p.phoneInput.fill(form.phone);
      if (form.birthDate !== undefined) await p.birthDateInput.fill(form.birthDate);
      if (form.gender !== undefined) await p.genderSelect.selectOption(form.gender);
    });
  }

  /** Kiểm tra giá trị đang có trong form sửa hồ sơ. */
  async verifyProfileForm(form: ProfileForm) {
    await this.step('Kiểm tra giá trị form hồ sơ', async () => {
      const p = this.po.profile;
      if (form.name !== undefined) await expect(p.nameInput).toHaveValue(form.name);
      if (form.phone !== undefined) await expect(p.phoneInput).toHaveValue(form.phone);
      if (form.birthDate !== undefined) await expect(p.birthDateInput).toHaveValue(form.birthDate);
      if (form.gender !== undefined) await expect(p.genderSelect).toHaveValue(form.gender);
    });
  }

  /** Kiểm tra ô Email trong form sửa bị khóa và hiển thị đúng email. */
  async verifyProfileEmailLocked(email: string) {
    await this.step(`Kiểm tra ô Email bị khóa (${email})`, async () => {
      await expect(this.po.profile.emailInput).toBeDisabled();
      await expect(this.po.profile.emailInput).toHaveValue(email);
    });
  }

  /** Bấm "Lưu thay đổi" trong form sửa hồ sơ. */
  async saveProfile() {
    await this.step('Bấm Lưu thay đổi hồ sơ', async () => {
      await this.po.profile.saveButton.click();
    });
  }

  /** Bấm "Hủy" để thoát chế độ sửa hồ sơ. */
  async cancelEditProfile() {
    await this.step('Bấm Hủy sửa hồ sơ', async () => {
      await this.po.profile.cancelEditButton.click();
    });
  }

  /** Kiểm tra hồ sơ đang ở chế độ sửa (true) hay chế độ xem (false). */
  async verifyProfileEditing(editing: boolean) {
    await this.step(`Kiểm tra hồ sơ ở chế độ ${editing ? 'sửa' : 'xem'}`, async () => {
      const p = this.po.profile;
      if (editing) {
        await expect(p.nameInput).toBeVisible();
        await expect(p.editButton).toBeHidden();
      } else {
        await expect(p.editButton).toBeVisible();
        await expect(p.nameInput).toBeHidden();
      }
    });
  }

  /** Bấm "Đổi mật khẩu" và chờ modal mở. */
  async openChangePassword() {
    await this.step('Mở modal Đổi mật khẩu', async () => {
      await this.po.profile.changePasswordButton.click();
      await expect(this.passwordModal.heading).toBeVisible();
    });
  }

  /** Điền 3 ô trong modal đổi mật khẩu (hiện tại, mới, xác nhận). */
  async fillChangePassword(form: PasswordForm) {
    await this.step('Điền form đổi mật khẩu', async () => {
      const m = this.passwordModal;
      await m.currentPassword.fill(form.currentPassword);
      await m.newPassword.fill(form.newPassword);
      await m.confirmPassword.fill(form.confirmPassword);
    });
  }

  /** Bấm "Xác nhận" trong modal đổi mật khẩu. */
  async submitChangePassword() {
    await this.step('Bấm Xác nhận đổi mật khẩu', async () => {
      await this.passwordModal.submitButton.click();
    });
  }

  /** Kiểm tra thông báo lỗi trong modal đổi mật khẩu. */
  async verifyChangePasswordError(message: string) {
    await this.step(`Kiểm tra lỗi đổi mật khẩu "${message}"`, async () => {
      await expect(this.passwordModal.error).toHaveText(message);
      await expect(this.passwordModal.heading).toBeVisible();
    });
  }

  /** Kiểm tra modal đổi mật khẩu đã đóng. */
  async verifyChangePasswordClosed() {
    await this.step('Kiểm tra modal Đổi mật khẩu đã đóng', async () => {
      await expect(this.passwordModal.heading).toBeHidden();
    });
  }

  /** Bấm "Hủy" ở cuối modal đổi mật khẩu. */
  async cancelChangePassword() {
    await this.step('Bấm Hủy trong modal Đổi mật khẩu', async () => {
      await this.passwordModal.cancelButton.click();
    });
  }

  /** Bấm nút chữ "Đóng" ở góc trên modal đổi mật khẩu. */
  async closeChangePassword() {
    await this.step('Bấm Đóng modal Đổi mật khẩu', async () => {
      await this.passwordModal.closeButton.click();
    });
  }

  /** Kiểm tra modal đổi mật khẩu đang mở với form trống, không có lỗi cũ. */
  async verifyChangePasswordFormEmpty() {
    await this.step('Kiểm tra form đổi mật khẩu trống', async () => {
      const m = this.passwordModal;
      await expect(m.heading).toBeVisible();
      await expect(m.currentPassword).toHaveValue('');
      await expect(m.newPassword).toHaveValue('');
      await expect(m.confirmPassword).toHaveValue('');
      await expect(m.error).toBeHidden();
    });
  }

  /** Kiểm tra dải thống kê trên trang hồ sơ: { "Tổng đơn hàng": "7", ... }. */
  async verifyProfileSummary(stats: Record<string, string>) {
    await this.step(`Kiểm tra thống kê hồ sơ: ${JSON.stringify(stats)}`, async () => {
      for (const [label, value] of Object.entries(stats)) {
        await expect(this.po.profile.summaryValue(label), `Ô "${label}"`).toHaveText(value);
      }
    });
  }

  /** Kiểm tra khối "Đơn hàng gần đây" hiển thị đúng các mã đơn theo thứ tự ([] = thông báo chưa có đơn). */
  async verifyRecentOrders(codes: string[]) {
    await this.step(`Kiểm tra đơn hàng gần đây: ${codes.join(', ') || '(trống)'}`, async () => {
      const section = this.po.profile.recentOrdersSection;
      if (!codes.length) {
        await expect(section.getByText('Bạn chưa có đơn hàng nào', { exact: true })).toBeVisible();
        return;
      }
      const rows = section.locator('div.divide-y > div');
      await expect(rows).toHaveCount(codes.length);
      for (const [i, code] of codes.entries()) await expect(rows.nth(i)).toContainText(code);
    });
  }

  /** Kiểm tra khối "Sản phẩm yêu thích gần đây" hiển thị đúng tên theo thứ tự ([] = thông báo trống). */
  async verifyRecentFavorites(names: string[]) {
    await this.step(`Kiểm tra yêu thích gần đây: ${names.join(', ') || '(trống)'}`, async () => {
      const section = this.po.profile.recentFavoritesSection;
      if (!names.length) {
        await expect(section.getByText('Bạn chưa lưu sản phẩm yêu thích nào', { exact: true })).toBeVisible();
        return;
      }
      const items = section.locator('div.grid > div');
      await expect(items).toHaveCount(names.length);
      for (const [i, name] of names.entries()) await expect(items.nth(i)).toContainText(name);
    });
  }

  /** Kiểm tra khối "Địa chỉ giao hàng mặc định" chứa các đoạn chữ. */
  async verifyDefaultAddress(texts: string[]) {
    await this.step(`Kiểm tra địa chỉ mặc định trên hồ sơ: ${texts.join(' | ')}`, async () => {
      for (const t of texts) await expect(this.po.profile.defaultAddressSection).toContainText(t);
    });
  }

  /** Bấm "Cập nhật địa chỉ" trên hồ sơ và chờ sang /addresses. */
  async clickUpdateAddress() {
    await this.step('Bấm Cập nhật địa chỉ', async () => {
      await this.po.profile.updateAddressLink.click();
      await expect(this.page).toHaveURL(ROUTES.addresses);
    });
  }

  // -------------------------------------------------------------------------
  // Đơn hàng của tôi
  // -------------------------------------------------------------------------

  /** Kiểm tra số đếm trên các ô thống kê: { "Tất cả đơn": 7, "Đã hủy": 1 }. */
  async verifyOrderStats(stats: Record<string, number>) {
    await this.step(`Kiểm tra thống kê đơn: ${JSON.stringify(stats)}`, async () => {
      for (const [label, count] of Object.entries(stats)) {
        await expect(this.po.orders.statCount(label), `Ô "${label}"`).toHaveText(count.toLocaleString('vi-VN'));
      }
    });
  }

  /** Bấm tab lọc trạng thái đơn, vd: "Chờ xác nhận". */
  async filterOrdersByStatus(tab: string) {
    await this.step(`Lọc đơn theo tab "${tab}"`, async () => {
      await this.po.orders.tab(tab).click();
      await expect(this.po.orders.tab(tab)).toHaveClass(/bg-\[#d71920\]/);
    });
  }

  /** Bấm 1 ô thống kê để lọc nhanh, vd: "Đã hủy". */
  async clickOrderStat(label: string) {
    await this.step(`Bấm ô thống kê "${label}"`, async () => {
      await this.po.orders.statButton(label).click();
    });
  }

  /** Gõ vào ô "Tìm theo mã đơn hàng...". */
  async searchOrders(query: string) {
    await this.step(`Tìm đơn hàng "${query}"`, async () => {
      await this.po.orders.searchInput.fill(query);
    });
  }

  /** Kiểm tra danh sách đơn hiển thị đúng các mã đơn theo thứ tự. */
  async verifyOrderList(codes: string[]) {
    await this.step(`Kiểm tra danh sách đơn: ${codes.join(', ') || '(trống)'}`, async () => {
      await expect(this.po.orders.orderItems).toHaveCount(codes.length);
      for (const [i, code] of codes.entries()) await expect(this.po.orders.orderItems.nth(i)).toContainText(code);
    });
  }

  /** Kiểm tra trang đơn hàng hiển thị thông báo rỗng, vd: "Bạn chưa có đơn hàng nào". */
  async verifyOrdersEmpty(message: string) {
    await this.step(`Kiểm tra không có đơn: "${message}"`, async () => {
      await expect(this.po.orders.emptyState(message)).toBeVisible();
      await expect(this.po.orders.orderItems).toHaveCount(0);
    });
  }

  /** Kiểm tra 1 đơn trong danh sách chứa các đoạn chữ (ngày, số lượng, thanh toán, tổng tiền...). */
  async verifyOrderItem(code: string, texts: string[]) {
    await this.step(`Kiểm tra đơn ${code}: ${texts.join(' | ')}`, async () => {
      for (const t of texts) await expect(this.po.orders.orderItem(code)).toContainText(t);
    });
  }

  /** Kiểm tra nhãn trạng thái của 1 đơn trong danh sách. */
  async verifyOrderStatus(code: string, label: string) {
    await this.step(`Kiểm tra đơn ${code} có trạng thái "${label}"`, async () => {
      await expect(this.po.orders.statusBadge(code)).toHaveText(label);
    });
  }

  /** Kiểm tra đơn trong danh sách có (true) / không có (false) nút "Hủy đơn". */
  async verifyOrderCancelable(code: string, cancelable: boolean) {
    await this.step(`Kiểm tra đơn ${code} ${cancelable ? 'có' : 'không có'} nút Hủy đơn`, async () => {
      await expect(this.po.orders.orderItem(code)).toBeVisible();
      await expect(this.po.orders.cancelButton(code)).toHaveCount(cancelable ? 1 : 0);
    });
  }

  /** Bấm "Hủy đơn" của 1 đơn trong danh sách (app không hỏi xác nhận). */
  async cancelOrderFromList(code: string) {
    await this.step(`Hủy đơn ${code} từ danh sách`, async () => {
      await this.po.orders.cancelButton(code).click();
    });
  }

  /** Bấm "Xem chi tiết" của 1 đơn và chờ sang trang chi tiết. */
  async openOrderFromList(code: string) {
    await this.step(`Xem chi tiết đơn ${code}`, async () => {
      await this.po.orders.detailLink(code).click();
      await expect(this.page).toHaveURL(/\/orders\/\d+$/);
      await expect(this.page.getByText('Đang tải thông tin đơn hàng...')).toBeHidden();
    });
  }

  // -------------------------------------------------------------------------
  // Chi tiết đơn hàng
  // -------------------------------------------------------------------------

  /** Kiểm tra tiêu đề trang chi tiết đơn, vd: "Chi tiết đơn hàng #ORD000107". */
  async verifyOrderDetailHeading(heading: string) {
    await this.step(`Kiểm tra tiêu đề "${heading}"`, async () => {
      await expect(this.orderDetail.heading).toHaveText(heading);
    });
  }

  /** Kiểm tra 2 ô trạng thái đơn hàng + trạng thái thanh toán ở đầu trang chi tiết. */
  async verifyOrderDetailStatus(status: string, payment: string) {
    await this.step(`Kiểm tra trạng thái "${status}", thanh toán "${payment}"`, async () => {
      await expect(this.orderDetail.statusValue).toHaveText(status);
      await expect(this.orderDetail.paymentStatusValue).toHaveText(payment);
    });
  }

  /** Kiểm tra các dòng "nhãn: giá trị" trong 1 khối, vd: ("Thông tin giao hàng", { "Người nhận": "..." }). */
  async verifyOrderDetailInfo(section: string, rows: Record<string, string>) {
    await this.step(`Kiểm tra khối "${section}"`, async () => {
      for (const [label, value] of Object.entries(rows)) {
        await expect(this.orderDetail.rowValue(section, label), `Dòng "${label}"`).toContainText(value);
      }
    });
  }

  /** Kiểm tra tiêu đề khối sản phẩm (vd: "Sản phẩm đã đặt (2)") và tên sản phẩm theo thứ tự. */
  async verifyOrderDetailItems(heading: string, names: string[]) {
    await this.step(`Kiểm tra ${heading}: ${names.join(', ')}`, async () => {
      await expect(this.orderDetail.itemsHeading).toHaveText(heading);
      await expect(this.orderDetail.itemRows).toHaveCount(names.length);
      for (const [i, name] of names.entries()) await expect(this.orderDetail.itemRows.nth(i)).toContainText(name);
    });
  }

  /** Kiểm tra 1 dòng sản phẩm trong đơn chứa các đoạn chữ (màu, size, SKU, giá, số lượng). */
  async verifyOrderDetailItem(name: string, texts: string[]) {
    await this.step(`Kiểm tra sản phẩm "${name}" trong đơn`, async () => {
      for (const t of texts) await expect(this.orderDetail.itemRow(name)).toContainText(t);
    });
  }

  /** Kiểm tra khối "Chi tiết thanh toán": { "Tạm tính": "480.000đ", "Phí vận chuyển": "Miễn phí", ... }. */
  async verifyOrderDetailTotals(rows: Record<string, string>) {
    await this.step('Kiểm tra Chi tiết thanh toán', async () => {
      for (const [label, value] of Object.entries(rows)) {
        await expect(this.orderDetail.rowValue('Chi tiết thanh toán', label), `Dòng "${label}"`).toHaveText(value);
      }
    });
  }

  /** Kiểm tra trang chi tiết có (true) / không có (false) nút "Hủy đơn hàng". */
  async verifyOrderDetailCancelable(cancelable: boolean) {
    await this.step(`Kiểm tra ${cancelable ? 'có' : 'không có'} nút Hủy đơn hàng`, async () => {
      await expect(this.orderDetail.statusValue).toBeVisible();
      await expect(this.orderDetail.cancelButton).toHaveCount(cancelable ? 1 : 0);
    });
  }

  /** Bấm "Hủy đơn hàng" và chờ hộp xác nhận hiện ra. */
  async openCancelOrderDialog() {
    await this.step('Mở hộp xác nhận hủy đơn', async () => {
      await this.orderDetail.cancelButton.click();
      await expect(this.orderDetail.cancelModal).toBeVisible();
    });
  }

  /** Nhập lý do (để trống = không nhập) rồi bấm "Xác nhận hủy". */
  async confirmCancelOrder(reason = '') {
    await this.step(`Xác nhận hủy đơn${reason ? ` - lý do "${reason}"` : ''}`, async () => {
      if (reason) await this.orderDetail.cancelReason.fill(reason);
      await this.orderDetail.confirmCancelButton.click();
    });
  }

  /** Bấm "Đóng" trên hộp xác nhận hủy đơn. */
  async closeCancelOrderDialog() {
    await this.step('Đóng hộp xác nhận hủy đơn', async () => {
      await this.orderDetail.closeCancelButton.click();
    });
  }

  /** Kiểm tra hộp xác nhận hủy đơn đang mở (true) / đã đóng (false). */
  async verifyCancelOrderDialog(open: boolean) {
    await this.step(`Kiểm tra hộp xác nhận hủy đơn ${open ? 'đang mở' : 'đã đóng'}`, async () => {
      if (open) await expect(this.orderDetail.cancelModal).toBeVisible();
      else await expect(this.orderDetail.cancelModal).toBeHidden();
    });
  }

  /** Kiểm tra trang chi tiết đơn báo lỗi (thông báo + nút "Quay lại đơn hàng"). */
  async verifyOrderDetailError(message: string) {
    await this.step(`Kiểm tra lỗi chi tiết đơn "${message}"`, async () => {
      await expect(this.orderDetail.message(message)).toBeVisible();
      await expect(this.orderDetail.backToOrdersLink).toBeVisible();
    });
  }

  /** Bấm "Quay lại đơn hàng" trên màn hình lỗi và chờ về /orders. */
  async backToOrdersFromError() {
    await this.step('Bấm Quay lại đơn hàng', async () => {
      await this.orderDetail.backToOrdersLink.click();
      await expect(this.page).toHaveURL(ROUTES.orders);
    });
  }

  /** Bấm nút "Quay lại" ở góc trên trang chi tiết đơn và chờ về /orders. */
  async goBackFromOrderDetail() {
    await this.step('Bấm Quay lại từ chi tiết đơn', async () => {
      await this.orderDetail.backLink.click();
      await expect(this.page).toHaveURL(ROUTES.orders);
    });
  }

  // -------------------------------------------------------------------------
  // Yêu thích
  // -------------------------------------------------------------------------

  /** Kiểm tra dòng "<N> sản phẩm yêu thích" dưới tiêu đề. */
  async verifyWishlistCount(count: number) {
    await this.step(`Kiểm tra có ${count} sản phẩm yêu thích`, async () => {
      await expect(this.po.wishlist.countMeta).toHaveText(`${count.toLocaleString('vi-VN')} sản phẩm yêu thích`);
    });
  }

  /** Kiểm tra danh sách thẻ sản phẩm yêu thích đúng tên + đúng thứ tự. */
  async verifyWishlistProducts(names: string[]) {
    await this.step(`Kiểm tra sản phẩm yêu thích: ${names.join(', ')}`, async () => {
      await expect(this.po.wishlist.cardNames).toHaveText(names);
    });
  }

  /** Gõ vào ô "Tìm sản phẩm yêu thích...". */
  async searchWishlist(query: string) {
    await this.step(`Tìm sản phẩm yêu thích "${query}"`, async () => {
      await this.po.wishlist.searchInput.fill(query);
    });
  }

  /** Chọn cách sắp xếp: recent | price_asc | price_desc. */
  async sortWishlist(sort: WishlistSort) {
    await this.step(`Sắp xếp yêu thích theo ${sort}`, async () => {
      await this.po.wishlist.sortSelect.selectOption(sort);
    });
  }

  /** Bấm trái tim "Bỏ yêu thích" trên thẻ sản phẩm. */
  async removeFromWishlist(name: string) {
    await this.step(`Bỏ yêu thích "${name}"`, async () => {
      await this.po.wishlist.removeButton(name).click();
    });
  }

  /** Bấm "Thêm vào giỏ hàng" trên thẻ sản phẩm yêu thích. */
  async addWishlistItemToCart(name: string) {
    await this.step(`Thêm "${name}" từ yêu thích vào giỏ`, async () => {
      await this.po.wishlist.addToCartButton(name).click();
    });
  }

  /** Kiểm tra thẻ sản phẩm yêu thích chứa các đoạn chữ (danh mục, giá, % giảm, tình trạng...). */
  async verifyWishlistItem(name: string, texts: string[]) {
    await this.step(`Kiểm tra thẻ "${name}": ${texts.join(' | ')}`, async () => {
      for (const t of texts) await expect(this.po.wishlist.card(name)).toContainText(t);
    });
  }

  /** Kiểm tra sản phẩm còn hàng (nút thêm giỏ bật) hay hết hàng (nhãn "Hết hàng", nút tắt). */
  async verifyWishlistItemAvailable(name: string, available: boolean) {
    await this.step(`Kiểm tra "${name}" ${available ? 'còn hàng' : 'hết hàng'}`, async () => {
      const w = this.po.wishlist;
      if (available) {
        await expect(w.addToCartButton(name)).toBeEnabled();
        await expect(w.outOfStockOverlay(name)).toBeHidden();
      } else {
        await expect(w.addToCartButton(name)).toBeDisabled();
        await expect(w.outOfStockOverlay(name)).toBeVisible();
      }
    });
  }

  /** Kiểm tra thông báo "Không tìm thấy sản phẩm phù hợp" khi lọc/tìm không ra. */
  async verifyWishlistNoMatch() {
    await this.step('Kiểm tra không có sản phẩm yêu thích phù hợp', async () => {
      await expect(this.po.wishlist.noMatch).toBeVisible();
      await expect(this.po.wishlist.cards).toHaveCount(0);
    });
  }

  /** Kiểm tra trang yêu thích trống ("Bạn chưa có sản phẩm yêu thích", 0 sản phẩm). */
  async verifyWishlistEmpty() {
    await this.step('Kiểm tra danh sách yêu thích trống', async () => {
      await expect(this.po.wishlist.emptyState).toBeVisible();
      await expect(this.po.wishlist.countMeta).toHaveText('0 sản phẩm yêu thích');
      await expect(this.po.wishlist.searchInput).toBeHidden();
    });
  }

  /** Mở trang danh mục và bấm nút trái tim (yêu thích) của sản phẩm đầu tiên. */
  async favoriteFromListing(path: string) {
    await this.step(`Bấm trái tim sản phẩm đầu tiên trên ${path}`, async () => {
      await this.page.goto(path);
      await this.po.wishlist.listingHeartButtons.first().click();
    });
  }

  // -------------------------------------------------------------------------
  // Sổ địa chỉ
  // -------------------------------------------------------------------------

  /** Kiểm tra trang địa chỉ trống ("Bạn chưa có địa chỉ nào"). */
  async verifyAddressesEmpty() {
    await this.step('Kiểm tra chưa có địa chỉ nào', async () => {
      await expect(this.addresses.emptyTitle).toBeVisible();
      await expect(this.addresses.subtitle).toHaveText('Quản lý địa chỉ giao hàng của bạn');
      await expect(this.addresses.cards).toHaveCount(0);
    });
  }

  /** Bấm nút "Thêm địa chỉ" trên tiêu đề và chờ form "Thêm địa chỉ mới". */
  async openAddAddressForm() {
    await this.step('Mở form Thêm địa chỉ', async () => {
      await this.addresses.addButton.click();
      await expect(this.addresses.formHeading).toHaveText('Thêm địa chỉ mới');
    });
  }

  /** Bấm "Thêm địa chỉ mới" ở màn hình trống và chờ form mở. */
  async openAddAddressFromEmptyState() {
    await this.step('Bấm Thêm địa chỉ mới (màn hình trống)', async () => {
      await this.addresses.emptyAddButton.click();
      await expect(this.addresses.formHeading).toHaveText('Thêm địa chỉ mới');
    });
  }

  /** Điền form địa chỉ (chỉ các trường có trong dữ liệu); city = tên tỉnh, vd: "Hồ Chí Minh". */
  async fillAddressForm(form: AddressForm) {
    await this.step(`Điền form địa chỉ: ${Object.keys(form).join(', ')}`, async () => {
      const a = this.addresses;
      if (form.fullName !== undefined) await a.fullName.fill(form.fullName);
      if (form.phone !== undefined) await a.phone.fill(form.phone);
      if (form.address !== undefined) await a.address.fill(form.address);
      if (form.ward !== undefined) await a.ward.fill(form.ward);
      if (form.district !== undefined) await a.district.fill(form.district);
      if (form.city !== undefined) await a.city.selectOption(form.city);
      if (form.isDefault !== undefined) await a.defaultCheckbox.setChecked(form.isDefault);
    });
  }

  /** Bấm nút lưu của form địa chỉ ("Thêm địa chỉ" / "Lưu thay đổi"). */
  async submitAddressForm() {
    await this.step('Bấm lưu form địa chỉ', async () => {
      await this.addresses.submitButton.click();
    });
  }

  /** Bấm "Hủy" để đóng form địa chỉ. */
  async cancelAddressForm() {
    await this.step('Bấm Hủy form địa chỉ', async () => {
      await this.addresses.cancelButton.click();
    });
  }

  /** Kiểm tra các thông báo lỗi dưới ô nhập của form địa chỉ. */
  async verifyAddressFormErrors(messages: string[]) {
    await this.step(`Kiểm tra lỗi form địa chỉ: ${messages.join(' | ')}`, async () => {
      for (const m of messages) await expect(this.addresses.fieldError(m)).toBeVisible();
      await expect(this.addresses.form.locator('p.text-xs')).toHaveCount(messages.length);
    });
  }

  /** Kiểm tra form địa chỉ đang mở với tiêu đề: "Thêm địa chỉ mới" | "Sửa địa chỉ". */
  async verifyAddressFormOpen(heading: string) {
    await this.step(`Kiểm tra form "${heading}" đang mở`, async () => {
      await expect(this.addresses.formHeading).toHaveText(heading);
      await expect(this.addresses.defaultCheckbox).toHaveCount(heading === 'Sửa địa chỉ' ? 0 : 1);
    });
  }

  /** Kiểm tra form địa chỉ đã đóng. */
  async verifyAddressFormClosed() {
    await this.step('Kiểm tra form địa chỉ đã đóng', async () => {
      await expect(this.addresses.form).toBeHidden();
    });
  }

  /** Kiểm tra giá trị đang có trong form địa chỉ. */
  async verifyAddressFormValues(form: AddressForm) {
    await this.step('Kiểm tra giá trị form địa chỉ', async () => {
      const a = this.addresses;
      if (form.fullName !== undefined) await expect(a.fullName).toHaveValue(form.fullName);
      if (form.phone !== undefined) await expect(a.phone).toHaveValue(form.phone);
      if (form.address !== undefined) await expect(a.address).toHaveValue(form.address);
      if (form.ward !== undefined) await expect(a.ward).toHaveValue(form.ward);
      if (form.district !== undefined) await expect(a.district).toHaveValue(form.district);
      if (form.city !== undefined) await expect(a.city).toHaveValue(form.city);
    });
  }

  /** Kiểm tra danh sách thẻ địa chỉ (tên người nhận theo thứ tự) và dòng "<N> địa chỉ đã lưu". */
  async verifyAddressList(names: string[]) {
    await this.step(`Kiểm tra danh sách địa chỉ: ${names.join(', ')}`, async () => {
      await expect(this.addresses.cards.locator('p.font-semibold')).toHaveText(names);
      await expect(this.addresses.subtitle).toHaveText(`${names.length} địa chỉ đã lưu`);
    });
  }

  /** Kiểm tra thẻ địa chỉ của người nhận chứa các đoạn chữ (SĐT, địa chỉ đầy đủ...). */
  async verifyAddressCard(name: string, texts: string[]) {
    await this.step(`Kiểm tra thẻ địa chỉ "${name}"`, async () => {
      for (const t of texts) await expect(this.addresses.card(name)).toContainText(t);
    });
  }

  /** Kiểm tra địa chỉ là mặc định (badge "Mặc định", không có nút đặt mặc định) hay không. */
  async verifyAddressDefault(name: string, isDefault: boolean) {
    await this.step(`Kiểm tra "${name}" ${isDefault ? 'là' : 'không là'} địa chỉ mặc định`, async () => {
      await expect(this.addresses.card(name)).toBeVisible();
      await expect(this.addresses.defaultBadge(name)).toHaveCount(isDefault ? 1 : 0);
      await expect(this.addresses.setDefaultButton(name)).toHaveCount(isDefault ? 0 : 1);
    });
  }

  /** Kiểm tra dòng tên trên thẻ địa chỉ chỉ gồm tên (+ "Mặc định" nếu là mặc định), không có ký tự thừa. */
  async verifyAddressNameRow(name: string, isDefault: boolean) {
    await this.step(`Kiểm tra dòng tên thẻ "${name}" không có ký tự thừa`, async () => {
      const expected = isDefault ? new RegExp(`^${escapeRegex(name)}\\s*Mặc định$`) : name;
      await expect(this.addresses.nameRow(name)).toHaveText(expected);
    });
  }

  /** Kiểm tra số badge "Mặc định" trên toàn trang địa chỉ. */
  async verifyDefaultBadgeCount(count: number) {
    await this.step(`Kiểm tra có ${count} badge Mặc định`, async () => {
      await expect(this.addresses.cards.first()).toBeVisible();
      await expect(this.addresses.defaultBadges).toHaveCount(count);
    });
  }

  /** Bấm nút "Sửa" trên thẻ địa chỉ và chờ form "Sửa địa chỉ". */
  async editAddress(name: string) {
    await this.step(`Sửa địa chỉ "${name}"`, async () => {
      await this.addresses.editButton(name).click();
      await expect(this.addresses.formHeading).toHaveText('Sửa địa chỉ');
    });
  }

  /** Bấm nút "Đặt làm mặc định" trên thẻ địa chỉ. */
  async setDefaultAddress(name: string) {
    await this.step(`Đặt "${name}" làm địa chỉ mặc định`, async () => {
      await this.addresses.setDefaultButton(name).click();
    });
  }

  /** Bấm nút "Xóa" trên thẻ địa chỉ và chờ hộp xác nhận "Xóa địa chỉ". */
  async deleteAddress(name: string) {
    await this.step(`Bấm Xóa địa chỉ "${name}"`, async () => {
      await this.addresses.deleteButton(name).click();
      await expect(this.addresses.deleteModal).toBeVisible();
    });
  }

  /** Bấm "Xóa địa chỉ" trong hộp xác nhận. */
  async confirmDeleteAddress() {
    await this.step('Xác nhận xóa địa chỉ', async () => {
      await this.addresses.confirmDeleteButton.click();
    });
  }

  /** Bấm "Hủy" trong hộp xác nhận xóa địa chỉ và chờ hộp đóng. */
  async cancelDeleteAddress() {
    await this.step('Hủy xóa địa chỉ', async () => {
      await this.addresses.cancelDeleteButton.click();
      await expect(this.addresses.deleteModal).toBeHidden();
    });
  }

  /** Kiểm tra hộp xác nhận xóa địa chỉ chứa đoạn chữ, vd: câu hỏi kèm địa chỉ. */
  async verifyDeleteAddressDialog(text: string) {
    await this.step(`Kiểm tra hộp xác nhận xóa: "${text}"`, async () => {
      await expect(this.addresses.deleteModal).toContainText(text);
    });
  }

  // -------------------------------------------------------------------------
  // Thanh toán khi đã đăng nhập + trang đặt hàng thành công
  // -------------------------------------------------------------------------

  /** Kiểm tra trang thanh toán hiển thị tài khoản đang đăng nhập (tên + email), không có nút đăng nhập. */
  async verifyCheckoutAccount(name: string, email: string) {
    await this.step(`Kiểm tra thanh toán với tài khoản "${email}"`, async () => {
      await expect(this.checkoutAccount.name).toHaveText(name);
      await expect(this.checkoutAccount.email).toHaveText(email);
      await expect(this.po.checkout.loginButton).toHaveCount(0);
    });
  }

  /** Kiểm tra form giao hàng được điền sẵn từ tài khoản: { firstName, lastName, phone }. */
  async verifyCheckoutPrefill(expected: { firstName: string; lastName: string; phone: string }) {
    await this.step(`Kiểm tra điền sẵn: Họ "${expected.firstName}", Tên "${expected.lastName}"`, async () => {
      await expect(this.po.checkout.lastName).toHaveValue(expected.lastName);
      await expect(this.po.checkout.firstName).toHaveValue(expected.firstName);
      await expect(this.po.checkout.phone).toHaveValue(expected.phone);
    });
  }

  /** Bấm "Đăng xuất" trong khối tài khoản trên trang thanh toán. */
  async logoutOnCheckout() {
    await this.step('Đăng xuất ngay trên trang thanh toán', async () => {
      await this.checkoutAccount.logoutButton.click();
    });
  }

  /** Kiểm tra trang thanh toán chuyển về chế độ khách vãng lai (vẫn ở /checkout, token bị xóa). */
  async verifyCheckoutGuestMode() {
    await this.step('Kiểm tra thanh toán ở chế độ khách vãng lai', async () => {
      await expect(this.checkoutAccount.root).toBeHidden();
      await expect(this.po.checkout.loginButton).toBeVisible();
      await expect(this.page).toHaveURL(ROUTES.checkout);
      const token = await this.page.evaluate((k) => localStorage.getItem(k), STORAGE_KEYS.customerToken);
      expect(token).toBeNull();
    });
  }

  /** Bấm "Đăng nhập / Đăng ký" trên trang thanh toán và chờ sang /login. */
  async goToLoginFromCheckout() {
    await this.step('Bấm Đăng nhập / Đăng ký trên trang thanh toán', async () => {
      await this.po.checkout.loginButton.click();
      await expect(this.page).toHaveURL(ROUTES.login);
    });
  }

  /** Kiểm tra mã đơn hiển thị cạnh "Mã đơn hàng:" trên trang đặt hàng thành công. */
  async verifyOrderSuccessNumber(orderNumber: string) {
    await this.step(`Kiểm tra mã đơn ${orderNumber}`, async () => {
      await expect(this.orderSuccess.orderNumber).toHaveText(orderNumber);
    });
  }

  /** Kiểm tra các dòng trong 1 khối trang thành công: "Thông tin thanh toán" | "Người nhận" | "Chi tiết thanh toán". */
  async verifyOrderSuccessInfo(section: string, rows: Record<string, string>) {
    await this.step(`Kiểm tra khối "${section}" trên trang thành công`, async () => {
      for (const [label, value] of Object.entries(rows)) {
        await expect(this.orderSuccess.rowValue(section, label), `Dòng "${label}"`).toHaveText(value);
      }
    });
  }

  /** Kiểm tra trang thành công có 2 link "Tiếp tục mua sắm" (về /) và link "Xem đơn hàng" (tới /orders). */
  async verifyOrderSuccessLinks() {
    await this.step('Kiểm tra các link điều hướng trên trang thành công', async () => {
      await expect(this.orderSuccess.continueLinks).toHaveCount(2);
      for (const link of await this.orderSuccess.continueLinks.all()) await expect(link).toHaveAttribute('href', '/');
      await expect(this.orderSuccess.viewOrdersLink).toHaveAttribute('href', ROUTES.orders);
    });
  }

  /** Bấm "Xem đơn hàng" trên trang thành công và chờ sang /orders. */
  async openOrdersFromSuccess() {
    await this.step('Bấm Xem đơn hàng', async () => {
      await this.orderSuccess.viewOrdersLink.click();
      await expect(this.page).toHaveURL(ROUTES.orders);
    });
  }
}
