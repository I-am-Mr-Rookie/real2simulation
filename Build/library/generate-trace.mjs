// Offline only: project accepted simulator samples, never publish replay parameters.
import { readFileSync } from 'node:fs';
import { stableHash } from '../simulator/replay.mjs';
import { consumeValidatedTrajectoryArtifact, trajectoryFromValidatedArtifact } from '../simulator/trajectories.mjs';
import { extendedTrajectoryFromValidatedArtifact } from '../simulator/extended-templates.mjs';

const { artifact, record } = JSON.parse(readFileSync(0, 'utf8'));
if (record.status !== 'passed' || record.deterministic !== true ||
    artifact.spec.template !== record.template) throw new Error('Not an accepted matching case');
// Only the accepted case supplies the horizon; initial conditions remain source-owned.
artifact.spec.simulation.duration.value = record.duration_s;
artifact.spec.simulation.time_step.value = record.time_step_s;
if (artifact.spec.environment.gravity.value !== record.gravity_m_s2) throw new Error('Gravity mismatch');
const steps = record.duration_s / record.time_step_s;
if (!Number.isFinite(steps) || steps < 1 || steps > 4095) throw new Error('Trace horizon exceeds guest bound');
const result = record.template === 'pendulum' ? extendedTrajectoryFromValidatedArtifact(artifact) :
  trajectoryFromValidatedArtifact(consumeValidatedTrajectoryArtifact(artifact));
const traceHash = await stableHash(result.samples);
if (result.samples.length !== record.samples) throw new Error('Simulator sample count differs from accepted horizon');
process.stdout.write(JSON.stringify({ traceHash, trace: {
  kind: result.kind, source: 'simulated', inputProvenance: 'synthetic', dt_s: result.dt_s,
  samples: result.samples.map(({ step, time_s, position_m }) => ({ step, time_s, position_m })),
  label: 'SIMULATED',
} }));
