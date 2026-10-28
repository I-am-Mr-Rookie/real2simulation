import assert from 'node:assert/strict';
import test from 'node:test';
import { createReplayRecord, replayRecord, stableHash } from '../../Build/simulator/replay.mjs';
const run = (p, seed) => p.points.map((point, index) => ({ index, x: point + seed / 1000, y: p.gravity * (index + 1) }));
const params = { gravity: 9.81, points: [0, 1, 2] };
test('same seed is byte-identical and immutable', async () => { const a = await createReplayRecord({ seed: 7, parameters: params, trace: run(params, 7) }); assert.deepEqual(await replayRecord(a, run), a); assert.equal(await stableHash(a.trace), a.traceHash); assert.ok(Object.isFrozen(a.parameters)); assert.throws(() => { a.seed = 9; }, TypeError); });
test('changed seed/params distinguish; hostile inputs fail', async () => { const a = await createReplayRecord({ seed: 7, parameters: params, trace: run(params, 7) }); assert.notEqual(a.replayHash, (await createReplayRecord({ seed: 8, parameters: params, trace: run(params, 8) })).replayHash); await assert.rejects(async () => createReplayRecord({ seed: 1, parameters: { x: NaN }, trace: [1] })); const sparse=[]; sparse[1]=1; await assert.rejects(async()=>createReplayRecord({seed:1,parameters:{},trace:sparse})); const cyclic={}; cyclic.x=cyclic; await assert.rejects(async()=>createReplayRecord({seed:1,parameters:cyclic,trace:[1]})); });

