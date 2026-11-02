// DEV only. Uses an existing Clerk test account, not real email delivery.
// shortcut: pins a DEV fixture and local Chromium, update them if the account or browser is removed.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { createRequire } = require('node:module');
const { chromium } = createRequire(path.join(process.env.APPDATA, 'npm/node_modules/@playwright/mcp/package.json'))('playwright');
const hosts = ['real2simulation.up.railway.app', 'real2simulation.rookiecoders.tech'];
const output = { observed_utc: new Date().toISOString(), headed: true, email_delivery: 'NOT_CHECKED: Clerk development test code, not Gmail', hosts: [] };

(async () => {
  const browser = await chromium.launch({ headless: false, executablePath: path.join(process.env.LOCALAPPDATA, 'ms-playwright/chromium-1248/chrome-win64/chrome.exe') });
  let activePage;
  try {
    for (const host of hosts) {
      const context = await browser.newContext({ viewport: { width: 1365, height: 900 } });
      const page = await context.newPage();
      activePage = page;
      const result = { host, checks: [], console_errors: [] };
      output.hosts.push(result);
      page.on('pageerror', e => result.console_errors.push(e.message));
      for (const [route, heading] of [['/lab', 'Test a motion model'], ['/library', 'Demo library']]) {
        const response = await page.goto(`https://${host}${route}`);
        assert.equal(response.status(), 200);
        await page.getByRole('heading', { name: heading, exact: true }).waitFor();
        result.checks.push({ route, status: response.status(), rendered: true });
      }
      const response = await page.goto(`https://${host}/sign-in`);
      assert.equal(response.status(), 200);
      await page.getByRole('textbox', { name: 'Email address', exact: true }).waitFor();
      result.checks.push({ route: '/sign-in', status: response.status(), clerk_widget: true });
      await page.screenshot({ path: path.join(__dirname, host + '-sign-in.png') });
      await page.getByRole('textbox', { name: 'Email address', exact: true }).fill('n43-mvym1kik+clerk_test@example.com');
      await page.getByRole('button', { name: 'Continue', exact: true }).click();
      await page.getByRole('textbox', { name: 'Enter verification code', exact: true }).fill('424242');
      await page.waitForURL(url => url.pathname.startsWith('/workspace'), { timeout: 30000, waitUntil: 'domcontentloaded' });
      await page.locator('[data-private-content="live"]').waitFor({ timeout: 30000 });
      const health = await page.request.get(`https://${host}/api/workspace/health`);
      assert.equal(health.status(), 200);
      result.checks.push({ route: '/workspace', authenticated: true, private_api_status: health.status(), method: 'Clerk development email-code fixture' });
      await page.screenshot({ path: path.join(__dirname, host + '-workspace.png') });
      console.log(JSON.stringify(result));
      await context.close();
    }
  } catch (error) {
    output.error = error.message;
    output.failure_url = activePage?.url();
    output.failure_text = await activePage?.locator('body').innerText();
    console.error(JSON.stringify({ error: output.error, url: output.failure_url, text: output.failure_text }));
    process.exitCode = 1;
  } finally {
    fs.writeFileSync(path.join(__dirname, 'browser-check.json'), JSON.stringify(output, null, 2) + '\n');
    await browser.close();
  }
})();
