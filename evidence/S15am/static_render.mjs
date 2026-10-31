// S15am static SSR evidence: real shell/upload/question-card renderers in all six modes (1280) + dark/light 375. Synthetic fixture, not a measurement.
import { createRequire } from 'node:module';
import { readFileSync, writeFileSync } from 'node:fs';
import { renderShell, toolsOf } from '../../Build/web/src/shell/workspace-shell.mjs';
import { renderUpload } from '../../Build/web/src/workspace/upload-view.mjs';
import { renderQuestionCard } from '../../Build/web/src/shell/agent-card.mjs';
import { PALETTES, THEME_CSS, toneOf } from '../../Build/web/src/shell/theme.mjs';
const require = createRequire(new URL('../../Build/web/package.json', import.meta.url));
const React = require('react'); const { renderToStaticMarkup } = require('react-dom/server');
const h = React.createElement;
const pub = new URL('../../Build/web/public/', import.meta.url).href; // file URL for /images/app art
const css = ['app/styles.css', 'workspace/workspace.css'].map((f) => readFileSync(new URL('../../Build/web/src/' + f, import.meta.url), 'utf8')).join('\n').replaceAll('url("/images/', 'url("' + pub + 'images/') + '\n' + THEME_CSS;
const tools = toolsOf({ live: true, phase: 'upload.idle', owner: false, jobId: null, uploadStatus: null, hasReport: false, pending: 1 });
const stage = (label, st, cur) => h('li', { 'data-status': st, 'aria-current': cur ? 'step' : undefined }, label);
const ws = h('div', { className: 'ws' },
  h('nav', { className: 'ws-stages', 'aria-label': 'Workspace stages' }, h('ol', null, stage('Upload', 'current', true), stage('Interview', 'todo'), stage('Run', 'todo'), stage('Fit', 'todo'), stage('Report', 'todo'))),
  h('section', { id: 'ws-viewport', className: 'ws-viewport', 'aria-label': 'Scene viewport' }, h('div', { className: 'ws-host', 'data-viewer-status': 'empty' }), h('p', { className: 'ws-status' }, 'No scene yet. The viewport appears when an upload produces a scene.')),
  h('section', { id: 'ws-panel', className: 'ws-panel' }, h('h2', null, 'Upload'), h('p', { className: 'ws-whatif', 'data-label': 'what-if' }, 'what-if · scale unverified · Held-out caveat (label check)')),
  h('div', { id: 'ws-job', className: 'ws-job' }, h('p', null, 'RECORDED · owner clip · SIMULATED · FIXTURE (label check)')));
let card = null;
try { card = renderQuestionCard(h, { status: 'asking', index: 0, answers: [], questions: [{ id: 'known_size', kind: 'free_text', chips: [], prompt: 'Synthetic fixture question: name one object of known size.' }] }, () => {}); } catch (e) { card = h('p', null, 'card render failed: ' + e.message); }
const probe = '<script>(()=>{const d=document.documentElement;document.title="PROBE theme="+d.dataset.theme+" docScroll="+d.scrollWidth+"/"+d.clientWidth})()</script>';
for (const p of PALETTES) for (const right of [true, false]) {
  const page = renderToStaticMarkup(h('main', { id: 'main' }, renderShell(h, { title: 'New project — static S15am render (synthetic fixture, not a measurement)', rail: { pane: right ? 'navigate' : null, open: right, preview: null }, right, tools, pending: 1, theme: p.id, agent: card }, {}, {},
    h('p', { role: 'note' }, 'FIXTURE: synthetic workspace render for design QA; not a measurement.'),
    h('p', { role: 'note', 'data-label': 'simulated' }, 'SIMULATED: label check (static render).'),
    h('p', { role: 'note', 'data-instruments': 'unavailable' }, 'Instruments are not available in this build; no reading is shown.'),
    renderUpload(h, { show: true, disabled: false, upload: null, percent: 0, status: 'No file uploaded yet.', error: null }, () => {}), ws)));
  writeFileSync(new URL('./static-' + p.id + (right ? '-right' : '') + '.html', import.meta.url), '<!doctype html><html data-theme="' + p.id + '" data-tone="' + toneOf(p.id) + '"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><style>' + css + '</style><body style="margin:0">' + page + probe + '</body></html>');
}
for (const t of ['dark', 'light']) writeFileSync(new URL('./wrap-' + t + '-375.html', import.meta.url), '<!doctype html><body style="margin:0;background:#888"><iframe src="static-' + t + '.html" style="width:375px;height:812px;border:0;display:block"></iframe></body>');
