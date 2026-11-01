// N03: BFF route passes multipart uploads (streamed), Range, 206 headers and DELETE for /files. Mocked Clerk + upstream; no network.
import assert from 'node:assert/strict';
import test, { after, beforeEach } from 'node:test';
import { registerHooks } from 'node:module';

const state = { identity: null, calls: [], reply: null };
globalThis.__N03_TEST__ = state;
const routeUrl = new URL('../../Build/web/src/app/api/workspace/[...path]/route.js', import.meta.url).href;
const source = (body) => ({ url: 'data:text/javascript,' + encodeURIComponent(body), shortCircuit: true });
const hooks = registerHooks({ resolve(specifier, context, next) {
  if (context.parentURL && decodeURI(context.parentURL) === decodeURI(routeUrl)) {
    if (specifier === '@clerk/nextjs/server') return source('export async function auth() { return globalThis.__N03_TEST__.identity; }');
    if (specifier === '../../../../auth/server-config') return source('export const getClerkConfiguration = () => ({ available: true });');
  }
  return next(specifier, context);
} });
const route = await import(routeUrl);
hooks.deregister();

const realFetch = globalThis.fetch;
const env = { WORKSPACE_API_URL: process.env.WORKSPACE_API_URL, WORKSPACE_INTERNAL_TOKEN: process.env.WORKSPACE_INTERNAL_TOKEN };
after(() => { globalThis.fetch = realFetch; delete globalThis.__N03_TEST__; for (const [k, v] of Object.entries(env)) { if (v === undefined) delete process.env[k]; else process.env[k] = v; } });
beforeEach(() => {
  state.identity = { isAuthenticated: true, userId: 'user_owner' }; state.calls = [];
  process.env.WORKSPACE_API_URL = 'http://api'; process.env.WORKSPACE_INTERNAL_TOKEN = 'test-token';
  globalThis.fetch = async (url, init) => { const sent = init.body ? new Uint8Array(await new Response(init.body).arrayBuffer()) : undefined; state.calls.push({ url, init, sent }); return state.reply(); };
  state.reply = () => new Response('{"ok":true}', { status: 201, headers: { 'content-type': 'application/json' } });
});
const ctx = (...path) => ({ params: Promise.resolve({ path }) });
const req = (url, init = {}) => new Request('https://web.example' + url, init);

test('multipart upload above the 1 MB JSON cap streams through with its boundary content-type', async () => {
  const form = new FormData(); form.append('file', new Blob([new Uint8Array(3_000_000).fill(7)]), 'clip.mp4');
  const request = req('/api/workspace/files', { method: 'POST', body: form });
  const expected = new Uint8Array(await request.clone().arrayBuffer());
  const res = await route.POST(request, ctx('files'));
  assert.equal(res.status, 201);
  const [{ url, init, sent }] = state.calls;
  assert.equal(url, 'http://api/internal/workspace/files'); assert.equal(init.duplex, 'half');
  assert.match(init.headers['content-type'], /^multipart\/form-data; boundary=/);
  assert.deepEqual(sent, expected);
});

test('declared upload above 201 MB -> 413 before any upstream call', async () => {
  const res = await route.POST(req('/api/workspace/files', { method: 'POST', body: 'x', headers: { 'content-length': String(202 * 1024 * 1024) } }), ctx('files'));
  assert.equal(res.status, 413); assert.equal(state.calls.length, 0);
});

test('Range is forwarded and 206 range headers come back; DELETE is forwarded', async () => {
  state.reply = () => new Response('abcd', { status: 206, headers: { 'content-type': 'video/mp4', 'content-range': 'bytes 0-3/10', 'accept-ranges': 'bytes', 'content-disposition': 'inline; filename="clip.mp4"', 'set-cookie': 'x=1' } });
  const res = await route.GET(req('/api/workspace/files/f1/content', { headers: { range: 'bytes=0-3' } }), ctx('files', 'f1', 'content'));
  assert.equal(res.status, 206); assert.equal(await res.text(), 'abcd');
  assert.equal(state.calls[0].init.headers.range, 'bytes=0-3');
  assert.equal(res.headers.get('content-range'), 'bytes 0-3/10'); assert.equal(res.headers.get('accept-ranges'), 'bytes');
  assert.equal(res.headers.get('content-disposition'), 'inline; filename="clip.mp4"'); assert.equal(res.headers.get('set-cookie'), null);
  state.reply = () => Response.json({ deleted: 'f1' });
  const del = await route.DELETE(req('/api/workspace/files/f1', { method: 'DELETE' }), ctx('files', 'f1'));
  assert.equal(del.status, 200); assert.equal(state.calls[1].init.method, 'DELETE'); assert.equal(state.calls[1].init.body, undefined);
});
