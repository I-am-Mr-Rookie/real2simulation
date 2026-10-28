import { handleLab } from '../../../../../lab/session-service.mjs';

const local = (value) => /^(localhost|127\.0\.0\.1|\[::1\]|::1)(:\d+)?$/.test(String(value || ''));
export async function POST(request) {
  if (process.env.NODE_ENV === 'production') return Response.json({ status: 'error', error: { code: 'local_lab_disabled' } }, { status: 403 });
  const host = request.headers.get('host'), origin = request.headers.get('origin');
  if (!local(host) || (origin && !/^https?:\/\/(localhost|127\.0\.0\.1|\[::1\])(?::\d+)?$/.test(origin))) return Response.json({ status: 'error', error: { code: 'local_origin_required' } }, { status: 403 });
  try { const text = await request.text(); if (text.length > 1_000_000) return Response.json({ status: 'error', error: { code: 'request_too_large' } }, { status: 413 }); return Response.json(await handleLab(JSON.parse(text), { signal: request.signal })); }
  catch { return Response.json({ status: 'error', error: { code: 'invalid_json' } }, { status: 400 }); }
}
