// S15h evidence: render fit table + residual chart through the real React 19 binding (SSR) and write a static 375px preview.
// Usage: node evidence/S15/fit-ssr-check.mjs <path-to-Build/web/node_modules>
import { createRequire } from 'node:module';
import assert from 'node:assert/strict';
import { readFileSync, writeFileSync } from 'node:fs';
import { createWorkspace } from '../../Build/web/src/workspace/react.mjs';
import { reduce, initialState } from '../../Build/web/src/workspace/workflow.mjs';
import { deps, jobReady, validSpec, runParameters, fixtureRunner } from '../../Build/web/src/workspace/fixtures.mjs';

const req = createRequire(process.argv[2].replace(/[\\/]?$/, '/') + 'x.js');
const React = req('react'), { renderToString } = req('react-dom/server');
const Workspace = createWorkspace(React);
const FIX = JSON.parse(readFileSync('tests/workspace/fixtures/fit-output.json', 'utf8'));
const fit = { times: FIX.request.times, output: FIX.output };
const evs = [{ type: 'UPLOAD_STARTED', jobId: 'synthetic-job-v1' }, { type: 'JOB_UPDATE', job: jobReady(1) }, { type: 'INTERVIEW_SPEC', spec: validSpec },
  { type: 'RUN_START', seed: 7 }, { type: 'RUN_COMPLETE', seed: 7, observations: fixtureRunner(runParameters, 7) }, { type: 'FIT_START', sessionId: 's15h' }];
const st = evs.reduce((s, e) => reduce(s, e, deps), initialState());
// Reducer fit.done needs a validated S11 reveal; reuse the state shape with a fit.done phase only for rendering this panel.
const state = { ...st, phase: 'fit.done' };
const html = renderToString(React.createElement(Workspace, { state, adapter: {}, loadScene: () => {}, fit }));
assert.match(html, /class="ws-fit"/); assert.match(html, /Residual chart \(simulated\)/);
assert.equal(html.split('<circle').length - 1, FIX.output.fit.residuals.length);
const css = readFileSync('Build/web/src/app/styles.css', 'utf8') + readFileSync('Build/web/src/workspace/workspace.css', 'utf8');
writeFileSync('evidence/S15/fit-preview.html', '<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>S15h fit preview (SYNTHETIC)</title><style>' + css + '</style><main>' + html + '</main>');
console.log('react', React.version, 'SSR ok', html.length, 'bytes');
