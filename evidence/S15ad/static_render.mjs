import { createRequire } from 'node:module';
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { renderShell, toolsOf } from '../../Build/web/src/shell/workspace-shell.mjs';
const require = createRequire(new URL('../../Build/web/package.json', import.meta.url));
const React = require('react'); const { renderToStaticMarkup } = require('react-dom/server');
const h = React.createElement;
const tools = toolsOf({ live: true, phase: 'result', owner: true, jobId: 'synthetic-job', uploadStatus: null, hasReport: false, pending: 0 });
const LONG = 'evidence/S07/S07m/results.json';
const ws = h('div', { className: 'ws' },
  h('section', { className: 'ws-viewport', 'aria-label': 'Scene viewport' }, h('div', { className: 'ws-host', 'data-viewer-status': 'empty' })),
  h('section', { id: 'ws-panel', className: 'ws-panel' }, h('h2', null, 'Result (RECORDED, owner clip, scale-unverified)'), h('span', { className: 'ws-src' }, 'source ' + LONG),
    h('p', null, 'Static synthetic fixture render, not a measurement. ' + 'x'.repeat(60) + '/' + 'evidence_S07_S07m_results_json_'.repeat(2))),
  h('div', { className: 'ws-job' }, h('p', null, 'job synthetic-job-' + 'a1b2c3d4e5f6'.repeat(5)), h('p', null, 'SIMULATED what-if; Held-out')));
const page = renderToStaticMarkup(renderShell(h, { title: 'Static S15ad render (synthetic fixture, not a measurement)', left: false, right: true, tools, pending: 0, agent: null }, {}, {}, ws));
const css = readFileSync(new URL('../../Build/web/src/workspace/workspace.css', import.meta.url), 'utf8');
const probe = '<script>addEventListener("load",()=>{const q=s=>document.querySelector(s);const o=[document.documentElement,q("#ws-panel"),q(".ws-viewport"),q(".r2s-center")].map(e=>e.scrollWidth+"/"+e.clientWidth);const a=q(".ws-viewport").getBoundingClientRect(),b=q("#ws-panel").getBoundingClientRect();document.title="PROBE doc,panel,view,centre="+o.join(" ")+" stacked="+(b.top>=a.bottom)+" panelW="+Math.round(b.width)})</script>';
mkdirSync(new URL('./', import.meta.url), { recursive: true });
writeFileSync(new URL('./static-result.html', import.meta.url), '<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width"><style>body{margin:0}' + css + '</style>' + page + probe);

