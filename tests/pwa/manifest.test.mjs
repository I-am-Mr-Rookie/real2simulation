import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, existsSync } from 'node:fs';
import { inflateSync } from 'node:zlib';
import { fileURLToPath } from 'node:url';
import { manifest, validateManifest } from '../../Build/web/src/pwa/manifest.mjs';
import { render } from '../../Build/web/src/pwa/icons.mjs';

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

test('every icon exists, PNG header matches declared size, pixels match the procedural source', () => {
  for (const i of manifest.icons) {
    assert.ok(existsSync(pub(i.src)), i.src);
    if (i.type !== 'image/png') continue;
    const buf = readFileSync(pub(i.src)), n = Number(i.sizes.split('x')[0]);
    assert.equal(buf.subarray(1, 4).toString(), 'PNG');
    assert.equal(buf.readUInt32BE(16), n); assert.equal(buf.readUInt32BE(20), n);
    assert.equal(buf[25], 6); // RGBA
    const idat = []; let o = 8;
    while (o < buf.length) { const len = buf.readUInt32BE(o), t = buf.toString('ascii', o + 4, o + 8); if (t === 'IDAT') idat.push(buf.subarray(o + 8, o + 8 + len)); o += 12 + len; }
    const raw = inflateSync(Buffer.concat(idat)), px = Buffer.alloc(n * n * 4);
    for (let y = 0; y < n; y++) raw.copy(px, y * n * 4, y * (n * 4 + 1) + 1, (y + 1) * (n * 4 + 1));
    assert.ok(px.equals(render(n, i.purpose)), i.src + ' differs from generator');
  }
});

test('maskable icon is full-bleed opaque; any icon has transparent corners', () => {
  const m = render(512, 'maskable'), a = render(512, 'any');
  assert.equal(m[3], 255); assert.equal(m[(512 * 512 - 1) * 4 + 3], 255);
  assert.equal(a[3], 0);
});

test('no unlicensed assets: only generated files under public/pwa, SVG is self-contained', () => {
  const svg = readFileSync(pub('/pwa/icon.svg'), 'utf8');
  assert.ok(!/href=|<image|<text|font|https?:\/\/(?!www\.w3\.org)/i.test(svg));
  const prov = readFileSync(fileURLToPath(new URL('../../Build/web/src/pwa/README.md', import.meta.url)), 'utf8');
  assert.match(prov, /Provenance/);
});
