// S15t contract: REAL RM04 what-if spec response (S15r API evidence) -> REAL browser simulator -> REAL controller, whose
// fit/report requests go to the REAL FastAPI /fit and /report routes (tests/api-workspace/route_cli.py). The API fit output
// then feeds the REAL fit-view parser. Upload/job/questions are SYNTHETIC transport stubs only. Needs python with fastapi.
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { createController, API_BASE, browserSimulate } from '../../Build/web/src/workspace/controller.mjs';
import { runBrowserSimulation } from '../../Build/web/src/lab/browser-simulator.mjs';
import { fitView } from '../../Build/web/src/workspace/fit-view.mjs';
import { job, jobReady } from '../../Build/web/src/workspace/fixtures.mjs';

const root = fileURLToPath(new URL('../../', import.meta.url));
const spec = JSON.parse(fs.readFileSync(root + 'evidence/S15r/rm04-spec-response.json', 'utf8'));
const api = (path, body) => {
  const p = spawnSync('python', ['-B', root + 'tests/api-workspace/route_cli.py', path], { input: body, cwd: root, encoding: 'utf8' });
  assert.equal(p.status, 0, p.stderr);
  return JSON.parse(p.stdout);
};
const progress = (j) => ({ kind: 'job_progress', job_id: 'synthetic-job-v1', events: [], job: j });
const stub = { 'POST uploads': [201, { upload_id: 'up1', chunk_bytes: 64, committed_bytes: 0 }], 'PUT uploads/up1/chunks/0': [200, {}],
  'POST uploads/up1/complete': [200, { upload: { upload_id: 'up1', sha256: 'abcdef0123456789' }, job: job(0, 'queued') }],
  'GET jobs/synthetic-job-v1': [200, progress(jobReady(2))], 'GET scenes/synthetic-room-v1/questions': [200, { questions: [] }],
  'POST scenes/synthetic-room-v1/spec': [200, spec] };
const calls = {};
const fetch = async (url, init) => {
  const path = url.slice(API_BASE.length + 1).split('?')[0], key = init.method + ' ' + path;
  const { status, body } = ['fit', 'report'].includes(path) ? api(path, init.body) : { status: stub[key][0], body: stub[key][1] };
  calls[path] = { req: init.body, status, body };
  return { ok: status < 400, status, json: async () => body };
};

test('RM04 what-if: real /fit output passes the fit view and real /report renders it with the verbatim label', async () => {
  assert.equal(spec.validated_setup.what_if, true);
  const c = createController({ fetch, sleep: async () => {}, simulate: browserSimulate(runBrowserSimulation), newSessionId: () => 'fit-s15t' });
  await c.upload(new File([new Uint8Array(10)], 'synthetic.mp4', { type: 'video/mp4' }));
  await c.loadQuestions();
  await c.submitAnswers({});
  assert.equal(c.state.phase, 'run.ready', JSON.stringify(c.state.error));
  await c.run(1);
  assert.equal(c.state.phase, 'run.done', JSON.stringify(c.state.error));
  await c.fit();
  assert.equal(calls.fit.status, 200, JSON.stringify(calls.fit.body));
  assert.equal(c.state.phase, 'fit.done');
  const v = fitView(c.state, c.snapshot().fitInput);
  assert.equal(v.error, null);
  assert.match(v.rows[0].text, /^-?9\.8\d* .* m\/s\^2$/);
  assert.equal(v.residuals.length, JSON.parse(calls.fit.req).times.length);
  await c.openReport();
  assert.equal(calls.report.status, 200, JSON.stringify(calls.report.body));
  assert.equal(JSON.parse(calls.report.req).label, spec.what_if_label);
  assert.equal(c.state.phase, 'report.open');
  assert.ok(c.snapshot().report.html.includes(spec.what_if_label));
});
