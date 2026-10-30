// Diagnostics only for synthetic-key smoke: no headers, query strings, tokens, or request changes.
const { subscribe } = require('node:diagnostics_channel');
let traced = false;
subscribe('undici:request:create', ({ request }) => {
  process.stdout.write('S04I_OUTBOUND_HOST ' + new URL(request.origin).hostname + '\n');
});
subscribe('http.client.request.start', ({ request }) => {
  process.stdout.write('S04I_HTTP_HOST ' + request.host + ' PATH ' + String(request.path).split('?')[0] + '\n');
  if (!traced) { traced = true; process.stdout.write(new Error('S04I_FIRST_HTTP_STACK').stack + '\n'); }
});
