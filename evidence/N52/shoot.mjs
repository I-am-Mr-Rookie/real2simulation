// Headed Chromium; the comparison uses an untouched source frame and the real lab canvas screenshot.
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
const require = createRequire('C:/Users/HP/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/');
const { chromium } = require('playwright-core');
const [base = 'http://localhost:3052', dir = 'evidence/N52/rm02'] = process.argv.slice(2);
const browser = await chromium.launch({ headless: false });
const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
const page = await context.newPage(), errors = [];
page.on('pageerror', e => errors.push(e.message));
await page.goto(base + '/lab');
await page.getByText('Open 3D lab editor', { exact: true }).click();
await page.locator('input[type=file]').first().setInputFiles(path.resolve(dir, 'scene.json'));
await page.getByRole('button', { name: 'Hide inspector and scene JSON', exact: true }).click();
await page.getByRole('button', { name: 'Fit view to the room', exact: true }).click();
await page.waitForTimeout(500);
const canvas = await page.getByTestId('lab-editor-canvas').screenshot();
const source = fs.readFileSync(dir + '/source-view4.png');
const summary = JSON.parse(fs.readFileSync(dir + '/summary.json'));
const chairs = summary.kept.filter(k => k.category === 'chair').length;
const tables = summary.kept.filter(k => ['table', 'desk'].includes(k.category)).length;
const compare = await context.newPage();
await compare.setViewportSize({ width: 1280, height: 640 });
await compare.setContent(`<style>*{box-sizing:border-box}body{margin:0;font:15px system-ui;background:#f4f5f7;color:#17202b}header,footer{padding:12px 18px;height:48px}main{display:grid;grid-template-columns:1fr 1fr;height:544px}section{border:1px solid #ccd2d8;display:flex;flex-direction:column}h2{margin:0;padding:9px 14px;font-size:14px;background:#fff}img{width:100%;height:500px;object-fit:contain}</style>
<header><b>RM02 classroom</b> · RECORDED source versus MODEL-ESTIMATED room shell</header><main>
<section><h2>RECORDED · sampled video frame 4 · Pexels</h2><img src="data:image/png;base64,${source.toString('base64')}"></section>
<section><h2>MODEL-ESTIMATED · scale unverified · SIMULATED physics</h2><img src="data:image/png;base64,${canvas.toString('base64')}"></section></main>
<footer>${tables} separate desk/table proxies · ${chairs} green chair proxies · ${summary.openings.length} projected window frames · Geometry and facing are estimates, not a calibrated scan.</footer>`);
await compare.locator('img').evaluateAll(imgs => Promise.all(imgs.map(img => img.decode())));
await compare.screenshot({ path: dir + '/rm02-side-by-side.jpg', type: 'jpeg', quality: 93 });
fs.writeFileSync(dir + '/browser.json', JSON.stringify({ browser: browser.version(), headless: false, renderOrigin: base, viewport: { width: 1280, height: 640 }, errors }, null, 1));
await browser.close();
