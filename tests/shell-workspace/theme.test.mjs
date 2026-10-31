import test from 'node:test';
import assert from 'node:assert/strict';
import { resolveTheme, choiceOf, applyTheme, THEME_KEY, THEME_SCRIPT, THEME_CSS, PALETTES, THEME_OPTIONS, toneOf } from '../../Build/web/src/shell/theme.mjs';

test('resolveTheme: system follows prefers-color-scheme, explicit wins, junk = system', () => {
  assert.equal(resolveTheme(null, true), 'dark');
  assert.equal(resolveTheme(undefined, false), 'light');
  assert.equal(resolveTheme('light', true), 'light');
  assert.equal(resolveTheme('dark', false), 'dark');
  assert.equal(choiceOf('purple'), 'system');
});

test('applyTheme persists explicit choices, clears system, sets html data-theme', () => {
  const m = new Map(); const store = { setItem: (k, v) => m.set(k, v), removeItem: (k) => m.delete(k) };
  const doc = { documentElement: { dataset: {} } };
  assert.equal(applyTheme('dark', { doc, store, prefersDark: false }), 'dark');
  assert.equal(m.get(THEME_KEY), 'dark'); assert.equal(doc.documentElement.dataset.theme, 'dark');
  assert.equal(applyTheme('system', { doc, store, prefersDark: true }), 'dark');
  assert.equal(m.has(THEME_KEY), false); assert.equal(doc.documentElement.dataset.themeChoice, 'system');
  const broken = { setItem() { throw new Error('quota'); }, removeItem() { throw new Error('quota'); } };
  assert.equal(applyTheme('light', { doc, store: broken, prefersDark: true }), 'light');
});

test('THEME_SCRIPT (pre-paint) agrees with resolveTheme', () => {
  for (const [stored, dark, hc] of [[null, true], [null, false], ['light', true], ['dark', false], ['bogus', true], ['midnight', false], [null, false, true], ['paper', true, true]]) {
    const doc = { documentElement: { dataset: {} } };
    new Function('document', 'localStorage', 'matchMedia', THEME_SCRIPT)(doc, { getItem: () => stored }, (q) => ({ matches: q.includes('contrast') ? !!hc : dark }));
    const want = resolveTheme(stored, dark, !!hc);
    assert.equal(doc.documentElement.dataset.theme, want); assert.equal(doc.documentElement.dataset.tone, toneOf(want));
  }
});

// S15am: six COLOR_MODES, System first, every mode rendered as one data-theme block, AA pairs recomputed (not copied).
const lum = (hex) => { const c = [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16) / 255).map((v) => (v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4)); return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]; };
const ratio = (a, b) => { const [x, y] = [lum(a), lum(b)].sort((p, q) => q - p); return (x + 0.05) / (y + 0.05); };
test('six modes in the menu, each a data-theme block, AA per mode', () => {
  assert.deepEqual(THEME_OPTIONS.map((o) => o.id), ['system', 'paper', 'light', 'dark', 'midnight', 'graphite', 'contrast']);
  for (const p of PALETTES) {
    assert.match(THEME_CSS, new RegExp('data-theme="' + p.id + '"\\]\\{color-scheme:' + (p.dark ? 'dark' : 'light')));
    const t = p.tokens, fails = [];
    for (const fg of ['text', 'muted', 'accent', 'success', 'warning', 'danger']) for (const bg of ['bg', 'surface', 'elevated']) if (ratio(t[fg], t[bg]) < 4.5) fails.push(fg + '/' + bg);
    for (const [fg, bg] of [['accent-contrast', 'accent'], ['recorded-fg', 'recorded-bg'], ['simulated-fg', 'simulated-bg'], ['whatif-fg', 'whatif-bg']]) if (ratio(t[fg], t[bg]) < 4.5) fails.push(fg + '/' + bg);
    for (const [fg, bg] of [['border-strong', 'bg'], ['border-strong', 'surface'], ['focus', 'bg'], ['focus', 'surface'], ['shadow', 'surface']]) if (ratio(t[fg], t[bg]) < 3) fails.push(fg + '/' + bg);
    assert.deepEqual(fails, [], p.id);
  }
});

test('applyTheme persists every mode and sets tone', () => {
  const m = new Map(); const store = { setItem: (k, v) => m.set(k, v), removeItem: (k) => m.delete(k) };
  for (const p of PALETTES) { const doc = { documentElement: { dataset: {} } }; assert.equal(applyTheme(p.id, { doc, store, prefersDark: false, prefersContrast: false }), p.id);
    assert.equal(m.get(THEME_KEY), p.id); assert.equal(doc.documentElement.dataset.tone, p.dark ? 'dark' : 'light'); }
});

