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
