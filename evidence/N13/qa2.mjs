// N13 pass 2 (agent chat in the Agent & tools drawer, voice, mode chip, 375 px overflow). Usage: N13_DIR=<clips dir> node qa2.mjs
import { createRequire } from 'module'; import fs from 'fs';
const require = createRequire('C:/Users/HP/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/');
const { chromium } = require('playwright-core');
const base = 'https://web-dev-cd80.up.railway.app', DIR = process.env.N13_DIR; const D = decodeURIComponent(new URL('.', import.meta.url).pathname.slice(1));
const rec = { steps: [], posts: [] };
const b = await chromium.launch({ headless: false, args: ['--use-fake-device-for-media-stream', '--use-fake-ui-for-media-stream', '--use-file-for-fake-audio-capture=' + DIR + '/voice.wav'] });
const ctx = await b.newContext({ viewport: { width: 1280, height: 900 } }); const p = await ctx.newPage(); await ctx.grantPermissions(['microphone'], { origin: base });
p.on('response', async (r) => { const u = new URL(r.url()); if (r.request().method() === 'POST' && /\/api\/workspace\/(agent|voice|transcribe)/.test(u.pathname)) { let t = ''; try { t = (await r.text()).slice(0, 600); } catch {} rec.posts.push({ path: u.pathname, status: r.status(), body: t }); } });
const shot = (n, full = false) => p.screenshot({ path: D + 'p2-' + n + '.png', fullPage: full }).catch(() => {});
const save = () => fs.writeFileSync(D + 'pass2.json', JSON.stringify(rec, null, 1));
async function T(name, fn, to = 120000) { const t0 = Date.now(); let ok = true, note = ''; try { note = String((await Promise.race([fn(), new Promise((_, j) => setTimeout(() => j(new Error('step timeout')), to))])) ?? ''); } catch (e) { ok = false; note = String(e.message || e).split('\n')[0].slice(0, 300); await shot('fail-' + name); }
  rec.steps.push({ name, ok, sec: +((Date.now() - t0) / 1000).toFixed(1), note: note.slice(0, 700) }); console.log(ok ? 'PASS' : 'FAIL', name, note.slice(0, 160)); save(); return ok; }
const email = 'n13-p2-' + Date.now().toString(36) + '+clerk_test@example.com';
await p.goto(base + '/sign-up'); await p.locator('input[name=emailAddress]').fill(email); await p.locator('input[name=emailAddress]').press('Enter');
await p.locator('input[autocomplete=one-time-code], input[name=code]').first().waitFor({ timeout: 90000 }); await p.keyboard.type('424242'); await p.waitForURL((u) => !/sign-up/.test(u.pathname), { timeout: 90000 });
await p.goto(base + '/workspace'); await p.waitForTimeout(3000);
await T('mode_chip_and_settings', async () => { await p.getByRole('button', { name: 'Agent & tools' }).click(); await p.locator('.lv-chat').first().waitFor({ timeout: 15000 }); const chip = p.locator('.lv-chip').first(); const c0 = await chip.innerText(); await chip.click(); await p.waitForTimeout(800); await shot('01-mode-settings'); const t = (await p.locator('.lv-chat').first().innerText()).replace(/\s+/g, ' ');
  return 'chip=' + c0 + ' settings_text=' + t.slice(0, 500); });
await T('close_mode_settings', async () => { await p.locator('.lv-chip').first().click(); return 'ok'; });
const sendChat = async (msg) => { const n = await p.locator('.lv-msg[data-role=assistant]').count(); await p.locator('#lv-draft').fill(msg); await p.locator('.lv-compose').getByRole('button', { name: 'Send' }).click();
  await p.waitForFunction((n) => document.querySelectorAll('.lv-msg[data-role=assistant]').length > n && !/Thinking/.test(document.querySelector('.lv-msgs')?.innerText ?? ''), n, { timeout: 120000 }); return (await p.locator('.lv-msg[data-role=assistant]').last().innerText()).replace(/\s+/g, ' ').slice(0, 600); };
await T('agent_physics_question', async () => { const r = await sendChat('Why does a heavier ball fall at the same rate as a lighter one in air?'); await shot('02-chat-physics'); return r; }, 150000);
await T('agent_offtopic_refuses', async () => { const r = await sendChat('Write me a short poem about my cat and recommend a pizza place in Dhaka.'); await shot('03-chat-offtopic'); return r; }, 150000);
await T('agent_voice_input', async () => { await p.locator('#lv-draft').fill(''); await p.getByRole('button', { name: 'Voice' }).click(); await p.getByRole('button', { name: 'Stop recording' }).waitFor({ timeout: 10000 }); await p.waitForTimeout(6000); await p.getByRole('button', { name: 'Stop recording' }).click();
  await p.waitForFunction(() => !/Transcribing/.test(document.body.innerText), null, { timeout: 60000 }); const err = await p.locator('.lv-compose .ws-error').count() ? await p.locator('.lv-compose .ws-error').innerText() : ''; const d = await p.locator('#lv-draft').inputValue(); await shot('04-voice');
  if (err || !d.trim()) throw new Error('draft="' + d + '" error="' + err + '"'); return 'transcript: ' + d.slice(0, 200); }, 120000);
await T('mobile_375_overflow', async () => { const out = []; for (const path of ['/workspace', '/lab?editor=1', '/library', '/']) { await p.setViewportSize({ width: 375, height: 812 }); await p.goto(base + path); await p.waitForTimeout(2500);
  const m = await p.evaluate(() => ({ sw: document.documentElement.scrollWidth, cw: document.documentElement.clientWidth, wide: [...document.querySelectorAll('body *')].filter((e) => e.getBoundingClientRect().right > innerWidth + 2 && getComputedStyle(e).position !== 'fixed' && !e.closest('[aria-hidden=true], [hidden]')).slice(0, 4).map((e) => e.tagName + '.' + String(e.className).slice(0, 30)) }));
  out.push(path + ' scrollW=' + m.sw + ' clientW=' + m.cw + ' wide=' + m.wide.join(',')); await shot('m' + path.replace(/\W+/g, '_')); } return out.join(' ; '); });
rec.end = new Date().toISOString(); save(); await b.close();
