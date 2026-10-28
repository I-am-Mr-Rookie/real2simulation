import test from 'node:test';
import assert from 'node:assert/strict';
import { consumeValidatedSetupArtifact, placeApparatus } from '../../Build/simulator/apparatus.mjs';
import { rk4Step, integrateRK4 } from '../../Build/simulator/rk4.mjs';
const valid = { artifact_version: 's10-validated-setup-v1', validation: 'validate_setup', producer: 'contracts/experiment/validate_experiment.py', spec: { scene: { scene_id: 'synthetic-room-v1', schema_version: '1.0.0', constraints: { bounds_m: { min: [-5, -1, -5], max: [5, 5, 5] } } }, placement: { surface_id: null, origin: { value: [0, 1, 0] } }, body: { radius: { value: 0.1 } } }, scene: { id: 'synthetic-room-v1', schema_version: '1.0.0', synthetic: true, bounds_m: { min: [-5, -1, -5], max: [5, 5, 5] }, surfaces: [], colliders: [] } };

test('S10a consumes only the trusted S08 validate_setup export and places geometry', () => {
  const artifact = consumeValidatedSetupArtifact(valid); const placed = placeApparatus(artifact);
  assert.deepEqual(placed.pose.position_m, [0, 1, 0]); assert.equal(placed.validation, 'validate_setup');
  assert.throws(() => consumeValidatedSetupArtifact({ ...valid, producer: 'caller' }), /trusted-transport/);
  assert.throws(() => consumeValidatedSetupArtifact({ ...valid, spec: { ...valid.spec, scene: { ...valid.spec.scene, constraints: { bounds_m: { min: [0, 0, 0], max: [1, 1, 1] } } } } }), /bounds mismatch/);
  assert.throws(() => placeApparatus({ ...artifact }), /returned by consume/);
  assert.ok(Object.isFrozen(artifact.spec.scene.constraints));
  assert.throws(() => { artifact.spec.scene.constraints.bounds_m.min[0] = -99; }, TypeError);
  assert.deepEqual(placeApparatus(artifact).pose.position_m, [0, 1, 0]);
});

test('RK4 zero-step validates every input, rejects sparse state, and preserves state', () => {
  assert.deepEqual(integrateRK4([1], 0.1, 0, (s) => [s[0]]), [[1]]);
  for (const args of [[[], 0.1, 0, null], [[1], NaN, 0, null], [[1], 0.1, 0, 'nope'], [[1, , 2], 0.1, 0, () => [1, 1, 1]]]) assert.throws(() => integrateRK4(...args), /INVALID_RK4/);
  const initial = [1]; integrateRK4(initial, 0.1, 0, (s) => [s[0]]); assert.deepEqual(initial, [1]);
});

test('RK4 convergence/order, determinism, immutability and invalid dynamics', () => {
  const dyn = (s) => [s[1], -s[0]]; const solve = (dt) => integrateRK4([1, 0], dt, Math.round(1 / dt), dyn).at(-1);
  const coarse = Math.abs(solve(0.1)[0] - Math.cos(1)), fine = Math.abs(solve(0.05)[0] - Math.cos(1));
  assert.ok(coarse / fine > 10); assert.deepEqual(solve(0.05), solve(0.05));
  assert.throws(() => rk4Step([1], 0.1, () => [NaN]), /derivative/);
  assert.throws(() => rk4Step([1], 0.1, () => [1, 2]), /derivative/);
  const seen = []; assert.throws(() => rk4Step([Number.MAX_VALUE], 2, (s) => { seen.push(s[0]); return [s[0]]; }), /intermediate state/);
  assert.deepEqual(seen, [Number.MAX_VALUE]);
  const sparseExtra = []; sparseExtra.length = 1; sparseExtra.note = 1;
  assert.throws(() => rk4Step(sparseExtra, 0.1, () => [1]), /state/);
});
