import test, { after } from 'node:test';
import assert from 'node:assert/strict';
import { registerHooks } from 'node:module';
import { fixtureSceneId } from '../../Build/web/src/auth/dev-scenes.mjs';

const routeUrl = new URL('../../Build/web/src/app/api/workspace/session/route.js', import.meta.url).href;
const state = { available: true, identity: { isAuthenticated: true, userId: 'user_A' } };
globalThis.__N45_SESSION__ = state;
const source = (s) => ({ url: 'data:text/javascript,' + encodeURIComponent(s), shortCircuit: true });
const hooks = registerHooks({ resolve(s, ctx, next) {
  if (ctx.parentURL === routeUrl) {
    if (s === '@clerk/nextjs/server') return source('export async function auth(o) { const s=globalThis.__N45_SESSION__; s.options=o; if(s.error) throw Error("private auth detail"); return s.identity; }');
    if (s === '../../../../auth/server-config') return source('export const getClerkConfiguration=()=>({available:globalThis.__N45_SESSION__.available});');
  }
  return next(s, ctx);
} });
const { GET } = await import(routeUrl);
hooks.deregister();
after(() => { delete globalThis.__N45_SESSION__; });

test('F3 session key matches the workspace and changes with the verified account, never request input', async () => {
  for (const userId of ['user_A', 'user_B']) {
    state.identity = { isAuthenticated: true, userId };
    const r = await GET(new Request('https://web.example/api/workspace/session?userId=spoofed'));
    assert.equal(r.status, 200); assert.equal(r.headers.get('cache-control'), 'no-store');
    assert.deepEqual(await r.json(), { userKey: fixtureSceneId(userId) });
    assert.deepEqual(state.options, { acceptsToken: 'session_token' });
  }
});

test('F3 session lookup fails closed when signed out, unconfigured, invalid, or Clerk fails', async () => {
  for (const overrides of [{ identity: null }, { identity: { isAuthenticated: false, userId: 'user_A' } }, { identity: { isAuthenticated: true, userId: '' } }, { available: false }, { error: true }]) {
    Object.assign(state, { available: true, identity: { isAuthenticated: true, userId: 'user_A' }, error: false }, overrides);
    const r = await GET(); assert.equal(r.status, 401); assert.equal(r.headers.get('cache-control'), 'no-store');
    assert.deepEqual(await r.json(), { error: { message: 'Sign in required.' } });
  }
});
