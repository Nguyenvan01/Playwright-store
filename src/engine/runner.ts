import { test } from '@playwright/test';
import type { Keywords } from '@keywords/index';
import { DataContext, maskSecrets, resolveData } from '@data/loader';
import type { Scenario, ScenarioStep } from '@data/types';
import { listKeywords, resolveKeyword } from './registry';

function stepArgs(step: ScenarioStep, ctx: DataContext): unknown[] {
  if (step.arg !== undefined && step.args !== undefined) {
    throw new Error(`Bước "${step.keyword}" chỉ được dùng "arg" HOẶC "args"`);
  }
  if (step.arg !== undefined) return [resolveData(step.arg, ctx)];
  if (step.args === undefined) return [];
  if (!Array.isArray(step.args)) {
    throw new Error(`Bước "${step.keyword}": "args" phải là mảng. Dùng "arg" cho 1 tham số.`);
  }
  return resolveData(step.args, ctx);
}

function formatArgs(args: unknown[]): string {
  return args
    .map((a) => {
      const s = typeof a === 'string' ? `"${a}"` : JSON.stringify(a);
      return s.length > 60 ? `${s.slice(0, 57)}...` : s;
    })
    .join(', ');
}

/** Kiểm tra mọi keyword trong kịch bản đều tồn tại (báo lỗi trước khi chạy bước nào). */
export function validateScenario(k: Keywords, scenario: Scenario) {
  const available = new Set(listKeywords(k));
  const unknown = scenario.steps.map((s) => s.keyword).filter((name) => !available.has(name));
  if (unknown.length) {
    throw new Error(
      `Kịch bản ${scenario.id} dùng keyword không tồn tại: ${unknown.join(', ')}\n` +
        `Keyword có sẵn:\n  ${[...available].join('\n  ')}`,
    );
  }
}

/** Chạy lần lượt các bước của 1 kịch bản keyword-driven. */
export async function runScenario(k: Keywords, scenario: Scenario, ctx: DataContext) {
  validateScenario(k, scenario);
  for (const [i, step] of scenario.steps.entries()) {
    const args = stepArgs(step, ctx);
    const title = `${i + 1}. ${step.keyword}(${formatArgs(args)})${step.note ? ` — ${step.note}` : ''}`;
    await test.step(maskSecrets(title), async () => {
      await resolveKeyword(k, step.keyword)(...args);
    });
  }
}
