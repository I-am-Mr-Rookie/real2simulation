// N10 screenshots: headed Playwright Chromium (ms-playwright cache) over raw CDP; no new dependency.
// Usage: node evidence/N10/shoot.mjs http://127.0.0.1:3110   (CHROME_BIN overrides the browser path)
import { spawn } from 'node:child_process';
import { readdir, writeFile, mkdtemp } from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import { fileURLToPath } from 'node:url';

const BASE = process.argv[2] ?? 'http://127.0.0.1:3110';
const OUT = path.dirname(fileURLToPath(import.meta.url));
const pw = path.join(process.env.LOCALAPPDATA, 'ms-playwright');
const dir = (await readdir(pw)).filter((d) => /^chromium-\d+$/.test(d)).sort().at(-1);
const sub = (await readdir(path.join(pw, dir))).find((d) => d.startsWith('chrome-win'));
const bin = process.env.CHROME_BIN ?? path.join(pw, dir, sub, 'chrome.exe');
const profile = await mkdtemp(path.join(os.tmpdir(), 'n10-'));
const proc = spawn(bin, ['--remote-debugging-port=9333', '--user-data-dir=' + profile, '--no-first-run', '--window-size=1400,1000', 'about:blank'], { stdio: 'ignore' });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
let targets;
for (let i = 0; i < 50 && !targets; i++) { await sleep(200); targets = await fetch('http://127.0.0.1:9333/json').then((r) => r.json()).catch(() => null); }
const page = targets.find((t) => t.type === 'page');
const ws = new WebSocket(page.webSocketDebuggerUrl);
await new Promise((r) => ws.addEventListener('open', r));
let id = 0; const wait = new Map(); const logs = [];
ws.addEventListener('message', (e) => { const m = JSON.parse(e.data); if (m.id) wait.get(m.id)?.(m); if (m.method === 'Runtime.exceptionThrown' || (m.method === 'Runtime.consoleAPICalled' && m.params.type === 'error')) logs.push(JSON.stringify(m.params).slice(0, 300)); });
const cdp = (method, params = {}) => new Promise((r) => { const i = ++id; wait.set(i, r); ws.send(JSON.stringify({ id: i, method, params })); });
const js = async (expr) => (await cdp('Runtime.evaluate', { expression: expr, awaitPromise: true, returnByValue: true })).result?.result?.value;
const click = (label) => js('(() => { const b = [...document.querySelectorAll("button")].find((x) => x.textContent.trim() === ' + JSON.stringify(label) + '); if (!b) return "missing"; b.click(); return "ok"; })()');
await cdp('Runtime.enable'); await cdp('Page.enable');
const results = {};
for (const [name, w, h, mobile] of [['desktop', 1280, 900, false], ['375', 375, 812, true]]) {
  await cdp('Emulation.setDeviceMetricsOverride', { width: w, height: h, deviceScaleFactor: mobile ? 2 : 1, mobile });
  await cdp('Page.navigate', { url: BASE + '/lab?editor=1' });
  for (let i = 0; i < 60 && !(await js('!!document.querySelector("[data-testid=lab-editor-canvas] canvas")')); i++) await sleep(250);
  for (const k of ['+ Ramp', '+ Ball', '+ Pendulum', '+ Spring', '+ Block']) await click(k);
  await sleep(300);
  await click('Play');
  for (let i = 0; i < 40 && (await js('!document.querySelector(".le-status")?.textContent.startsWith("Running")')); i++) await sleep(250);
  await sleep(900);
  await click('Pause');
  await sleep(300);
  const info = await js('({ status: document.querySelector(".le-status")?.textContent, time: document.querySelector(".le-time")?.textContent, scrollW: document.documentElement.scrollWidth, objects: JSON.parse(document.querySelector("textarea").value).objects.length })');
  results[name] = info;
  const shot = await cdp('Page.captureScreenshot', { format: 'png', captureBeyondViewport: false });
  await writeFile(path.join(OUT, 'lab-editor-' + name + '.png'), Buffer.from(shot.result.data, 'base64'));
}
results.console_errors = logs;
await writeFile(path.join(OUT, 'screenshots.json'), JSON.stringify(results, null, 2));
console.log(JSON.stringify(results, null, 2));
ws.close(); proc.kill();

