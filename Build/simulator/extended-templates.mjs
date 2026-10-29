// S10e: synthetic ramp and pendulum trajectories on the accepted fixed-step RK4 core.
import { rk4Step } from './rk4.mjs';

const fail = (message) => { throw new TypeError(`INVALID_EXTENDED_TEMPLATE: ${message}`); };
const finite = (value) => typeof value === 'number' && Number.isFinite(value);
const dense = (value, length) => Array.isArray(value) && value.length === length && Array.from({ length }, (_, i) => Object.hasOwn(value, i) && finite(value[i])).every(Boolean);
const integerHorizon = (duration, dt) => {
  const ratio = duration / dt, steps = Math.round(ratio);
  if (!finite(duration) || duration < 0 || !finite(dt) || dt <= 0 || !finite(ratio) || Math.abs(ratio - steps) > Number.EPSILON * Math.max(1, Math.abs(ratio)) || !Number.isSafeInteger(steps) || steps > 1_000_000) fail('duration/time_step must be a finite integer horizon');
  return steps;
};
const quantity = (value, name) => {
  if (!value || !finite(value.value)) fail(`${name} quantity must be finite`);
  return value.value;
};
const freeze = (value) => {
  if (value && typeof value === 'object' && !Object.isFrozen(value)) { Object.values(value).forEach(freeze); Object.freeze(value); }
  return value;
};
const finiteVector = (value, label) => {
  if (!dense(value, 3)) fail(`${label} became non-finite`);
  return Object.freeze(value);
};
const checked = (input, kind) => {
  if (!input || typeof input !== 'object') fail('input is required');
  const required = kind === 'ramp'
    ? ['length', 'inclineAngle', 'frictionCoefficient', 'initialSpeed', 'gravity']
    : ['length', 'initialAngle', 'initialAngularVelocity', 'gravity'];
  required.forEach((key) => { if (!finite(input[key])) fail(`${key} must be finite`); });
  if (input.length <= 0 || input.gravity <= 0 || input.dt <= 0 || !finite(input.dt)) fail('length, gravity, and dt must be positive');
  if (!Number.isSafeInteger(input.steps) || input.steps < 0 || input.steps > 1_000_000 || !finite(input.dt * input.steps)) fail('steps must be a safe finite integer');
  if (kind === 'ramp' && (input.inclineAngle <= 0 || input.inclineAngle >= Math.PI / 2 || input.frictionCoefficient < 0 || input.initialSpeed < 0)) fail('ramp parameters are outside the S08 domain');
  if (kind === 'pendulum' && (input.initialAngle < -Math.PI || input.initialAngle > Math.PI)) fail('initialAngle is outside the S08 domain');
  if (input.source !== 'simulated' || input.inputProvenance !== 'synthetic') fail('source labels must be explicit simulated/synthetic');
  if (!dense(input.origin, 3)) fail('origin must be a finite dense 3-vector');
  return { ...input, origin: [...input.origin] };
};

function sampleFor(spec, kind, state, step) {
  const time = step * spec.dt;
  if (!finite(time)) fail('sample time became non-finite');
  if (kind === 'ramp') {
    const [distance, speed] = state;
    return Object.freeze({ step, time_s: time, distance_m: distance, speed_m_s: speed, position_m: finiteVector([spec.origin[0] + distance * Math.cos(spec.inclineAngle), spec.origin[1] - distance * Math.sin(spec.inclineAngle), spec.origin[2]], 'ramp position'), velocity_m_s: finiteVector([speed * Math.cos(spec.inclineAngle), -speed * Math.sin(spec.inclineAngle), 0], 'ramp velocity') });
  }
  const [angle, angularVelocity] = state;
  return Object.freeze({ step, time_s: time, angle_rad: angle, angular_velocity_rad_s: angularVelocity, position_m: finiteVector([spec.origin[0] + spec.length * Math.sin(angle), spec.origin[1] - spec.length * Math.cos(angle), spec.origin[2]], 'pendulum position'), velocity_m_s: finiteVector([spec.length * Math.cos(angle) * angularVelocity, spec.length * Math.sin(angle) * angularVelocity, 0], 'pendulum velocity') });
}

function samplesFor(spec, kind, acceleration, endpoint) {
  const state0 = kind === 'ramp' ? [0, spec.initialSpeed] : [spec.initialAngle, spec.initialAngularVelocity];
  let state = [...state0];
  const samples = [];
  samples.push(sampleFor(spec, kind, state, 0));
  let stop = { reached: false, bracket: null };
  for (let step = 1; step <= spec.steps; step += 1) {
    const previous = state;
    state = rk4Step(state, spec.dt, acceleration);
    if (endpoint && state[0] >= endpoint) {
      stop = { reached: true, bracket: { before: sampleFor(spec, kind, previous, step - 1), after: { step, time_s: step * spec.dt, distance_m: state[0], speed_m_s: state[1] } } };
      break;
    }
    samples.push(sampleFor(spec, kind, state, step));
  }
  return Object.freeze({ samples: Object.freeze(samples), stop });
}

export function rampTrajectory(input) {
  const spec = checked(input, 'ramp');
  const accelerationValue = spec.gravity * (Math.sin(spec.inclineAngle) - spec.frictionCoefficient * Math.cos(spec.inclineAngle));
  if (!(accelerationValue > 0)) fail('ramp acceleration must be positive; S08 does not support coasting, stalling, or static-friction stick/slip');
  const acceleration = (state) => {
    return [state[1], accelerationValue];
  };
  const run = samplesFor(spec, 'ramp', acceleration, spec.length);
  const reached = run.stop.reached;
  return freeze({ kind: 'ramp', source: spec.source, inputProvenance: spec.inputProvenance, integrator: 'rk4-fixed-step', dt_s: spec.dt, requestedSteps: spec.steps, units: { time: 's', distance: 'm', speed: 'm/s', position: 'm', velocity: 'm/s', acceleration: 'm/s^2', angle: 'rad' }, analyticComparison: { model: 'constant-positive-acceleration-until-length', inputs: { gravity_m_s2: spec.gravity, incline_angle_rad: spec.inclineAngle, friction_coefficient: spec.frictionCoefficient, initial_speed_m_s: spec.initialSpeed } }, stop: reached ? { reached: true, crossing: 'sampled_endpoint_bracket', bracket: run.stop.bracket } : { reached: false, crossing: null }, samples: run.samples });
}

export function pendulumTrajectory(input) {
  const spec = checked(input, 'pendulum');
  const omega = Math.sqrt(spec.gravity / spec.length);
  const amplitude = Math.hypot(spec.initialAngle, spec.initialAngularVelocity / omega);
  const analyticComparison = amplitude <= 0.1 ? { model: 'small-angle-linearized', valid_for_amplitude_rad: 0.1, inputs: { length_m: spec.length, gravity_m_s2: spec.gravity, initial_angle_rad: spec.initialAngle, initial_angular_velocity_rad_s: spec.initialAngularVelocity, angular_frequency_rad_s: omega } } : { model: 'nonlinear-only', inputs: { length_m: spec.length, gravity_m_s2: spec.gravity, initial_angle_rad: spec.initialAngle, initial_angular_velocity_rad_s: spec.initialAngularVelocity } };
  // Follow the declared S08 model; small-angle angular dynamics conserve linearized energy.
  const restoringAngle = analyticComparison.model === 'small-angle-linearized' ? (angle) => angle : Math.sin;
  const acceleration = (state) => [state[1], -(spec.gravity / spec.length) * restoringAngle(state[0])];
  const samples = samplesFor(spec, 'pendulum', acceleration).samples;
  return freeze({ kind: 'pendulum', source: spec.source, inputProvenance: spec.inputProvenance, integrator: 'rk4-fixed-step', dt_s: spec.dt, requestedSteps: spec.steps, units: { time: 's', angle: 'rad', angular_velocity: 'rad/s', position: 'm', velocity: 'm/s' }, analyticComparison, samples });
}

// Consumes the real export_validated_setup.py envelope; Python validate_setup remains authoritative.
export function extendedTrajectoryFromValidatedArtifact(raw) {
  if (!raw || raw.artifact_version !== 's10-validated-setup-v1' || raw.validation !== 'validate_setup' || raw.producer !== 'contracts/experiment/validate_experiment.py') fail('untrusted validated artifact');
  const spec = raw.spec, scene = raw.scene;
  if (!spec || !scene || scene.schema_version !== '1.0.0' || scene.synthetic !== true || spec.scene?.scene_id !== scene.id || spec.scene?.schema_version !== scene.schema_version) fail('S08 synthetic scene mismatch');
  if (!['ramp', 'pendulum'].includes(spec.template)) fail('extended template must be ramp or pendulum');
  const gravity = quantity(spec.environment?.gravity, 'gravity');
  if (JSON.stringify(spec.environment?.gravity_direction) !== '[0,-1,0]') fail('gravity direction must be world -Y');
  const origin = spec.placement?.origin?.value;
  if (!dense(origin, 3)) fail('origin must be a finite dense 3-vector');
  const p = spec.parameters, sim = spec.simulation;
  const steps = integerHorizon(quantity(sim?.duration, 'duration'), quantity(sim?.time_step, 'time_step'));
  const common = { origin, gravity, dt: sim.time_step.value, steps, source: 'simulated', inputProvenance: 'synthetic' };
  return spec.template === 'ramp' ? rampTrajectory({ ...common, length: quantity(p.length, 'length'), inclineAngle: quantity(p.incline_angle, 'incline_angle'), frictionCoefficient: quantity(p.friction_coefficient, 'friction_coefficient'), initialSpeed: quantity(p.initial_speed, 'initial_speed') }) : pendulumTrajectory({ ...common, length: quantity(p.length, 'length'), initialAngle: quantity(p.release_angle, 'release_angle'), initialAngularVelocity: quantity(p.initial_angular_velocity, 'initial_angular_velocity') });
}

export const extendedTemplateApi = Object.freeze({ rampTrajectory, pendulumTrajectory, extendedTrajectoryFromValidatedArtifact });
