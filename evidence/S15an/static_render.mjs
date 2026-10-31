// S15an static SSR evidence (adapted from evidence/S15am/static_render.mjs): global header with the ONE theme menu + full-bleed
// private shell (main > section > .r2s-shell), live chips, owner-clip result state. FIXTURE values copied from tests/workspace/spec-body.test.mjs; not a measurement.
import { createRequire } from 'node:module';
import { readFileSync, writeFileSync } from 'node:fs';
import { renderShell, toolsOf } from '../../Build/web/src/shell/workspace-shell.mjs';
import { renderWorkspace } from '../../Build/web/src/workspace/view.mjs';
import { icon } from '../../Build/web/src/shell/icons.mjs';
import { THEME_CSS, THEME_OPTIONS, toneOf } from '../../Build/web/src/shell/theme.mjs';
import { LIVE_NOTICE, INSTRUMENTS_UNAVAILABLE } from '../../Build/web/src/shell/PrivateWorkspace.mjs';
const require = createRequire(new URL('../../Build/web/package.json', import.meta.url));
const React = require('react'); const { renderToStaticMarkup } = require('react-dom/server');
const h = React.createElement;
const pub = '/Build/web/public/'; // served from the worktree root (python -m http.server), so public art resolves over http
const css = ['app/styles.css', 'workspace/workspace.css'].map((f) => readFileSync(new URL('../../Build/web/src/' + f, import.meta.url), 'utf8')).join('\n').replaceAll('url("/images/', 'url("' + pub + 'images/').replaceAll('url("/brand/', 'url("' + pub + 'brand/') + '\n' + THEME_CSS;
// Mirrors app/ThemeToggle.jsx + SiteFrame.jsx header markup (JSX is compiled only by next build).
const header = (theme, open) => h('header', { className: 'site-header' }, h('a', { className: 'wordmark', href: '#' }, h('img', { className: 'brand-mark', src: pub + 'brand/mark-192.png', width: 28, height: 28, alt: '' }), 'Real2Simulation'),
  h('nav', null, h('a', { href: '#' }, icon(h, 'book', 16), h('span', { className: 'nav-label' }, 'Demo library')), h('a', { href: '#' }, icon(h, 'flask', 16), h('span', { className: 'nav-label' }, 'Local simulation lab')),
    h('details', { className: 'theme-menu', open }, h('summary', { 'aria-label': 'Colour theme', title: 'Colour theme' }, icon(h, 'palette', 18)),
      h('div', { className: 'theme-menu-list', role: 'group', 'aria-label': 'Colour theme' }, ...THEME_OPTIONS.map((t) => h('button', { key: t.id, type: 'button', 'data-theme-option': t.id, 'aria-pressed': t.id === theme },
        t.tokens ? h('span', { className: 'theme-swatch', 'aria-hidden': true, style: { background: t.tokens.bg, borderColor: t.tokens['border-strong'], color: t.tokens.accent } }) : icon(h, t.icon, 16), t.label)))),
    h('a', { className: 'nav-cta', href: '#' }, 'Account')));
const chip = (label, text, id) => h('details', { className: 'r2s-chip', 'data-chip': id }, h('summary', { title: text }, icon(h, 'info', 14), label), h('p', { role: 'note' }, text));
const measurement = { clip_id: 'OWN01', input_label: 'OWNER_RECORDED / RECORDED', status: 'recorded', label: 'RECORDED replay of a MEASURED result',
  g: 10.96, u: 0.77, unit: 'm/s^2', measured_label: 'MEASURED (owner clip OWN01)', source: 'evidence/S07/S07i/result-own01.json',
  caveat: 'Held-out prediction FAILS (RMSE 23 px >> 2 px)', scale: { reference: 'book cover horizontal edge in fall plane', value_m: 0.2028, label: 'user-declared, not verified' } };
const stages = [['upload', 'Upload', 'done'], ['interview', 'Interview', 'done'], ['run', 'Run (not run)', 'skipped'], ['fit', 'Fit (not run)', 'skipped'], ['report', 'Report', 'current']].map(([id, label, status]) => ({ id, label, status, failed: false }));
const layout = { phase: 'report.owner', stages, viewport: { banner: null }, jobStatus: { label: 'Clip result (owner clip; no scene, run or fit)', jobId: 'job_FIXTURE', surface: null, error: null } };
const tools = toolsOf({ live: true, phase: 'report.owner', owner: true, jobId: 'job_FIXTURE', uploadStatus: null, hasReport: true, pending: 0 });
const probe = '<script>(()=>{const d=document.documentElement;document.title="PROBE theme="+d.dataset.theme+" docScroll="+d.scrollWidth+"/"+d.clientWidth})()</script>';
for (const theme of ['dark', 'paper', 'contrast']) for (const [suffix, right, menu] of [['', false, false], ['-right', true, false], ['-menu', false, true]]) {
  const ws = renderWorkspace(h, layout, { status: 'empty' }, null, null, undefined, undefined, undefined, undefined, undefined, undefined, undefined, { label: 'RECORDED FIXTURE', measurement });
  const page = renderToStaticMarkup(h(React.Fragment, null, header(theme, menu), h('main', { id: 'main' }, h('section', { 'data-private-content': 'live', 'aria-label': 'Private workspace' },
    renderShell(h, { title: 'Private development fixture scene (FIXTURE static S15an render, not a measurement)', rail: { pane: 'navigate', open: false, preview: null }, right, tools, pending: 0, agent: null }, {}, {},
      chip('Connected', LIVE_NOTICE, 'live'), chip('Instruments off', INSTRUMENTS_UNAVAILABLE, 'instruments'), ws)))));
  writeFileSync(new URL('./static-' + theme + suffix + '.html', import.meta.url), '<!doctype html><html data-theme="' + theme + '" data-tone="' + toneOf(theme) + '"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><style>' + css + '</style><body style="margin:0">' + page + probe + '</body></html>');
}
