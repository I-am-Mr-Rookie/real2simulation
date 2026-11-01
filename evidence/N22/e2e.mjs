// N22 headed Playwright E2E of both live modes on local dev (next dev :3022 + local API :8122, temp R2S_DATA_DIR).
// Usage: N22_DIR=<dir with ST03-trim.mp4 and RM02.mp4> node evidence/N22/e2e.mjs   (clips are Pexels, not committed)
import { createRequire } from 'module'; import fs from 'fs';
const require = createRequire('C:/Users/HP/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/');
const { chromium } = require('playwright-core');
const base = process.env.BASE || 'http://localhost:3022', DIR = process.env.N22_DIR, ONLY = process.env.N22_ONLY || 'AB';
const D = decodeURIComponent(new URL('.', import.meta.url).pathname.slice(1));
const rec = { start_utc: new Date().toISOString(), steps: [], fails: [] };
const step = (k, v = true) => { rec.steps.push({ k, v, utc: new Date().toISOString() }); console.log(k, typeof v === 'string' ? v.slice(0, 160) : v); };
const b = await chromium.launch({ headless: false });
const ctx = await b.newContext({ viewport: { width: 1280, height: 900 } }); const p = await ctx.newPage();
await ctx.grantPermissions(['clipboard-read', 'clipboard-write'], { origin: base });
p.on('response', (r) => { if (r.status() >= 400) rec.fails.push(r.status() + ' ' + new URL(r.url()).pathname.slice(0, 70)); });
const shot = (n, full = false) => p.screenshot({ path: D + n + '.png', fullPage: full });
const narrow = async (n, fn) => { await p.setViewportSize({ width: 375, height: 812 }); await p.waitForTimeout(400); if (fn) await fn(); await shot(n, true); await p.setViewportSize({ width: 1280, height: 900 }); };
try {
  // next dev compiles routes on first visit and full-reloads other tabs; warm them so the workspace state survives.
  for (const w of ['/guess/warmup-token-not-real', '/lab', '/workspace']) await p.goto(base + w).catch(() => {});
  const email = 'n22-' + Date.now().toString(36) + '+clerk_test@example.com';
  await p.goto(base + '/sign-up');
  await p.locator('input[name=emailAddress]').fill(email); await p.locator('input[name=emailAddress]').press('Enter');
  await p.locator('input[autocomplete=one-time-code], input[name=code]').first().waitFor({ timeout: 90000 }); await p.keyboard.type('424242');
  await p.waitForURL((u) => !/sign-up/.test(u.pathname), { timeout: 90000 }); step('signed_up');
  if (!/workspace/.test(p.url())) await p.goto(base + '/workspace');
  await p.getByRole('heading', { name: 'Choose how the agent runs' }).waitFor({ timeout: 90000 });
  await p.getByRole('button', { name: 'Continue' }).click(); step('mode_saved');
  const wsUrl = p.url();
  if (ONLY.includes('B')) {
    await p.getByRole('button', { name: 'New project' }).click();
    await p.locator('.lv-q .r2s-qopt', { hasText: 'My experiment' }).click(); await p.locator('.lv-q button[type=submit]').click();
    await p.getByText('Filming tips for my experiment:').waitFor({ timeout: 30000 }); step('project_experiment');
    await p.setInputFiles('#lv-files input[type=file]', DIR + '/ST03-trim.mp4');
    const row = p.locator('.lv-files > li', { hasText: 'ST03-trim.mp4' });
    await row.waitFor({ timeout: 90000 }); step('uploaded_st03');
    await row.getByRole('button', { name: 'Measure this experiment' }).click();
    const v = p.locator('.lv-still video');
    await p.waitForFunction(() => document.querySelector('.lv-still video')?.readyState >= 2, null, { timeout: 30000 }); step('first_frame_still');
    const bb = await v.boundingBox(); await v.click({ position: { x: bb.width * 0.5, y: bb.height * 0.3 } });
    step('clicked_point', await p.locator('.lv-measure [role=status]').innerText());
    await shot('desktop-1-measure-click');
    await p.getByLabel('Or its name').fill('apple'); step('name_clears_point', await p.locator('.lv-measure [role=status]').innerText());
    await p.getByLabel('What it is').fill('apple width'); await p.getByLabel('Value').fill('8'); await p.getByLabel('Unit').selectOption('cm');
    await p.getByRole('button', { name: 'Start measuring' }).click();
    await p.locator('.lv-jobcard').first().waitFor({ timeout: 20000 }); await shot('desktop-2-measure-progress'); step('progress', await p.locator('.lv-jobcard').first().innerText());
    await p.locator('.lv-result').first().waitFor({ timeout: 300000 }).catch(() => {});
    step('result', await p.locator('.lv-jobcard').first().innerText());
    await p.locator('.lv-jobcard').first().scrollIntoViewIfNeeded(); await shot('desktop-3-measure-result');
    if (await p.getByRole('button', { name: 'Share as Guess the Gravity' }).count()) {
      await p.getByRole('button', { name: 'Share as Guess the Gravity' }).click();
      const link = p.getByLabel('Challenge link'); await link.waitFor({ timeout: 20000 }); const url = await link.inputValue(); step('share_link', url.replace(/guess\/.+/, 'guess/<token>'));
      await p.getByRole('button', { name: 'Copy link' }).click(); await p.getByRole('button', { name: 'Copied' }).waitFor({ timeout: 5000 }).then(() => step('copied')).catch(() => step('copied', false));
      const pub = await ctx.newPage(); await pub.goto(url); await pub.getByText('Guess the Gravity').first().waitFor({ timeout: 30000 }); step('public_page_ok'); await pub.screenshot({ path: D + 'desktop-4-guess-public.png' });
      await p.bringToFront(); await p.getByRole('button', { name: 'Revoke' }).click(); await p.getByText('Link revoked.').waitFor({ timeout: 10000 }); step('revoked');
      const r = await pub.goto(url); await pub.waitForTimeout(1500); step('public_after_revoke', (await pub.locator('body').innerText()).slice(0, 120)); await pub.close();
    }
    await narrow('mobile-1-measure-result', () => p.locator('.lv-result').first().scrollIntoViewIfNeeded().catch(() => {}));
    const redo = p.getByRole('link', { name: '3D replay, redo with changes' }).first();
    if (await redo.count()) {
      await redo.click(); await p.getByText('Dots and line: your measured track').waitFor({ timeout: 60000 }); step('redo_scene', await p.locator('.le-status').innerText());
      await p.getByRole('button', { name: 'Play' }).click(); await p.waitForTimeout(1500); await shot('desktop-5-redo-lab'); step('redo_played', await p.locator('.le-time').innerText());
      await narrow('mobile-2-redo-lab');
      await p.goto(wsUrl);
    }
  }
  if (ONLY.includes('A')) {
    await p.getByRole('button', { name: 'New project' }).click();
    await p.locator('.lv-q .r2s-qopt', { hasText: 'Room video' }).last().click(); await p.locator('.lv-q button[type=submit]').last().click();
    await p.getByText('Filming tips for room video:').last().waitFor({ timeout: 30000 }); step('project_room');
    await p.setInputFiles('#lv-files input[type=file]', DIR + '/RM02.mp4');
    const row = p.locator('.lv-files > li', { hasText: 'RM02.mp4' }); await row.waitFor({ timeout: 120000 }); step('uploaded_rm02');
    await row.getByRole('button', { name: 'Build my lab' }).click();
    const card = p.locator('.lv-jobcard', { hasText: 'Room lab' }).first(); await card.waitFor({ timeout: 20000 });
    await p.waitForTimeout(4000); await card.scrollIntoViewIfNeeded(); await shot('desktop-6-room-progress'); step('room_progress', await card.innerText());
    await narrow('mobile-3-room-progress', () => card.scrollIntoViewIfNeeded());
    await card.getByRole('link', { name: 'Open my lab' }).waitFor({ timeout: 420000 }); step('room_done', await card.innerText());
    await card.getByRole('link', { name: 'Open my lab' }).click();
    await p.getByText(/Your room: \d+ points/).waitFor({ timeout: 90000 }); step('lab_room', await p.locator('.le-status').innerText());
    await p.waitForTimeout(1500); await shot('desktop-7-room-lab');
    const img = p.locator('.le-view img');
    await p.getByLabel('View').selectOption('4'); await p.waitForFunction(() => document.querySelector('.le-view img')?.complete && document.querySelector('.le-view img').naturalWidth > 0, null, { timeout: 30000 });
    const nat = await img.evaluate((e) => [e.naturalWidth, e.naturalHeight, e.clientWidth, e.clientHeight]); step('view_dims', nat.join('x'));
    const at = (row, col) => ({ x: (col * nat[2]) / nat[0], y: (row * nat[3]) / nat[1] });
    // RM02 has no A4 sheet: these two clicks only exercise the wiring (temp data dir), they are not a real scale reference.
    await p.getByRole('button', { name: 'Mark the A4 sheet' }).click(); await img.click({ position: at(250, 200), force: true }); await img.click({ position: at(250, 260), force: true });
    await p.getByText(/A4 scale applied|Not applied/).waitFor({ timeout: 60000 }); step('a4', await p.locator('.le-status').innerText() + ' | ' + await p.locator('.le-room').innerText());
    await p.getByLabel('View').selectOption('4'); await p.waitForTimeout(800);
    await p.getByRole('button', { name: 'Add a real object' }).click(); await img.click({ position: at(215, 320), force: true });
    await p.getByText(/Added room-object|Not applied/).first().waitFor({ timeout: 90000 }); step('object', await p.locator('.le-status').innerText());
    await p.waitForTimeout(1000); await shot('desktop-8-room-object', true);
    await narrow('mobile-4-room-lab');
  }
} catch (e) { step('error', String(e.message || e).slice(0, 400)); await shot('error').catch(() => {}); }
rec.end_utc = new Date().toISOString();
fs.writeFileSync(D + 'e2e.json', JSON.stringify(rec, null, 1));
await b.close();
