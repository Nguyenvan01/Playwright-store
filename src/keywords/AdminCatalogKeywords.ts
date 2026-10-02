import { Page, expect } from '@playwright/test';
import type { ApiClient } from '@api/ApiClient';
import type { PageObjects } from '@pages/PageObjects';
import { AdminRequestLog, fulfillGet, includesCI, queryOf } from '@pages/admin/sales/AdminApiMock';
import { ProductsListPage } from '@pages/admin/catalog/ProductsListPage';
import { ProductFormPage } from '@pages/admin/catalog/ProductFormPage';
import { TaxonomyPage } from '@pages/admin/catalog/TaxonomyPage';
import type { CatalogFixture, ProductRowExpect, VariantRowExpect } from '@data/admin-catalog.types';
import { STORAGE_KEYS } from '@utils/storage';
import { BaseKeywords } from './BaseKeywords';

const PRODUCTS_PAGE_SIZE = 10;
/** Ảnh PNG 1x1 dùng cho test tải ảnh lên (không cần file trên đĩa). */
const PNG_1X1 = Buffer.from(
  'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+ip1sAAAAASUVORK5CYII=',
  'base64',
);

/** Quản trị danh mục hàng: sản phẩm, form sản phẩm, danh mục, thương hiệu. */
export class AdminCatalogKeywords extends BaseKeywords {
  private readonly list: ProductsListPage;
  private readonly form: ProductFormPage;
  private readonly taxonomy: TaxonomyPage;
  private readonly requests: AdminRequestLog;
  private uploadAuthorization: string | null | undefined;

  constructor(page: Page, po: PageObjects, api: ApiClient) {
    super(page, po, api);
    this.list = new ProductsListPage(page);
    this.form = new ProductFormPage(page);
    this.taxonomy = new TaxonomyPage(page);
    this.requests = new AdminRequestLog(page);
  }

  // ===========================================================================
  // Mock dữ liệu đọc (GET) - KHÔNG chặn request ghi
  // ===========================================================================

  /** Mock GET /admin/products (lọc search/category/brand), /admin/products/:id, /admin/categories, /admin/brands. */
  async mockCatalogApi(fixture: CatalogFixture) {
    const parts = Object.keys(fixture).join(', ');
    await this.step(`Mock API danh mục hàng (${parts})`, async () => {
      if (fixture.categories) {
        const categories = fixture.categories;
        await this.page.route(/\/api\/admin\/categories(?:\?.*)?$/, (route) => fulfillGet(route, () => ({ categories })));
      }
      if (fixture.brands) {
        const brands = fixture.brands;
        await this.page.route(/\/api\/admin\/brands(?:\?.*)?$/, (route) => fulfillGet(route, () => ({ brands })));
      }
      if (fixture.products) {
        const products = fixture.products;
        await this.page.route(/\/api\/admin\/products(?:\/(\d+))?(?:\?.*)?$/, (route) => {
          const id = new URL(route.request().url()).pathname.match(/products\/(\d+)$/)?.[1];
          if (id) {
            const p = products.find((x) => String(x.id) === id);
            if (!p) return fulfillGet(route, () => ({ success: false, message: 'Không tìm thấy' }), 404);
            return fulfillGet(route, () => ({ product: { ...p, ...(fixture.productDetails?.[id] ?? {}) } }));
          }
          const q = queryOf(route);
          const search = q.get('search') ?? '';
          const filtered = products.filter(
            (p) =>
              (!search || includesCI(p.name, search) || includesCI(p.sku, search)) &&
              (!q.get('category') || String(p.category_id) === q.get('category')) &&
              (!q.get('brand') || String(p.brand_id) === q.get('brand')),
          );
          const total = fixture.productsTotal ?? filtered.length;
          return fulfillGet(route, () => ({
            products: filtered,
            total,
            totalPages: Math.ceil(total / PRODUCTS_PAGE_SIZE),
            page: Number(q.get('page') ?? 1),
          }));
        });
      }
    });
  }

  /** Kiểm tra trình duyệt đã gọi GET tới đường dẫn (vd: "/admin/products") với đủ tham số query. */
  async verifyApiRequested(path: string, params: Record<string, string | number> = {}) {
    await this.step(`Kiểm tra đã gọi GET ${path} ${JSON.stringify(params)}`, async () => {
      await expect
        .poll(() => this.requests.has(path, params), {
          message: `Không thấy GET ${path} với ${JSON.stringify(params)}. Đã gọi: ${this.requests.describe()}`,
        })
        .toBe(true);
    });
  }

  /** Kiểm tra tiêu đề cột bảng theo nội dung gốc (bỏ qua CSS uppercase), đúng thứ tự. */
  async verifyColumns(headers: string[]) {
    await this.step(`Kiểm tra cột bảng: ${headers.join(' | ')}`, async () => {
      const ths = this.page.locator('main table').first().locator('thead th');
      await expect(ths.first()).toBeVisible();
      const texts = (await ths.allTextContents()).map((t) => t.trim()).filter(Boolean);
      expect(texts).toEqual(headers);
    });
  }

  // ===========================================================================
  // Danh sách sản phẩm
  // ===========================================================================

  /** Kiểm tra bảng sản phẩm có ít nhất `min` dòng dữ liệu. */
  async verifyProductCountAtLeast(min: number) {
    await this.step(`Kiểm tra có >= ${min} sản phẩm`, async () => {
      await expect(this.list.dataRows.first()).toBeVisible();
      expect(await this.list.dataRows.count()).toBeGreaterThanOrEqual(min);
    });
  }

  /** Kiểm tra từng dòng sản phẩm: thương hiệu, SKU, danh mục, giá, tồn kho (đỏ khi <= 5), đã bán, nổi bật, trạng thái. */
  async verifyProductRows(rows: ProductRowExpect[]) {
    await this.step(`Kiểm tra ${rows.length} dòng sản phẩm`, async () => {
      await expect(this.list.dataRows).toHaveCount(rows.length);
      for (const r of rows) {
        await expect(this.list.cell(r.name, 1), r.name).toContainText(r.brand);
        await expect(this.list.cell(r.name, 2), r.name).toHaveText(r.sku);
        await expect(this.list.cell(r.name, 3), r.name).toHaveText(r.category);
        await expect(this.list.cell(r.name, 4), r.name).toHaveText(r.price);
        await expect(this.list.cell(r.name, 5), r.name).toHaveText(r.stock);
        await expect(this.list.cell(r.name, 5).locator('span'), r.name).toHaveClass(r.lowStock ? /text-red-600/ : /text-gray-700/);
        await expect(this.list.cell(r.name, 6), r.name).toHaveText(r.sold);
        await expect(this.list.featuredButton(r.name), r.name).toHaveAttribute(
          'title',
          r.featured ? 'Bỏ nổi bật' : 'Đánh dấu nổi bật',
        );
        await expect(this.list.statusButton(r.name), r.name).toHaveClass(r.active ? /text-green-500/ : /text-gray-300/);
      }
    });
  }

  /** Kiểm tra có/không có dòng sản phẩm theo tên chính xác. */
  async verifyProductListed(name: string, visible = true) {
    await this.step(`Kiểm tra ${visible ? 'có' : 'không có'} sản phẩm "${name}"`, async () => {
      await (visible ? expect(this.list.row(name)).toBeVisible() : expect(this.list.rows(name)).toHaveCount(0));
    });
  }

  /** Gõ từ khóa vào ô tìm sản phẩm. */
  async searchProducts(text: string) {
    await this.step(`Tìm sản phẩm "${text}"`, async () => {
      await this.list.searchInput.fill(text);
    });
  }

  /** Chọn lọc danh mục theo tên hiển thị. */
  async filterProductsByCategory(label: string) {
    await this.step(`Lọc danh mục "${label}"`, async () => {
      await this.list.categorySelect.selectOption({ label });
    });
  }

  /** Chọn lọc thương hiệu theo tên hiển thị. */
  async filterProductsByBrand(label: string) {
    await this.step(`Lọc thương hiệu "${label}"`, async () => {
      await this.list.brandSelect.selectOption({ label });
    });
  }

  /** Bấm nút ngôi sao (nổi bật) trên dòng sản phẩm. */
  async clickProductFeatured(name: string) {
    await this.step(`Bấm ngôi sao nổi bật của "${name}"`, async () => {
      await this.list.featuredButton(name).click();
    });
  }

  /** Kiểm tra title nút ngôi sao: "Đánh dấu nổi bật" (chưa nổi bật) hoặc "Bỏ nổi bật". */
  async verifyProductFeaturedTitle(name: string, title: string) {
    await this.step(`Kiểm tra ngôi sao của "${name}" = "${title}"`, async () => {
      await expect(this.list.featuredButton(name)).toHaveAttribute('title', title);
    });
  }

  /** Bấm nút gạt trạng thái bán trên dòng sản phẩm. */
  async clickProductStatus(name: string) {
    await this.step(`Bấm gạt trạng thái của "${name}"`, async () => {
      await this.list.statusButton(name).click();
    });
  }

  /** Kiểm tra nút gạt trạng thái bán đang bật (xanh) hay tắt (xám). */
  async verifyProductActive(name: string, active: boolean) {
    await this.step(`Kiểm tra "${name}" ${active ? 'đang bán' : 'ngừng bán'}`, async () => {
      await expect(this.list.statusButton(name)).toHaveClass(active ? /text-green-500/ : /text-gray-300/);
    });
  }

  /** Bấm nút hành động "Xem" / "Sửa" / "Xóa" trên dòng sản phẩm. */
  async clickProductAction(name: string, title: 'Xem' | 'Sửa' | 'Xóa') {
    await this.step(`Sản phẩm "${name}" -> "${title}"`, async () => {
      await this.list.action(name, title).click();
    });
  }

  /** Kiểm tra link "Xem" của sản phẩm trỏ tới trang chi tiết ngoài cửa hàng. */
  async verifyProductViewLink(name: string, href: string) {
    await this.step(`Kiểm tra link "Xem" của "${name}" = ${href}`, async () => {
      await expect(this.list.action(name, 'Xem')).toHaveAttribute('href', href);
    });
  }

  /** Kiểm tra modal xóa sản phẩm đang mở với tiêu đề + nội dung cảnh báo. */
  async verifyDeleteProductModal(heading: string, message: string) {
    await this.step(`Kiểm tra modal "${heading}"`, async () => {
      await expect(this.list.deleteModal).toBeVisible();
      await expect(this.list.deleteModal.getByText(message, { exact: true })).toBeVisible();
    });
  }

  /** Tích chọn các dòng sản phẩm theo tên. */
  async selectProducts(names: string[]) {
    await this.step(`Chọn sản phẩm: ${names.join(', ')}`, async () => {
      for (const n of names) await this.list.rowCheckbox(n).check();
    });
  }

  /** Tích ô chọn tất cả trên đầu bảng sản phẩm. */
  async selectAllProducts() {
    await this.step('Chọn tất cả sản phẩm', async () => {
      await this.list.headerCheckbox.check();
    });
  }

  /** Kiểm tra thanh thao tác hàng loạt "{n} sản phẩm được chọn" (null = ẩn). */
  async verifyBulkSelection(text: string | null) {
    await this.step(`Kiểm tra thanh chọn hàng loạt = ${text ?? '(ẩn)'}`, async () => {
      await (text === null ? expect(this.list.bulkBarText).toHaveCount(0) : expect(this.list.bulkBarText).toHaveText(text));
      if (text !== null) await expect(this.list.bulkDeleteButton).toBeVisible();
    });
  }

  /** Bấm "Xóa đã chọn" trên thanh thao tác hàng loạt. */
  async clickBulkDelete() {
    await this.step('Bấm "Xóa đã chọn"', async () => {
      await this.list.bulkDeleteButton.click();
    });
  }

  /** Kiểm tra dòng phân trang sản phẩm, vd: "Trang 1 trên 3" (null = không có phân trang). */
  async verifyProductsPagination(text: string | null) {
    await this.step(`Kiểm tra phân trang sản phẩm = ${text ?? '(không có)'}`, async () => {
      await (text === null ? expect(this.list.paginationText).toHaveCount(0) : expect(this.list.paginationText).toHaveText(text));
    });
  }

  /** Kiểm tra dòng phân trang sản phẩm khớp mẫu "Trang 1 trên N". */
  async verifyProductsPaginationFirstPage() {
    await this.step('Kiểm tra phân trang "Trang 1 trên N"', async () => {
      await expect(this.list.paginationText).toHaveText(/^Trang 1 trên \d+$/);
    });
  }

  /** Bấm số trang trên phân trang sản phẩm. */
  async goToProductsPage(n: number) {
    await this.step(`Bấm trang sản phẩm ${n}`, async () => {
      await this.list.pageButton(n).click();
    });
  }

  /** Bấm "Thêm sản phẩm" trên trang danh sách. */
  async clickAddProduct() {
    await this.step('Bấm "Thêm sản phẩm"', async () => {
      await this.list.addLink.click();
    });
  }

  // ===========================================================================
  // Form sản phẩm
  // ===========================================================================

  /** Chờ form sản phẩm tải xong (hết "Đang tải dữ liệu...") và kiểm tra nhãn nút lưu. */
  async verifyProductFormReady(submitLabel: string) {
    await this.step(`Kiểm tra form sản phẩm sẵn sàng (nút "${submitLabel}")`, async () => {
      await expect(this.form.loadingText).toHaveCount(0);
      await expect(this.form.submitButton).toHaveText(submitLabel);
    });
  }

  /** Bấm nút lưu form sản phẩm ("Tạo sản phẩm" / "Cập nhật"). */
  async submitProductForm() {
    await this.step('Bấm lưu form sản phẩm', async () => {
      await this.form.submitButton.click();
    });
  }

  /** Kiểm tra hộp lỗi đỏ trên form sản phẩm. */
  async verifyProductFormError(text: string) {
    await this.step(`Kiểm tra lỗi form sản phẩm "${text}"`, async () => {
      await expect(this.form.errorBox).toHaveText(text);
    });
  }

  /** Bấm "Quay lại" trên form sản phẩm. */
  async clickBackToProducts() {
    await this.step('Bấm "Quay lại"', async () => {
      await this.form.backButton.click();
    });
  }

  /** Bấm "+ Tạo biến thể" / "Tắt chế độ" trong khối Biến thể. */
  async toggleVariantBuilder() {
    await this.step('Bật/tắt chế độ tạo biến thể', async () => {
      await this.form.variantToggle.click();
    });
  }

  /** Kiểm tra nhãn nút bật/tắt chế độ tạo biến thể. */
  async verifyVariantToggleLabel(label: string) {
    await this.step(`Kiểm tra nút biến thể = "${label}"`, async () => {
      await expect(this.form.variantToggle).toHaveText(label);
    });
  }

  /** Chọn các size trong chế độ tạo biến thể (vd: ["S", "M"]). */
  async selectVariantSizes(sizes: string[]) {
    await this.step(`Chọn size: ${sizes.join(', ')}`, async () => {
      for (const s of sizes) {
        await this.form.sizeButton(s).click();
        await expect(this.form.sizeButton(s)).toHaveClass(/bg-\[#d71920\]/);
      }
    });
  }

  /** Chọn các màu trong chế độ tạo biến thể (vd: ["Đen", "Trắng"]). */
  async selectVariantColors(colors: string[]) {
    await this.step(`Chọn màu: ${colors.join(', ')}`, async () => {
      for (const c of colors) {
        await this.form.colorButton(c).click();
        await expect(this.form.colorButton(c)).toHaveClass(/bg-\[#d71920\]/);
      }
    });
  }

  /** Kiểm tra nút "Tạo {n} biến thể" (nhãn + bật/tắt). */
  async verifyGenerateVariantsButton(label: string, enabled: boolean) {
    await this.step(`Kiểm tra nút "${label}" ${enabled ? 'bật' : 'bị khóa'}`, async () => {
      await expect(this.form.generateButton).toHaveText(label);
      await (enabled ? expect(this.form.generateButton).toBeEnabled() : expect(this.form.generateButton).toBeDisabled());
    });
  }

  /** Bấm "Tạo {n} biến thể". */
  async generateVariants() {
    await this.step('Bấm tạo biến thể', async () => {
      await this.form.generateButton.click();
    });
  }

  /** Kiểm tra lưới biến thể: size, màu, SKU từng dòng (đúng thứ tự). */
  async verifyVariantRows(rows: VariantRowExpect[]) {
    await this.step(`Kiểm tra ${rows.length} biến thể`, async () => {
      await expect(this.form.variantRows).toHaveCount(rows.length);
      for (const [i, r] of rows.entries()) {
        await expect(this.form.variantCell(i, 'size')).toHaveText(r.size);
        await expect(this.form.variantCell(i, 'color')).toHaveText(r.color);
        await expect(this.form.variantSku(i)).toHaveValue(r.sku);
      }
    });
  }

  /** Kiểm tra số dòng biến thể. */
  async verifyVariantCount(count: number) {
    await this.step(`Kiểm tra có ${count} biến thể`, async () => {
      await expect(this.form.variantRows).toHaveCount(count);
    });
  }

  /** Xóa dòng biến thể thứ `index` (bắt đầu từ 0). */
  async removeVariant(index: number) {
    await this.step(`Xóa biến thể #${index + 1}`, async () => {
      await this.form.variantRemove(index).click();
    });
  }

  /** Dán URL ảnh vào ô "Dán URL ảnh..." và nhấn Enter. */
  async addImageUrl(url: string) {
    await this.step(`Thêm ảnh từ URL ${url}`, async () => {
      await this.form.imageUrlInput.fill(url);
      await this.form.imageUrlInput.press('Enter');
    });
  }

  /** Kiểm tra số ảnh trong khối Hình ảnh và nhãn "Ảnh chính" (ảnh đầu tiên). */
  async verifyImageCount(count: number) {
    await this.step(`Kiểm tra có ${count} ảnh`, async () => {
      await expect(this.form.imageTiles).toHaveCount(count);
      await expect(this.form.mainImageBadge).toHaveCount(count > 0 ? 1 : 0);
    });
  }

  /** Rê chuột vào ảnh thứ `index` và bấm nút X để xóa. */
  async removeImage(index: number) {
    await this.step(`Xóa ảnh #${index + 1}`, async () => {
      await this.form.imageTiles.nth(index).hover();
      await this.form.imageRemove(index).click();
    });
  }

  /** Mock POST /api/admin/upload (ghi lại header Authorization) rồi chọn 1 ảnh PNG để tải lên. */
  async uploadProductImage(fileName: string, response: unknown) {
    await this.step(`Tải ảnh "${fileName}" lên (mock upload)`, async () => {
      this.uploadAuthorization = undefined;
      await this.page.route('**/api/admin/upload', async (route) => {
        if (route.request().method() !== 'POST') return route.fallback();
        this.uploadAuthorization = (await route.request().allHeaders())['authorization'] ?? null;
        await route.fulfill({ status: 200, json: response });
      });
      await this.form.fileInput.setInputFiles({ name: fileName, mimeType: 'image/png', buffer: PNG_1X1 });
    });
  }

  /** Kiểm tra request tải ảnh gửi đúng token admin (Bearer + admin_token trong localStorage). */
  async verifyUploadUsedAdminToken() {
    await this.step('Kiểm tra upload gửi token admin', async () => {
      await expect.poll(() => this.uploadAuthorization, { message: 'Chưa thấy request upload' }).not.toBeUndefined();
      const token = await this.page.evaluate((k) => localStorage.getItem(k), STORAGE_KEYS.adminToken);
      expect(token, 'Không có admin_token trong localStorage').toBeTruthy();
      expect(this.uploadAuthorization === `Bearer ${token}`, 'Header Authorization của upload không phải token admin').toBe(true);
    });
  }

  // ===========================================================================
  // Danh mục / Thương hiệu (lưới thẻ)
  // ===========================================================================

  /** Kiểm tra có ít nhất `min` thẻ (danh mục / thương hiệu). */
  async verifyCardCountAtLeast(min: number) {
    await this.step(`Kiểm tra có >= ${min} thẻ`, async () => {
      await expect(this.taxonomy.cardNames.first()).toBeVisible();
      expect(await this.taxonomy.cardNames.count()).toBeGreaterThanOrEqual(min);
    });
  }

  /** Kiểm tra các thẻ hiển thị (`visible`) và không hiển thị (`hidden`) theo tên. */
  async verifyCards(visible: string[], hidden: string[] = []) {
    await this.step(`Kiểm tra thẻ hiện: ${visible.join(', ') || '-'} | ẩn: ${hidden.join(', ') || '-'}`, async () => {
      for (const n of visible) await expect(this.taxonomy.card(n), n).toBeVisible();
      for (const n of hidden) await expect(this.taxonomy.card(n), n).toHaveCount(0);
    });
  }

  /** Kiểm tra lưới thẻ trống với thông báo, vd: "Không tìm thấy danh mục". */
  async verifyCardsEmpty(text: string) {
    await this.step(`Kiểm tra "${text}"`, async () => {
      await expect(this.page.getByText(text, { exact: true })).toBeVisible();
      await expect(this.taxonomy.cards).toHaveCount(0);
    });
  }

  /** Rê chuột vào thẻ rồi bấm icon Sửa (icon ẩn tới khi hover, không có tên). */
  async clickCardEdit(name: string) {
    await this.step(`Thẻ "${name}" -> Sửa`, async () => {
      await this.taxonomy.card(name).hover();
      await this.taxonomy.editButton(name).click();
    });
  }

  /** Rê chuột vào thẻ rồi bấm icon Xóa (icon ẩn tới khi hover, không có tên). */
  async clickCardDelete(name: string) {
    await this.step(`Thẻ "${name}" -> Xóa`, async () => {
      await this.taxonomy.card(name).hover();
      await this.taxonomy.deleteButton(name).click();
    });
  }

  /** Bấm nút gạt Hoạt động trên thẻ. */
  async clickCardToggle(name: string) {
    await this.step(`Thẻ "${name}" -> gạt Hoạt động`, async () => {
      await this.taxonomy.toggleButton(name).click();
    });
  }

  /** Kiểm tra nút gạt Hoạt động trên thẻ đang bật (xanh) hay tắt (xám). */
  async verifyCardActive(name: string, active: boolean) {
    await this.step(`Kiểm tra thẻ "${name}" ${active ? 'đang hoạt động' : 'tắt'}`, async () => {
      await expect(this.taxonomy.toggleButton(name)).toHaveClass(active ? /text-green-500/ : /text-gray-300/);
    });
  }

  /** Kiểm tra thẻ có/không có nhãn "Nổi bật". */
  async verifyCardFeatured(name: string, featured: boolean) {
    await this.step(`Kiểm tra thẻ "${name}" ${featured ? 'có' : 'không có'} nhãn "Nổi bật"`, async () => {
      await expect(this.taxonomy.card(name)).toBeVisible();
      await (featured
        ? expect(this.taxonomy.featuredBadge(name)).toBeVisible()
        : expect(this.taxonomy.featuredBadge(name)).toHaveCount(0));
    });
  }

  /** Kiểm tra slug (/{slug}) và mô tả hiển thị trên thẻ. */
  async verifyCardDetails(name: string, slug: string, description?: string) {
    await this.step(`Kiểm tra thẻ "${name}" có slug /${slug}`, async () => {
      await expect(this.taxonomy.slug(name)).toHaveText(`/${slug}`);
      if (description) await expect(this.taxonomy.card(name)).toContainText(description);
    });
  }

  /** Kiểm tra nội dung modal "Xác nhận xóa". */
  async verifyDeleteConfirmMessage(message: string) {
    await this.step(`Kiểm tra modal xác nhận xóa: "${message}"`, async () => {
      await expect(this.taxonomy.deleteModal).toBeVisible();
      await expect(this.taxonomy.deleteMessage).toHaveText(message);
    });
  }
}
