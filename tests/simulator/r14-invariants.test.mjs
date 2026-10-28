import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';
import { rk4Step } from '../../Build/simulator/rk4.mjs';
import { consumeValidatedTrajectoryArtifact, trajectoryFromValidatedArtifact } from '../../Build/simulator/trajectories.mjs';
import { extendedTrajectoryFromValidatedArtifact } from '../../Build/simulator/extended-templates.mjs';

const cases = JSON.parse(readFileSync(new URL('../../evidence/S10/numerical-invariants/validated-cases.json', import.meta.url), 'utf8'));
const run = (artifact) => ['ramp', 'pendulum'].includes(artifact.spec.template)
  ? extendedTrajectoryFromValidatedArtifact(artifact)
  : trajectoryFromValidatedArtifact(consumeValidatedTrajectoryArtifact(artifact));

// Closed forms are independent of RK4; pendulum uses the declared S08 linear oracle, not sin(theta) dynamics.
function reference(artifact, time) {
  const s = artifact.spec, p = s.parameters, g = s.environment.gravity.value;
  const o = s.placement.origin.value;
  if (s.template === 'pendulum') {
    const length = p.length.value, w = Math.sqrt(g / length);
    const angle = p.release_angle.value * Math.cos(w * time) + p.initial_angular_velocity.value / w * Math.sin(w * time);
    return [o[0] + length * Math.sin(angle), o[1] - length * Math.cos(angle), o[2]];
  }
  if (s.template === 'ramp') {
    const angle = p.incline_angle.value;
    const acceleration = g * (Math.sin(angle) - p.friction_coefficient.value * Math.cos(angle));
    const distance = (p.initial_speed.value + 0.5 * acceleration * time) * time;
    return [o[0] + distance * Math.cos(angle), o[1] - distance * Math.sin(angle), o[2]];
  }
  const vx = p.horizontal_speed?.value ?? 0, vy = p.initial_vertical_velocity?.value ?? 0;
  return [o[0] + vx * time, o[1] + (vy - 0.5 * g * time) * time, o[2]];
}

function errorFor(artifact, samples) {
  const s = artifact.spec, p = s.parameters;
  const scale = s.template === 'pendulum'
    ? p.length.value * Math.hypot(p.release_angle.value, p.initial_angular_velocity.value / Math.sqrt(s.environment.gravity.value / p.length.value))
    : Math.max(...samples.map((sample) => Math.hypot(...reference(artifact, sample.time_s).map((x, i) => x - s.placement.origin.value[i]))));
  let worst = { relativeError: 0, time_s: 0 };
  for (const sample of samples) {
    const expected = reference(artifact, sample.time_s);
    const absolute = Math.hypot(...sample.position_m.map((x, i) => x - expected[i]));
    const relativeError = scale === 0 ? absolute : absolute / scale;
    if (relativeError > worst.relativeError) worst = { relativeError, time_s: sample.time_s };
    assert.equal(sample.step * s.simulation.time_step.value, sample.time_s);
  }
  return worst;
}

for (const [name, { artifact, oracle }] of Object.entries(cases).filter(([name]) => name.startsWith('control-'))) {
  test(`R14 valid-domain control: ${name}`, () => {
    const out = run(artifact), end = out.samples.at(-1), dt = artifact.spec.simulation.time_step.value;
    assert.equal(out.samples.length, Math.round(artifact.spec.simulation.duration.value / dt) + 1);
    assert.deepEqual(reference(artifact, oracle.samples.at(-1).time.value), oracle.samples.at(-1).position.value);
    assert.ok(errorFor(artifact, out.samples).relativeError <= 0.005, JSON.stringify(errorFor(artifact, out.samples)));
    assert.ok(end.position_m.every(Number.isFinite));
    if (['free_fall', 'projectile'].includes(artifact.spec.template)) {
      const g = artifact.spec.environment.gravity.value;
      const expected = (artifact.spec.parameters.initial_vertical_velocity?.value ?? 0) - g * end.time_s;
      assert.ok(Math.abs(end.velocity_m_s[1] - expected) <= Math.abs(expected) * 1e-11 + Number.MIN_VALUE * out.samples.length * 16);
    }
    if (artifact.spec.template === 'pendulum') {
      const origin = artifact.spec.placement.origin.value, length = artifact.spec.parameters.length.value;
      const g = artifact.spec.environment.gravity.value;
      const energy = (sample) => 0.5 * (length * sample.angular_velocity_rad_s) ** 2 + 2 * g * length * Math.sin(sample.angle_rad / 2) ** 2;
      const initialEnergy = energy(out.samples[0]);
      for (const sample of out.samples) {
        const r = sample.position_m.map((x, i) => x - origin[i]);
        assert.ok(Math.abs(Math.hypot(...r) - length) <= 1e-14 * Math.max(1, length));
        assert.ok(Math.abs(r.reduce((sum, x, i) => sum + x * sample.velocity_m_s[i], 0)) <= 1e-14);
        assert.ok(Math.abs(energy(sample) / initialEnergy - 1) <= 1e-7);
      }
    }
  });
}

test('R14 regression: accepted amplitude 0.1 pendulum stays within unchanged 0.005 analytic tolerance over 4 s', () => {
  const { artifact, oracle } = cases['pendulum-amplitude-boundary'];
  const out = run(artifact), worst = errorFor(artifact, out.samples);
  const frozenOracle = oracle.samples.find((sample) => sample.time.value === 3.531);
  assert.deepEqual(reference(artifact, 3.531), frozenOracle.position.value);
  assert.equal(out.analyticComparison.model, 'small-angle-linearized');
  assert.ok(worst.relativeError <= 0.005, JSON.stringify(worst));
});

test('R14 diagnosis: halving pendulum step converges without repairing the model discrepancy', () => {
  const a = run(cases['pendulum-amplitude-boundary'].artifact);
  const b = run(cases['pendulum-amplitude-boundary-half-step'].artifact);
  for (let i = 0; i < a.samples.length; i++) {
    assert.ok(Math.abs(a.samples[i].angle_rad - b.samples[2 * i].angle_rad) < 1e-10);
  }
});

test('R14 regression: actual S08 positive near-friction ramp must not be rejected as stalled', () => {
  const { artifact, oracle } = cases['ramp-positive-near-friction-boundary'];
  assert.ok(oracle.acceleration.value > 0);
  const out = run(artifact);
  assert.ok(out.samples.at(-1).speed_m_s > 0);
});

test('R14 regression: finite RK4 weighted increment must not overflow before multiplication by tiny dt', () => {
  const dt = 2 ** -1030, derivative = 5e307;
  const expected = dt * derivative;
  assert.ok(Number.isFinite(expected) && expected > 0);
  const [observed] = rk4Step([0], dt, () => [derivative]);
  assert.ok(Math.abs(observed / expected - 1) <= 1e-14);
});

for (const name of ['free-fall-large-finite-gravity', 'projectile-large-finite-gravity', 'ramp-large-finite-gravity']) {
  test(`R14 regression: validated finite analytic trajectory remains executable: ${name}`, () => {
    const { artifact, oracle } = cases[name];
    assert.ok(oracle.samples.at(-1).position.value.every(Number.isFinite));
    const out = run(artifact);
    assert.equal(out.samples.length, 9);
    assert.ok(out.samples.every((sample) => sample.position_m.every(Number.isFinite)));
  });
}
