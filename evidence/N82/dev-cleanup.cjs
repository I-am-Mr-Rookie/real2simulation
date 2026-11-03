// Explicitly approved DEV fixture projects only. Uses headed Playwright Chromium and the existing product UI.
const { chromium } = require('C:/Users/HP/AppData/Roaming/npm/node_modules/@playwright/mcp/node_modules/playwright');
const fs = require('node:fs/promises');
const assert = require('node:assert/strict');
const path = require('node:path');
const ORIGIN = 'https://real2simulation.up.railway.app';
const TARGETS = ['17f7acaaed9945aab6b782b3c93c91cc', '89f46b23753945718843074eaf9004e4', '3a0b6e11051c4ea59fe08034deab553b'];
const EMAIL = 'n43-mvym1kik+clerk_test@example.com';
const out = __dirname;
const allowedDelete = (url) => TARGETS.some((id) => url === ORIGIN + '/api/workspace/projects/' + id);
assert.ok(TARGETS.every((id) => allowedDelete(ORIGIN + '/api/workspace/projects/' + id)));
assert.ok(!allowedDelete(ORIGIN + '/api/workspace/projects/unapproved'));

(async () => {
  const browser = await chromium.launch({ headless: false,
    executablePath: 'C:/Users/HP/AppData/Local/ms-playwright/chromium-1248/chrome-win64/chrome.exe' });
  const page = await browser.newPage({ viewport: { width: 1366, height: 900 } });
  const result = { origin: ORIGIN, allowed: TARGETS, deleted: [], alreadyAbsent: [], dialogs: [], unrequestedPrefixAbsent: null };
  let expected = null;
  await page.route('**/api/workspace/**', async (route) => {
    const r = route.request();
    if (r.method() !== 'GET' && !(r.method() === 'DELETE' && allowedDelete(r.url()))) return route.abort();
    return route.continue();
  });
  page.on('dialog', async (dialog) => {
    const message = dialog.message();
    result.dialogs.push({ type: dialog.type(), message, approved: message === expected });
    if (dialog.type() === 'confirm' && message === expected) await dialog.accept();
    else await dialog.dismiss();
  });
  page.on('request', (request) => {
    if (request.method() === 'DELETE') assert.ok(allowedDelete(request.url()), 'unapproved DELETE');
  });
  try {
    await page.goto(ORIGIN + '/sign-in');
    await page.getByRole('textbox', { name: /email/i }).waitFor({ timeout: 30000 });
    await page.getByRole('textbox', { name: /email/i }).fill(EMAIL);
    const prepared = page.waitForResponse((r) => new URL(r.url()).pathname.endsWith('/prepare_first_factor') && r.request().method() === 'POST', { timeout: 30000 });
    await page.getByRole('button', { name: /^Continue$/ }).click();
    const preparation = await prepared;
    result.codePreparedStatus = preparation.status();
    assert.equal(preparation.status(), 200);
    const code = page.locator('input[autocomplete="one-time-code"]');
    await code.waitFor({ timeout: 30000 });
    await code.fill('424242');
    await page.waitForURL(/\/workspace(?:\/|$)/, { timeout: 30000, waitUntil: 'domcontentloaded' });
    await page.getByRole('heading', { name: /^(Projects|Choose how the agent runs)$/ }).waitFor();
    // A fresh browser context has no local agent-mode preference; keep the displayed Standard default.
    if (await page.getByRole('heading', { name: 'Choose how the agent runs', exact: true }).count())
      await page.getByRole('button', { name: 'Continue', exact: true }).click();
    await page.getByRole('heading', { name: 'Projects', exact: true }).waitFor();
    await page.locator('.lv-projects[aria-busy="true"]').waitFor({ state: 'hidden' });
    const list = async () => {
      const response = await page.request.get(ORIGIN + '/api/workspace/projects');
      assert.equal(response.status(), 200);
      return (await response.json()).projects;
    };
    const before = await list();
    assert.ok(before.length && before.every((p) => p.user === 'user_3LWziQJxcsdCLbV2bCKATtu7KMg'), 'not the independently verified fixture owner');
    result.before = before.map(({ id, title, created }) => ({ id, title, created }));
    result.unrequestedPrefixAbsent = !before.some((p) => p.id.startsWith('c46d33ba'));
    for (const id of TARGETS) {
      const projects = await list();
      const project = projects.find((p) => p.id === id);
      if (!project) { result.alreadyAbsent.push(id); continue; }
      assert.ok(!project.title.startsWith('SAMPLE'));
      const showEmpty = page.getByRole('button', { name: /^Show empty/ });
      if (await showEmpty.count()) await showEmpty.click();
      const sameTitle = projects.filter((p) => p.title === project.title);
      const cards = page.locator('li.lv-pcard').filter({ has: page.locator('strong.lv-pname').filter({ hasText: new RegExp('^' + project.title.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '$') }) });
      await cards.first().waitFor();
      assert.equal(await cards.count(), sameTitle.length);
      const card = cards.nth(sameTitle.findIndex((p) => p.id === id));
      await card.locator('summary[aria-label="Project actions for ' + project.title + '"]').click();
      expected = 'Delete project ' + project.title + '? Its files stay in Files.';
      const deleted = page.waitForResponse((r) => r.url() === ORIGIN + '/api/workspace/projects/' + id && r.request().method() === 'DELETE');
      await card.getByRole('menuitem', { name: 'Delete', exact: true }).click();
      assert.equal((await deleted).status(), 200);
      expected = null;
      assert.ok(!(await list()).some((p) => p.id === id), 'target still exists');
      result.deleted.push(id);
      await page.reload({ waitUntil: 'domcontentloaded' });
      await page.getByRole('heading', { name: 'Projects', exact: true }).waitFor();
      await page.locator('.lv-projects[aria-busy="true"]').waitFor({ state: 'hidden' });
    }
    const after = await list();
    result.after = after.map(({ id, title, created }) => ({ id, title, created }));
    assert.deepEqual(after.map((p) => p.id).sort(), before.filter((p) => !TARGETS.includes(p.id)).map((p) => p.id).sort());
    assert.ok(after.some((p) => p.title.startsWith('SAMPLE')));
    await page.screenshot({ path: path.join(out, 'dev-after.jpg'), fullPage: true });
    result.status = 'DONE';
  } catch (error) {
    result.status = 'PARTIAL';
    result.error = error.message;
    result.lastUrl = page.url();
    result.lastUi = (await page.locator('body').innerText().catch(() => '')).replaceAll(EMAIL, '[fixture email]').slice(-1800);
    if (page.url().includes('/workspace/') && !(await page.locator('body').innerText()).includes(EMAIL))
      await page.screenshot({ path: path.join(out, 'dev-cleanup-failure.jpg'), fullPage: true });
    // Never capture an email/code/auth screen.
  } finally {
    await fs.writeFile(path.join(out, 'dev-cleanup.json'), JSON.stringify(result, null, 2) + '\n');
    console.log(JSON.stringify({ status: result.status, deleted: result.deleted, alreadyAbsent: result.alreadyAbsent, error: result.error }));
    await browser.close();
  }
})();
