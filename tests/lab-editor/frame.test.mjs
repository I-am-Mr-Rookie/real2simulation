// N24: camera auto-frame helpers (robust room bounds, fit distance).
import test from 'node:test';
import assert from 'node:assert/strict';
import { robustBounds, fitDistance } from '../../Build/web/src/lab-editor/frame.mjs';

test('robust bounds ignore a few stray points', () => {
  const pts = [];
  for (let i = 0; i < 200; i += 1) pts.push((i % 10) / 9 * 4 - 2, (i % 7) / 6 * 3, (i % 5) / 4 * 2 + 10);
  pts.push(500, 500, 500, -500, -500, -500);
  const b = robustBounds(new Float32Array(pts));
  assert.ok(b.max[0] <= 2 + 1e-6 && b.min[0] >= -2 - 1e-6, JSON.stringify(b));
  assert.ok(Math.abs(b.center[2] - 11) < 0.3);
  assert.ok(b.radius > 2 && b.radius < 4);
  assert.equal(robustBounds([]), null);
});

test('fit distance grows with radius and with a narrow aspect', () => {
  const d = fitDistance(1, 50, 1.6);
  assert.ok(Math.abs(d - 1.05 / Math.sin((25 * Math.PI) / 180)) < 1e-9);
  assert.ok(fitDistance(2, 50, 1.6) > d);
  assert.ok(fitDistance(1, 50, 0.46) > d);
});
