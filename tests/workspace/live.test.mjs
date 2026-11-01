// N09: pure logic of the live workspace (WAV encoder, GPU dot, quota, job 404 handling, agent mode storage, chat history).
import assert from 'node:assert/strict';
import test from 'node:test';
import { encodeWav, toWav16k, gpuDot, quotaView, jobsState, historyOf, readAgentMode, writeAgentMode, AGENT_MODES, UPLOAD_QUESTION, TIPS,
  questionAnswer, recommendedIndex, fmtBytes, shouldPoll } from '../../Build/web/src/workspace/live.mjs';

test('encodeWav writes a mono PCM16 16 kHz RIFF header and clamped samples', () => {
  const b = encodeWav(new Float32Array([0, 1, -1, 2, -0.5]), 16000), v = new DataView(b.buffer);
  const s = (o, n) => String.fromCharCode(...b.slice(o, o + n));
  assert.equal(s(0, 4), 'RIFF'); assert.equal(s(8, 4), 'WAVE'); assert.equal(s(12, 4), 'fmt '); assert.equal(s(36, 4), 'data');
  assert.equal(b.length, 44 + 10); assert.equal(v.getUint32(4, true), 36 + 10);
  assert.equal(v.getUint16(20, true), 1); assert.equal(v.getUint16(22, true), 1); assert.equal(v.getUint32(24, true), 16000);
  assert.equal(v.getUint32(28, true), 32000); assert.equal(v.getUint16(32, true), 2); assert.equal(v.getUint16(34, true), 16); assert.equal(v.getUint32(40, true), 10);
  assert.deepEqual([0, 1, 2, 3, 4].map((i) => v.getInt16(44 + i * 2, true)), [0, 32767, -32768, 32767, -16384]);
});

test('toWav16k downmixes through a mono 16 kHz OfflineAudioContext and caps at 60 s', async () => {
  const seen = {};
  class AC { decodeAudioData() { return Promise.resolve({ duration: 90 }); } close() { seen.closed = true; } }
  class OAC {
    constructor(ch, len, rate) { Object.assign(seen, { ch, len, rate }); }
    createBufferSource() { return { connect() {}, start() { seen.started = true; } }; }
    startRendering() { return Promise.resolve({ getChannelData: () => new Float32Array(4) }); }
  }
  const wav = await toWav16k(new ArrayBuffer(1), AC, OAC);
  assert.deepEqual({ ch: seen.ch, len: seen.len, rate: seen.rate, closed: seen.closed, started: seen.started }, { ch: 1, len: 960000, rate: 16000, closed: true, started: true });
  assert.equal(wav.length, 44 + 8);
});

test('gpuDot maps N04 status to red/yellow/green with queue position, unknown otherwise', () => {
  assert.deepEqual(gpuDot({ state: 'red', queue_length: 0, your_position: null }), { tone: 'red', label: 'GPU sleeping', detail: 'Queue empty' });
  assert.deepEqual(gpuDot({ state: 'yellow', queue_length: 3, your_position: 2 }), { tone: 'yellow', label: 'GPU starting', detail: 'Your job: 2 of 3 in queue' });
  assert.equal(gpuDot({ state: 'green', queue_length: 1, your_position: null }).detail, '1 job in queue');
  for (const bad of [null, {}, { state: 'blue' }, { status: 'error' }]) assert.equal(gpuDot(bad).tone, 'unknown');
  assert.equal(shouldPoll({ visibilityState: 'hidden' }), false); assert.equal(shouldPoll({ visibilityState: 'visible' }), true);
});

test('quotaView and fmtBytes use only API numbers', () => {
  const q = { storage_bytes_used: 256 * 1024 * 1024, storage_bytes_limit: 1024 ** 3, storage_bytes_remaining: 768 * 1024 * 1024, uploads_remaining_today: 18, uploads_daily_limit: 20 };
  assert.deepEqual(quotaView(q), { pct: 25, full: false, text: '256 MB of 1.0 GB used. 18 of 20 uploads left today.' });
  assert.equal(quotaView({ ...q, uploads_remaining_today: 0 }).full, true);
  assert.equal(quotaView(null), null);
  assert.equal(fmtBytes(0), '0 B'); assert.equal(fmtBytes(1536), '1.5 KB');
});

test('jobsState: 404 is not available yet, errors stay errors, lists pass through', () => {
  assert.deepEqual(jobsState(404, null, 'rooms'), { state: 'unavailable', items: [] });
  assert.equal(jobsState(502, { error: { message: 'down' } }, 'rooms').message, 'down');
  assert.deepEqual(jobsState(200, { rooms: [{ id: 'a' }] }, 'rooms').items, [{ id: 'a' }]);
  assert.deepEqual(jobsState(200, { jobs: [{ id: 'b' }] }, 'experiments').items, [{ id: 'b' }]);
});

test('agent mode: default unset (first run), persisted, bad values ignored; contributor shows the training con', () => {
  const m = new Map(), s = { getItem: (k) => m.get(k) ?? null, setItem: (k, v) => m.set(k, v) };
  assert.equal(readAgentMode(s), null);
  writeAgentMode(s, 'contributor'); assert.equal(readAgentMode(s), 'contributor');
  m.set('r2s.agent.mode', 'evil'); assert.equal(readAgentMode(s), null);
  assert.equal(readAgentMode({ getItem() { throw new Error('blocked'); } }), null);
  assert.equal(AGENT_MODES[0].id, 'standard');
  assert.ok(AGENT_MODES[1].cons.some((c) => /train/.test(c)));
});

test('upload question, tips and chat history', () => {
  assert.equal(UPLOAD_QUESTION.options.filter((o) => o.recommended).length, 1);
  assert.deepEqual(UPLOAD_QUESTION.options.map((o) => o.mode).sort(), ['experiment', 'room']);
  assert.ok(TIPS.room.length && TIPS.experiment.length);
  assert.equal(recommendedIndex(UPLOAD_QUESTION), 0);
  assert.equal(questionAnswer(UPLOAD_QUESTION, 1, ''), 'Room video'); assert.equal(questionAnswer(UPLOAD_QUESTION, 1, ' my own '), 'my own');
  const msgs = [{ role: 'note', text: 'x' }, { role: 'error', text: 'e' }, ...Array.from({ length: 25 }, (_, i) => ({ role: i % 2 ? 'assistant' : 'user', text: 't' + i }))];
  const h = historyOf(msgs);
  assert.equal(h.length, 20); assert.deepEqual(h.at(-1), { role: 'user', content: 't24' });
  const text = JSON.stringify([AGENT_MODES, UPLOAD_QUESTION, TIPS]);
  assert.ok(!text.includes('\u2014'), 'no em dashes in visible text');
});
