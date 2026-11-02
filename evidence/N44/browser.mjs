// N44: local /lab check of the N43 RM02 scene (Pexels room geometry, no owner data): desktop + 375 screenshots.
import { createRequire } from 'module'; import fs from 'fs';
const require = createRequire('C:/Users/HP/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/');
const { chromium } = require('playwright-core');
const [base, out, scene] = process.argv.slice(2);
fs.mkdirSync(out, { recursive: true });
const b = await chromium.launch({ headless: false }); const res = {};
for (const [name, vp] of [['desktop', { width: 1280, height: 900 }], ['m375', { width: 375, height: 812 }]]) {
  const p = await (await b.newContext({ viewport: vp })).newPage(); const errors = [];
  p.on('pageerror', (e) => errors.push(e.message));
  await p.goto(base + '/lab'); await p.waitForTimeout(3000); await p.getByText('Open 3D lab editor').first().click(); await p.waitForTimeout(4000);
  await p.locator('input[type=file]').first().setInputFiles(scene); await p.waitForTimeout(3000);
  await p.screenshot({ path: out + '/' + name + '-rm02.png' });
  res[name] = { scrollWidth: await p.evaluate(() => document.documentElement.scrollWidth), errors };
}
fs.writeFileSync(out + '/browser.json', JSON.stringify(res, null, 1)); console.log(JSON.stringify(res)); await b.close();



