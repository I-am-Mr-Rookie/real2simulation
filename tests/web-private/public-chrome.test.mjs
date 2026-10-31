import assert from 'node:assert/strict';
import test from 'node:test';
import { readFile, access } from 'node:fs/promises';

// S15ai: public chrome/logo/metadata/honesty labels (source-level; JSX is compiled by next build, also run).
const src = (p) => readFile(new URL('../../Build/web/src/' + p, import.meta.url), 'utf8');
const pub = (p) => access(new URL('../../Build/web/public' + p, import.meta.url));

test('layout wires brand favicon/apple icons and A5 OG image through SiteFrame', async () => {
  const layout = await src('app/layout.jsx');
  assert.match(layout, /metadataBase: new URL\(process\.env\.RAILWAY_PUBLIC_DOMAIN/);
  for (const s of ["import SiteFrame from './SiteFrame'", "'/brand/favicon.ico'", "apple: { url: '/brand/mark-192.png'", "openGraph:", "'/images/marketing/a5-light-line@1x.png', width: 1200, height: 630", "manifest: '/pwa/manifest.webmanifest'"]) assert.ok(layout.includes(s), s);
  for (const p of ['/brand/favicon.ico', '/brand/mark-192.png', '/brand/mark-32.png', '/images/marketing/a5-light-line@1x.png']) await pub(p);
});

test('header has logo mark, wordmark text, icon nav and S15ah theme toggle; footer copy verbatim', async () => {
  const frame = await src('app/SiteFrame.jsx'), toggle = await src('app/ThemeToggle.jsx');
  for (const s of ['src="/brand/mark-192.png"', '>Real2Simulation</Link>', "icon(h, 'book'", "icon(h, 'flask'", '<ThemeToggle />', 'href="/sign-in"', 'Synthetic lab results are not calibrated measurements. Uploads are limited to approved licensed clips in the signed-in workspace.']) assert.ok(frame.includes(s), s);
  assert.match(toggle, /from '\.\.\/shell\/theme\.mjs'/);
  assert.match(toggle, /THEME_OPTIONS\.map\(\(t\) => <button key=\{t\.id\} type="button" data-theme-option=\{t\.id\}/);
});

test('home keeps honesty labels and serves one picture per theme family with explicit size', async () => {
  const home = await src('app/(public)/page.jsx'), art = await src('app/(public)/MarketingArt.jsx');
  for (const s of ['>RECORDED<', '>SIMULATED<', '>what-if<', 'Illustration only, not scene evidence.', 'We abstain when scale is unverified.', 'id="a1" width={1600} height={1000}']) assert.ok(home.includes(s), s);
  for (const id of ['a1', 'a2', 'a3', 'a4']) for (const fam of ['light', 'dark']) for (const ext of ['png', 'webp']) await pub('/images/marketing/' + id + '-' + fam + '-line@1x.' + ext);
  assert.match(art, /type="image\/webp"/);
  assert.match(art, /width=\{width\} height=\{height\}/);
});

test('public restyle uses tokens: no hard-coded colours in S15ai CSS, no legacy ink shadows in lab/library', async () => {
  const css = await src('app/styles.css');
  assert.doesNotMatch(css.slice(css.indexOf('/* S15ai')), /#[0-9a-fA-F]{3,8}\b/);
  assert.doesNotMatch(await src('lab/lab.css'), /box-shadow:[^;]*0 var\(--lab-ink\)/);
  assert.doesNotMatch(await src('app/(public)/library/page.jsx'), /#[0-9a-fA-F]{3,8}\b|0 var\(--r2s-ink\)/);
});
