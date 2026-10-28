import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';
import test from 'node:test';
import { createReplayRecord, replayRecord, stableHash } from '../../Build/simulator/replay.mjs';
import { consumeValidatedTrajectoryArtifact, trajectoryFromValidatedArtifact } from '../../Build/simulator/trajectories.mjs';
import { extendedTrajectoryFromValidatedArtifact } from '../../Build/simulator/extended-templates.mjs';

// Independent expected bytes + Node SHA-256, never the product canonicalizer/hash.
const expectedBytes = (v) => Array.isArray(v)
  ? `[${v.map(expectedBytes).join(',')}]`
  : v && typeof v === 'object'
    ? `{${Object.keys(v).sort().map((k) => `${JSON.stringify(k)}:${expectedBytes(v[k])}`).join(',')}}`
    : JSON.stringify(v);
const expectedHash = (v) => createHash('sha256').update(expectedBytes(v), 'utf8').digest('hex');
const body = ({ version, seed, parameters, trace }) => ({ version, seed, parameters, trace });
const signed = (b) => ({ ...b, traceHash: expectedHash(b.trace), replayHash: expectedHash(b) });
const simple = () => ({ seed: 7, version: 's10-replay-v1', parameters: { x: [1, 2] }, trace: [{ x: 3 }] });
const plainRunner = () => [{ x: 3 }];
const actualRunner = ({ artifact }) => (['ramp', 'pendulum'].includes(artifact.spec.template)
  ? extendedTrajectoryFromValidatedArtifact(artifact)
  : trajectoryFromValidatedArtifact(consumeValidatedTrajectoryArtifact(artifact))).samples;

test('clean: independent canonical byte vectors and standard SHA-256', async () => {
  for (const [value, bytes] of [
    [null, 'null'], [[], '[]'], [-0, '0'],
    [{ z: [true, '雪', null], a: 1 }, '{"a":1,"z":[true,"雪",null]}'],
    [{ '10': 10, '2': 2, a: -1e-7 }, '{"10":10,"2":2,"a":-1e-7}'],
  ]) {
    assert.equal(expectedBytes(value), bytes);
    assert.equal(await stableHash(value), createHash('sha256').update(bytes).digest('hex'));
  }
});

for (const template of ['free_fall', 'projectile', 'ramp', 'pendulum']) {
  test(`clean: actual ${template} output matches independent record/hash oracle`, async () => {
    const artifact = JSON.parse(readFileSync(new URL(`../../evidence/S10/replay-invariants/${template}-validated.json`, import.meta.url), 'utf8'));
    const parameters = { artifact }, seed = artifact.spec.simulation.seed;
    const trace = actualRunner(parameters), record = await createReplayRecord({ seed, parameters, trace });
    assert.equal(record.traceHash, expectedHash(trace));
    assert.equal(record.replayHash, expectedHash(body(record)));
    const captured = JSON.parse(readFileSync(new URL('../../evidence/S10/replay-invariants/actual-record-hashes.json', import.meta.url), 'utf8'));
    const evidence = captured.cases.find((entry) => entry.template === template).replay;
    assert.equal(evidence.traceHash, record.traceHash); assert.equal(evidence.replayHash, record.replayHash);
    assert.deepEqual(await replayRecord(JSON.parse(JSON.stringify(record)), actualRunner), record);
    assert.equal(JSON.stringify(await createReplayRecord({ seed, parameters, trace: actualRunner(parameters) })), JSON.stringify(record));
    assert.equal(record.trace.length, template === 'pendulum' ? 1001 : 201);
    assert.ok(Object.isFrozen(record.trace[0].position_m));
    assert.ok(Object.isFrozen(record.parameters.artifact.spec));
    assert.equal(record.parameters.artifact.scene.synthetic, true);
  });
}

test('clean: sorted object keys preserve identity; ordered arrays do not', async () => {
  assert.equal(await stableHash({ b: 2, a: [0, 1] }), await stableHash({ a: [0, 1], b: 2 }));
  assert.notEqual(await stableHash([0, 1]), await stableHash([1, 0]));
});

test('clean: seed is identity-bound metadata, including legal boundary seeds', async () => {
  const records = await Promise.all([0, 7, Number.MAX_SAFE_INTEGER].map((seed) => createReplayRecord({ ...simple(), seed })));
  assert.equal(new Set(records.map((r) => r.replayHash)).size, 3);
  assert.equal(new Set(records.map((r) => r.traceHash)).size, 1);
  for (const record of records) {
    let args;
    await replayRecord(record, (...a) => { args = a; return plainRunner(); });
    assert.deepEqual(args, [record.parameters, record.seed, record.version]);
  }
});

test('clean: record is detached and deeply frozen; runner cannot mutate stored parameters', async () => {
  const input = simple(), record = await createReplayRecord(input);
  input.parameters.x[0] = 99; input.trace[0].x = 99;
  assert.deepEqual(record.parameters.x, [1, 2]); assert.deepEqual(record.trace, [{ x: 3 }]);
  await replayRecord(record, (p) => { p.x[0] = 100; return plainRunner(); });
  assert.deepEqual(record.parameters.x, [1, 2]);
  assert.throws(() => { record.trace[0].x = 100; }, TypeError);
});

for (const [name, mutate] of [
  ['seed', (r) => { r.seed += 1; }],
  ['parameters', (r) => { r.parameters.x[0] += 1; }],
  ['trace', (r) => { r.trace[0].x += 1; }],
  ['version', (r) => { r.version = 's10-replay-v2'; }],
  ['traceHash', (r) => { r.traceHash = '0'.repeat(64); }],
  ['replayHash', (r) => { r.replayHash = '0'.repeat(64); }],
]) {
  test(`clean: tampered ${name} rejects before runner`, async () => {
    const record = structuredClone(await createReplayRecord(simple())); mutate(record);
    let calls = 0;
    await assert.rejects(replayRecord(record, () => { calls++; return plainRunner(); }), /INVALID_REPLAY/);
    assert.equal(calls, 0);
  });
}

test('clean: changed runner output rejects; hashes are not authentication', async () => {
  const record = await createReplayRecord(simple());
  await assert.rejects(replayRecord(record, () => [{ x: 4 }]), /runner output differs/);
  const authored = signed({ ...simple(), trace: [{ x: 4 }] });
  assert.deepEqual(await replayRecord(authored, () => [{ x: 4 }]), authored);
});

test('clean: documented hostile JSON-incompatible parameter values reject', async () => {
  const sparse = [1, 2]; delete sparse[0];
  const cyclic = {}; cyclic.self = cyclic;
  const accessor = {}; Object.defineProperty(accessor, 'x', { enumerable: true, get() { throw new Error('must not invoke'); } });
  for (const value of [NaN, Infinity, undefined, 1n, () => 1, Symbol('x'), sparse, cyclic, accessor, new Date()]) {
    await assert.rejects(createReplayRecord({ ...simple(), parameters: { value } }), /INVALID_REPLAY/);
  }
  const symbol = { [Symbol('x')]: 1 };
  await assert.rejects(createReplayRecord({ ...simple(), parameters: symbol }), /INVALID_REPLAY/);
});

test('counterexample: array index accessor must reject before invoking getter', async () => {
  let reads = 0;
  const trace = [0]; Object.defineProperty(trace, '0', { enumerable: true, get() { reads++; return 9; } });
  const result = await createReplayRecord({ ...simple(), trace }).then(() => 'accepted', () => 'rejected');
  assert.deepEqual({ result, reads }, { result: 'rejected', reads: 0 });
});

for (const key of ['01', '4294967295']) {
  test(`counterexample: extra non-index array key ${key} must not disappear`, async () => {
    const trace = [1]; trace[key] = 2;
    await assert.rejects(createReplayRecord({ ...simple(), trace }), /INVALID_REPLAY/);
  });
}

test('counterexample: array subclass must not manufacture canonical trace through map', async () => {
  let calls = 0;
  class Forged extends Array { map() { calls++; return ['123']; } }
  const trace = new Forged(0, 1, 2, 3, 4, 5, 6);
  const result = await createReplayRecord({ ...simple(), trace }).then((record) => record, () => null);
  assert.equal(calls, 0, 'canonicalization must not invoke caller-controlled map');
  if (result) assert.deepEqual(result.trace, [0, 1, 2, 3, 4, 5, 6]);
});

for (const [name, changes] of [
  ['negative seed', { seed: -1 }], ['fractional seed', { seed: 1.5 }],
  ['unsafe seed', { seed: Number.MAX_SAFE_INTEGER + 1 }],
  ['null parameters', { parameters: null }], ['array parameters', { parameters: [] }],
  ['empty trace', { trace: [] }], ['object trace', { trace: {} }],
]) {
  test(`counterexample: malformed record ${name} rejects before running simulator`, async () => {
    const record = signed({ ...simple(), ...changes });
    let calls = 0;
    await assert.rejects(replayRecord(record, () => { calls++; return plainRunner(); }), /INVALID_REPLAY/);
    assert.equal(calls, 0, 'malformed record must not execute runner before validation');
  });
}

test('counterexample: envelope getter must reject before property execution', async () => {
  const record = signed(simple()), trace = record.trace;
  let reads = 0;
  Object.defineProperty(record, 'trace', { enumerable: true, get() { reads++; return trace; } });
  const result = await replayRecord(record, plainRunner).then(() => 'accepted', () => 'rejected');
  assert.deepEqual({ result, reads }, { result: 'rejected', reads: 0 });
});

test('counterexample: async verification must use one detached record snapshot', async () => {
  const initial = { ...simple(), seed: 1, parameters: { x: 1 }, trace: [1] };
  const record = signed(initial);
  const pending = replayRecord(record, (p) => [p.x]);
  queueMicrotask(() => Object.assign(record, signed({ ...initial, seed: 2, parameters: { x: 2 }, trace: [2] })));
  const result = await pending.then((replayed) => ({ accepted: true, replayed }), () => ({ accepted: false }));
  // Either reject concurrent mutation or replay the original record; never mix versions.
  if (result.accepted) assert.deepEqual(body(result.replayed), initial);
});
