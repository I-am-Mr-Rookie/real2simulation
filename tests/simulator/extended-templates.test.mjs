import assert from 'node:assert/strict';
import { mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { spawnSync } from 'node:child_process';
import test from 'node:test';
import { rampTrajectory, pendulumTrajectory, extendedTrajectoryFromValidatedArtifact } from '../../Build/simulator/extended-templates.mjs';

const ramp = { origin: [0, 1, 0], length: 2, inclineAngle: 0.5, frictionCoefficient: 0, initialSpeed: 1, gravity: 8, dt: 0.001, steps: 500, source: 'simulated', inputProvenance: 'synthetic' };
const pendulum = { origin: [0, 0, 0], length: 1, initialAngle: 0.04, initialAngularVelocity: 0, gravity: 9.81, dt: 0.001, steps: 1000, source: 'simulated', inputProvenance: 'synthetic' };

test('ramp uses signed fixed-step dynamics and exposes analytic comparison inputs', () => {
  const out = rampTrajectory(ramp), end = out.samples.at(-1);
  const a = ramp.gravity * Math.sin(ramp.inclineAngle);
  assert.equal(out.kind, 'ramp');
  assert.ok(Math.abs(end.distance_m - (ramp.initialSpeed * 0.5 + 0.5 * a * 0.5 ** 2)) < 1e-10);
  assert.ok(Math.abs(end.speed_m_s - (ramp.initialSpeed + a * 0.5)) < 1e-10);
  assert.equal(out.analyticComparison.inputs.friction_coefficient, 0);
});

test('ramp stops at the first endpoint crossing and rejects unsupported stall/coast regimes', () => {
  const out = rampTrajectory({ ...ramp, length: 1, steps: 5000 });
  assert.equal(out.stop.reached, true);
  assert.equal(out.stop.crossing, 'sampled_endpoint_bracket');
  assert.ok(out.samples.at(-1).distance_m < 1);
  assert.ok(out.stop.bracket.after.distance_m >= 1);
  assert.throws(() => rampTrajectory({ ...ramp, frictionCoefficient: 1 }), /positive|coasting|stalling/);
});

test('pendulum matches the small-angle analytic comparison and maps geometry', () => {
  const out = pendulumTrajectory(pendulum), end = out.samples.at(-1), w = Math.sqrt(pendulum.gravity / pendulum.length), t = 1;
  assert.equal(out.analyticComparison.model, 'small-angle-linearized');
  assert.ok(Math.abs(end.angle_rad - pendulum.initialAngle * Math.cos(w * t)) < 2e-7);
  assert.deepEqual(out.samples[0].position_m, [Math.sin(pendulum.initialAngle), -Math.cos(pendulum.initialAngle), 0]);
});

test('nonlinear pendulum converges and conserves energy', () => {
  const coarse = pendulumTrajectory({ ...pendulum, initialAngle: 1.1, dt: 0.01, steps: 1000 });
  const fine = pendulumTrajectory({ ...pendulum, initialAngle: 1.1, dt: 0.0025, steps: 4000 });
  assert.equal(coarse.analyticComparison.model, 'nonlinear-only');
  const energy = (s) => 0.5 * pendulum.length ** 2 * s.angular_velocity_rad_s ** 2 + pendulum.gravity * pendulum.length * (1 - Math.cos(s.angle_rad));
  assert.ok(Math.abs(energy(coarse.samples.at(-1)) - energy(coarse.samples[0])) < 1e-5);
  assert.ok(Math.abs(coarse.samples.at(-1).angle_rad - fine.samples.at(-1).angle_rad) < 1e-4);
});

test('zero horizon is one immutable sample; inputs remain unchanged and deterministic', () => {
  const input = { ...ramp, origin: [...ramp.origin], steps: 0 }, before = structuredClone(input);
  const a = rampTrajectory(input), b = rampTrajectory(input);
  assert.deepEqual(a, b); assert.deepEqual(input, before); assert.equal(a.samples.length, 1);
  assert.ok(Object.isFrozen(a)); assert.ok(Object.isFrozen(a.samples)); assert.ok(Object.isFrozen(a.samples[0].position_m));
});

test('rejects sparse, nonfinite, overflow, and hidden-default inputs', () => {
  const sparse = [0, 0, 0]; delete sparse[1];
  assert.throws(() => rampTrajectory({ ...ramp, origin: sparse }), /origin/);
  assert.throws(() => rampTrajectory({ ...ramp, gravity: Infinity }), /gravity/);
  assert.throws(() => rampTrajectory({ ...ramp, dt: Number.MAX_VALUE, steps: 2 }), /steps/);
  assert.throws(() => rampTrajectory({ ...ramp, source: undefined }), /labels/);
  assert.throws(() => pendulumTrajectory({ ...pendulum, initialAngle: 4 }), /initialAngle/);
  // Keep the endpoint beyond this step so the test checks actual position overflow, not an unscaled RK4 sum.
  assert.throws(() => rampTrajectory({ ...ramp, length: Number.MAX_VALUE, origin: [Number.MAX_VALUE, 0, 0], initialSpeed: Number.MAX_VALUE / 2, steps: 1 }), /position|non-finite/);
});

test('consumes actual Python validate_setup export for both extended templates', () => {
  const root = process.cwd();
  const code = `import sys,json,shutil; from pathlib import Path; root=Path(sys.argv[2]); sys.path[:0]=[str(root),str(root/'tests/spec')]; from test_setup_validation import setup,BUNDLE; from Build.simulator.export_validated_setup import export; d=Path(sys.argv[1]); spec,scene=setup(sys.argv[3]); (d/'spec.json').write_text(json.dumps(spec)); (d/'scene.json').write_text(json.dumps(scene)); shutil.copy(BUNDLE/'points.ply', d/'points.ply'); print(json.dumps(export(d/'spec.json', d/'scene.json'))) `;
  for (const kind of ['ramp', 'pendulum']) {
    const d = mkdtempSync(join(tmpdir(), `s10e-${kind}-`));
    const made = spawnSync('python', ['-c', code, d, root, kind], { encoding: 'utf8' });
    assert.equal(made.status, 0, made.stderr);
    const out = extendedTrajectoryFromValidatedArtifact(JSON.parse(made.stdout));
    assert.equal(out.kind, kind); assert.equal(out.source, 'simulated'); assert.ok(out.samples.length > 1);
    rmSync(d, { recursive: true, force: true });
  }
});

