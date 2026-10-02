import { test } from '@fixtures';
import { AUTH_FILES } from '@config/env';
import { loadData } from '@data/loader';
import type { ReportsData } from '@data/admin-ops.types';
import { applyCaseMeta, caseTitle } from '@engine/cases';
import { hasAdminAuth } from '@utils/storage';

const d = loadData<ReportsData>('admin-ops/reports.json');
const OVERVIEW = '/admin/reports/overview';

test.describe('Quản trị - Báo cáo', () => {
  test.use({ storageState: AUTH_FILES.admin });
  test.skip(() => !hasAdminAuth(), 'Cần E2E_ADMIN_EMAIL/PASSWORD trong .env');

  test('[ADO-RPT-01] Dữ liệu thật: đủ thẻ tổng quan và các khối báo cáo @smoke', async ({ k }) => {
    await k.adminOps.openReports();
    for (const text of [...d.cardLabels, ...d.sectionHeadings]) await k.common.verifyTextVisible(text);
    await k.common.verifyNoPageErrors();
  });

  test('[ADO-RPT-02] Thẻ tổng quan, cảnh báo, biểu đồ trạng thái hiển thị đúng số liệu API', async ({ k }) => {
    await k.adminOps.mockReportsOverview(d.overview);
    await k.adminOps.openReports();
    await k.adminOps.verifyStatCards(d.summaryCards);
    await k.common.verifyTextVisible('+12.5% so với kỳ trước');
    await k.adminOps.verifyReportSectionText('Trạng thái đơn hàng', d.statusLegend);
  });

  test('[ADO-RPT-03] Bảng "Sản phẩm bán chạy" và "Khách hàng mua nhiều"', async ({ k }) => {
    await k.adminOps.mockReportsOverview(d.overview);
    await k.adminOps.openReports();
    for (const s of d.sections) await k.adminOps.verifyReportSection(s.heading, s.rows, s.firstRow);
    await k.adminOps.verifyReportSectionText('Sản phẩm bán chạy', ['Chưa phân loại']);
  });

  test('[ADO-RPT-04] Không có dữ liệu: thẻ = 0 và các khối báo trống', async ({ k }) => {
    await k.adminOps.mockReportsOverview(d.emptyOverview);
    await k.adminOps.openReports();
    await k.adminOps.verifyStatCards(d.emptyCards);
    for (const [heading, text] of Object.entries(d.emptyTexts)) await k.adminOps.verifyReportSectionText(heading, [text]);
  });

  test('[ADO-RPT-05] API lỗi -> toast "Không thể tải dữ liệu báo cáo."', async ({ k }) => {
    await k.common.mockGet('**/api/admin/reports/overview*', { success: false }, 500);
    await k.adminOps.openReports();
    await k.common.verifyToast('Không thể tải dữ liệu báo cáo.');
  });

  test.describe('Chọn kỳ báo cáo (data-driven)', () => {
    for (const c of d.periods) {
      test(caseTitle(c), async ({ k }) => {
        applyCaseMeta(c);
        await k.adminOps.mockReportsOverview(d.overview);
        await k.adminOps.openReports();
        if (c.value) await k.adminOps.selectReportPeriod(c.value);
        await k.adminOps.verifyListQuery(OVERVIEW, { period: c.apiPeriod, start_date: null, end_date: null });
        await k.adminOps.verifyReportSectionText('Doanh thu theo thời gian', [c.label]);
      });
    }
  });

  test(caseTitle(d.custom), async ({ k }) => {
    applyCaseMeta(d.custom);
    await k.adminOps.mockReportsOverview(d.overview);
    await k.adminOps.openReports();
    await k.adminOps.selectReportPeriod('custom');
    await k.adminOps.applyCustomRange(d.custom.start, d.custom.end);
    await k.adminOps.verifyListQuery(OVERVIEW, { period: 'custom', start_date: d.custom.start, end_date: d.custom.end });
  });

  test(caseTitle(d.customDefaults), async ({ k }) => {
    applyCaseMeta(d.customDefaults);
    await k.adminOps.mockReportsOverview(d.overview);
    await k.adminOps.openReports();
    await k.adminOps.selectReportPeriod('custom');
    await k.adminOps.verifyCustomRangeDefaults();
  });

  test.describe('Xuất báo cáo CSV (data-driven)', () => {
    for (const c of d.exports) {
      test(caseTitle(c), async ({ k }) => {
        applyCaseMeta(c);
        await k.adminOps.mockReportsOverview(d.overview);
        await k.adminOps.openReports();
        if (c.value) await k.adminOps.selectReportPeriod(c.value);
        if (c.range) await k.adminOps.applyCustomRange(c.range.start, c.range.end);
        await k.adminOps.exportReport(c.filePattern, c.lines);
      });
    }
  });
});
