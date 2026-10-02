import { Keywords, KEYWORD_GROUPS } from '@keywords/index';

type KeywordFn = (...args: unknown[]) => Promise<unknown>;

/** Method nội bộ, không cho kịch bản JSON gọi. */
const EXCLUDED = new Set(['constructor', 'step', 'watchReload']);

/** Toàn bộ keyword dạng "nhóm.hàm" mà kịch bản JSON có thể gọi. */
export function listKeywords(k: Keywords): string[] {
  return KEYWORD_GROUPS.flatMap((group) => {
    const proto = Object.getPrototypeOf(k[group]);
    return Object.getOwnPropertyNames(proto)
      .filter((name) => !EXCLUDED.has(name) && typeof proto[name] === 'function')
      .map((name) => `${group}.${name}`);
  });
}

/** Tìm keyword theo tên "nhóm.hàm" -> hàm đã bind sẵn. */
export function resolveKeyword(k: Keywords, name: string): KeywordFn {
  const [group, method, ...rest] = name.split('.');
  const target = (KEYWORD_GROUPS as readonly string[]).includes(group)
    ? (k as unknown as Record<string, Record<string, unknown>>)[group]
    : undefined;
  const fn = target?.[method];
  if (rest.length || !target || EXCLUDED.has(method) || typeof fn !== 'function') {
    throw new Error(`Keyword không tồn tại: "${name}". Xem danh sách trong KEYWORDS.md`);
  }
  return (fn as KeywordFn).bind(target);
}
