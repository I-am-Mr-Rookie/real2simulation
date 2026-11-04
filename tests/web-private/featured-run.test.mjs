import assert from 'node:assert/strict';
import test from 'node:test';
import { readFile, access } from 'node:fs/promises';
import { chartGeom, gravityCheck } from '../../Build/web/src/workspace/measure.mjs';

// N89: the public featured run must be the stored live result verbatim (no hand-typed numbers).
const read = async (p) => JSON.parse(await readFile(new URL('../../' + p, import.meta.url), 'utf8'));

test('featured run is a verbatim copy of the N07 live ST03 result and renders', async () => {
  const shown = await read('Build/web/src/app/(public)/home/featured-st03.json');
  assert.deepEqual(shown, await read('evidence/N07/live-st03.json'));
  const r = shown.result;
  assert.equal(r.fit.x.model, 'constant_acceleration'); // the card says acceleration wins on both axes
  assert.equal(r.fit.y.model, 'constant_acceleration');
  assert.ok(chartGeom(r).curve);
  assert.match(gravityCheck(r).text, /^what-if: .* mm in the plane of the fall/);
  await access(new URL('../../Build/web/public/featured/st03-frames.webp', import.meta.url));
  const jsx = await readFile(new URL('../../Build/web/src/app/(public)/home/FeaturedRun.jsx', import.meta.url), 'utf8');
  assert.doesNotMatch(jsx, /\u2014/);
  assert.match(jsx, /Roman Odintsov, Pexels License/);
});
