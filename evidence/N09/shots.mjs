// N09 headed Playwright check of the live workspace on local dev (next dev :3009 + local API :8077). Usage: node evidence/N09/shots.mjs
import { createRequire } from 'module'; import fs from 'fs';
const require = createRequire('C:/Users/HP/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/');
const { chromium } = require('playwright-core');
const base = process.env.BASE || 'http://localhost:3009';
const VIDEO = process.env.N09_VIDEO; // synthetic ffmpeg testsrc clip, not committed
const D = decodeURIComponent(new URL('.', import.meta.url).pathname.slice(1));
const rec = { start_utc: new Date().toISOString(), steps: [], fails: [] };
const step = (k, v = true) => rec.steps.push({ k, v, utc: new Date().toISOString() });
const b = await chromium.launch({ headless: false });
const ctx = await b.newContext({ viewport: { width: 1280, height: 900 } }); const p = await ctx.newPage();
p.on('response', (r) => { if (r.status() >= 400) rec.fails.push(r.status() + ' ' + new URL(r.url()).pathname.slice(0, 60)); });
const shot = (n) => p.screenshot({ path: D + n + '.png' });
try {
  const email = 'n09-' + Date.now().toString(36) + '+clerk_test@example.com';
  await p.goto(base + '/sign-up');
  await p.locator('input[name=emailAddress]').fill(email); await p.locator('input[name=emailAddress]').press('Enter');
  await p.locator('input[autocomplete=one-time-code], input[name=code]').first().waitFor({ timeout: 60000 }); await p.keyboard.type('424242');
  await p.waitForURL((u) => !/sign-up/.test(u.pathname), { timeout: 60000 }); step('signed_up');
  if (!/workspace/.test(p.url())) await p.goto(base + '/workspace');
  await p.waitForURL(/workspace\/.+/, { timeout: 60000 });
  await p.getByRole('heading', { name: 'Choose how the agent runs' }).waitFor({ timeout: 60000 }); step('first_run_screen');
  await shot('desktop-1-first-run');
  await p.getByText('Contributor', { exact: true }).click(); step('contributor_selectable', await p.locator('.lv-mode[data-on=true]').innerText());
  await p.getByText('Standard', { exact: true }).first().click();
  await p.getByRole('button', { name: 'Continue' }).click(); step('mode_saved', await p.evaluate(() => localStorage.getItem('r2s.agent.mode')));
  step('gpu_dot', await p.locator('.lv-gpu').getAttribute('data-tone'));
  await p.getByRole('button', { name: 'New project' }).click();
  await p.getByText('What are you uploading?').first().waitFor(); await p.waitForTimeout(500);
  await shot('desktop-2-question-card');
  await p.locator('.lv-q .r2s-qopt', { hasText: 'Room video' }).click(); await p.locator('.lv-q button[type=submit]').click();
  await p.getByText('Filming tips for room video:').waitFor({ timeout: 20000 }); step('project_created', await p.locator('#lv-proj-h').innerText());
  if (VIDEO) {
    await p.setInputFiles('#lv-files input[type=file]', VIDEO);
    await p.locator('.lv-files li').first().waitFor({ timeout: 60000 }); step('uploaded', await p.locator('.lv-quota p').innerText());
    await p.getByRole('button', { name: 'Preview' }).first().click(); await p.locator('.lv-video').waitFor();
    await p.waitForFunction(() => document.querySelector('.lv-video')?.readyState >= 1, null, { timeout: 20000 }).then(() => step('preview_metadata_loaded')).catch(() => step('preview_metadata_loaded', false));
  }
  step('jobs', await p.locator('#lv-jobs').innerText());
  await p.locator('textarea#lv-draft').fill('How do I measure g with a falling ball?'); await p.getByRole('button', { name: 'Send' }).click();
  await p.locator('.lv-msg[data-role=assistant], .lv-msg[data-role=error]').last().waitFor({ timeout: 60000 }); await p.waitForTimeout(800);
  step('agent_turn', await p.locator('.lv-msgs').innerText());
  await shot('desktop-3-files-chat');
  // 375 px: fresh narrow page in the same signed-in context; the agent turn is mocked (ask_user fixture) so no paid model call is made.
  const m = await ctx.newPage(); await m.setViewportSize({ width: 375, height: 812 });
  await m.route('**/api/workspace/agent/turn', (route) => route.fulfill({ json: { model: 'fixture', reply: 'What are you dropping?', stopped: 'ask_user', question: {
    question: 'What are you dropping?', options: [{ label: 'A ball', recommended: true }, { label: 'A coin', recommended: false }, { label: 'Something else', recommended: false }] } } }));
  await m.goto(base + '/workspace'); await m.waitForURL(/workspace\/.+/); await m.locator('#lv-files .lv-files li').first().waitFor({ timeout: 60000 });
  await m.screenshot({ path: D + 'mobile-1-centre.png' });
  await m.locator('#lv-files').scrollIntoViewIfNeeded(); await m.screenshot({ path: D + 'mobile-2-files.png' });
  await m.locator('button[data-toggle=right]').click(); await m.waitForTimeout(500);
  await m.locator('textarea#lv-draft').fill('Measure g with a drop'); await m.getByRole('button', { name: 'Send' }).click();
  await m.getByText('What are you dropping?').first().waitFor(); await m.waitForTimeout(400);
  step('mobile_question_card', await m.locator('.lv-q').innerText());
  await m.screenshot({ path: D + 'mobile-3-agent-question.png' });
  rec.status = 'ok';
} catch (e) { rec.status = 'error'; rec.error = String(e).replace(/\S+@\S+/g, '<email>').slice(0, 400); await shot('error').catch(() => {}); }
rec.end_utc = new Date().toISOString();
fs.writeFileSync(D + 'shots.json', JSON.stringify(rec, null, 1).replace(/[\w.+-]+@example\.com/g, '<email>'));
await b.close();
console.log(rec.status, rec.error || '');
