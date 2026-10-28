// Local trusted transport only; Python validates the full spec/scene before invoking this process.
import { readFileSync } from 'node:fs';
import { consumeValidatedTrajectoryArtifact, trajectoryFromValidatedArtifact } from '../simulator/trajectories.mjs';

try {
  const raw = JSON.parse(readFileSync(0, 'utf8'));
  let trajectory;
  if (['ramp', 'pendulum'].includes(raw.spec?.template)) {
    const { extendedTrajectoryFromValidatedArtifact } = await import('../simulator/extended-templates.mjs');
    trajectory = extendedTrajectoryFromValidatedArtifact(raw);
  } else {
    trajectory = trajectoryFromValidatedArtifact(consumeValidatedTrajectoryArtifact(raw));
  }
  process.stdout.write(JSON.stringify(trajectory));
} catch {
  process.stderr.write('SIMULATION_INPUT_OR_RUNTIME_ERROR\n');
  process.exitCode = 1;
}
