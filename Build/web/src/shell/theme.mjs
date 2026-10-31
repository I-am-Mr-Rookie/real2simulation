// S15ah: one theme switch for every surface. Choice = system | light | dark (localStorage); applied = light | dark on <html data-theme>.
export const THEME_KEY = 'r2s.theme';
// A palette = one [data-theme="<id>"] variables block in app/styles.css; add more here (S15am: midnight/graphite/paper/high-contrast).
export const PALETTES = Object.freeze([{ id: 'light', label: 'Light', icon: 'sun', dark: false }, { id: 'dark', label: 'Dark', icon: 'moon', dark: true }]);
export const THEMES = Object.freeze(['system', ...PALETTES.map((p) => p.id)]);
export const THEME_OPTIONS = Object.freeze([{ id: 'system', label: 'System', icon: 'monitor' }, ...PALETTES]);
export const DARK_QUERY = '(prefers-color-scheme: dark)';
export const choiceOf = (stored) => (THEMES.includes(stored) ? stored : 'system');
export const resolveTheme = (stored, prefersDark) => { const c = choiceOf(stored); return c === 'system' ? (prefersDark ? 'dark' : 'light') : c; };

// Inline in <head> before paint (no flash). Mirrors resolveTheme; storage/matchMedia failures fall back to light.
export const THEME_SCRIPT = "(function(){var d=document.documentElement;try{var s=localStorage.getItem('" + THEME_KEY + "');var c=" + JSON.stringify(THEMES) + ".indexOf(s)>0?s:'system';" +
  "d.dataset.theme=c==='system'?(matchMedia('" + DARK_QUERY + "').matches?'dark':'light'):c;d.dataset.themeChoice=c}catch(e){d.dataset.theme='light'}})()";

// Persist + apply a choice; returns the applied theme. env = { doc, store, prefersDark } (injectable for tests).
export function applyTheme(choice, { doc = globalThis.document, store = globalThis.localStorage, prefersDark = globalThis.matchMedia?.(DARK_QUERY).matches } = {}) {
  const c = choiceOf(choice);
  try { if (c === 'system') store?.removeItem(THEME_KEY); else store?.setItem(THEME_KEY, c); } catch { /* private mode: theme still applies for this page */ }
  const t = resolveTheme(c, prefersDark);
  if (doc?.documentElement) { doc.documentElement.dataset.theme = t; doc.documentElement.dataset.themeChoice = c; }
  return t;
}
