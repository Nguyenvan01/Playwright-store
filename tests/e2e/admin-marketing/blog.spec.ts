import { test } from '@fixtures';
import { AUTH_FILES } from '@config/env';
import { loadData } from '@data/loader';
import type { BlogData } from '@data/admin-marketing.types';
import { applyCaseMeta, caseTitle } from '@engine/cases';
import { hasAdminAuth } from '@utils/storage';

const d = loadData<BlogData>('admin-marketing/blog.json');
const SEARCH = 'Tìm theo tiêu đề, slug, mô tả...';
const LIST_API = '**/api/admin/blogs';
const ITEM_API = '**/api/admin/blogs/*';
const CREATE = 'Thêm bài viết';
const EDIT = 'Sửa bài viết';
/** Ảnh PNG 1x1 dạng data URL (không cần mạng). */
const PIXEL = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==';

test.describe('Quản trị - Bài viết', () => {
  test.use({ storageState: AUTH_FILES.admin });
  test.skip(() => !hasAdminAuth(), 'Cần E2E_ADMIN_EMAIL/PASSWORD trong .env');

  test('[ADM-BLG-01] Dữ liệu thật: đủ cột và có ít nhất 1 bài viết @smoke', async ({ k }) => {
    await k.adminMarketing.openBlog();
    await k.adminMarketing.verifyColumns(d.headers);
    await k.adminMarketing.verifyRowsAtLeast(1);
    await k.common.verifyNoPageErrors();
  });

  test('[ADM-BLG-02] Chưa có bài viết -> trạng thái rỗng', async ({ k }) => {
    await k.adminMarketing.mockBlogList([]);
    await k.adminMarketing.openBlog();
    await k.common.verifyTextVisible('Chưa có bài viết nào');
    await k.common.verifyTextVisible('Nhấn Thêm bài viết để tạo nội dung mới.');
  });

  test.describe('Hiển thị dòng (data-driven)', () => {
    for (const c of d.rows) {
      test(caseTitle(c), async ({ k }) => {
        applyCaseMeta(c);
        await k.adminMarketing.mockBlogList(d.list);
        await k.adminMarketing.openBlog();
        await k.adminMarketing.verifyRowCount(d.list.length);
        await k.adminMarketing.verifyRowCells(c.rowText, c.expected);
        await k.adminMarketing.verifyRowActions(c.rowText, c.actions);
      });
    }
  });

  test.describe('Tìm kiếm (data-driven)', () => {
    for (const c of d.search) {
      test(caseTitle(c), async ({ k }) => {
        applyCaseMeta(c);
        await k.adminMarketing.mockBlogList(d.list);
        await k.adminMarketing.openBlog();
        await k.admin.searchList(SEARCH, c.keyword);
        await k.adminMarketing.verifyVisibleRows(c.visible, c.hidden);
        if (c.emptyText) await k.common.verifyTextVisible(c.emptyText);
      });
    }
  });

  test.describe('Form thêm - kiểm tra dữ liệu (data-driven)', () => {
    for (const c of d.validation) {
      test(caseTitle(c), async ({ k }) => {
        applyCaseMeta(c);
        await k.common.mockWrite('POST', LIST_API, { success: true });
        await k.adminMarketing.mockBlogList(d.list);
        await k.adminMarketing.openBlog();
        await k.adminMarketing.openCreateBlog();
        await k.admin.fillForm(c.form);
        await k.adminMarketing.clickModalButton(CREATE, 'Lưu bài viết');
        await k.common.verifyToast(c.toast);
        await k.admin.verifyModalOpen(CREATE);
        await k.common.verifyNoRequest('POST', '/admin/blogs');
      });
    }
  });

  test.describe('Slug (data-driven)', () => {
    for (const c of d.slugCases) {
      test(caseTitle(c), async ({ k }) => {
        applyCaseMeta(c);
        await k.adminMarketing.mockBlogList(d.list);
        await k.adminMarketing.openBlog();
        await k.adminMarketing.openCreateBlog();
        for (const step of c.steps) await k.admin.fillForm(step);
        await k.admin.verifyFieldValue('Slug', c.expectedSlug);
      });
    }
  });

  test('[ADM-BLG-03] Thêm bài viết thành công gửi đúng dữ liệu, bài mới lên đầu (mock POST) @smoke', async ({ k }) => {
    const created = { id: 99, ...d.create.expectedPayload, created_at: '2026-10-01T03:00:00.000Z' };
    await k.common.mockWrite('POST', LIST_API, { success: true, blog: created });
    await k.adminMarketing.mockBlogList(d.list);
    await k.adminMarketing.openBlog();
    await k.adminMarketing.openCreateBlog();
    await k.admin.fillForm(d.create.form);
    await k.adminMarketing.clickModalButton(CREATE, 'Lưu bài viết');
    await k.common.verifyRequest('POST', '/admin/blogs', d.create.expectedPayload);
    await k.common.verifyToast(d.create.toast);
    await k.admin.verifyModalClosed(CREATE);
    await k.adminMarketing.verifyRowCount(d.list.length + 1);
    await k.adminMarketing.verifyRowCells(d.create.expectedPayload.title as string, { 'Trạng thái': 'Ẩn', 'Bài viết': 'Nổi bật' });
  });

  test('[ADM-BLG-04] Sửa: form điền sẵn, giữ slug cũ khi đổi tiêu đề, gửi PUT đúng (mock)', async ({ k }) => {
    const updated = { ...d.list[0], title: d.edit.form['Tiêu đề'] };
    await k.common.mockWrite('PUT', ITEM_API, { success: true, blog: updated });
    await k.adminMarketing.mockBlogList(d.list);
    await k.adminMarketing.openBlog();
    await k.admin.clickRowAction(d.edit.title, 'Sửa');
    await k.admin.verifyModalOpen(EDIT);
    for (const [label, value] of Object.entries(d.edit.prefilled)) await k.admin.verifyFieldValue(label, value);
    await k.admin.fillForm(d.edit.form);
    await k.admin.verifyFieldValue('Slug', d.edit.prefilled['Slug']);
    await k.adminMarketing.clickModalButton(EDIT, 'Lưu bài viết');
    await k.common.verifyRequest('PUT', '/admin/blogs/1', d.edit.expectedPayload);
    await k.common.verifyToast(d.edit.toast);
    await k.admin.verifyRow(String(d.edit.form['Tiêu đề']));
  });

  test.describe('Ẩn/Hiển thị, nổi bật trên dòng (data-driven)', () => {
    for (const c of d.toggles) {
      test(caseTitle(c), async ({ k }) => {
        applyCaseMeta(c);
        await k.common.mockWrite('PUT', ITEM_API, { success: true });
        await k.adminMarketing.mockBlogList(d.list);
        await k.adminMarketing.openBlog();
        await k.admin.clickRowAction(c.rowText, c.action);
        await k.common.verifyRequest('PUT', '/admin/blogs/', c.expectedPayload);
        await k.common.verifyToast(c.toast);
        await k.adminMarketing.verifyRowCells(c.rowText, c.expected);
      });
    }
  });

  test('[ADM-BLG-05] Xem chi tiết bài viết', async ({ k }) => {
    await k.adminMarketing.mockBlogList(d.list);
    await k.adminMarketing.openBlog();
    await k.admin.clickRowAction(d.view.title, 'Xem');
    await k.adminMarketing.verifyModalText('Chi tiết bài viết', d.view.texts);
  });

  test('[ADM-BLG-06] Xóa: bấm "Hủy" không gửi DELETE', async ({ k }) => {
    await k.common.mockWrite('DELETE', ITEM_API, { success: true });
    await k.adminMarketing.mockBlogList(d.list);
    await k.adminMarketing.openBlog();
    await k.admin.clickRowAction(d.remove.title, 'Xóa');
    await k.adminMarketing.verifyModalText('Xóa bài viết', ['Bạn có chắc chắn muốn xóa bài viết này không?']);
    await k.adminMarketing.clickModalButton('Xóa bài viết', 'Hủy');
    await k.admin.verifyModalClosed('Xóa bài viết');
    await k.common.verifyNoRequest('DELETE', '/admin/blogs');
  });

  test('[ADM-BLG-07] Xóa: xác nhận gửi DELETE và bỏ dòng (mock)', async ({ k }) => {
    await k.common.mockWrite('DELETE', ITEM_API, { success: true });
    await k.adminMarketing.mockBlogList(d.list);
    await k.adminMarketing.openBlog();
    await k.admin.clickRowAction(d.remove.title, 'Xóa');
    await k.adminMarketing.clickModalButton('Xóa bài viết', 'Xóa');
    await k.common.verifyRequest('DELETE', '/admin/blogs/3');
    await k.common.verifyToast(d.remove.toast);
    await k.admin.verifyRow(d.remove.title, false);
  });

  test('[ADM-BLG-08] Ảnh: URL hợp lệ hiện ảnh xem trước, URL hỏng hiện lỗi', async ({ k }) => {
    await k.adminMarketing.mockBlogList(d.list);
    await k.adminMarketing.openBlog();
    await k.adminMarketing.openCreateBlog();
    await k.adminMarketing.setBlogImage(PIXEL);
    await k.adminMarketing.setBlogImage(d.invalidImage.url, d.invalidImage.error);
  });

  test('[ADM-BLG-09] Hủy form sửa rồi bấm "Thêm bài viết" -> form trống', async ({ k }) => {
    await k.adminMarketing.mockBlogList(d.list);
    await k.adminMarketing.openBlog();
    await k.admin.clickRowAction(d.edit.title, 'Sửa');
    await k.adminMarketing.clickModalButton(EDIT, 'Hủy');
    await k.admin.verifyModalClosed(EDIT);
    await k.adminMarketing.openCreateBlog();
    await k.admin.verifyFieldValue('Tiêu đề', '');
    await k.admin.verifyFieldValue('Slug', '');
    await k.admin.verifyFieldValue('Mô tả ngắn', '');
  });
});
