// R-W independent probes (read-only against Build/). Run from repo root: node --test evidence/reviews/R-W/probe.test.mjs
import test from 'node:test';
import assert from 'node:assert/strict';
import { createRequire } from 'node:module';
import { authorizePrivateScene } from '../../../Build/web/src/auth/access.mjs';
import { clerkConfiguration } from '../../../Build/web/src/auth/config.mjs';
import { developmentScenesEnabled, fixtureSceneId, readDevelopmentScene } from '../../../Build/web/src/auth/dev-scenes.mjs';

const require = createRequire(new URL('../../../Build/web/package.json', import.meta.url));
const dev = { NODE_ENV: 'test' };
const meta = (env) => (id, uid) => { const s = readDevelopmentScene(id, uid, env); return s && { sceneId: s.sceneId, ownerId: s.ownerId, access: s.access }; };
const as = (userId) => async () => ({ isAuthenticated: true, userId });

test('fixture repository gate: production/unlabelled/non-dev Railway deny', () => {
  for (const [env, want] of [
    [{ NODE_ENV: 'production' }, false], [{}, false], [{ NODE_ENV: 'Development' }, false],
    [{ NODE_ENV: 'production', RAILWAY_ENVIRONMENT_NAME: 'production' }, false],
    [{ NODE_ENV: 'development', RAILWAY_ENVIRONMENT_NAME: 'production' }, false],
    [{ NODE_ENV: 'production', RAILWAY_ENVIRONMENT_NAME: 'Dev' }, false],
    [{ NODE_ENV: 'production', RAILWAY_ENVIRONMENT: 'staging' }, false],
    [{ NODE_ENV: 'production', RAILWAY_ENVIRONMENT_NAME: 'dev' }, true],
    [{ NODE_ENV: 'test' }, true]]) assert.equal(developmentScenesEnabled(env), want, JSON.stringify(env));
});

test('cross-user: B cannot open A fixture even knowing its id; same null as unknown id', async () => {
  const a = fixtureSceneId('user_A');
  const grantA = await authorizePrivateScene({ configured: true, sceneId: a, readIdentity: as('user_A'), readSceneMetadata: meta(dev) });
  assert.deepEqual({ ...grantA }, { sceneId: a, userId: 'user_A' });
  for (const id of [a, fixtureSceneId('user_C'), 'dev-fixture-' + '0'.repeat(64), '../' + a, a.toUpperCase(), a + ' '])
    assert.equal(await authorizePrivateScene({ configured: true, sceneId: id, readIdentity: as('user_B'), readSceneMetadata: meta(dev) }), null, id);
  for (const readIdentity of [async () => null, async () => ({ isAuthenticated: false, userId: 'user_A' }),
    async () => ({ isAuthenticated: true, userId: ' ' }), async () => { throw new Error('jwks'); }])
    assert.equal(await authorizePrivateScene({ configured: true, sceneId: a, readIdentity, readSceneMetadata: meta(dev) }), null);
  assert.equal(await authorizePrivateScene({ configured: false, sceneId: a, readIdentity: as('user_A'), readSceneMetadata: meta(dev) }), null);
  assert.equal(await authorizePrivateScene({ configured: true, sceneId: a, readIdentity: as('user_A'), readSceneMetadata: meta({ NODE_ENV: 'production' }) }), null);
});

test('Clerk config fails closed on malformed/mismatched synthetic keys (no real values)', () => {
  const pk = (h) => 'pk_test_' + Buffer.from(h).toString('base64');
  const ok = { NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY: pk('example.clerk.accounts.dev$'), CLERK_SECRET_KEY: 'sk_test_synthetic' };
  assert.equal(clerkConfiguration(ok).available, true);
  for (const bad of [{}, { ...ok, CLERK_SECRET_KEY: undefined }, { ...ok, CLERK_SECRET_KEY: 'sk_live_synthetic' },
    { ...ok, NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY: pk('example.clerk.accounts.dev') },
    { ...ok, NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY: pk('evil/path$') }, { ...ok, CLERK_SECRET_KEY: '' }])
    assert.equal(clerkConfiguration(bad).available, false, JSON.stringify(Object.keys(bad)));
});

test('matcher edge cases (Next testing helper)', () => {
  const { unstable_doesMiddlewareMatch: m } = require('next/experimental/testing/server');
  const config = { matcher: ['/workspace/:path*'] };
  for (const url of ['/workspace', '/workspace/', '/workspace/a/b', '/workspace/x?_rsc=1']) assert.equal(m({ config, url }), true, url);
  for (const url of ['/workspaces', '/library/workspace', '/api/workspace', '/sign-in/workspace', '/health/ready']) assert.equal(m({ config, url }), false, url);
});

