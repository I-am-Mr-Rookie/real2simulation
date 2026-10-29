import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';
import { rk4Step } from '../../Build/simulator/rk4.mjs';
import { consumeValidatedTrajectoryArtifact, trajectoryFromValidatedArtifact } from '../../Build/simulator/trajectories.mjs';
import { extendedTrajectoryFromValidatedArtifact, pendulumTrajectory, rampTrajectory } from '../../Build/simulator/extended-templates.mjs';

const cases = JSON.parse(readFileSync(new URL('../../evidence/S10/numerical-invariants/validated-cases.json', import.meta.url), 'utf8'));
const run = (artifact) => ['ramp', 'pendulum'].includes(artifact.spec.template)
  ? extendedTrajectoryFromValidatedArtifact(artifact)
  : trajectoryFromValidatedArtifact(consumeValidatedTrajectoryArtifact(artifact));

// Independent closed forms: the frozen Python S08 samples anchor these formulas.
function reference(artifact, time) {
  const s = artifact.spec, p = s.parameters, g = s.environment.gravity.value, o = s.placement.origin.value;
  if (s.template === 'pendulum') {
    const length = p.length.value, w = Math.sqrt(g / length);
    const angle = p.release_angle.value * Math.cos(w * time) + p.initial_angular_velocity.value / w * Math.sin(w * time);
    return [o[0] + length * Math.sin(angle), o[1] - length * Math.cos(angle), o[2]];
  }
  if (s.template === 'ramp') {
    const angle = p.incline_angle.value, a = g * (Math.sin(angle) - p.friction_coefficient.value * Math.cos(angle));
    const distance = (p.initial_speed.value + 0.5 * a * time) * time;
    return [o[0] + distance * Math.cos(angle), o[1] - distance * Math.sin(angle), o[2]];
  }
  return [o[0] + (p.horizontal_speed?.value ?? 0) * time,
    o[1] + ((p.initial_vertical_velocity?.value ?? 0) - 0.5 * g * time) * time, o[2]];
}

for (const [name, { artifact, oracle }] of Object.entries(cases)) {
  test(`R14 recovery: unchanged all-sample 0.005 oracle: ${name}`, () => {
    const out = run(artifact), s = artifact.spec, p = s.parameters;
    for (const sample of oracle.samples) {
      assert.deepEqual(reference(artifact, sample.time.value), sample.position.value);
    }
    const scale = s.template === 'pendulum'
      ? p.length.value * Math.hypot(p.release_angle.value, p.initial_angular_velocity.value / Math.sqrt(s.environment.gravity.value / p.length.value))
      : Math.max(...out.samples.map((sample) => Math.hypot(...reference(artifact, sample.time_s).map((x, i) => x - s.placement.origin.value[i]))));
    let worst = 0, linearEnergyDrift = 0, nonlinearEnergyDrift = 0;
    const length = p.length?.value, g = s.environment.gravity.value;
    const linearEnergy = (v) => 0.5 * (length * v.angular_velocity_rad_s) ** 2 + 0.5 * g * length * v.angle_rad ** 2;
    const nonlinearEnergy = (v) => 0.5 * (length * v.angular_velocity_rad_s) ** 2 + 2 * g * length * Math.sin(v.angle_rad / 2) ** 2;
    for (const sample of out.samples) {
      const absoluteError = Math.hypot(...sample.position_m.map((x, i) => x - reference(artifact, sample.time_s)[i]));
      worst = Math.max(worst, scale === 0 ? absoluteError : absoluteError / scale);
      assert.equal(sample.time_s, sample.step * s.simulation.time_step.value);
      if (s.template === 'pendulum') {
        assert.equal(out.analyticComparison.model, 'small-angle-linearized');
        const radius = sample.position_m.map((x, i) => x - s.placement.origin.value[i]);
        assert.ok(Math.abs(Math.hypot(...radius) - length) <= 1e-14 * Math.max(1, length));
        assert.ok(Math.abs(radius.reduce((sum, x, i) => sum + x * sample.velocity_m_s[i], 0)) <= 1e-14);
        linearEnergyDrift = Math.max(linearEnergyDrift, Math.abs(linearEnergy(sample) / linearEnergy(out.samples[0]) - 1));
        nonlinearEnergyDrift = Math.max(nonlinearEnergyDrift, Math.abs(nonlinearEnergy(sample) / nonlinearEnergy(out.samples[0]) - 1));
      }
    }
    assert.ok(worst <= 0.005, `${name}: ${worst}`);
    if (s.template === 'pendulum') assert.ok(linearEnergyDrift <= 1e-7, `${name}: linear energy ${linearEnergyDrift}`);
    console.log(JSON.stringify({ name, samples: out.samples.length, maxRelativePositionError: worst,
      ...(s.template === 'pendulum' ? { linearEnergyDrift, nonlinearEnergyDrift } : {}) }));
  });
}

test('R14 RK4: constant finite derivatives across large, tiny and subnormal scales', () => {
  for (const [dt, derivative] of [[2 ** -1030, 5e307], [Number.MIN_VALUE, 5e307],
    [Number.MIN_VALUE, 1], [2e307, Number.MIN_VALUE], [1, 1e308], [0.5, -1e308]]) {
    const expected = dt * derivative;
    const [actual] = rk4Step([0], dt, () => [derivative]);
    assert.ok(Number.isFinite(actual));
    assert.ok(Math.abs(actual - expected) <= Math.abs(expected) * 1e-14,
      JSON.stringify({ dt, derivative, expected, actual }));
    assert.notEqual(actual, 0);
  }
});

test('R14 RK4: mixed-sign stages and finite weighted increment despite dt*largestSlope overflow', () => {
  let stage = 0;
  const max = Number.MAX_VALUE;
  const [mixed] = rk4Step([0], 1, () => [[max, -max, -max, max][stage++]]);
  assert.ok(Math.abs(mixed / (-max / 3) - 1) <= 1e-14);
  stage = 0;
  const [last] = rk4Step([0], 4, () => [[0, 0, 0, 1e308][stage++]]);
  assert.ok(Math.abs(last / (1e308 * (4 / 6)) - 1) <= 1e-14);
});

test('R15 RK4: finite half-stage survives overflow of the unhalved product', () => {
  for (const slope of [-1e308, 1e308]) {
    const seen = [];
    const result = rk4Step([0, 0], 3, ([time, value]) => {
      seen.push([time, value]);
      return [1, time === 0 ? slope : 0];
    });
    assert.deepEqual(seen, [[0, 0], [1.5, 1.5 * slope], [1.5, 0], [3, 0]]);
    assert.equal(result[0], 3);
    assert.ok(Math.abs(result[1] / (slope / 2) - 1) <= 1e-14);
  }
});

test('R14 RK4: actual stage/derivative/result checks are preserved', () => {
  let calls = 0;
  assert.throws(() => rk4Step([0], 4, () => { calls++; return [1e308]; }), /intermediate state/);
  assert.equal(calls, 1);
  for (let invalidStage = 0; invalidStage < 4; invalidStage++) {
    calls = 0;
    assert.throws(() => rk4Step([0], 0.01, () => [calls++ === invalidStage ? Infinity : 1]), /invalid derivative/);
    assert.equal(calls, invalidStage + 1);
  }
  calls = 0;
  assert.throws(() => rk4Step([Number.MAX_VALUE], 4, () => [[0, 0, 0, Number.MAX_VALUE][calls++]]), /state became non-finite/);
  assert.equal(calls, 4);
  assert.deepEqual(rk4Step([7, -2], 0.1, () => [0, 0]), [7, -2]);
});

test('R14 ramp: positive cancellation result matches S08 and zero/negative are still rejected', () => {
  const { artifact, oracle } = cases['ramp-positive-near-friction-boundary'];
  const out = run(artifact), last = out.samples.at(-1);
  assert.ok(last.speed_m_s > 0);
  assert.ok(Math.abs(last.speed_m_s / (oracle.acceleration.value * last.time_s) - 1) <= 1e-12);
  const base = { origin: [0, 0, 0], gravity: 1.62, length: 1, inclineAngle: 0.7,
    initialSpeed: 0, dt: 0.001, steps: 200, source: 'simulated', inputProvenance: 'synthetic' };
  const threshold = Math.sin(base.inclineAngle) / Math.cos(base.inclineAngle);
  for (const mu of [threshold, threshold + Number.EPSILON]) {
    assert.throws(() => rampTrajectory({ ...base, frictionCoefficient: mu }), /acceleration must be positive/);
  }
});

test('R14 ramp: large finite endpoint bracket no longer fails from an unscaled RK4 sum', () => {
  const out = rampTrajectory({ origin: [Number.MAX_VALUE, 0, 0], length: 2, gravity: 8,
    inclineAngle: 0.5, frictionCoefficient: 0, initialSpeed: Number.MAX_VALUE / 2,
    dt: 0.001, steps: 1, source: 'simulated', inputProvenance: 'synthetic' });
  assert.equal(out.stop.reached, true);
  assert.ok(Number.isFinite(out.stop.bracket.after.distance_m));
  assert.ok(Number.isFinite(out.stop.bracket.after.speed_m_s));
});

test('R14 model: linear dynamics across signed phases, velocities, scales and long horizons', () => {
  for (const initialAngle of [-0.1, -0.04, 0, 0.04, 0.1]) {
    for (const [gravity, length] of [[1.62, 2], [9.81, 1], [20, 0.2]]) {
      const omega = Math.sqrt(gravity / length), initialAngularVelocity = initialAngle === 0 ? 0.08 * omega : 0;
      const out = pendulumTrajectory({ origin: [0, 2, 0], length, gravity, initialAngle,
        initialAngularVelocity, dt: 0.001, steps: 20000, source: 'simulated', inputProvenance: 'synthetic' });
      assert.equal(out.analyticComparison.model, 'small-angle-linearized');
      for (const sample of out.samples) {
        const expected = initialAngle * Math.cos(omega * sample.time_s) + initialAngularVelocity / omega * Math.sin(omega * sample.time_s);
        assert.ok(Math.abs(sample.angle_rad - expected) / 0.1 <= 0.005);
      }
    }
  }
});

test('R14 model: nonlinear-only remains nonlinear and small-angle equilibrium remains supported', () => {
  const base = { origin: [0, 2, 0], length: 1, gravity: 9.81, dt: 0.001, steps: 4000,
    initialAngularVelocity: 0, source: 'simulated', inputProvenance: 'synthetic' };
  const still = pendulumTrajectory({ ...base, initialAngle: 0 });
  assert.ok(still.samples.every((s) => s.angle_rad === 0 && s.angular_velocity_rad_s === 0));
  const nonlinear = pendulumTrajectory({ ...base, initialAngle: 1.1 });
  assert.equal(nonlinear.analyticComparison.model, 'nonlinear-only');
  const energy = (s) => 0.5 * s.angular_velocity_rad_s ** 2 + 2 * base.gravity * Math.sin(s.angle_rad / 2) ** 2;
  for (const sample of nonlinear.samples) assert.ok(Math.abs(energy(sample) / energy(nonlinear.samples[0]) - 1) <= 1e-7);
});

test('R15 model: linear energy is conserved; nonlinear-energy change has the independently predicted magnitude', () => {
  for (const amplitude of [-0.1, -0.02, 0.02, 0.1]) {
    for (const [gravity, length] of [[1.62, 2], [9.81, 1]]) {
      const frequency = Math.sqrt(gravity / length), quarterSteps = 256;
      const out = pendulumTrajectory({ origin: [0, 2, 0], length, gravity,
        initialAngle: amplitude, initialAngularVelocity: 0,
        dt: Math.PI / (2 * frequency * quarterSteps), steps: 4 * quarterSteps,
        source: 'simulated', inputProvenance: 'synthetic' });
      assert.equal(out.analyticComparison.model, 'small-angle-linearized');
      // theta'' = -w^2 theta implies theta^2 + (theta'/w)^2 = amplitude^2.
      for (const sample of out.samples) {
        const invariant = sample.angle_rad ** 2 + (sample.angular_velocity_rad_s / frequency) ** 2;
        assert.ok(Math.abs(invariant / amplitude ** 2 - 1) <= 1e-9);
      }
      const nonlinearEnergy = (sample) => 0.5 * (length * sample.angular_velocity_rad_s) ** 2
        + 2 * gravity * length * Math.sin(sample.angle_rad / 2) ** 2;
      const observed = nonlinearEnergy(out.samples[quarterSteps]) / nonlinearEnergy(out.samples[0]) - 1;
      // At a quarter-period theta=0, theta'=-w*A, so E_nonlin/E_initial=A^2/(4*sin^2(A/2)).
      const predicted = amplitude ** 2 / (4 * Math.sin(amplitude / 2) ** 2) - 1;
      assert.ok(predicted > 1e-7, 'the frozen nonlinear diagnostic must disagree with this model');
      assert.ok(Math.abs(observed - predicted) <= 1e-9, JSON.stringify({ amplitude, observed, predicted }));
    }
  }
});
