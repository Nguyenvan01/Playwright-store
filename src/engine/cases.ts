import { test } from '@playwright/test';
import { env } from '@config/env';
import type { DataCase, Requirement } from '@data/types';

const REQUIREMENTS: Record<Requirement, () => string | null> = {
  customer: () => (env.customer.email ? null : 'Cần E2E_CUSTOMER_EMAIL/PASSWORD'),
  admin: () => (env.admin.email ? null : 'Cần E2E_ADMIN_EMAIL/PASSWORD'),
  allowWrite: () => (env.allowWrite ? null : 'Cần E2E_ALLOW_WRITE=1 (ghi dữ liệu thật)'),
};

/** Lý do skip nếu thiếu điều kiện, null nếu đủ. */
export function missingRequirement(requires: Requirement[] = []): string | null {
  for (const r of requires) {
    const reason = REQUIREMENTS[r]?.();
    if (reason) return reason;
  }
  return null;
}

/** Tên test chuẩn cho 1 case dữ liệu: "[ID] Tiêu đề @tag". */
export function caseTitle(c: DataCase): string {
  return `[${c.id}] ${c.title}${c.tags?.length ? ` ${c.tags.join(' ')}` : ''}`;
}

/** Gọi đầu thân test: skip nếu thiếu điều kiện, đánh dấu test.fail nếu là bug đã biết. */
export function applyCaseMeta(c: DataCase) {
  const reason = missingRequirement(c.requires);
  test.skip(!!reason, reason ?? '');
  if (c.knownBug) test.fail(true, `BUG: ${c.knownBug}`);
}
