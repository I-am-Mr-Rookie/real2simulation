// S15ah: one theme switch for every surface. S15am: six COLOR_MODES (S15aj contrast.py tables, verbatim) as data; THEME_CSS renders them.
// Choice = system | <palette id> (localStorage); applied palette id on <html data-theme>; dark palettes also get data-tone="dark".
export const THEME_KEY = 'r2s.theme';
export const PALETTES = Object.freeze([
  { id: 'paper', label: 'Paper', dark: false, tokens: { bg: '#f3eee3', surface: '#fffcf5', elevated: '#ffffff', border: '#d8cfbe', 'border-strong': '#8a8174', text: '#1c1a16', muted: '#5a554b', accent: '#b23a0e', 'accent-contrast': '#ffffff', success: '#1d6a3a', warning: '#8a5300', danger: '#a3191b', 'recorded-bg': '#dcebe0', 'recorded-fg': '#14532d', 'simulated-bg': '#e4e3f6', 'simulated-fg': '#3730a3', 'whatif-bg': '#f6e3c6', 'whatif-fg': '#6f3800', shadow: '#1c1a16', focus: '#1c1a16' } },
  { id: 'light', label: 'Light', dark: false, tokens: { bg: '#f7f7f8', surface: '#ffffff', elevated: '#ffffff', border: '#e4e4e7', 'border-strong': '#84848d', text: '#18181b', muted: '#52525b', accent: '#b53d0b', 'accent-contrast': '#ffffff', success: '#15703a', warning: '#8f4e00', danger: '#b91c1c', 'recorded-bg': '#dcf2e3', 'recorded-fg': '#14532d', 'simulated-bg': '#e6e6fb', 'simulated-fg': '#3730a3', 'whatif-bg': '#fbe8cc', 'whatif-fg': '#713f00', shadow: '#18181b', focus: '#18181b' } },
  { id: 'dark', label: 'Dark', dark: true, tokens: { bg: '#111113', surface: '#18181b', elevated: '#212126', border: '#2e2e35', 'border-strong': '#71717c', text: '#f4f4f5', muted: '#a1a1aa', accent: '#ff8a4c', 'accent-contrast': '#1a0d05', success: '#4ade80', warning: '#fbbf24', danger: '#f87171', 'recorded-bg': '#0f2e1c', 'recorded-fg': '#86efac', 'simulated-bg': '#1e1b4b', 'simulated-fg': '#c7d2fe', 'whatif-bg': '#3a2508', 'whatif-fg': '#fcd34d', shadow: '#71717c', focus: '#ff8a4c' } },
  { id: 'midnight', label: 'Midnight', dark: true, tokens: { bg: '#0b1020', surface: '#111831', elevated: '#18213f', border: '#26304f', 'border-strong': '#5f6c95', text: '#e8ecf8', muted: '#9aa6c7', accent: '#7dd3fc', 'accent-contrast': '#062033', success: '#5eead4', warning: '#fcd34d', danger: '#fca5a5', 'recorded-bg': '#0c2e2a', 'recorded-fg': '#99f6e4', 'simulated-bg': '#221d52', 'simulated-fg': '#c4b5fd', 'whatif-bg': '#3a2a0a', 'whatif-fg': '#fde68a', shadow: '#5f6c95', focus: '#7dd3fc' } },
  { id: 'graphite', label: 'Graphite', dark: true, tokens: { bg: '#1f2023', surface: '#26282c', elevated: '#2e3035', border: '#3a3d43', 'border-strong': '#7a7e87', text: '#ededee', muted: '#b0b3ba', accent: '#f08a5d', 'accent-contrast': '#1f0d04', success: '#7bd88f', warning: '#e8c15a', danger: '#ff8f8f', 'recorded-bg': '#1d3324', 'recorded-fg': '#a7f3b9', 'simulated-bg': '#2b2a4a', 'simulated-fg': '#cfd0ff', 'whatif-bg': '#3d3014', 'whatif-fg': '#f5d98a', shadow: '#7a7e87', focus: '#f08a5d' } },
  { id: 'contrast', label: 'High contrast', dark: false, tokens: { bg: '#ffffff', surface: '#ffffff', elevated: '#ffffff', border: '#000000', 'border-strong': '#000000', text: '#000000', muted: '#262626', accent: '#8a1f00', 'accent-contrast': '#ffffff', success: '#0b5a26', warning: '#6b3d00', danger: '#8b0000', 'recorded-bg': '#ffffff', 'recorded-fg': '#0b5a26', 'simulated-bg': '#ffffff', 'simulated-fg': '#2a1f8f', 'whatif-bg': '#ffffff', 'whatif-fg': '#6b3d00', shadow: '#000000', focus: '#000000' } },
]);
export const THEMES = Object.freeze(['system', ...PALETTES.map((p) => p.id)]);
export const THEME_OPTIONS = Object.freeze([{ id: 'system', label: 'System', icon: 'monitor' }, ...PALETTES]);
export const DARK_QUERY = '(prefers-color-scheme: dark)';
export const CONTRAST_QUERY = '(prefers-contrast: more)';
const DARK_IDS = PALETTES.filter((p) => p.dark).map((p) => p.id);
export const toneOf = (theme) => (DARK_IDS.includes(theme) ? 'dark' : 'light');
export const choiceOf = (stored) => (THEMES.includes(stored) ? stored : 'system');
export const resolveTheme = (stored, prefersDark, prefersContrast = false) => {
  const c = choiceOf(stored); return c !== 'system' ? c : prefersContrast ? 'contrast' : prefersDark ? 'dark' : 'light';
};

// COLOR_MODES key -> existing styles.css token name (--r2s-shadow stays the box-shadow shorthand, so the slab colour is --r2s-shadow-ink).
const RENAME = { text: 'ink', success: 'ok', warning: 'warn', 'accent-contrast': 'accent-ink', shadow: 'shadow-ink' };
const levels = (p) => (p.id === 'contrast' ? ['3px 3px 0 #000', '3px 3px 0 #000', '6px 6px 0 #000']
  : p.dark ? ['2px 2px 0 var(--r2s-shadow-ink)', '3px 3px 0 var(--r2s-shadow-ink)', '4px 4px 0 var(--r2s-shadow-ink), 0 16px 40px rgba(0,0,0,.55)']
    : ['2px 2px 0 var(--r2s-shadow-ink)', '4px 4px 0 var(--r2s-shadow-ink)', '6px 6px 0 var(--r2s-shadow-ink), 0 12px 32px rgba(0,0,0,.12)']);
// html:root[...] outranks app/styles.css :root[...] blocks regardless of stylesheet order; rendered once by ShellFrame.
export const THEME_CSS = PALETTES.map((p) => {
  const [s1, s2, s3] = levels(p);
  const vars = Object.entries(p.tokens).map(([k, v]) => '--r2s-' + (RENAME[k] ?? k) + ':' + v).join(';');
  return 'html:root[data-theme="' + p.id + '"]{color-scheme:' + (p.dark ? 'dark' : 'light') + ';' + vars + ';--r2s-shadow-sm:' + s1 + ';--r2s-shadow:' + s2 + ';--r2s-shadow-3:' + s3 +
    ';--r2s-overlay:' + (p.dark ? 'rgba(0,0,0,.62)' : 'rgba(28,26,22,.42)') + ';--r2s-accent-soft:color-mix(in srgb,' + p.tokens.accent + ' 14%,' + p.tokens.surface + ');--r2s-chart-1:' + p.tokens.text + ';--r2s-chart-2:' + p.tokens['border-strong'] + '}';
}).join('\n');

// Inline in <head> before paint (no flash). Mirrors resolveTheme; storage/matchMedia failures fall back to light.
export const THEME_SCRIPT = "(function(){var d=document.documentElement;try{var s=localStorage.getItem('" + THEME_KEY + "');var c=" + JSON.stringify(THEMES) + ".indexOf(s)>0?s:'system';" +
  "var t=c!=='system'?c:matchMedia('" + CONTRAST_QUERY + "').matches?'contrast':matchMedia('" + DARK_QUERY + "').matches?'dark':'light';" +
  "d.dataset.theme=t;d.dataset.tone=" + JSON.stringify(DARK_IDS) + ".indexOf(t)>=0?'dark':'light';d.dataset.themeChoice=c}catch(e){d.dataset.theme='light';d.dataset.tone='light'}})()";

// Persist + apply a choice; returns the applied theme. env = { doc, store, prefersDark, prefersContrast } (injectable for tests).
export function applyTheme(choice, { doc = globalThis.document, store = globalThis.localStorage, prefersDark = globalThis.matchMedia?.(DARK_QUERY).matches,
  prefersContrast = globalThis.matchMedia?.(CONTRAST_QUERY).matches } = {}) {
  const c = choiceOf(choice);
  try { if (c === 'system') store?.removeItem(THEME_KEY); else store?.setItem(THEME_KEY, c); } catch { /* private mode: theme still applies for this page */ }
  const t = resolveTheme(c, prefersDark, prefersContrast);
  if (doc?.documentElement) Object.assign(doc.documentElement.dataset, { theme: t, tone: toneOf(t), themeChoice: c });
  return t;
}
