// N49: headed Playwright Chromium, local /lab, import a room shell scene.json, 1280 px screenshot (canvas + full page).
import { createRequire } from 'module'; import fs from 'fs';
const require = createRequire('C:/Users/HP/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/');
const { chromium } = require('playwright-core');
const [base, out, scene, name] = process.argv.slice(2);
fs.mkdirSync(out, { recursive: true });
const b = await chromium.launch({ headless: false });
const p = await (await b.newContext({ viewport: { width: 1280, height: 900 } })).newPage(); const errors = [];
p.on('pageerror', (e) => errors.push(e.message));
await p.goto(base + '/lab'); await p.waitForTimeout(3000); await p.getByText('Open 3D lab editor').first().click(); await p.waitForTimeout(4000);
await p.locator('input[type=file]').first().setInputFiles(scene); await p.waitForTimeout(3000);
const c = p.getByTestId('lab-editor-canvas');
await c.screenshot({ path: out + '/' + name + '-canvas.png' });
await p.screenshot({ path: out + '/' + name + '-page.png' });
const msg = await p.locator('body').innerText();
fs.writeFileSync(out + '/' + name + '-browser.json', JSON.stringify({ errors, scrollWidth: await p.evaluate(() => document.documentElement.scrollWidth), rawScanToggle: msg.includes('Show raw scan') }, null, 1));
console.log(JSON.stringify({ errors })); await b.close();

