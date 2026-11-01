// N16: public BFF for Guess the Gravity. No session: the unguessable token is the credential. Only /public/guess/<token>[/reveal]
// is reachable, so nothing else on the API is exposed through here.
const TOKEN = /^[A-Za-z0-9_-]{32}$/;
const headers = { 'cache-control': 'no-store', 'x-content-type-options': 'nosniff' };
const fail = (status, code) => Response.json({ status: 'error', error: { code } }, { status, headers });

export async function guessProxy(request, token, reveal, env = process.env, fetcher = fetch) {
  if (!TOKEN.test(token ?? '')) return fail(404, 'NOT_FOUND');
  const base = env.WORKSPACE_API_URL;
  if (!base) return fail(503, 'DEPENDENCY_UNAVAILABLE');
  let body;
  if (reveal) {
    const text = await request.text();
    if (text.length > 1000) return fail(413, 'INVALID_INPUT');
    body = text;
  }
  try {
    const up = await fetcher(base.replace(/\/+$/, '') + '/public/guess/' + token + (reveal ? '/reveal' : ''),
      { method: reveal ? 'POST' : 'GET', body, headers: reveal ? { 'content-type': 'application/json' } : {}, cache: 'no-store', redirect: 'manual' });
    return new Response(up.body, { status: up.status, headers: { ...headers, 'content-type': 'application/json' } });
  } catch { return fail(502, 'DEPENDENCY_UNAVAILABLE'); }
}
