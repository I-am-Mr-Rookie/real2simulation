const assert = require('node:assert/strict');
const fs = require('node:fs/promises');
const path = require('node:path');
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const React = require('../../Build/web/node_modules/react');
const { renderToStaticMarkup } = require('../../Build/web/node_modules/react-dom/server');
const sizes = [[375, 812], [1280, 720], [1920, 1080], [2560, 1440]];
const measure = () => {
  const rect = s => { const r = document.querySelector(s).getBoundingClientRect(); return { x: r.x, width: r.width, right: r.right }; };
  return { header: rect('.site-header'), main: rect('main'), footer: rect('.site-footer'), footerDisplay: getComputedStyle(document.querySelector('.site-footer')).display, viewport: document.documentElement.clientWidth };
};
(async () => {
  const browser = await chromium.launch({ headless: false, executablePath: process.env.CHROMIUM_EXECUTABLE });
  const page = await browser.newPage({ reducedMotion: 'reduce' });
  const results = [];
  try {
    const { default: Workspace } = await import('../../Build/web/src/shell/PrivateWorkspace.mjs');
    const html = renderToStaticMarkup(React.createElement(Workspace, { scene: { title: 'LAYOUT FIXTURE ONLY', notice: 'Not a signed-in session' } }));
    for (const [width, height] of sizes) {
      await page.setViewportSize({ width, height });
      await page.goto('http://localhost:3054/', { waitUntil: 'domcontentloaded' });
      await page.locator('main').evaluate((e, markup) => { e.innerHTML = markup; }, html);
      await page.addStyleTag({ path: path.join(__dirname, '../../Build/web/src/workspace/workspace.css') });
      const r = await page.evaluate(measure);
      assert.equal(r.header.width, r.viewport);
      assert.equal(r.main.width, r.viewport);
      assert.equal(r.footerDisplay, 'none');
      results.push({ kind: 'actual component SSR fixture, not authenticated E2E; no screenshots', width, ...r });
    }
    for (const [width, height] of sizes) {
      await page.setViewportSize({ width, height });
      await page.goto('https://real2simulation.up.railway.app/sign-in', { waitUntil: 'domcontentloaded' });
      await page.getByText('Continue with Google', { exact: true }).waitFor();
      await page.evaluate(() => document.fonts.ready);
      const before = await page.evaluate(measure);
      await page.addStyleTag({ content: '.site-header, main, .site-footer { width: var(--site-width, min(1120px, calc(100% - 2.5rem))); margin-inline: auto; }' });
      const proposed = await page.evaluate(measure);
      assert.deepEqual(proposed, before);
      assert.equal(proposed.header.x, proposed.main.x);
      assert.equal(proposed.footer.right, proposed.main.right);
      if (width === 375 || width === 1920) await page.screenshot({ path: path.join(__dirname, `dev-proposed-sign-in-${width}.jpg`), type: 'jpeg', quality: 65, fullPage: true, style: 'html { scrollbar-gutter: stable; }' });
      results.push({ kind: 'live public DEV sign-in with proposed container CSS injected; not deployed', width, before, proposed });
    }
  } finally {
    await fs.writeFile(path.join(__dirname, 'shell-checks.json'), JSON.stringify(results, null, 2) + '\n');
    await browser.close();
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
