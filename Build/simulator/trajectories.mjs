import { rk4Step } from './rk4.mjs';

const fail = (message) => { throw new TypeError(`INVALID_TRAJECTORY: ${message}`); };
const finite = (value) => typeof value === 'number' && Number.isFinite(value);
const vector3 = (value) => Array.isArray(value) && value.length === 3 && value.every(finite);

function checked(input) {
  if (!input || typeof input !== 'object') fail('input is required');
  const { initialPosition, initialVelocity, gravity, dt, steps, source, inputProvenance } = input;
  if (!vector3(initialPosition) || !vector3(initialVelocity)) fail('initial position and velocity must be finite 3-vectors');
  if (!finite(gravity) || gravity <= 0) fail('gravity must be finite and positive');
  if (!finite(dt) || dt <= 0) fail('dt must be finite and positive');
  if (!Number.isSafeInteger(steps) || steps < 0 || steps > 1_000_000) fail('steps must be a safe integer in [0, 1000000]');
  if (source !== 'simulated' || inputProvenance !== 'synthetic') fail('source labels must be explicit simulated/synthetic');
  return { initialPosition: [...initialPosition], initialVelocity: [...initialVelocity], gravity, dt, steps, source, inputProvenance };
}

function run(input, stopPlaneY) {
  const spec = checked(input);
  if (stopPlaneY !== undefined && !finite(stopPlaneY)) fail('stopPlaneY must be finite when supplied');
  let state = [...spec.initialPosition, ...spec.initialVelocity];
  const samples = [Object.freeze({ step: 0, time_s: 0, position_m: Object.freeze(state.slice(0, 3)), velocity_m_s: Object.freeze(state.slice(3)) })];
  let crossedAtStep = null;
  for (let step = 1; step <= spec.steps; step += 1) {
    state = rk4Step(state, spec.dt, (s) => [s[3], s[4], s[5], 0, -spec.gravity, 0]);
    const sample = Object.freeze({ step, time_s: step * spec.dt, position_m: Object.freeze(state.slice(0, 3)), velocity_m_s: Object.freeze(state.slice(3)) });
    samples.push(sample);
    // The event is deliberately sample-based: this records a bracket, never a fabricated exact hit.
    if (stopPlaneY !== undefined && state[1] <= stopPlaneY) { crossedAtStep = step; break; }
  }
  const output = {
    kind: input.kind,
    source: spec.source,
    inputProvenance: spec.inputProvenance,
    integrator: 'rk4-fixed-step',
    dt_s: spec.dt,
    requestedSteps: spec.steps,
    samples,
    stopPlaneY: stopPlaneY ?? null,
    stop: crossedAtStep === null ? { crossed: false, crossedAtStep: null, crossing: null } : { crossed: true, crossedAtStep, crossing: 'between_samples_or_at_sample' },
  };
  return Object.freeze(output);
}

export function freeFallTrajectory(input) {
  return run({ ...input, kind: 'free-fall' }, input?.stopPlaneY);
}

export function projectileTrajectory(input) {
  return run({ ...input, kind: 'projectile' }, input?.stopPlaneY);
}
