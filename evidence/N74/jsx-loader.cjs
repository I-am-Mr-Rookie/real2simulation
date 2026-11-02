const swc = require('../../Build/web/node_modules/next/dist/build/swc');
module.exports = function(source) { const done = this.async(); swc.loadBindings().then(()=>swc.transform(source, { filename: this.resourcePath, jsc:{parser:{syntax:'ecmascript',jsx:true},transform:{react:{runtime:'automatic'}}}, module:{type:'es6'} })).then(r=>done(null,r.code),done); };
