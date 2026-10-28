// Shared viewer helpers. Framework-free ES module (no package manifest; S04a owns deps).

/** Viewer failure with a stable plain-text code. Messages are authored here, never upstream text. */
export class ViewerError extends Error {
  constructor(code, message) { super(message); this.name = 'ViewerError'; this.code = code; }
}

export const abortError = () => new DOMException('Viewer mount aborted', 'AbortError');

/** Recursively freeze plain objects/arrays. Typed arrays cannot be frozen and are left as-is. */
export function deepFreeze(v) {
  if (v && typeof v === 'object' && !ArrayBuffer.isView(v) && !Object.isFrozen(v)) {
    Object.freeze(v);
    for (const k of Object.keys(v)) deepFreeze(v[k]);
  }
  return v;
}
