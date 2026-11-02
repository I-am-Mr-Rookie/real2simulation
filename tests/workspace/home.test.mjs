// N55: workspace home helpers (content names, relative time, card status, model picker rows).
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { relTime, groupStatus, groupJobs } from '../../Build/web/src/workspace/projects.mjs';
import { contentTitle, isDefaultTitle, projectTitle, MODEL_CHOICES } from '../../Build/web/src/workspace/live.mjs';

test('phone model dialog starts beyond the permanent rail, without changing desktop positioning', () => {
  const css = readFileSync(new URL('../../Build/web/src/workspace/workspace.css', import.meta.url), 'utf8');
  const phone = css.slice(css.lastIndexOf('@media (max-width: 760px)'));
  const picker = phone.match(/\.lv-pickpop \{([^}]+)\}/)?.[1];
  assert.ok(picker, 'phone picker rule');
  assert.match(picker, /position: fixed;/);
  assert.match(picker, /left: calc\(3\.25rem \+ \.75rem\);/);
  assert.match(picker, /right: \.75rem;/);
  assert.match(css, /\.r2s-rail \{[^}]*width: 3\.25rem;/);
  assert.match(css, /\.lv-pickpop \{ position: absolute;[^}]*left: 0;/);
});

test('projects get content names, never timestamps', () => {
  assert.equal(projectTitle('room'), 'Room lab');
  assert.equal(projectTitle('experiment'), 'New experiment');
  assert.equal(contentTitle('experiment', 'apple_drop.MOV'), 'Apple drop');
  assert.equal(contentTitle('room', 'Classroom-walk.mp4'), 'Classroom walk lab');
  assert.equal(contentTitle('room', 'my lab.mp4'), 'My lab');
  assert.equal(contentTitle('room', 'IMG_2041.mp4'), 'Img 2041 lab');
  assert.equal(contentTitle('experiment', '20261102.mp4'), 'New experiment');
  assert.ok(isDefaultTitle('Room lab') && isDefaultTitle('Experiment 2026-11-01 09:40') && !isDefaultTitle('Apple drop'));
});

test('relative time', () => {
  const now = Date.parse('2026-11-02T10:00:00Z');
  assert.equal(relTime('2026-11-02T09:59:30Z', now), 'just now');
  assert.equal(relTime('2026-11-02T09:55:00Z', now), '5 min ago');
  assert.equal(relTime('2026-11-02T07:00:00Z', now), '3 h ago');
  assert.equal(relTime('2026-10-31T10:00:00Z', now), '2 d ago');
  assert.equal(relTime('', now), '');
});

test('card status: newest job wins, live tracked state first, failure keeps its reason', () => {
  const [g] = groupJobs([{ id: 'p', mode: 'experiment', title: 'Apple drop' }],
    [{ id: 'a', project_id: 'p', status: 'done', created: '2026-11-01T00:00:00Z' }, { id: 'b', project_id: 'p', status: 'running', progress: 0.4, created: '2026-11-02T00:00:00Z' }], []);
  assert.deepEqual(groupStatus(g).state, 'processing');
  assert.equal(groupStatus(g).progress, 0.4);
  assert.equal(groupStatus(g, { 'experiment:b': { state: 'failed', error: 'object lost' } }).reason, 'object lost');
  assert.equal(groupStatus(g, { 'experiment:b': { state: 'done' } }).state, 'ready');
  assert.equal(groupStatus({ rooms: [], experiments: [] }).state, 'empty');
  assert.equal(groupStatus({ snapshot: '/snapshot', rooms: [], experiments: [] }).state, 'saved');
});

test('undated room rows use their update timestamp, not an artificial oldest date', () => {
  const room = { id: 'room', status: 'done', updated_at: '2026-11-02T10:00:00Z' };
  const experiment = { id: 'experiment', status: 'done', created: '2026-11-02T09:00:00Z' };
  const g = { rooms: [room], experiments: [experiment] };
  assert.equal(groupStatus(g).job, room);
  assert.equal(groupStatus(g, { 'room:room': { state: 'failed', error: 'room unavailable' } }).reason, 'room unavailable');
  assert.equal(groupStatus({ rooms: [room], experiments: [{ ...experiment, created: '2026-11-02T11:00:00Z' }] }).kind, 'experiment');
});

test('model picker: four tiers, bars only, no Sol, contributor warns about training', () => {
  assert.deepEqual(MODEL_CHOICES.map((m) => [m.id, m.tag]), [['standard', 'Recommended'], ['contributor', 'Cheapest'], ['open', 'Fastest'], ['wonder', 'Smartest']]);
  assert.ok(!JSON.stringify(MODEL_CHOICES).match(/sol|gpt|\$|\u2014/i));
  assert.match(MODEL_CHOICES[1].con, /trains on your prompts/);
  for (const m of MODEL_CHOICES) assert.deepEqual(Object.keys(m.bars), ['Intelligence', 'Speed', 'Cost']);
  const [spark, , , wonder] = MODEL_CHOICES;
  assert.ok(wonder.bars.Intelligence > spark.bars.Intelligence && wonder.bars.Speed < spark.bars.Speed && wonder.bars.Cost > spark.bars.Cost);
});

