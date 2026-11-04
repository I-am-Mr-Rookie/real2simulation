// N89: free-fall sanity check against Earth g, always what-if.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { gravityCheck } from '../../Build/web/src/workspace/measure.mjs';

const q = (value, uncertainty, unit) => ({ quantity: { name: 'vertical acceleration (g if only gravity acts)', value, uncertainty, unit } });

test('pixels: solves for millimetres per pixel at Earth g', () => {
  const g = gravityCheck(q(2329.54, 105.54, 'px/s^2'));
  assert.equal(g.tone, 'warn');
  assert.match(g.text, /^what-if: .*1 pixel is about 4\.21 \+\/- 0\.19 mm/);
});

test('metric: consistent within 2 sigma, else names slow motion or a wrong size', () => {
  assert.match(gravityCheck(q(9.6, 0.3, 'm/s^2')).text, /^Consistent with Earth g .*0\.7 sigma/);
  const slow = gravityCheck(q(2.71, 0.42, 'm/s^2'));
  assert.match(slow.text, /16\.9 sigma .* about 1\.90x slower than real time \(slow motion\), or the size you gave is off by about 3\.62x/);
  assert.match(gravityCheck(q(39.2, 1, 'm/s^2')).text, /about 2\.00x faster than real time \(time-lapse\)/);
});

test('no check for other quantities, missing or non-positive values', () => {
  assert.equal(gravityCheck({ quantity: { name: 'period', value: 1, unit: 's' } }), null);
  assert.equal(gravityCheck(q(-3, 1, 'm/s^2')), null);
  assert.equal(gravityCheck(null), null);
});
