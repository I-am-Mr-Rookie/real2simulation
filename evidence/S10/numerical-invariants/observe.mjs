import { readFileSync } from 'node:fs';
import { rk4Step } from '../../../Build/simulator/rk4.mjs';
import { consumeValidatedTrajectoryArtifact, trajectoryFromValidatedArtifact } from '../../../Build/simulator/trajectories.mjs';
import { extendedTrajectoryFromValidatedArtifact } from '../../../Build/simulator/extended-templates.mjs';

const cases = JSON.parse(readFileSync(new URL('./validated-cases.json', import.meta.url), 'utf8'));
const rows = [];
for (const [name, { artifact, oracle }] of Object.entries(cases)) {
  const spec = artifact.spec, p = spec.parameters;
  const row = { name, template: spec.template, validated: artifact.validation, oracle: oracle.method };
  try {
    const out = ['ramp', 'pendulum'].includes(spec.template)
      ? extendedTrajectoryFromValidatedArtifact(artifact)
      : trajectoryFromValidatedArtifact(consumeValidatedTrajectoryArtifact(artifact));
    Object.assign(row, { status: 'returned', samples: out.samples.length, endpoint: out.samples.at(-1), oracleEndpoint: oracle.samples.at(-1) });
    if (spec.template === 'pendulum') {
      const length = p.length.value, w = Math.sqrt(spec.environment.gravity.value / length);
      const amplitude = Math.hypot(p.release_angle.value, p.initial_angular_velocity.value / w);
      const origin = spec.placement.origin.value;
      let worst = { relative_error: 0, time_s: 0 };
      for (const sample of out.samples) {
        const angle = p.release_angle.value * Math.cos(w * sample.time_s) + p.initial_angular_velocity.value / w * Math.sin(w * sample.time_s);
        const expected = [origin[0] + length * Math.sin(angle), origin[1] - length * Math.cos(angle), origin[2]];
        const error = Math.hypot(...sample.position_m.map((x, i) => x - expected[i])) / (length * amplitude);
        if (error > worst.relative_error) worst = { relative_error: error, time_s: sample.time_s, observed_position_m: sample.position_m, expected_position_m: expected };
      }
      row.worst = worst;
    }
  } catch (error) {
    Object.assign(row, { status: 'rejected', error: error.message, oracleEndpoint: oracle.samples.at(-1) });
  }
  rows.push(row);
}

// Energy quadrature after theta=2 asin(sin(A/2) sin(u)); no time-step integrator.
const amplitude = 0.1, k = Math.sin(amplitude / 2), panels = 8192;
const h = Math.PI / 2 / panels;
const f = (u) => 1 / Math.sqrt(1 - (k * Math.sin(u)) ** 2);
let sum = f(0) + f(Math.PI / 2);
for (let i = 1; i < panels; i++) sum += (i % 2 ? 4 : 2) * f(i * h);
const nonlinearPeriod_s = 4 / Math.sqrt(9.81) * h / 3 * sum;
const linearPeriod_s = 2 * Math.PI / Math.sqrt(9.81);
const dt = 2 ** -1030, derivative = 5e307;
const scalar = { input: { state: [0], dt, derivative }, independent_expected: dt * derivative };
try { scalar.observed = rk4Step([0], dt, () => [derivative]); }
catch (error) { scalar.error = error.message; }
console.log(JSON.stringify({ threshold: 0.005, cases: rows, scalarRK4: scalar,
  pendulumPeriod: { derivation: 'nonlinear energy integral; composite Simpson, 8192 panels', linearPeriod_s, nonlinearPeriod_s } }, null, 2));
