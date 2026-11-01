// S04n BFF: Clerk-authenticated proxy to the API's private /internal/workspace/* routes (evidence/S15/S15m/PLAN.md §2).
import { auth } from '@clerk/nextjs/server';
import { getClerkConfiguration } from '../../../../auth/server-config';

const noStore = { 'cache-control': 'no-store' };
const JSON_CAP = 1_000_000;
const CHUNK_CAP = 8_388_608; // contracts/jobs/policy.json upload.chunk_bytes
const FILE_CAP = 200 * 1024 * 1024 + 1_048_576; // N03: 200 MB file + multipart overhead; the API enforces exact limits
const AUDIO_CAP = 4 * 1024 * 1024; // N05 transcribe: 4 MB WAV
const PASS_REQUEST = ['content-type', 'x-chunk-sha256', 'range'];
const PASS_RESPONSE = ['content-type', 'content-length', 'content-range', 'accept-ranges', 'content-disposition'];
const fail = (status, code, message) => Response.json({ status: 'error', error: { code, message } }, { status, headers: noStore });

// Same pattern as app/api/lab/route.js readCapped, but returns bytes and takes the cap (chunks exceed the lab 1 MB cap).
async function readCapped(request, cap) {
  const declared = Number(request.headers.get('content-length'));
  if (Number.isFinite(declared) && declared > cap) throw new Error('request_too_large');
  const reader = request.body?.getReader(); if (!reader) return undefined; const chunks = []; let size = 0;
  while (true) { const part = await reader.read(); if (part.done) break; size += part.value.byteLength; if (size > cap) { reader.cancel().catch(() => {}); throw new Error('request_too_large'); } chunks.push(part.value); }
  const bytes = new Uint8Array(size); let at = 0; for (const chunk of chunks) { bytes.set(chunk, at); at += chunk.byteLength; } return bytes;
}

// N03 multipart file upload: stream to the API instead of buffering up to 200 MB in the web process.
function streamCapped(request, cap) {
  const declared = Number(request.headers.get('content-length'));
  if (Number.isFinite(declared) && declared > cap) throw new Error('request_too_large');
  let size = 0;
  return request.body?.pipeThrough(new TransformStream({ transform(chunk, c) { size += chunk.byteLength; if (size > cap) c.error(new Error('request_too_large')); else c.enqueue(chunk); } }));
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
  let body; const fileUpload = method === 'POST' && segments.length === 1 && segments[0] === 'files';
  if (method !== 'GET' && method !== 'DELETE') {
    const cap = method === 'PUT' && segments[0] === 'uploads' ? CHUNK_CAP : segments.join('/') === 'agent/transcribe' ? AUDIO_CAP : JSON_CAP;
    try { body = fileUpload ? streamCapped(request, FILE_CAP) : await readCapped(request, cap); }
    catch { return fail(413, 'INVALID_INPUT', 'Request body too large.'); }
  }
  const headers = { 'x-workspace-owner': userId, 'x-workspace-token': token };
  for (const name of PASS_REQUEST) { const value = request.headers.get(name); if (value) headers[name] = value; }
  const probe = method === 'GET' && segments.length === 1 && segments[0] === 'health'; // S15ay: reachability probe; upstream 404 stays server-side
  // N09: the N05 agent router is mounted at /workspace/agent (not under /internal/workspace); same owner token gate.
  const prefix = segments[0] === 'agent' ? '/workspace/' : '/internal/workspace/';
  const target = base.replace(/\/+$/, '') + prefix + (probe ? 'jobs/health-probe' : segments.map(encodeURIComponent).join('/') + new URL(request.url).search);
  let upstream;
  try { upstream = await fetch(target, { method, headers, body, cache: 'no-store', redirect: 'manual', signal: request.signal, ...(fileUpload && body ? { duplex: 'half' } : {}) }); }
  catch { return fail(502, 'DEPENDENCY_UNAVAILABLE', 'Workspace API unreachable.'); }
  if (probe) return upstream.status < 500 && upstream.status !== 401 && upstream.status !== 403 ? Response.json({ status: 'ok' }, { headers: noStore }) : fail(502, 'DEPENDENCY_UNAVAILABLE', 'Workspace API unavailable.');
  const out = { ...noStore }; for (const name of PASS_RESPONSE) { const value = upstream.headers.get(name); if (value) out[name] = value; }
  return new Response(upstream.body, { status: upstream.status, headers: out }); // streamed: file downloads can be 200 MB
}

export const dynamic = 'force-dynamic';
export const GET = proxy;
export const POST = proxy;
export const PUT = proxy;
export const DELETE = proxy;

