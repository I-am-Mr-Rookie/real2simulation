// N55: the new home renders prompt, model picker, mode cards, project grid and progress pop-up; old chrome is gone.
import test from 'node:test';
import assert from 'node:assert/strict';
import { createRequire } from 'node:module';
import { createLive } from '../../Build/web/src/workspace/live-view.mjs';
import { renderShell, PANES } from '../../Build/web/src/shell/workspace-shell.mjs';
import { icon } from '../../Build/web/src/shell/icons.mjs';
import { agentTier, readAgentMode, writeAgentMode } from '../../Build/web/src/workspace/live.mjs';

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

test('Wonder picker renders Smartest and relative bars; saved choice reaches the API', () => {
  const html = renderToStaticMarkup(h(Live.Centre, { L: { ...L, mode: 'wonder', pickerOpen: true } }));
  assert.match(html, /Muse Wonder/);
  assert.match(html, /data-tag="Smartest">Smartest/);
  assert.match(html, /Intelligence high, relative/);
  assert.match(html, /Speed low, relative/);
  assert.match(html, /Cost high, relative/);
  assert.ok(!/gpt|sol|\$|\u2014/i.test(html));
  assert.deepEqual(agentTier('wonder'), { contributor: false, tier: 'wonder' });
  const data = new Map(), storage = { getItem: (k) => data.get(k), setItem: (k, v) => data.set(k, v) };
  writeAgentMode(storage, 'wonder', 'u1');
  assert.equal(readAgentMode(storage, 'u1'), 'wonder');
  assert.equal(readAgentMode(storage, 'u2'), null);
});

test('Wonder limit notice is visible in the chat, not only hidden response metadata', () => {
  const notice = 'Wonder limit reached for today, using Muse Spark';
  const html = renderToStaticMarkup(h(Live.Chat, { L: { ...L, mode: 'wonder', msgs: [
    { id: 'limit', role: 'assistant', text: 'Ready for lab work.', notice },
  ] } }));
  assert.match(html, /role="status">Wonder limit reached for today, using Muse Spark/);
  assert.ok(html.includes('Ready for lab work.'));
});

test('microphone permission pending is named and disabled in both workspace voice controls', () => {
  for (const View of [Live.Centre, Live.Chat]) {
    const html = renderToStaticMarkup(h(View, { L: { ...L, voice: { state: 'requesting' } } }));
    assert.match(html, /Waiting for microphone/);
    assert.match(html, /data-voice="requesting"[^>]*disabled/);
    assert.doesNotMatch(html, /Transcribing/);
  }
});

