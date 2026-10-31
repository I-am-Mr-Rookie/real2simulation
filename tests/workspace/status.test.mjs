import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { initialLogged, reduceLogged, jobTimeline, failureSurface, partialState, statusSurface, eventText, LOG_MAX } from '../../Build/web/src/workspace/status.mjs';
import { availableEvents, initialState } from '../../Build/web/src/workspace/workflow.mjs';
import { layoutOf } from '../../Build/web/src/workspace/layout.mjs';
import { renderWorkspace } from '../../Build/web/src/workspace/view.mjs';
import { deps, job, jobReady, jobFailed, validSpec, observations } from '../../Build/web/src/workspace/fixtures.mjs';

const feed = (m, ...evs) => evs.reduce((a, e) => reduceLogged(a, e, deps), m);
const start = (m = initialLogged()) => feed(m, { type: 'UPLOAD_STARTED', jobId: 'synthetic-job-v1' });
const failedWith = (code, message = 'SYNTHETIC failure fixture') => ({ type: 'JOB_UPDATE', job: job(5, 'failed', { error: { code, message } }) });

// minimal h that renders an inspectable tree
const h = (type, props, ...children) => ({ type, props: props ?? {}, children: children.flat().filter((c) => c != null) });
const find = (n, pred, out = []) => { if (n && typeof n === 'object') { if (pred(n)) out.push(n); n.children.forEach((c) => find(c, pred, out)); } return out; };
const textOf = (n) => (typeof n === 'string' ? n : n.children.map(textOf).join(' '));
const render = (m, onAction) => renderWorkspace(h, layoutOf(m.state, { log: m.log }), { status: 'empty', error: null }, null, onAction);

test('job-stage events are logged in order, including ignored stale/illegal ones', () => {
  const m = feed(start(), { type: 'JOB_UPDATE', job: job(1, 'running') }, { type: 'JOB_UPDATE', job: job(1, 'running') }, { type: 'RUN_START', seed: 1 }, { type: 'JOB_UPDATE', job: jobReady(2) });
  assert.deepEqual(m.log.map((e) => [e.type, e.outcome]), [['UPLOAD_STARTED', 'applied'], ['JOB_UPDATE', 'applied'], ['JOB_UPDATE', 'ignored'], ['RUN_START', 'ignored'], ['JOB_UPDATE', 'applied']]);
  assert.deepEqual(m.log.map((e) => e.seq), [1, 2, 3, 4, 5]);
  assert.match(eventText(m.log[2]), /ignored/);
  assert.match(eventText(m.log[4]), /Job update r2: ready \(upload\.running -> interview\.active\)/);
  const same = reduceLogged(m, { type: 'RUN_START', seed: 1 }, deps);
  assert.equal(same.state, m.state); // ignored events never change state
});

test('log is bounded and never copies payload text (job status allow-listed)', () => {
  let m = start();
  for (let i = 0; i < LOG_MAX + 20; i++) m = feed(m, { type: 'JOB_UPDATE', job: { status: '<img onerror=x>', revision: 'x' } });
  assert.equal(m.log.length, LOG_MAX);
  assert.ok(m.log.every((e) => e.jobStatus === null && e.revision === null));
  assert.doesNotMatch(JSON.stringify(m.log), /img/);
  assert.equal(reduceLogged(initialLogged(), null).log[0].type, 'UNKNOWN');
});

test('timeline follows the job through queued -> running -> ready; failure marks the furthest step', () => {
  const ids = (m) => jobTimeline(m.state, m.log).map((t) => t.id + ':' + t.status);
  assert.deepEqual(jobTimeline(initialState()), []);
  let m = start();
  assert.deepEqual(ids(m), ['queued:current', 'running:todo', 'ready:todo']);
  m = feed(m, { type: 'JOB_UPDATE', job: job(1, 'running') });
  assert.deepEqual(ids(m), ['queued:done', 'running:current', 'ready:todo']);
  assert.deepEqual(ids(feed(m, { type: 'JOB_UPDATE', job: jobReady(2) })), ['queued:done', 'running:done', 'ready:done']);
  assert.deepEqual(ids(feed(m, failedWith('PROCESSING_FAILED'))), ['queued:done', 'running:done', 'failed:failed']);
  assert.deepEqual(ids(feed(start(), failedWith('PROCESSING_FAILED'))), ['queued:done', 'failed:failed']); // failed straight from queued
});

test('upload failure: partial-state says nothing was created; retry offered only when it can help', () => {
  for (const code of ['PROCESSING_FAILED', 'DEPENDENCY_UNAVAILABLE', 'INVALID_INPUT', 'NOT_FOUND']) {
    const f = failureSurface(feed(start(), failedWith(code)).state);
    assert.equal(f.code, code); assert.deepEqual(f.retry, { event: 'UPLOAD_STARTED', label: 'Start a new upload' });
    assert.match(f.lost[0], /none was created/); assert.deepEqual(f.kept, []);
  }
  for (const code of ['SPEND_PAUSED', 'UNAUTHORIZED']) {
    const f = failureSurface(feed(start(), failedWith(code)).state);
    assert.equal(f.retry, null); assert.match(f.advice, /not help|Sign in/);
  }
  const c = failureSurface(feed(start(), { type: 'JOB_UPDATE', job: job(1, 'cancelled') }).state);
  assert.equal(c.kind, 'cancelled'); assert.equal(c.retry.event, 'UPLOAD_STARTED');
  assert.equal(failureSurface(start().state), null);
});

test('every offered retry is a legal reducer edge and actually recovers (new job id, log restarts)', () => {
  let m = feed(start(), failedWith('PROCESSING_FAILED'));
  const f = failureSurface(m.state);
  assert.ok(availableEvents(m.state).includes(f.retry.event));
  m = feed(m, { type: f.retry.event, jobId: 'synthetic-job-v2' });
  assert.equal(m.state.phase, 'upload.queued'); assert.equal(m.state.error, null);
  assert.deepEqual(statusSurface(m.state, m.log).events.map((e) => e.slice(0, 3)), ['#3 ']); // events since the retry start only (log seq continues; earlier failed attempt hidden)
  m = feed(m, { type: 'JOB_UPDATE', job: { ...job(1, 'running'), job_id: 'synthetic-job-v2' } });
  assert.equal(m.state.phase, 'upload.running');
  // the failed job's late update cannot revive the old attempt
  const late = feed(m, { type: 'JOB_UPDATE', job: jobReady(9) });
  assert.equal(late.state, m.state); assert.equal(late.log.at(-1).outcome, 'ignored');
});

test('run/fit failures keep what exists and say what is missing; no fit number without a validated fit', () => {
  const runReady = feed(start(), { type: 'JOB_UPDATE', job: jobReady(1) }, { type: 'INTERVIEW_SPEC', spec: validSpec });
  const runFailed = feed(runReady, { type: 'RUN_START', seed: 3 }, { type: 'RUN_FAIL', error: { message: 'SYNTHETIC run failure' } });
  let f = failureSurface(runFailed.state);
  assert.equal(f.stage, 'run'); assert.deepEqual(f.retry, { event: 'RUN_START', label: 'Run again' });
  assert.deepEqual(f.kept, ['Scene (viewport stays available)', 'Interview spec']); assert.deepEqual(f.lost, ['Run result: none stored']);
  const fitFailed = feed(runReady, { type: 'RUN_START', seed: 3 }, { type: 'RUN_COMPLETE', seed: 3, observations }, { type: 'FIT_START', sessionId: 's1' }, { type: 'FIT_FAIL', error: { message: 'x' } });
  f = failureSurface(fitFailed.state);
  assert.equal(f.stage, 'fit'); assert.equal(f.retry.event, 'FIT_START');
  assert.ok(f.kept.includes('Run observations (simulated)')); assert.match(f.lost.join(), /Fit value: none shown/);
  assert.equal(fitFailed.state.fit, null);
  assert.deepEqual(partialState(runReady.state).lost, ['Run result: none stored']); // run.ready: accurate, not yet run
});

test('markup: timeline, events, failure copy and retry button; retry reports only the event type', () => {
  const m = feed(start(), { type: 'JOB_UPDATE', job: job(1, 'running') }, failedWith('DEPENDENCY_UNAVAILABLE', 'SYNTHETIC <b>x</b>'));
  const got = []; const t = render(m, (a) => got.push(a));
  const slot = find(t, (n) => n.props['data-slot'] === 'job-status')[0];
  assert.equal(find(slot, (n) => n.props.className === 'ws-timeline')[0].children.length, 3);
  assert.match(textOf(find(slot, (n) => n.props.className === 'ws-events')[0]), /#3 Job update r5: failed/);
  const fail = find(slot, (n) => n.props.className === 'ws-failure')[0];
  assert.match(textOf(fail), /Upload failed[\s\S]*Retrying later may work[\s\S]*Not available: Scene: none was created/);
  assert.match(textOf(find(slot, (n) => n.props.className === 'ws-error')[0]), /DEPENDENCY_UNAVAILABLE: SYNTHETIC <b>x<\/b>/); // text node, not HTML
  const btn = find(fail, (n) => n.type === 'button')[0];
  assert.equal(btn.props.disabled, false); btn.props.onClick();
  assert.deepEqual(got, [{ type: 'UPLOAD_STARTED' }]);
  assert.equal(find(render(m), (n) => n.type === 'button')[0].props.disabled, true); // no handler -> disabled
  const blocked = render(feed(start(), failedWith('SPEND_PAUSED')));
  assert.equal(find(blocked, (n) => n.type === 'button').length, 0);
  assert.match(textOf(find(blocked, (n) => n.props.className === 'ws-noretry')[0]), /not available/);
});

test('in-flight upload explains that no scene exists yet; idle renders no status chrome', () => {
  assert.match(statusSurface(start().state).inFlight, /No scene yet/);
  const idle = find(render(initialLogged()), (n) => n.props.className === 'ws-status-surface')[0];
  assert.equal(idle.children.length, 0);
  assert.equal(layoutOf(initialState()).jobStatus.surface.failure, null); // layoutOf without opts still works
});

test('status module stays inside the workspace import boundary', () => {
  const imports = [...readFileSync(new URL('../../Build/web/src/workspace/status.mjs', import.meta.url), 'utf8').matchAll(/from '([^']+)'/g)].map((x) => x[1]);
  assert.deepEqual(imports, ['./workflow.mjs']);
});

test('S15ba D5: owner clip timeline ends "Clip result ready (no scene)"; scene jobs keep "Scene ready"', () => {
  const last = (st) => jobTimeline(st).at(-1).label;
  assert.equal(last({ phase: 'interview.active', owner: { jobId: 'x' } }), 'Clip result ready (no scene)');
  assert.equal(last({ phase: 'interview.active', owner: null }), 'Scene ready');
});
