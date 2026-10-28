// Pure synthetic policy checks: no Clerk import, session or network.
import assert from 'node:assert/strict';
import { authorizePrivateScene } from '../../../../Build/web/src/auth/access.mjs';

const identity = async () => ({ isAuthenticated: true, userId: 'synthetic-owner' });
const record = (sceneId) => ({ sceneId, ownerId: 'synthetic-owner', access: 'private' });
let checks = 0;
for (const configured of ['true', 1, {}, null]) {
  assert.equal(await authorizePrivateScene({ configured, sceneId: 'scene',
    readIdentity: () => assert.fail('configuration must deny before identity'),
    readSceneMetadata: () => assert.fail('configuration must deny before repository') }), null);
  checks++;
}
for (const sceneId of ['a', 'a'.repeat(128)]) {
  assert.deepEqual(await authorizePrivateScene({ configured: true, sceneId,
    readIdentity: identity, readSceneMetadata: async () => record(sceneId) }),
  { sceneId, userId: 'synthetic-owner' });
  checks++;
}
for (const userId of ['   ', 1, {}, null]) {
  assert.equal(await authorizePrivateScene({ configured: true, sceneId: 'scene',
    readIdentity: async () => ({ isAuthenticated: true, userId }),
    readSceneMetadata: () => assert.fail('invalid identity must not access repository') }), null);
  checks++;
}
assert.equal(await authorizePrivateScene({ configured: true, sceneId: 'scene',
  readIdentity: identity, readSceneMetadata: async () => {
    const value = record('scene');
    Object.defineProperty(value, 'ownerId', { get() { throw new Error('synthetic lookup error'); } });
    return value;
  } }), null);
checks++;
console.log(JSON.stringify({ checks, status: 'PASS', liveAuth: 'NOT_RUN' }));
