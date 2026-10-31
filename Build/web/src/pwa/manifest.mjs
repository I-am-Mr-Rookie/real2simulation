// Single source of truth for the PWA manifest (S19a). Generated file:
// Build/web/public/pwa/manifest.webmanifest (node Build/web/src/pwa/build-pwa-assets.mjs).
export const MANIFEST_PATH = '/pwa/manifest.webmanifest';

export const manifest = {
  id: '/',
  name: 'Real2Simulation',
  short_name: 'Real2Sim',
  description: 'A workbench for testing physical explanations against video.',
  start_url: '/?source=pwa',
  scope: '/',
  display: 'standalone',
  background_color: '#ffffff',
  theme_color: '#155a92',
  categories: ['education', 'science'],
  // No "orientation" member: orientation locking is not claimed or requested.
  icons: [
    { src: '/brand/mark-192.png', sizes: '192x192', type: 'image/png', purpose: 'any' },
    { src: '/brand/mark-512.png', sizes: '512x512', type: 'image/png', purpose: 'any' },
    { src: '/brand/icon-maskable-512.png', sizes: '512x512', type: 'image/png', purpose: 'maskable' },
    { src: '/brand/mark.svg', sizes: 'any', type: 'image/svg+xml', purpose: 'any' }
  ]
};

// Not wired into layout.jsx (outside S19a Owns): layout may use
// `export const metadata = { ..., ...pwaMetadata }` in a later integration run.
export const pwaMetadata = { manifest: MANIFEST_PATH };

const HEX = /^#[0-9a-fA-F]{6}$/;
const DISPLAY = new Set(['standalone', 'fullscreen', 'minimal-ui', 'browser']);

// Returns a list of problems; empty means valid. Local icons only (no remote assets).
export function validateManifest(m) {
  const e = [];
  const str = (k) => { if (typeof m[k] !== 'string' || !m[k].trim()) e.push(k + ' must be a non-empty string'); };
  ['id', 'name', 'short_name', 'description', 'start_url', 'scope'].forEach(str);
  if (typeof m.short_name === 'string' && m.short_name.length > 12) e.push('short_name longer than 12 chars');
  if (!DISPLAY.has(m.display)) e.push('display invalid');
  if (!HEX.test(m.theme_color || '')) e.push('theme_color must be #rrggbb');
  if (!HEX.test(m.background_color || '')) e.push('background_color must be #rrggbb');
  if ('orientation' in m) e.push('orientation must not be set (no orientation-lock claim)');
  if (typeof m.scope === 'string' && typeof m.start_url === 'string') {
    const u = new URL(m.start_url, 'https://x.invalid');
    if (u.origin !== 'https://x.invalid' || !u.pathname.startsWith(m.scope)) e.push('start_url outside scope');
  }
  if (!Array.isArray(m.icons) || !m.icons.length) { e.push('icons missing'); return e; }
  for (const i of m.icons) {
    if (typeof i.src !== 'string' || !/^\/(pwa|brand)\//.test(i.src) || i.src.includes('..')) e.push('icon src must be local /pwa/ or /brand/: ' + i.src);
    if (!['image/png', 'image/svg+xml'].includes(i.type)) e.push('icon type invalid: ' + i.src);
    if (!['any', 'maskable'].includes(i.purpose)) e.push('icon purpose must be exactly any|maskable: ' + i.src);
    if (i.type === 'image/png' && !/^\d+x\d+$/.test(i.sizes)) e.push('png icon sizes invalid: ' + i.src);
  }
  const has = (sz, p) => m.icons.some((i) => i.type === 'image/png' && i.sizes === sz && i.purpose === p);
  if (!has('192x192', 'any')) e.push('need 192x192 any png');
  if (!has('512x512', 'any')) e.push('need 512x512 any png');
  if (!has('512x512', 'maskable')) e.push('need 512x512 maskable png');
  return e;
}
