import test from 'node:test';
import assert from 'node:assert/strict';
import { handleLab, _sessionTest } from '../../Build/lab/session-service.mjs';
import { POST } from '../../Build/web/src/app/api/lab/route.js';

test('normal start/fit uses the actual bridge and fitter', async () => {
  const start = await handleLab({ action: 'start', template: 'free_fall', mystery: false });
  assert.equal(start.status, 'ok'); assert.equal(start.mode, 'normal'); assert.ok(start.gravity);
  const fit = await handleLab({ action: 'fit', sessionId: start.sessionId });
  assert.equal(fit.status, 'ok'); assert.equal(fit.sessionId, start.sessionId); assert.equal(fit.fit.status, 'ok'); assert.ok(fit.fit.gravity); assert.ok(Math.abs(fit.reveal.gravity - 9.81) < 0.001);
  assert.deepEqual(await Promise.all([handleLab({ action: 'fit', sessionId: start.sessionId }), handleLab({ action: 'fit', sessionId: start.sessionId })]), [fit, fit]);
});

test('mystery redacts pre-fit and reveals only through matching fit', async () => {
  const start = await handleLab({ action: 'start', template: 'projectile', mystery: true });
  assert.equal(start.status, 'ok'); assert.equal(start.mode, 'mystery-g'); assert.equal('gravity' in start, false);
  assert.equal(JSON.stringify(start).includes('private'), false); assert.equal(JSON.stringify(start).includes('seed'), false);
  const fit = await handleLab({ action: 'fit', sessionId: start.sessionId });
  assert.equal(fit.status, 'ok'); assert.equal(fit.reveal.source, 'simulated'); assert.ok(fit.reveal.gravity > 0);
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

test('loopback route accepts the UI contract and rejects nonlocal hosts', async () => {
  const body = JSON.stringify({ action: 'start', template: 'free_fall', mystery: false });
  const good = await POST(new Request('http://localhost:3000/api/lab', { method: 'POST', headers: { host: 'localhost:3000', origin: 'http://localhost:3000' }, body }));
  assert.equal(good.status, 200); assert.equal((await good.json()).status, 'ok');
  const bad = await POST(new Request('http://example.test/api/lab', { method: 'POST', headers: { host: 'example.test' }, body }));
  assert.equal(bad.status, 403); assert.equal((await bad.json()).error.code, 'local_origin_required');
  const oversized = await POST(new Request('http://localhost:3000/api/lab', { method: 'POST', headers: { host: 'localhost:3000', 'content-length': '1000001' }, body: '{}' }));
  assert.equal(oversized.status, 413); assert.equal((await oversized.json()).error.code, 'request_too_large');
});
