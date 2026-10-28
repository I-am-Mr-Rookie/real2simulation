// Internal validated-artifact transport: use actual four-template engines, not a fake replay runner.
import { readFileSync } from 'node:fs';
import { createReplayRecord, replayRecord } from '../simulator/replay.mjs';
import { consumeValidatedTrajectoryArtifact, trajectoryFromValidatedArtifact } from '../simulator/trajectories.mjs';
import { extendedTrajectoryFromValidatedArtifact } from '../simulator/extended-templates.mjs';

const artifact = JSON.parse(readFileSync(0, 'utf8'));
const runner = ({ artifact: raw }) => (
  ['ramp', 'pendulum'].includes(raw.spec.template)
    ? extendedTrajectoryFromValidatedArtifact(raw)
    : trajectoryFromValidatedArtifact(consumeValidatedTrajectoryArtifact(raw))
).samples;
const parameters = { artifact };
const seed = artifact.spec.simulation.seed;
const trace = runner(parameters);
const record = await createReplayRecord({ seed, parameters, trace });
const replayed = await replayRecord(record, runner);
const changedSeed = await createReplayRecord({ seed: seed + 1, parameters, trace });
if (record.replayHash !== replayed.replayHash || record.traceHash !== replayed.traceHash
    || record.replayHash === changedSeed.replayHash) throw new Error('ACTUAL_REPLAY_MISMATCH');
process.stdout.write(JSON.stringify({ replayHash: record.replayHash, traceHash: record.traceHash,
  deterministic: true, seedBound: true, samples: trace.length,
  seedSemantics: 'seed binds replay identity; deterministic noiseless physics does not randomize by seed' }));
