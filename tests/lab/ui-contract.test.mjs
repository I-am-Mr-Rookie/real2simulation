import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';

const source = await readFile(new URL('../../Build/web/src/lab/LabClient.jsx', import.meta.url), 'utf8');
const css = await readFile(new URL('../../Build/web/src/lab/lab.css', import.meta.url), 'utf8');

test('lab UI keeps the user flow and trust labels visible in source', () => {
  for (const text of ['Run trial', 'Fit &amp; reveal', 'Mystery-g mode', 'Simulated', 'limitations', 'aria-live="polite"']) assert.match(source, new RegExp(text));
  assert.match(source, /action: 'start'/); assert.match(source, /action: 'fit'/);
  assert.match(source, /disabled=\{!session \|\| !ballistic/);
  assert.doesNotMatch(source, /gravity\s*=\s*9\.81|seed\s*=|privateSetup/);
});

test('lab layout collapses before the narrow mobile viewport', () => {
  assert.match(css, /max-width: 390px/);
  assert.match(css, /overflow-x: auto/);
  assert.match(css, /grid-template-columns: 1fr/);
});
