/** Chuỗi an toàn để đặt trong selector CSS `:text-is("...")`. */
export const cssText = (text: string) => text.replace(/\\/g, '\\\\').replace(/"/g, '\\"');

/** Escape chuỗi để dùng trong RegExp. */
export const escapeRegex = (text: string) => text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
