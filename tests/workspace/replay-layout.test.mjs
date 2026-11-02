import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

test('phone replay summary clears the floating navigation, including the safe area, without changing desktop', () => {
  const css = readFileSync(new URL('../../Build/web/src/lab-editor/lab-editor.css', import.meta.url), 'utf8');
  const phone = css.slice(css.indexOf('@media (max-width: 900px)'));
  const rail = phone.match(/\.le-rail \{([^}]+)\}/)?.[1];
  const status = phone.match(/\.le-status \{([^}]+)\}/)?.[1];
  assert.ok(rail && status);
  const railBottom = Number(rail.match(/bottom: (\d+)px/)?.[1]);
  const buttonHeight = Number(css.match(/\.le-top button, \.le-file, \.le-timeline button, \.le-float button, \.le-rail button \{[^}]*min-height: (\d+)px/)?.[1]);
  const padding = Number(rail.match(/padding: (\d+)px/)?.[1]);
  const border = Number(rail.match(/border: (\d+)px/)?.[1]);
  const bottom = Number(status.match(/bottom: calc\((\d+)px \+ env\(safe-area-inset-bottom\)\)/)?.[1]);
  assert.ok(bottom >= railBottom + buttonHeight + 2 * (padding + border) + 8, 'summary must sit above the entire rail plus a gap');
  assert.match(status, /env\(safe-area-inset-bottom\)/);
  assert.match(css, /\.le-status \{ position: absolute;[^}]*bottom: 10px;[^}]*overflow-y: auto;/);
});
