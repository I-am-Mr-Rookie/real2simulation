import assert from 'node:assert/strict';
import test from 'node:test';
import { readFile } from 'node:fs/promises';
const src = (p) => readFile(new URL('../../Build/web/src/app/(public)/' + p, import.meta.url), 'utf8');

test('home copy is the owner-approved text', async () => {
  const page = await src('page.jsx');
  assert.match(page, /<span>Film Physics<\/span><span>Simulate it in 3D<\/span>/);
  assert.ok(page.includes('Point your phone at a real experiment. Get a 3D replay, measurements with error bars, and a lab to ask "what if".'));
  for (const t of ["title: 'Film it'", "title: 'Measure it'", "title: 'Remix it'", '<strong>Guess the Gravity</strong>', 'Every number shows where it came from: measured, simulated or what-if.']) assert.ok(page.includes(t), t);
  assert.ok(!page.includes('Guess the gravity'), 'hook is title case without a full stop');
  assert.ok((await src('MarketingArt.jsx')).includes("export const REPO_URL = 'https://github.com/I-am-Mr-Rookie/real2simulation';"), 'one shared repo constant');
  assert.ok(page.includes("import MarketingArt, { REPO_URL, GITHUB_MARK } from './MarketingArt';") && !page.includes('const REPO_URL'));
  assert.match(page, /href=\{REPO_URL\} target="_blank" rel="noopener noreferrer">\{GITHUB_MARK\}Explore the code on GitHub</);
  for (const l of ['>RECORDED<', '>SIMULATED<', '>what-if<', 'Real output.', 'Geometry MODEL-ESTIMATED, scale unverified.']) assert.ok(page.includes(l), l);
});

test('S15au showcase sections are full-width splits with captioned agent art', async () => {
  const [page, css] = await Promise.all([src('page.jsx'), src('home/home.css')]);
  assert.equal(page.match(/className="show show-split /g)?.length, 3);
  for (const c of ['<figcaption>The agent asks</figcaption>', '<figcaption>Your answer, labelled</figcaption>', "'scale unverified'"]) assert.ok(page.includes(c), c);
  assert.ok(!/text-align: center/.test(css), 'CTA aligned with the other sections');
  assert.match(css, /\.label-list \{ display: grid; grid-template-columns: repeat\(2, minmax\(0, 1fr\)\)/);
});

test('home has no em dash and motion is guarded for reduced motion', async () => {
  const [page, css, art] = await Promise.all([src('page.jsx'), src('home/home.css'), src('MarketingArt.jsx')]);
  for (const s of [page, css, art]) assert.ok(!s.includes('\u2014'));
  const guard = css.indexOf('@media (prefers-reduced-motion: no-preference)');
  assert.ok(guard > 0 && !css.slice(0, guard).includes('animation-timeline:') && css.slice(guard).includes('animation-timeline:'), 'all scroll timelines sit inside the no-preference guard');
  assert.ok(!/(^|[^-])(top|left|width|height|margin)\s*:/.test(css.slice(css.indexOf('@keyframes'))), 'keyframes animate composited props only');
});

test('N90 scroll-craft: engine mounted on the home, hero clock reads stored evidence, Meta credit leads the footer', async () => {
  const [page, mount, clock] = await Promise.all([src('page.jsx'), src('home/ScrollMount.jsx'), src('home/HeroClock.jsx')]);
  assert.ok(mount.includes("'/scrollcraft/scrollcraft.js'") && mount.includes('ScrollCraft.mount('));
  assert.match(page, /data-sc-act="pin"/);
  assert.ok(clock.includes("import run from './featured-st03.json';"));
  const frame = await readFile(new URL('../../Build/web/src/app/SiteFrame.jsx', import.meta.url), 'utf8');
  assert.ok(frame.indexOf('Built on Meta AI') < frame.indexOf('Powered by Stability AI'), 'Meta credit first, Stability attribution kept');
  for (const s of ['Baseten', 'Modal', 'Cerebral Valley', 'Meta Model API']) assert.ok(frame.includes(s), s);
});

