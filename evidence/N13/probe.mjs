// N13 isolation probe: fresh account lists experiments and tries to read other accounts' experiment, file, room ids. Usage: node probe.mjs (reads acc1..3.json)
import { createRequire } from 'module'; import fs from 'fs';
const require = createRequire('C:/Users/HP/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/');
const { chromium } = require('playwright-core');
const base = 'https://web-dev-cd80.up.railway.app'; const D = decodeURIComponent(new URL('.', import.meta.url).pathname.slice(1));
const ids = []; for (const a of [1, 2, 3]) { try { const j = JSON.parse(fs.readFileSync(D + 'acc' + a + '.json', 'utf8')); for (const x of j.posts) { const m = x.body.match(/"experiment":\{"id":"(\w+)"/) || x.body.match(/"room":\{"id":"(\w+)"/); if (m) ids.push({ acc: a, path: x.path, id: m[1] }); } } catch {} }
const b = await chromium.launch({ headless: false }); const ctx = await b.newContext({ viewport: { width: 1280, height: 900 } }); const p = await ctx.newPage();
const out = { ids_seen_own_accounts: ids.length, steps: [] };
await p.goto(base + '/sign-up'); const email = 'n13-probe-' + Date.now().toString(36) + '+clerk_test@example.com';
await p.locator('input[name=emailAddress]').fill(email); await p.locator('input[name=emailAddress]').press('Enter');
await p.locator('input[autocomplete=one-time-code], input[name=code]').first().waitFor({ timeout: 90000 }); await p.keyboard.type('424242'); await p.waitForURL((u) => !/sign-up/.test(u.pathname), { timeout: 90000 });
await p.goto(base + '/workspace'); await p.waitForTimeout(4000);
const get = (path) => p.evaluate(async (u) => { const r = await fetch(u, { cache: 'no-store' }); const t = await r.text(); return { status: r.status, body: t.slice(0, 400) }; }, base + path);
out.list_experiments = await get('/api/workspace/experiments'); out.list_rooms = await get('/api/workspace/rooms'); out.list_files = await get('/api/workspace/files'); out.list_projects = await get('/api/workspace/projects');
out.cross = [];
for (const x of ids) { const kind = x.path.includes('rooms') ? 'rooms' : 'experiments'; const r = await get('/api/workspace/' + kind + '/' + x.id); out.cross.push({ from_acc: x.acc, kind, status: r.status, body: r.body.slice(0, 120) }); }
await p.screenshot({ path: D + 'probe-fresh-account.png' }); fs.writeFileSync(D + 'probe.json', JSON.stringify(out, null, 1)); await b.close();
