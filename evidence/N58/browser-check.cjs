// Headed Playwright Chromium. Local compiled app + isolated public RM04/ST03 and template data only.
// The temporary local workspace page is not shipped. Authentication, paid SAM/SF3D and DEV are not exercised.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { createRequire } = require('node:module');
const { chromium } = createRequire(path.join(process.env.APPDATA, 'npm/node_modules/@playwright/mcp/package.json'))('playwright');
const BASE = 'http://127.0.0.1:18559';
const headers = { 'x-workspace-owner': 'n58_public', 'x-workspace-token': 'n58-local-public-only' };
const receipts = [], errors = [], calls = [];
const receipt = (name, data) => { receipts.push({ name, utc: new Date().toISOString(), data }); console.log(name + ': PASS'); };
async function api(p, init = {}) {
  const r = await fetch('http://127.0.0.1:18558/internal/workspace' + p, { ...init, headers: { ...headers, 'content-type': 'application/json', ...init.headers } });
  const data = await r.json(); assert.equal(r.ok, true, JSON.stringify(data)); return data;
}
async function geometry(page) {
  return page.evaluate(() => ({ width: innerWidth, scrollWidth: document.documentElement.scrollWidth,
    header: getComputedStyle(document.querySelector('.site-header')).display,
    emDash: document.body.innerText.includes('\u2014'),
    top: [...document.querySelectorAll('.le-top button,.le-top label,.le-top a')].map((el) => { const b = el.getBoundingClientRect(); return { label: el.getAttribute('aria-label') || el.title || el.textContent, left: b.left, right: b.right, top: b.top, bottom: b.bottom }; }) }));
}
(async () => {
  const browser = await chromium.launch({ headless: false, executablePath: path.join(process.env.LOCALAPPDATA, 'ms-playwright/chromium-1248/chrome-win64/chrome.exe') });
  const context = await browser.newContext({ viewport: { width: 1366, height: 900 }, acceptDownloads: true });
  const page = await context.newPage();
  page.on('pageerror', (e) => errors.push(e.message));
  page.on('dialog', (d) => { errors.push('Unexpected browser dialog: ' + d.type()); d.dismiss(); });
  await context.addInitScript(() => { localStorage.setItem('r2s.agent.mode.n58-public-sample', 'standard'); });
  await page.route('**/api/workspace/**', async (route) => {
    const req = route.request(), tail = new URL(req.url()).pathname.slice('/api/workspace'.length);
    if (tail === '/session') return route.fulfill({ json: { userKey: 'n58-public-sample' } });
    if (tail === '/agent/lab/scene') return route.fulfill({ json: { scene: { objects: [] } } });
    if (tail === '/agent/lab/report') return route.fulfill({ json: { markdown: '' } });
    if (tail.startsWith('/agent/') || req.method() === 'POST' && /\/(objects|shell|rooms|experiments)$/.test(tail)) {
      calls.push({ path: tail, method: req.method(), blocked_paid: true });
      return route.fulfill({ status: 503, json: { detail: { message: 'Paid operation disabled in local verification.' } } });
    }
    const res = await fetch('http://127.0.0.1:18558/internal/workspace' + tail + new URL(req.url()).search, {
      method: req.method(), headers: { ...headers, 'content-type': req.headers()['content-type'] || 'application/json' }, body: ['GET', 'HEAD'].includes(req.method()) ? undefined : req.postDataBuffer(),
    });
    calls.push({ path: tail, method: req.method(), status: res.status });
    await route.fulfill({ status: res.status, contentType: res.headers.get('content-type') || 'application/octet-stream', body: Buffer.from(await res.arrayBuffer()) });
  });
  try {
    const { rooms } = await api('/rooms'), { experiments } = await api('/experiments');
    const room = rooms.find((r) => r.sample), experiment = experiments.find((e) => e.sample);
    assert.ok(room && experiment, 'public sample is provisioned');
    const { project } = await api('/projects', { method: 'POST', body: JSON.stringify({ mode: 'experiment', title: 'N58 template lab ' + Date.now() }) });
    await page.goto(BASE + '/lab?editor=1&project=' + project.id);
    await page.getByLabel('Lab editor', { exact: true }).waitFor();
    await page.locator('.le-canvas canvas').waitFor();
    const add = page.getByLabel('Add an object or probe');
    await add.click(); await page.getByRole('menuitem', { name: 'Ball', exact: true }).click();
    await page.locator('.le-top').getByRole('button', { name: 'Play', exact: true }).click();
    await page.waitForTimeout(250);
    await page.locator('.le-top').getByRole('button', { name: 'Pause', exact: true }).click();
    const seek = page.getByRole('slider', { name: 'Seek recorded sensor trace' });
    await seek.fill('5');
    assert.match(await seek.getAttribute('aria-valuetext'), /s$/);
    receipt('template-sensor-seek', { value: await seek.inputValue(), time: await seek.getAttribute('aria-valuetext'), graph: await page.locator('.le-graph').innerText() });
    await page.getByRole('button', { name: 'Fit trace', exact: true }).click();
    await page.getByRole('region', { name: 'Fit result' }).waitFor();
    const fitText = await page.getByRole('region', { name: 'Fit result' }).innerText();
    assert.match(fitText, /SIMULATED/); assert.match(fitText, /\+\/-/);
    receipt('template-cpu-fit', { text: fitText, fitRequest: calls.filter((c) => c.path === '/fit') });
    await page.goto(BASE + '/lab/n58-check');
    await page.locator('[data-private-content="live"]').waitFor();
    const relativePath = page.locator('.lv-pcard[data-sample] .lv-track-preview[data-plot]');
    await relativePath.waitFor();
    receipt('public-recorded-relative-path-preview', { label: await relativePath.getAttribute('aria-label'), overlayOnVideo: false });
    const card = page.locator('.lv-pcard').filter({ hasText: project.title });
    await card.locator('img.lv-thumb').waitFor();
    await page.waitForFunction(() => [...document.querySelectorAll('.lv-pcard img')].some((x) => x.naturalWidth > 0));
    assert.match(await card.innerText(), /Saved lab/);
    receipt('snapshot-only-card', { text: await card.innerText(), small: await card.getAttribute('data-small'), snapshot: await card.locator('img').getAttribute('src') });
    await card.locator('summary').click(); await card.getByRole('menuitem', { name: 'Rename', exact: true }).click();
    const renamed = 'N58 inline rename ' + project.id.slice(0, 6);
    await page.getByRole('textbox', { name: 'Project name' }).fill(renamed);
    await page.getByRole('button', { name: 'Save', exact: true }).click();
    await page.getByText(renamed, { exact: true }).waitFor();
    receipt('inline-rename', { title: renamed, browserDialogs: errors.filter((x) => x.includes('dialog')) });
    for (const width of [1366, 375]) for (const theme of ['light', 'dark']) {
      await page.setViewportSize({ width, height: 900 });
      if (width === 375) await page.keyboard.press('Escape');
      await page.evaluate((t) => { document.documentElement.dataset.theme = t; document.documentElement.dataset.tone = t; }, theme);
      const g = await geometry(page);
      assert.ok(g.scrollWidth <= width, JSON.stringify(g)); assert.equal(g.header, 'none'); assert.equal(g.emDash, false);
      assert.equal(await page.locator('.ws-legacy').getAttribute('open'), null);
      await page.locator('.ws-legacy > summary').click();
      assert.ok(await page.locator('.ws-legacy .ws').isVisible());
      await page.locator('.ws-legacy > summary').click();
      receipt('workspace-' + width + '-' + theme, g);
      await page.screenshot({ path: path.join(__dirname, 'workspace-' + width + '-' + theme + '.png'), fullPage: true });
    }
    await page.goto(BASE + '/lab?editor=1&room=' + room.job_id);
    await page.getByRole('button', { name: 'Room', exact: true }).click();
    const image = page.getByAltText(/^Room view 1(?:\.|$)/);
    await image.waitFor(); await page.waitForFunction(() => document.querySelector('.le-view img')?.naturalWidth > 0);
    const a4 = page.getByRole('button', { name: 'Mark the A4 sheet', exact: true });
    assert.equal(await a4.isEnabled(), true);
    await a4.click(); await image.click({ position: { x: 35, y: 35 } });
    await page.getByRole('tab', { name: 'Objects', exact: true }).click();
    await page.getByRole('tab', { name: 'Room', exact: true }).click();
    assert.equal(await a4.getAttribute('aria-pressed'), 'true'); assert.equal(await page.locator('.le-mark').count(), 1);
    receipt('room-view-and-tool-retention', { view: await image.evaluate((el) => ({ width: el.naturalWidth, height: el.naturalHeight })), a4: await a4.getAttribute('aria-pressed'), marks: await page.locator('.le-mark').count() });
    const raw = page.getByRole('checkbox', { name: 'Show raw scan', exact: true }), collisions = page.getByRole('checkbox', { name: 'Enable raw scan collisions', exact: true });
    assert.equal(await collisions.isChecked(), false); await raw.uncheck(); await raw.check(); assert.equal(await collisions.isChecked(), false);
    await collisions.check(); assert.equal(await raw.isChecked(), true); await collisions.uncheck();
    receipt('raw-visibility-and-collisions-independent', { visible: await raw.isChecked(), collisions: await collisions.isChecked() });
    await page.getByRole('button', { name: 'Add a real object', exact: true }).click();
    assert.equal(await page.getByRole('button', { name: 'Add a real object', exact: true }).getAttribute('aria-pressed'), 'true');
    receipt('real-object-tool-available', { armed: true, paidSegmentation: 'NOT RUN' });
    await page.getByRole('button', { name: 'Collapse side panel', exact: true }).click();
    for (const width of [1366, 375]) for (const theme of ['light', 'dark']) {
      await page.setViewportSize({ width, height: 900 }); await page.evaluate((t) => { document.documentElement.dataset.theme = t; document.documentElement.dataset.tone = t; }, theme);
      const g = await geometry(page);
      assert.ok(g.top.every((b) => b.left >= 0 && b.right <= width + 1), JSON.stringify(g));
      assert.equal(g.emDash, false);
      await page.getByLabel('Add an object or probe').click();
      const box = await page.getByRole('menu', { name: 'Lab kit' }).boundingBox();
      assert.ok(box.x >= 0 && box.x + box.width <= width + 1, JSON.stringify(box));
      await page.keyboard.press('Escape'); assert.equal(await page.locator('.le-add').getAttribute('open'), null);
      await page.getByLabel('Add an object or probe').click(); await page.locator('.le-canvas canvas').click({ position: { x: 5, y: 5 } });
      assert.equal(await page.locator('.le-add').getAttribute('open'), null);
      receipt('room-editor-' + width + '-' + theme, { ...g, addMenu: box, escapeAndOutside: true });
      await page.screenshot({ path: path.join(__dirname, 'room-' + width + '-' + theme + '.png') });
    }
    await page.getByRole('button', { name: 'Agent', exact: true }).click();
    assert.equal(await page.getByRole('button', { name: 'Voice input', exact: true }).isVisible(), true);
    receipt('agent-voice-control', { visible: true, realMicrophoneAndTranscription: 'NOT RUN: no paid call' });
    await page.goto(BASE + '/lab?editor=1&experiment=' + experiment.id);
    await page.getByRole('region', { name: 'Fit result' }).waitFor();
    const measured = await page.getByRole('region', { name: 'Fit result' }).innerText();
    assert.match(measured, /MEASURED/); assert.match(measured, /scale unverified/); assert.match(measured, /\+\/-/);
    await page.getByRole('slider', { name: 'Seek recorded sensor trace' }).fill('4');
    receipt('public-recorded-experiment-fit-and-seek', { text: measured, time: await page.getByRole('slider', { name: 'Seek recorded sensor trace' }).getAttribute('aria-valuetext') });
    assert.deepEqual(errors, []);
    receipt('console-and-network', { pageErrors: errors, imageResponses: calls.filter((c) => c.path.includes('/views/')), paidCalls: 0 });
  } catch (e) {
    receipts.push({ name: 'FAIL', error: e.message, stack: e.stack, url: page.url(), text: (await page.locator('body').innerText()).slice(0, 7000) });
    await page.screenshot({ path: path.join(__dirname, 'failure.png'), fullPage: true }); process.exitCode = 1;
    console.error(e.message);
  } finally {
    fs.writeFileSync(path.join(__dirname, 'browser-receipts.json'), JSON.stringify({ headed: true, browser: browser.version(), scope: 'local compiled app; public samples/templates; auth and paid paths untested', receipts, calls }, null, 2) + '\n');
    await browser.close();
  }
})();
