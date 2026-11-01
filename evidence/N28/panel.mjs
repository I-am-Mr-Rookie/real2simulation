// N28 headed Playwright Chromium (never Chrome): public /lab?editor=1 with the real AgentPanel; its /api/workspace/agent/* calls
// are forwarded to a local uvicorn (throwaway local token, owner n28-live) so the 3 turns hit the real Muse Spark model and lab tools.
import { createRequire } from 'module'; import fs from 'fs';
const require = createRequire('C:/Users/HP/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/');
const { chromium } = require('playwright-core');
const D = decodeURIComponent(new URL('.', import.meta.url).pathname.slice(1));
const API = 'http://127.0.0.1:8128', base = 'http://localhost:3028';
const PROMPTS = ['Drop a 5 cm ball from 1.2 m and measure g', 'move the ball 30 cm left and make it 10 cm', 'remove the ramp'];
const OWNER = process.env.OWNER || 'n28-live', TAG = process.env.TAG || '';
const turns = [], scrolls = [];
// REPLAY=<json>: answer /turn from recorded live turns (no model call) so screenshots can be retaken; every other call is forwarded.
const replay = process.env.REPLAY ? JSON.parse(fs.readFileSync(D + process.env.REPLAY, 'utf8')).turns : null;
const b = await chromium.launch({ headless: false });
const ctx = await b.newContext({ viewport: { width: 1280, height: 900 } }); const p = await ctx.newPage();
await p.route('**/api/workspace/agent/**', async (route) => {
  const req = route.request(), path = new URL(req.url()).pathname.replace('/api', '');
  if (replay && path.endsWith('/turn')) { const t = replay[turns.length]; turns.push({ replayed: true, ...t }); return route.fulfill({ json: t }); }
  const r = await route.fetch({ url: API + path, headers: { 'content-type': 'application/json', 'x-workspace-token': 'n28-local-only', 'x-workspace-owner': OWNER } });
  if (path.endsWith('/turn')) { const body = await r.json(); turns.push({ utc: new Date().toISOString(), sent: JSON.parse(req.postData()).text, status: r.status(), ...body }); }
  await route.fulfill({ response: r });
});
try {
  await p.goto(base + '/lab?editor=1');
  await p.getByRole('heading', { name: 'Ask the agent' }).waitFor({ timeout: 60000 });
  await p.getByRole('button', { name: 'Add Ramp' }).click(); // the user built a ramp in the editor before asking
  const input = p.getByLabel('Message to the agent');
  for (const t of PROMPTS) {
    await input.fill(t); await p.getByRole('button', { name: 'Ask', exact: true }).click();
    await p.getByRole('button', { name: 'Working...' }).waitFor({ state: 'detached', timeout: 240000 });
    const m = () => p.locator('.le-log').evaluate((el) => el.scrollHeight - el.clientHeight - el.scrollTop); // 0 = last line in view
    scrolls.push({ t, gap_now: await m(), gap_after_1s: (await p.waitForTimeout(1000), await m()) });
  }
  const panel = p.locator('.le-agent');
  await panel.screenshot({ path: D + TAG + 'panel-desktop.png' }); await p.screenshot({ path: D + TAG + 'editor-desktop.png' });
  const log = p.locator('.le-log');
  const fit = await log.evaluate((el) => ({ scrollTop: el.scrollTop, scrollHeight: el.scrollHeight, clientHeight: el.clientHeight }));
  await p.setViewportSize({ width: 375, height: 812 }); await p.waitForTimeout(800);
  await panel.scrollIntoViewIfNeeded(); await panel.screenshot({ path: D + TAG + 'panel-375.png' }); await p.screenshot({ path: D + TAG + 'viewport-375.png' });
  const sw = await p.evaluate(() => document.documentElement.scrollWidth);
  fs.writeFileSync(D + TAG + 'turns.json', JSON.stringify({ turns, log_scroll_desktop: fit, scrolls, scrollWidth_375: sw, panel_text: await panel.innerText() }, null, 2));
  console.log('ok', JSON.stringify(fit), sw);
} catch (e) { fs.writeFileSync(D + TAG + 'turns.json', JSON.stringify({ error: String(e).slice(0, 500), turns }, null, 2)); await p.screenshot({ path: D + TAG + 'fail.png' }); console.log('FAIL', e.message); }
await b.close();


