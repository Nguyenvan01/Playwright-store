import { Page, test } from '@playwright/test';
import type { ApiClient } from '@api/ApiClient';
import type { PageObjects } from '@pages/PageObjects';
import { maskSecrets } from '@data/loader';

/**
 * Lớp cha của mọi nhóm keyword.
 * Quy ước: mỗi method public = 1 keyword, có 1 dòng JSDoc mô tả (dùng để sinh KEYWORDS.md),
 * thân hàm bọc trong `this.step()` để hiện thành 1 bước có tên trong report.
 */
export abstract class BaseKeywords {
  constructor(
    protected readonly page: Page,
    protected readonly po: PageObjects,
    protected readonly api: ApiClient,
  ) {}

  protected step<T>(title: string, body: () => Promise<T>): Promise<T> {
    return test.step(maskSecrets(title), body, { box: true });
  }
}
