// S04n BFF: Clerk-authenticated proxy to the API's private /internal/workspace/* routes (evidence/S15/S15m/PLAN.md §2).
import { auth } from '@clerk/nextjs/server';
import { getClerkConfiguration } from '../../../../auth/server-config';

const noStore = { 'cache-control': 'no-store' };
const JSON_CAP = 1_000_000;
const CHUNK_CAP = 8_388_608; // contracts/jobs/policy.json upload.chunk_bytes
const PASS_REQUEST = ['content-type', 'x-chunk-sha256'];
const fail = (status, code, message) => Response.json({ status: 'error', error: { code, message } }, { status, headers: noStore });

// Same pattern as app/api/lab/route.js readCapped, but returns bytes and takes the cap (chunks exceed the lab 1 MB cap).
async function readCapped(request, cap) {
  const declared = Number(request.headers.get('content-length'));
  if (Number.isFinite(declared) && declared > cap) throw new Error('request_too_large');
  const reader = request.body?.getReader(); if (!reader) return undefined; const chunks = []; let size = 0;
  while (true) { const part = await reader.read(); if (part.done) break; size += part.value.byteLength; if (size > cap) { reader.cancel().catch(() => {}); throw new Error('request_too_large'); } chunks.push(part.value); }
  const bytes = new Uint8Array(size); let at = 0; for (const chunk of chunks) { bytes.set(chunk, at); at += chunk.byteLength; } return bytes;
}

async function readUserId() {
  if (!getClerkConfiguration().available) return null;
  try { const identity = await auth({ acceptsToken: 'session_token' }); return identity?.isAuthenticated === true && identity.userId ? identity.userId : null; }
  catch { return null; }
}

async function proxy(request, context) {
  const userId = await readUserId();
  if (!userId) return fail(401, 'UNAUTHORIZED', 'Sign in required.');
  const base = process.env.WORKSPACE_API_URL, token = process.env.WORKSPACE_INTERNAL_TOKEN;
  if (!base || !token) return fail(503, 'DEPENDENCY_UNAVAILABLE', 'Workspace API is not configured.');
  const segments = (await context.params).path || [];
  if (!segments.length || segments.some((s) => !s || s === '.' || s === '..' || /[\\/]/.test(s))) return fail(404, 'NOT_FOUND', 'Unknown workspace route.');
  const method = request.method;
  let body;
  if (method !== 'GET') {
    try { body = await readCapped(request, method === 'PUT' && segments[0] === 'uploads' ? CHUNK_CAP : JSON_CAP); }
    catch { return fail(413, 'INVALID_INPUT', 'Request body too large.'); }
  }
  const headers = { 'x-workspace-owner': userId, 'x-workspace-token': token };
  for (const name of PASS_REQUEST) { const value = request.headers.get(name); if (value) headers[name] = value; }
  const target = base.replace(/\/+$/, '') + '/internal/workspace/' + segments.map(encodeURIComponent).join('/') + new URL(request.url).search;
  let upstream;
  try { upstream = await fetch(target, { method, headers, body, cache: 'no-store', redirect: 'manual', signal: request.signal }); }
  catch { return fail(502, 'DEPENDENCY_UNAVAILABLE', 'Workspace API unreachable.'); }
  const out = { ...noStore }; const type = upstream.headers.get('content-type'); if (type) out['content-type'] = type;
  return new Response(await upstream.arrayBuffer(), { status: upstream.status, headers: out });
}

export const dynamic = 'force-dynamic';
export const GET = proxy;
export const POST = proxy;
export const PUT = proxy;

