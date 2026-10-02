import { test } from '@fixtures';
import { AUTH_FILES } from '@config/env';
import { loadData } from '@data/loader';
import type { CatalogFixture, TaxonomyEntity } from '@data/admin-catalog.types';
import { applyCaseMeta, caseTitle } from '@engine/cases';
import { hasAdminAuth } from '@utils/storage';

/** Danh mục và Thương hiệu dùng chung cấu trúc lưới thẻ + modal -> 1 bộ test chạy cho cả 2 (data-driven). */
const fixture = loadData<CatalogFixture>('admin-catalog/fixtures.json');
const entities = loadData<TaxonomyEntity[]>('admin-catalog/taxonomy.json');
const ID = { category: 'ADC-CAT', brand: 'ADC-BRD' } as const;

for (const e of entities) {
  const id = ID[e.key];
  const api = `**/api/admin/${e.api}`;
  const items = fixture[e.fixture]!;

  test.describe(`Admin - ${e.label}`, () => {
    test.use({ storageState: AUTH_FILES.admin });
    test.skip(() => !hasAdminAuth(), 'Cần E2E_ADMIN_EMAIL/PASSWORD trong .env');

    test(`[${id}-01] Dữ liệu thật: trang ${e.label} có thẻ, ô tìm kiếm, nút thêm @smoke`, async ({ k }) => {
      await k.admin.openAdminPage(e.path, e.title);
      await k.adminCatalog.verifyApiRequested(`/admin/${e.api}`);
      await k.adminCatalog.verifyCardCountAtLeast(1);
      await k.common.verifyNoPageErrors();
    });

    test.describe('Dữ liệu mock', () => {
      test.beforeEach(async ({ k }) => {
        await k.adminCatalog.mockCatalogApi({ [e.fixture]: items });
        await k.admin.openAdminPage(e.path, e.title);
      });

      test(`[${id}-02] Thẻ hiển thị tên, slug, mô tả và nút gạt theo dữ liệu`, async ({ k }) => {
        await k.adminCatalog.verifyCards(items.map((i) => i.name));
        for (const i of items) {
          await k.adminCatalog.verifyCardDetails(i.name, i.slug, i.description ?? undefined);
          await k.adminCatalog.verifyCardActive(i.name, i.is_active);
        }
      });

      test.describe('Tìm kiếm (data-driven)', () => {
        for (const c of e.searches) {
          test(caseTitle(c), async ({ k }) => {
            applyCaseMeta(c);
            await k.admin.searchList(e.searchPlaceholder, c.text);
            await k.adminCatalog.verifyCards(c.visible, c.hidden);
            if (c.empty) await k.adminCatalog.verifyCardsEmpty(e.empty);
          });
        }
      });

      test(`[${id}-03] Thêm ${e.label.toLowerCase()} (mock POST) -> payload đúng, toast, thẻ mới`, async ({ k }) => {
        await k.common.mockWrite('POST', api, e.create.response);
        await k.admin.clickButton(e.addButton);
        await k.admin.verifyModalOpen(e.addHeading);
        await k.admin.fillForm(e.create.form);
        await k.admin.clickButton('Lưu');
        await k.common.verifyRequest('POST', `/admin/${e.api}`, e.create.payload);
        await k.common.verifyToast(e.toasts.created);
        await k.admin.verifyModalClosed(e.addHeading);
        await k.adminCatalog.verifyCards([e.create.name]);
      });

      test(`[${id}-04] Bỏ trống tên -> trình duyệt chặn, không gửi request`, async ({ k }) => {
        await k.common.mockWrite('POST', api, e.create.response);
        await k.admin.clickButton(e.addButton);
        await k.admin.clickButton('Lưu');
        await k.admin.verifyModalOpen(e.addHeading);
        await k.common.verifyNoRequest('POST', `/admin/${e.api}`);
      });

      test(`[${id}-05] "Hủy" đóng modal thêm, không gửi request`, async ({ k }) => {
        await k.common.mockWrite('POST', api, e.create.response);
        await k.admin.clickButton(e.addButton);
        await k.admin.fillForm({ [e.nameLabel]: e.create.name });
        await k.admin.clickButton('Hủy');
        await k.admin.verifyModalClosed(e.addHeading);
        await k.common.verifyNoRequest('POST', `/admin/${e.api}`);
        await k.adminCatalog.verifyCards([], [e.create.name]);
      });

      test(`[${id}-06] Lưu lỗi -> toast lỗi, modal vẫn mở giữ dữ liệu đã nhập`, async ({ k }) => {
        test.fail(true, `BUG: ${e.key === 'category' ? 'AdminCategories.jsx:57-59' : 'AdminBrands.jsx:57-59'} - catch gọi setShowForm(false) nên modal đóng, mất dữ liệu vừa nhập`);
        await k.common.mockWrite('POST', api, { success: false, message: 'Có lỗi xảy ra, vui lòng thử lại sau.' }, 500);
        await k.admin.clickButton(e.addButton);
        await k.admin.fillForm({ [e.nameLabel]: e.create.name });
        await k.admin.clickButton('Lưu');
        await k.common.verifyToast(e.toasts.saveFailed);
        await k.admin.verifyModalOpen(e.addHeading);
        await k.admin.verifyFieldValue(e.nameLabel, e.create.name);
      });

      test(`[${id}-07] Sửa: modal điền sẵn dữ liệu, lưu gửi PUT (mock) và cập nhật thẻ`, async ({ k }) => {
        const ed = e.edit;
        await k.common.mockWrite('PUT', `${api}/${ed.id}`, ed.response);
        await k.adminCatalog.clickCardEdit(ed.target);
        await k.admin.verifyModalOpen(e.editHeading);
        for (const [label, value] of Object.entries(ed.prefill)) await k.admin.verifyFieldValue(label, value);
        await k.admin.fillForm(ed.form);
        await k.admin.clickButton('Lưu');
        await k.common.verifyRequest('PUT', `/admin/${e.api}/${ed.id}`, ed.payload);
        await k.common.verifyToast(e.toasts.updated);
        await k.admin.verifyModalClosed(e.editHeading);
        await k.adminCatalog.verifyCardDetails(ed.name, ed.payload.slug as string, ed.description);
      });

      test(`[${id}-08] Xóa: modal xác nhận đúng tên; "Hủy" không gửi request`, async ({ k }) => {
        const d = e.delete;
        await k.common.mockWrite('DELETE', `${api}/${d.id}`, { success: true });
        await k.adminCatalog.clickCardDelete(d.target);
        await k.adminCatalog.verifyDeleteConfirmMessage(e.deleteMessage.replace('{name}', d.target));
        await k.admin.clickButton('Hủy');
        await k.admin.verifyModalClosed('Xác nhận xóa');
        await k.common.verifyNoRequest('DELETE', `/admin/${e.api}/`);
        await k.adminCatalog.verifyCards([d.target]);
      });

      test(`[${id}-09] Xóa thành công (mock DELETE) -> toast, thẻ biến mất`, async ({ k }) => {
        const d = e.delete;
        await k.common.mockWrite('DELETE', `${api}/${d.id}`, { success: true });
        await k.adminCatalog.clickCardDelete(d.target);
        await k.admin.clickButton('Xóa');
        await k.common.verifyRequest('DELETE', `/admin/${e.api}/${d.id}`);
        await k.common.verifyToast(e.toasts.deleted);
        await k.adminCatalog.verifyCards([], [d.target]);
      });

      test(`[${id}-10] Xóa bị server từ chối -> toast thông điệp server, thẻ còn nguyên`, async ({ k }) => {
        const d = e.delete;
        await k.common.mockWrite('DELETE', `${api}/${d.id}`, { success: false, message: d.errorMessage }, 400);
        await k.adminCatalog.clickCardDelete(d.target);
        await k.admin.clickButton('Xóa');
        await k.common.verifyToast(d.errorMessage);
        await k.admin.verifyModalClosed('Xác nhận xóa');
        await k.adminCatalog.verifyCards([d.target]);
      });

      test(`[${id}-11] Gạt tắt Hoạt động (mock PUT) -> gửi is_active=false, toast`, async ({ k }) => {
        const t = e.toggle;
        await k.common.mockWrite('PUT', `${api}/${t.id}`, { success: true });
        await k.adminCatalog.clickCardToggle(t.target);
        await k.common.verifyRequest('PUT', `/admin/${e.api}/${t.id}`, t.payload);
        await k.common.verifyToast(e.toasts.toggled);
        await k.adminCatalog.verifyCardActive(t.target, false);
      });

      test(`[${id}-12] Gạt Hoạt động lỗi -> toast lỗi, giữ nguyên trạng thái`, async ({ k }) => {
        test.fail(true, `BUG: ${e.key === 'category' ? 'AdminCategories.jsx:36-38' : 'AdminBrands.jsx:36-38'} - nhánh catch vẫn đảo trạng thái nên nút gạt đổi dù API lỗi`);
        const t = e.toggle;
        await k.common.mockWrite('PUT', `${api}/${t.id}`, { success: false }, 500);
        await k.adminCatalog.clickCardToggle(t.target);
        await k.common.verifyToast(e.toasts.toggleFailed);
        await k.adminCatalog.verifyCardActive(t.target, true);
      });

      test(`[${id}-13] ${e.label} nổi bật hiển thị nhãn "Nổi bật"`, async ({ k }) => {
        test.fail(true, `BUG: ${e.featured.knownBug}`);
        await k.adminCatalog.verifyCardFeatured(e.featured.target, true);
      });

      if (e.slugAutofill) {
        test.describe('Slug tự sinh khi gõ tên (data-driven)', () => {
          for (const c of e.slugAutofill!) {
            test(caseTitle(c), async ({ k }) => {
              applyCaseMeta(c);
              await k.admin.clickButton(e.addButton);
              await k.admin.fillForm({ [e.nameLabel]: c.name });
              await k.admin.verifyFieldValue('Slug', c.slug);
            });
          }
        });
      }
    });
  });
}
