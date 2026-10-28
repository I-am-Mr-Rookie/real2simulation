import assert from 'node:assert/strict';
import test from 'node:test';
import { freeFallTrajectory, projectileTrajectory } from '../../Build/simulator/trajectories.mjs';

const base = { initialPosition: [0, 2, 0], initialVelocity: [0, 0, 0], gravity: 9.81, dt: 0.01, steps: 100, source: 'simulated', inputProvenance: 'synthetic' };

test('free fall uses fixed-step RK4 and matches the authoritative analytic reference', () => {
  const out = freeFallTrajectory(base);
  const last = out.samples.at(-1);
  assert.equal(out.integrator, 'rk4-fixed-step');
  assert.equal(out.samples.length, 101);
  assert.ok(Math.abs(last.position_m[1] - (2 - 0.5 * 9.81)) < 1e-12);
  assert.ok(Math.abs(last.velocity_m_s[1] + 9.81) < 1e-12);
  assert.equal(out.source, 'simulated');
  assert.equal(out.inputProvenance, 'synthetic');
});

test('projectile preserves horizontal motion and reports a sampled stop-plane bracket', () => {
  const out = projectileTrajectory({ ...base, initialPosition: [0, 1, 0], initialVelocity: [2, 0, 0], steps: 1000, stopPlaneY: 0 });
  assert.equal(out.stop.crossed, true);
  assert.equal(out.stop.crossing, 'between_samples_or_at_sample');
  const hit = out.samples.at(-1);
  assert.ok(hit.position_m[1] <= 0);
  assert.ok(Math.abs(hit.position_m[0] - 2 * hit.time_s) < 1e-12);
});

test('rejects missing provenance and hidden numeric defaults', () => {
  assert.throws(() => freeFallTrajectory({ ...base, source: undefined }), /simulated\/synthetic/);
  assert.throws(() => freeFallTrajectory({ ...base, dt: undefined }), /dt/);
  assert.throws(() => freeFallTrajectory({ ...base, steps: 1.5 }), /steps/);
});

test('is deterministic, finite, and does not mutate caller inputs', () => {
  const input = { ...base, initialPosition: [...base.initialPosition], initialVelocity: [...base.initialVelocity] };
  const before = structuredClone(input);
  const a = freeFallTrajectory(input);
  const b = freeFallTrajectory(input);
  assert.deepEqual(input, before);
  assert.deepEqual(a, b);
  assert.ok(a.samples.every((s) => [s.time_s, ...s.position_m, ...s.velocity_m_s].every(Number.isFinite)));
  assert.ok(Object.isFrozen(a.samples.at(0).position_m));
});
