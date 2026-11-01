// N33 headed Playwright Chromium: public /lab editor, compact Add menu, kit objects, Play, Delete key, undo/redo; desktop + 375. Local only, no paid calls.
import { createRequire } from 'module'; import fs from 'fs';
const require = createRequire('C:/Users/HP/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/');
const { chromium } = require('playwright-core');
const base = process.env.BASE || 'http://localhost:3033';
const D = decodeURIComponent(new URL('.', import.meta.url).pathname.slice(1));
const rec = { start_utc: new Date().toISOString(), steps: [], console_errors: [] };
const step = (k, v = true) => { rec.steps.push({ k, v }); console.log(k, typeof v === 'string' ? v.slice(0, 300) : JSON.stringify(v)); };
const b = await chromium.launch({ headless: false });
const p = await (await b.newContext({ viewport: { width: 1280, height: 900 } })).newPage();
p.on('console', (m) => { if (m.type() === 'error') rec.console_errors.push(m.text().slice(0, 200)); });
// The JSON textarea updates one render after the scene; settle before reading it.
const ids = async () => { await p.waitForTimeout(400); return JSON.parse(await p.locator('textarea[aria-label="Scene JSON"]').inputValue()).objects.map((o) => o.id); };
const add = async (name) => { await p.locator('details.le-add summary').click(); await p.getByRole('menuitem', { name }).click(); };
try {
  await p.goto(base + '/lab?editor=1');
  await p.locator('[data-testid=lab-editor-canvas] canvas').waitFor({ timeout: 60000 });
  await p.locator('details.le-add summary').click();
  step('menu_items', await p.getByRole('menuitem').count());
  await p.screenshot({ path: D + 'add-menu-desktop.png' });
  await p.locator('details.le-add summary').click();
  for (const n of ['Atwood machine', 'Flywheel', 'Cart and track', 'Projectile launcher', 'Collision balls', '200 g mass', 'Photogate timer']) await add(n);
  step('ids_after_add', await ids());
  await p.locator('.le-panel', { hasText: 'photogate-1' }).first().waitFor({ timeout: 5000 }); // selection rendered, as a user sees it
  await p.keyboard.press('Delete'); await p.waitForTimeout(200); step('ids_after_delete_key', await ids());
  await p.keyboard.press('Control+z'); step('ids_after_undo', await ids());
  await p.keyboard.press('Control+Shift+z'); step('ids_after_redo', await ids());
  await p.getByRole('button', { name: 'Undo' }).click(); step('ids_after_undo_button', await ids());
  await p.getByRole('button', { name: /Fit view/ }).click();
  await p.getByRole('button', { name: 'Play' }).click();
  await p.getByText(/Running\. SIMULATED physics/).waitFor({ timeout: 30000 });
  await p.waitForFunction(() => parseFloat(document.querySelector('.le-time')?.textContent.replace('t = ', '')) > 0.9, null, { timeout: 30000 });
  await p.getByRole('button', { name: 'Pause' }).click();
  step('time', await p.locator('.le-time').innerText());
  await p.screenshot({ path: D + 'kit-play-desktop.png' });
  await p.setViewportSize({ width: 375, height: 812 }); await p.waitForTimeout(800);
  step('scrollWidth_375', await p.evaluate(() => document.documentElement.scrollWidth));
  await p.screenshot({ path: D + 'kit-play-375.png' });
  await p.getByRole('button', { name: 'Reset' }).click();
  await p.locator('details.le-add summary').click(); await p.waitForTimeout(300);
  step('menu_box_375', await p.locator('.le-menu').boundingBox());
  await p.screenshot({ path: D + 'add-menu-375.png' });
  step('status', await p.locator('.le-status').innerText());
} catch (e) { step('error', String(e).slice(0, 400)); process.exitCode = 1; }
finally { rec.end_utc = new Date().toISOString(); fs.writeFileSync(D + 'screenshots.json', JSON.stringify(rec, null, 2)); await b.close(); }
