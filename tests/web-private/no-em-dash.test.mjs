import test from 'node:test';
import assert from 'node:assert/strict';
import { readdirSync, readFileSync, statSync } from 'node:fs';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { dash } from '../../Build/web/src/workspace/display.mjs';

const ROOT = fileURLToPath(new URL('../../Build/web/src/', import.meta.url));
// S15au owns these; they are checked by their own tests.
const SKIP = ['workspace/controller.mjs', 'workspace/workflow.mjs', 'app/SiteFrame.jsx', 'app/(public)/page.jsx', 'app/(public)/home', 'app/(public)/MarketingArt.jsx'];
const walk = (d) => readdirSync(d).flatMap((n) => { const p = join(d, n); return statSync(p).isDirectory() ? walk(p) : [p]; });

test('no em dash or spaced en dash in rendered web sources', () => {
  const bad = walk(ROOT).filter((p) => /\.(mjs|jsx|js|json|css)$/.test(p) && !SKIP.some((s) => p.replaceAll('\\', '/').includes(s)))
    .filter((p) => /\u2014| \u2013 /.test(readFileSync(p, 'utf8')));
  assert.deepEqual(bad, []);
});

test('dash swaps only the separator', () => assert.equal(dash('SIMULATED \u2014 a\u2014b'), 'SIMULATED \u00b7 a\u2014b'));

