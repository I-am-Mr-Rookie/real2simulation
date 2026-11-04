import { auth } from '@clerk/nextjs/server';
import { getClerkConfiguration } from '../../../../auth/server-config';
import { fixtureSceneId } from '../../../../auth/dev-scenes.mjs';

export const dynamic = 'force-dynamic';

// Same verified account key used by /workspace; never infer it from another account's localStorage keys.
// N89: signed out is an expected state, not an error: 200 with userKey null keeps the public editor console clean.
export async function GET() {
  let identity;
  try { if (getClerkConfiguration().available) identity = await auth({ acceptsToken: 'session_token' }); } catch {}
  const userKey = identity?.isAuthenticated === true ? fixtureSceneId(identity.userId) : null;
  return Response.json(userKey ? { userKey } : { userKey: null, error: { message: 'Sign in required.' } },
    { headers: { 'cache-control': 'no-store' } });
}
