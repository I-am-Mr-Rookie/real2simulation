// Local trusted transport only; Python validates the full spec/scene before invoking this process.
import { readFileSync } from 'node:fs';
import { consumeValidatedTrajectoryArtifact, trajectoryFromValidatedArtifact } from '../simulator/trajectories.mjs';

try {
  const artifact = consumeValidatedTrajectoryArtifact(JSON.parse(readFileSync(0, 'utf8')));
  process.stdout.write(JSON.stringify(trajectoryFromValidatedArtifact(artifact)));
} catch {
  process.stderr.write('SIMULATION_INPUT_OR_RUNTIME_ERROR\n');
  process.exitCode = 1;
}
