import 'server-only';
import { readDevelopmentScene } from './dev-scenes.mjs';

// Caller identity is derived by Clerk server auth, never supplied by an HTTP field.
export function readSceneMetadata(sceneId, userId) {
  const scene = readDevelopmentScene(sceneId, userId, process.env);
  return scene && { sceneId: scene.sceneId, ownerId: scene.ownerId, access: scene.access };
}

export function readSceneForOwner(sceneId, userId) {
  const scene = readDevelopmentScene(sceneId, userId, process.env);
  if (!scene) return null;
  const { ownerId, access, ...view } = scene;
  return view;
}
