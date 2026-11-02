
// N44: sign in as the N43 Clerk test account (headed Playwright Chromium) and save RM02 room.ply/result (Pexels room; private dir, not committed).
import { createRequire } from 'module'; import fs from 'fs';
const require = createRequire('C:/Users/HP/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/');
const { chromium } = require('playwright-core');
const base = 'https://web-dev-cd80.up.railway.app', id = '82f05b85de1748b3bd91003122b8e70d';
const out = process.argv[2]; fs.mkdirSync(out, { recursive: true });
const b = await chromium.launch({ headless: false }); const p = await (await b.newContext({ viewport: { width: 1280, height: 900 } })).newPage();
await p.goto(base + '/sign-in');
const f = p.locator('input[name=identifier], input[name=emailAddress]').first(); await f.waitFor({ timeout: 60000 });
await f.fill('n43-mvym1kik+clerk_test@example.com'); await f.press('Enter');
await p.locator('input[autocomplete=one-time-code], input[name=code]').first().waitFor({ timeout: 90000 }); await p.keyboard.type('424242');
await p.waitForURL((u) => !/sign-in/.test(u.pathname), { timeout: 90000 });
await p.goto(base + '/workspace'); await p.waitForTimeout(4000);
const get = (path) => p.evaluate(async (u) => { const r = await fetch(u, { cache: 'no-store' }); return { status: r.status, body: await r.text() }; }, base + path);
for (const [name, path] of [['room.ply', '/api/workspace/rooms/' + id + '/room.ply'], ['result.json', '/api/workspace/rooms/' + id + '/result']]) {
  const r = await get(path); console.log(name, r.status, r.body.length); if (r.status === 200) fs.writeFileSync(out + '/' + name, r.body);
}
await b.close();

