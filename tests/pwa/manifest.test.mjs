import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { manifest, validateManifest } from '../../Build/web/src/pwa/manifest.mjs';

const pub = (f) => fileURLToPath(new URL('../../Build/web/public' + f, import.meta.url));
const onDisk = JSON.parse(readFileSync(pub('/pwa/manifest.webmanifest'), 'utf8'));

test('generated manifest file equals source and validates', () => {
  assert.deepEqual(onDisk, manifest);
  assert.deepEqual(validateManifest(onDisk), []);
});

test('validator rejects bad manifests', () => {
  const bad = (patch) => validateManifest({ ...manifest, ...patch }).length > 0;
  assert.ok(bad({ orientation: 'landscape' }));
  assert.ok(bad({ display: 'weird' }));
  assert.ok(bad({ theme_color: 'blue' }));
  assert.ok(bad({ start_url: 'https://elsewhere.example/' }));
  assert.ok(bad({ icons: [{ src: 'https://cdn.example/i.png', sizes: '192x192', type: 'image/png', purpose: 'any' }] }));
  assert.ok(bad({ icons: manifest.icons.map((i) => ({ ...i, purpose: 'any maskable' })) }));
  assert.ok(bad({ icons: manifest.icons.filter((i) => i.purpose !== 'maskable') }));
});

test('manifest icons are the logo v2 brand files with the declared PNG size', () => {
  assert.deepEqual(manifest.icons.map((i) => i.src), ['/brand/mark-192.png', '/brand/mark-512.png', '/brand/icon-maskable-512.png', '/brand/mark.svg']);
  for (const i of manifest.icons) {
    assert.ok(existsSync(pub(i.src)), i.src);
    if (i.type !== 'image/png') continue;
    const buf = readFileSync(pub(i.src)), n = Number(i.sizes.split('x')[0]);
    assert.equal(buf.subarray(1, 4).toString(), 'PNG');
    assert.equal(buf.readUInt32BE(16), n); assert.equal(buf.readUInt32BE(20), n);
  }
  assert.equal(manifest.icons.find((i) => i.purpose === 'maskable').src, '/brand/icon-maskable-512.png');
});

test('provenance doc present', () => {
  const prov = readFileSync(fileURLToPath(new URL('../../Build/web/src/pwa/README.md', import.meta.url)), 'utf8');
  assert.match(prov, /Provenance/);
});
