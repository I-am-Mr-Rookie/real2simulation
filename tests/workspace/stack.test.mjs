import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

// S15j: 375px stacking contract, read from the real stylesheet (no browser needed).
const css = readFileSync(new URL('../../Build/web/src/workspace/workspace.css', import.meta.url), 'utf8');
const narrow = css.match(/@media \(max-width: (\d+)px\) \{([\s\S]*?)\n\}/);

test('375px: single column, sidebar stacked below viewport, panel and job', () => {
  assert.ok(narrow && Number(narrow[1]) >= 375);
  assert.match(narrow[2], /grid-template-columns: minmax\(0, 1fr\)/);
  const areas = narrow[2].match(/grid-template-areas: ([^;]+);/)[1].match(/"(\w+)"/g).map((a) => a.slice(1, -1));
  assert.deepEqual(areas, ['nav', 'viewport', 'panel', 'job', 'side']);
});

test('no fixed width/min-width wider than a 375px viewport minus padding', () => {
  const wide = [...css.matchAll(/(?<![-\w])(min-width|width):\s*([\d.]+)(px|rem)/g)].filter(([, , n, u]) => (u === 'px' ? +n : +n * 16) > 343);
  assert.deepEqual(wide.map((m) => m[0]), []);
});
