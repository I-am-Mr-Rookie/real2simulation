import assert from 'node:assert/strict';
import test from 'node:test';
import { readFile, access } from 'node:fs/promises';
import { filterChips, matchesFilter } from '../../Build/web/src/app/(public)/library/library-copy.mjs';

// S15ao: library L1 / lab LB1 / icon-link polish (source-level; JSX compiled by next build).
const src = (p) => readFile(new URL('../../Build/web/src/' + p, import.meta.url), 'utf8');

test('library filter chips count manifest labels verbatim, keep zero-count evidence chips, and filter exactly', () => {
  const demos = [{ label: 'SIMULATED' }, { label: 'SIMULATED' }, { label: 'UNAVAILABLE' }];
  assert.deepEqual(filterChips(demos), [['All', 3], ['RECORDED', 0], ['SIMULATED', 2], ['what-if', 0], ['UNAVAILABLE', 1]]);
  assert.equal(demos.filter((d) => matchesFilter(d, 'RECORDED')).length, 0);
  assert.equal(demos.filter((d) => matchesFilter(d, 'All')).length, 3);
});

test('library keeps credit/caveat copy, B3 thumbnail + empty state; page CSS is tokens-only', async () => {
  const client = await src('app/(public)/library/LibraryClient.jsx');
  for (const s of ['{creditLine(entry)}', 'Display only · not a measurement.', "entry.scale_label || 'SCALE_UNVERIFIED'", 'AppArt id="b3"', 'No clips match', 'Clear filters', 'aria-pressed']) assert.ok(client.includes(s), s);
  assert.doesNotMatch(await src('app/(public)/library/library.css'), /#[0-9a-fA-F]{3,8}\b|0 var\(--r2s-ink\)/);
});

test('lab is two-column with B4 never-run state and a SIMULATED chip on every chart', async () => {
  const lab = await src('lab/LabClient.jsx'), sim = await src('lab/BrowserSimulation.jsx');
  for (const s of ['lab-layout', 'AppArt id="b4"', 'Set parameters and run']) assert.ok(lab.includes(s), s);
  for (const f of [lab, sim]) assert.equal(f.match(/<svg/g).length, f.match(/<span className="chart-chip">SIMULATED<\/span><svg/g).length);
});

test('no app/icon.svg file convention (single icon link set from layout metadata); /icon.svg still served by a route', async () => {
  await assert.rejects(access(new URL('../../Build/web/src/app/icon.svg/icon.svg', import.meta.url)));
  assert.match(await src('app/icon.svg/route.js'), /image\/svg\+xml/);
});
