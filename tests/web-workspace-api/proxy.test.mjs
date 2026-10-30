// S04n: exercise the actual BFF route with a mocked Clerk transport and mocked upstream fetch (no network, no secrets).
import assert from 'node:assert/strict';
import test, { after, beforeEach } from 'node:test';
import { registerHooks } from 'node:module';

const state = { available: true, identity: null, calls: [] };
globalThis.__S04N_TEST__ = state;
const routeUrl = new URL('../../Build/web/src/app/api/workspace/[...path]/route.js', import.meta.url).href;
const source = (body) => ({ url: 'data:text/javascript,' + encodeURIComponent(body), shortCircuit: true });
const hooks = registerHooks({ resolve(specifier, context, next) {
  if (context.parentURL && decodeURI(context.parentURL) === decodeURI(routeUrl)) { // loader may percent-encode the [...path] brackets
    if (specifier === '@clerk/nextjs/server') return source('export async function auth(o) { return globalThis.__S04N_TEST__.identity; }');
    if (specifier === '../../../../auth/server-config') return source('export const getClerkConfiguration = () => ({ available: globalThis.__S04N_TEST__.available });');
  }
  return next(specifier, context);
} });
const route = await import(routeUrl);
hooks.deregister();

const realFetch = globalThis.fetch;
const env = { WORKSPACE_API_URL: process.env.WORKSPACE_API_URL, WORKSPACE_INTERNAL_TOKEN: process.env.WORKSPACE_INTERNAL_TOKEN };
after(() => { globalThis.fetch = realFetch; delete globalThis.__S04N_TEST__; for (const [k, v] of Object.entries(env)) { if (v === undefined) delete process.env[k]; else process.env[k] = v; } });
beforeEach(() => {
  state.available = true; state.identity = { isAuthenticated: true, userId: 'user_owner' }; state.calls = [];
  process.env.WORKSPACE_API_URL = 'http://api.railway.internal:8000/'; process.env.WORKSPACE_INTERNAL_TOKEN = 'test-token';
  globalThis.fetch = async (url, init) => { state.calls.push({ url, init }); return new Response('{"ok":true}', { status: 201, headers: { 'content-type': 'application/json', 'set-cookie': 'x=1' } }); };
});
const ctx = (...path) => ({ params: Promise.resolve({ path }) });
const req = (url, init = {}) => new Request('https://web.example' + url, init);

test('signed out or Clerk unavailable -> 401 and no upstream call', async () => {
  state.identity = { isAuthenticated: false, userId: null };
  let res = await route.POST(req('/api/workspace/jobs', { method: 'POST', body: '{}' }), ctx('jobs'));
  assert.equal(res.status, 401); assert.equal((await res.json()).error.code, 'UNAUTHORIZED');
  state.identity = { isAuthenticated: true, userId: 'user_owner' }; state.available = false;
  res = await route.GET(req('/api/workspace/jobs/j1/progress'), ctx('jobs', 'j1', 'progress'));
  assert.equal(res.status, 401); assert.equal(state.calls.length, 0);
});

test('forwards only owner/token/content headers, never cookies; no-store; query kept', async () => {
  const res = await route.POST(req('/api/workspace/scenes/s1/spec?x=1', { method: 'POST', body: '{"answers":{}}',
    headers: { 'content-type': 'application/json', cookie: '__session=secret', authorization: 'Bearer abc', 'x-workspace-owner': 'user_evil' } }), ctx('scenes', 's1', 'spec'));
  assert.equal(res.status, 201); assert.equal(res.headers.get('cache-control'), 'no-store'); assert.equal(res.headers.get('set-cookie'), null);
  assert.deepEqual(await res.json(), { ok: true });
  const [{ url, init }] = state.calls;
  assert.equal(url, 'http://api.railway.internal:8000/internal/workspace/scenes/s1/spec?x=1');
  assert.deepEqual(init.headers, { 'x-workspace-owner': 'user_owner', 'x-workspace-token': 'test-token', 'content-type': 'application/json' });
  assert.equal(init.method, 'POST'); assert.equal(new TextDecoder().decode(init.body), '{"answers":{}}');
});

test('chunk PUT allows 8 MiB with chunk sha header; above -> 413; JSON above 1 MB -> 413', async () => {
  const chunk = new Uint8Array(8_388_608);
  let res = await route.PUT(req('/api/workspace/uploads/u1?offset=0', { method: 'PUT', body: chunk, headers: { 'x-chunk-sha256': 'ab' } }), ctx('uploads', 'u1'));
  assert.equal(res.status, 201); assert.equal(state.calls[0].init.body.byteLength, 8_388_608); assert.equal(state.calls[0].init.headers['x-chunk-sha256'], 'ab');
  assert.match(state.calls[0].url, /\/uploads\/u1\?offset=0$/);
  res = await route.PUT(req('/api/workspace/uploads/u1?offset=0', { method: 'PUT', body: new Uint8Array(8_388_609) }), ctx('uploads', 'u1'));
  assert.equal(res.status, 413); assert.equal((await res.json()).error.code, 'INVALID_INPUT');
  res = await route.POST(req('/api/workspace/fit', { method: 'POST', body: new Uint8Array(1_000_001) }), ctx('fit'));
  assert.equal(res.status, 413); assert.equal(state.calls.length, 1);
});

test('missing WORKSPACE_API_URL or token -> 503 DEPENDENCY_UNAVAILABLE; unreachable -> 502', async () => {
  delete process.env.WORKSPACE_API_URL;
  let res = await route.GET(req('/api/workspace/jobs/j1/progress'), ctx('jobs', 'j1', 'progress'));
  assert.equal(res.status, 503); assert.equal((await res.json()).error.code, 'DEPENDENCY_UNAVAILABLE');
  process.env.WORKSPACE_API_URL = 'http://api'; delete process.env.WORKSPACE_INTERNAL_TOKEN;
  res = await route.GET(req('/api/workspace/jobs/j1/progress'), ctx('jobs', 'j1', 'progress'));
  assert.equal(res.status, 503); assert.equal(state.calls.length, 0);
  process.env.WORKSPACE_INTERNAL_TOKEN = 't'; globalThis.fetch = async () => { throw new TypeError('fetch failed'); };
  res = await route.GET(req('/api/workspace/jobs/j1/progress'), ctx('jobs', 'j1', 'progress'));
  assert.equal(res.status, 502); assert.equal((await res.json()).error.code, 'DEPENDENCY_UNAVAILABLE');
});

test('path traversal segments rejected before forwarding', async () => {
  const res = await route.GET(req('/api/workspace/x'), ctx('..', 'admin'));
  assert.equal(res.status, 404); assert.equal(state.calls.length, 0);
});

