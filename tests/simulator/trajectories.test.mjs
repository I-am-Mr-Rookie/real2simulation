import assert from 'node:assert/strict';
import { rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { spawnSync } from 'node:child_process';
import test from 'node:test';
import { freeFallTrajectory, projectileTrajectory, consumeValidatedTrajectoryArtifact, trajectoryFromValidatedArtifact } from '../../Build/simulator/trajectories.mjs';

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
  const root = process.cwd();
  const d = join(tmpdir(), `s10-export-${process.pid}`);
  const code = `import sys,json,shutil; from pathlib import Path; root=Path(sys.argv[2]); sys.path[:0]=[str(root),str(root/'tests/spec')]; from test_setup_validation import setup,BUNDLE; from Build.simulator.export_validated_setup import export; d=Path(sys.argv[1]); d.mkdir(parents=True,exist_ok=True); spec,scene=setup('free_fall'); (d/'spec.json').write_text(json.dumps(spec)); (d/'scene.json').write_text(json.dumps(scene)); shutil.copy(BUNDLE/'points.ply', d/'points.ply'); print(json.dumps(export(d/'spec.json', d/'scene.json'))) `;
  const made = spawnSync('python', ['-c', code, d, root], { encoding: 'utf8' });
  assert.equal(made.status, 0, made.stderr);
  const trusted = consumeValidatedTrajectoryArtifact(JSON.parse(made.stdout));
  const out = trajectoryFromValidatedArtifact(trusted);
  assert.equal(out.kind, 'free-fall'); assert.equal(out.source, 'simulated'); assert.equal(out.inputProvenance, 'synthetic');
  assert.ok(out.samples.length > 1);
  assert.throws(() => { trusted.spec.template = 'projectile'; }, /read only|Cannot assign|frozen/i);
  assert.throws(() => trajectoryFromValidatedArtifact(structuredClone(trusted)), /returned by consume/);
  rmSync(d, { recursive: true, force: true });
});
