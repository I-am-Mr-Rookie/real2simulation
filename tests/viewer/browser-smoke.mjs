// S09b real-WebGL smoke: serves an allow-listed slice of the repo on 127.0.0.1 and drives
// headless Chromium (Playwright-cached chrome-headless-shell, SwiftShader GL) over raw CDP
// (Node built-in WebSocket; no new dependency) on tests/viewer/browser-smoke.html.
// Usage: node tests/viewer/browser-smoke.mjs   (CHROME_BIN overrides the browser path)
import http from 'node:http';
import { readFile, readdir, mkdtemp, rm } from 'node:fs/promises';
import { spawn } from 'node:child_process';
import path from 'node:path';
import os from 'node:os';
import { ROOT } from './fixture-bundle.mjs';

const TYPES = { '.html': 'text/html', '.mjs': 'text/javascript', '.js': 'text/javascript', '.json': 'application/json' };
const ALLOWED = ['/tests/viewer/browser-smoke.html', '/Build/web/src/viewer/', '/Build/web/node_modules/three/build/', '/test-data/synthetic/scene/'];

async function findChrome() {
  if (process.env.CHROME_BIN) return process.env.CHROME_BIN;
  const base = path.join(process.env.LOCALAPPDATA ?? path.join(os.homedir(), '.cache'), 'ms-playwright');
  const dirs = (await readdir(base)).filter((d) => d.startsWith('chromium_headless_shell-')).sort().reverse();
  if (!dirs.length) throw new Error('no chrome-headless-shell; set CHROME_BIN');
  const sub = (await readdir(path.join(base, dirs[0]))).find((d) => d.startsWith('chrome-headless-shell'));
  return path.join(base, dirs[0], sub, process.platform === 'win32' ? 'chrome-headless-shell.exe' : 'chrome-headless-shell');
}

const server = http.createServer(async (req, res) => {
  const url = decodeURIComponent(new URL(req.url, 'http://x').pathname);
  if (req.method !== 'GET' || url.includes('..') || !ALLOWED.some((p) => url === p || (p.endsWith('/') && url.startsWith(p)))) { res.writeHead(404).end(); return; }
  try { res.writeHead(200, { 'content-type': TYPES[path.extname(url)] ?? 'application/octet-stream' }).end(await readFile(path.join(ROOT, url))); }
  catch { res.writeHead(404).end(); }
});
await new Promise((r) => server.listen(0, '127.0.0.1', r));
const page = 'http://127.0.0.1:' + server.address().port + '/tests/viewer/browser-smoke.html';
const profile = await mkdtemp(path.join(os.tmpdir(), 's09b-chrome-'));
const chrome = spawn(await findChrome(), ['--headless', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--no-first-run',
  '--remote-debugging-port=0', '--user-data-dir=' + profile, 'about:blank'], { stdio: ['ignore', 'ignore', 'pipe'] });

let result;
const timer = setTimeout(() => chrome.kill(), 60000);
try {
  const wsUrl = await new Promise((resolve, reject) => {
    let buf = '';
    chrome.stderr.on('data', (d) => { buf += d; const m = /DevTools listening on (ws:\/\/\S+)/.exec(buf); if (m) resolve(m[1]); });
    chrome.once('exit', () => reject(new Error('chrome exited early')));
  });
  const ws = new WebSocket(wsUrl);
  await new Promise((r, j) => { ws.onopen = r; ws.onerror = () => j(new Error('cdp connect failed')); });
  let id = 0; const pending = new Map(); const errors = [];
  ws.onmessage = (m) => {
    const msg = JSON.parse(m.data);
    if (msg.id && pending.has(msg.id)) { pending.get(msg.id)(msg); pending.delete(msg.id); }
    else if (msg.method === 'Runtime.exceptionThrown') errors.push(msg.params.exceptionDetails?.exception?.description ?? 'exception');
  };
  const send = (method, params = {}, sessionId) => new Promise((r) => { const i = ++id; pending.set(i, r); ws.send(JSON.stringify({ id: i, method, params, sessionId })); });
  const { result: { targetId } } = await send('Target.createTarget', { url: 'about:blank' });
  const { result: { sessionId } } = await send('Target.attachToTarget', { targetId, flatten: true });
  await send('Runtime.enable', {}, sessionId);
  // S09e: optional device emulation, e.g. SMOKE_DEVICE=375x667@3 (phone width + DPR) for the reduced budget tier.
  const dev = /^(\d+)x(\d+)@([\d.]+)$/.exec(process.env.SMOKE_DEVICE ?? '');
  if (dev) await send('Emulation.setDeviceMetricsOverride', { width: +dev[1], height: +dev[2], deviceScaleFactor: +dev[3], mobile: true }, sessionId);
  await send('Page.navigate', { url: page }, sessionId);
  for (let i = 0; i < 150 && !result; i++) {
    await new Promise((r) => setTimeout(r, 200));
    const r = await send('Runtime.evaluate', { expression: "document.getElementById('out')?.textContent ?? 'PENDING'", returnByValue: true }, sessionId);
    const v = r.result?.result?.value;
    if (v && v !== 'PENDING') result = JSON.parse(v);
  }
  result ??= { ok: false, error: 'page never reported', exceptions: errors.slice(0, 5) };
  ws.close();
} catch (e) { result = { ok: false, error: String(e.message ?? e) }; }
clearTimeout(timer);
chrome.kill(); server.close();
if (chrome.exitCode === null) await new Promise((r) => chrome.once('exit', r));
await rm(profile, { recursive: true, force: true }).catch(() => {});
console.log(JSON.stringify(result));
process.exitCode = result.ok === true ? 0 : 1;
