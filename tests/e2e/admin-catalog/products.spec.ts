import { test } from '@fixtures';
import { AUTH_FILES } from '@config/env';
import { loadData } from '@data/loader';
import type { CatalogFixture, ProductsData } from '@data/admin-catalog.types';
import { applyCaseMeta, caseTitle } from '@engine/cases';
import { hasAdminAuth } from '@utils/storage';

const fixture = loadData<CatalogFixture>('admin-catalog/fixtures.json');
const data = loadData<ProductsData>('admin-catalog/products.json');

test.describe('Admin - Danh sách sản phẩm', () => {
  test.use({ storageState: AUTH_FILES.admin });
  test.skip(() => !hasAdminAuth(), 'Cần E2E_ADMIN_EMAIL/PASSWORD trong .env');

  test('[ADC-PRD-01] Dữ liệu thật: có sản phẩm, đủ cột, phân trang 10/trang @smoke', async ({ k }) => {
    await k.admin.openAdminPage('/admin/products', 'Sản phẩm');
    await k.adminCatalog.verifyApiRequested('/admin/products', { page: 1, limit: 10 });
    await k.adminCatalog.verifyColumns(data.headers);
    await k.adminCatalog.verifyProductCountAtLeast(1);
    await k.adminCatalog.verifyProductsPaginationFirstPage();
    await k.common.verifyNoPageErrors();
  });

  test('[ADC-PRD-02] "Thêm sản phẩm" mở form tạo mới', async ({ k }) => {
    await k.adminCatalog.mockCatalogApi(fixture);
    await k.admin.openAdminPage('/admin/products', 'Sản phẩm');
    await k.adminCatalog.clickAddProduct();
    await k.common.verifyUrl('/admin/products/create');
    await k.admin.verifyHeaderTitle('Thêm sản phẩm mới');
    await k.adminCatalog.verifyProductFormReady('Tạo sản phẩm');
  });

  test.describe('Dữ liệu mock', () => {
    test.beforeEach(async ({ k }) => {
      await k.adminCatalog.mockCatalogApi(fixture);
      await k.admin.openAdminPage('/admin/products', 'Sản phẩm');
    });

    test('[ADC-PRD-03] Mỗi dòng hiển thị đúng thương hiệu, SKU, danh mục, giá, tồn kho, đã bán, nổi bật, trạng thái', async ({ k }) => {
      await k.adminCatalog.verifyProductRows(data.rows);
      await k.adminCatalog.verifyProductsPagination(null);
    });

    test.describe('Tìm kiếm & lọc (data-driven)', () => {
      for (const c of data.filters) {
        test(caseTitle(c), async ({ k }) => {
          applyCaseMeta(c);
          if (c.search) await k.adminCatalog.searchProducts(c.search);
          if (c.category) await k.adminCatalog.filterProductsByCategory(c.category);
          if (c.brand) await k.adminCatalog.filterProductsByBrand(c.brand);
          await k.adminCatalog.verifyApiRequested('/admin/products', { ...c.request, page: 1 });
          for (const n of c.rows) await k.adminCatalog.verifyProductListed(n);
          for (const n of c.hidden) await k.adminCatalog.verifyProductListed(n, false);
        });
      }
    });

    test.describe('Nổi bật (mock PUT /toggle-featured, data-driven)', () => {
      for (const c of data.featured) {
        test(caseTitle(c), async ({ k }) => {
          applyCaseMeta(c);
          await k.common.mockWrite('PUT', `**/api/admin/products/${c.productId}/toggle-featured`, { success: !c.status }, c.status ?? 200);
          await k.adminCatalog.verifyProductFeaturedTitle(c.product, c.before);
          await k.adminCatalog.clickProductFeatured(c.product);
          await k.common.verifyRequest('PUT', `/admin/products/${c.productId}/toggle-featured`);
          await k.common.verifyToast(c.toast);
          await k.adminCatalog.verifyProductFeaturedTitle(c.product, c.after);
        });
      }
    });

    test.describe('Trạng thái bán (mock PUT /toggle, data-driven)', () => {
      for (const c of data.status) {
        test(caseTitle(c), async ({ k }) => {
          applyCaseMeta(c);
          await k.common.mockWrite('PUT', `**/api/admin/products/${c.productId}/toggle`, { success: !c.status }, c.status ?? 200);
          await k.adminCatalog.verifyProductActive(c.product, c.before);
          await k.adminCatalog.clickProductStatus(c.product);
          await k.common.verifyRequest('PUT', `/admin/products/${c.productId}/toggle`);
          await k.common.verifyToast(c.toast);
          await k.adminCatalog.verifyProductActive(c.product, c.after);
        });
      }
    });

    test('[ADC-PRD-04] Link "Xem" trỏ tới trang sản phẩm ngoài cửa hàng', async ({ k }) => {
      await k.adminCatalog.verifyProductViewLink(data.viewLink.product, data.viewLink.href);
    });

    test('[ADC-PRD-05] "Sửa" mở form chỉnh sửa của đúng sản phẩm', async ({ k }) => {
      await k.adminCatalog.clickProductAction(data.editLink.product, 'Sửa');
      await k.common.verifyUrl(data.editLink.path);
      await k.adminCatalog.verifyProductFormReady('Cập nhật');
      await k.admin.verifyFieldValue('Tên sản phẩm', data.editLink.product);
    });

    test.describe('Xóa sản phẩm (mock DELETE)', () => {
      test('[ADC-PRD-06] Modal "Xóa sản phẩm?" + "Hủy" không gửi request', async ({ k }) => {
        await k.common.mockWrite('DELETE', '**/api/admin/products/*', { success: true });
        await k.adminCatalog.clickProductAction('Mũ lưỡi trai E2E', 'Xóa');
        await k.adminCatalog.verifyDeleteProductModal(data.deleteModal.heading, data.deleteModal.message);
        await k.admin.clickButton('Hủy');
        await k.admin.verifyModalClosed(data.deleteModal.heading);
        await k.common.verifyNoRequest('DELETE', '/admin/products/');
        await k.adminCatalog.verifyProductListed('Mũ lưỡi trai E2E');
      });

      for (const c of data.delete) {
        test(caseTitle(c), async ({ k }) => {
          applyCaseMeta(c);
          await k.common.mockWrite('DELETE', `**/api/admin/products/${c.productId}`, { success: c.status === 200 }, c.status);
          await k.adminCatalog.clickProductAction(c.product, 'Xóa');
          await k.admin.clickButton('Xóa');
          await k.common.verifyRequest('DELETE', `/admin/products/${c.productId}`);
          await k.common.verifyToast(c.toast);
          await k.admin.verifyModalClosed(data.deleteModal.heading);
          await k.adminCatalog.verifyProductListed(c.product, !c.removed);
        });
      }
    });

    test.describe('Chọn nhiều', () => {
      test('[ADC-PRD-07] Chọn từng dòng / chọn tất cả hiển thị số sản phẩm được chọn', async ({ k }) => {
        await k.adminCatalog.verifyBulkSelection(null);
        await k.adminCatalog.selectProducts(data.bulk.select);
        await k.adminCatalog.verifyBulkSelection(data.bulk.text);
        await k.adminCatalog.selectAllProducts();
        await k.adminCatalog.verifyBulkSelection(data.bulk.allText);
      });

      test('[ADC-PRD-08] "Xóa đã chọn" xóa các sản phẩm đã chọn', async ({ k }) => {
        test.fail(true, 'BUG: AdminProducts.jsx:170 nút "Xóa đã chọn" không có onClick -> bấm không làm gì');
        await k.common.mockWrite('DELETE', '**/api/admin/products/*', { success: true });
        await k.adminCatalog.selectProducts(data.bulk.select);
        await k.adminCatalog.clickBulkDelete();
        await k.common.verifyRequest('DELETE', '/admin/products/');
      });
    });
  });

  test('[ADC-PRD-09] Phân trang: sang trang 2 gọi API page=2', async ({ k }) => {
    await k.adminCatalog.mockCatalogApi({ ...fixture, productsTotal: data.pagination.total });
    await k.admin.openAdminPage('/admin/products', 'Sản phẩm');
    await k.adminCatalog.verifyProductsPagination(data.pagination.first);
    await k.adminCatalog.goToProductsPage(2);
    await k.adminCatalog.verifyApiRequested('/admin/products', { page: 2, limit: 10 });
    await k.adminCatalog.verifyProductsPagination(data.pagination.second);
  });
});
