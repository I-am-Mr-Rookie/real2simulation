import assert from 'node:assert/strict';
import test from 'node:test';
import { authorizePrivateScene } from './access.mjs';

const identity = async () => ({ userId: 'user_owner', isAuthenticated: true });
const record = { sceneId: 'scene-1', ownerId: 'user_owner', access: 'private' };
test('missing configuration or invalid ID denies before identity/data access', async () => {
  const unexpected = async () => { throw new Error('must not be called'); };
  for (const sceneId of ['../private', '', null, 'x/y', 'x?token=y', 'a'.repeat(129)]) {
    assert.equal(await authorizePrivateScene({ configured: true, sceneId,
      readIdentity: unexpected, readSceneMetadata: unexpected }), null);
  }
  assert.equal(await authorizePrivateScene({ configured: false, sceneId: 'scene-1',
    readIdentity: unexpected, readSceneMetadata: unexpected }), null);
});
test('unverified/missing identity cannot trigger a private metadata lookup', async () => {
  for (const value of [null, {}, { userId: 'user_owner' },
    { isAuthenticated: false, userId: 'user_owner' }, { isAuthenticated: true, userId: '' }]) {
    assert.equal(await authorizePrivateScene({ configured: true, sceneId: 'scene-1',
      readIdentity: async () => value,
      readSceneMetadata: async () => { assert.fail('unauthenticated lookup'); } }), null);
  }
});
test('only exact owner, scene ID and private access match is authorized', async () => {
  for (const metadata of [null, {}, { ...record, ownerId: 'user_other' },
    { ...record, sceneId: 'scene-2' }, { ...record, access: 'public' }]) {
    assert.equal(await authorizePrivateScene({ configured: true, sceneId: 'scene-1',
      readIdentity: identity, readSceneMetadata: async () => metadata }), null);
  }
  const result = await authorizePrivateScene({ configured: true, sceneId: 'scene-1',
    readIdentity: identity, readSceneMetadata: async (id, ownerId) => {
      assert.equal(id, 'scene-1'); assert.equal(ownerId, 'user_owner');
      return { ...record, storageRoot: 'must-not-leak' };
    } });
  assert.deepEqual(result, { sceneId: 'scene-1', userId: 'user_owner' });
  assert.ok(Object.isFrozen(result));
});
test('missing repository and identity/lookup failures deny without leaking errors', async () => {
  const fail = async () => { throw new Error('private diagnostic'); };
  const base = { configured: true, sceneId: 'scene-1', readIdentity: identity };
  let identityReads = 0;
  assert.equal(await authorizePrivateScene({ ...base,
    readIdentity: async () => { identityReads++; return identity(); } }), null);
  assert.equal(identityReads, 0, 'unavailable repository must deny before provider work');
  assert.equal(await authorizePrivateScene({ ...base, readIdentity: fail,
    readSceneMetadata: async () => record }), null);
  assert.equal(await authorizePrivateScene({ ...base, readSceneMetadata: fail }), null);
});
