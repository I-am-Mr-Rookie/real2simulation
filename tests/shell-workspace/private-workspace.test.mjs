// S04o: PrivateWorkspace host wiring. Probe decides live vs honest-unavailable; onAction routes to controller/reducers.
import test from 'node:test';
import assert from 'node:assert/strict';
import { workspaceHeading, probeApi, routeAction, UNAVAILABLE_NOTICE, INSTRUMENTS_UNAVAILABLE } from '../../Build/web/src/shell/PrivateWorkspace.mjs';
import { createController } from '../../Build/web/src/workspace/controller.mjs';
import { initialInterview } from '../../Build/web/src/workspace/interview.mjs';
import { initialInstruments } from '../../Build/web/src/workspace/instruments.mjs';

const res = (status, body) => async () => ({ status, ok: status < 300, json: async () => { if (body === undefined) throw new Error('no json'); return body; } });

test('probe: API JSON answer (even 404) is live; auth, 5xx, non-JSON and network failure are unavailable', async () => {
  assert.equal(await probeApi(res(404, { detail: { code: 'NOT_FOUND', message: 'job not found' } })), 'live');
  assert.equal(await probeApi(res(200, { kind: 'job_progress' })), 'live');
  for (const f of [res(401, { error: { code: 'UNAUTHORIZED' } }), res(502, { error: { code: 'DEPENDENCY_UNAVAILABLE' } }), res(404, undefined), async () => { throw new Error('down'); }])
    assert.equal(await probeApi(f), 'unavailable');
  assert.match(UNAVAILABLE_NOTICE, /unavailable/);
});

test('probe hits the BFF path with same-origin credentials', async () => {
  let seen;
  await probeApi(async (url, init) => { seen = { url, init }; return { status: 404, json: async () => ({}) }; });
  assert.equal(seen.url, '/api/workspace/health');
  assert.equal(seen.init.credentials, 'same-origin');
});

test('routeAction: workflow events reach the controller, unknown fetch failures never fabricate data', async () => {
  const calls = [];
  const ctl = createController({ fetch: async (url, init) => { calls.push(init.method + ' ' + url); return { status: 503, ok: false, json: async () => ({}) }; } });
  const local = { interview: initialInterview(), instruments: initialInstruments() };
  assert.equal(await routeAction(ctl, local, { type: 'FIT_START' }), local); // illegal from upload.idle: no request
  assert.equal(await routeAction(ctl, local, { type: 'REPORT_OPEN' }), local); // S15s: report needs fit.done; no request
  assert.deepEqual(calls, []);
  assert.equal(ctl.state.phase, 'upload.idle');
  await routeAction(ctl, local, { type: 'RUN_START' });
  assert.equal(ctl.state.fit ?? null, null);
});

test('routeAction: Q_* go to the interview reducer, I_MEASURE fails honestly without an instrument service', async () => {
  const ctl = createController({ fetch: async () => { throw new Error('no network expected'); } });
  const local = { interview: initialInterview(), instruments: initialInstruments() };
  const q = await routeAction(ctl, local, { type: 'Q_CHIP', chipId: 'x' });
  assert.equal(q.interview, local.interview); // illegal with no questions: same object
  const i = await routeAction(ctl, local, { type: 'I_SELECT', instrument: 'ruler' });
  assert.equal(i.instruments.selected, 'ruler');
  const m = await routeAction(ctl, { ...local, instruments: i.instruments }, { type: 'I_MEASURE' });
  assert.equal(m.instruments.trials.length, 0); // not run.done: no reading, nothing invented
  assert.match(INSTRUMENTS_UNAVAILABLE, /not available in this build/);
});


test('S15ba D7/D8: scene label only with a loaded scene; live title is "Private workspace"', async () => {
  const { readFile } = await import('node:fs/promises');
  const src = await readFile(new URL('../../Build/web/src/shell/PrivateWorkspace.mjs', import.meta.url), 'utf8');
  assert.match(src, /live && s\.state\.scene \? React\.createElement\('p', \{ role: 'note', 'data-scene-label'/);
  assert.match(src, /title: workspaceHeading\(api, scene\)/);
});

test('heading: no fixture wording while checking or live', () => {
  const scene = { title: 'Private development fixture' };
  assert.equal(workspaceHeading('checking', scene), 'Workspace');
  assert.equal(workspaceHeading('live', scene), 'Private workspace');
  assert.equal(workspaceHeading('unavailable', scene), scene.title);
});
