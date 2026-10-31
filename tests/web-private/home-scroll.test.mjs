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
  assert.ok(page.includes("const REPO_URL = 'https://github.com/I-am-Mr-Rookie/real2simulation';"));
  assert.match(page, /href=\{REPO_URL\} target="_blank" rel="noopener noreferrer">\{GITHUB_MARK\}Explore the code on GitHub</);
  for (const l of ['>RECORDED<', '>SIMULATED<', '>what-if<', 'Illustration only, not scene evidence.']) assert.ok(page.includes(l), l);
});

test('home has no em dash and motion is guarded for reduced motion', async () => {
  const [page, css, art] = await Promise.all([src('page.jsx'), src('home/home.css'), src('MarketingArt.jsx')]);
  for (const s of [page, css, art]) assert.ok(!s.includes('\u2014'));
  const guard = css.indexOf('@media (prefers-reduced-motion: no-preference)');
  assert.ok(guard > 0 && !css.slice(0, guard).includes('animation-timeline:') && css.slice(guard).includes('animation-timeline:'), 'all scroll timelines sit inside the no-preference guard');
  assert.ok(!/(^|[^-])(top|left|width|height|margin)\s*:/.test(css.slice(css.indexOf('@keyframes'))), 'keyframes animate composited props only');
});

