import { consumeValidatedTrajectoryArtifact, trajectoryFromValidatedArtifact } from '../../../simulator/trajectories.mjs';
import { extendedTrajectoryFromValidatedArtifact } from '../../../simulator/extended-templates.mjs';

const fail = (message) => { throw new TypeError(`INVALID_BROWSER_SIMULATION: ${message}`); };
const finite = (value) => typeof value === 'number' && Number.isFinite(value);

// Trusted NORMAL transport must supply an actual Python-validated export. Envelope labels are not authentication.
export function runBrowserSimulation(publicNormalPayload) {
  if (publicNormalPayload?.mode !== 'normal') fail('only explicit normal mode is supported');
  const artifact = publicNormalPayload.validatedSetup;
  const template = artifact?.spec?.template;
  if (!['free_fall', 'projectile', 'ramp', 'pendulum'].includes(template)) fail('unsupported template');
  const duration = artifact.spec.simulation?.duration?.value;
  const dt = artifact.spec.simulation?.time_step?.value;
  if (!finite(duration) || duration < 0 || !finite(dt) || dt <= 0 ||
      !Number.isSafeInteger(Math.round(duration / dt)) || Math.round(duration / dt) > 1999) {
    fail('finite fixed-step horizon must fit 2000 samples including the initial point');
  }
  const trajectory = ['ramp', 'pendulum'].includes(template)
    ? extendedTrajectoryFromValidatedArtifact(artifact)
    : trajectoryFromValidatedArtifact(consumeValidatedTrajectoryArtifact(artifact));
  if (trajectory.source !== 'simulated' || trajectory.inputProvenance !== 'synthetic' ||
      trajectory.integrator !== 'rk4-fixed-step' || !trajectory.samples.length || trajectory.samples.length > 2000 ||
      trajectory.samples.some((sample) => !finite(sample.time_s) ||
        !sample.position_m.every(finite) || !sample.velocity_m_s.every(finite))) {
    fail('engine output must be finite simulated/synthetic RK4 samples');
  }
  return trajectory;
}
