// N33 undo/redo for lab-scene-v1 edits (toolbar, gizmo, keyboard and agent edits). Pure, so node tests cover it.
export const MAX_HISTORY = 100;
export const emptyHistory = () => ({ past: [], future: [] });
export const record = (h, prev) => ({ past: [...h.past, prev].slice(-MAX_HISTORY), future: [] });
export function undo(h, current) {
  if (!h.past.length) return null;
  return { scene: h.past.at(-1), history: { past: h.past.slice(0, -1), future: [current, ...h.future] } };
}
export function redo(h, current) {
  if (!h.future.length) return null;
  return { scene: h.future[0], history: { past: [...h.past, current], future: h.future.slice(1) } };
}
export const removeObject = (scene, id) => ({ ...scene, objects: scene.objects.filter((o) => o.id !== id) });
// Keys that should not delete objects while the user types in a field.
export const typing = (el) => !!el && (el.isContentEditable || ['INPUT', 'TEXTAREA', 'SELECT'].includes(el.tagName));
