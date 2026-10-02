import { test } from '@fixtures';
import { AUTH_FILES } from '@config/env';
import { loadData } from '@data/loader';
import type { CatalogFixture, ProductFormData } from '@data/admin-catalog.types';
import { applyCaseMeta, caseTitle } from '@engine/cases';
import { hasAdminAuth } from '@utils/storage';

const fixture = loadData<CatalogFixture>('admin-catalog/fixtures.json');
const data = loadData<ProductFormData>('admin-catalog/product-form.json');

test.describe('Admin - Form sản phẩm', () => {
  test.use({ storageState: AUTH_FILES.admin });
  test.skip(() => !hasAdminAuth(), 'Cần E2E_ADMIN_EMAIL/PASSWORD trong .env');

  test.beforeEach(async ({ k }) => {
    // Danh mục / thương hiệu / sản phẩm giả để dropdown và payload xác định được
    await k.adminCatalog.mockCatalogApi(fixture);
  });

  test.describe('Tạo sản phẩm', () => {
    test.beforeEach(async ({ k }) => {
      await k.common.mockWrite('POST', '**/api/admin/products', data.create.response);
      await k.admin.openAdminPage('/admin/products/create', 'Thêm sản phẩm mới');
      await k.adminCatalog.verifyProductFormReady('Tạo sản phẩm');
    });

    test.describe('Validate (data-driven)', () => {
      for (const c of data.validation) {
        test(caseTitle(c), async ({ k }) => {
          applyCaseMeta(c);
          if (Object.keys(c.fields).length) await k.admin.fillForm(c.fields);
          await k.adminCatalog.submitProductForm();
          await k.adminCatalog.verifyProductFormError(c.error);
          await k.common.verifyNoRequest('POST', '/admin/products');
          await k.common.verifyUrl('/admin/products/create');
        });
      }
    });

    test.describe('Slug tự sinh từ tên (data-driven)', () => {
      for (const c of data.slugs) {
        test(caseTitle(c), async ({ k }) => {
          applyCaseMeta(c);
          await k.admin.fillForm({ 'Tên sản phẩm': c.name });
          await k.admin.verifyFieldValue('Slug', c.slug);
        });
      }
    });

    test('[ADC-PF-01] Tạo sản phẩm đầy đủ thông tin (mock POST) -> payload đúng, toast, về danh sách @smoke', async ({ k }) => {
      const c = data.create;
      await k.admin.fillForm(c.fields);
      await k.admin.verifyFieldValue('Slug', c.slug);
      await k.adminCatalog.addImageUrl(c.imageUrl);
      await k.adminCatalog.verifyImageCount(1);
      await k.adminCatalog.submitProductForm();
      await k.common.verifyRequest('POST', '/admin/products', c.payload);
      await k.common.verifyToast(c.toast);
      await k.common.verifyUrl('/admin/products');
      await k.admin.verifyHeaderTitle('Sản phẩm');
    });

    test('[ADC-PF-02] Server báo lỗi -> hiện lỗi trên form + toast, ở lại trang', async ({ k }) => {
      const c = data.create;
      await k.common.mockWrite('POST', '**/api/admin/products', { success: false, message: c.error.message }, c.error.status);
      await k.admin.fillForm({ 'Tên sản phẩm': 'Áo lỗi E2E', 'Giá bán': '100000' });
      await k.adminCatalog.submitProductForm();
      await k.common.verifyRequest('POST', '/admin/products', { name: 'Áo lỗi E2E', price: 100000 });
      await k.adminCatalog.verifyProductFormError(c.error.message);
      await k.common.verifyToast(c.error.message);
      await k.common.verifyUrl('/admin/products/create');
    });

    test('[ADC-PF-03] Tạo biến thể: chọn size x màu sinh lưới SKU, xóa 1 dòng, gửi kèm payload', async ({ k }) => {
      const v = data.variants;
      await k.admin.fillForm({ 'Tên sản phẩm': 'Áo biến thể E2E', 'Giá bán': v.price, SKU: v.sku });
      await k.adminCatalog.verifyVariantToggleLabel('+ Tạo biến thể');
      await k.adminCatalog.toggleVariantBuilder();
      await k.adminCatalog.verifyVariantToggleLabel('Tắt chế độ');
      await k.adminCatalog.verifyGenerateVariantsButton(v.buttonBefore, false);
      await k.adminCatalog.selectVariantSizes(v.sizes);
      await k.adminCatalog.verifyGenerateVariantsButton('Tạo 0 biến thể', false);
      await k.adminCatalog.selectVariantColors(v.colors);
      await k.adminCatalog.verifyGenerateVariantsButton(v.buttonAfter, true);
      await k.adminCatalog.generateVariants();
      await k.adminCatalog.verifyVariantToggleLabel('+ Tạo biến thể');
      await k.adminCatalog.verifyVariantRows(v.rows);
      await k.adminCatalog.removeVariant(1);
      await k.adminCatalog.verifyVariantRows(v.rows.filter((_, i) => i !== 1));
      await k.adminCatalog.submitProductForm();
      await k.common.verifyRequest('POST', '/admin/products', {
        sku: v.sku,
        variants: v.rows
          .filter((_, i) => i !== 1)
          .map((r) => ({ sku: r.sku, price: v.price, stock: 0, is_active: true })),
      });
    });

    test('[ADC-PF-04] Ảnh từ URL: thêm, bỏ trùng, ảnh đầu là "Ảnh chính", xóa ảnh', async ({ k }) => {
      const [first, second] = data.images.urls;
      await k.adminCatalog.verifyImageCount(0);
      await k.adminCatalog.addImageUrl(first);
      await k.adminCatalog.addImageUrl(second);
      await k.adminCatalog.verifyImageCount(2);
      await k.adminCatalog.addImageUrl(first);
      await k.adminCatalog.verifyImageCount(2);
      await k.adminCatalog.removeImage(0);
      await k.adminCatalog.verifyImageCount(1);
    });

    test('[ADC-PF-05] Tải ảnh lên gửi kèm token admin', async ({ k }) => {
      test.fail(true, `BUG: ${data.upload.knownBug}`);
      await k.adminCatalog.uploadProductImage(data.upload.fileName, data.upload.response);
      await k.adminCatalog.verifyImageCount(1);
      await k.adminCatalog.verifyUploadUsedAdminToken();
    });

    test('[ADC-PF-06] "Quay lại" về danh sách sản phẩm, không gửi request', async ({ k }) => {
      await k.admin.fillForm({ 'Tên sản phẩm': 'Bỏ dở E2E' });
      await k.adminCatalog.clickBackToProducts();
      await k.common.verifyUrl('/admin/products');
      await k.common.verifyNoRequest('POST', '/admin/products');
    });
  });

  test.describe('Sửa sản phẩm', () => {
    test('[ADC-PF-07] Mở trực tiếp URL sửa: tải chi tiết, điền sẵn; lưu gửi PUT giữ nguyên mô tả/chất liệu (mock)', async ({ k }) => {
      const e = data.edit;
      await k.common.mockWrite('PUT', `**/api/admin/products/${e.id}`, { success: true });
      await k.common.goto(e.path);
      await k.adminCatalog.verifyProductFormReady('Cập nhật');
      await k.adminCatalog.verifyApiRequested(`/admin/products/${e.id}`);
      for (const [label, value] of Object.entries(e.prefill)) await k.admin.verifyFieldValue(label, value);
      await k.adminCatalog.verifyVariantCount(e.variantCount);
      await k.adminCatalog.verifyImageCount(e.imageCount);
      await k.admin.fillForm(e.change);
      await k.adminCatalog.submitProductForm();
      await k.common.verifyRequest('PUT', `/admin/products/${e.id}`, e.payload);
      await k.common.verifyToast(e.toast);
      await k.common.verifyUrl('/admin/products');
    });

    test('[ADC-PF-08] Bấm "Sửa" từ danh sách: danh mục được chọn sẵn', async ({ k }) => {
      test.fail(true, `BUG: ${data.edit.fromListBug}`);
      await k.admin.openAdminPage('/admin/products', 'Sản phẩm');
      await k.adminCatalog.clickProductAction(data.edit.product, 'Sửa');
      await k.adminCatalog.verifyProductFormReady('Cập nhật');
      await k.admin.verifyFieldValue('Danh mục', String(data.edit.prefill['Danh mục']));
    });

    test('[ADC-PF-09] Bấm "Sửa" từ danh sách rồi lưu không làm mất mô tả/chất liệu/giới tính', async ({ k }) => {
      test.fail(true, `BUG: ${data.edit.fromListBug}`);
      const e = data.edit;
      await k.common.mockWrite('PUT', `**/api/admin/products/${e.id}`, { success: true });
      await k.admin.openAdminPage('/admin/products', 'Sản phẩm');
      await k.adminCatalog.clickProductAction(e.product, 'Sửa');
      await k.adminCatalog.verifyProductFormReady('Cập nhật');
      await k.admin.fillForm(e.change);
      await k.adminCatalog.submitProductForm();
      await k.common.verifyRequest('PUT', `/admin/products/${e.id}`, e.payload);
    });
  });
});
