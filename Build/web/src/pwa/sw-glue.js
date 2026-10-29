// service worker glue; appended after cache-policy.mjs by build-sw.mjs
self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(CACHE_NAME).then((c) => Promise.all(PRECACHE.map(async (url) => {
    const res = await fetch(new Request(url, { credentials: 'omit', cache: 'reload' }));
    if (isCacheableResponse(res)) await c.put(url, res); // skip, never fail install, on a non-cacheable reply
  }))));
});
self.addEventListener('activate', (e) => {
  e.waitUntil(caches.keys().then((ks) => Promise.all(ks
    .filter((k) => k.startsWith(CACHE_PREFIX) && k !== CACHE_NAME).map((k) => caches.delete(k)))));
});
// Sign-out hook: page posts {type:'CLEAR_CACHES'} to drop everything this worker stored.
self.addEventListener('message', (e) => {
  if (e.data && e.data.type === 'CLEAR_CACHES') e.waitUntil(caches.keys().then((ks) => Promise.all(
    ks.filter((k) => k.startsWith(CACHE_PREFIX)).map((k) => caches.delete(k)))));
});
self.addEventListener('fetch', (e) => {
  const req = e.request;
  if (!isCacheableRequest(req, self.location.origin)) return; // not intercepted: browser default, nothing stored
  e.respondWith((async () => {
    const cache = await caches.open(CACHE_NAME);
    const hit = await cache.match(req);
    if (hit) return hit;
    const res = await fetch(req);
    if (isCacheableResponse(res)) {
      await cache.put(req, res.clone());
      const keys = await cache.keys();
      for (const k of keys.slice(0, Math.max(0, keys.length - MAX_ENTRIES))) await cache.delete(k);
    }
    return res;
  })());
});
