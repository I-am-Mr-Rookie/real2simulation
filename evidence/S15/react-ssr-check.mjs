// S15b evidence: render the React binding with real React 19 (SSR) and assert slot markup. React is resolved from
// the canonical Build/web/node_modules (read-only, no install). Usage: node evidence/S15/react-ssr-check.mjs <path-to-Build/web/node_modules>
import { createRequire } from 'node:module';
import assert from 'node:assert/strict';
import { readFileSync, writeFileSync } from 'node:fs';
import { createWorkspace } from '../../Build/web/src/workspace/react.mjs';
import { initialState, reduce } from '../../Build/web/src/workspace/workflow.mjs';
import { jobReady } from '../../Build/web/src/workspace/fixtures.mjs';

const req = createRequire(process.argv[2].replace(/[\\/]?$/, '/') + 'x.js');
const React = req('react'), { renderToString } = req('react-dom/server');
const Workspace = createWorkspace(React);
const adapter = { mount: () => assert.fail('SSR must not mount') };
const render = (state) => renderToString(React.createElement(Workspace, { state, adapter, loadScene: () => {} }));

const idle = render(initialState());
for (const slot of ['stage-nav', 'viewport', 'panel', 'job-status']) assert.match(idle, new RegExp('data-slot="' + slot + '"'));
assert.match(idle, /data-viewer-status="empty"/); assert.match(idle, /aria-current="step"/); assert.doesNotMatch(idle, /SYNTHETIC/);
const withScene = reduce(reduce(initialState(), { type: 'UPLOAD_STARTED', jobId: 'synthetic-job-v1' }), { type: 'JOB_UPDATE', job: jobReady(1) });
const html = render(withScene);
assert.match(html, /SYNTHETIC scene/); assert.match(html, /<div class="ws-host"[^>]*><\/div>/); assert.match(html, /Job synthetic-job-v1/);
// Static preview for a manual responsive check (viewer canvas absent: the host is an empty dark box).
const css = readFileSync('Build/web/src/app/styles.css', 'utf8') + readFileSync('Build/web/src/workspace/workspace.css', 'utf8');
writeFileSync('evidence/S15/layout-preview.html', '<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>S15b layout preview (SYNTHETIC)</title><style>' + css + '</style><main>' + html + '</main>');
console.log('react', React.version, 'SSR ok; idle', idle.length, 'bytes, scene', html.length, 'bytes');

// S15c: failure surface through the real React binding (SSR).
import { initialLogged as IL, reduceLogged as RL } from '../../Build/web/src/workspace/status.mjs';
import { job as jobF } from '../../Build/web/src/workspace/fixtures.mjs';
{
  let m = IL();
  for (const e of [{ type: 'UPLOAD_STARTED', jobId: 'synthetic-job-v1' }, { type: 'JOB_UPDATE', job: jobF(1, 'running') },
    { type: 'JOB_UPDATE', job: jobF(2, 'failed', { error: { code: 'DEPENDENCY_UNAVAILABLE', message: 'SYNTHETIC failure fixture' } }) }]) m = RL(m, e);
  const out = renderToString(React.createElement(Workspace, { state: m.state, log: m.log, onAction: () => {}, adapter, loadScene: () => {} }));
  for (const re of [/class="ws-timeline"/, /data-status="failed"/, /Job update r2: failed/, /Upload failed/, /Retrying later may work/, /Not available: Scene: none was created/, /data-event="UPLOAD_STARTED"/, /Start a new upload/])
    assert.match(out, re);
  assert.doesNotMatch(out, /disabled=""/);
  const noRetry = renderToString(React.createElement(Workspace, { state: RL(RL(IL(), { type: 'UPLOAD_STARTED', jobId: 'synthetic-job-v1' }), { type: 'JOB_UPDATE', job: jobF(1, 'failed', { error: { code: 'SPEND_PAUSED', message: 'SYNTHETIC' } }) }).state, adapter, loadScene: () => {} }));
  assert.doesNotMatch(noRetry, /ws-retry/); assert.match(noRetry, /Retry is not available/);
  writeFileSync('evidence/S15/failure-preview.html', '<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>S15c failure preview (SYNTHETIC)</title><style>' + css + '</style><main>' + out + '</main>');
  console.log('S15c SSR ok: failure surface, retry button, blocked-retry copy');
}

