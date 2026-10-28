// S09e: device render budget (DPR cap + detail tier) and deterministic point decimation.
// Expectations are hand-derived literals, not recomputed with the code under test.
import test from 'node:test';
import assert from 'node:assert/strict';
import { renderBudget, decimatePoints, probeDevice } from '../../Build/web/src/viewer/render-budget.mjs';

const FULL = { tier: 'full', pixelRatio: 2, maxPoints: 2_000_000, antialias: true };
const REDUCED = { tier: 'reduced', pixelRatio: 1.5, maxPoints: 250_000, antialias: false };

test('desktop budget caps DPR at 2 and keeps full detail', () => {
  assert.deepEqual({ ...renderBudget({ devicePixelRatio: 3, viewportWidthPx: 1440 }) }, FULL);
  assert.deepEqual({ ...renderBudget({ devicePixelRatio: 1.25, viewportWidthPx: 1440, deviceMemoryGiB: 8, cores: 8 }) }, { ...FULL, pixelRatio: 1.25 });
});

test('375 px phone gets reduced detail and DPR capped at 1.5', () => {
  assert.deepEqual({ ...renderBudget({ devicePixelRatio: 3, viewportWidthPx: 375 }) }, REDUCED);
});

test('tier boundaries: width 767 reduced, 768 full; memory <4 GiB or <4 cores reduced', () => {
  assert.equal(renderBudget({ devicePixelRatio: 1, viewportWidthPx: 767 }).tier, 'reduced');
  assert.equal(renderBudget({ devicePixelRatio: 1, viewportWidthPx: 768 }).tier, 'full');
  assert.equal(renderBudget({ devicePixelRatio: 1, viewportWidthPx: 1440, deviceMemoryGiB: 2 }).tier, 'reduced');
  assert.equal(renderBudget({ devicePixelRatio: 1, viewportWidthPx: 1440, deviceMemoryGiB: 4 }).tier, 'full');
  assert.equal(renderBudget({ devicePixelRatio: 2, viewportWidthPx: 1280, cores: 2 }).pixelRatio, 1.5);
  assert.equal(renderBudget({ devicePixelRatio: 2, viewportWidthPx: 1280, cores: 4 }).pixelRatio, 2);
});

test('invalid or missing device facts fall back deterministically (DPR 1, unknown facts ignored)', () => {
  for (const dpr of [NaN, 0, -2, Infinity, undefined, '3']) assert.equal(renderBudget({ devicePixelRatio: dpr, viewportWidthPx: 1440 }).pixelRatio, 1);
  assert.deepEqual({ ...renderBudget({}) }, { ...FULL, pixelRatio: 1 });
  assert.deepEqual({ ...renderBudget() }, { ...FULL, pixelRatio: 1 });
  assert.equal(renderBudget({ devicePixelRatio: 2, viewportWidthPx: NaN, deviceMemoryGiB: 'x', cores: -1 }).tier, 'full');
});

test('same device -> identical frozen budget', () => {
  const d = { devicePixelRatio: 2.75, viewportWidthPx: 412, deviceMemoryGiB: 4, cores: 8 };
  const a = renderBudget(d), b = renderBudget({ ...d });
  assert.deepEqual(a, b);
  assert.ok(Object.isFrozen(a));
});

test('probeDevice uses the narrower of layout viewport and screen (phone page without meta viewport reports 980)', () => {
  const phone = { devicePixelRatio: 3, innerWidth: 981, screen: { width: 375 }, navigator: { deviceMemory: 8, hardwareConcurrency: 8 } };
  assert.deepEqual(probeDevice(phone), { devicePixelRatio: 3, viewportWidthPx: 375, deviceMemoryGiB: 8, cores: 8 });
  assert.equal(renderBudget(probeDevice(phone)).tier, 'reduced');
  assert.equal(probeDevice({ innerWidth: 700, screen: { width: 1920 } }).viewportWidthPx, 700);
  assert.equal(probeDevice({ innerWidth: 1280 }).viewportWidthPx, 1280);
  assert.equal(probeDevice({}).viewportWidthPx, undefined);
});

test('decimatePoints keeps every ceil(n/max)-th point, colours aligned', () => {
  const positions = Float32Array.from({ length: 30 }, (_, i) => i); // point k = [3k, 3k+1, 3k+2]
  const colors = Uint8Array.from({ length: 30 }, (_, i) => 100 + i);
  const d = decimatePoints(positions, colors, 4); // stride 3 -> points 0,3,6,9
  assert.equal(d.count, 4);
  assert.deepEqual([...d.positions], [0, 1, 2, 9, 10, 11, 18, 19, 20, 27, 28, 29]);
  assert.deepEqual([...d.colors], [100, 101, 102, 109, 110, 111, 118, 119, 120, 127, 128, 129]);
  assert.deepEqual([...decimatePoints(positions, colors, 4).positions], [...d.positions]);
});

test('decimatePoints returns the original arrays when within budget and rejects bad caps', () => {
  const positions = new Float32Array(6), colors = new Uint8Array(6);
  const d = decimatePoints(positions, colors, 2);
  assert.equal(d.positions, positions); assert.equal(d.colors, colors); assert.equal(d.count, 2);
  for (const m of [0, -1, 1.5, NaN]) assert.throws(() => decimatePoints(positions, colors, m));
  assert.throws(() => decimatePoints(positions, new Uint8Array(3), 2));
});
