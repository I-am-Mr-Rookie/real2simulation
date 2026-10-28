import { handleLab } from '../../../../../lab/session-service.mjs';
const local = (value) => /^(localhost|127\.0\.0\.1|\[::1\]|::1)(:\d+)?$/.test(String(value || ''));
const noStore = { 'cache-control': 'no-store' };
async function readCapped(request) {
  const declared = Number(request.headers.get('content-length'));
  if (Number.isFinite(declared) && declared > 1_000_000) throw new Error('request_too_large');
  const reader = request.body?.getReader(); if (!reader) return request.text(); const chunks = []; let size = 0;
  while (true) { const part = await reader.read(); if (part.done) break; size += part.value.byteLength; if (size > 1_000_000) throw new Error('request_too_large'); chunks.push(part.value); }
  const bytes = new Uint8Array(size); let at = 0; for (const chunk of chunks) { bytes.set(chunk, at); at += chunk.byteLength; } return new TextDecoder().decode(bytes);
}
export async function POST(request) {
  if (!['development', 'test'].includes(process.env.NODE_ENV)) return Response.json({ status: 'error', error: { code: 'local_lab_disabled' } }, { status: 403, headers: noStore });
  const host = request.headers.get('host'), origin = request.headers.get('origin');
  if (!local(host) || (origin && (() => { try { return new URL(origin).host !== host; } catch { return true; } })())) return Response.json({ status: 'error', error: { code: 'local_origin_required' } }, { status: 403, headers: noStore });
  try { return Response.json(await handleLab(JSON.parse(await readCapped(request)), { signal: request.signal }), { headers: noStore }); }
  catch (e) { const tooLarge = e.message === 'request_too_large'; return Response.json({ status: 'error', error: { code: tooLarge ? 'request_too_large' : 'invalid_json' } }, { status: tooLarge ? 413 : 400, headers: noStore }); }
}
