import assert from 'node:assert/strict';
import test from 'node:test';
import { readFile } from 'node:fs/promises';
import { authorizePrivateScene } from '../../Build/web/src/auth/access.mjs';
import { developmentScenesEnabled, fixtureSceneId, readDevelopmentScene, FIXTURE_NOTICE } from '../../Build/web/src/auth/dev-scenes.mjs';
import { createRequire } from 'node:module';
import PrivateWorkspace from '../../Build/web/src/shell/PrivateWorkspace.mjs';

const require = createRequire(new URL('../../Build/web/package.json', import.meta.url));
const React = require('react');
const { renderToStaticMarkup } = require('react-dom/server');
const env = { NODE_ENV: 'production', RAILWAY_ENVIRONMENT_NAME: 'dev' };
const owner = 'user_owner', other = 'user_other', sceneId = fixtureSceneId(owner);
const authorize = (id, identity, configured = true) => authorizePrivateScene({ configured, sceneId: id,
  readIdentity: async () => identity,
  readSceneMetadata: async (id, userId) => readDevelopmentScene(id, userId, env) });

test('only local development/test or existing Railway dev environment enables the repository', () => {
  for (const value of [{ NODE_ENV: 'development' }, { NODE_ENV: 'test' }, env,
    { NODE_ENV: 'production', RAILWAY_ENVIRONMENT: 'dev' }]) assert.equal(developmentScenesEnabled(value), true);
  for (const value of [{}, { NODE_ENV: 'production' }, { NODE_ENV: 'development', RAILWAY_ENVIRONMENT_NAME: 'judging' },
    { NODE_ENV: 'production', RAILWAY_ENVIRONMENT_NAME: 'production' }]) {
    assert.equal(developmentScenesEnabled(value), false);
    assert.equal(readDevelopmentScene(sceneId, owner, value), null);
  }
});

test('fixture identities are stable, distinct, bounded and never a client-supplied default owner', () => {
  assert.equal(fixtureSceneId(owner), sceneId);
  assert.notEqual(fixtureSceneId(other), sceneId);
  assert.match(sceneId, /^[A-Za-z0-9_-]{1,96}$/);
  for (const user of [null, undefined, {}, '', '  ']) assert.equal(fixtureSceneId(user), null);
  for (const user of [other, '', null]) assert.equal(readDevelopmentScene(sceneId, user, env), null);
  for (const id of ['', '../private', 'unknown', '__proto__', sceneId + 'x']) assert.equal(readDevelopmentScene(id, owner, env), null);
});

test('owner is granted; nonowner, unknown, invalid, guest, missing config uniformly deny', async () => {
  assert.deepEqual(await authorize(sceneId, { userId: owner, isAuthenticated: true }), { sceneId, userId: owner });
  for (const identity of [null, {}, { userId: owner }, { userId: owner, isAuthenticated: false },
    { userId: other, isAuthenticated: true }]) assert.equal(await authorize(sceneId, identity), null);
  for (const id of ['unknown', '../private', null]) assert.equal(await authorize(id, { userId: owner, isAuthenticated: true }), null);
  assert.equal(await authorize(sceneId, { userId: owner, isAuthenticated: true }, false), null);
});

test('fixture states do not persist mutations or contain fabricated artifacts/numbers', () => {
  const first = readDevelopmentScene(sceneId, owner, env);
  first.state.phase = 'report.open';
  const next = readDevelopmentScene(sceneId, owner, env);
  assert.equal(next.state.phase, 'upload.idle');
  for (const key of ['scene', 'spec', 'run', 'fit']) assert.equal(next.state[key], null);
  assert.match(next.notice, /FIXTURE.*SYNTHETIC/);
});

test('public S15 React interface mounts all workspace slots; fixture notice waits for the probe (S15bg)', () => {
  const { ownerId, access, ...scene } = readDevelopmentScene(sceneId, owner, env);
  const html = renderToStaticMarkup(React.createElement(PrivateWorkspace, { scene }));
  // S15bg: first paint (api = checking) is neutral; the fixture notice renders only once the probe reports fixture mode.
  assert.ok(!html.includes(FIXTURE_NOTICE));
  for (const slot of ['stage-nav', 'viewport', 'panel', 'job-status']) assert.ok(html.includes(`data-slot="${slot}"`));
  assert.ok(html.includes('data-phase="upload.idle"'));
  assert.ok(html.includes('Waiting for an upload'));
  assert.ok(!html.includes(owner));
  assert.ok(!html.includes('data-status="ready"'));
});

test('server-only repository and guarded leaf keep owner identity out of client composition', async () => {
  const text = async (path) => readFile(new URL('../../Build/web/src/' + path, import.meta.url), 'utf8');
  assert.ok((await text('auth/scene-repository.js')).startsWith("import 'server-only';"));
  const page = await text('app/(private)/workspace/[sceneId]/page.jsx');
  assert.ok(page.indexOf('await requirePrivateSceneView(sceneId)') < page.indexOf('<PrivateWorkspace'));
  const client = await text('shell/PrivateWorkspace.mjs');
  assert.doesNotMatch(client, /scene-repository|dev-scenes|server-access|ownerId|process\.env/);
  const proxy = await text('proxy.js');
  assert.match(proxy, /matcher: \['\/workspace\/:path\*', '\/api\/workspace\/:path\*'\]/);
  assert.doesNotMatch(proxy, /auth\.protect|redirectToSignIn/);
});

test('actual Next matcher includes only workspace, never public library or health endpoints', async () => {
  const source = await readFile(new URL('../../Build/web/src/proxy.js', import.meta.url), 'utf8');
  const matcher = JSON.parse(source.match(/matcher: (\[[^\]]+\])/)[1].replaceAll("'", '"'));
  const { unstable_doesMiddlewareMatch: matches } = require('next/experimental/testing/server');
  for (const url of ['/workspace', '/workspace/' + sceneId, '/api/workspace/x']) assert.equal(matches({ config: { matcher }, url }), true, url);
  for (const url of ['/', '/library', '/library/scene', '/health/live', '/health/ready',
    '/api/health', '/api/lab', '/sign-in', '/workspace-other', '/icon.svg']) {
    assert.equal(matches({ config: { matcher }, url }), false, url);
  }
});
