// N13 end-to-end QA on DEV. Usage: ACC=1|2|3 N13_DIR=<clips dir> node evidence/N13/qa.mjs  (clips are Pexels, not committed)
import { createRequire } from 'module'; import fs from 'fs';
const require = createRequire('C:/Users/HP/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/');
const { chromium } = require('playwright-core');
const base = 'https://web-dev-cd80.up.railway.app', DIR = process.env.N13_DIR, ACC = process.env.ACC || '1';
const D = decodeURIComponent(new URL('.', import.meta.url).pathname.slice(1));
const rec = { acc: ACC, start_utc: new Date().toISOString(), steps: [], fails: [], posts: [], gpu: [], notes: {} };
const log = (...a) => console.log('[a' + ACC + ']', ...a);
const b = await chromium.launch({ headless: false, args: ['--use-fake-device-for-media-stream', '--use-fake-ui-for-media-stream', '--use-file-for-fake-audio-capture=' + DIR + '/voice.wav'] });
const ctx = await b.newContext({ viewport: { width: 1280, height: 900 } }); const p = await ctx.newPage();
await ctx.grantPermissions(['clipboard-read', 'clipboard-write', 'microphone'], { origin: base });
p.on('dialog', (d) => d.accept().catch(() => {}));
p.on('response', async (r) => {
  const u = new URL(r.url()), m = r.request().method();
  if (r.status() >= 400) rec.fails.push(r.status() + ' ' + m + ' ' + u.pathname.slice(0, 80));
  if (m === 'POST' && /\/api\/workspace\//.test(u.pathname) && !/\/files$/.test(u.pathname)) { let t = ''; try { t = (await r.text()).slice(0, 700); } catch {} rec.posts.push({ utc: new Date().toISOString(), path: u.pathname, status: r.status(), body: t }); }
});
const shot = (n, full = false) => p.screenshot({ path: D + 'a' + ACC + '-' + n + '.png', fullPage: full }).catch(() => {});
const narrow = async (n, fn) => { await p.setViewportSize({ width: 375, height: 812 }); await p.waitForTimeout(500); if (fn) await fn().catch(() => {}); await shot('m-' + n, true); await p.setViewportSize({ width: 1280, height: 900 }); await p.waitForTimeout(300); };
const save = () => fs.writeFileSync(D + 'acc' + ACC + '.json', JSON.stringify(rec, null, 1));
// T: run a step, record pass/fail, seconds, a short note; a failure does not stop later steps.
async function T(name, fn, to = 120000) {
  const t0 = Date.now(); let ok = true, note = '';
  try { note = String((await Promise.race([fn(), new Promise((_, j) => setTimeout(() => j(new Error('step timeout ' + to + ' ms')), to))])) ?? ''); }
  catch (e) { ok = false; note = String(e.message || e).split('\n')[0].slice(0, 300); await shot('fail-' + name.replace(/\W+/g, '_')); }
  const s = { name, ok, sec: +((Date.now() - t0) / 1000).toFixed(1), note: note.slice(0, 600) }; rec.steps.push(s); log(ok ? 'PASS' : 'FAIL', name, s.sec + 's', note.slice(0, 140)); save(); return ok;
}
let sampling = true;
(async () => { while (sampling) { try { const g = await p.evaluate(() => { const e = document.querySelector('.lv-gpu'); return e ? e.dataset.tone + '|' + e.innerText.replace(/\s+/g, ' ').slice(0, 80) : null; }); if (g && rec.gpu.at(-1)?.v !== g) rec.gpu.push({ utc: new Date().toISOString(), v: g }); } catch {} await new Promise((r) => setTimeout(r, 2000)); } })();
const txt = (sel) => p.locator(sel).first().innerText();
const email = 'n13-a' + ACC + '-' + Date.now().toString(36) + '+clerk_test@example.com';
let wsUrl;
const jobsDone = (n) => p.waitForFunction((n) => [...document.querySelectorAll('#lv-jobs .lv-jobcard')].filter((e) => ['done', 'failed', 'error'].includes(e.dataset.state)).length >= n, n, { timeout: 240000, polling: 1000 });
const uploadAndWait = async (file, name) => { await p.setInputFiles('#lv-files input[type=file]', file); const row = p.locator('.lv-files > li', { hasText: name }).first(); await row.waitFor({ timeout: 150000 }); return row; };
try {
  await T('signup', async () => {
    await p.goto(base + '/sign-up');
    await p.locator('input[name=emailAddress]').fill(email); await p.locator('input[name=emailAddress]').press('Enter');
    await p.locator('input[autocomplete=one-time-code], input[name=code]').first().waitFor({ timeout: 90000 }); await p.keyboard.type('424242');
    await p.waitForURL((u) => !/sign-up/.test(u.pathname), { timeout: 90000 });
  });
  await T('contributor_screen', async () => {
    if (!/workspace/.test(p.url())) await p.goto(base + '/workspace');
    await p.getByRole('heading', { name: 'Choose how the agent runs' }).waitFor({ timeout: 90000 });
    const t = await p.locator('main, body').first().innerText(); await shot('01-contributor');
    const pros = /cheaper|contributor/i.test(t) && /train/i.test(t);
    if (ACC === '2') { await p.getByText(/Contributor/i).first().click().catch(() => {}); }
    await p.getByRole('button', { name: 'Continue' }).click(); wsUrl = p.url();
    await p.locator('.lv-chip').first().waitFor({ timeout: 30000 });
    return 'pros_and_cons_text=' + pros + ' chip=' + await txt('.lv-chip');
  });
  await T('sample_project_visible', async () => {
    await p.waitForTimeout(1500); const t = await p.locator('body').innerText(); await shot('02-workspace-first');
    const m = t.match(/.{0,40}sample.{0,60}/i); if (!m) throw new Error('no SAMPLE project text anywhere on /workspace'); return m[0].replace(/\s+/g, ' ');
  });
  await T('gpu_dot_present', async () => { const e = p.locator('.lv-gpu').first(); await e.waitFor({ timeout: 15000 }); return await e.getAttribute('data-tone') + ' ' + await e.innerText(); });
  // ---------- Mode B
  await T('new_project_question_card', async () => {
    await p.getByRole('button', { name: 'New project' }).click();
    const q = await p.locator('.lv-q').last(); await q.waitFor({ timeout: 30000 }); const qt = await q.innerText(); await shot('03-question-card');
    await p.locator('.lv-q .r2s-qopt', { hasText: 'My experiment' }).last().click(); await p.locator('.lv-q button[type=submit]').last().click();
    await p.getByText('Filming tips for my experiment:').last().waitFor({ timeout: 30000 }); return qt.replace(/\s+/g, ' ').slice(0, 200);
  });
  let row;
  await T('upload_st03', async () => { row = await uploadAndWait(DIR + '/ST03-trim.mp4', 'ST03-trim.mp4'); return await row.innerText().then((x) => x.replace(/\s+/g, ' ')); });
  const openMeasure = async () => { const btn = p.locator('.lv-files > li', { hasText: 'ST03-trim.mp4' }).first().getByRole('button', { name: 'Measure this experiment' }); if ((await btn.getAttribute('aria-expanded')) !== 'true') await btn.click(); await p.waitForFunction(() => document.querySelector('.lv-still video')?.readyState >= 2, null, { timeout: 30000 }); };
  let nJobs = 0;
  await T('modeB1_click_no_size', async () => {
    await openMeasure(); const v = p.locator('.lv-still video'); const bb = await v.boundingBox(); await v.click({ position: { x: bb.width * 0.5, y: bb.height * 0.3 } });
    await shot('04-b1-click'); await p.getByRole('button', { name: 'Start measuring' }).click(); const t0 = Date.now();
    await p.locator('#lv-jobs .lv-jobcard').first().waitFor({ timeout: 20000 }); await shot('05-b1-progress');
    await jobsDone(++nJobs); await shot('06-b1-result', true); const c = p.locator('#lv-jobs .lv-jobcard').first();
    return ((Date.now() - t0) / 1000).toFixed(0) + 's job: ' + (await c.innerText()).replace(/\s+/g, ' ').slice(0, 420);
  }, 280000);
  await T('modeB1_fit_band_and_labels', async () => { const c = p.locator('#lv-jobs .lv-jobcard').first(); const band = await c.locator('.lv-band').count(), curve = await c.locator('.lv-curve').count(), pts = await c.locator('.lv-pt').count();
    const t = await c.innerText(); if (!band || !curve || !pts) throw new Error('chart parts band=' + band + ' curve=' + curve + ' pts=' + pts); return 'band=' + band + ' pts=' + pts + ' scale_unverified=' + /scale unverified/i.test(t) + ' em_dash=' + /\u2014/.test(t); });
  await narrow('b1-result', () => p.locator('#lv-jobs').scrollIntoViewIfNeeded());
  await T('modeB2_typed_name_known_size', async () => {
    await openMeasure(); await p.getByLabel('Or its name').fill('apple');
    await p.getByLabel('What it is').fill('apple width'); await p.getByLabel('Value').fill('8'); await p.getByLabel('Unit').selectOption('cm'); await shot('07-b2-form');
    await p.getByRole('button', { name: 'Start measuring' }).click(); const t0 = Date.now(); await jobsDone(++nJobs); await shot('08-b2-result', true);
    const c = p.locator('#lv-jobs .lv-jobcard').first(); return ((Date.now() - t0) / 1000).toFixed(0) + 's job: ' + (await c.innerText()).replace(/\s+/g, ' ').slice(0, 420);
  }, 280000);
  let shareUrl;
  await T('share_link', async () => {
    const c = p.locator('#lv-jobs .lv-jobcard').first(); await c.getByRole('button', { name: 'Share as Guess the Gravity' }).click();
    const inp = c.getByLabel('Challenge link'); await inp.waitFor({ timeout: 20000 }); shareUrl = await inp.inputValue(); return shareUrl.replace(/\/[^/]+$/, '/<token>');
  });
  await T('share_logged_out_open', async () => {
    const c2 = await b.newContext({ viewport: { width: 1280, height: 900 } }); const q = await c2.newPage(); await q.goto(shareUrl);
    await q.getByText('Guess the Gravity').first().waitFor({ timeout: 40000 }); await q.screenshot({ path: D + 'a' + ACC + '-09-guess-public.png' }); const body = (await q.locator('body').innerText()).replace(/\s+/g, ' ');
    await q.setViewportSize({ width: 375, height: 812 }); await q.screenshot({ path: D + 'a' + ACC + '-m-guess-public.png', fullPage: true }); await c2.close();
    return 'leaks_answer_before_guess=' + /2\.\d+ ?\+/.test(body) + ' text=' + body.slice(0, 200);
  });
  await T('share_revoke', async () => {
    const c = p.locator('#lv-jobs .lv-jobcard').first(); await c.getByRole('button', { name: 'Revoke' }).click(); await c.getByText('Link revoked.').waitFor({ timeout: 15000 });
    const c2 = await b.newContext(); const q = await c2.newPage(); const r = await q.goto(shareUrl); await q.waitForTimeout(2000); const body = (await q.locator('body').innerText()).replace(/\s+/g, ' ').slice(0, 160); await q.screenshot({ path: D + 'a' + ACC + '-10-guess-revoked.png' }); await c2.close();
    return 'http=' + r.status() + ' ' + body;
  });
  await T('redo_in_3d', async () => {
    await p.locator('#lv-jobs .lv-jobcard').first().getByRole('link', { name: '3D replay, redo with changes' }).click();
    await p.getByText('Dots and line: your measured track').waitFor({ timeout: 90000 }); const st = await txt('.le-status');
    await p.getByRole('button', { name: 'Play' }).click(); await p.waitForTimeout(2000); await shot('11-redo-lab'); const tm = await txt('.le-time');
    return st.replace(/\s+/g, ' ') + ' | time ' + tm;
  });
  await narrow('redo-lab');
  // ---------- Mode A
  await p.goto(wsUrl).catch(() => {});
  await T('modeA_new_project_upload', async () => {
    await p.getByRole('button', { name: 'New project' }).click();
    await p.locator('.lv-q .r2s-qopt', { hasText: 'Room video' }).last().click(); await p.locator('.lv-q button[type=submit]').last().click();
    await p.getByText('Filming tips for room video:').last().waitFor({ timeout: 30000 });
    await uploadAndWait(DIR + '/RM02-trim.mp4', 'RM02-trim.mp4'); return 'ok';
  });
  let roomHref;
  await T('modeA_build_lab', async () => {
    const before = await p.locator('#lv-jobs .lv-jobcard').count();
    await p.locator('.lv-files > li', { hasText: 'RM02-trim.mp4' }).first().getByRole('button', { name: 'Build my lab' }).click(); const t0 = Date.now();
    const card = p.locator('#lv-jobs .lv-jobcard', { hasText: 'Room lab' }).first(); await card.waitFor({ timeout: 30000 }); await p.waitForTimeout(3000); await shot('12-a-progress');
    await card.getByRole('link', { name: 'Open my lab' }).waitFor({ timeout: 420000 }); roomHref = await card.getByRole('link', { name: 'Open my lab' }).getAttribute('href');
    return ((Date.now() - t0) / 1000).toFixed(0) + 's ' + (await card.innerText()).replace(/\s+/g, ' ').slice(0, 300);
  }, 450000);
  await narrow('a-job', () => p.locator('#lv-jobs').scrollIntoViewIfNeeded());
  await T('modeA_open_editor', async () => {
    await p.locator('#lv-jobs .lv-jobcard', { hasText: 'Room lab' }).first().getByRole('link', { name: 'Open my lab' }).click();
    await p.getByText(/Your room: \d+ points/).waitFor({ timeout: 90000 }); await p.waitForTimeout(1500); await shot('13-a-lab'); return await txt('.le-status');
  }, 120000);
  await narrow('a-lab');
  const img = p.locator('.le-view img');
  await T('A4_click_wiring', async () => {
    await p.getByLabel('View').selectOption('4'); await p.waitForFunction(() => document.querySelector('.le-view img')?.complete && document.querySelector('.le-view img').naturalWidth > 0, null, { timeout: 30000 });
    const nat = await img.evaluate((e) => [e.naturalWidth, e.naturalHeight, e.clientWidth, e.clientHeight]); const at = (r, c) => ({ x: (c * nat[2]) / nat[0], y: (r * nat[3]) / nat[1] });
    await p.getByRole('button', { name: 'Mark the A4 sheet' }).click(); await img.click({ position: at(250, 200), force: true }); await img.click({ position: at(250, 260), force: true });
    await p.getByText(/A4 scale applied|Not applied/).waitFor({ timeout: 60000 }); await shot('14-a4');
    return 'RM02 has no A4 sheet (wiring only): ' + (await txt('.le-status')).replace(/\s+/g, ' ');
  }, 120000);
  await T('add_real_object', async () => {
    await p.getByLabel('View').selectOption('4'); await p.waitForTimeout(1000);
    const nat = await img.evaluate((e) => [e.naturalWidth, e.naturalHeight, e.clientWidth, e.clientHeight]); const at = (r, c) => ({ x: (c * nat[2]) / nat[0], y: (r * nat[3]) / nat[1] });
    await p.getByRole('button', { name: 'Add a real object' }).click(); await img.click({ position: at(215, 320), force: true });
    await p.getByText(/Added room-object|Not applied/).first().waitFor({ timeout: 90000 }); await shot('15-object', true); const s = await txt('.le-status'); if (/Not applied/.test(s)) throw new Error(s); return s.replace(/\s+/g, ' ');
  }, 120000);
  const askEditor = async (msg) => { const n = await p.locator('.le-log p').count(); await p.getByLabel('Message to the agent').fill(msg); await p.getByRole('button', { name: 'Ask', exact: true }).click();
    await p.waitForFunction((n) => document.querySelectorAll('.le-log p').length >= n + 2 && !/Working/.test(document.querySelector('.le-agent')?.innerText ?? ''), n, { timeout: 120000 }); return (await p.locator('.le-log p').allInnerTexts()).slice(-1)[0].replace(/\s+/g, ' ').slice(0, 500); };
  await T('agent_editor_drop_ball_measure_g', async () => { const r = await askEditor('Drop a 5 cm ball from 1.2 m and measure g'); await shot('16-agent-drop', true); return r; }, 150000);
  await narrow('agent-editor');
  // ---------- workspace agent chat
  await p.goto(wsUrl).catch(() => {});
  await p.locator('.lv-chat').first().waitFor({ timeout: 30000 }).catch(() => {});
  const sendChat = async (msg) => { const n = await p.locator('.lv-msg[data-role=assistant]').count(); await p.locator('#lv-draft').fill(msg); await p.locator('.lv-compose').getByRole('button', { name: 'Send' }).click();
    await p.waitForFunction((n) => document.querySelectorAll('.lv-msg[data-role=assistant]').length > n && !/Thinking/.test(document.querySelector('.lv-msgs')?.innerText ?? ''), n, { timeout: 120000 }); return (await p.locator('.lv-msg[data-role=assistant]').last().innerText()).replace(/\s+/g, ' ').slice(0, 500); };
  await T('agent_physics_question', async () => { const r = await sendChat('Why does a heavier ball fall at the same rate as a lighter one in air?'); await shot('17-chat-physics'); return r; }, 150000);
  await T('agent_offtopic_refuses', async () => { const r = await sendChat('Write me a short poem about my cat and recommend a pizza place in Dhaka.'); await shot('18-chat-offtopic'); return r; }, 150000);
  await T('agent_voice_input', async () => {
    await p.locator('#lv-draft').fill(''); await p.getByRole('button', { name: 'Voice' }).click(); await p.getByRole('button', { name: 'Stop recording' }).waitFor({ timeout: 10000 }); await p.waitForTimeout(6000); await p.getByRole('button', { name: 'Stop recording' }).click();
    await p.waitForFunction(() => !/Transcribing/.test(document.body.innerText), null, { timeout: 60000 }); const err = await p.locator('.lv-compose .ws-error').count() ? await p.locator('.lv-compose .ws-error').innerText() : ''; const d = await p.locator('#lv-draft').inputValue(); await shot('19-voice');
    if (err || !d.trim()) throw new Error('draft="' + d + '" error="' + err + '"'); return 'transcript: ' + d.slice(0, 200);
  }, 120000);
  await narrow('workspace-chat');
  // ---------- files
  await T('files_preview', async () => { await p.locator('.lv-files > li').first().getByRole('button', { name: 'Preview' }).click(); const v = p.locator('.lv-files video.lv-video').first(); await v.waitFor({ timeout: 20000 });
    await p.waitForFunction(() => { const e = document.querySelector('.lv-files video.lv-video'); return e && e.readyState >= 2 && e.videoWidth > 0; }, null, { timeout: 30000 }); await shot('20-preview'); return 'video ' + await v.evaluate((e) => e.videoWidth + 'x' + e.videoHeight + ' ' + e.duration.toFixed(1) + 's'); });
  await T('files_download', async () => { const [dl] = await Promise.all([p.waitForEvent('download', { timeout: 30000 }), p.locator('.lv-files > li').first().getByRole('link', { name: 'Download' }).click()]); const path = D + 'tmp-dl-' + ACC; await dl.saveAs(path); const sz = fs.statSync(path).size; fs.unlinkSync(path); return dl.suggestedFilename() + ' ' + sz + ' bytes'; });
  const quota = async () => (await p.locator('.lv-quota p').first().innerText().catch(() => 'n/a')).replace(/\s+/g, ' ');
  rec.notes.quota_before_delete = await quota();
  if (ACC === '1') await T('upload_25mb', async () => {
    const t0 = Date.now(); await p.setInputFiles('#lv-files input[type=file]', DIR + '/RM02-25mb.mp4');
    await p.waitForFunction(() => [...document.querySelectorAll('.lv-files > li')].some((e) => /RM02-25mb/.test(e.innerText)) || document.querySelector('.lv-up .ws-error'), null, { timeout: 200000 });
    const er = await p.locator('.lv-up .ws-error').count() ? await p.locator('.lv-up .ws-error').innerText() : ''; await shot('21-25mb'); if (er) throw new Error(er); return ((Date.now() - t0) / 1000).toFixed(0) + 's; quota ' + await quota();
  }, 220000);
  await T('files_delete', async () => { const n = await p.locator('.lv-files > li').count(); await p.locator('.lv-files > li').first().getByRole('button', { name: 'Delete' }).click(); await p.waitForFunction((n) => document.querySelectorAll('.lv-files > li').length < n, n, { timeout: 30000 }); const after = await quota(); await shot('22-after-delete'); return 'quota ' + rec.notes.quota_before_delete + ' -> ' + after; });
  await narrow('files', () => p.locator('#lv-files').scrollIntoViewIfNeeded());
  if (ACC === '3') await T('over_quota_21st_upload', async () => {
    let n = 0, err = ''; const res = [];
    for (let i = 1; i <= 24 && !err; i++) {
      const nm = 'tiny-' + i + '.mp4'; fs.copyFileSync(DIR + '/tiny.mp4', DIR + '/' + nm);
      await p.setInputFiles('#lv-files input[type=file]', DIR + '/' + nm);
      await p.waitForFunction((nm) => [...document.querySelectorAll('.lv-files > li')].some((e) => e.innerText.includes(nm)) || document.querySelector('.lv-up .ws-error'), nm, { timeout: 60000 });
      err = await p.locator('.lv-up .ws-error').count() ? await p.locator('.lv-up .ws-error').innerText() : ''; if (!err) n++;
    }
    await shot('23-quota-limit'); rec.notes.tiny_uploads_ok = n; return 'successful tiny uploads=' + n + ' (plus earlier uploads on this account: st03, rm02 = 2, deleted 1) first error="' + err + '" quota ' + await quota();
  }, 400000);
  await T('mobile_375_workspace_top', async () => { await p.goto(wsUrl); await p.waitForTimeout(2000); await narrow('workspace-top'); return 'shot'; });
} catch (e) { log('fatal', e.message); }
sampling = false; rec.end_utc = new Date().toISOString(); save(); await b.close();
