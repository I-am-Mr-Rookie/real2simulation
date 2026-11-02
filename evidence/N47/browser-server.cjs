// Keep the QA browser alive when an interactive recorder cell times out.
const { createRequire } = require('node:module');
const fs = require('node:fs');
const path = require('node:path');
const { chromium } = createRequire('C:/Users/HP/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/')('playwright-core');
(async () => {
  const executablePath = path.join(process.env.LOCALAPPDATA, 'ms-playwright/chromium-1248/chrome-win64/chrome.exe');
  if (!fs.existsSync(executablePath)) throw new Error('Installed Playwright Chromium missing');
  const server = await chromium.launchServer({ headless: false, executablePath });
  fs.writeFileSync(path.join(__dirname, '.browser-endpoint'), server.wsEndpoint());
  console.log('N47 headed Playwright Chromium ready');
  await new Promise(resolve => server.on('close', resolve));
})();
