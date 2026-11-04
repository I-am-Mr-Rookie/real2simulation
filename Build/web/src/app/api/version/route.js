// N89: judges probe /api/version on the product domain; report the web build and the API build it talks to.
export const dynamic = 'force-dynamic';

export async function GET() {
  let api = null;
  const base = process.env.WORKSPACE_API_URL;
  if (base) {
    try {
      const r = await fetch(base.replace(/\/+$/, '') + '/api/version', { cache: 'no-store', signal: AbortSignal.timeout(3000) });
      if (r.ok) api = (await r.json()).revision ?? null;
    } catch {}
  }
  return Response.json({ service: 'web', revision: process.env.RAILWAY_GIT_COMMIT_SHA ?? null, api_revision: api },
    { headers: { 'cache-control': 'no-store' } });
}
