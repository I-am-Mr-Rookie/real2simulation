// N09: pure logic of the live workspace (WAV encoder, GPU dot, quota, job 404 handling, agent mode storage, chat history).
import assert from 'node:assert/strict';
import test from 'node:test';
import { encodeWav, toWav16k, gpuDot, quotaView, jobsState, historyOf, readAgentMode, writeAgentMode, apiErrorText, AGENT_MODES, UPLOAD_QUESTION, TIPS,
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
  // N26: warm-idle window (green, nothing queued): no minutes are claimed because the API sends none
  assert.deepEqual(gpuDot({ state: 'green', queue_length: 0, your_position: null }), { tone: 'green', label: 'GPU on, idle', detail: 'Queue empty' });
  assert.equal(gpuDot({ state: 'green', queue_length: 2, your_position: 1 }).label, 'GPU running');
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
  assert.deepEqual(jobsState(405, null, 'rooms'), { state: 'unavailable', items: [] });
  assert.equal(jobsState(502, { error: { message: 'down' } }, 'rooms').message, 'down');
  assert.deepEqual(jobsState(200, { rooms: [{ id: 'a' }] }, 'rooms').items, [{ id: 'a' }]);
  assert.deepEqual(jobsState(200, { jobs: [{ id: 'b' }] }, 'experiments').items, [{ id: 'b' }]);
});

test('agent mode (N26): undecided until the user is known, new user always unset, per user, bad values ignored', () => {
  const m = new Map(), s = { getItem: (k) => m.get(k) ?? null, setItem: (k, v) => m.set(k, v) };
  assert.equal(readAgentMode(s), undefined); assert.equal(readAgentMode(s, ''), undefined); // user (session) not known yet: decide nothing
  assert.equal(writeAgentMode(s, 'contributor'), false); assert.equal(m.size, 0); // never writes a mode for an unknown user
  assert.equal(readAgentMode(s, 'u1'), null);
  writeAgentMode(s, 'contributor', 'u1'); assert.equal(readAgentMode(s, 'u1'), 'contributor');
  assert.equal(readAgentMode(s, 'u2'), null); // a new account in the same browser still sees the choice card
  m.set('r2s.agent.mode', 'standard'); assert.equal(readAgentMode(s, 'u2'), null); // the old global key is ignored
  m.set('r2s.agent.mode.u2', 'evil'); assert.equal(readAgentMode(s, 'u2'), null);
  assert.equal(readAgentMode({ getItem() { throw new Error('blocked'); } }, 'u1'), null);
  assert.equal(AGENT_MODES[0].id, 'standard');
  assert.ok(AGENT_MODES[1].cons.some((c) => /train/.test(c)));
});

test('apiErrorText shows the server message (detail.message) and the reset time in local time (N26)', () => {
  const msg = 'Daily upload limit reached: 20 uploads per day. It resets at 2026-11-01T18:00:00Z (midnight Dhaka time). Deleting a file frees storage.';
  const r = { status: 429, body: { detail: { code: 'QUOTA_UPLOADS', message: msg, reason: 'daily_upload_limit', reset_at: '2026-11-01T18:00:00Z' } } };
  assert.equal(apiErrorText(r, 'Upload failed', (iso) => 'LOCAL(' + iso + ')'), msg.replace('2026-11-01T18:00:00Z', 'LOCAL(2026-11-01T18:00:00Z)'));
  assert.match(apiErrorText(r, 'Upload failed'), /^Daily upload limit reached: 20 uploads per day\. It resets at (?!2026-11-01T18:00:00Z).+ \(midnight Dhaka time\)/);
  assert.equal(apiErrorText({ status: 400, body: { error: { message: 'Bad' } } }, 'x'), 'Bad');
  assert.equal(apiErrorText({ status: 400, body: { detail: { error: { message: 'Nested' } } } }, 'x'), 'Nested');
  assert.equal(apiErrorText({ status: 500, body: null }, 'Upload failed'), 'Upload failed (500).');
  assert.equal(apiErrorText(null, 'Upload failed'), 'Upload failed (network).');
  assert.equal(apiErrorText({ status: 429, body: { detail: { message: 'm', reset_at: 'not a date' } } }, 'x'), 'm');
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
