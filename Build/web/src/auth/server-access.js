import 'server-only';
import { auth } from '@clerk/nextjs/server';
import { notFound, redirect } from 'next/navigation';
import { getClerkConfiguration } from './server-config';
import { authorizePrivateScene } from './access.mjs';
import { developmentScenesEnabled, fixtureSceneId } from './dev-scenes.mjs';
import { readSceneMetadata, readSceneForOwner } from './scene-repository';

async function readIdentity() {
  if (!getClerkConfiguration().available || !developmentScenesEnabled(process.env)) return null;
  try { return await auth({ acceptsToken: 'session_token' }); }
  catch { return null; }
}

export async function requirePrivateScene(sceneId) {
  const grant = await authorizePrivateScene({
    configured: getClerkConfiguration().available,
    sceneId,
    readIdentity,
    readSceneMetadata,
  });
  if (!grant) notFound();
  return grant;
}

export async function requireOwnFixtureSceneId() {
  const identity = await readIdentity();
  // S15bc: a verified logged-out visitor goes to sign-in; config/auth failure and other users stay uniform 404.
  if (identity && identity.isAuthenticated !== true) redirect('/sign-in');
  if (identity?.isAuthenticated !== true || !fixtureSceneId(identity.userId)) notFound();
  return fixtureSceneId(identity.userId);
}

export async function requirePrivateSceneView(sceneId) {
  const grant = await requirePrivateScene(sceneId);
  const view = readSceneForOwner(grant.sceneId, grant.userId);
  if (!view) notFound();
  return view;
}
