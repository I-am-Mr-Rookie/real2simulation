import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { reduce, initialState, parseJob, availableEvents, stageOf, PHASES, EVENTS } from '../../Build/web/src/workspace/workflow.mjs';
import { deps, job, jobReady, jobFailed, validSpec, observations, fitBody } from '../../Build/web/src/workspace/fixtures.mjs';

const run = (s, ...events) => events.reduce((a, e) => reduce(a, e, deps), s);
const toInterview = () => run(initialState(), { type: 'UPLOAD_STARTED', jobId: 'synthetic-job-v1' }, { type: 'JOB_UPDATE', job: job(1, 'running') }, { type: 'JOB_UPDATE', job: jobReady(2) });
const toRunReady = () => run(toInterview(), { type: 'INTERVIEW_SPEC', spec: validSpec });
const toRunDone = () => run(toRunReady(), { type: 'RUN_START', seed: 7 }, { type: 'RUN_COMPLETE', seed: 7, observations });
const toFitDone = () => run(toRunDone(), { type: 'FIT_START', sessionId: 's1' }, { type: 'FIT_RESULT', body: fitBody('s1') });

test('happy path walks upload -> interview -> run -> fit -> report', () => {
  assert.deepEqual([stageOf(toInterview()), stageOf(toRunReady()), stageOf(toRunDone()), stageOf(toFitDone())], ['interview', 'run', 'run', 'fit']);
  const s = run(toFitDone(), { type: 'REPORT_OPEN' });
  assert.equal(s.phase, 'report.open');
  assert.equal(s.scene.evidence, 'synthetic');
  assert.equal(s.run.label, 'simulated');
  assert.equal(run(s, { type: 'REPORT_CLOSE' }).phase, 'fit.done');
});

test('shell example job DTO parses; malformed DTOs are rejected', () => {
  const ex = JSON.parse(readFileSync(new URL('../../Build/web/src/shell/examples.json', import.meta.url))).find((e) => e.kind === 'job');
  assert.ok(parseJob(ex));
  for (const bad of [null, { ...ex, status: 'ready' }, { ...ex, error: { code: 'PROCESSING_FAILED', message: 'x' } }, { ...ex, revision: -1 }, { ...ex, job_id: '../x' }, jobFailed(1).error && { ...jobFailed(1), error: null }])
    assert.equal(parseJob(bad), null);
});

test('job rules: stale/equal revisions, wrong id, regression and terminal states are ignored', () => {
  const started = run(initialState(), { type: 'UPLOAD_STARTED', jobId: 'synthetic-job-v1' });
  const running = run(started, { type: 'JOB_UPDATE', job: job(3, 'running') });
  assert.equal(running.phase, 'upload.running');
  for (const j of [job(3, 'running'), job(2, 'failed', { error: { code: 'PROCESSING_FAILED', message: 'x' } }), job(4, 'queued'), { ...job(9, 'running'), job_id: 'other' }])
    assert.equal(reduce(running, { type: 'JOB_UPDATE', job: j }), running);
  const failed = reduce(running, { type: 'JOB_UPDATE', job: jobFailed(4) });
  assert.equal(failed.phase, 'upload.failed');
  assert.equal(failed.error.code, 'PROCESSING_FAILED');
  assert.equal(reduce(failed, { type: 'JOB_UPDATE', job: jobReady(5) }), failed);       // terminal never transitions
  assert.equal(run(failed, { type: 'UPLOAD_STARTED', jobId: 'retry-job-2' }).job.id, 'retry-job-2'); // retry = new job id
  assert.equal(reduce(run(started, { type: 'JOB_UPDATE', job: job(1, 'cancelled') }), { type: 'RESET' }).phase, 'upload.idle');
});

test('invalid spec stays in interview with a readable error; valid spec advances', () => {
  const s = run(toInterview(), { type: 'INTERVIEW_SPEC', spec: { template: 'free-fall' } });
  assert.equal(s.phase, 'interview.active');
  assert.match(s.error.message, /rejected/);
  assert.equal(reduce(toInterview(), { type: 'INTERVIEW_SPEC', spec: validSpec }, deps).phase, 'run.ready');
  assert.equal(reduce(toInterview(), { type: 'INTERVIEW_SPEC', spec: validSpec }, {}).phase, 'interview.active'); // no validator = fail closed
});

test('run: pause/resume/cancel, seed binding, malformed and gravity-leaking output rejected', () => {
  const r = run(toRunReady(), { type: 'RUN_START', seed: 7 });
  assert.equal(run(r, { type: 'RUN_PAUSE' }).phase, 'run.paused');
  assert.equal(run(r, { type: 'RUN_PAUSE' }, { type: 'RUN_RESUME' }).phase, 'run.running');
  assert.equal(run(r, { type: 'RUN_PAUSE' }, { type: 'RUN_CANCEL' }).phase, 'run.ready');
  assert.equal(run(r, { type: 'RUN_PAUSE' }, { type: 'RUN_COMPLETE', seed: 7, observations }).phase, 'run.paused');
  assert.equal(reduce(r, { type: 'RUN_COMPLETE', seed: 8, observations }), r);
  assert.equal(reduce(r, { type: 'RUN_START', seed: 1.5 }), r);
  for (const o of [[], [{ time_s: NaN, position_m: 0 }], [{ time_s: 0, position_m: 0, hidden_g: 9 }]])
    assert.equal(reduce(r, { type: 'RUN_COMPLETE', seed: 7, observations: o }).phase, 'run.failed');
  assert.equal(run(toRunDone(), { type: 'RUN_START', seed: 7 }).phase, 'run.running'); // seeded replay
});

test('fit: only validated reveal for the expected session produces numbers', () => {
  const done = toFitDone();
  assert.equal(done.fit.value, 1.25); // equals parseFitReveal output of the fixture, nothing added
  const started = run(toRunDone(), { type: 'FIT_START', sessionId: 's1' });
  for (const body of [fitBody('other'), { status: 'ok' }, null]) {
    const s = reduce(started, { type: 'FIT_RESULT', body });
    assert.equal(s.phase, 'fit.failed');
    assert.equal(s.fit, null);
  }
  assert.equal(run(started, { type: 'FIT_CANCEL' }).phase, 'run.done');
  assert.equal(run(started, { type: 'FIT_FAIL', error: { message: 'x' } }, { type: 'FIT_START', sessionId: 's2' }).phase, 'fit.running'); // retry
});

test('EDIT_SPEC invalidates run and fit; blocked while work is in flight', () => {
  const s = run(toFitDone(), { type: 'REPORT_OPEN' }, { type: 'EDIT_SPEC' });
  assert.deepEqual([s.phase, s.spec, s.run, s.fit], ['interview.active', null, null, null]);
  const running = run(toRunReady(), { type: 'RUN_START', seed: 1 });
  assert.equal(reduce(running, { type: 'EDIT_SPEC' }), running);
});

test('illegal events return the same state; every phase/event is reachable and documented', () => {
  const idle = initialState();
  for (const t of ['JOB_UPDATE', 'RUN_START', 'FIT_START', 'REPORT_OPEN', 'EDIT_SPEC', 'nope']) assert.equal(reduce(idle, { type: t }), idle);
  assert.equal(reduce(idle, undefined), idle);
  assert.deepEqual(availableEvents(idle).sort(), ['RESET', 'UPLOAD_STARTED']);
  const seen = new Set(); const snaps = [initialState(), run(initialState(), { type: 'UPLOAD_STARTED', jobId: 'a' }), toInterview(), toRunReady(), toRunDone(), toFitDone(), run(toFitDone(), { type: 'REPORT_OPEN' }),
    run(toRunReady(), { type: 'RUN_START', seed: 1 }), run(toRunReady(), { type: 'RUN_START', seed: 1 }, { type: 'RUN_PAUSE' }), run(toRunReady(), { type: 'RUN_START', seed: 1 }, { type: 'RUN_FAIL' }),
    run(toRunDone(), { type: 'FIT_START', sessionId: 's1' }), run(toRunDone(), { type: 'FIT_START', sessionId: 's1' }, { type: 'FIT_FAIL' }),
    run(initialState(), { type: 'UPLOAD_STARTED', jobId: 'synthetic-job-v1' }, { type: 'JOB_UPDATE', job: job(1, 'running') }),
    run(initialState(), { type: 'UPLOAD_STARTED', jobId: 'synthetic-job-v1' }, { type: 'JOB_UPDATE', job: jobFailed(1) }),
    run(initialState(), { type: 'UPLOAD_STARTED', jobId: 'synthetic-job-v1' }, { type: 'JOB_UPDATE', job: job(1, 'cancelled') })];
  for (const s of snaps) seen.add(s.phase);
  assert.deepEqual([...seen].sort(), [...PHASES].sort());
  const doc = readFileSync(new URL('../../Build/web/src/workspace/README.md', import.meta.url), 'utf8');
  for (const p of PHASES) assert.ok(doc.includes('`' + p + '`'), 'README missing ' + p);
  for (const e of EVENTS) assert.ok(doc.includes('`' + e + '`'), 'README missing ' + e);
});

