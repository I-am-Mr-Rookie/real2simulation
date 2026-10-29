// Executes the GENERATED public/pwa/sw.js in a vm with fake caches/fetch and proves the
// worker never intercepts or stores private/authenticated/API/upload responses.
import test from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { buildSw } from '../../Build/web/src/pwa/build-sw.mjs';
import { PRECACHE, MAX_ENTRIES, CACHE_NAME } from '../../Build/web/src/pwa/cache-policy.mjs';

const ORIGIN = 'https://app.example';
const swPath = fileURLToPath(new URL('../../Build/web/public/pwa/sw.js', import.meta.url));
const abs = (u) => new URL(u, ORIGIN).href;

const res = ({ status = 200, type = 'basic', redirected = false, headers = {}, body = 'x' } = {}) =>
  ({ status, type, redirected, body, headers: new Headers(headers), clone() { return { ...this }; } });
const req = (url, { method = 'GET', mode = 'no-cors', headers = {} } = {}) =>
  ({ method, mode, url: abs(url), headers: new Headers(headers) });

function harness(routes = {}) {
  const store = new Map(); // cacheName -> Map(url -> response)
  const fetched = [];
  const handlers = {};
  const open = (n) => { if (!store.has(n)) store.set(n, new Map()); return store.get(n); };
  const key = (r) => (typeof r === 'string' ? abs(r) : r.url);
  const caches = {
    open: async (n) => { const m = open(n); return {
      match: async (r) => m.get(key(r)), put: async (r, v) => { m.set(key(r), v); },
      keys: async () => [...m.keys()].map((url) => ({ url })), delete: async (r) => m.delete(key(r)) }; },
    keys: async () => [...store.keys()], delete: async (n) => store.delete(n),
  };
  const fetchFn = async (r) => { const u = typeof r === 'string' ? abs(r) : r.url; fetched.push(u);
    return (routes[new URL(u).pathname] || (() => res()))(); };
  const self = { location: { origin: ORIGIN }, addEventListener: (t, h) => { handlers[t] = h; } };
  vm.runInNewContext(readFileSync(swPath, 'utf8'), { self, caches, fetch: fetchFn, URL, Headers,
    Request: class { constructor(u, o) { this.url = abs(u); Object.assign(this, o); } }, Promise });
  const fire = async (type, ev) => { const p = []; handlers[type]({ ...ev, waitUntil: (x) => p.push(x) }); await Promise.all(p); };
  const fetchEv = async (r) => {
    const p = []; let responded = false, out;
    handlers.fetch({ request: r, respondWith: (x) => { responded = true; out = x; p.push(x); }, waitUntil: (x) => p.push(x) });
    await Promise.all(p); return { responded, out: responded ? await out : undefined }; };
  return { store, fetched, caches, fire, fetchEv, open, handlers };
}
const stored = (h) => [...h.store.values()].flatMap((m) => [...m.keys()]);

test('committed sw.js is up to date with its sources', () => {
  assert.equal(readFileSync(swPath, 'utf8'), buildSw());
});

test('install precaches only public static files, skips non-cacheable replies', async () => {
  const h = harness({ '/pwa/icon.svg': () => res({ headers: { 'cache-control': 'no-store' } }) });
  await h.fire('install', {});
  assert.deepEqual(stored(h).sort(), PRECACHE.filter((p) => p !== '/pwa/icon.svg').map(abs).sort());
});

const NEVER = {
  'API GET': req('/api/lab'),
  'API POST': req('/api/lab', { method: 'POST' }),
  'API under static prefix via dot-segments': req('/_next/static/../../api/lab'),
  'encoded dot-segments': req('/_next/static/%2e%2e/api/lab'),
  'private workspace page': req('/workspace/scene-1'),
  'workspace navigation': req('/workspace/scene-1', { mode: 'navigate' }),
  'public navigation': req('/library', { mode: 'navigate' }),
  'private upload video': req('/uploads/user-1/clip.mp4'),
  'signed upload url': req('/api/uploads/abc?sig=1'),
  'upload-looking path under pwa': req('/pwa/uploads/clip.mp4'),
  'authorization header on allowed path': req('/pwa/icon-192.png', { headers: { authorization: 'Bearer t' } }),
  'range request on allowed path': req('/_next/static/chunks/a.js', { headers: { range: 'bytes=0-9' } }),
  'cross-origin static path': { ...req('/x'), url: 'https://cdn.example/_next/static/a.js' },
  'credentialed url': { ...req('/x'), url: 'https://u:p@app.example/_next/static/a.js' },
  'query on pwa asset': req('/pwa/icon-192.png?user=1'),
  'unlisted pwa file': req('/pwa/sw.js'),
  'static prefix itself': req('/_next/static/'),
  'sign-in': req('/sign-in'),
  'PUT on allowed path': req('/pwa/icon-192.png', { method: 'PUT' }),
  'navigation to allowed path': req('/pwa/icon-192.png', { mode: 'navigate' }),
};
for (const [name, r] of Object.entries(NEVER)) {
  test('never intercepted/cached: ' + name, async () => {
    const h = harness();
    const out = await h.fetchEv(r);
    assert.equal(out.responded, false);
    assert.deepEqual(h.fetched, []);
    assert.deepEqual(stored(h), []);
  });
}

const BAD_RESPONSES = {
  'Cache-Control: no-store': { headers: { 'cache-control': 'no-store' } },
  'Cache-Control: private': { headers: { 'cache-control': 'max-age=60, private' } },
  'Cache-Control: no-cache': { headers: { 'cache-control': 'no-cache' } },
  'Vary: Cookie': { headers: { vary: 'Accept-Encoding, Cookie' } },
  'Vary: Authorization': { headers: { vary: 'authorization' } },
  'Vary: *': { headers: { vary: '*' } },
  'Set-Cookie': { headers: { 'set-cookie': 'sid=1' } },
  'WWW-Authenticate': { headers: { 'www-authenticate': 'Bearer' } },
  'Content-Range / 206': { status: 206, headers: { 'content-range': 'bytes 0-1/9' } },
  'redirected (e.g. to sign-in)': { redirected: true },
  'opaque (cross-origin)': { type: 'opaque' },
  '401': { status: 401 },
  '404': { status: 404 },
  '500': { status: 500 },
};
for (const [name, opts] of Object.entries(BAD_RESPONSES)) {
  test('allowed URL but response not stored: ' + name, async () => {
    const h = harness({ '/_next/static/chunks/a.js': () => res(opts) });
    const out = await h.fetchEv(req('/_next/static/chunks/a.js'));
    assert.equal(out.responded, true);
    assert.equal(out.out.status, opts.status || 200); // still returned to the page
    assert.deepEqual(stored(h), []);
  });
}

test('public hashed asset is cached once, then served from cache', async () => {
  const h = harness({ '/_next/static/chunks/a.js': () => res({ headers: { 'cache-control': 'public, max-age=31536000, immutable' } }) });
  await h.fetchEv(req('/_next/static/chunks/a.js'));
  assert.deepEqual(stored(h), [abs('/_next/static/chunks/a.js')]);
  await h.fetchEv(req('/_next/static/chunks/a.js'));
  assert.equal(h.fetched.length, 1);
});

test('cache is trimmed to MAX_ENTRIES', async () => {
  const h = harness();
  for (let i = 0; i < MAX_ENTRIES + 5; i++) await h.fetchEv(req('/_next/static/c' + i + '.js'));
  assert.equal(h.open(CACHE_NAME).size, MAX_ENTRIES);
});

test('activate drops old versions of our caches only; CLEAR_CACHES drops ours only', async () => {
  const h = harness();
  h.open('r2s-static-v0'); h.open(CACHE_NAME); h.open('other-app');
  await h.fire('activate', {});
  assert.deepEqual([...h.store.keys()].sort(), ['other-app', CACHE_NAME].sort());
  await h.fire('message', { data: { type: 'CLEAR_CACHES' } });
  assert.deepEqual([...h.store.keys()], ['other-app']);
  await h.fire('message', { data: { type: 'other' } });
  assert.deepEqual([...h.store.keys()], ['other-app']);
});
