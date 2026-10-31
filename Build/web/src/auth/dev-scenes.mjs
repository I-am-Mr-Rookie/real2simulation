import { createHash } from 'node:crypto';
import { initialState } from '../workspace/workflow.mjs';

export const FIXTURE_NOTICE = 'FIXTURE / SYNTHETIC: empty private development scene; no reconstruction, measurement or gate evidence. Uploads and live workflow services are not connected.';

export function developmentScenesEnabled(env) {
  const railway = env.RAILWAY_ENVIRONMENT_NAME || env.RAILWAY_ENVIRONMENT;
  return railway ? railway === 'dev' : ['development', 'test'].includes(env.NODE_ENV);
}

export function fixtureSceneId(userId) {
  if (typeof userId !== 'string' || !userId.trim()) return null;
  return 'dev-fixture-' + createHash('sha256').update(userId).digest('hex');
}

// shortcut: one empty, read-only fixture per verified user; replace with persistent storage before accepting real scenes.
export function readDevelopmentScene(sceneId, userId, env) {
  if (!developmentScenesEnabled(env) || !sceneId || sceneId !== fixtureSceneId(userId)) return null;
  return { sceneId, ownerId: userId, access: 'private', title: 'Private development fixture',
    notice: FIXTURE_NOTICE, state: initialState() };
}
