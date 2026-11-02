// Scripted fallback only: IAB returned "Browser is not available: iab". Real paid RM04 output, local mocked BFF.
import assert from 'node:assert/strict';
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { createRequire } from 'node:module';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const require = createRequire(import.meta.url);
const { chromium } = require('C:/Users/HP/AppData/Local/npm-cache/_npx/db89d7302a373f10/node_modules/playwright-core');
const out = path.dirname(fileURLToPath(import.meta.url));
const id = '59'.repeat(16), job = path.join(out, 'live-data/rooms/n59_public_rm04', id);
const json = async (name) => JSON.parse(await readFile(path.join(job, name), 'utf8'));
const sleep = (ms) => new Promise((ok) => setTimeout(ok, ms));
const deadline = Date.now() + 20 * 60 * 1000;
while ((await json('status.json')).state !== 'done') {
  assert.ok(Date.now() < deadline, 'public sample room did not become ready');
  await sleep(1000);
}
const initial = await json('room.json');
const selected = initial.shell.kept.find((o) => o.upgrade?.state === 'pending') ?? initial.shell.kept[0];
assert.ok(selected, 'sample must have furniture');
const browser = await chromium.launch({ headless: false });
const page = await browser.newPage({ viewport: { width: 1440, height: 960 }, acceptDownloads: true });
const errors = [], glbs = new Set();
page.on('pageerror', (e) => errors.push(e.message));
await page.route('**/api/workspace/**', async (route) => {
  const p = new URL(route.request().url()).pathname;
  if (p.endsWith('/result')) return route.fulfill({ json: { room: await json('room.json'), scene: await json('scene.json') } });
  if (p.endsWith('/room.ply')) return route.fulfill({ body: await readFile(path.join(job, 'room.ply')), contentType: 'application/octet-stream' });
  if (p.endsWith('.glb')) {
    glbs.add(path.basename(p));
    return route.fulfill({ body: await readFile(path.join(job, 'objects', path.basename(p))), contentType: 'model/gltf-binary' });
  }
  if (p.endsWith('/' + id)) return route.fulfill({ json: { job: await json('status.json') } });
  return route.fulfill({ json: {} });
});
await page.goto('http://localhost:3099/lab?editor=1&room=' + id);
await page.getByRole('status').filter({ hasText: 'Your room as a lab shell' }).waitFor({ timeout: 30000 });
await page.getByRole('button', { name: selected.id + ' Block', exact: true }).click();
await page.getByLabel('Mass (kg)', { exact: true }).fill('42');
await page.getByLabel('Mass (kg)', { exact: true }).press('Tab');
await mkdir(path.join(out, 'ui'), { recursive: true });
const pendingText = await page.locator('.le-status').textContent();
await page.screenshot({ path: path.join(out, 'ui/room-pending.png'), fullPage: true });
while ((await json('room.json')).shell.kept.some((o) => o.upgrade?.state === 'pending')) {
  assert.ok(Date.now() < deadline, 'background upgrades did not finish');
  await sleep(1000);
}
await page.waitForFunction(() => !document.querySelector('.le-status').textContent.includes('Improving '), { timeout: 20000 });
assert.ok(glbs.size > 0, 'editor must request a real generated GLB without reload');
const downloadPromise = page.waitForEvent('download');
await page.getByRole('button', { name: 'Export scene', exact: true }).click();
const download = await downloadPromise;
const stream = await download.createReadStream(), chunks = [];
for await (const chunk of stream) chunks.push(chunk);
const exported = JSON.parse(Buffer.concat(chunks).toString('utf8'));
const improved = exported.objects.filter((o) => o.shape?.type === 'mesh');
assert.ok(improved.length > 0);
assert.ok(improved.every((o) => o.shape.collider === 'box'));
assert.equal(exported.objects.find((o) => o.id === selected.id).mass, 42, 'poll preserves local user edits');
await page.locator('.le-honesty summary').click();
assert.equal(await page.getByText('MODEL-GENERATED shapes · Powered by Stability AI', { exact: true }).count(), 1);
await page.screenshot({ path: path.join(out, 'ui/room-ready.png'), fullPage: true });
await page.reload();
await page.getByRole('status').filter({ hasText: 'Your room as a lab shell' }).waitFor({ timeout: 30000 });
await page.setViewportSize({ width: 390, height: 844 });
await page.screenshot({ path: path.join(out, 'ui/room-reopened-mobile.png'), fullPage: true });
assert.deepEqual(errors, []);
await writeFile(path.join(out, 'ui-summary.json'), JSON.stringify({ mode: 'headed Playwright scripted fallback',
  iab_error: 'Browser is not available: iab', source: 'real paid RM04 output via local test-only BFF interception',
  pendingText, requested_glbs: [...glbs], upgraded: improved.map((o) => o.id), edited_mass_preserved: true,
  reopened: true, mobile_viewport: [390, 844], page_errors: errors }, null, 2));
await browser.close();
console.log(JSON.stringify({ upgraded: improved.length, requested_glbs: glbs.size, errors }));
