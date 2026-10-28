import test from 'node:test';
import assert from 'node:assert/strict';
import { validatePlacementSnapshot, placeApparatus } from '../../Build/simulator/apparatus.mjs';
import { rk4Step, integrateRK4 } from '../../Build/simulator/rk4.mjs';

const snapshot = () => validatePlacementSnapshot({ schema_version: '1.0.0', scene_id: 'synthetic-room-v1', bounds_m: { min: [-5, -1, -5], max: [5, 5, 5] }, surfaces: [{ id: 'floor', normal: [0, 1, 0], offset: 0 }] });
const apparatus = () => ({ id: 'box-a', shape: 'box', surface_id: 'floor', half_extents_m: [0.5, 0.5, 0.5], pose: { position_m: [0, 2, 0], rotation_xyzw: [0, 0, 0, 1] } });

test('S10a only validated snapshots reach placement and rest on the selected plane', () => {
  const placed = placeApparatus(snapshot(), apparatus());
  assert.deepEqual(placed.pose.position_m, [0, 0.5, 0]);
  assert.ok(placed.vertices.every(([x, y, z]) => y >= -1e-9));
  assert.throws(() => placeApparatus({ ...snapshot() }, apparatus()), /validated snapshot/);
  assert.throws(() => validatePlacementSnapshot({ ...snapshot(), bounds_m: { min: [0, 0], max: [1, 1] } }), /snapshot bounds/);
});

test('S10b RK4 exponential smoke, fixed-step determinism, and no input mutation', () => {
  const f = (s) => [s[0]];
  const initial = [1]; const out = integrateRK4(initial, 0.01, 100, f);
  assert.equal(initial[0], 1); assert.ok(Math.abs(out.at(-1)[0] - Math.E) < 1e-8);
  assert.deepEqual(out, integrateRK4([1], 0.01, 100, f));
  assert.deepEqual(rk4Step([1, 2], 0.1, () => [1, 0]), [1.1, 2]);
});

test('S10b rejects invalid inputs and malformed dynamics', () => {
  assert.throws(() => rk4Step([1], 0, () => [1]), /dt/);
  assert.throws(() => rk4Step([1], 0.1, () => [NaN]), /derivative/);
  assert.throws(() => integrateRK4([1], 0.1, 1.5, () => [1]), /steps/);
  assert.throws(() => rk4Step([1, Infinity], 0.1, () => [1, 1]), /state/);
});
