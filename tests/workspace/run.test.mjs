import test from 'node:test';
import assert from 'node:assert/strict';
import { reduce, initialState } from '../../Build/web/src/workspace/workflow.mjs';
import { deps, jobReady, validSpec, runParameters, fixtureRunner } from '../../Build/web/src/workspace/fixtures.mjs';
import { initialRun, reduceRun, prepareRun, verifyReplay, completionEvent, runView } from '../../Build/web/src/workspace/runcontrol.mjs';
import { renderRun } from '../../Build/web/src/workspace/run-view.mjs';
import { createReplayRecord, replayRecord } from '../../Build/simulator/replay.mjs';

const sim = { createReplayRecord, replayRecord, runner: fixtureRunner, parameters: runParameters };
const ready = () => [{ type: 'UPLOAD_STARTED', jobId: 'synthetic-job-v1' }, { type: 'JOB_UPDATE', job: jobReady(1) }, { type: 'INTERVIEW_SPEC', spec: validSpec }]
  .reduce((s, e) => reduce(s, e, deps), initialState());
// Host loop mirror: every event goes to the S15a reducer and the run model.
const mk = () => { const h = { s: ready(), m: initialRun() };
  h.send = (e) => { h.m = reduceRun(h.m, e, h.s); h.s = reduce(h.s, e, deps); return h; }; return h; };
const start = async (h, seed) => { h.send({ type: 'RUN_START', seed }); return h.send({ type: 'R_LOAD', record: await prepareRun({ ...sim, seed }) }); };
const play = (h) => { for (let i = 0; i < 100 && !completionEvent(h.s, h.m); i += 1) h.send({ type: 'R_TICK' }); const c = completionEvent(h.s, h.m); if (c) h.send(c); return h; };

test('run, pause, resume, complete: pause freezes the cursor and never changes the trace', async () => {
  const h = mk(); assert.equal(runView(h.s, h.m).canRun, true);
  await start(h, 7); assert.equal(h.s.phase, 'run.running');
  h.send({ type: 'R_TICK' }).send({ type: 'R_TICK' }); assert.equal(h.m.cursor, 2);
  h.send({ type: 'RUN_PAUSE' }); const frozen = h.m; assert.equal(h.s.phase, 'run.paused');
  assert.equal(reduceRun(frozen, { type: 'R_TICK' }, h.s), frozen); // same reference: no-op
  assert.equal(completionEvent(h.s, h.m), null);
  const v = runView(h.s, h.m); assert.deepEqual([v.canPause, v.canResume, v.canRun, v.canReplay], [false, true, false, false]);
  h.send({ type: 'RUN_RESUME' }); play(h);
  assert.equal(h.s.phase, 'run.done'); assert.equal(h.s.run.label, 'simulated');
  assert.deepEqual(h.s.run.observations, fixtureRunner(runParameters, 7)); // observations == simulator trace verbatim
  const paused = h.s.run.observations; // same run with no pause at all
  const g = mk(); await start(g, 7); play(g); assert.deepEqual(g.s.run.observations, paused); assert.equal(g.m.record.replayHash, h.m.record.replayHash);
});

test('same-seed replay reproduces an identical trace and hashes; seed is bound into identity only', async () => {
  const a = await prepareRun({ ...sim, seed: 42 }), b = await prepareRun({ ...sim, seed: 42 }), c = await prepareRun({ ...sim, seed: 43 });
  assert.deepEqual(a.trace, b.trace); assert.equal(a.traceHash, b.traceHash); assert.equal(a.replayHash, b.replayHash);
  assert.deepEqual(a.trace, c.trace); assert.equal(a.traceHash, c.traceHash); assert.notEqual(a.replayHash, c.replayHash); // replay contract
  const v = await verifyReplay({ replayRecord, record: a, runner: fixtureRunner });
  assert.deepEqual(v, { status: 'verified', replayHash: a.replayHash, traceHash: a.traceHash });
});

test('replay mismatch is surfaced, never swallowed', async () => {
  const a = await prepareRun({ ...sim, seed: 5 });
  const drift = await verifyReplay({ replayRecord, record: a, runner: (p, s, v) => fixtureRunner(p, s, v).map((f) => ({ ...f, position_m: f.position_m + 1 })) });
  assert.equal(drift.status, 'mismatch'); assert.match(drift.message, /differs from recorded trace/);
  const tampered = JSON.parse(JSON.stringify(a)); tampered.trace[1].position_m = 99;
  assert.match((await verifyReplay({ replayRecord, record: tampered, runner: fixtureRunner })).message, /hash mismatch/);
  assert.equal((await verifyReplay({ replayRecord, record: { nope: 1 }, runner: fixtureRunner })).status, 'mismatch');
});

test('replay UI flow: only when done, once at a time, result recorded; run again clears it', async () => {
  const h = mk(); await start(h, 9);
  assert.equal(reduceRun(h.m, { type: 'R_REPLAY_START' }, h.s), h.m); // not while running
  play(h); assert.equal(runView(h.s, h.m).canReplay, true);
  h.send({ type: 'R_REPLAY_START' }); assert.equal(h.m.replay.status, 'checking'); assert.equal(runView(h.s, h.m).canReplay, false);
  assert.equal(reduceRun(h.m, { type: 'R_REPLAY_START' }, h.s), h.m);
  h.send({ type: 'R_REPLAY_RESULT', result: await verifyReplay({ replayRecord, record: h.m.record, runner: fixtureRunner }) });
  assert.equal(runView(h.s, h.m).replay.status, 'verified'); assert.equal(runView(h.s, h.m).replay.text, 'Replay matched: identical trace and hashes.');
  assert.equal(reduceRun(h.m, { type: 'R_REPLAY_RESULT', result: { status: 'verified' } }, h.s), h.m); // no pending check: ignored
  h.send({ type: 'RUN_START', seed: 9 }); assert.deepEqual(h.m, initialRun()); // re-run: no stale record/replay
  assert.equal(completionEvent(h.s, h.m), null);
});

test('guards: stale/foreign records, ticks outside running, cancel and spec edit drop playback', async () => {
  const h = mk(); const rec = await prepareRun({ ...sim, seed: 1 });
  assert.equal(reduceRun(h.m, { type: 'R_LOAD', record: rec }, h.s), h.m); // run.ready: ignored
  h.send({ type: 'RUN_START', seed: 2 }); assert.equal(reduceRun(h.m, { type: 'R_LOAD', record: rec }, h.s), h.m); // seed 1 record for seed 2 run
  assert.equal(reduceRun(h.m, { type: 'R_TICK' }, h.s), h.m); // no record yet
  h.send({ type: 'R_LOAD', record: await prepareRun({ ...sim, seed: 2 }) }).send({ type: 'R_TICK' }).send({ type: 'RUN_CANCEL' });
  assert.equal(h.s.phase, 'run.ready'); assert.deepEqual(h.m, initialRun());
  await start(h, 3); play(h); h.send({ type: 'EDIT_SPEC' }); assert.deepEqual(h.m, initialRun()); assert.equal(runView(h.s, h.m).show, false);
});

test('a hidden-physics key in the trace still fails the run (S15a leak guard)', async () => {
  const h = mk(); h.send({ type: 'RUN_START', seed: 4 });
  h.send({ type: 'R_LOAD', record: await prepareRun({ ...sim, seed: 4, runner: () => [{ time_s: 0, position_m: 0, hidden_g: 9 }] }) });
  play(h); assert.equal(h.s.phase, 'run.failed');
});

// minimal h(): element tree with text + button lookup
const h = (type, props, ...kids) => ({ type, props: props ?? {}, kids: kids.flat().filter((k) => k !== null) });
const text = (n) => (typeof n === 'string' ? n : n.kids.map(text).join(' '));
const buttons = (n) => (typeof n === 'string' ? [] : [...(n.type === 'button' ? [n] : []), ...n.kids.flatMap(buttons)]);

test('controls per phase; clicks report plain events; disabled without a host', async () => {
  const h0 = mk(); const sent = [];
  let t = renderRun(h, runView(h0.s, h0.m), (e) => sent.push(e)); assert.deepEqual(buttons(t).map((b) => text(b)), ['Run']);
  buttons(t)[0].props.onClick(); assert.deepEqual(sent, [{ type: 'RUN_START' }]);
  await start(h0, 8); h0.send({ type: 'R_TICK' });
  t = renderRun(h, runView(h0.s, h0.m), () => {}); assert.deepEqual(buttons(t).map(text), ['Pause', 'Cancel run']); assert.match(text(t), /Frame 1 of 8: t = 0.25 s/);
  h0.send({ type: 'RUN_PAUSE' }); assert.deepEqual(buttons(renderRun(h, runView(h0.s, h0.m), () => {})).map(text), ['Resume', 'Cancel run']);
  h0.send({ type: 'RUN_RESUME' }); play(h0); t = renderRun(h, runView(h0.s, h0.m), () => {});
  assert.deepEqual(buttons(t).map(text), ['Run again', 'Replay with same seed']); assert.match(text(t), /Seed 8 \(simulated; trace [0-9a-f]{12}, replay [0-9a-f]{12}\)/);
  assert.ok(buttons(renderRun(h, runView(h0.s, h0.m))).every((b) => b.props.disabled));
  assert.equal(renderRun(h, runView(initialState(), initialRun())), null);
});

