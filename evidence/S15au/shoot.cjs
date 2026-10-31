// S15au evidence: node shoot.cjs <outdir> <url> <tag> [full]  (codex runtime playwright-core chromium, not Chrome)
const { chromium } = require('C:/Users/HP/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright-core');
const [out, url, tag, full] = process.argv.slice(2);
const THEMES = full ? ['paper', 'light', 'dark', 'midnight', 'graphite', 'contrast'] : ['paper', 'dark', 'contrast'];
(async () => {
  const b = await chromium.launch();
  for (const theme of THEMES) for (const [w, hgt] of [[1280, 800], [375, 812]]) for (const rm of full ? ['no-preference', 'reduce'] : ['reduce']) {
    const ctx = await b.newContext({ viewport: { width: w, height: hgt }, reducedMotion: rm });
    await ctx.addInitScript((t) => localStorage.setItem('r2s.theme', t), theme);
    const p = await ctx.newPage();
    await p.goto(url, { waitUntil: 'networkidle' });
    // signed-in nav cannot be produced locally without Clerk keys: inject the AccountNav markup shape to measure the phone header
    if (full) await p.evaluate(() => { const n = document.querySelector('.site-header nav'); const s = n.querySelector('.nav-cta'); const a = document.createElement('a'); a.href = '/workspace'; a.textContent = 'Private workspace'; const av = document.createElement('span'); av.style.cssText = 'width:32px;height:32px;border-radius:50%;background:teal;flex:none'; s.replaceWith(a, av); });
    const m = await p.evaluate(() => { const d = document.documentElement; const ws = document.querySelector('.site-header a[href="/workspace"]'); const mk = [...document.querySelectorAll('.brand-mark')].find((e) => e.offsetWidth); const txt = document.body.innerText;
      return { theme: d.dataset.theme, sw: d.scrollWidth, cw: d.clientWidth, headerH: document.querySelector('.site-header').offsetHeight, mark: mk && mk.getBoundingClientRect().width, wsH: ws && ws.getBoundingClientRect().height, wordmarkFont: getComputedStyle(document.querySelector('.wordmark')).fontSize,
        gh: (() => { const g = document.querySelector('.site-header a[aria-label="GitHub repository"]'); return g ? [g.target, g.rel, g.offsetWidth] : null; })(),
        labels: ['RECORDED', 'SIMULATED', 'what-if', 'scale unverified'].every((l) => txt.includes(l)), emdash: txt.includes('\u2014') }; });
    console.log(tag, theme, w, rm, JSON.stringify(m));
    const base = out + '/' + tag + '-' + theme + '-' + w + (rm === 'reduce' ? '-rm' : '');
    await p.screenshot({ path: base + '.png', fullPage: true });
    if (full && rm === 'no-preference' && theme === 'dark') {
      const H = await p.evaluate(() => document.documentElement.scrollHeight);
      for (const f of [0.15, 0.3, 0.45, 0.6, 0.75]) { await p.evaluate((y) => window.scrollTo(0, y), Math.round((H - hgt) * f)); await p.waitForTimeout(300); await p.screenshot({ path: base + '-mid' + Math.round(f * 100) + '.png' }); }
    }
    await ctx.close();
  }
  await b.close();
})();

