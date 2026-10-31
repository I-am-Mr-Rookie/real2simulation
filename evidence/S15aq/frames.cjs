const { chromium } = require(process.argv[3]);
const out = process.argv[2]; const url = 'http://127.0.0.1:3917/';
(async () => {
  const b = await chromium.launch();
  for (const [w, hgt, rm] of [[1280, 800, 'no-preference'], [390, 844, 'no-preference'], [1280, 800, 'reduce']]) {
    const p = await b.newPage({ viewport: { width: w, height: hgt }, reducedMotion: rm });
    await p.goto(url, { waitUntil: 'networkidle' });
    const H = await p.evaluate(() => document.documentElement.scrollHeight);
    const sw = await p.evaluate(() => document.documentElement.scrollWidth);
    console.log(w, rm, 'scrollHeight', H, 'scrollWidth', sw);
    for (let i = 0; i <= 10; i++) {
      const y = Math.round((H - hgt) * i / 10);
      await p.evaluate((y) => window.scrollTo(0, y), y); await p.waitForTimeout(250);
      await p.screenshot({ path: out + '/' + w + '-' + rm + '-' + String(i).padStart(2, '0') + '.png' });
    }
    await p.close();
  }
  await b.close();
})();
