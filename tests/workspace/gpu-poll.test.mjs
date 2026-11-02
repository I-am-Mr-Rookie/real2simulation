import assert from 'node:assert/strict';
import test from 'node:test';
import { createLive } from '../../Build/web/src/workspace/live-view.mjs';

test('GPU hook ticks locally each second, keeps 10s API polls, refreshes on visibility and cleans up', async (t) => {
  const effects = [], updates = [], timers = new Map(), listeners = new Map();
  let now = 100000, calls = 0;
  let body = { state: 'green', queue_length: 0, source: 'modal+jobs', idle_seconds_remaining: 900 };
  const doc = { visibilityState: 'visible', addEventListener: (k, fn) => listeners.set(k, fn), removeEventListener: (k) => listeners.delete(k) };
  const originalDoc = Object.getOwnPropertyDescriptor(globalThis, 'document');
  Object.defineProperty(globalThis, 'document', { value: doc, configurable: true });
  t.after(() => originalDoc ? Object.defineProperty(globalThis, 'document', originalDoc) : delete globalThis.document);
  t.mock.method(Date, 'now', () => now);
  t.mock.method(globalThis, 'setInterval', (fn, ms) => { timers.set(ms, fn); return ms; });
  t.mock.method(globalThis, 'clearInterval', (id) => timers.delete(id));
  t.mock.method(globalThis, 'fetch', async () => { calls++; return { status: 200, ok: true, json: async () => body }; });
  const React = {
    createElement: () => null,
    useState: (value) => [value, (v) => { if (v?.tone) updates.push(v); }],
    useRef: (current) => ({ current }), useCallback: (fn) => fn, useEffect: (fn) => effects.push(fn)
  };
  createLive(React).useLive(true, () => {}, 'user');
  const cleanup = effects.find((fn) => String(fn).includes("call('/gpu/status')"))();
  const flush = async () => { await new Promise((r) => setImmediate(r)); };
  await flush();
  assert.equal(updates.at(-1).label, 'GPU on, sleeps in 15:00');
  now += 28000; timers.get(1000)();
  assert.equal(updates.at(-1).label, 'GPU on, sleeps in 14:32');
  assert.equal(calls, 1); // Local ticks do not call Modal or the API.
  body = { state: 'yellow', queue_length: 1, your_position: 1 };
  await timers.get(10000)();
  assert.equal(updates.at(-1).label, 'GPU starting');
  body = { state: 'green', queue_length: 1, idle_seconds_remaining: 900 };
  await timers.get(10000)();
  assert.equal(updates.at(-1).label, 'GPU on, sleeps in 15:00 after job');
  body = { state: 'green', queue_length: 0, idle_seconds_remaining: 900 };
  await timers.get(10000)();
  assert.equal(updates.at(-1).label, 'GPU on, sleeps in 15:00');
  doc.visibilityState = 'hidden';
  const count = updates.length, requests = calls;
  timers.get(1000)(); await timers.get(10000)();
  assert.equal(updates.length, count); assert.equal(calls, requests);
  doc.visibilityState = 'visible'; body = { state: 'red', queue_length: 0 };
  await listeners.get('visibilitychange')();
  assert.equal(updates.at(-1).label, 'GPU sleeping');
  cleanup();
  assert.equal(timers.size, 0); assert.equal(listeners.size, 0);
});
