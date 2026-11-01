// N11 headed Playwright smoke on DEV. Usage: node evidence/N11/smoke.mjs <trimmed ST03 mp4>. Fresh +clerk_test account, code 424242; no emails written.
import { createRequire } from 'module'; import fs from 'fs';
const require = createRequire('C:/Users/HP/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/');
const { chromium } = require('playwright-core');
const base = process.env.BASE || 'https://web-dev-cd80.up.railway.app';
const VIDEO = process.argv[2];
const D = decodeURIComponent(new URL('.', import.meta.url).pathname.slice(1));
const rec = { start_utc: new Date().toISOString(), steps: [], fails: [] };
const step = (k, v = true) => { rec.steps.push({ k, v, utc: new Date().toISOString() }); console.log(k, JSON.stringify(v).slice(0, 300)); };
const b = await chromium.launch({ headless: false });
const ctx = await b.newContext({ viewport: { width: 1280, height: 900 } }); const p = await ctx.newPage();
p.on('response', (r) => { if (r.status() >= 400) rec.fails.push(r.status() + ' ' + new URL(r.url()).pathname.slice(0, 60)); });
const shot = (n) => p.screenshot({ path: D + n + '.png' });
const api = (path, init) => p.evaluate(async ([u, i]) => { const r = await fetch('/api/workspace' + u, i); let body = null; try { body = await r.json(); } catch {} return { status: r.status, body }; }, [path, init]);
try {
  const email = 'n11-' + Date.now().toString(36) + '+clerk_test@example.com';
  await p.goto(base + '/sign-up');
  await p.locator('input[name=emailAddress]').fill(email); await p.locator('input[name=emailAddress]').press('Enter');
  await p.locator('input[autocomplete=one-time-code], input[name=code]').first().waitFor({ timeout: 60000 }); await p.keyboard.type('424242');
  await p.waitForURL((u) => !/sign-up/.test(u.pathname), { timeout: 60000 }); step('signed_up');
  if (!/workspace/.test(p.url())) await p.goto(base + '/workspace');
  await p.waitForURL(/workspace\/.+/, { timeout: 60000 });
  await p.getByRole('heading', { name: 'Choose how the agent runs' }).waitFor({ timeout: 60000 });
  await p.getByRole('button', { name: 'Continue' }).click(); await p.locator('.lv-gpu').waitFor({ timeout: 30000 });
  // 1. sample project: seeded on the first files list the page already made
  const pr = await api('/projects'); const sample = (pr.body?.projects ?? []).filter((x) => x.title.startsWith('SAMPLE'));
  step('sample_projects', { status: pr.status, count: (pr.body?.projects ?? []).length, titles: sample.map((x) => x.title) });
  const sid = sample[0]?.id;
  const ex = await api('/experiments?project_id=' + sid);
  const e0 = ex.body?.experiments?.[0];
  step('sample_experiment', { status: ex.status, n: ex.body?.experiments?.length, state: e0?.status, label: e0?.result?.sample?.label, qty: e0?.result?.quantity?.unit });
  step('sample_files_empty', (await api('/files')).body?.files?.length === 0);
  step('rooms_list', (await api('/rooms')).status);
  await p.waitForTimeout(1500); await shot('1-sample-gpu-dot');
  step('gpu_dot', await p.locator('.lv-gpu').getAttribute('data-tone'));
  step('gpu_api', await api('/gpu/status'));
  // 2. upload the trimmed licensed clip, 3. start an experiment (one hosted SAM call, daily-cap reserved)
  await p.setInputFiles('#lv-files input[type=file]', VIDEO);
  await p.locator('.lv-files li').first().waitFor({ timeout: 60000 });
  const fl = (await api('/files')).body; const f = fl.files[0]; step('uploaded', { name: f.name, size: f.size, dur: f.duration_s, quota: fl.quota.uploads_today });
  const st = process.env.SKIP_EXP ? { status: 0, body: null } : await api('/experiments', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ file_id: f.id, target_text: 'apple' }) });
  step('experiment_started', { status: st.status, state: st.body?.experiment?.status }); const eid = st.body?.experiment?.id; let e;
  for (let i = 0; i < (process.env.SKIP_EXP ? 0 : 40); i++) { e = (await api('/experiments/' + eid)).body?.experiment; if (e && !['queued', 'running'].includes(e.status)) break; await p.waitForTimeout(5000); }
  step('experiment_done', { state: e?.status, err: e?.error, fit: e?.result?.status, label: e?.result?.label?.slice(0, 80), cost: e?.result?.cost_usd, frames: e?.result?.video_frames_processed });
  await p.reload(); await p.locator('#lv-jobs').waitFor({ timeout: 30000 }); await p.waitForTimeout(1500); await shot('2-after-experiment');
  // 4. agent one turn (one paid model call)
  if (!(await p.locator('textarea#lv-draft').isVisible())) await p.getByRole('button', { name: 'Agent & tools' }).click(); // agent panel is collapsed by default
  await p.locator('textarea#lv-draft').fill('In one sentence, what do I need to film to measure g?'); await p.getByRole('button', { name: 'Send' }).click();
  await p.locator('.lv-msg[data-role=assistant], .lv-msg[data-role=error]').last().waitFor({ timeout: 90000 }); await p.waitForTimeout(800);
  step('agent_turn', (await p.locator('.lv-msgs').innerText()).slice(0, 400)); await shot('3-agent-turn');
  rec.status = 'ok';
} catch (e) { rec.status = 'error'; rec.error = String(e).replace(/\S+@\S+/g, '<email>').slice(0, 400); await shot('error').catch(() => {}); }
rec.end_utc = new Date().toISOString();
fs.writeFileSync(D + 'smoke.json', JSON.stringify(rec, null, 1).replace(/[\w.+-]+@example\.com/g, '<email>'));
await b.close();

