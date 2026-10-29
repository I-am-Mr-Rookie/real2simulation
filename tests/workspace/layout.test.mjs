import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, readdirSync } from 'node:fs';
import { PHASES, initialState, reduce } from '../../Build/web/src/workspace/workflow.mjs';
import { deps, job, jobReady, jobFailed } from '../../Build/web/src/workspace/fixtures.mjs';
import { layoutOf, viewerRequestOf, SLOTS, STAGES, PHASE_LABEL, VIEWER_STATUS_TEXT, SYNTHETIC_SCENE_BANNER } from '../../Build/web/src/workspace/layout.mjs';
import { createViewport } from '../../Build/web/src/workspace/viewport.mjs';
import { renderWorkspace } from '../../Build/web/src/workspace/view.mjs';
// Viewer reached through its public modules only (adapter + loader contract), as the app composition would.
import { createViewerAdapter, checkViewerRequest } from '../../Build/web/src/viewer/adapter.mjs';
import { loadFixtureBundle } from '../viewer/fixture-bundle.mjs';

const run = (s, ...events) => events.reduce((a, e) => reduce(a, e, deps), s);
const withScene = () => run(initialState(), { type: 'UPLOAD_STARTED', jobId: 'synthetic-job-v1' }, { type: 'JOB_UPDATE', job: jobReady(1) });
const sceneB = { scene_id: 'synthetic-room-b', scene_version: '1.0.0', access: 'private', evidence: 'synthetic' };
const tick = () => new Promise((r) => setImmediate(r));
const until = async (arr, pred) => { for (let i = 0; i < 200 && !pred(arr); i++) await new Promise((r) => setTimeout(r, 10)); };

// Fake adapter honouring the public contract; records calls so the controller is tested in isolation.
function fakeAdapter({ manual = false } = {}) {
  const calls = [];
  return { calls, mount(host, request, svc) {
    const rec = { host, request, svc, disposed: 0 };
    calls.push(rec);
    const handle = { dispose() { rec.disposed++; } };
    if (manual) return new Promise((res) => { rec.resolve = () => res(handle); rec.reject = (e) => svc.signal.aborted ? res(handle) : (svc.onState('error'), svc.onError(e), res(Promise.reject(e))); });
    svc.onState('loading'); svc.onState('ready'); return Promise.resolve(handle);
  } };
}

test('layout: every phase maps to a labelled stage; slots fixed; exactly one current stage', () => {
  for (const p of PHASES) {
    assert.ok(PHASE_LABEL[p], p);
    const l = layoutOf({ ...initialState(), phase: p });
    assert.deepEqual(l.slots, SLOTS);
    assert.deepEqual(l.stages.map((s) => s.id), STAGES);
    assert.equal(l.stages.filter((s) => s.status === 'current').length, 1);
    const cur = l.stages.findIndex((s) => s.status === 'current');
    assert.ok(l.stages.slice(0, cur).every((s) => s.status === 'done') && l.stages.slice(cur + 1).every((s) => s.status === 'todo'));
  }
  assert.equal(Object.keys(PHASE_LABEL).length, PHASES.length);
});

test('layout: no scene -> no viewer request; failed upload flags its stage and surfaces the error', () => {
  const idle = layoutOf(initialState());
  assert.equal(idle.viewport.request, null); assert.equal(idle.viewport.key, null);
  const bad = run(initialState(), { type: 'UPLOAD_STARTED', jobId: 'synthetic-job-v1' }, { type: 'JOB_UPDATE', job: jobFailed(1) });
  const l = layoutOf(bad);
  assert.equal(l.stages[0].failed, true); assert.equal(l.viewport.request, null);
  assert.equal(l.jobStatus.error.code, 'PROCESSING_FAILED');
});

test('viewer request: schema-exact, passes the viewer checker, no job/owner ids, never mystery', () => {
  const s = withScene();
  const req = viewerRequestOf(s);
  assert.equal(checkViewerRequest(req), null);
  assert.deepEqual(Object.keys(req).sort(), ['audience', 'contract_version', 'kind', 'mode', 'scene']);
  assert.equal(req.mode, 'inspect'); assert.equal(req.audience, 'signed-in');
  assert.ok(!JSON.stringify(req).includes('synthetic-job-v1'));
  assert.notEqual(req.scene, s.scene); // copy, state not shared with the viewer
  assert.equal(layoutOf(s).viewport.banner, SYNTHETIC_SCENE_BANNER);
  // scene persists through the downstream phases, so the viewport stays mounted
  const later = run(s, { type: 'INTERVIEW_SPEC', spec: { synthetic: true } });
  assert.equal(layoutOf(later).viewport.key, layoutOf(s).viewport.key);
});

test('viewport: one mount per key, replace aborts+disposes old, destroy cleans up', async () => {
  const a = fakeAdapter(), seen = [];
  const vp = createViewport({ adapter: a, loadScene: () => {}, onStatus: (s) => seen.push(s.status) });
  const s1 = layoutOf(withScene()).viewport;
  vp.sync('H', s1.request, s1.key); vp.sync('H', s1.request, s1.key);
  await tick();
  assert.equal(a.calls.length, 1); assert.equal(a.calls[0].host, 'H');
  assert.deepEqual(seen, ['loading', 'loading', 'ready']);
  const req2 = { ...s1.request, scene: sceneB };
  vp.sync('H', req2, 'k2'); await tick();
  assert.equal(a.calls.length, 2); assert.equal(a.calls[0].disposed, 1); assert.ok(a.calls[0].svc.signal.aborted);
  vp.sync('H', null, null); await tick();
  assert.equal(a.calls[1].disposed, 1); assert.equal(seen.at(-1), 'empty');
  vp.sync('H', s1.request, s1.key); vp.destroy(); await tick();
  assert.equal(a.calls[2].disposed, 1);
});

test('viewport: a late mount of a replaced scene is disposed and silent', async () => {
  const a = fakeAdapter({ manual: true }), seen = [];
  const vp = createViewport({ adapter: a, loadScene: () => {}, onStatus: (s) => seen.push(s.status) });
  vp.sync('H', { scene: 1 }, 'k1');
  vp.sync('H', { scene: 2 }, 'k2');
  a.calls[0].resolve(); await tick();
  assert.equal(a.calls[0].disposed, 1);
  a.calls[1].svc.onState('ready'); a.calls[0].svc.onState('ready'); // stale callback ignored
  assert.deepEqual(seen, ['loading', 'loading', 'ready']);
  vp.destroy();
});

test('viewport: adapter failure surfaces code once; unexpected throw falls back to RENDER_FAILED', async () => {
  const a = fakeAdapter({ manual: true }), seen = [];
  const vp = createViewport({ adapter: a, loadScene: () => {}, onStatus: (s) => seen.push(s) });
  vp.sync('H', {}, 'k1');
  a.calls[0].reject({ code: 'LOAD_FAILED', message: 'Scene could not be loaded' }); await tick();
  assert.deepEqual(seen.at(-1), { status: 'error', error: { code: 'LOAD_FAILED', message: 'Scene could not be loaded' } });
  const n = seen.length;
  const vp2 = createViewport({ adapter: { mount: () => Promise.reject(new Error('boom')) }, loadScene: () => {}, onStatus: (s) => seen.push(s) });
  vp2.sync('H', {}, 'k'); await tick();
  assert.equal(seen.length, n + 2); assert.equal(seen.at(-1).error.code, 'RENDER_FAILED');
});

test('real viewer adapter: reducer scene mounts via public interface (fixture bundle, fake renderer); load failure maps', async () => {
  const bundle = await loadFixtureBundle({ validate: false });
  let disposed = 0, rendererHost = null;
  const adapter = createViewerAdapter({ createRenderer: (host) => { rendererHost = host; return { dispose() { disposed++; } }; } });
  const seen = [];
  const vp = createViewport({ adapter, loadScene: async () => bundle, onStatus: (s) => seen.push(s.status) });
  const l = layoutOf(withScene()).viewport;
  vp.sync('HOST', l.request, l.key); await until(seen, (a) => a.includes('ready'));
  assert.deepEqual(seen, ['loading', 'loading', 'ready']); assert.equal(rendererHost, 'HOST');
  vp.destroy(); assert.equal(disposed, 1);
  const bad = [];
  const vp2 = createViewport({ adapter, loadScene: async () => { throw new Error('network'); }, onStatus: (s) => bad.push(s) });
  vp2.sync('HOST', l.request, l.key); await until(bad, (a) => a.some((x) => x.status === 'error'));
  assert.equal(bad.at(-1).status, 'error'); assert.equal(bad.at(-1).error.code, 'LOAD_FAILED');
});

test('view: slot markup, viewer host has no children, aria, error and synthetic banner', () => {
  const h = (type, props, ...children) => ({ type, props: props ?? {}, children: children.flat().filter((c) => c != null) });
  const find = (n, pred, out = []) => { if (n && typeof n === 'object') { if (pred(n)) out.push(n); n.children.forEach((c) => find(c, pred, out)); } return out; };
  const l = layoutOf(withScene());
  const t = renderWorkspace(h, l, { status: 'ready', error: null }, 'REF');
  assert.deepEqual(find(t, (n) => n.props['data-slot']).map((n) => n.props['data-slot']), SLOTS);
  const host = find(t, (n) => n.props.className === 'ws-host')[0];
  assert.deepEqual(host.children, []); assert.equal(host.props.ref, 'REF'); assert.equal(host.props['data-viewer-status'], 'ready');
  assert.equal(find(t, (n) => n.props['aria-current'] === 'step').length, 1);
  assert.equal(find(t, (n) => n.props.role === 'note').length, 1);
  assert.equal(find(t, (n) => n.props.role === 'alert').length, 0);
  const e = renderWorkspace(h, l, { status: 'error', error: { code: 'LOAD_FAILED', message: 'x' } });
  assert.equal(find(e, (n) => n.props.role === 'alert')[0].children[0], 'LOAD_FAILED: x');
  for (const k of Object.keys(VIEWER_STATUS_TEXT)) assert.ok(VIEWER_STATUS_TEXT[k]);
});

test('boundary: workspace imports no viewer internals, shell, app, auth or Clerk', () => {
  const dir = 'Build/web/src/workspace/';
  for (const f of readdirSync(dir).filter((x) => x.endsWith('.mjs'))) {
    const imports = [...readFileSync(dir + f, 'utf8').matchAll(/^import .* from '([^']+)'/gm)].map((m) => m[1]);
    for (const i of imports) assert.match(i, /^\.\/|^\.\.\/lab\/fit-contract\.mjs$/, f + ' imports ' + i);
  }
});
