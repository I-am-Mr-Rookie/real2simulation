const path = require('node:path');

module.exports = {
  // The local lab imports the existing simulator beside the web application.
  turbopack: { root: path.join(__dirname, '..') },
  // Lets the /pwa/sw.js worker control the whole origin.
  async headers() {
    return [{ source: '/pwa/sw.js', headers: [{ key: 'Service-Worker-Allowed', value: '/' }, { key: 'Cache-Control', value: 'no-cache' }] }];
  },
};
