import assert from 'node:assert/strict';
import { readFile, readdir, writeFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import vm from 'node:vm';

const root = fileURLToPath(new URL('../../../', import.meta.url));
const web = path.join(root, 'Build/web');
const files = [];
async function walk(dir) {
  for (const e of await readdir(dir, { withFileTypes: true })) {
    const p = path.join(dir, e.name);
    if (e.isDirectory()) await walk(p);
    else if (/\.(js|map)$/.test(e.name)) files.push(p);
  }
}
await walk(path.join(web, '.next/static'));
assert.ok(files.length > 0, 'fresh emitted browser assets required');
const forbidden = [
  'node:child_process', 'child_process', 'session-bridge.py', 'local_lab_root_not_found',
  'createMysteryGSession', 'createTrustedFitterHandoff', 'privateSetup', 'randomsecret', 'randomSecret',
  'GOOGLE_CLIENT_SECRET', 'sk_test_S04C_SYNTHETIC_SERVER_SENTINEL',
];
const required = [
  'INVALID_BROWSER_SIMULATION', 'only explicit normal mode is supported',
  'rk4-fixed-step', 'Compute in browser', 'NORMAL mode only',
];
const hits = Object.fromEntries(required.map(s => [s, []]));
const inventory = [];
const sdkNameReferences = [];
for (const f of files) {
  const body = await readFile(f, 'utf8');
  for (const marker of forbidden) assert.ok(!body.includes(marker), `${marker} leaked into ${path.relative(web, f)}`);
  assert.doesNotMatch(body, /sk_(?:test|live)_[A-Za-z0-9_-]{16,}/, 'credential-shaped browser text');
  if (body.includes('CLERK_SECRET_KEY')) {
    // SDK constants retain process.env property names, not inlined private values.
    assert.match(body, /\.env\.CLERK_SECRET_KEY/);
    sdkNameReferences.push({ file: path.relative(web, f), namesOnly: ['CLERK_SECRET_KEY', 'CLERK_MACHINE_SECRET_KEY', 'CLERK_ENCRYPTION_KEY'], owner: '@clerk/nextjs/dist/esm/server/constants.js' });
  }
  for (const marker of required) if (body.includes(marker)) hits[marker].push(path.relative(web, f));
  inventory.push({ file: path.relative(web, f), bytes: Buffer.byteLength(body), sha256: createHash('sha256').update(body).digest('hex') });
}
for (const marker of required) assert.ok(hits[marker].length, `normal browser module marker missing: ${marker}`);
const manifestPath = path.join(web, '.next/server/app/(public)/lab/page_client-reference-manifest.js');
const manifest = await readFile(manifestPath, 'utf8');
const manifestContext = {};
vm.runInNewContext(manifest, manifestContext, { timeout: 1000 });
const clientModules = manifestContext.__RSC_MANIFEST['/(public)/lab/page'].clientModules;
const labEntry = Object.entries(clientModules).find(([name]) => name.replaceAll('\\', '/').endsWith('/src/app/(public)/lab/page.jsx'));
assert.ok(labEntry, 'client lab page manifest entry');
const labChunkPaths = labEntry[1].chunks.filter(s => s.endsWith('.js'));
assert.ok(labChunkPaths.length);
for (const chunk of hits.INVALID_BROWSER_SIMULATION) assert.ok(labChunkPaths.some(s => chunk.replaceAll('\\', '/').endsWith(s)), 'normal simulation is in lab client entry chunk');
const sourceGraph = [];
async function imports(file) {
  if (sourceGraph.includes(path.relative(root, file))) return;
  sourceGraph.push(path.relative(root, file));
  assert.ok(!/session-service|mystery-g|session-bridge|server-config/.test(file));
  const body = await readFile(file, 'utf8');
  for (const m of body.matchAll(/(?:import|export)\s[^;]*?from\s*['"]([^'"]+)['"]/g)) {
    assert.ok(!m[1].startsWith('node:'), 'Node builtin in browser simulator source graph');
    if (m[1].startsWith('.')) await imports(path.resolve(path.dirname(file), m[1]));
  }
}
await imports(path.join(web, 'src/lab/browser-simulator.mjs'));
const result = {
  status: 'PASS', assetsScanned: files.length, forbiddenMarkers: forbidden,
  requiredMarkerAssets: hits, clientManifest: path.relative(web, manifestPath), labClientEntry: labEntry[0], labChunkPaths, sourceGraph, sdkNameReferences, assets: inventory,
  caveats: ['9.81 is allowed authored normal simulation data, not a secret.', 'SDK server/constants environment-variable NAMES occur in browser chunks; no values found. This is not a claim that all server-named SDK code is absent.', 'Static marker checks are not exhaustive secret detection or proof of runtime browser execution.'],
};
await writeFile(new URL('./bundle-inspection.json', import.meta.url), JSON.stringify(result, null, 2) + '\n');
console.log(`PASS ${files.length} emitted browser assets; normal RK4/UI present in manifested lab client entry; named app server/private markers absent`);
