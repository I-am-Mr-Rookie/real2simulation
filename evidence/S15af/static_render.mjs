// S15af static SSR evidence: activity bar at 1280 (pane open, collapsed, temporary preview) and 375 (drawer). Synthetic fixture, not a measurement.
import { createRequire } from 'node:module';
import { readFileSync, writeFileSync } from 'node:fs';
import { renderShell, toolsOf } from '../../Build/web/src/shell/workspace-shell.mjs';
const require = createRequire(new URL('../../Build/web/package.json', import.meta.url));
const React = require('react'); const { renderToStaticMarkup } = require('react-dom/server');
const h = React.createElement;
const tools = toolsOf({ live: true, phase: 'result', owner: true, jobId: 'synthetic-job', uploadStatus: null, hasReport: false, pending: 0 });
const css = readFileSync(new URL('../../Build/web/src/workspace/workspace.css', import.meta.url), 'utf8');
const ws = h('div', { className: 'ws' },
  h('section', { id: 'ws-viewport', className: 'ws-viewport', 'aria-label': 'Scene viewport' }, h('div', { className: 'ws-host', 'data-viewer-status': 'empty' })),
  h('section', { id: 'ws-panel', className: 'ws-panel' }, h('h2', null, 'Result (RECORDED, owner clip, scale-unverified)'), h('p', null, 'Static synthetic fixture render, not a measurement.')),
  h('div', { id: 'ws-job', className: 'ws-job' }, h('p', null, 'SIMULATED what-if; Held-out')));
const probe = '<script>addEventListener("load",()=>{const q=s=>document.querySelector(s);const c=q(".r2s-center").getBoundingClientRect(),p=[...document.querySelectorAll(".r2s-pane")].find(e=>!e.hidden&&getComputedStyle(e).display!=="none");const pr=p&&p.getBoundingClientRect();const tg=q("[data-toggle=left]").getBoundingClientRect(),el=document.elementFromPoint(tg.left+tg.width/2,tg.top+tg.height/2);const lab=[...document.querySelectorAll(".r2s-pane:not([hidden]) a")].map(a=>a.scrollWidth>a.clientWidth).some(Boolean);const cur=getComputedStyle(q("[aria-current=true]"));document.title="PROBE toggleTop="+(el&&el.closest("[data-toggle=left]")?"toggle":"COVERED:"+el.className)+" clipped="+lab+" curBg="+cur.backgroundColor+" curShadow="+cur.boxShadow+"  docScroll="+document.documentElement.scrollWidth+"/"+document.documentElement.clientWidth+" centreLeft="+Math.round(c.left)+" pane="+(p?p.id+"@"+Math.round(pr.left)+"w"+Math.round(pr.width):"none")+" current="+q("[aria-current=true]").dataset.pane})</script>';
const states = { open: { pane: 'navigate', open: true, preview: null }, collapsed: { pane: 'navigate', open: false, preview: null },
  preview: { pane: 'navigate', open: false, preview: 'project' }, 'narrow-drawer': { pane: 'project', open: true, preview: null } };
for (const [name, rail] of Object.entries(states)) {
  const page = renderToStaticMarkup(renderShell(h, { title: 'Static S15af render (synthetic fixture, not a measurement)', rail, right: false, tools, pending: 0, agent: null }, {}, {}, ws));
  writeFileSync(new URL('./static-' + name + '.html', import.meta.url), '<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width"><style>body{margin:0}' + css + '</style>' + page + probe);
}


