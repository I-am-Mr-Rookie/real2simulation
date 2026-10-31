import test from 'node:test';
import assert from 'node:assert/strict';
import http from 'node:http';
import { spawnSync } from 'node:child_process';
import { POST } from '../../Build/web/src/app/api/lab/route.js';
import { _sessionTest } from '../../Build/lab/session-service.mjs';

// S15av: production web path proxies to the API lab bridge; this stub runs the real session-bridge.py per request.
const TOKEN = 'test-internal-token';
let server, base, calls = 0;
test.before(async () => {
  server = http.createServer((req, res) => {
    let body = ''; req.on('data', (c) => { body += c; }); req.on('end', () => {
      calls += 1;
      if (req.url !== '/internal/lab/bridge' || req.headers['x-workspace-token'] !== TOKEN) { res.writeHead(401); return res.end('{}'); }
      const proc = spawnSync(process.env.PYTHON || 'python', ['Build/lab/session-bridge.py'], { input: body, encoding: 'utf8', timeout: 30000, env: { ...process.env, PYTHONPATH: process.cwd(), PYTHONIOENCODING: 'utf-8' } });
      res.writeHead(proc.status === 0 ? 200 : 500, { 'content-type': 'application/json' }); res.end(proc.stdout || '{}');
    });
  });
  await new Promise((r) => server.listen(0, '127.0.0.1', r)); base = `http://127.0.0.1:${server.address().port}`;
});
test.after(() => server.close());
const saved = { ...process.env };
test.beforeEach(() => { _sessionTest.sessions.clear(); Object.assign(process.env, { NODE_ENV: 'production', WORKSPACE_API_URL: base + '/', WORKSPACE_INTERNAL_TOKEN: TOKEN }); });
test.afterEach(() => { for (const k of ['NODE_ENV', 'WORKSPACE_API_URL', 'WORKSPACE_INTERNAL_TOKEN']) { if (saved[k] === undefined) delete process.env[k]; else process.env[k] = saved[k]; } });
const HOST = 'web-dev-cd80.up.railway.app';
const post = (body, headers = {}) => POST(new Request(`https://${HOST}/api/lab`, { method: 'POST', headers: { host: HOST, origin: `https://${HOST}`, 'content-type': 'application/json', ...headers }, body: typeof body === 'string' ? body : JSON.stringify(body) }));

test('production mystery-g start and fit work through the API bridge without leaking the answer early', async () => {
  const start = await post({ action: 'start', template: 'free_fall', mystery: true });
  assert.equal(start.status, 200); const s = await start.json();
  assert.equal(s.status, 'ok'); assert.equal(s.mode, 'mystery-g'); assert.equal(s.source, 'simulated');
  for (const key of ['private', 'seed', 'gravity_m_s2', 'browserSimulation']) assert.equal(JSON.stringify(s).includes(`"${key}"`), false, key);
  const fit = await (await post({ action: 'fit', sessionId: s.sessionId })).json();
  assert.equal(fit.status, 'ok'); assert.equal(fit.fit.status, 'ok'); assert.ok(Number.isFinite(fit.reveal.gravity)); assert.equal(fit.reveal.unit, 'm/s^2');
});

test('production normal trial returns the validated browser setup', async () => {
  const s = await (await post({ action: 'start', template: 'projectile', mystery: false })).json();
  assert.equal(s.status, 'ok'); assert.equal(s.mode, 'normal'); assert.equal(s.browserSimulation.mode, 'normal');
});

test('missing API configuration gives a friendly retry message, not a raw code only', async () => {
  delete process.env.WORKSPACE_API_URL;
  const body = await (await post({ action: 'start', template: 'free_fall', mystery: false })).json();
  assert.equal(body.error.code, 'lab_request_failed'); assert.match(body.error.message, /try again/i);
});

test('wrong internal token fails closed with a friendly message', async () => {
  process.env.WORKSPACE_INTERNAL_TOKEN = 'wrong';
  const body = await (await post({ action: 'start', template: 'free_fall', mystery: false })).json();
  assert.equal(body.status, 'error'); assert.match(body.error.message, /try again/i);
});

test('production guards: cross-origin, schema, unknown template, oversize, bad JSON', async () => {
  const before = calls;
  const cross = await post({ action: 'start', template: 'free_fall', mystery: false }, { origin: 'https://evil.example' });
  assert.equal(cross.status, 403); assert.ok((await cross.json()).error.message);
  for (const bad of [{ action: 'start', template: 'free_fall', mystery: false, path: '/etc/passwd' }, { action: 'start', template: 'orbit', mystery: false }, { action: 'start', template: 'ramp', mystery: true }, { action: 'fit', sessionId: 'nope' }, { action: 'shell' }]) {
    const body = await (await post(bad)).json(); assert.equal(body.status, 'error'); assert.ok(body.error.message && !/^[a-z_]+$/.test(body.error.message));
  }
  assert.equal((await post('x'.repeat(1_000_001))).status, 413);
  assert.equal((await post('{nope')).status, 400);
  assert.equal(calls, before, 'rejected requests must never reach the API bridge');
});
