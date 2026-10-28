// Pure policy. Both callbacks must be supplied by trusted server code, never HTTP input.
// Authorize metadata first; do not load assets/jobs/scene payloads before this check.
export async function authorizePrivateScene({ configured, sceneId, readIdentity, readSceneMetadata }) {
  if (configured !== true || typeof sceneId !== 'string'
      || !/^[A-Za-z0-9_-]{1,128}$/.test(sceneId)
      || typeof readIdentity !== 'function' || typeof readSceneMetadata !== 'function') return null;
  try {
    const identity = await readIdentity();
    if (identity?.isAuthenticated !== true || typeof identity.userId !== 'string'
        || !identity.userId.trim()) return null;
    const metadata = await readSceneMetadata(sceneId, identity.userId);
    if (metadata?.sceneId !== sceneId || metadata.ownerId !== identity.userId
        || metadata.access !== 'private') return null;
    return Object.freeze({ sceneId, userId: identity.userId });
  } catch {
    // Uniform denial; never return provider/storage diagnostics to a caller.
    return null;
  }
}
