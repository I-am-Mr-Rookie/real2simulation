const path = require('node:path');

module.exports = {
  // The local lab imports the existing simulator beside the web application.
  turbopack: { root: path.join(__dirname, '..') },
  // proxy.js (Clerk) buffers request bodies; default 10 MB blocked the 200 MB upload limit (N22 finding).
  experimental: { proxyClientMaxBodySize: '201mb' },
  // Lets the /pwa/sw.js worker control the whole origin.
  async headers() {
    return [{ source: '/pwa/sw.js', headers: [{ key: 'Service-Worker-Allowed', value: '/' }, { key: 'Cache-Control', value: 'no-cache' }] }];
  },
};
