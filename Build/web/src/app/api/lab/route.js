import { handleLab } from '../../../../../lab/session-service.mjs';
const local = (value) => /^(localhost|127\.0\.0\.1|\[::1\]|::1)(:\d+)?$/.test(String(value || ''));
const noStore = { 'cache-control': 'no-store' };
// Users see these sentences (LabClient prefers error.message over code); never a raw code.
const RETRY = 'The simulated lab could not finish this step. Please try again.';
const FRIENDLY = {
  session_not_found_or_expired: 'This trial expired. Run a new trial and try again.',
  session_expired_during_fit: 'This trial expired. Run a new trial and try again.',
  request_too_large: 'That request was too large. Reload the page and try again.',
  invalid_json: 'The lab could not read that request. Reload the page and try again.',
};
function friendly(body) {
  for (const error of [body?.error, body?.fit?.error]) if (error?.code && !error.message) error.message = FRIENDLY[error.code] || RETRY;
  return body;
}
const reply = (body, status = 200) => Response.json(friendly(body), { status, headers: noStore });
async function readCapped(request) {
  const declared = Number(request.headers.get('content-length'));
  if (Number.isFinite(declared) && declared > 1_000_000) throw new Error('request_too_large');
  const reader = request.body?.getReader(); if (!reader) return request.text(); const chunks = []; let size = 0;
  while (true) { const part = await reader.read(); if (part.done) break; size += part.value.byteLength; if (size > 1_000_000) throw new Error('request_too_large'); chunks.push(part.value); }
  const bytes = new Uint8Array(size); let at = 0; for (const chunk of chunks) { bytes.set(chunk, at); at += chunk.byteLength; } return new TextDecoder().decode(bytes);
}
export async function POST(request) {
  // Production (deployed DEV) proxies to the API bridge; development/test keep the localhost-only Python bridge.
  const production = process.env.NODE_ENV === 'production';
  if (!production && !['development', 'test'].includes(process.env.NODE_ENV)) return reply({ status: 'error', error: { code: 'local_lab_disabled' } }, 403);
  const host = (production && request.headers.get('x-forwarded-host')) || request.headers.get('host'), origin = request.headers.get('origin');
  if ((!production && !local(host)) || (origin && (() => { try { return new URL(origin).host !== host; } catch { return true; } })())) return reply({ status: 'error', error: { code: 'local_origin_required' } }, 403);
  try { return reply(await handleLab(JSON.parse(await readCapped(request)), { signal: request.signal })); }
  catch (e) { const tooLarge = e.message === 'request_too_large'; return reply({ status: 'error', error: { code: tooLarge ? 'request_too_large' : 'invalid_json' } }, tooLarge ? 413 : 400); }
}
