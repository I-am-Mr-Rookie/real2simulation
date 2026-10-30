// S15q: the exact spec body the live web sends for the RM04 interview (real reducers + real controller + real PrivateWorkspace
// routeAction). rm04-questions.json = Build.agent.interview.questions() for the recorded RM04 free_fall job; the produced body is
// pinned in rm04-spec-body.json, which tests/api-workspace/test_spec_web_body.py posts to the real analysis router.
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { initialInterview } from '../../Build/web/src/workspace/interview.mjs';
import { createController, specAnswers } from '../../Build/web/src/workspace/controller.mjs';
import { routeAction } from '../../Build/web/src/shell/PrivateWorkspace.mjs';
import { jobReady } from '../../Build/web/src/workspace/fixtures.mjs';
import { initialInstruments } from '../../Build/web/src/workspace/instruments.mjs';
import { layoutOf } from '../../Build/web/src/workspace/layout.mjs';
import { renderWorkspace } from '../../Build/web/src/workspace/view.mjs';

const fx = (n) => JSON.parse(readFileSync(new URL('./fixtures/' + n, import.meta.url), 'utf8'));
const QS = fx('rm04-questions.json'), BODY = fx('rm04-spec-body.json');
const h = (type, props, ...children) => ({ type, props: props ?? {}, children: children.flat(Infinity) });
const strings = (n) => (typeof n === 'string' ? [n] : n?.children?.flatMap(strings) ?? []);

function walk(reply) {
  const calls = [];
  const f = async (url, init) => { calls.push({ url, body: init.body && JSON.parse(init.body) }); return reply(); };
  const ctl = createController({ fetch: f, onChange: () => {} });
  ctl.dispatch({ type: 'UPLOAD_STARTED', jobId: 'synthetic-job-v1' });
  ctl.dispatch({ type: 'JOB_UPDATE', job: jobReady(1) });
  assert.equal(ctl.state.phase, 'interview.active');
  return { ctl, calls };
}
async function answer(ctl) {
  let local = { interview: initialInterview(), instruments: initialInstruments() };
  for (const a of [{ type: 'Q_LOADED', response: QS, sceneId: QS.scene_id }, { type: 'Q_TEXT', text: '1.5' }, { type: 'Q_SUBMIT' },
    { type: 'Q_CHIP', chipId: 'at-rest' }, { type: 'Q_SUBMIT' }]) local = await routeAction(ctl, local, a);
  return local;
}
const json = (status, body) => () => ({ ok: status < 300, status, json: async () => body });

test('RM04 interview -> POST spec body is the answers_to_spec object shape (pinned fixture)', async () => {
  const { ctl, calls } = walk(json(200, { ok: true, spec: { t: 1 }, validated_setup: { t: 1 }, label: 'scale unverified, not setup-validated' }));
  await answer(ctl);
  const spec = calls.filter((c) => c.url.endsWith('/spec'));
  assert.equal(spec.length, 1);
  assert.deepEqual(spec[0].body, BODY);
  assert.deepEqual(BODY, { answers: { drop_height: { text: '1.5' }, initial_vertical_velocity: { chip: 'at-rest' } } });
  assert.equal(ctl.state.phase, 'run.ready');
  assert.equal(ctl.snapshot().specLabel, 'scale unverified, not setup-validated');
});

test('specAnswers: exactly one key per answer, chip wins over text', () => {
  assert.deepEqual(specAnswers([{ questionId: 'a', chipId: 'c', text: 'x' }, { questionId: 'b', chipId: null, text: '2' }]),
    { a: { chip: 'c' }, b: { text: '2' } });
});

test('spec 422 is visible in the stage panel with code, message and a working Retry', async () => {
  let status = 422;
  const { ctl, calls } = walk(() => (status === 422
    ? { ok: false, status, json: async () => ({ detail: { code: 'INVALID_INPUT', message: 'spec did not validate', errors: ['$.x: bad'] } }) }
    : json(200, { ok: true, spec: { t: 1 }, validated_setup: { t: 1 } })()));
  const local = await answer(ctl);
  assert.equal(ctl.state.phase, 'interview.active');
  const tree = renderWorkspace(h, layoutOf(ctl.state, { audience: 'signed-in' }), { status: 'error', error: { code: 'LOAD_FAILED', message: 'Scene could not be loaded' } }, null, () => {});
  const panel = tree.children.find((c) => c?.props['data-slot'] === 'panel');
  assert.ok(strings(panel).includes('INVALID_INPUT: spec did not validate: $.x: bad'));
  assert.ok(strings(panel).includes('Retry'));
  const aside = strings(tree.children.find((c) => c?.props['data-slot'] === 'job-status'));
  assert.ok(aside.includes('LOAD_FAILED: Scene could not be loaded') && aside.includes('INVALID_INPUT: spec did not validate: $.x: bad')); // viewer error no longer masks it
  status = 200;
  await routeAction(ctl, local, { type: 'SPEC_RETRY' });
  assert.equal(calls.filter((c) => c.url.endsWith('/spec')).length, 2);
  assert.equal(ctl.state.phase, 'run.ready');
  assert.equal(ctl.state.error, null);
});

test('RECORDED provenance stage labels and UTC render in the job panel', () => {
  const { ctl } = walk(json(200, {}));
  const prov = { executor: 'recorded', label: 'RECORDED S13h-orch46', live: false, stage_labels: { keyframes: 'RECORDED S13h-orch46', understand: 'RECORDED S14g-fix3' },
    understand: { recorded_utc: '2026-10-29T00:00:00Z' }, note: 'replay; not a live run' };
  const tree = renderWorkspace(h, layoutOf(ctl.state, { audience: 'signed-in' }), { status: 'empty', error: null }, null, undefined,
    undefined, undefined, undefined, undefined, undefined, undefined, undefined, prov);
  const aside = strings(tree.children.find((c) => c?.props['data-slot'] === 'job-status')).join('|');
  assert.match(aside, /RECORDED S13h-orch46 \(not a live run\)/);
  assert.match(aside, /understand: RECORDED S14g-fix3 @ 2026-10-29T00:00:00Z/);
});

