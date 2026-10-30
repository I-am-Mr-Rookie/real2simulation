import test from 'node:test';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { createController, errorOf, API_BASE, browserSimulate } from '../../Build/web/src/workspace/controller.mjs';
import { runBrowserSimulation } from '../../Build/web/src/lab/browser-simulator.mjs';
import { reportView, renderReport } from '../../Build/web/src/workspace/navigation.mjs';
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
// SYNTHETIC body in the real fitter.api.fit_observations shape (top-level gravity/uncertainty, no sessionId).
const apiFit = (gravity = { value: 9.8, unit: 'm/s^2', uncertainty: 0.1, source: { label: 'simulated', evidence: 'SYNTHETIC' } }) => ({ status: 'ok',
  fit: { degree: 2, rmse: 0.01, n: 3, source: { label: 'simulated', evidence: 'SYNTHETIC' } }, gravity,
  uncertainty: { model: 'independent_position_time_first_order', assumptions: ['SYNTHETIC'], quantity_uncertainty: 'standard uncertainty (one sigma), not a 95% interval' } });
function happyRoutes() {
  let polls = 0;
  return {
    'POST uploads': () => [201, { upload_id: 'up1', chunk_bytes: 4, committed_bytes: 0 }],
    'PUT uploads/up1/chunks/0': () => [200, { kind: 'chunk_ack' }],
    'PUT uploads/up1/chunks/4': () => [200, { kind: 'chunk_ack' }],
    'PUT uploads/up1/chunks/8': () => [200, { kind: 'chunk_ack' }],
    // S13i: complete returns {upload, job, provenance}; no POST /jobs
    'POST uploads/up1/complete': () => [200, { upload: { upload_id: 'up1', sha256: 'abcdef0123456789' }, job: job(0, 'queued'), provenance: { label: 'SYNTHETIC' } }],
    'GET jobs/synthetic-job-v1': () => [200, (polls += 1) === 1 ? progress(job(1, 'running'), 1) : progress(jobReady(2), 2)],
    'GET scenes/synthetic-room-v1/questions': () => [200, { questions: [] }],
    'POST scenes/synthetic-room-v1/spec': () => [200, { ok: true, spec: SPEC, validated_setup: SETUP, label: 'scale unverified, not setup-validated' }],
    'POST fit': () => [200, apiFit()],
    'POST report': () => [200, { status: 'html-print-fallback', labels: ['simulated'], fitter_digest: 'x', html: '<p>SYNTHETIC report</p>' }],
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
  assert.deepEqual(puts.map((x) => x.path), ['uploads/up1/chunks/0', 'uploads/up1/chunks/4', 'uploads/up1/chunks/8']);
  assert.ok(!calls.some((x) => x.path === 'jobs'));
  assert.equal(puts[2].init.headers['x-chunk-sha256'], createHash('sha256').update(bytes.subarray(8)).digest('hex'));
  assert.equal(calls[0].body.sha256, createHash('sha256').update(bytes).digest('hex'));
  assert.equal(c.snapshot().upload.approvedClip, 'sha256 abcdef012345');
  assert.equal(c.snapshot().provenance.label, 'SYNTHETIC');
  assert.equal(c.snapshot().events.length, 2);
  assert.ok(calls.some((x) => x.path === 'jobs/synthetic-job-v1?after=1'));
  await c.loadQuestions();
  await c.submitAnswers({ q1: 'a' });
  assert.equal(c.state.phase, 'run.ready');
  await c.run(7);
  assert.equal(c.state.phase, 'run.done');
  assert.equal(c.state.run.label, 'simulated');
  await c.fit();
  assert.equal(c.state.phase, 'fit.done');
  const fitReq = calls.find((x) => x.path === 'fit').body;
  assert.deepEqual(Object.keys(fitReq).sort(), ['positions', 'times']); // fitter rejects unknown fields
  assert.deepEqual(fitReq.times.map((t) => t.value), observations.map((o) => o.time_s));
  assert.deepEqual(fitReq.positions.map((t) => [t.value, t.unit, t.source.label]), observations.map((o) => [o.position_m, 'm', 'simulated']));
  assert.equal(c.state.fit.value, 9.8);
  await c.openReport();
  assert.deepEqual(calls.find((x) => x.path === 'report').body.fit, apiFit()); // raw fitter result, as the API requires
  assert.equal(c.state.phase, 'report.open');
  assert.equal(c.snapshot().report.status, 'html-print-fallback');
  assert.equal(c.snapshot().report.specLabel, 'scale unverified, not setup-validated');
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
    ['PUT uploads/up1/chunks/4', 402, { error: { code: 'SPEND_PAUSED', message: 'cap reached' } }, 'SPEND_PAUSED'],
    ['POST uploads/up1/complete', 200, { upload: { upload_id: 'up1' }, job: { status: 'queued' } }, 'PROCESSING_FAILED'],
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
  let r = make({ ...happyRoutes(), 'GET jobs/synthetic-job-v1': () => [200, progress(job(1, 'failed', { error: { code: 'DEPENDENCY_UNAVAILABLE', message: 'no recorded run' } }), 1)] });
  await r.c.upload(file());
  assert.equal(r.c.state.phase, 'upload.failed');
  assert.equal(r.c.state.error.code, 'DEPENDENCY_UNAVAILABLE');
  r = make({ ...happyRoutes(), 'GET jobs/synthetic-job-v1': () => [200, { kind: 'other' }] });
  await r.c.upload(file());
  assert.equal(r.c.state.error.code, 'PROCESSING_FAILED');
  assert.equal(r.c.state.scene, null);
  r = make({ ...happyRoutes(), 'GET jobs/synthetic-job-v1': () => [200, progress(job(1, 'running'), 1)] }, { maxPolls: 3 });
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

  r = await toRunReady({ 'POST fit': () => [200, apiFit(null)] }); // covariance unavailable -> no gravity -> no number
  await r.c.run(7); await r.c.fit();
  assert.equal(r.c.state.phase, 'fit.failed');
  assert.equal(r.c.state.fit, null);

  r = await toRunReady({ 'POST fit': () => [200, fitBody('fit-s1')] }); // legacy lab envelope is not the API shape
  await r.c.run(7); await r.c.fit();
  assert.equal(r.c.state.phase, 'fit.failed');

  r = await toRunReady({ 'POST report': () => [200, { status: 'ok' }] });
  await r.c.run(7); await r.c.fit(); await r.c.openReport();
  assert.equal(r.c.state.phase, 'fit.done');
  assert.equal(r.c.state.error.code, 'PROCESSING_FAILED');
  assert.equal(r.c.snapshot().report, null);
});

test('browserSimulate: real runBrowserSimulation fails closed on a non-artifact setup; samples map to world-Y observations', async () => {
  await assert.rejects(browserSimulate(runBrowserSimulation)({ template: 'free_fall' }), /INVALID_BROWSER_SIMULATION/);
  const fake = (p) => (p.mode === 'normal' && p.validatedSetup === SETUP ? { samples: [{ time_s: 0, position_m: [0, 2, 0] }, { time_s: 0.1, position_m: [0, 1.95, 0] }] } : null);
  assert.deepEqual(await browserSimulate(fake)(SETUP), [{ time_s: 0, position_m: 2 }, { time_s: 0.1, position_m: 1.95 }]);
  const r = await toRunReady({}, { simulate: browserSimulate(runBrowserSimulation) });
  await r.c.run(7);
  assert.equal(r.c.state.phase, 'run.failed');
  assert.equal(r.c.state.run.observations, null);
});

test('report view: html-print-fallback renders only in a sandboxed srcdoc iframe with server labels; bad shape rejected', () => {
  const open = { phase: 'report.open' };
  const v = reportView(open, { status: 'html-print-fallback', html: '<p>SYNTHETIC</p>', labels: ['simulated'], specLabel: 'scale unverified, not setup-validated' });
  assert.equal(v.error, null);
  const tree = renderReport(h, v);
  const frame = find(tree, (n) => n.tag === 'iframe')[0];
  assert.equal(frame.props.sandbox, '');
  assert.equal(frame.props.srcDoc, '<p>SYNTHETIC</p>');
  assert.match(JSON.stringify(tree), /SIMULATED/);
  assert.match(JSON.stringify(tree), /scale unverified, not setup-validated/);
  assert.match(reportView(open, { status: 'html-print-fallback', html: '<p>x</p>', labels: [1] }).error, /rejected/);
});

// Minimal createElement stand-in: enough to inspect the accessible tree.
const h = (tag, props, ...kids) => ({ tag, props: props ?? {}, kids: kids.flat().filter((k) => k !== null && k !== undefined) });

// S15r (owner Q20=A): SYNTHETIC numbers in the API what-if artifact shape (analysis._what_if_artifact); real simulator, fake BFF.
test('what-if: artifact runs in labelled what-if mode, report request carries the label, panel shows label and run-failure reason', async () => {
  const { WHAT_IF_LABEL } = await import('../../Build/web/src/lab/browser-simulator.mjs');
  const { renderWorkspace } = await import('../../Build/web/src/workspace/view.mjs');
  const qq = (value, unit) => ({ value, unit });
  const spec = { template: 'free_fall', scene: { scene_id: 'RM04', schema_version: '1.0.0' },
    environment: { gravity: qq(9.81, 'm/s^2'), gravity_direction: [0, -1, 0] }, placement: { origin: qq([0, 1.5, 0], 'm') },
    parameters: { drop_height: qq(1.5, 'm'), initial_vertical_velocity: qq(0, 'm/s') }, simulation: { duration: qq(0.5, 's'), time_step: qq(0.01, 's') } };
  const art = { artifact_version: 's15r-what-if-setup-v1', validation: 'numeric_contract_only', what_if: true, label: WHAT_IF_LABEL, spec,
    scene: { id: 'RM04', schema_version: '1.0.0', synthetic: false, scale_verified: false } };
  const r = await toRunReady({ 'POST scenes/synthetic-room-v1/spec': () => [200, { ok: true, spec, validated_setup: art, label: 'scale unverified, not setup-validated', setup_validated: false }] },
    { simulate: browserSimulate(runBrowserSimulation) });
  assert.equal(r.c.snapshot().whatIfLabel, WHAT_IF_LABEL);
  await r.c.run(1);
  assert.equal(r.c.state.phase, 'run.done');
  assert.ok(r.c.state.run.observations.length > 1);
  const layout = (phase, error = null) => ({ phase, stages: [], viewport: { banner: null }, jobStatus: { label: 'x', jobId: null, error, surface: null } });
  const text = (t) => JSON.stringify(t);
  // S15s: reach fit and report through the rendered next-step buttons and the real host router (PrivateWorkspace.routeAction)
  const { routeAction } = await import('../../Build/web/src/shell/PrivateWorkspace.mjs');
  const { runView, initialRun } = await import('../../Build/web/src/workspace/runcontrol.mjs');
  const local = { interview: null, instruments: null };
  const render = () => renderWorkspace(h, layout(r.c.state.phase), { status: 'idle', error: null }, null, (a) => routeAction(r.c, local, a),
    null, null, runView(r.c.state, initialRun()), null, null, null, r.c.snapshot().report ? reportView(r.c.state, r.c.snapshot().report) : null, null, WHAT_IF_LABEL);
  const next = (t) => find(t, (n) => n.props['data-slot'] === 'next-step');
  const click = async (label) => {
    const t = render(), b = find(next(t)[0], (n) => n.tag === 'button');
    assert.equal(b.length, 1); assert.equal(b[0].kids[0], label);
    assert.match(text(t), /SIMULATED what-if of your described setup/);
    await b[0].props.onClick();
  };
  await click('Fit');
  assert.equal(r.c.state.phase, 'fit.done');
  assert.equal(r.calls.filter((x) => x.path === 'fit').length, 1);
  await click('Open report');
  assert.equal(r.c.state.phase, 'report.open');
  assert.equal(r.calls.find((x) => x.path === 'report').body.label, WHAT_IF_LABEL);
  const rep = render();
  assert.deepEqual(next(rep), []); // no forward control once the report is open
  assert.match(text(rep), /SIMULATED what-if of your described setup/);
  assert.ok(find(rep, (n) => n.tag === 'iframe').length === 1, 'report shown in the sandboxed iframe');
  for (const phase of ['upload.idle', 'interview.active', 'run.ready', 'run.running', 'run.paused', 'run.failed', 'fit.running', 'fit.failed', 'report.open'])
    assert.equal(runView({ phase, run: null }, initialRun()).next, null, phase);
  assert.match(text(renderWorkspace(h, layout('fit.done'), { status: 'idle', error: null }, null, null, null, null, null, null, null, null, null, null, WHAT_IF_LABEL)), /SIMULATED what-if of your described setup; scale unverified; not measured from the clip/);
  const failed = renderWorkspace(h, layout('run.failed', { code: 'PROCESSING_FAILED', message: 'INVALID_BROWSER_SIMULATION: bad horizon' }), { status: 'idle', error: null }, null, null, null, null, null, null, null, null, null, null);
  const panel = find(failed, (n) => n.props['aria-label'] === 'Stage panel')[0];
  assert.match(text(panel), /INVALID_BROWSER_SIMULATION: bad horizon/);
  // an S10-shaped setup still goes through normal mode, which rejects a non-synthetic scene
  const bad = await toRunReady({ 'POST scenes/synthetic-room-v1/spec': () => [200, { ok: true, spec, validated_setup: { ...art, what_if: false }, label: 'x' }] },
    { simulate: browserSimulate(runBrowserSimulation) });
  await bad.c.run(1);
  assert.equal(bad.c.state.phase, 'run.failed');
  assert.match(bad.c.state.error.message, /untrusted validated artifact/);
});

const find = (n, pred, out = []) => { if (n && typeof n === 'object') { if (pred(n)) out.push(n); n.kids.forEach((k) => find(k, pred, out)); } return out; };

test('S15s normal path: run.done -> Fit -> fit.done -> Open report -> report.open via runView.next and the host router', async () => {
  const { routeAction } = await import('../../Build/web/src/shell/PrivateWorkspace.mjs');
  const { runView, initialRun } = await import('../../Build/web/src/workspace/runcontrol.mjs');
  const r = await toRunReady({});
  await r.c.run(7);
  for (const [from, event, label, to] of [['run.done', 'FIT_START', 'Fit', 'fit.done'], ['fit.done', 'REPORT_OPEN', 'Open report', 'report.open']]) {
    assert.equal(r.c.state.phase, from);
    assert.deepEqual(runView(r.c.state, initialRun()).next, { event, label });
    await routeAction(r.c, {}, { type: event });
    assert.equal(r.c.state.phase, to);
  }
  assert.equal(r.c.snapshot().report.html, '<p>SYNTHETIC report</p>');
});

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
