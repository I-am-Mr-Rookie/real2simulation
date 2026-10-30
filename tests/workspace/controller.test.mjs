import test from 'node:test';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { createController, errorOf, API_BASE } from '../../Build/web/src/workspace/controller.mjs';
import { uploadView, renderUpload } from '../../Build/web/src/workspace/upload-view.mjs';
import { job, jobReady, observations, fitBody } from '../../Build/web/src/workspace/fixtures.mjs';

// SYNTHETIC fake BFF: routes 'METHOD path' -> (req) => [status, body]. Not API evidence.
function fakeFetch(routes) {
  const calls = [];
  const fetch = async (url, init) => {
    const path = url.slice(API_BASE.length + 1), key = init.method + ' ' + path.split('?')[0];
    const req = { path, init, body: typeof init.body === 'string' ? JSON.parse(init.body) : init.body };
    calls.push(req);
    const h = routes[key];
    if (!h) return { ok: false, status: 404, json: async () => ({ error: { code: 'NOT_FOUND', message: 'no route ' + key } }) };
    const [status, body] = h(req);
    return { ok: status < 400, status, json: async () => { if (body === undefined) throw new SyntaxError('no json'); return body; } };
  };
  return { fetch, calls };
}
const bytes = new Uint8Array([0, 0, 0, 24, 102, 116, 121, 112, 105, 115]); // 10 bytes, SYNTHETIC
const file = () => new File([bytes], 'synthetic.mp4', { type: 'video/mp4' });
const progress = (j, rev) => ({ contract_version: '1.0.0', kind: 'job_progress', job_id: 'synthetic-job-v1', after_revision: 0, events: [{ revision: rev, message: 'SYNTHETIC' }], job: j });
const SPEC = { synthetic: true }, SETUP = { synthetic: true, spec: { template: 'free_fall' } };
function happyRoutes() {
  let polls = 0;
  return {
    'POST uploads': () => [201, { upload_id: 'up1', chunk_bytes: 4, committed_bytes: 0 }],
    'PUT uploads/up1': () => [200, { kind: 'chunk_ack' }],
    'POST uploads/up1/complete': () => [200, { upload_id: 'up1', sha256: 'x', approved_clip: 'SYNTHETIC-CLIP' }],
    'POST jobs': () => [202, job(0, 'queued')],
    'GET jobs/synthetic-job-v1/progress': () => [200, (polls += 1) === 1 ? progress(job(1, 'running'), 1) : progress(jobReady(2), 2)],
    'GET scenes/synthetic-room-v1/questions': () => [200, { questions: [] }],
    'POST scenes/synthetic-room-v1/spec': () => [200, { ok: true, spec: SPEC, validated_setup: SETUP }],
    'POST fit': (r) => [200, fitBody(r.body.sessionId)],
    'POST report': () => [200, { status: 'html-print-fallback', html: '<p>SYNTHETIC report</p>' }],
  };
}
const make = (routes, extra = {}) => {
  const ff = fakeFetch(routes), phases = [];
  const c = createController({ fetch: ff.fetch, sleep: async () => {}, simulate: async (setup, seed) => (setup === SETUP && seed === 7 ? observations : []),
    newSessionId: () => 'fit-s1', onChange: (s) => phases.at(-1) !== s.state.phase && phases.push(s.state.phase), ...extra });
  return { c, ...ff, phases };
};

test('happy path drives upload.idle -> JOB_UPDATE(ready) -> INTERVIEW_SPEC -> RUN_COMPLETE -> FIT_RESULT -> REPORT_OPEN over PLAN §2 paths', async () => {
  const { c, calls, phases } = make(happyRoutes());
  assert.equal(c.state.phase, 'upload.idle');
  await c.upload(file());
  assert.equal(c.state.phase, 'interview.active');
  assert.equal(c.state.scene.scene_id, 'synthetic-room-v1');
  const puts = calls.filter((x) => x.init.method === 'PUT');
  assert.deepEqual(puts.map((x) => x.path), ['uploads/up1?offset=0', 'uploads/up1?offset=4', 'uploads/up1?offset=8']);
  assert.equal(puts[2].init.headers['x-chunk-sha256'], createHash('sha256').update(bytes.subarray(8)).digest('hex'));
  assert.equal(calls[0].body.sha256, createHash('sha256').update(bytes).digest('hex'));
  assert.equal(c.snapshot().upload.approvedClip, 'SYNTHETIC-CLIP');
  assert.equal(c.snapshot().events.length, 2);
  assert.ok(calls.some((x) => x.path === 'jobs/synthetic-job-v1/progress?after=1'));
  await c.loadQuestions();
  await c.submitAnswers({ q1: 'a' });
  assert.equal(c.state.phase, 'run.ready');
  await c.run(7);
  assert.equal(c.state.phase, 'run.done');
  assert.equal(c.state.run.label, 'simulated');
  await c.fit();
  assert.equal(c.state.phase, 'fit.done');
  assert.deepEqual(calls.find((x) => x.path === 'fit').body.observations, observations);
  await c.openReport();
  assert.equal(c.state.phase, 'report.open');
  assert.equal(c.snapshot().report.status, 'html-print-fallback');
  assert.deepEqual(phases, ['upload.idle', 'upload.queued', 'upload.running', 'interview.active', 'run.ready', 'run.running', 'run.done', 'fit.running', 'fit.done', 'report.open']);
  for (const x of calls) assert.equal(x.init.credentials, 'same-origin');
});

test('errorOf maps body codes first, then HTTP status, else DEPENDENCY_UNAVAILABLE', () => {
  const cases = [[401, null, 'UNAUTHORIZED'], [404, null, 'NOT_FOUND'], [422, null, 'INVALID_INPUT'], [413, null, 'INVALID_INPUT'], [402, null, 'SPEND_PAUSED'],
    [503, null, 'DEPENDENCY_UNAVAILABLE'], [500, { error: { code: 'SPEND_PAUSED', message: 'cap' } }, 'SPEND_PAUSED'],
    [409, { detail: { code: 'SPEND_PAUSED', message: 'floor' } }, 'SPEND_PAUSED'], [400, { error: { code: 'BOGUS' } }, 'INVALID_INPUT']];
  for (const [s, b, code] of cases) assert.equal(errorOf(s, b).code, code, s + JSON.stringify(b));
  assert.ok(errorOf(500, { error: { code: 'X', message: 'y'.repeat(999) } }).message.length <= 240);
});

test('upload errors keep the phase, create no job and inject no data', async () => {
  for (const [route, status, body, code] of [['POST uploads', 401, { error: { code: 'UNAUTHORIZED', message: 'sign in' } }, 'UNAUTHORIZED'],
    ['POST uploads/up1/complete', 422, { error: { code: 'INVALID_INPUT', message: 'not an approved clip' } }, 'INVALID_INPUT'],
    ['POST jobs', 402, { error: { code: 'SPEND_PAUSED', message: 'cap reached' } }, 'SPEND_PAUSED'],
    ['POST uploads', 502, undefined, 'DEPENDENCY_UNAVAILABLE']]) {
    const routes = { ...happyRoutes(), [route]: () => [status, body] };
    const { c } = make(routes);
    await c.upload(file());
    assert.equal(c.state.phase, 'upload.idle', route);
    assert.equal(c.state.error.code, code, route);
    assert.equal(c.state.job, null);
    assert.equal(c.state.scene, null);
    assert.equal(c.snapshot().busy, false);
  }
  const { c } = make({}, { fetch: async () => { throw new TypeError('network'); } });
  await c.upload(file());
  assert.equal(c.state.error.code, 'DEPENDENCY_UNAVAILABLE');
});

test('failed job, bad progress doc and poll timeout fail honestly', async () => {
  let r = make({ ...happyRoutes(), 'GET jobs/synthetic-job-v1/progress': () => [200, progress(job(1, 'failed', { error: { code: 'DEPENDENCY_UNAVAILABLE', message: 'no recorded run' } }), 1)] });
  await r.c.upload(file());
  assert.equal(r.c.state.phase, 'upload.failed');
  assert.equal(r.c.state.error.code, 'DEPENDENCY_UNAVAILABLE');
  r = make({ ...happyRoutes(), 'GET jobs/synthetic-job-v1/progress': () => [200, { kind: 'other' }] });
  await r.c.upload(file());
  assert.equal(r.c.state.error.code, 'PROCESSING_FAILED');
  assert.equal(r.c.state.scene, null);
  r = make({ ...happyRoutes(), 'GET jobs/synthetic-job-v1/progress': () => [200, progress(job(1, 'running'), 1)] }, { maxPolls: 3 });
  await r.c.upload(file());
  assert.equal(r.c.state.phase, 'upload.running');
  assert.equal(r.c.state.error.code, 'DEPENDENCY_UNAVAILABLE');
});

async function toRunReady(routes, extra) {
  const r = make({ ...happyRoutes(), ...routes }, extra);
  await r.c.upload(file());
  await r.c.submitAnswers({});
  return r;
}

test('spec rejection, missing simulator, fit transport error and invalid fit body show no numbers', async () => {
  let r = await toRunReady({ 'POST scenes/synthetic-room-v1/spec': () => [200, { ok: false, errors: ['mass must be positive'] }] });
  assert.equal(r.c.state.phase, 'interview.active');
  assert.deepEqual(r.c.state.error, { code: 'INVALID_INPUT', message: 'mass must be positive' });
  assert.equal(r.c.state.spec, null);

  r = await toRunReady({}, { simulate: undefined });
  await r.c.run(7);
  assert.equal(r.c.state.phase, 'run.failed');
  assert.equal(r.c.state.error.code, 'DEPENDENCY_UNAVAILABLE');
  assert.equal(r.c.state.run.observations, null);

  r = await toRunReady({ 'POST fit': () => [503, undefined] });
  await r.c.run(7); await r.c.fit();
  assert.equal(r.c.state.phase, 'fit.failed');
  assert.equal(r.c.state.error.code, 'DEPENDENCY_UNAVAILABLE');
  assert.equal(r.c.state.fit, null);

  r = await toRunReady({ 'POST fit': (q) => [200, { ...fitBody(q.body.sessionId), sessionId: 'someone-else' }] });
  await r.c.run(7); await r.c.fit();
  assert.equal(r.c.state.phase, 'fit.failed');
  assert.equal(r.c.state.fit, null);

  r = await toRunReady({ 'POST report': () => [200, { status: 'ok' }] });
  await r.c.run(7); await r.c.fit(); await r.c.openReport();
  assert.equal(r.c.state.phase, 'fit.done');
  assert.equal(r.c.state.error.code, 'PROCESSING_FAILED');
  assert.equal(r.c.snapshot().report, null);
});

// Minimal createElement stand-in: enough to inspect the accessible tree.
const h = (tag, props, ...kids) => ({ tag, props: props ?? {}, kids: kids.flat().filter((k) => k !== null && k !== undefined) });
const find = (n, pred, out = []) => { if (n && typeof n === 'object') { if (pred(n)) out.push(n); n.kids.forEach((k) => find(k, pred, out)); } return out; };

test('upload control: labelled, keyboard-reachable file input; busy disables; errors announced', () => {
  const base = { state: { phase: 'upload.idle', error: null }, busy: false, upload: null };
  let picked = null;
  const tree = renderUpload(h, uploadView(base), (f) => { picked = f; });
  const [input] = find(tree, (n) => n.tag === 'input');
  const [label] = find(tree, (n) => n.tag === 'label');
  assert.equal(input.props.type, 'file');
  assert.equal(label.props.htmlFor, input.props.id);
  assert.ok(typeof label.kids[0] === 'string' && label.kids[0].length > 0);
  assert.equal(input.props.disabled, false);
  assert.ok(!('tabIndex' in input.props) || input.props.tabIndex >= 0);
  for (const id of input.props['aria-describedby'].split(' ')) assert.equal(find(tree, (n) => n.props.id === id).length, 1, id);
  input.props.onChange({ target: { files: ['F'] } });
  assert.equal(picked, 'F');
  const busy = renderUpload(h, uploadView({ ...base, busy: true, upload: { name: 'a.mp4', committed: 5, total: 10 } }), () => {});
  assert.equal(find(busy, (n) => n.tag === 'input')[0].props.disabled, true);
  assert.equal(find(busy, (n) => n.tag === 'progress')[0].props.value, 50);
  const failed = renderUpload(h, uploadView({ state: { phase: 'upload.failed', error: { code: 'INVALID_INPUT', message: 'not approved' } } }), () => {});
  assert.equal(find(failed, (n) => n.props.role === 'alert')[0].kids[0], 'INVALID_INPUT: not approved');
  assert.equal(renderUpload(h, uploadView({ state: { phase: 'interview.active', error: null } }), () => {}), null);
});
