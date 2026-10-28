import test from 'node:test';
import assert from 'node:assert/strict';
import childProcess from 'node:child_process';
import { syncBuiltinESMExports } from 'node:module';
import { EventEmitter } from 'node:events';
import { PassThrough } from 'node:stream';
import { handleLab, _sessionTest } from '../../Build/lab/session-service.mjs';
import { POST } from '../../Build/web/src/app/api/lab/route.js';
process.env.NODE_ENV = 'test'; // This test subprocess only; no environment/config file is touched.

// Reuse the existing controlled transport pattern; no Python, sockets, or OS-kill claims.
function transport(t) {
  const children = [];
  t.mock.method(childProcess, 'spawn', () => {
    const child = new EventEmitter();
    child.stdin = new PassThrough(); child.stdout = new PassThrough();
    children.push(child); return child;
  });
  syncBuiltinESMExports();
  t.after(() => {
    for (const child of children) child.emit('close', 1);
    t.mock.restoreAll(); syncBuiltinESMExports(); _sessionTest.sessions.clear();
  });
  return children;
}
const error = (code) => ({ status: 'error', error: { code } });
const startRequest = { action: 'start', template: 'free_fall', mystery: true };
function startReply(limitations = ['controlled synthetic transport fixture']) {
  return { status: 'ok', observations: [{ time_s: 0, position_m: 0 }, { time_s: 1, position_m: 4.905 },
    { time_s: 2, position_m: 19.62 }], private: { seed: 42, gravity_m_s2: 9.81, setup: { template: 'free_fall' } }, limitations };
}
function fitReply() {
  // State-machine fixture, not an independently measured/calibrated S11 result.
  return { status: 'ok', gravity: { value: 9.81, uncertainty: 0.01, unit: 'm/s^2',
    source: { label: 'simulated', evidence: 'controlled state-machine fixture' } },
  covariance: { status: 'available' }, uncertainty: { model: 'iid_fixed_clock_scale' } };
}
function finish(child, value) {
  child.stdout.write(typeof value === 'string' || Buffer.isBuffer(value) ? value : JSON.stringify(value));
  child.emit('close', 0);
}
async function start(children) {
  const pending = handleLab(startRequest); finish(children.at(-1), startReply());
  const result = await pending; assert.equal(result.status, 'ok'); return result;
}
test.beforeEach(() => { _sessionTest.sessions.clear(); assert.equal(_sessionTest.getActiveBridges(), 0); });

test('request shape and allowlists reject malformed JSON values before spawning', async (t) => {
  const children = transport(t);
  for (const value of [null, [], false, 42, 'start', {}, { action: 42 }]) {
    assert.deepEqual(await handleLab(value), error('invalid_request'));
  }
  for (const value of [{ action: 'start' }, { ...startRequest, mystery: 1 }, { ...startRequest, template: 'unknown' },
    { ...startRequest, observations: [] }, { ...startRequest, sessionId: 'caller' }]) {
    assert.deepEqual(await handleLab(value), error('invalid_start_request'));
  }
  for (const value of [{ action: 'fit' }, { action: 'fit', sessionId: 1 }, { action: 'fit', sessionId: 'x', observations: [] }]) {
    assert.deepEqual(await handleLab(value), error('invalid_fit_request'));
  }
  assert.deepEqual(await handleLab({ action: 'fit', sessionId: '' }), error('session_not_found_or_expired'));
  assert.deepEqual(await handleLab({ action: 'unknown' }), error('unsupported_action'));
  assert.equal(children.length, 0); assert.equal(_sessionTest.sessions.size, 0);
});

test('observation shape, finite numbers and 2000-sample cap fail closed', async (t) => {
  const children = transport(t);
  for (const observations of [[], null, [{}], [{ time_s: 0, position_m: 0, extra: 1 }],
    [{ time_s: '0', position_m: 0 }], [{ time_s: null, position_m: 0 }],
    Array.from({ length: 2001 }, () => ({ time_s: 0, position_m: 0 }))]) {
    const pending = handleLab(startRequest); finish(children.at(-1), { ...startReply(), observations });
    assert.deepEqual(await pending, error('lab_start_failed')); assert.equal(_sessionTest.sessions.size, 0);
  }
  const observations = Array.from({ length: 2000 }, (_, i) => ({ time_s: i, position_m: i * i }));
  const pending = handleLab(startRequest); finish(children.at(-1), { ...startReply(), observations });
  const result = await pending; assert.equal(result.status, 'ok'); assert.deepEqual(result.observations, observations);
});

test('concurrent failed fits share one attempt and a later completed retry is cached', async (t) => {
  const children = transport(t), sessionStart = await start(children);
  const request = { action: 'fit', sessionId: sessionStart.sessionId };
  const pending = [handleLab(request), handleLab(request), handleLab(request)];
  assert.equal(children.length, 2); finish(children.at(-1), { status: 'error', error: { code: 'fit_not_identifiable' } });
  for (const result of await Promise.all(pending)) assert.deepEqual(result, error('fit_unavailable'));
  const session = _sessionTest.sessions.get(request.sessionId);
  assert.equal(session.result, undefined); assert.equal(session.inFlightPromise, null);
  const retry = [handleLab(request), handleLab(request)]; assert.equal(children.length, 3);
  finish(children.at(-1), fitReply()); const [first, second] = await Promise.all(retry);
  assert.equal(first.status, 'ok'); assert.strictEqual(first, second);
  assert.deepEqual(first.reveal, { gravity: 9.81, uncertainty: 0.01, unit: 'm/s^2', source: 'simulated', fitStatus: 'ok' });
  assert.strictEqual(await handleLab(request), first); assert.equal(children.length, 3);
});

test('malformed successful fits never cache or consume reveal; valid retry succeeds', async (t) => {
  const children = transport(t), sessionStart = await start(children);
  const request = { action: 'fit', sessionId: sessionStart.sessionId };
  const mutations = [
    (r) => { r.gravity.value = 0; }, (r) => { r.gravity.uncertainty = -1; },
    (r) => { r.gravity.unit = 'm'; }, (r) => { r.gravity.source.label = 'measured'; },
    (r) => { r.covariance.status = 'unavailable'; }, (r) => { r.uncertainty.model = 'unknown'; },
  ];
  for (const mutate of mutations) {
    const reply = fitReply(); mutate(reply);
    const attempt = [handleLab(request), handleLab(request)]; finish(children.at(-1), reply);
    for (const result of await Promise.all(attempt)) assert.deepEqual(result, error('lab_request_failed'));
    const session = _sessionTest.sessions.get(request.sessionId);
    assert.equal(session.result, undefined); assert.equal(session.inFlightPromise, null);
  }
  const retry = handleLab(request); finish(children.at(-1), fitReply()); assert.equal((await retry).status, 'ok');
});

test('interleaved failure and success remain confined to their own sessions', async (t) => {
  const children = transport(t), a = await start(children), b = await start(children);
  const requestA = { action: 'fit', sessionId: a.sessionId }, requestB = { action: 'fit', sessionId: b.sessionId };
  const failed = [handleLab(requestA), handleLab(requestA)], completed = [handleLab(requestB), handleLab(requestB)];
  assert.equal(children.length, 4);
  finish(children[3], fitReply()); finish(children[2], { status: 'error' });
  for (const result of await Promise.all(failed)) assert.deepEqual(result, error('fit_unavailable'));
  const [first, second] = await Promise.all(completed);
  assert.equal(first.sessionId, b.sessionId); assert.strictEqual(first, second);
  assert.equal(_sessionTest.sessions.get(a.sessionId).result, undefined);
  assert.strictEqual(await handleLab(requestB), first); assert.equal(children.length, 4);
});

test('a same-ID replacement cannot receive or publish the old session fit', async (t) => {
  const children = transport(t), sessionStart = await start(children);
  const request = { action: 'fit', sessionId: sessionStart.sessionId };
  const old = _sessionTest.sessions.get(request.sessionId), pending = handleLab(request);
  const replacement = { ...old, inFlightPromise: null }; _sessionTest.sessions.set(request.sessionId, replacement);
  finish(children.at(-1), fitReply());
  assert.deepEqual(await pending, error('session_not_found_or_expired'));
  assert.equal(old.result, undefined); assert.equal(replacement.result, undefined);
});

function requestWith(body, headers = {}) {
  return new Request('http://localhost:3000/api/lab', { method: 'POST', headers: { host: 'localhost:3000', ...headers }, body });
}
test('HTTP parser enforces actual UTF-8 byte cap, inclusive boundary and expected errors', async (t) => {
  transport(t);
  const minimal = JSON.stringify({ action: 'fit', sessionId: 'missing' });
  const cases = [
    [minimal + ' '.repeat(1_000_000 - Buffer.byteLength(minimal)), {}, 200, 'session_not_found_or_expired'],
    [minimal + ' '.repeat(1_000_001 - Buffer.byteLength(minimal)), {}, 413, 'request_too_large'],
    [JSON.stringify({ action: 'unknown', payload: '€'.repeat(340000) }), { 'content-length': '1' }, 413, 'request_too_large'],
    ['{}', { 'content-length': '1000001' }, 413, 'request_too_large'],
    ['{', {}, 400, 'invalid_json'], ['', {}, 400, 'invalid_json'], ['null', {}, 200, 'invalid_request'],
  ];
  for (const [body, headers, status, code] of cases) {
    const result = await POST(requestWith(body, headers)); assert.equal(result.status, status);
    assert.equal(result.headers.get('cache-control'), 'no-store'); assert.deepEqual(await result.json(), error(code));
  }
});

test('streamed HTTP JSON preserves split UTF-8 and counts bytes across chunks', async (t) => {
  const children = transport(t), text = JSON.stringify({ action: 'unknown', payload: 'µ' });
  const bytes = Buffer.from(text), split = bytes.indexOf(Buffer.from('µ')) + 1;
  for (const oversized of [false, true]) {
    const chunks = [bytes.subarray(0, split), bytes.subarray(split)];
    if (oversized) chunks.push(Buffer.alloc(1_000_001 - bytes.byteLength, 32));
    const body = new ReadableStream({ start(controller) { for (const chunk of chunks) controller.enqueue(chunk); controller.close(); } });
    const result = await POST(new Request('http://localhost:3000/api/lab', { method: 'POST', duplex: 'half',
      headers: { host: 'localhost:3000', 'content-length': '1' }, body }));
    assert.equal(result.status, oversized ? 413 : 200);
    assert.deepEqual(await result.json(), error(oversized ? 'request_too_large' : 'unsupported_action'));
  }
  assert.equal(children.length, 0);
});

test('ASCII-escaped current-producer-style output has no Unicode chunk loss', async (t) => {
  const children = transport(t), reply = startReply(['synthetic µs timing']);
  const ascii = JSON.stringify(reply).replace('µ', '\\u00b5');
  assert.equal(Buffer.byteLength(ascii), ascii.length);
  const pending = handleLab(startRequest), child = children.at(-1), split = ascii.indexOf('\\u00b5') + 3;
  child.stdout.write(Buffer.from(ascii.slice(0, split))); child.stdout.write(Buffer.from(ascii.slice(split))); child.emit('close', 0);
  assert.deepEqual((await pending).limitations, reply.limitations);
});

test('UTF-8 bridge response decoding is independent of stream chunk boundaries', async (t) => {
  const children = transport(t), reply = startReply(['synthetic µs timing']);
  const bytes = Buffer.from(JSON.stringify(reply)), split = bytes.indexOf(Buffer.from('µ')) + 1;
  assert.ok(split > 0);
  const pending = handleLab(startRequest), child = children.at(-1);
  child.stdout.write(bytes.subarray(0, split)); child.stdout.write(bytes.subarray(split)); child.emit('close', 0);
  const result = await pending; assert.equal(result.status, 'ok');
  assert.deepEqual(result.limitations, reply.limitations, 'a split UTF-8 character must round-trip unchanged');
});

test('bridge response cap rejects more than one million UTF-8 bytes, not just code units', async (t) => {
  const children = transport(t), bytes = Buffer.from(JSON.stringify(startReply(['€'.repeat(340000)])));
  assert.ok(bytes.byteLength > 1_000_000); assert.ok(bytes.toString('utf8').length < 1_000_000);
  const pending = handleLab(startRequest); finish(children.at(-1), bytes);
  const result = await pending;
  t.diagnostic(JSON.stringify({ bytes: bytes.byteLength, codeUnits: bytes.toString('utf8').length,
    actualStatus: result.status, insertedSessions: _sessionTest.sessions.size }));
  assert.equal(result.status, 'error', 'oversized UTF-8 output must fail closed');
  assert.deepEqual(result, error('lab_request_failed'));
  assert.equal(_sessionTest.sessions.size, 0);
});
