// Run against a local server: node evidence/N48/auth-screenshots.cjs <installed-playwright-path> <base-url>
const assert = require('node:assert/strict');
const fs = require('node:fs/promises');
const path = require('node:path');
const { pathToFileURL } = require('node:url');

(async () => {
  const { PALETTES } = await import(pathToFileURL(path.resolve('Build/web/src/shell/theme.mjs')));
  const cases = [...PALETTES, ...['light', 'dark', 'contrast'].map((resolved) => ({
    ...PALETTES.find((p) => p.id === resolved), id: 'system-' + resolved, choice: 'system', resolved
  }))];
  const browser = await require(process.argv[2]).chromium.launch({ headless: false, channel: 'chromium' });
  const context = await browser.newContext({ viewport: { width: 1280, height: 960 } });
  const page = await context.newPage(), results = [];
  try {
    for (const width of [1280, 375]) for (const route of ['sign-in', 'sign-up']) {
      await page.setViewportSize({ width, height: 960 });
      await page.goto((process.argv[3] || 'http://localhost:3050') + '/' + route);
      await page.locator('.cl-card').waitFor({ timeout: 30000 });
      for (const palette of cases) {
        await page.emulateMedia({ colorScheme: palette.resolved === 'dark' ? 'dark' : 'light', contrast: palette.resolved === 'contrast' ? 'more' : 'no-preference' });
        await page.locator('.theme-menu > summary').click();
        await page.locator('[data-theme-option="' + (palette.choice || palette.id) + '"]').click();
        await page.waitForFunction((id) => document.documentElement.dataset.theme === id, palette.resolved || palette.id);
        // Clerk transitions colors for 200 ms; audit the settled palette, not an in-between animation frame.
        await page.waitForFunction((t) => {
          const rgb = (hex) => 'rgb(' + [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16)).join(', ') + ')';
          const card = getComputedStyle(document.querySelector('.cl-card'));
          const button = getComputedStyle(document.querySelector('.cl-formButtonPrimary'));
          return card.backgroundColor === rgb(t.surface) && card.color === rgb(t.text)
            && button.backgroundColor === rgb(t.accent) && button.color === rgb(t['accent-contrast']);
        }, palette.tokens);
        const audit = await page.evaluate(() => {
          const ctx = document.createElement('canvas').getContext('2d', { willReadFrequently: true });
          const rgba = (value) => { ctx.clearRect(0, 0, 1, 1); ctx.fillStyle = value; ctx.fillRect(0, 0, 1, 1); return [...ctx.getImageData(0, 0, 1, 1).data].map((n, i) => i === 3 ? n / 255 : n); };
          const blend = (a, b) => a.slice(0, 3).map((v, i) => v * a[3] + b[i] * (1 - a[3])).concat(1);
          const background = (e) => { const chain = []; for (; e; e = e.parentElement) chain.unshift(e); return chain.reduce((bg, el) => blend(rgba(getComputedStyle(el).backgroundColor), bg), [255, 255, 255, 1]); };
          const lum = (rgb) => rgb.slice(0, 3).map((v) => v / 255).map((v) => v <= 0.04045 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4).reduce((s, v, i) => s + v * [0.2126, 0.7152, 0.0722][i], 0);
          const ratio = (fg, bg) => { const a = lum(blend(fg, bg)), b = lum(bg); return (Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05); };
          const selectors = '.cl-headerTitle,.cl-headerSubtitle,.cl-socialButtonsBlockButtonText,.cl-dividerText,.cl-formFieldLabel,.cl-formFieldInput,.cl-formButtonPrimary,.cl-footerActionText,.cl-footerActionLink,.cl-footer p,.cl-footer a';
          const pairs = [...document.querySelectorAll(selectors)].filter((e) => e.getBoundingClientRect().width && getComputedStyle(e).visibility !== 'hidden').map((e) => ({
            element: e.className.split(' ')[0], contrast: ratio(rgba(getComputedStyle(e).color), background(e)), text: e.tagName === 'INPUT' ? '(empty input)' : e.textContent.trim().slice(0, 60)
          }));
          for (const e of document.querySelectorAll('.cl-formFieldInput')) {
            pairs.push({ element: 'input placeholder', contrast: ratio(rgba(getComputedStyle(e, '::placeholder').color), background(e)) });
          }
          const controls = [...document.querySelectorAll('.cl-formFieldInput,.cl-socialButtonsBlockButton')].map((e) => ({
            element: e.className.split(' ')[0], width: parseFloat(getComputedStyle(e).borderTopWidth), contrast: ratio(rgba(getComputedStyle(e).borderTopColor), background(e))
          }));
          const card = document.querySelector('.cl-card').getBoundingClientRect();
          return { pairs, controls, cardFits: card.x >= 0 && card.right <= innerWidth, theme: document.documentElement.dataset.theme, cardBackground: getComputedStyle(document.querySelector('.cl-card')).backgroundColor };
        });
        const name = route + '-' + palette.id + '-' + width;
        await page.screenshot({ path: path.resolve('evidence/N48/' + name + '.png'), fullPage: true });
        results.push({ name, ...audit, failures: [...audit.pairs.filter((p) => p.contrast < 4.5), ...audit.controls.filter((p) => !p.width || p.contrast < 3)] });
      }
    }
    await fs.writeFile('evidence/N48/auth-render-checks.json', JSON.stringify({ browser: 'headed Playwright Chromium', server: 'local next start; real DEV publishable key, synthetic noncredential secret; no authentication attempted', results }, null, 2));
    assert.equal(results.length, 36);
    assert.ok(results.every((r) => r.cardFits && r.failures.length === 0), JSON.stringify(results.filter((r) => !r.cardFits || r.failures.length).map(({ name, cardFits, failures }) => ({ name, cardFits, failures }))));
    console.log('PASS: 36 real Clerk screenshots (six palettes + System light/dark/contrast); text >= 4.5:1; controls >= 3:1; cards fit both widths.');
  } finally { await browser.close(); }
})().catch((e) => { console.error(e); process.exitCode = 1; });
