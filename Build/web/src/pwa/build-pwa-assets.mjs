// Regenerate public/pwa assets: node Build/web/src/pwa/build-pwa-assets.mjs
import { mkdirSync, writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { manifest, validateManifest } from './manifest.mjs';
import { render, encodePng, svg } from './icons.mjs';

const out = fileURLToPath(new URL('../../public/pwa/', import.meta.url));
const problems = validateManifest(manifest);
if (problems.length) throw new Error('invalid manifest: ' + problems.join('; '));
mkdirSync(out, { recursive: true });
writeFileSync(out + 'manifest.webmanifest', JSON.stringify(manifest, null, 2) + '\n');
writeFileSync(out + 'icon.svg', svg());
for (const [name, size, variant] of [['icon-192.png', 192, 'any'], ['icon-512.png', 512, 'any'], ['icon-maskable-512.png', 512, 'maskable']])
  writeFileSync(out + name, encodePng(size, render(size, variant)));
console.log('wrote PWA assets to ' + out);
