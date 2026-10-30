// S21f: parse/transform About.jsx with the installed Next SWC (no new deps). argv: <Build/web dir> <file>
const path = require('path'), fs = require('fs');
const swc = require(path.join(process.argv[2], 'node_modules/next/dist/build/swc'));
(async () => {
  await swc.loadBindings();
  const file = process.argv[3];
  const o = await swc.transform(fs.readFileSync(file, 'utf8'), { filename: file,
    jsc: { parser: { syntax: 'ecmascript', jsx: true }, transform: { react: { runtime: 'automatic' } } } });
  console.log('OK', o.code.length);
})().catch((e) => { console.error('FAIL', e.message || e); process.exit(1); });
