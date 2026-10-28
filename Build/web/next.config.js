const path = require('node:path');

module.exports = {
  // The local lab imports the existing simulator beside the web application.
  turbopack: { root: path.join(__dirname, '..') },
};
