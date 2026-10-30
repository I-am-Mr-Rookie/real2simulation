// node evidence/S19/check-served.mjs <baseUrl>  -> prints status/type of PWA assets and head links
const base = process.argv[2] || 'http://localhost:3919';
const out = {};
for (const p of ['/pwa/manifest.webmanifest', '/pwa/sw.js', '/pwa/icon-192.png', '/pwa/icon-512.png', '/pwa/icon-maskable-512.png', '/pwa/icon.svg']) {
  const r = await fetch(base + p);
  out[p] = { status: r.status, type: r.headers.get('content-type'), swAllowed: r.headers.get('service-worker-allowed') };
}
const html = await (await fetch(base + '/')).text();
out.head = html.match(/<(link|meta)[^>]*(manifest|theme-color|icon)[^>]*>/g);
console.log(JSON.stringify(out, null, 1));
