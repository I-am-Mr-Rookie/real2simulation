// S15ah static SSR evidence: workspace shell in light + dark (1280, 375). Synthetic fixture, not a measurement.
import { createRequire } from 'node:module';
import { readFileSync, writeFileSync } from 'node:fs';
import { renderShell, toolsOf } from '../../Build/web/src/shell/workspace-shell.mjs';
import { renderUpload } from '../../Build/web/src/workspace/upload-view.mjs';
const require = createRequire(new URL('../../Build/web/package.json', import.meta.url));
const React = require('react'); const { renderToStaticMarkup } = require('react-dom/server');
const h = React.createElement;
const tools = toolsOf({ live: true, phase: 'interview.active', owner: false, jobId: 'synthetic-job', uploadStatus: null, hasReport: false, pending: 2 });
const css = ['app/styles.css', 'workspace/workspace.css'].map((f) => readFileSync(new URL('../../Build/web/src/' + f, import.meta.url), 'utf8')).join('\n');
const stage = (label, st, cur) => h('li', { 'data-status': st, 'aria-current': cur ? 'step' : undefined }, label);
const ws = h('div', { className: 'ws' },
  h('nav', { className: 'ws-stages', 'aria-label': 'Workspace stages' }, h('ol', null, stage('Upload', 'done'), stage('Interview', 'current', true), stage('Run', 'todo'), stage('Fit', 'todo'), stage('Report', 'todo'))),
  h('section', { id: 'ws-viewport', className: 'ws-viewport', 'aria-label': 'Scene viewport' }, h('div', { className: 'ws-host', 'data-viewer-status': 'empty' })),
  h('section', { id: 'ws-panel', className: 'ws-panel' }, h('h2', null, 'Result (RECORDED, owner clip, scale unverified)'), h('p', null, 'Static synthetic fixture render, not a measurement.')),
  h('div', { id: 'ws-job', className: 'ws-job' }, h('p', null, 'SIMULATED what-if; Held-out caveat; FIXTURE')));
const probe = '<script>(()=>{const d=document.documentElement;document.title="PROBE theme="+d.dataset.theme+" docScroll="+d.scrollWidth+"/"+d.clientWidth+" bg="+getComputedStyle(document.body).backgroundColor})()</script>';
for (const theme of ['light', 'dark']) for (const right of [true, false]) {
  const page = renderToStaticMarkup(renderShell(h, { title: 'Static S15ah render (synthetic fixture, not a measurement)', rail: { pane: 'navigate', open: right, preview: null }, right, tools, pending: 2, theme, agent: null }, {}, {},
    h('p', { role: 'note' }, 'Connected to the private workspace API. Only approved licensed clips are accepted; every result is labelled RECORDED or SIMULATED by the server.'),
    h('p', { role: 'note', 'data-label': 'simulated' }, 'SIMULATED: run and fit values come from the in-browser simulator on the validated setup.'),
    renderUpload(h, { show: true, disabled: false, upload: null, percent: 0, status: 'No file uploaded yet.', error: null }, () => {}), ws));
  writeFileSync(new URL('./static-' + theme + (right ? '-right' : '') + '.html', import.meta.url), '<!doctype html><html data-theme="' + theme + '"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><style>' + css + '</style><body style="margin:0">' + page + probe + '</body></html>');
}
