// S15i evidence: render sidebar + report through the real React 19 binding (SSR); writes a static 375px preview. SYNTHETIC fixtures.
// Usage: node evidence/S15/nav-ssr-check.mjs <path-to-Build/web/node_modules>
import { createRequire } from 'node:module';
import assert from 'node:assert/strict';
import { readFileSync, writeFileSync } from 'node:fs';
import { createWorkspace } from '../../Build/web/src/workspace/react.mjs';
import { initialState } from '../../Build/web/src/workspace/workflow.mjs';

const req = createRequire(process.argv[2].replace(/[\\/]?$/, '/') + 'x.js');
const React = req('react'), { renderToString } = req('react-dom/server');
const Workspace = createWorkspace(React);
const report = JSON.parse(readFileSync('tests/workspace/fixtures/report-output.json', 'utf8')).report;
const state = { ...initialState(), phase: 'report.open', scene: { scene_id: 'synthetic-room-v1', scene_version: '1.0.0', access: 'public-library', evidence: 'synthetic' } };
const html = renderToString(React.createElement(Workspace, { state, adapter: {}, loadScene: () => {}, navigate: true, report, onAction: () => {} }));
assert.match(html, /data-nav="sidebar"/); assert.match(html, /class="ws-report"/); assert.match(html, /\(simulated\)/);
const css = readFileSync('Build/web/src/app/styles.css', 'utf8') + readFileSync('Build/web/src/workspace/workspace.css', 'utf8');
writeFileSync('evidence/S15/nav-preview.html', '<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>S15i nav preview (SYNTHETIC)</title><style>' + css + '</style><main>' + html + '</main>');
console.log('react', React.version, 'SSR ok', html.length, 'bytes');
