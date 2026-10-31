// Regenerate public/pwa/manifest.webmanifest: node Build/web/src/pwa/build-pwa-assets.mjs. Icons live in public/brand (S15ap logo v2).
import { mkdirSync, writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { manifest, validateManifest } from './manifest.mjs';

const out = fileURLToPath(new URL('../../public/pwa/', import.meta.url));
const problems = validateManifest(manifest);
if (problems.length) throw new Error('invalid manifest: ' + problems.join('; '));
mkdirSync(out, { recursive: true });
writeFileSync(out + 'manifest.webmanifest', JSON.stringify(manifest, null, 2) + '\n');
console.log('wrote ' + out + 'manifest.webmanifest');
