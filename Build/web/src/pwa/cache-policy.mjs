// Cache policy for the service worker (S19b). Pure functions; public/pwa/sw.js is
// generated from this file (build-sw.mjs), so tests exercise the shipped logic.
// Design: ALLOWLIST, not blocklist. Anything not listed is never intercepted or cached,
// so private uploads, authenticated pages, /api/* and cross-origin responses stay out.
export const CACHE_PREFIX = 'r2s-static-';
export const CACHE_VERSION = 'v1';
export const CACHE_NAME = CACHE_PREFIX + CACHE_VERSION;
export const MAX_ENTRIES = 100; // shortcut: FIFO trim by insertion order, no LRU; upgrade if hit-rate matters.

// Public, non-personalised static files only.
export const PRECACHE = [
  '/pwa/manifest.webmanifest', '/pwa/icon.svg',
  '/pwa/icon-192.png', '/pwa/icon-512.png', '/pwa/icon-maskable-512.png',
];
const STATIC_PREFIXES = ['/_next/static/']; // content-hashed build output
const STATIC_EXACT = new Set(PRECACHE);
const VARY_DENY = /(^|[\s,])(\*|cookie|authorization)([\s,]|$)/i;
const CC_DENY = /(no-store|private|no-cache)/i;

// Request side: may the service worker handle (and later store) this request at all?
export function isCacheableRequest(request, origin) {
  if (request.method !== 'GET') return false;
  if (request.headers && request.headers.has('authorization')) return false;
  if (request.headers && request.headers.has('range')) return false;
  if (request.mode === 'navigate') return false; // HTML may be personalised
  let u;
  try { u = new URL(request.url); } catch { return false; }
  if (u.origin !== origin) return false;
  if (u.username || u.password) return false;
  if (STATIC_EXACT.has(u.pathname)) return !u.search;
  return STATIC_PREFIXES.some((p) => u.pathname.startsWith(p) && u.pathname.length > p.length);
}

// Response side: may this response be stored? Fails closed on missing/odd headers.
export function isCacheableResponse(response) {
  if (!response || response.status !== 200 || response.type !== 'basic' || response.redirected) return false;
  const h = response.headers;
  if (h.has('set-cookie') || h.has('content-range') || h.has('www-authenticate')) return false;
  if (CC_DENY.test(h.get('cache-control') || '')) return false;
  if (VARY_DENY.test(h.get('vary') || '')) return false;
  return true;
}
