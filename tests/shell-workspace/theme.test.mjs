import test from 'node:test';
import assert from 'node:assert/strict';
import { resolveTheme, choiceOf, applyTheme, THEME_KEY, THEME_SCRIPT } from '../../Build/web/src/shell/theme.mjs';

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
  for (const [stored, dark] of [[null, true], [null, false], ['light', true], ['dark', false], ['bogus', true]]) {
    const doc = { documentElement: { dataset: {} } };
    new Function('document', 'localStorage', 'matchMedia', THEME_SCRIPT)(doc, { getItem: () => stored }, () => ({ matches: dark }));
    assert.equal(doc.documentElement.dataset.theme, resolveTheme(stored, dark));
  }
});

