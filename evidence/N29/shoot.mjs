// N29 headed Playwright Chromium: public /lab editor, import the SAMPLE room cloud (RM04 points-mobile.ply, RECORDED,
// MODEL-ESTIMATED geometry), add a ball above a proxy surface, Play, then screenshot desktop and 375 px. Local only, no paid calls.
import { createRequire } from 'module'; import fs from 'fs';
const require = createRequire('C:/Users/HP/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/');
const { chromium } = require('playwright-core');
const base = process.env.BASE || 'http://localhost:3029';
const D = decodeURIComponent(new URL('.', import.meta.url).pathname.slice(1));
const PLY = process.env.PLY;
const rec = { start_utc: new Date().toISOString(), steps: [], console_errors: [] };
const step = (k, v = true) => { rec.steps.push({ k, v }); console.log(k, typeof v === 'string' ? v.slice(0, 300) : JSON.stringify(v)); };
const b = await chromium.launch({ headless: false });
const p = await (await b.newContext({ viewport: { width: 1280, height: 900 } })).newPage();
p.on('console', (m) => { if (m.type() === 'error') rec.console_errors.push(m.text().slice(0, 200)); });
try {
  await p.goto(base + '/lab?editor=1');
  await p.locator('[data-testid=lab-editor-canvas] canvas').waitFor({ timeout: 60000 });
  await p.locator('input[type=file][accept=".json,.ply"]').setInputFiles(PLY);
  await p.getByText(/Room loaded: \d+ points/).waitFor({ timeout: 30000 });
  const chip = p.locator('.le-chip', { hasText: 'MODEL-ESTIMATED collision proxy' });
  const toggle = p.getByLabel('Room collisions');
  step('chip', await chip.innerText()); step('collisions_checked_on_load', await toggle.isChecked());
  await toggle.click(); step('chip_after_toggle_off', await chip.count());
  await toggle.click(); step('chip_after_toggle_on', await chip.count());
  step('room_panel', await p.locator('.le-panel', { hasText: 'static boxes' }).innerText());
  // Ball above a proxy surface found offline (rests at y about 0.75 in the shared Rapier world).
  const text = await p.locator('textarea[aria-label="Scene JSON"]').inputValue();
  const s = JSON.parse(text);
  s.objects.push({ id: 'ball-1', kind: 'ball', position: [-1.13, 1.2, -2.66], size: [0.1, 0.1, 0.1], restitution: 0.1 });
  await p.locator('details.le-json summary').click();
  await p.locator('textarea[aria-label="Scene JSON"]').fill(JSON.stringify(s));
  await p.getByRole('button', { name: 'Apply JSON' }).click();
  await p.getByText(/Scene loaded: 1 objects/).waitFor({ timeout: 10000 });
  await p.getByRole('button', { name: /Fit view to the room/ }).click();
  await p.getByRole('button', { name: 'Play' }).click();
  await p.getByText(/Running\. SIMULATED physics/).waitFor({ timeout: 30000 });
  await p.waitForFunction(() => parseFloat(document.querySelector('.le-time')?.textContent.replace('t = ', '')) > 2.5, null, { timeout: 30000 });
  await p.getByRole('button', { name: 'Pause' }).click();
  step('time', await p.locator('.le-time').innerText());
  await p.getByText('ball-1').first().waitFor({ timeout: 2000 }).catch(() => {});
  await p.screenshot({ path: D + 'room-ball-desktop.png' });
  await p.setViewportSize({ width: 375, height: 812 }); await p.waitForTimeout(800);
  await p.getByRole('button', { name: /Fit view to the room/ }).click(); await p.waitForTimeout(500);
  step('scrollWidth_375', await p.evaluate(() => document.documentElement.scrollWidth));
  await p.screenshot({ path: D + 'room-ball-375.png' });
  step('status', await p.locator('.le-status').innerText());
} catch (e) { step('error', String(e).slice(0, 400)); process.exitCode = 1; }
finally { rec.end_utc = new Date().toISOString(); fs.writeFileSync(D + 'screenshots.json', JSON.stringify(rec, null, 2)); await b.close(); }
