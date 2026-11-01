// S15bg: real headless Chromium (Playwright, not Chrome) mounts the real PrivateWorkspace client module from the working tree,
// delays /api/workspace/health, and samples h1, document.title and every [role=alert]/[aria-live] node before and after the probe.
// Harness limits: React from esm.sh, no Next route announcer or Clerk (no keys locally); the announcer reads document.title or h1.
import { createRequire } from 'module';
import fs from 'fs';
import path from 'path';
const require = createRequire('C:/Users/HP/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/');
const { chromium } = require('playwright-core');
const SRC = path.resolve(import.meta.dirname, '../../Build/web/src');
const OUT = import.meta.dirname;
const mode = process.argv[2] ?? 'live'; // live | unavailable
const VER = '19.3.1';
const html = '<!doctype html><html><head><title>Real2Simulation</title><script type="importmap">' + JSON.stringify({ imports: {
  react: 'https://esm.sh/react@' + VER, 'react-dom/client': 'https://esm.sh/react-dom@' + VER + '/client?deps=react@' + VER,
  three: 'https://esm.sh/three@0.186.1', 'next/link': 'http://h.test/stub-link.mjs', '@clerk/nextjs': 'http://h.test/stub-link.mjs' } }) + '</script></head><body><div id="root"></div>'
  + '<script type="module">import React from "react";import {createRoot} from "react-dom/client";import W from "/src/shell/PrivateWorkspace.mjs";'
  + 'createRoot(document.getElementById("root")).render(React.createElement(W,{scene:{title:"Private development fixture",notice:"FIXTURE / SYNTHETIC: empty private development scene"}}));</script></body></html>';
const b = await chromium.launch({ headless: true });
const p = await (await b.newContext({ viewport: { width: 1280, height: 800 } })).newPage();
const errs = []; p.on('pageerror', (e) => errs.push(String(e).slice(0, 200)));
p.on('console', (m) => m.type() === 'error' && errs.push(m.text().slice(0, 200)));
p.on('requestfailed', (q) => errs.push('FAILED ' + q.url().slice(0, 120)));
await p.route('http://h.test/**', async (r) => {
  const u = new URL(r.request().url());
  if (u.pathname === '/') return r.fulfill({ contentType: 'text/html', body: html });
  if (u.pathname === '/stub-link.mjs') return r.fulfill({ contentType: 'text/javascript', body: 'export default (p)=>null;export const SignedIn=()=>null,UserButton=()=>null,useAuth=()=>({});' });
  if (u.pathname === '/api/workspace/health') {
    await new Promise((s) => setTimeout(s, 2500));
    return mode === 'live' ? r.fulfill({ status: 404, contentType: 'application/json', body: '{"detail":{"code":"NOT_FOUND"}}' }) : r.fulfill({ status: 502, contentType: 'application/json', body: '{}' });
  }
  if (u.pathname.startsWith('/simulator/')) return r.fulfill({ contentType: 'text/javascript', body: fs.readFileSync(path.join(SRC, '../../simulator', u.pathname.slice(11)), 'utf8') });
  if (u.pathname.startsWith('/src/')) return r.fulfill({ contentType: 'text/javascript', body: fs.readFileSync(path.join(SRC, u.pathname.slice(5)), 'utf8') });
  return r.continue();
});
const snap = () => p.evaluate(() => ({ title: document.title, h1: document.querySelector('h1')?.textContent ?? null,
  live: [...document.querySelectorAll('[role=alert],[aria-live]')].map((n) => ({ role: n.getAttribute('role'), live: n.getAttribute('aria-live'), text: n.textContent.trim().slice(0, 120) })),
  fixtureWording: /development fixture|FIXTURE/i.test(document.body.innerText), section: document.querySelector('section[data-private-content]')?.getAttribute('data-private-content') }));
await p.goto('http://h.test/');
await p.waitForSelector('h1', { timeout: 20000 }).catch(() => { console.log('NO H1', JSON.stringify(errs)); process.exit(2); });
const before = await snap();
await p.waitForSelector('section[data-api=' + (mode === 'live' ? 'live' : 'unavailable') + ']', { timeout: 15000 });
const after = await snap();
await p.addStyleTag({ content: 'video{visibility:hidden!important}' });
await p.screenshot({ path: OUT + '/' + mode + '.png' });
fs.writeFileSync(OUT + '/result-' + mode + '.json', JSON.stringify({ mode, before, after, pageErrors: errs }, null, 1));
console.log(JSON.stringify({ before, after, errs }));
await b.close();
