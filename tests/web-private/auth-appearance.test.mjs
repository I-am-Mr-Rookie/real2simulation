import assert from 'node:assert/strict';
import test from 'node:test';
import { readFileSync } from 'node:fs';
import { clerkAppearance } from '../../Build/web/src/auth/appearance.js';
import { PALETTES } from '../../Build/web/src/shell/theme.mjs';

const luminance = (hex) => {
  const [r, g, b] = [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16) / 255)
    .map((v) => v <= 0.04045 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4);
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
};
const contrast = (a, b) => { const [lo, hi] = [luminance(a), luminance(b)].sort((x, y) => x - y); return (hi + 0.05) / (lo + 0.05); };

test('both auth pages share Clerk 7 appearance, live CSS tokens and AA text/control pairs in all six palettes', () => {
  const v = clerkAppearance.variables;
  for (const key of ['formFieldInput', 'socialButtonsBlockButton']) {
    assert.equal(clerkAppearance.elements[key].borderWidth, '1px !important'); // Beat Clerk's variant borderWidth:0.
    assert.equal(clerkAppearance.elements[key].borderColor, 'var(--r2s-border-strong)');
  }
  for (const removed of ['colorText', 'colorTextSecondary', 'colorInputText', 'colorInputBackground']) assert.equal(v[removed], undefined);
  const aliases = { ink: 'text', 'accent-ink': 'accent-contrast', ok: 'success', warn: 'warning' };
  for (const p of PALETTES) {
    const color = (key) => {
      const token = /^var\(--r2s-([\w-]+)\)$/.exec(v[key])?.[1];
      assert.ok(token, key);
      return p.tokens[aliases[token] || token];
    };
    for (const [fg, bg] of [['colorForeground', 'colorBackground'], ['colorMutedForeground', 'colorBackground'],
      ['colorInputForeground', 'colorInput'], ['colorPrimaryForeground', 'colorPrimary'], ['colorPrimary', 'colorMuted'],
      ['colorDanger', 'colorBackground'], ['colorWarning', 'colorBackground']]) {
      assert.ok(contrast(color(fg), color(bg)) >= 4.5, p.id + ': ' + fg + '/' + bg);
    }
    assert.ok(contrast(color('colorBorder'), color('colorInput')) >= 3, p.id + ': input boundary');
  }
  for (const route of ['sign-in', 'sign-up']) {
    const src = readFileSync(new URL('../../Build/web/src/app/(public)/' + route + '/[[...' + route + ']]/page.jsx', import.meta.url), 'utf8');
    assert.match(src, /appearance=\{clerkAppearance\}/);
  }
});
