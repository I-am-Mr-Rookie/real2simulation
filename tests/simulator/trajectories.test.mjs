import assert from 'node:assert/strict';
import { cp, mkdtemp, readFile, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { fileURLToPath } from 'node:url';
import { join } from 'node:path';
import test from 'node:test';

// The child owns no RK4 copy. Stage the read-only peer module outside the worktree
// so this test exercises the real import seam without changing the checkout.
const peer = 'C:/Users/HP/.codex/worktrees/swarm-s10-simulator/2026-10-26 - Meta Global AI Developer Hackathon/Build/simulator/rk4.mjs';
const staged = await mkdtemp(join(tmpdir(), 's10-trajectories-'));
await cp(fileURLToPath(new URL('../../Build/simulator/trajectories.mjs', import.meta.url)), join(staged, 'trajectories.mjs'));
await cp(peer, join(staged, 'rk4.mjs'));
const { freeFallTrajectory, projectileTrajectory, consumeValidatedTrajectoryArtifact, trajectoryFromValidatedArtifact } = await import(`file://${join(staged, 'trajectories.mjs').replaceAll('\\', '/')}`);
test.after(async () => rm(staged, { recursive: true, force: true }));

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
  assert.throws(() => freeFallTrajectory({ ...base, dt: Number.MAX_VALUE, steps: 2 }), /multiplied/);
  const sparse = [0, 0, 0]; delete sparse[1];
  assert.throws(() => freeFallTrajectory({ ...base, initialPosition: sparse }), /3-vectors/);
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
  assert.ok(Object.isFrozen(a.samples));
});

test('reports an already-crossed plane without advancing the integrator', () => {
  const out = freeFallTrajectory({ ...base, initialPosition: [0, -1, 0], steps: 4, stopPlaneY: 0 });
  assert.deepEqual(out.stop, { crossed: true, crossedAtStep: 0, crossing: 'at_initial_sample' });
  assert.equal(out.samples.length, 1);
});

test('accepts only the validated S08 transport and maps explicit template quantities', () => {
  const artifact = { artifact_version: 's10-validated-setup-v1', validation: 'validate_setup', producer: 'contracts/experiment/validate_experiment.py', spec: {
    template: 'projectile', scene: { scene_id: 'room', schema_version: '1.0.0' },
    environment: { gravity: { value: 9.81 }, gravity_direction: [0, -1, 0] },
    placement: { origin: { value: [0, 2, 0] } },
    parameters: { launch_height: { value: 2 }, horizontal_speed: { value: 3 } },
    simulation: { duration: { value: 1 }, time_step: { value: 0.01 } },
  }, scene: { id: 'room', schema_version: '1.0.0' } };
  const trusted = consumeValidatedTrajectoryArtifact(artifact);
  const out = trajectoryFromValidatedArtifact(trusted);
  assert.equal(out.kind, 'projectile'); assert.equal(out.requestedSteps, 100); assert.equal(out.samples.length, 65);
  assert.throws(() => trajectoryFromValidatedArtifact(structuredClone(trusted)), /returned by consume/);
  assert.throws(() => consumeValidatedTrajectoryArtifact({ ...artifact, producer: 'caller' }), /untrusted/);
});
