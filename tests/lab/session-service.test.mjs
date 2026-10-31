import test from 'node:test';
import assert from 'node:assert/strict';
import childProcess from 'node:child_process';
import { syncBuiltinESMExports } from 'node:module';
import { EventEmitter } from 'node:events';
import { PassThrough } from 'node:stream';
import { handleLab, _sessionTest } from '../../Build/lab/session-service.mjs';
import { POST } from '../../Build/web/src/app/api/lab/route.js';
process.env.NODE_ENV ??= 'test';
test.beforeEach(() => _sessionTest.sessions.clear());

function actualStart(template, mystery = false, seed) {
  const code = `import importlib.util,json,sys; from unittest.mock import patch; s=importlib.util.spec_from_file_location('bridge','Build/lab/session-bridge.py'); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); r=json.loads(sys.stdin.read());\nwith patch.object(m.secrets,'randbits',return_value=${seed ?? 42}): print(json.dumps(m.handle(r)))`;
  const proc = childProcess.spawnSync(process.env.PYTHON || 'python', ['-c', code], {
    input: JSON.stringify({ action: 'start', template, mystery }), encoding: 'utf8', timeout: 30000,
    env: { PATH: process.env.PATH || '', SystemRoot: process.env.SystemRoot || '', PYTHONPATH: process.cwd(), PYTHONIOENCODING: 'utf-8' },
  });
  assert.equal(proc.status, 0, 'actual Python bridge must complete');
  const result = JSON.parse(proc.stdout); assert.equal(result.status, 'ok'); return result;
}
function assertNoSetup(value) {
  const text = JSON.stringify(value);
  for (const key of ['browserSimulation', 'validatedSetup', 'artifact_version', 'private', 'seed', 'setup', 'gravity_m_s2']) {
    assert.equal(text.includes(`"${key}"`), false, `public response must not contain ${key}`);
  }
}

test('all four normal DTOs match actual Python validated exports, not authored envelope fixtures', async () => {
  for (const template of ['free_fall', 'projectile', 'ramp', 'pendulum']) {
    const expected = actualStart(template);
    const start = await handleLab({ action: 'start', template, mystery: false });
    assert.equal(start.status, 'ok'); assert.equal(start.source, 'simulated');
    assert.deepEqual(start.browserSimulation, expected.browserSimulation);
    assert.deepEqual(start.observations, expected.observations);
    const artifact = start.browserSimulation.validatedSetup;
    assert.equal(artifact.scene.synthetic, true); assert.equal(artifact.scene.provenance.method, 'synthetic');
    const sim = artifact.spec.simulation;
    assert.ok(Math.round(sim.duration.value / sim.time_step.value) + 1 <= 2000);
    assert.ok(start.observations.length <= 2000);
    assert.equal('private' in start, false);
  }
});

test('caller-supplied setups remain outside the fixed request allowlist', async () => {
  for (const mystery of [false, true]) for (const key of ['browserSimulation', 'validatedSetup', 'private', 'seed', 'gravity']) {
    assert.deepEqual(await handleLab({ action: 'start', template: 'free_fall', mystery, [key]: {} }),
      { status: 'error', error: { code: 'invalid_start_request' } });
  }
  assert.equal(_sessionTest.getActiveBridges(), 0); assert.equal(_sessionTest.sessions.size, 0);
});

test('normal start/fit uses the actual bridge and fitter', async () => {
  const start = await handleLab({ action: 'start', template: 'free_fall', mystery: false });
  assert.equal(start.status, 'ok'); assert.equal(start.mode, 'normal'); assert.ok(start.gravity);
  const fit = await handleLab({ action: 'fit', sessionId: start.sessionId });
  assert.equal(fit.status, 'ok'); assert.equal(fit.sessionId, start.sessionId); assert.equal(fit.fit.status, 'ok'); assert.ok(fit.fit.gravity); assert.ok(Math.abs(fit.reveal.gravity - 9.81) < 0.001);
  assertNoSetup(fit);
  assert.deepEqual(await Promise.all([handleLab({ action: 'fit', sessionId: start.sessionId }), handleLab({ action: 'fit', sessionId: start.sessionId })]), [fit, fit]);
});

test('mystery redacts pre-fit and reveals only through matching fit', async () => {
  const start = await handleLab({ action: 'start', template: 'projectile', mystery: true });
  assert.equal(start.status, 'ok'); assert.equal(start.mode, 'mystery-g'); assert.equal('gravity' in start, false);
  assert.equal(JSON.stringify(start).includes('private'), false); assert.equal(JSON.stringify(start).includes('seed'), false);
  const fit = await handleLab({ action: 'fit', sessionId: start.sessionId });
  assert.equal(fit.status, 'ok'); assert.equal(fit.reveal.source, 'simulated'); assert.ok(fit.reveal.gravity > 0);
  assertNoSetup(fit);
});

test('pre-abort does not spawn and expired reads do not evict live sessions', async () => {
  const controller = new AbortController(); controller.abort();
  const aborted = await handleLab({ action: 'start', template: 'free_fall', mystery: false }, { signal: controller.signal });
  assert.equal(aborted.status, 'error'); assert.equal(_sessionTest.getActiveBridges(), 0);
  const id = 'live-test'; _sessionTest.sessions.set(id, { id, expiresAt: Date.now() + 100000 }); _sessionTest.expireOnly(); assert.equal(_sessionTest.sessions.has(id), true); _sessionTest.sessions.delete(id);
  for (let i = 0; i < 64; i += 1) _sessionTest.sessions.set(`cap-${i}`, { id: `cap-${i}`, expiresAt: Date.now() + 100000 });
  const inserted = await handleLab({ action: 'start', template: 'free_fall', mystery: false }); assert.equal(inserted.status, 'ok'); assert.equal(_sessionTest.sessions.size, 64); assert.equal(_sessionTest.sessions.has('cap-0'), false);
});

test('allowlists, expiry and bounded session errors are clean', async () => {
  assert.equal((await handleLab({ action: 'start', template: 'free_fall', mystery: 'yes' })).status, 'error');
  assert.equal((await handleLab({ action: 'start', template: 'bad', mystery: false })).status, 'error');
  assert.equal((await handleLab({ action: 'fit', sessionId: 'missing' })).status, 'error');
  const start = await handleLab({ action: 'start', template: 'ramp', mystery: false });
  _sessionTest.sessions.get(start.sessionId).expiresAt = Date.now() - 1;
  assert.equal((await handleLab({ action: 'fit', sessionId: start.sessionId })).error.code, 'session_not_found_or_expired');
});

test('aborting an active bridge settles and releases its capacity', async () => {
  const controller = new AbortController();
  const count = _sessionTest.sessions.size;
  const pending = handleLab({ action: 'start', template: 'free_fall', mystery: false }, { signal: controller.signal });
  assert.equal(_sessionTest.getActiveBridges(), 1);
  controller.abort();
  assert.equal(controller.signal.aborted, true);
  assert.deepEqual(await pending, { status: 'error', error: { code: 'lab_request_failed' } });
  assert.equal(_sessionTest.sessions.size, count);
  assert.equal(_sessionTest.getActiveBridges(), 0);
});

test('loopback route accepts the UI contract and rejects nonlocal hosts', async () => {
  const body = JSON.stringify({ action: 'start', template: 'free_fall', mystery: false });
  const good = await POST(new Request('http://localhost:3000/api/lab', { method: 'POST', headers: { host: 'localhost:3000', origin: 'http://localhost:3000' }, body }));
  assert.equal(good.status, 200); assert.equal((await good.json()).status, 'ok');
  const bad = await POST(new Request('http://example.test/api/lab', { method: 'POST', headers: { host: 'example.test' }, body }));
  assert.equal(bad.status, 403); assert.equal((await bad.json()).error.code, 'local_origin_required');
  const oversized = await POST(new Request('http://localhost:3000/api/lab', { method: 'POST', headers: { host: 'localhost:3000', 'content-length': '1000001' }, body: '{}' }));
  assert.equal(oversized.status, 413); assert.equal((await oversized.json()).error.code, 'request_too_large');
});

test('production route (S15av) keeps same-origin and schema guards with friendly messages', async () => {
  const previous = process.env.NODE_ENV;
  try {
    process.env.NODE_ENV = 'production';
    const cross = await POST(new Request('http://example.app/api/lab', { method: 'POST', headers: { host: 'example.app', origin: 'https://evil.example' }, body: '{}' }));
    assert.equal(cross.status, 403); const crossBody = await cross.json();
    assert.equal(crossBody.error.code, 'local_origin_required'); assert.ok(crossBody.error.message);
    const invalid = await (await POST(new Request('http://example.app/api/lab', { method: 'POST', headers: { host: 'example.app' }, body: '{}' }))).json();
    assert.equal(invalid.error.code, 'invalid_request'); assert.match(invalid.error.message, /try again/i);
  } finally { process.env.NODE_ENV = previous; }
});

test('cold concurrent fits reuse one bridge and pre-aborted cached reads fail', async () => {
  const start = await handleLab({ action: 'start', template: 'free_fall', mystery: true });
  assert.equal(start.status, 'ok');
  const first = handleLab({ action: 'fit', sessionId: start.sessionId });
  const second = handleLab({ action: 'fit', sessionId: start.sessionId });
  const joiningController = new AbortController();
  const joining = handleLab({ action: 'fit', sessionId: start.sessionId }, { signal: joiningController.signal });
  joiningController.abort();
  assert.equal(_sessionTest.getActiveBridges(), 1);
  const [a, b] = await Promise.all([first, second]);
  assert.equal(a.status, 'ok'); assert.strictEqual(a, b);
  assert.deepEqual(await joining, { status: 'error', error: { code: 'lab_request_failed' } });
  const controller = new AbortController(); controller.abort();
  assert.deepEqual(await handleLab({ action: 'fit', sessionId: start.sessionId }, { signal: controller.signal }),
    { status: 'error', error: { code: 'lab_request_failed' } });
});

test('evicted in-flight sessions never publish a fit or reveal', async () => {
  const start = await handleLab({ action: 'start', template: 'free_fall', mystery: true });
  assert.equal(start.status, 'ok');
  const session = _sessionTest.sessions.get(start.sessionId);
  const pending = handleLab({ action: 'fit', sessionId: start.sessionId });
  assert.equal(_sessionTest.getActiveBridges(), 1);
  _sessionTest.sessions.delete(start.sessionId);
  assert.deepEqual(await pending, { status: 'error', error: { code: 'session_not_found_or_expired' } });
  assert.equal(session.result, undefined);
});

// Controlled bridge events test lifecycle bookkeeping, not OS process-tree death.
function controlledBridge(t) {
  const children = [];
  t.mock.method(childProcess, 'spawn', () => {
    const child = new EventEmitter();
    child.stdin = new PassThrough(); child.stdout = new PassThrough();
    children.push(child); return child;
  });
  syncBuiltinESMExports();
  t.after(() => {
    for (const child of children) child.emit('close', 1);
    t.mock.restoreAll(); syncBuiltinESMExports();
  });
  return children;
}
const startRequest = { action: 'start', template: 'free_fall', mystery: false };
// Actual fixed-action export; controlled events below test transport/lifecycle, not producer authentication.
const startReply = actualStart('free_fall');

test('normal-to-Mystery starts never carry a previous normal DTO into the new response', async () => {
  const normal = await handleLab(startRequest); assert.ok(normal.browserSimulation);
  for (const template of ['free_fall', 'projectile']) {
    const mystery = await handleLab({ action: 'start', template, mystery: true });
    assert.equal(mystery.status, 'ok'); assert.equal(mystery.mode, 'mystery-g');
    assert.equal('gravity' in mystery, false); assertNoSetup(mystery);
    assert.notEqual(mystery.sessionId, normal.sessionId);
  }
});

test('service strips an injected DTO even from actual Mystery replies across ballistic seeds', async (t) => {
  // The actual bridge must already omit the DTO; the service independently refuses to publish one.
  const replies = [];
  for (const template of ['free_fall', 'projectile']) for (const seed of [0, 1, 2**31, 2**32 - 1]) {
    const reply = actualStart(template, true, seed);
    assert.equal('browserSimulation' in reply, false);
    replies.push({ template, reply });
  }
  const children = controlledBridge(t);
  for (const { template, reply } of replies) {
    const pending = handleLab({ action: 'start', template, mystery: true });
    children.at(-1).stdout.write(JSON.stringify({ ...reply, browserSimulation: startReply.browserSimulation,
      gravity: { seed: reply.private.seed, setup: reply.private.setup }, nested: { validatedSetup: startReply.browserSimulation.validatedSetup } }));
    children.at(-1).emit('close', 0);
    const result = await pending;
    assert.equal(result.status, 'ok'); assert.equal('gravity' in result, false); assertNoSetup(result);
  }
});

test('normal transport fails closed for missing/mismatched/non-synthetic or unbounded exports', async (t) => {
  const children = controlledBridge(t);
  const mutations = [
    (r) => { delete r.browserSimulation; },
    (r) => { r.source = 'measured'; },
    (r) => { r.browserSimulation.mode = 'mystery-g'; },
    (r) => { r.browserSimulation.private = { seed: 123 }; },
    (r) => { r.browserSimulation.validatedSetup.artifact_version = 'fake'; },
    (r) => { r.browserSimulation.validatedSetup.validation = 'unchecked'; },
    (r) => { r.browserSimulation.validatedSetup.producer = 'untrusted'; },
    (r) => { r.browserSimulation.validatedSetup.private = { setup: 'do not forward' }; },
    (r) => { r.browserSimulation.validatedSetup.spec.template = 'projectile'; },
    (r) => { r.browserSimulation.validatedSetup.scene.synthetic = false; },
    (r) => { r.browserSimulation.validatedSetup.scene.provenance.method = 'reconstructed'; },
    (r) => { r.browserSimulation.validatedSetup.spec.scene.scene_id = 'different'; },
    (r) => { r.browserSimulation.validatedSetup.spec.simulation.seed = 123; },
    (r) => { r.browserSimulation.validatedSetup.spec.environment.gravity.value = 4; },
    (r) => { r.browserSimulation.validatedSetup.scene.gravity.magnitude_m_s2 = 4; },
    (r) => { r.browserSimulation.validatedSetup.spec.environment.gravity.source.label = 'measured'; },
    (r) => { r.browserSimulation.validatedSetup.spec.simulation.duration.value = 2; },
    (r) => { r.browserSimulation.validatedSetup.spec.simulation.duration.value = 0.2005; },
    (r) => { r.browserSimulation.validatedSetup.spec.simulation.time_step.value = 0; },
    (r) => { r.browserSimulation.validatedSetup.spec.simulation.time_step.value = '0.001'; },
  ];
  for (const mutate of mutations) {
    const reply = structuredClone(startReply); mutate(reply);
    const pending = handleLab(startRequest);
    children.at(-1).stdout.write(JSON.stringify(reply)); children.at(-1).emit('close', 0);
    assert.deepEqual(await pending, { status: 'error', error: { code: 'lab_start_failed' } });
  }
  assert.equal(_sessionTest.sessions.size, 0);
});

test('normal transport includes the initial point in its 2000-sample ceiling', async (t) => {
  const children = controlledBridge(t), reply = structuredClone(startReply);
  // Deliberately controlled bridge output exercises the cap, not Python producer authentication.
  reply.browserSimulation.validatedSetup.spec.simulation.duration.value = 1.999;
  const pending = handleLab(startRequest);
  children[0].stdout.write(JSON.stringify(reply)); children[0].emit('close', 0);
  const result = await pending;
  assert.equal(result.status, 'ok');
  const sim = result.browserSimulation.validatedSetup.spec.simulation;
  assert.equal(Math.round(sim.duration.value / sim.time_step.value) + 1, 2000);
});

test('Mystery error and exception envelopes never forward nested bridge details', async (t) => {
  const children = controlledBridge(t);
  for (const reply of [{ status: 'error', error: { code: 'private seed setup', nested: startReply } },
    { ...startReply, private: null }]) {
    const pending = handleLab({ action: 'start', template: 'free_fall', mystery: true });
    children.at(-1).stdout.write(JSON.stringify(reply)); children.at(-1).emit('close', 0);
    const result = await pending;
    assert.equal(result.status, 'error'); assertNoSetup(result);
    assert.deepEqual(Object.keys(result.error), ['code']);
    assert.ok(['lab_start_failed', 'lab_request_failed'].includes(result.error.code));
  }
});

test('abort cannot become success when bridge closes with code zero', async (t) => {
  const children = controlledBridge(t), controller = new AbortController();
  const count = _sessionTest.sessions.size;
  const pending = handleLab(startRequest, { signal: controller.signal });
  controller.abort();
  children[0].stdout.write(JSON.stringify(startReply)); children[0].emit('close', 0);
  assert.deepEqual(await pending, { status: 'error', error: { code: 'lab_request_failed' } });
  assert.equal(_sessionTest.sessions.size, count); assert.equal(_sessionTest.getActiveBridges(), 0);
});

test('stdin failure retains bridge capacity until close, including the four-process cap', async (t) => {
  const children = controlledBridge(t);
  const pending = Array.from({ length: 4 }, () => handleLab(startRequest));
  assert.equal(_sessionTest.getActiveBridges(), 4);
  children[0].stdin.emit('error', new Error('controlled stdin failure'));
  assert.equal(_sessionTest.getActiveBridges(), 4);
  assert.deepEqual(await handleLab(startRequest), { status: 'error', error: { code: 'lab_request_failed' } });
  assert.equal(children.length, 4);
  for (const child of children) child.emit('close', 1);
  for (const result of await Promise.all(pending)) assert.equal(result.status, 'error');
  assert.equal(_sessionTest.getActiveBridges(), 0);
});

test('synchronous spawn failures do not consume capacity or expose internal errors', async (t) => {
  t.mock.method(childProcess, 'spawn', () => { throw new Error('private process details'); });
  syncBuiltinESMExports();
  t.after(() => { t.mock.restoreAll(); syncBuiltinESMExports(); });
  for (let i = 0; i < 5; i += 1) {
    assert.deepEqual(await handleLab(startRequest), { status: 'error', error: { code: 'lab_request_failed' } });
    assert.equal(_sessionTest.getActiveBridges(), 0);
  }
});

function pauseHash(t) {
  let entered, release;
  const reached = new Promise((resolve) => { entered = resolve; });
  const gate = new Promise((resolve) => { release = resolve; });
  const digest = globalThis.crypto.subtle.digest.bind(globalThis.crypto.subtle);
  t.mock.method(globalThis.crypto.subtle, 'digest', async (...args) => {
    const result = await digest(...args); entered(); await gate; return result;
  });
  t.after(release);
  return { reached, release };
}

for (const transition of ['expired', 'evicted', 'aborted']) {
  test(`${transition} during trusted handoff hashing cannot reveal or cache a fit`, async (t) => {
    const children = controlledBridge(t), hash = pauseHash(t), controller = new AbortController();
    const id = `hash-${transition}`; let reveals = 0;
    const session = { id, template: 'free_fall', observations: startReply.observations,
      expiresAt: Date.now() + 100000, mysterySession: { revealFit: () => { reveals += 1; return { reveal: {} }; } } };
    _sessionTest.sessions.set(id, session); t.after(() => _sessionTest.sessions.delete(id));
    const pending = handleLab({ action: 'fit', sessionId: id }, { signal: controller.signal });
    // A synthetic S11-shaped fixture exercises service state, not fitter accuracy.
    children[0].stdout.write(JSON.stringify({ status: 'ok', gravity: { value: 9.81, uncertainty: 0.01,
      unit: 'm/s^2', source: { label: 'simulated', evidence: 'controlled test fixture' } },
    covariance: { status: 'available' }, uncertainty: { model: 'iid_fixed_clock_scale' } }));
    children[0].emit('close', 0);
    await hash.reached;
    if (transition === 'expired') session.expiresAt = Date.now() - 1;
    if (transition === 'evicted') _sessionTest.sessions.delete(id);
    if (transition === 'aborted') controller.abort();
    hash.release();
    const code = transition === 'expired' ? 'session_expired_during_fit' : transition === 'evicted' ? 'session_not_found_or_expired' : 'lab_request_failed';
    assert.deepEqual(await pending, { status: 'error', error: { code } });
    assert.equal(reveals, 0); assert.equal(session.result, undefined);
  });
}

test('abort during start hashing does not insert a session', async (t) => {
  const children = controlledBridge(t), hash = pauseHash(t), controller = new AbortController();
  const count = _sessionTest.sessions.size;
  const pending = handleLab(startRequest, { signal: controller.signal });
  children[0].stdout.write(JSON.stringify(startReply)); children[0].emit('close', 0);
  await hash.reached; controller.abort(); hash.release();
  assert.deepEqual(await pending, { status: 'error', error: { code: 'lab_request_failed' } });
  assert.equal(_sessionTest.sessions.size, count);
});

test('a failed active Mystery-g fit can retry without consuming its reveal', async () => {
  const start = await handleLab({ action: 'start', template: 'projectile', mystery: true });
  assert.equal(start.status, 'ok'); assert.equal('reveal' in start, false);
  const controller = new AbortController();
  const pending = handleLab({ action: 'fit', sessionId: start.sessionId }, { signal: controller.signal });
  assert.equal(_sessionTest.getActiveBridges(), 1); controller.abort();
  assert.equal((await pending).status, 'error'); assert.equal(_sessionTest.getActiveBridges(), 0);
  const session = _sessionTest.sessions.get(start.sessionId);
  assert.equal(session.result, undefined); assert.equal(session.inFlightPromise, null);
  const retry = await handleLab({ action: 'fit', sessionId: start.sessionId });
  assert.equal(retry.status, 'ok'); assert.equal(retry.reveal.source, 'simulated');
});

test('UTF-8 bridge output preserves every interior split of two, three and four byte characters', async (t) => {
  const children = controlledBridge(t);
  for (const text of ['µ', '€', '😀']) {
    const reply = { ...startReply, limitations: [text] }, bytes = Buffer.from(JSON.stringify(reply));
    const offset = bytes.indexOf(Buffer.from(text));
    for (let part = 1; part < Buffer.byteLength(text); part += 1) {
      const pending = handleLab(startRequest), child = children.at(-1), split = offset + part;
      child.stdout.write(bytes.subarray(0, split)); child.stdout.write(bytes.subarray(split)); child.emit('close', 0);
      const result = await pending; assert.equal(result.status, 'ok'); assert.deepEqual(result.limitations, [text]);
    }
  }
});

test('bridge raw-byte ceiling accepts exactly one million bytes with multibyte output', async (t) => {
  const children = controlledBridge(t), reply = { ...startReply, limitations: ['µ€😀'] };
  const bytes = Buffer.from(JSON.stringify(reply)), pending = handleLab(startRequest), child = children.at(-1);
  child.stdout.write(bytes); child.stdout.write(Buffer.alloc(1_000_000 - bytes.length, 32)); child.emit('close', 0);
  const result = await pending; assert.equal(result.status, 'ok'); assert.deepEqual(result.limitations, reply.limitations);
  assert.equal(_sessionTest.getActiveBridges(), 0);
});

test('bridge raw-byte overflow is sticky and retains capacity until close', async (t) => {
  const children = controlledBridge(t), count = _sessionTest.sessions.size;
  const bytes = Buffer.from(JSON.stringify({ ...startReply, limitations: ['µ€😀'] }));
  const pending = handleLab(startRequest), child = children.at(-1);
  child.stdout.write(bytes); child.stdout.write(Buffer.alloc(1_000_000 - bytes.length, 32));
  assert.equal(_sessionTest.getActiveBridges(), 1);
  child.stdout.write(Buffer.from(' '));
  assert.equal(_sessionTest.getActiveBridges(), 1);
  child.stdout.write(Buffer.from(JSON.stringify(startReply))); child.emit('close', 0);
  assert.deepEqual(await pending, { status: 'error', error: { code: 'lab_request_failed' } });
  assert.equal(_sessionTest.sessions.size, count); assert.equal(_sessionTest.getActiveBridges(), 0);
});

test('timeout cannot become success and capacity is retained until close', async (t) => {
  const children = controlledBridge(t);
  t.mock.timers.enable({ apis: ['setTimeout'] });
  const pending = handleLab(startRequest);
  t.mock.timers.tick(30000);
  assert.equal(_sessionTest.getActiveBridges(), 1);
  children[0].stdout.write(JSON.stringify(startReply)); children[0].emit('close', 0);
  assert.deepEqual(await pending, { status: 'error', error: { code: 'lab_request_failed' } });
  assert.equal(_sessionTest.getActiveBridges(), 0);
});

for (const [name, response] of [['invalid JSON', '{private-details'], ['null', 'null'],
  ['unexpected shape', '{}'], ['oversized output', 'x'.repeat(1_000_001)]]) {
  test(`${name} bridge output returns a bounded error envelope`, async (t) => {
    const children = controlledBridge(t);
    const pending = handleLab(startRequest);
    children[0].stdout.write(response); children[0].emit('close', 0);
    const result = await pending;
    assert.equal(result.status, 'error');
    assert.deepEqual(Object.keys(result), ['status', 'error']);
    assert.deepEqual(Object.keys(result.error), ['code']);
    assert.ok(['lab_request_failed', 'lab_start_failed'].includes(result.error.code));
    assert.equal(_sessionTest.getActiveBridges(), 0);
  });
}

test('asynchronous spawn error retains its slot until close and never returns success', async (t) => {
  const children = controlledBridge(t);
  const pending = handleLab(startRequest);
  children[0].emit('error', new Error('private spawn details'));
  assert.equal(_sessionTest.getActiveBridges(), 1);
  children[0].stdout.write(JSON.stringify(startReply)); children[0].emit('close', 0);
  assert.deepEqual(await pending, { status: 'error', error: { code: 'lab_request_failed' } });
  assert.equal(_sessionTest.getActiveBridges(), 0);
});

test('a real capacity insertion evicts the oldest in-flight session without revealing it', async (t) => {
  const children = controlledBridge(t), id = 'oldest-fitting-session';
  const session = { id, template: 'free_fall', observations: startReply.observations, expiresAt: Date.now() + 100000 };
  _sessionTest.sessions.set(id, session);
  for (let i = 0; i < 63; i += 1) _sessionTest.sessions.set(`live-${i}`, { id: `live-${i}`, expiresAt: Date.now() + 100000 });
  const fitting = handleLab({ action: 'fit', sessionId: id });
  const starting = handleLab(startRequest);
  children[1].stdout.write(JSON.stringify(startReply)); children[1].emit('close', 0);
  assert.equal((await starting).status, 'ok');
  assert.equal(_sessionTest.sessions.size, 64); assert.equal(_sessionTest.sessions.has(id), false);
  children[0].stdout.write(JSON.stringify({ status: 'ok', gravity: {} })); children[0].emit('close', 0);
  assert.deepEqual(await fitting, { status: 'error', error: { code: 'session_not_found_or_expired' } });
  assert.equal(session.result, undefined); assert.equal(_sessionTest.getActiveBridges(), 0);
});

test('expiry while a bridge is running rejects the fit and permits no reveal', async (t) => {
  const children = controlledBridge(t), id = 'expiring-fit';
  const session = { id, template: 'projectile', observations: startReply.observations, expiresAt: Date.now() + 100000 };
  _sessionTest.sessions.set(id, session);
  const pending = handleLab({ action: 'fit', sessionId: id });
  session.expiresAt = Date.now() - 1;
  children[0].stdout.write(JSON.stringify({ status: 'ok', gravity: {} })); children[0].emit('close', 0);
  assert.deepEqual(await pending, { status: 'error', error: { code: 'session_expired_during_fit' } });
  assert.equal(session.result, undefined); assert.equal(session.inFlightPromise, null);
});
