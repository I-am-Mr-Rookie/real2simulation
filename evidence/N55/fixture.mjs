// N55 local fixture: server-renders the new workspace (shell + live centre) with synthetic data for screenshots.
// No API, no Clerk, no private clips. Usage: node evidence/N55/fixture.mjs -> evidence/N55/out/*.html
import { createRequire } from 'node:module';
import { readFileSync, mkdirSync, writeFileSync } from 'node:fs';
import { createLive } from '../../Build/web/src/workspace/live-view.mjs';
import { renderShell } from '../../Build/web/src/shell/workspace-shell.mjs';
import { icon } from '../../Build/web/src/shell/icons.mjs';
import { THEME_CSS } from '../../Build/web/src/shell/theme.mjs';

const req = createRequire(new URL('../../Build/web/package.json', import.meta.url));
const React = req('react'), { renderToStaticMarkup } = req('react-dom/server');
const root = new URL('../../', import.meta.url);
const css = ['Build/web/src/app/styles.css', 'Build/web/src/workspace/workspace.css'].map((p) => readFileSync(new URL(p, root), 'utf8')).join('\n');
const Live = createLive(React, icon), h = React.createElement;
const ago = (min) => new Date(Date.now() - min * 60000).toISOString();
const img = (n) => '/Build/web/public/images/app/' + n; // served from the worktree root
const projects = [
  { id: 'p1', mode: 'room', title: 'Classroom lab', created: ago(4), snapshot_url: img('b1-light@1x.webp') },
  { id: 'p2', mode: 'experiment', title: 'Apple drop', created: ago(95) },
  { id: 'p3', mode: 'experiment', title: 'Pendulum swing', created: ago(60 * 26) },
  { id: 'p4', mode: 'room', title: 'Room 2026-11-01 09:12', created: ago(60 * 30) },
  { id: 'p5', mode: 'experiment', title: 'Experiment 2026-11-01 09:40', created: ago(60 * 29) },
  { id: 's1', mode: 'room', title: 'SAMPLE (RECORDED): Classroom room lab', sample: true, created: ago(60 * 48) },
  { id: 's2', mode: 'experiment', title: 'SAMPLE (RECORDED): Falling apple', sample: true, created: ago(60 * 48) },
];
const rooms = [{ id: 'r1', project_id: 'p1', status: 'running', progress: 0.42, created: ago(3) }, { id: 'r2', project_id: 's1', status: 'done', created: ago(60 * 48) }];
const experiments = [{ id: 'e1', project_id: 'p2', status: 'done', created: ago(90) }, { id: 'e2', project_id: 'p3', status: 'failed', error: 'object lost after frame 40', created: ago(60 * 26) },
  { id: 'e3', project_id: 's2', status: 'done', created: ago(60 * 48) }];
const files = [
  { id: 'f1', name: 'classroom_walk.mp4', media_type: 'video/mp4', size: 48_300_000, duration_s: 41.2, project_id: 'p1' },
  { id: 'f2', name: 'apple_drop.mov', media_type: 'video/quicktime', size: 12_800_000, duration_s: 6.4, project_id: 'p2' },
  { id: 'f3', name: 'pendulum_swing.mp4', media_type: 'video/mp4', size: 22_100_000, duration_s: 14.9, project_id: 'p3' },
  { id: 'f4', name: 'desk_test.webm', media_type: 'video/webm', size: 3_400_000, duration_s: 3.1, project_id: null },
];
const quota = { storage_bytes_used: 86_600_000, storage_bytes_limit: 1024 ** 3, storage_bytes_remaining: 1024 ** 3 - 86_600_000, uploads_today: 4, uploads_daily_limit: 20, uploads_remaining_today: 16 };
const L = (extra = {}) => ({ mode: 'standard', setMode() {}, files: { items: files, quota, error: null, loaded: true }, up: { name: 'swing_take2.mp4', pct: 63, error: null },
  jobs: { projects: { state: 'ok', items: projects }, rooms: { state: 'ok', items: rooms }, experiments: { state: 'ok', items: experiments } },
  tracked: { 'room:r1': { kind: 'room', id: 'r1', state: 'running', step: 'Reconstructing room', terminal: false } },
  gpu: { tone: 'green', label: 'GPU on, sleeps in 14:32', detail: 'Queue empty' }, voice: { state: 'idle', error: null }, draft: '', setDraft() {}, msgs: [],
  project: null, preview: null, action: null, busy: false, ...extra });
const page = (name, theme, l, hash, open = true) => {
  globalThis.location = { hash };
  const shell = renderShell(h, { title: 'Private workspace', rail: { pane: 'project', open, preview: null }, right: false, tools: [], pending: 0,
    status: h(Live.Dot, { L: l }), foot: h(Live.Meter, { L: l }) }, {}, {}, h(Live.Centre, { L: l }));
  const body = renderToStaticMarkup(h('section', { 'data-private-content': 'live', 'aria-label': 'Private workspace' }, shell));
  const html = '<!doctype html><html lang="en" data-theme="' + theme + '" data-tone="' + (theme === 'dark' ? 'dark' : 'light') + '"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>N55 fixture</title><style>' + THEME_CSS + css + '</style></head><body><main id="main">' + body + '</main></body></html>';
  writeFileSync(new URL('out/' + name + '.html', import.meta.url), html);
};
mkdirSync(new URL('out/', import.meta.url), { recursive: true });
for (const theme of ['light', 'dark']) {
  page('home-' + theme, theme, L(), '');
  page('picker-' + theme, theme, L({ pickerOpen: true, up: null, tracked: {} }), '');
  page('files-' + theme, theme, L({ preview: 'f2', up: null, tracked: {} }), '#files');
  page('narrow-' + theme, theme, L(), '', false);
}
console.log('ok');

