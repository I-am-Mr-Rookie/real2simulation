// Exercise the actual server facade/repository with a mocked Clerk transport, never a real session or auth bypass.
import assert from 'node:assert/strict';
import test, { after } from 'node:test';
import { registerHooks } from 'node:module';
import { fixtureSceneId } from '../../Build/web/src/auth/dev-scenes.mjs';

const state = { available: true, identity: null, calls: [], error: null };
globalThis.__S04I_AUTH_TEST__ = state;
const originalMode = process.env.NODE_ENV;
process.env.NODE_ENV = 'test';
after(() => {
  delete globalThis.__S04I_AUTH_TEST__;
  if (originalMode === undefined) delete process.env.NODE_ENV;
  else process.env.NODE_ENV = originalMode;
});
const facadeUrl = new URL('../../Build/web/src/auth/server-access.js', import.meta.url).href;
const source = (body) => ({ url: 'data:text/javascript,' + encodeURIComponent(body), shortCircuit: true });
const hooks = registerHooks({ resolve(specifier, context, next) {
  if (specifier === 'server-only') return source('export {};');
  if (context.parentURL === facadeUrl) {
    if (specifier === '@clerk/nextjs/server') return source(`export async function auth(options) {
      const s = globalThis.__S04I_AUTH_TEST__; s.calls.push(options);
      if (s.error) throw s.error; return s.identity;
    }`);
    if (specifier === 'next/navigation') return source(`export function notFound() {
      throw Object.assign(new Error('Not found'), { digest: 'NEXT_HTTP_ERROR_FALLBACK;404' });
    }`);
    if (specifier === './server-config') return source('export const getClerkConfiguration = () => ({ available: globalThis.__S04I_AUTH_TEST__.available });');
    if (specifier === './scene-repository') return { url: new URL('./scene-repository.js', facadeUrl).href, shortCircuit: true };
  }
  return next(specifier, context);
} });
const { requirePrivateSceneView, requireOwnFixtureSceneId } = await import(facadeUrl);
hooks.deregister();
const denied = (fn) => assert.rejects(fn, { digest: 'NEXT_HTTP_ERROR_FALLBACK;404' });

test('actual server facade returns only the owner view and derives entry ID from the verified session', async () => {
  state.identity = { isAuthenticated: true, userId: 'user_owner' };
  const sceneId = fixtureSceneId('user_owner');
  assert.equal(await requireOwnFixtureSceneId(), sceneId);
  const view = await requirePrivateSceneView(sceneId);
  assert.equal(view.sceneId, sceneId);
  assert.equal(view.state.phase, 'upload.idle');
  assert.ok(!Object.hasOwn(view, 'ownerId'));
  assert.ok(!Object.hasOwn(view, 'access'));
  assert.ok(state.calls.every((options) => options.acceptsToken === 'session_token'));
});

test('actual facade uniformly throws Next 404 for guest, other owner, unknown, malformed, config/auth failure', async () => {
  const sceneId = fixtureSceneId('user_owner');
  for (const identity of [null, {}, { isAuthenticated: false, userId: 'user_owner' },
    { isAuthenticated: true, userId: 'user_other' }]) {
    state.identity = identity;
    await denied(() => requirePrivateSceneView(sceneId));
  }
  state.identity = { isAuthenticated: true, userId: 'user_owner' };
  for (const id of ['unknown', '../private', null]) await denied(() => requirePrivateSceneView(id));
  const before = state.calls.length;
  await denied(() => requirePrivateSceneView('../private'));
  assert.equal(state.calls.length, before, 'invalid ID must deny before Clerk');
  state.available = false;
  await denied(() => requirePrivateSceneView(sceneId));
  await denied(() => requireOwnFixtureSceneId());
  assert.equal(state.calls.length, before, 'missing configuration must deny before Clerk');
  state.available = true;
  state.error = new Error('provider diagnostic must not reach response');
  await denied(() => requirePrivateSceneView(sceneId));
  await denied(() => requireOwnFixtureSceneId());
  state.error = null;
});

test('actual facade denies even the owner outside development, without reading a session', async () => {
  state.identity = { isAuthenticated: true, userId: 'user_owner' };
  const before = state.calls.length;
  process.env.NODE_ENV = 'production';
  try {
    await denied(() => requirePrivateSceneView(fixtureSceneId('user_owner')));
    await denied(() => requireOwnFixtureSceneId());
    assert.equal(state.calls.length, before);
  } finally { process.env.NODE_ENV = 'test'; }
});
