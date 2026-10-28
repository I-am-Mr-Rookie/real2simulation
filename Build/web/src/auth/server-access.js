import 'server-only';
import { auth } from '@clerk/nextjs/server';
import { notFound } from 'next/navigation';
import { getClerkConfiguration } from './server-config';
import { authorizePrivateScene } from './access.mjs';

// No private repository is connected yet. Intentionally no client-injected loader,
// default owner, public-fixture lookup or environment switch to bypass ownership.
const readSceneMetadata = undefined;

export async function requirePrivateScene(sceneId) {
  const grant = await authorizePrivateScene({
    configured: getClerkConfiguration().available,
    sceneId,
    readIdentity: () => auth({ acceptsToken: 'session_token' }),
    readSceneMetadata,
  });
  if (!grant) notFound();
  return grant;
}
