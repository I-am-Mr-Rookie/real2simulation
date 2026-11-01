// N23 headed Playwright smoke on DEV (from evidence/N11/smoke.mjs). Usage: node evidence/N23/smoke.mjs <ST03 trimmed mp4> <RM02 trimmed mp4>.
// Fresh +clerk_test account, code 424242; no emails written. Paid: one hosted sam-3.1 run, one agent turn, one Modal room job.
import { createRequire } from 'module'; import fs from 'fs'; import path from 'path';
const require = createRequire('C:/Users/HP/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/');
const { chromium } = require('playwright-core');
const base = process.env.BASE || 'https://web-dev-cd80.up.railway.app';
const [ST03, RM02] = process.argv.slice(2);
const AGENT_ONLY = !!process.env.AGENT_ONLY; // rerun only the agent turn (writes smoke-agent.json)
const D = decodeURIComponent(new URL('.', import.meta.url).pathname.slice(1));
const rec = { start_utc: new Date().toISOString(), steps: [], fails: [] };
const step = (k, v = true) => { rec.steps.push({ k, v, utc: new Date().toISOString() }); console.log(k, JSON.stringify(v).slice(0, 300)); };
const b = await chromium.launch({ headless: false });
const ctx = await b.newContext({ viewport: { width: 1280, height: 900 } }); const p = await ctx.newPage();
p.on('response', (r) => { if (r.status() >= 400) rec.fails.push(r.status() + ' ' + new URL(r.url()).pathname.slice(0, 60)); });
const shot = (n) => p.screenshot({ path: D + n + '.png' });
const api = (u, init) => p.evaluate(async ([u, i]) => { const r = await fetch('/api/workspace' + u, i); let body = null; try { body = await r.json(); } catch {} return { status: r.status, body }; }, [u, init]);
const post = (u, body) => api(u, { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(body) });
const upload = async (file) => {
  await p.setInputFiles('#lv-files input[type=file]', file);
  const name = path.basename(file);
  await p.locator('.lv-files li', { hasText: name }).first().waitFor({ timeout: 90000 });
  const fl = (await api('/files')).body; const f = fl.files.find((x) => x.name === name);
  step('uploaded', { name: f.name, size: f.size, dur: f.duration_s, quota: fl.quota.uploads_today }); return f;
};
try {
  const email = 'n23-' + Date.now().toString(36) + '+clerk_test@example.com';
  await p.goto(base + '/sign-up');
  await p.locator('input[name=emailAddress]').fill(email); await p.locator('input[name=emailAddress]').press('Enter');
  await p.locator('input[autocomplete=one-time-code], input[name=code]').first().waitFor({ timeout: 60000 }); await p.keyboard.type('424242');
  await p.waitForURL((u) => !/sign-up/.test(u.pathname), { timeout: 60000 }); step('signed_up');
  if (!/workspace/.test(p.url())) await p.goto(base + '/workspace');
  await p.waitForURL(/workspace\/.+/, { timeout: 60000 });
  await p.getByRole('heading', { name: 'Choose how the agent runs' }).waitFor({ timeout: 60000 });
  await p.getByRole('button', { name: 'Continue' }).click(); await p.locator('.lv-gpu').waitFor({ timeout: 30000 });
  step('rooms_list_empty', await api('/rooms'));
  if (!AGENT_ONLY) {
  // Mode B: trimmed ST03 -> hosted SAM 3.1 tracking -> fit
  const f = await upload(ST03);
  const st = await post('/experiments', { file_id: f.id, target_text: 'apple' });
  step('experiment_started', { status: st.status, state: st.body?.experiment?.status }); const eid = st.body?.experiment?.id; let e;
  for (let i = 0; i < 60; i++) { e = (await api('/experiments/' + eid)).body?.experiment; if (e && !['queued', 'running'].includes(e.status)) break; await p.waitForTimeout(5000); }
  step('experiment_done', { state: e?.status, err: e?.error, fit: e?.result?.status, label: e?.result?.label?.slice(0, 120), quantity: e?.result?.quantity, cost: e?.result?.cost_usd, frames: e?.result?.video_frames_processed });
  }
  // Agent: one paid turn
  if (!(await p.locator('textarea#lv-draft').isVisible())) await p.getByRole('button', { name: 'Agent & tools' }).click();
  await p.locator('textarea#lv-draft').fill('In one sentence, what do I need to film to measure g?'); await p.getByRole('button', { name: 'Send' }).click();
  await p.waitForFunction(() => { const t = document.querySelector('.lv-msgs')?.innerText.trim() ?? ''; return t && !/Thinking$/.test(t) && !/\?$/.test(t); }, null, { timeout: 120000 }); await p.waitForTimeout(800);
  step('agent_turn', (await p.locator('.lv-msgs').innerText()).slice(0, 500)); await shot('1-experiment-and-agent');
  if (AGENT_ONLY) throw 'done';
  // Mode A: trimmed RM02 -> Modal MapAnything room job
  const rf = await upload(RM02);
  const rs = await post('/rooms', { file_id: rf.id });
  step('room_started', { status: rs.status, state: rs.body?.job?.state }); const rid = rs.body?.job?.job_id; let r;
  for (let i = 0; i < 120; i++) { r = (await api('/rooms/' + rid)).body?.job; if (r && ['done', 'failed'].includes(r.state)) break; await p.waitForTimeout(5000); }
  step('room_done', r);
  const res = r?.state === 'done' ? await api('/rooms/' + rid + '/result') : null;
  step('room_result', res && { status: res.status, scene: res.body?.scene?.version, objects: res.body?.scene?.objects?.length, scale: res.body?.room?.scale });
  const rl = await api('/rooms'); step('rooms_list', { status: rl.status, n: rl.body?.rooms?.length, first: rl.body?.rooms?.[0]?.id === rid });
  await p.reload(); await p.locator('#lv-jobs').waitFor({ timeout: 30000 }).catch(() => {}); await p.waitForTimeout(2000); await shot('2-processing-card');
  rec.status = 'ok';
} catch (e) { if (e === 'done') rec.status = 'ok'; else { rec.status = 'error'; rec.error = String(e).replace(/\S+@\S+/g, '<email>').slice(0, 400); await shot('error').catch(() => {}); } }
rec.end_utc = new Date().toISOString();
fs.writeFileSync(D + (AGENT_ONLY ? 'smoke-agent.json' : 'smoke.json'), JSON.stringify(rec, null, 1).replace(/[\w.+-]+@example\.com/g, '<email>'));
await b.close();
