// Run with PLAYWRIGHT_MODULE and CHROMIUM_EXECUTABLE pointing to the installed runtime and Chromium.
const assert = require('node:assert/strict');
const fs = require('node:fs/promises');
const path = require('node:path');
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const [phase, base] = process.argv.slice(2);
assert.ok(['before', 'after'].includes(phase) && base);
const routes = ['/', '/library', '/lab', '/lab?editor=1', '/sign-in'];
const sizes = [[375, 812], [1280, 720], [1366, 768], [1920, 1080], [2560, 1440]];
const rects = () => {
  const bounds = (s) => {
    const e = document.querySelector(s);
    if (!e) return null;
    const r = e.getBoundingClientRect();
    return { x: r.x, right: r.right, y: r.y, bottom: r.bottom, width: r.width, height: r.height };
  };
  return { header: bounds('.site-header'), main: bounds('main'), footer: bounds('.site-footer'), editor: bounds('.lab-editor'), stage: bounds('.le-stage'), left: bounds('.le-left'), right: bounds('.le-right'), canvas: bounds('.le-canvas canvas'), scrollWidth: document.documentElement.scrollWidth, clientWidth: document.documentElement.clientWidth };
};
(async () => {
  const browser = await chromium.launch({ headless: false, executablePath: process.env.CHROMIUM_EXECUTABLE });
  const context = await browser.newContext({ deviceScaleFactor: 1, reducedMotion: 'reduce' });
  const page = await context.newPage();
  const results = [];
  try {
    for (const route of routes) for (const [width, height] of sizes) {
      await page.setViewportSize({ width, height });
      await page.goto(base + route, { waitUntil: 'domcontentloaded' });
      await page.locator('main').waitFor();
      await page.evaluate(() => document.fonts.ready);
      if (route === '/library') await page.locator('.lib-card, .lib-empty').first().waitFor();
      if (phase === 'before' && route === '/sign-in') await page.getByText('Continue with Google', { exact: true }).waitFor();
      if (route.includes('editor')) await page.locator('.le-canvas canvas').waitFor();
      const measured = await page.evaluate(rects);
      results.push({ route, width, height, url: page.url(), ...measured });
      if (phase === 'after') {
        for (const key of ['header', 'footer']) {
          assert.ok(Math.abs(measured[key].x - measured.main.x) < 1, `${route} ${width}: ${key} left`);
          assert.ok(Math.abs(measured[key].right - measured.main.right) < 1, `${route} ${width}: ${key} right`);
        }
        assert.ok(measured.scrollWidth <= measured.clientWidth, `${route} ${width}: horizontal overflow`);
        if (measured.editor) {
          assert.ok(Math.abs(measured.editor.x - measured.main.x) < 1);
          assert.ok(Math.abs(measured.editor.right - measured.main.right) < 1);
          assert.ok(measured.stage.height >= 320 && measured.stage.height <= 640);
          assert.ok(Math.abs(measured.canvas.height - (measured.stage.height - 2)) < 1);
          if (width >= 1280) for (const key of ['left', 'right']) {
            assert.ok(measured[key].height <= measured.stage.height + 1, `${width}: panel exceeds stage`);
          }
          await page.setViewportSize({ width, height: height + 400 });
          const taller = await page.evaluate(rects);
          // A disappearing scrollbar changes available width, not the sizing rule.
          const expected = r => width <= 900 ? Math.max(320, Math.min(480, .8 * r.editor.width)) : Math.max(420, Math.min(640, .38 * r.editor.width));
          for (const r of [measured, taller]) assert.ok(Math.abs(r.stage.height - expected(r)) < 1, `${width}: stage is not width-based`);
          await page.setViewportSize({ width, height });
        }
      }
      if ((route.includes('editor') || width === 375 || width === 1920) && !(phase === 'after' && route === '/sign-in')) {
        const name = route === '/' ? 'home' : route.includes('editor') ? 'editor' : route.slice(1);
        const style = await page.evaluate(() => document.documentElement.scrollHeight > innerHeight ? 'html { scrollbar-gutter: stable; }' : '');
        await page.screenshot({ path: path.join(__dirname, `${phase}-${name}-${width}.jpg`), type: 'jpeg', quality: 65, fullPage: true, style });
      }
      console.log(`${phase} ${route} ${width}: header ${measured.header.width}, main ${measured.main.width}, stage ${measured.stage?.height || '-'}, footer top ${measured.footer.y}`);
    }
    if (phase === 'after') {
      await page.setViewportSize({ width: 1366, height: 768 });
      await page.goto(base + '/lab?editor=1', { waitUntil: 'domcontentloaded' });
      await page.locator('.le-canvas canvas').waitFor();
      await page.locator('.le-stage').evaluate(e => e.requestFullscreen());
      await page.waitForFunction(() => document.fullscreenElement && Math.abs(document.querySelector('.le-stage').getBoundingClientRect().height - innerHeight) < 1);
      results.push({ fullscreen: await page.evaluate(rects), height: await page.evaluate(() => innerHeight) });
      await page.evaluate(() => document.exitFullscreen());
      await page.locator('.lab-editor').evaluate(e => e.requestFullscreen());
      await page.waitForFunction(() => document.fullscreenElement?.classList.contains('lab-editor') && Math.abs(document.querySelector('.lab-editor').getBoundingClientRect().height - innerHeight) < 1);
      const fullEditor = await page.evaluate(rects);
      assert.ok(Math.abs(fullEditor.stage.bottom - fullEditor.editor.bottom) <= 17);
      results.push({ fullscreenEditor: fullEditor });
      await page.evaluate(() => document.exitFullscreen());
    }
  } finally {
    await fs.writeFile(path.join(__dirname, `${phase}-metrics.json`), JSON.stringify({ base, headless: false, executable: process.env.CHROMIUM_EXECUTABLE, results }, null, 2) + '\n');
    await browser.close();
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
