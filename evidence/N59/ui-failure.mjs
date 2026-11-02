// SIMULATED API failures only. The paid live proof remains ui-summary.json; this script makes no model calls.
import assert from 'node:assert/strict';
import { readFile, writeFile } from 'node:fs/promises';
import { createRequire } from 'node:module';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const { chromium } = createRequire(import.meta.url)('C:/Users/HP/AppData/Local/npm-cache/_npx/db89d7302a373f10/node_modules/playwright-core');
const out = path.dirname(fileURLToPath(import.meta.url)), id = '59'.repeat(16);
const job = path.join(out, 'live-data/rooms/n59_public_rm04', id);
const room = JSON.parse(await readFile(path.join(job, 'room.json'), 'utf8'));
const scene = JSON.parse(await readFile(path.join(job, 'scene.json'), 'utf8'));
const selected = room.shell.kept.find((o) => o.upgrade?.state === 'ready').id;
let failed = false;
const browser = await chromium.launch({ headless: false });
const page = await browser.newPage({ viewport: { width: 1440, height: 960 } });
const errors = [];
page.on('pageerror', (e) => errors.push(e.message));
await page.route('**/api/workspace/**', async (route) => {
  const p = new URL(route.request().url()).pathname;
  if (p.endsWith('/result')) {
    const r = structuredClone(room), s = structuredClone(scene);
    for (const o of r.shell.kept) if (o.upgrade) o.upgrade = failed ? { state: 'failed', reason: 'SIMULATED cap denial' } : { state: 'pending' };
    for (const o of s.objects) if (o.shape?.type === 'mesh') o.shape = { type: 'box', fallback_reason: failed ? 'SIMULATED cap denial' : 'pending' };
    return route.fulfill({ json: { scene: s, room: r } });
  }
  if (p.endsWith('/room.ply')) return route.fulfill({ body: await readFile(path.join(job, 'room.ply')) });
  if (p.endsWith('/' + id)) return route.fulfill({ json: { job: { state: 'done' } } });
  return route.fulfill({ json: {} });
});
await page.goto('http://localhost:3099/lab?editor=1&room=' + id);
await page.locator('.le-status').filter({ hasText: 'Improving 4 objects' }).waitFor({ timeout: 30000 });
await page.getByRole('button', { name: selected + ' Block', exact: true }).click();
await page.getByLabel('Mass (kg)', { exact: true }).fill('42');
await page.getByLabel('Mass (kg)', { exact: true }).press('Tab');
await page.getByRole('button', { name: 'Play', exact: true }).first().click();
await page.locator('.le-status').filter({ hasText: 'Running.' }).waitFor({ timeout: 20000 });
failed = true;
await page.getByRole('button', { name: 'Reset', exact: true }).first().click();
await page.getByText('Measured box shape. SIMULATED cap denial', { exact: true }).waitFor({ timeout: 20000 });
assert.equal(await page.getByLabel('Mass (kg)', { exact: true }).inputValue(), '42');
assert.ok(!(await page.locator('.le-status').textContent()).includes('Improving '));
assert.deepEqual(errors, []);
await writeFile(path.join(out, 'ui-failure-summary.json'), JSON.stringify({ label: 'SIMULATED API-only regression check',
  checks: ['failed reason replaces pending', 'room simulation remains usable', 'reset applies terminal update', 'mass edit preserved'],
  model_calls: 0, page_errors: errors }, null, 2));
await browser.close();
console.log('UI failure regression passed (SIMULATED, zero model calls)');
