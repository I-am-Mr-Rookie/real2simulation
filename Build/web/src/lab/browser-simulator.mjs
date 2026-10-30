import { consumeValidatedTrajectoryArtifact, trajectoryFromValidatedArtifact, freeFallTrajectory, projectileTrajectory } from '../../../simulator/trajectories.mjs';
import { extendedTrajectoryFromValidatedArtifact } from '../../../simulator/extended-templates.mjs';

const fail = (message) => { throw new TypeError(`INVALID_BROWSER_SIMULATION: ${message}`); };
const finite = (value) => typeof value === 'number' && Number.isFinite(value);
// Owner Q20=A: the only label under which a recorded (Q16, scale-unverified) scene may be run.
export const WHAT_IF_LABEL = 'SIMULATED what-if of your described setup; scale unverified; not measured from the clip';

// Trusted NORMAL transport must supply an actual Python-validated export. Envelope labels are not authentication.
export function runBrowserSimulation(publicNormalPayload) {
  if (publicNormalPayload?.mode === 'what-if') return runWhatIf(publicNormalPayload.validatedSetup);
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

// S15r: explicit what-if mode for the API's s15r-what-if-setup-v1 artifact (recorded scene, numeric-contract spec only).
// Never goes through the synthetic-only validated-artifact path; engine input provenance is 'image-derived', not 'synthetic'.
// shortcut: free_fall/projectile only (extended-templates.mjs accepts synthetic provenance only); ramp/pendulum fail closed.
function runWhatIf(a) {
  if (a?.artifact_version !== 's15r-what-if-setup-v1' || a.validation !== 'numeric_contract_only' || a.what_if !== true ||
      a.label !== WHAT_IF_LABEL || a.scene?.synthetic !== false || a.scene?.scale_verified !== false) fail('what-if mode needs a labelled non-synthetic what-if artifact');
  const spec = a.spec, template = spec?.template;
  if (!['free_fall', 'projectile'].includes(template)) fail('what-if run supports free_fall and projectile only');
  const g = spec.environment?.gravity?.value, origin = spec.placement?.origin?.value, p = spec.parameters ?? {};
  const dt = spec.simulation?.time_step?.value, duration = spec.simulation?.duration?.value;
  const height = p[template === 'free_fall' ? 'drop_height' : 'launch_height']?.value;
  const v0 = template === 'free_fall' ? [0, p.initial_vertical_velocity?.value, 0] : [p.horizontal_speed?.value, 0, 0];
  if (!finite(g) || g <= 0 || JSON.stringify(spec.environment?.gravity_direction) !== '[0,-1,0]' || !Array.isArray(origin) ||
      origin.length !== 3 || !origin.every(finite) || !finite(height) || height <= 0 || !v0.every(finite)) fail('what-if spec needs explicit gravity, origin, height and velocity');
  if (!finite(duration) || duration < 0 || !finite(dt) || dt <= 0 || Math.round(duration / dt) > 1999 ||
      Math.abs(Math.round(duration / dt) * dt - duration) > 1e-9 * Math.max(1, duration)) fail('finite fixed-step horizon must fit 2000 samples including the initial point');
  const t = (template === 'free_fall' ? freeFallTrajectory : projectileTrajectory)({ initialPosition: [...origin], initialVelocity: v0,
    gravity: g, dt, steps: Math.round(duration / dt), stopPlaneY: origin[1] - height, source: 'simulated', inputProvenance: 'image-derived' });
  if (t.source !== 'simulated' || t.inputProvenance !== 'image-derived' || t.integrator !== 'rk4-fixed-step' || !t.samples.length ||
      t.samples.some((s) => !finite(s.time_s) || !s.position_m.every(finite) || !s.velocity_m_s.every(finite))) fail('engine output must be finite simulated RK4 samples');
  return { ...t, whatIf: true, label: WHAT_IF_LABEL };
}
