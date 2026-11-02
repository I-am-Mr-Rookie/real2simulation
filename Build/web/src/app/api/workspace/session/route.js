import { auth } from '@clerk/nextjs/server';
import { getClerkConfiguration } from '../../../../auth/server-config';
import { fixtureSceneId } from '../../../../auth/dev-scenes.mjs';

export const dynamic = 'force-dynamic';

// Same verified account key used by /workspace; never infer it from another account's localStorage keys.
export async function GET() {
  let identity;
  try { if (getClerkConfiguration().available) identity = await auth({ acceptsToken: 'session_token' }); } catch {}
  const userKey = identity?.isAuthenticated === true ? fixtureSceneId(identity.userId) : null;
  return Response.json(userKey ? { userKey } : { error: { message: 'Sign in required.' } },
    { status: userKey ? 200 : 401, headers: { 'cache-control': 'no-store' } });
}
