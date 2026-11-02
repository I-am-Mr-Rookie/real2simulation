// N43 interactive QA. Reuses N13 qa.mjs/qa2.mjs step, screenshot and response patterns.
import fs from 'node:fs';
export function attach(page, dir) {
  const rec = { start_utc: new Date().toISOString(), steps: [], responses: [], gpu: [], errors: [] };
  const save = () => fs.writeFileSync(dir + 'results.json', JSON.stringify(rec, null, 2));
  const shot = async (name, fullPage = false) => {
    await page.screenshot({ path: dir + name + '.png', fullPage });
    const text = (await page.locator('body').innerText()).replace(/[ \t]+$/gm, '');
    fs.writeFileSync(dir + name + '.txt', text);
    return name + '.png';
  };
  page.on('pageerror', e => { rec.errors.push({ utc: new Date().toISOString(), error: e.message }); save(); });
  page.on('dialog', d => d.accept().catch(() => {}));
  page.on('response', async r => {
    const u = new URL(r.url()), method = r.request().method();
    if (!u.pathname.startsWith('/api/workspace/')) return;
    if (method === 'GET' && r.status() < 400) return;
    let body = '', body_is_excerpt = false;
    try { const all = await r.text(); body = all.slice(0, 12000); body_is_excerpt = all.length > 12000; } catch {}
    rec.responses.push({ utc: new Date().toISOString(), method, path: u.pathname, status: r.status(), body, body_is_excerpt }); save();
  });
  const step = async (name, fn) => {
    const t = Date.now(); let ok = true, detail;
    try { detail = await fn(); } catch (e) { ok = false; detail = e.message; }
    rec.steps.push({ utc: new Date().toISOString(), name, ok, seconds: (Date.now() - t) / 1000, detail });
    await shot(name).catch(() => {}); save();
    console.log(JSON.stringify(rec.steps.at(-1)));
    return ok;
  };
  const gpu = async () => {
    const v = await page.locator('.lv-gpu').evaluate(e => ({ tone: e.dataset.tone, text: e.innerText })).catch(() => null);
    if (v && JSON.stringify(rec.gpu.at(-1)?.value) !== JSON.stringify(v)) {
      rec.gpu.push({ utc: new Date().toISOString(), value: v }); save();
    }
    return v;
  };
  const get = path => page.evaluate(async path => {
    const r = await fetch(path, { cache: 'no-store' });
    return { status: r.status, body: await r.text() };
  }, path);
  return { rec, save, shot, step, gpu, get };
}
