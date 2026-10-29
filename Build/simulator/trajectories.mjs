import { rk4Step } from './rk4.mjs';

const fail = (message) => { throw new TypeError(`INVALID_TRAJECTORY: ${message}`); };
// 'image-derived' (S12c): scale-free params fitted from tracked footage; Gate M NOT_MET, never metres.
export const INPUT_PROVENANCE = Object.freeze(['synthetic', 'image-derived']);
const finite = (value) => typeof value === 'number' && Number.isFinite(value);
const vector3 = (value) => Array.isArray(value) && value.length === 3 && [0, 1, 2].every((i) => Object.prototype.hasOwnProperty.call(value, i) && finite(value[i]));
const trustedArtifacts = new WeakSet();
const integerHorizon = (duration, dt) => {
  const ratio = duration / dt, nearest = Math.round(ratio);
  // Accept only floating-point representation noise; no fractional horizon is silently truncated.
  if (!finite(ratio) || ratio < 0 || Math.abs(ratio - nearest) > Number.EPSILON * Math.max(1, Math.abs(ratio))) fail('S08 duration/time_step must be an integer horizon');
  if (!Number.isSafeInteger(nearest) || nearest > 1_000_000) fail('S08 fixed-step horizon exceeds safe limit');
  return nearest;
};
const freezeDeep = (value) => {
  if (value && typeof value === 'object' && !Object.isFrozen(value)) {
    Object.values(value).forEach(freezeDeep); Object.freeze(value);
  }
  return value;
};

function checked(input) {
  if (!input || typeof input !== 'object') fail('input is required');
  const { initialPosition, initialVelocity, gravity, dt, steps, source, inputProvenance } = input;
  if (!vector3(initialPosition) || !vector3(initialVelocity)) fail('initial position and velocity must be finite 3-vectors');
  if (!finite(gravity) || gravity <= 0) fail('gravity must be finite and positive');
  if (!finite(dt) || dt <= 0) fail('dt must be finite and positive');
  if (!Number.isSafeInteger(steps) || steps < 0 || steps > 1_000_000) fail('steps must be a safe integer in [0, 1000000]');
  if (!finite(dt * steps)) fail('dt multiplied by steps must remain finite');
  if (source !== 'simulated' || !INPUT_PROVENANCE.includes(inputProvenance)) fail('source labels must be explicit simulated/synthetic|image-derived');
  return { initialPosition: [...initialPosition], initialVelocity: [...initialVelocity], gravity, dt, steps, source, inputProvenance };
}

function run(input, stopPlaneY) {
  const spec = checked(input);
  if (stopPlaneY !== undefined && !finite(stopPlaneY)) fail('stopPlaneY must be finite when supplied');
  let state = [...spec.initialPosition, ...spec.initialVelocity];
  const samples = [Object.freeze({ step: 0, time_s: 0, position_m: Object.freeze(state.slice(0, 3)), velocity_m_s: Object.freeze(state.slice(3)) })];
  let crossedAtStep = stopPlaneY !== undefined && state[1] <= stopPlaneY ? 0 : null;
  const stepsToRun = crossedAtStep === 0 ? 0 : spec.steps;
  for (let step = 1; step <= stepsToRun; step += 1) {
    state = rk4Step(state, spec.dt, (s) => [s[3], s[4], s[5], 0, -spec.gravity, 0]);
    const time = step * spec.dt;
    if (!finite(time)) fail('sample time became non-finite');
    const sample = Object.freeze({ step, time_s: time, position_m: Object.freeze(state.slice(0, 3)), velocity_m_s: Object.freeze(state.slice(3)) });
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
    samples: Object.freeze(samples),
    stopPlaneY: stopPlaneY ?? null,
    stop: crossedAtStep === null ? { crossed: false, crossedAtStep: null, crossing: null } : { crossed: true, crossedAtStep, crossing: crossedAtStep === 0 ? 'at_initial_sample' : 'between_samples_or_at_sample' },
  };
  return freezeDeep(output);
}

export function consumeValidatedTrajectoryArtifact(raw) {
  if (!raw || raw.artifact_version !== 's10-validated-setup-v1' || raw.validation !== 'validate_setup' || raw.producer !== 'contracts/experiment/validate_experiment.py') fail('untrusted validated artifact');
  const spec = raw.spec, scene = raw.scene;
  if (!spec || !scene || scene.schema_version !== '1.0.0' || scene.synthetic !== true || spec.scene?.scene_id !== scene.id || spec.scene?.schema_version !== scene.schema_version) fail('S08 synthetic scene mismatch');
  if (!['free_fall', 'projectile'].includes(spec.template)) fail('trajectory template must be free_fall or projectile');
  const gravity = spec.environment?.gravity, direction = spec.environment?.gravity_direction;
  const origin = spec.placement?.origin, parameters = spec.parameters, simulation = spec.simulation;
  if (!finite(gravity?.value) || gravity.value <= 0 || JSON.stringify(direction) !== '[0,-1,0]' || !vector3(origin?.value)) fail('explicit S08 gravity/origin required');
  if (!parameters || !simulation || !finite(simulation.duration?.value) || simulation.duration.value < 0 || !finite(simulation.time_step?.value) || simulation.time_step.value <= 0) fail('explicit S08 duration/time_step required');
  const height = parameters[spec.template === 'free_fall' ? 'drop_height' : 'launch_height'];
  if (!finite(height?.value) || height.value <= 0) fail('explicit stop-plane height required');
  integerHorizon(simulation.duration.value, simulation.time_step.value);
  const artifact = freezeDeep(structuredClone(raw)); trustedArtifacts.add(artifact);
  return artifact;
}

export function trajectoryFromValidatedArtifact(artifact) {
  if (!trustedArtifacts.has(artifact)) fail('artifact must be returned by consumeValidatedTrajectoryArtifact');
  const { spec } = artifact, p = spec.parameters;
  const projectile = spec.template === 'projectile';
  const height = p[projectile ? 'launch_height' : 'drop_height'].value;
  const steps = integerHorizon(spec.simulation.duration.value, spec.simulation.time_step.value);
  return (projectile ? projectileTrajectory : freeFallTrajectory)({
    initialPosition: [...spec.placement.origin.value],
    initialVelocity: projectile ? [p.horizontal_speed.value, 0, 0] : [0, p.initial_vertical_velocity.value, 0],
    gravity: spec.environment.gravity.value, dt: spec.simulation.time_step.value,
    steps,
    stopPlaneY: spec.placement.origin.value[1] - height,
    source: 'simulated', inputProvenance: 'synthetic',
  });
}

export function freeFallTrajectory(input) {
  return run({ ...input, kind: 'free-fall' }, input?.stopPlaneY);
}

export function projectileTrajectory(input) {
  return run({ ...input, kind: 'projectile' }, input?.stopPlaneY);
}
