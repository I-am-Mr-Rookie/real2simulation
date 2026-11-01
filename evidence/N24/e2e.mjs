// N24 headed Playwright check of the polished live screens (workspace home, measure result, room lab) in light and dark,
// desktop 1280 and 375 px, on local dev (next dev :3024 + local uvicorn :8124, temp R2S_DATA_DIR). Uses only the seeded
// SAMPLE project (RECORDED results), so no paid model or GPU call is made. Adapted from evidence/N22/e2e.mjs.
import { createRequire } from 'module'; import fs from 'fs';
const require = createRequire('C:/Users/HP/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/');
const { chromium } = require('playwright-core');
const base = process.env.BASE || 'http://localhost:3024';
const D = decodeURIComponent(new URL('.', import.meta.url).pathname.slice(1));
const rec = { start_utc: new Date().toISOString(), steps: [], fails: [] };
const step = (k, v = true) => { rec.steps.push({ k, v, utc: new Date().toISOString() }); console.log(k, typeof v === 'string' ? v.slice(0, 200) : v); };
const b = await chromium.launch({ headless: false });
const ctx = await b.newContext({ viewport: { width: 1280, height: 900 } }); const p = await ctx.newPage();
p.on('response', (r) => { if (r.status() >= 400) rec.fails.push(r.status() + ' ' + new URL(r.url()).pathname.slice(0, 70)); });
const shot = (n, full = false) => p.screenshot({ path: D + n + '.png', fullPage: full });
// Theme through the visible palette menu (the one control on every page), then confirm what <html> carries.
const theme = async (t) => { await p.locator('.theme-menu summary').first().click(); await p.locator('[data-theme-option="' + t + '"]').first().click(); await p.waitForTimeout(900);
  step('theme_' + t, await p.evaluate(() => document.documentElement.dataset.theme + '/' + document.documentElement.dataset.tone)); };
// The desktop-pinned nav pane turns into an overlay after a live resize to 375 px; Escape closes it (a fresh phone load starts closed).
const narrow = async (n, fn) => { await p.setViewportSize({ width: 375, height: 812 }); await p.waitForTimeout(600); await p.keyboard.press('Escape'); await p.waitForTimeout(300); if (fn) await fn(); await shot(n); await p.setViewportSize({ width: 1280, height: 900 }); await p.waitForTimeout(300); };
try {
  for (const w of ['/lab', '/workspace']) await p.goto(base + w).catch(() => {});
  const email = 'n24-' + Date.now().toString(36) + '+clerk_test@example.com';
  await p.goto(base + '/sign-up');
  await p.locator('input[name=emailAddress]').fill(email); await p.locator('input[name=emailAddress]').press('Enter');
  await p.locator('input[autocomplete=one-time-code], input[name=code]').first().waitFor({ timeout: 90000 }); await p.keyboard.type('424242');
  await p.waitForURL((u) => !/sign-up/.test(u.pathname), { timeout: 90000 }); step('signed_up');
  if (!/workspace/.test(p.url())) await p.goto(base + '/workspace');
  await p.evaluate(() => localStorage.setItem('r2s.theme', 'light'));
  const cont = p.getByRole('button', { name: 'Continue' });
  await cont.waitFor({ timeout: 60000 }).then(() => cont.click()).catch(() => {}); step('mode_saved');
  const homeReady = () => p.locator('.lv-pgroup').first().waitFor({ timeout: 60000 });
  await homeReady(); step('projects', await p.locator('#lv-project').innerText());
  await shot('desktop-1-home-light');
  await narrow('mobile-1-home-light');
  const sample = p.locator('.lv-pgroup[data-sample]');
  const roomHref = await sample.getByRole('link', { name: 'Open lab' }).first().getAttribute('href').catch(() => null); step('sample_room_href', String(roomHref));
  await sample.getByRole('button', { name: 'Open' }).first().click();
  const resultReady = () => p.locator('.lv-chart').first().waitFor({ timeout: 60000 });
  await resultReady(); await p.locator('.lv-jobcard').first().scrollIntoViewIfNeeded(); step('result', await p.locator('.lv-jobcard').first().innerText());
  await shot('desktop-2-measure-result-light');
  await narrow('mobile-2-measure-result-light', () => p.locator('.lv-chart').first().scrollIntoViewIfNeeded());
  await p.evaluate(() => window.scrollTo(0, 0)); await theme('dark'); await shot('desktop-3-home-dark');
  await resultReady().catch(() => {}); await p.locator('.lv-chart').first().scrollIntoViewIfNeeded().catch(() => {});
  await shot('desktop-4-measure-result-dark');
  await narrow('mobile-3-measure-result-dark', () => p.locator('.lv-chart').first().scrollIntoViewIfNeeded().catch(() => {}));
  const redo = await p.getByRole('link', { name: '3D replay, redo with changes' }).first().getAttribute('href').catch(() => null);
  if (roomHref) {
    await p.goto(base + roomHref); await p.getByText(/Your room: \d+ points/).waitFor({ timeout: 90000 }); await p.waitForTimeout(1500);
    step('room_lab', await p.locator('.le-status').innerText());
    await shot('desktop-5-room-lab-dark');
    await narrow('mobile-4-room-lab-dark');
    step('lab_theme', await p.evaluate(() => document.documentElement.dataset.theme));
    await theme('light'); await p.waitForTimeout(600);
    await shot('desktop-6-room-lab-light');
    await narrow('mobile-5-room-lab-light');
    await p.getByRole('button', { name: /inspector and scene JSON/ }).click(); await p.waitForTimeout(800); await shot('desktop-7-room-lab-panel-toggled');
  } else step('room_lab', 'no sample room link');
  if (redo) {
    await p.goto(base + redo); await p.getByText('Dots and line: your measured track').waitFor({ timeout: 60000 }); await p.waitForTimeout(1200);
    step('redo', await p.locator('.le-status').innerText()); await shot('desktop-8-redo-light');
  }
  await theme('midnight'); await p.waitForTimeout(800); await shot('desktop-9-redo-midnight');
} catch (e) { step('error', String(e.message || e)); await shot('error').catch(() => {}); }
rec.end_utc = new Date().toISOString();
fs.writeFileSync(D + 'e2e.json', JSON.stringify(rec, null, 1));
await b.close();
