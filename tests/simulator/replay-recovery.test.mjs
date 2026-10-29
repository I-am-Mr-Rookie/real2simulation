import assert from 'node:assert/strict';
import test from 'node:test';
import { createReplayRecord, replayRecord, stableHash } from '../../Build/simulator/replay.mjs';

const input = () => ({ seed: 7, parameters: { x: 3 }, trace: [3] });
const mutableRecord = async () => structuredClone(await createReplayRecord(input()));

for (const enumerable of [true, false]) {
  for (const field of ['seed', 'version', 'parameters', 'trace', 'traceHash', 'replayHash']) {
    test(`replay rejects ${enumerable ? 'enumerable' : 'hidden'} ${field} accessor without execution`, async () => {
      const record = await mutableRecord();
      let reads = 0, calls = 0;
      Object.defineProperty(record, field, { enumerable, get() { reads++; throw new Error('getter executed'); } });
      await assert.rejects(replayRecord(record, () => { calls++; return [3]; }), /INVALID_REPLAY/);
      assert.equal(reads, 0);
      assert.equal(calls, 0);
    });
  }
}

test('creation rejects envelope and nested hidden accessors without execution', async () => {
  for (const field of ['seed', 'parameters', 'trace']) {
    const payload = input();
    let reads = 0;
    Object.defineProperty(payload, field, { get() { reads++; return 3; } });
    await assert.rejects(createReplayRecord(payload), /INVALID_REPLAY/);
    assert.equal(reads, 0);
  }
  const payload = input();
  let reads = 0;
  Object.defineProperty(payload.parameters, 'hidden', { get() { reads++; return 3; } });
  await assert.rejects(createReplayRecord(payload), /INVALID_REPLAY/);
  assert.equal(reads, 0);
});

test('array descriptors reject non-index/symbol/map extras without invoking them', async () => {
  for (const key of ['00', '-0', '-1', '1.0', '1e0', '4294967295', 'map', Symbol('extra')]) {
    const trace = [3];
    let reads = 0;
    Object.defineProperty(trace, key, { get() { reads++; return 3; } });
    await assert.rejects(stableHash(trace), /INVALID_REPLAY/);
    assert.equal(reads, 0);
  }
});

test('array subclass traversal uses own data rather than inherited map/index getters', async () => {
  let calls = 0;
  class HostileArray extends Array {
    map() { calls++; throw new Error('map executed'); }
  }
  Object.defineProperty(HostileArray.prototype, '1', { get() { calls++; return 99; } });
  const dense = new HostileArray(1);
  dense[0] = 3;
  assert.equal(await stableHash(dense), await stableHash([3]));
  const sparse = new HostileArray(2);
  sparse[0] = 3;
  await assert.rejects(stableHash(sparse), /INVALID_REPLAY/);
  assert.equal(calls, 0);
});

test('runner mutation of original record cannot replace the verified snapshot', async () => {
  const record = await mutableRecord(), expected = structuredClone(record);
  const replay = await replayRecord(record, (parameters, seed, version) => {
    assert.equal(seed, 7);
    assert.equal(version, 's10-replay-v1');
    record.seed = 8;
    record.parameters.x = 99;
    record.trace[0] = 99;
    record.traceHash = record.replayHash = '0'.repeat(64);
    const trace = [parameters.x];
    parameters.x = 100;
    return trace;
  });
  assert.deepEqual(replay, expected);
  assert.ok(Object.isFrozen(replay.parameters));
  assert.ok(Object.isFrozen(replay.trace));
});

test('creation detaches parameters and trace before its first await', async () => {
  const payload = input(), expected = await createReplayRecord(payload);
  const pending = createReplayRecord(payload);
  payload.seed = 8;
  payload.parameters.x = 99;
  payload.trace[0] = 99;
  assert.deepEqual(await pending, expected);
});

test('invalid envelope types reject before runner', async () => {
  for (const record of [null, undefined, [], 3, 'record', new Date()]) {
    let calls = 0;
    await assert.rejects(replayRecord(record, () => { calls++; return [3]; }), /INVALID_REPLAY/);
    assert.equal(calls, 0);
  }
});

test('unsupported versions reject during creation without a simulator dependency', async () => {
  await assert.rejects(createReplayRecord({ ...input(), version: 'unknown' }), /INVALID_REPLAY:.*metadata/);
});
