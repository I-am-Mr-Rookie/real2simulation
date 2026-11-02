// N55: the new home renders prompt, model picker, mode cards, project grid and progress pop-up; old chrome is gone.
import test from 'node:test';
import assert from 'node:assert/strict';
import { createRequire } from 'node:module';
import { createLive } from '../../Build/web/src/workspace/live-view.mjs';
import { renderShell, PANES } from '../../Build/web/src/shell/workspace-shell.mjs';
import { icon } from '../../Build/web/src/shell/icons.mjs';

const req = createRequire(new URL('../../Build/web/package.json', import.meta.url));
const React = req('react'), { renderToStaticMarkup } = req('react-dom/server');
const Live = createLive(React, icon), h = React.createElement;
const L = { mode: 'standard', setMode() {}, files: { items: [{ id: 'f', name: 'apple_drop.mov', media_type: 'video/quicktime', size: 1e6, project_id: 'p' }],
  quota: { storage_bytes_used: 1e6, storage_bytes_limit: 2 ** 30, storage_bytes_remaining: 2 ** 30 - 1e6, uploads_daily_limit: 20, uploads_remaining_today: 19 }, loaded: true },
  up: { name: 'x.mp4', pct: 10, error: null }, tracked: {}, gpu: { tone: 'red', label: 'GPU sleeping', detail: '' }, voice: { state: 'idle' }, draft: '', msgs: [],
  jobs: { projects: { items: [{ id: 'p', mode: 'experiment', title: 'Apple drop' }, { id: 'e', mode: 'room', title: 'Room 2026-11-01 09:12' }] }, experiments: { items: [] }, rooms: { items: [] } } };

test('home view: prompt, picker, mode cards, grid, empty projects tucked away, progress pop-up', () => {
  const html = renderToStaticMarkup(h(Live.Centre, { L }));
  for (const s of ['What do you want to simulate?', 'Muse Spark 1.3', 'Turn your room into a lab', 'Measure your experiment', 'New project', 'Apple drop', 'Show empty (1)'])
    assert.ok(html.includes(s), s);
  assert.ok(!html.includes('Room 2026-11-01 09:12'), 'empty project hidden behind Show empty');
  assert.ok(html.includes('Processing 1 item'));
  assert.ok(!/Refresh|Connected|\u2014/.test(html));
});

test('rail: no "This project" menu; storage meter at the bottom', () => {
  assert.ok(!PANES.some((p) => p.label === 'This project'));
  const html = renderToStaticMarkup(renderShell(h, { title: 'Private workspace', rail: null, right: false, tools: [], foot: h(Live.Meter, { L }) }));
  assert.match(html, /r2s-foot/);
  assert.match(html, /19 of 20 uploads left today/);
  assert.ok(!/Scene viewport|Stage panel|Job status/.test(html));
});

