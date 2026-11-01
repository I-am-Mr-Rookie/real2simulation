// N26 headed Playwright check (Chromium, never Chrome): fresh-session contributor card, result cards (no size, typed size, abstain),
// SAMPLE row in the Processing list, F8 upload limit text, F10 GPU label. Local dev: next dev :3026 + local uvicorn :8126, temp R2S_DATA_DIR.
// Fixtures: evidence/N26/seed.py (real fitter on a RECORDED track). The 429 and the green/empty GPU status are mocked responses (marked in e2e.json).
import { createRequire } from 'module'; import fs from 'fs'; import { execFileSync } from 'child_process';
const require = createRequire('C:/Users/HP/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/');
const { chromium } = require('playwright-core');
const base = process.env.BASE || 'http://localhost:3026', DATA = process.env.DATA_DIR, ROOT = process.env.ROOT;
const D = decodeURIComponent(new URL('.', import.meta.url).pathname.slice(1));
const rec = { start_utc: new Date().toISOString(), steps: [], fails: [], mocked: ['POST /api/workspace/files -> 429 (body shape from tests/api-storage)', 'GET /api/workspace/gpu/status -> green, queue 0'] };
const step = (k, v = true) => { rec.steps.push({ k, v: typeof v === 'string' ? v.slice(0, 600) : v }); console.log(k, typeof v === 'string' ? v.slice(0, 300) : v); };
const b = await chromium.launch({ headless: false });
const ctx = await b.newContext({ viewport: { width: 1280, height: 900 } }); const p = await ctx.newPage();
// A previous account in this browser chose Standard under the OLD global key: a new account must still be asked.
await ctx.addInitScript(() => { try { if (!localStorage.getItem('n26-seeded')) { localStorage.setItem('r2s.agent.mode', 'standard'); localStorage.setItem('n26-seeded', '1'); } } catch {} });
p.on('response', (r) => { if (r.status() >= 400) rec.fails.push(r.status() + ' ' + new URL(r.url()).pathname.slice(0, 70)); });
const shot = (n, loc) => (loc ? loc.screenshot({ path: D + n + '.png' }) : p.screenshot({ path: D + n + '.png' }));
const narrow = async (n, fn) => { await p.setViewportSize({ width: 375, height: 812 }); await p.waitForTimeout(600); await p.keyboard.press('Escape'); await p.waitForTimeout(300); if (fn) await fn(); await shot(n); await p.setViewportSize({ width: 1280, height: 900 }); await p.waitForTimeout(300); };
try {
  await p.goto(base + '/sign-up');
  const email = 'n26-' + Date.now().toString(36) + '+clerk_test@example.com';
  await p.locator('input[name=emailAddress]').fill(email); await p.locator('input[name=emailAddress]').press('Enter');
  await p.locator('input[autocomplete=one-time-code], input[name=code]').first().waitFor({ timeout: 90000 }); await p.keyboard.type('424242');
  await p.waitForURL((u) => !/sign-up/.test(u.pathname), { timeout: 90000 }); step('signed_up');
  if (!/workspace/.test(p.url())) await p.goto(base + '/workspace');
  // F3: the choice card must be there on the very first load after sign-up (no reload, no second goto).
  const card = p.getByRole('heading', { name: 'Choose how the agent runs' });
  const t0 = Date.now(); await card.waitFor({ timeout: 30000 }); step('contributor_card_first_load_ms', String(Date.now() - t0));
  step('legacy_global_key_was_set', await p.evaluate(() => localStorage.getItem('r2s.agent.mode')));
  await shot('desktop-1-contributor-card-fresh');
  await narrow('mobile-1-contributor-card-fresh');
  step('card_text', await p.locator('.lv-modes').innerText());
  await p.getByRole('button', { name: 'Continue' }).click();
  step('mode_keys', JSON.stringify(await p.evaluate(() => Object.keys(localStorage).filter((k) => k.startsWith('r2s.agent.mode')).map((k) => k.slice(0, 22) + '..' + localStorage.getItem(k)))));
  await p.reload(); await p.locator('.lv-pgroup').first().waitFor({ timeout: 60000 });
  step('card_not_shown_again_after_choice', String(await card.count() === 0));
  // F10 mock: warm-idle (green, queue empty)
  await p.route('**/api/workspace/gpu/status', (r) => r.fulfill({ json: { state: 'green', queue_length: 0, your_position: null, source: 'jobs' } }));
  await p.reload(); await p.locator('.lv-pgroup').first().waitFor({ timeout: 60000 });
  await p.locator('.lv-gpu').first().waitFor({ timeout: 20000 }).catch(() => {});
  const dotText = async () => p.locator('.lv-gpu').first().innerText().catch(() => 'no dot');
  step('gpu_dot', await dotText());
  if (!/idle/.test(await dotText())) { await p.getByRole('button', { name: /Agent & tools|agent/i }).first().click().catch(() => {}); await p.waitForTimeout(500); step('gpu_dot_after_open', await dotText()); }
  await shot('desktop-gpu-idle-dot');
  // seed fixtures for this owner (SAMPLE row was created by the first /projects list)
  const uid = await p.evaluate(() => window.Clerk?.user?.id);
  const seeded = JSON.parse(execFileSync('python', ['evidence/N26/seed.py', uid, DATA], { cwd: ROOT, encoding: 'utf8', env: { ...process.env, PYTHONPATH: ROOT } }).trim().split('\n').pop());
  step('seeded', JSON.stringify(Object.fromEntries(Object.entries(seeded).map(([k, v]) => [k, { label: v.label, curve: v.has_curve, reason: v.reason, q: v.quantity && [v.quantity.value, v.quantity.unit, v.quantity.label] }]))));
  await p.getByRole('button', { name: 'Refresh' }).click(); await p.waitForTimeout(1500);
  const sample = p.locator('.lv-pgroup[data-sample]');
  step('sample_row', await sample.locator('.lv-jobrow').first().innerText());
  await shot('desktop-2-projects-sample-row', p.locator('#lv-project'));
  const openRow = async (id) => { await p.locator('li.lv-jobrow[title="' + id + '"]').getByRole('button', { name: 'Open' }).click(); const c = p.locator('.lv-jobcard:has(strong[title="' + id + '"])'); await c.locator('.lv-result').waitFor({ timeout: 30000 }); await c.scrollIntoViewIfNeeded(); return c; };
  // SAMPLE in Processing
  const sid = await sample.locator('.lv-jobrow').first().getAttribute('title');
  const cs = await openRow(sid); step('processing_sample_card', await cs.innerText()); await shot('desktop-3-processing-sample', cs);
  // no size, typed size, abstain
  for (const [k, n] of [['no_size', '4-result-no-size'], ['typed_size', '5-result-typed-size'], ['abstain', '6-result-abstain']]) {
    const c = await openRow(seeded[k].id); step('card_' + k, await c.innerText());
    step('chart_' + k, JSON.stringify({ curve: await c.locator('.lv-curve').count(), band: await c.locator('.lv-band').count(), pts: await c.locator('.lv-pt').count() }));
    await shot('desktop-' + n, c);
    await narrow('mobile-' + n, async () => { await c.scrollIntoViewIfNeeded(); });
  }
  // F8: upload limit message with the reset time in local time
  const reset = '2026-11-01T18:00:00Z';
  const msg = 'Daily upload limit reached: 20 uploads per day. It resets at ' + reset + ' (midnight Dhaka time). Deleting a file frees storage but does not give back an upload.';
  await p.route('**/api/workspace/files', (r) => r.request().method() === 'POST'
    ? r.fulfill({ status: 429, json: { detail: { code: 'QUOTA_UPLOADS', message: msg, reason: 'daily_upload_limit', reset_at: reset } } }) : r.fallback());
  fs.writeFileSync(D + 'tiny.mp4', Buffer.from('not a real video'));
  await p.locator('#lv-files input[type=file]').setInputFiles(D + 'tiny.mp4'); await p.locator('#lv-files .ws-error').first().waitFor({ timeout: 15000 });
  step('upload_error_text', await p.locator('#lv-files .ws-error').first().innerText());
  step('browser_tz', await p.evaluate(() => Intl.DateTimeFormat().resolvedOptions().timeZone));
  await p.locator('#lv-files').scrollIntoViewIfNeeded(); await shot('desktop-7-upload-limit', p.locator('#lv-files'));
  fs.unlinkSync(D + 'tiny.mp4');
} catch (e) { step('error', String(e.message || e)); await shot('error').catch(() => {}); }
rec.end_utc = new Date().toISOString();
fs.writeFileSync(D + 'e2e.json', JSON.stringify(rec, null, 1));
await b.close();