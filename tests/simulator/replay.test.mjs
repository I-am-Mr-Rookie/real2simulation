import assert from 'node:assert/strict';
import test from 'node:test';
import { createReplayRecord, replayRecord, stableHash } from '../../Build/simulator/replay.mjs';

const run = (parameters, seed) => parameters.points.map((point, index) => ({ index, x: point + seed / 1000, y: parameters.gravity * (index + 1) }));
const params = { gravity: 9.81, points: [0, 1, 2] };

test('same seed and parameters produce byte-identical immutable record', () => {
  const a = createReplayRecord({ seed: 7, parameters: params, trace: run(params, 7) });
  const b = replayRecord(a, run);
  assert.deepEqual(b, a);
  assert.equal(stableHash(a.trace), a.traceHash);
  assert.ok(Object.isFrozen(a) && Object.isFrozen(a.parameters) && Object.isFrozen(a.trace));
  assert.throws(() => { a.seed = 9; }, TypeError);
});

test('changed seed or numeric parameters changes the replay hash', () => {
  const a = createReplayRecord({ seed: 7, parameters: params, trace: run(params, 7) });
  const seedChanged = createReplayRecord({ seed: 8, parameters: params, trace: run(params, 8) });
  const parameterChanged = createReplayRecord({ seed: 7, parameters: { ...params, gravity: 9.8 }, trace: run({ ...params, gravity: 9.8 }, 7) });
  assert.notEqual(a.replayHash, seedChanged.replayHash);
  assert.notEqual(a.replayHash, parameterChanged.replayHash);
});

test('rejects sparse, nonfinite, hostile, and non-deterministic records', () => {
  assert.throws(() => createReplayRecord({ seed: 1, parameters: { x: NaN }, trace: [1] }), /non-finite/);
  const sparse = []; sparse[1] = 1;
  assert.throws(() => createReplayRecord({ seed: 1, parameters: {}, trace: sparse }), /sparse|undefined/);
  assert.throws(() => createReplayRecord({ seed: 1, parameters: { x: 1 }, trace: [() => 1] }), /parameters must contain only JSON/);
  const record = createReplayRecord({ seed: 1, parameters: { x: 1 }, trace: [1] });
  assert.throws(() => replayRecord(record, () => [2]), /differs/);
  assert.throws(() => replayRecord({ ...record, replayHash: 'x' }, () => [1]), /hash/);
});


