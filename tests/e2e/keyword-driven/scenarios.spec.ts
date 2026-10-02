import { test } from '@fixtures';
import { listDataFiles, loadData } from '@data/loader';
import type { Scenario } from '@data/types';
import { applyCaseMeta, caseTitle } from '@engine/cases';
import { runScenario } from '@engine/runner';

/**
 * Keyword-driven: mỗi phần tử trong test-data/scenarios/*.json là 1 test.
 * Thêm kịch bản mới = thêm JSON, không cần sửa code. Danh sách keyword: KEYWORDS.md
 */
for (const file of listDataFiles('scenarios')) {
  test.describe(`Kịch bản ${file}`, () => {
    for (const scenario of loadData<Scenario[]>(file)) {
      test(caseTitle(scenario), async ({ k, ctx }) => {
        applyCaseMeta(scenario);
        await runScenario(k, scenario, ctx);
      });
    }
  });
}
