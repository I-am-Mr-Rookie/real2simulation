# PWA manifest and icons (S19a)

- `manifest.mjs` is the source of truth + `validateManifest`; `public/pwa/manifest.webmanifest` is generated.
- `icons.mjs` draws the icon (pendulum glyph) procedurally; `build-pwa-assets.mjs` writes the PNG/SVG files.
- **Provenance:** every icon is original, authored in this run from geometric primitives and the project colour #155a92. No third-party logo, font, stock image or Meta/NASA/Clerk artwork is used or embedded. The icon is a placeholder brand mark, not a legal trademark clearance.
- Manifest has no `orientation` member (no orientation lock claimed).
- **Not done here (outside Owns):** linking the manifest from `src/app/layout.jsx` (`...pwaMetadata`), service worker (S19b), install guidance (S19c), installability evidence (S19d). The manifest lives under `/pwa/` with `scope: "/"`; S19b must serve any service worker from a path allowed to control `/`.
