const { chromium } = require(process.argv[2]);
(async () => { const b = await chromium.launch(); const r = [];
for (const w of [320, 390, 1000, 1280]) { const p = await b.newPage({ viewport: { width: w, height: 800 } }); await p.goto('http://127.0.0.1:3917/', { waitUntil: 'networkidle' });
 r.push(await p.evaluate((w) => { const h = document.querySelector('.home-h1'); return { w, scrollWidth: document.documentElement.scrollWidth, h1: h.getBoundingClientRect().width|0, lines: [...h.children].map(s => s.scrollWidth + "/" + s.clientWidth), lineHeights: [...h.children].map(s => s.getBoundingClientRect().height|0), emDash: document.body.innerText.includes('\u2014') }; }, w)); await p.close(); }
console.log(JSON.stringify(r)); await b.close(); })();
