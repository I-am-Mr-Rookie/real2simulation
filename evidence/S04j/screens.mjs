// S04j evidence: headless Edge (never Chrome UI) over CDP; logged-out /library desktop + 375px, replays opened.
import { spawn } from 'node:child_process';
import { writeFile, mkdtemp } from 'node:fs/promises';
import os from 'node:os'; import path from 'node:path'; import { fileURLToPath } from 'node:url';
const EDGE = 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe', BASE = process.argv[2] || 'http://localhost:3417';
const out = path.dirname(fileURLToPath(import.meta.url));
const dir = await mkdtemp(path.join(os.tmpdir(), 's04j-'));
const edge = spawn(EDGE, ['--headless=new', '--remote-debugging-port=9333', '--user-data-dir=' + dir, 'about:blank'], { stdio: 'ignore' });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
let targets; for (let i = 0; i < 160 && !targets?.some((t) => t.type === 'page'); i++) { await sleep(250); try { targets = await (await fetch('http://127.0.0.1:9333/json')).json(); } catch {} }
const ws = new WebSocket(targets.find((t) => t.type === 'page').webSocketDebuggerUrl); await new Promise((r) => ws.onopen = r);
let id = 0; const pending = new Map(); ws.onmessage = (m) => { const d = JSON.parse(m.data); pending.get(d.id)?.(d); };
const cdp = (method, params = {}) => new Promise((r) => { pending.set(++id, r); ws.send(JSON.stringify({ id, method, params })); });
const evalJs = async (expression) => (await cdp('Runtime.evaluate', { expression, awaitPromise: true, returnByValue: true })).result?.result?.value;
const report = {};
for (const [name, width] of [['desktop', 1280], ['mobile-375', 375]]) {
  await cdp('Emulation.setDeviceMetricsOverride', { width, height: 900, deviceScaleFactor: 1, mobile: width < 500 });
  await cdp('Page.navigate', { url: BASE + '/library' });
  for (let i = 0; i < 120 && !(await evalJs('document.querySelectorAll(".library-card").length')); i++) await sleep(250);
  await evalJs('[...document.querySelectorAll(".library-card button")].forEach((b) => b.click())');
  for (let i = 0; i < 120 && (await evalJs('document.querySelectorAll("[data-slot=viewer][data-state=ready]").length')) < 2; i++) await sleep(250);
  report[name] = await evalJs(`({cards: document.querySelectorAll('.library-card').length,
    labels: [...document.querySelectorAll('.library-card')].map((c) => c.dataset.label + '/' + c.dataset.availability),
    replays: [...document.querySelectorAll('[data-slot=viewer]')].map((v) => v.dataset.state),
    overflowX: document.documentElement.scrollWidth > innerWidth, mysteryAnswerShown: /true_g|answer\s*[:=]/i.test(document.body.innerText)})`);
  const h = await evalJs('document.documentElement.scrollHeight');
  const shot = await cdp('Page.captureScreenshot', { format: 'png', captureBeyondViewport: true, clip: { x: 0, y: 0, width, height: Math.min(h, 6000), scale: 1 } });
  await writeFile(path.join(out, name + '.png'), Buffer.from(shot.result.data, 'base64'));
}
await writeFile(path.join(out, 'screens.json'), JSON.stringify(report, null, 2)); console.log(JSON.stringify(report));
ws.close(); edge.kill();
