// S15ah AA contrast self-check over the light/dark token blocks in app/styles.css (text 4.5:1, UI borders 3:1). Exits non-zero on failure.
import { readFileSync } from 'node:fs';
const css = readFileSync(new URL('../../Build/web/src/app/styles.css', import.meta.url), 'utf8');
const block = (sel) => Object.fromEntries([...css.slice(css.indexOf(sel)).split('}')[0].matchAll(/--r2s-([a-z0-9-]+):\s*(#[0-9a-f]{6})/g)].map((m) => [m[1], m[2]]));
const lum = (hex) => { const c = [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16) / 255).map((v) => (v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4)); return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]; };
const ratio = (a, b) => { const [x, y] = [lum(a), lum(b)].sort((p, q) => q - p); return (x + 0.05) / (y + 0.05); };
let bad = 0;
for (const sel of [':root, :root[data-theme="light"]', ':root[data-theme="dark"]']) {
  const t = block(sel);
  const pairs = [['ink', 'bg', 4.5], ['ink', 'surface', 4.5], ['muted', 'bg', 4.5], ['muted', 'surface', 4.5], ['accent', 'surface', 4.5], ['accent-ink', 'accent', 4.5],
    ['warn', 'surface', 4.5], ['danger', 'surface', 4.5], ['ok', 'surface', 4.5], ['ink', 'accent-soft', 4.5], ['surface', 'ok', 4.5], ['border-strong', 'surface', 3], ['border-strong', 'bg', 3], ['focus', 'surface', 3]];
  for (const [f, b, min] of pairs) { const r = ratio(t[f], t[b]); const ok = r >= min; bad += !ok; console.log(sel.padEnd(34), (f + '/' + b).padEnd(24), r.toFixed(2), ok ? 'ok' : 'FAIL <' + min); }
}
if (bad) { console.error(bad + ' contrast failures'); process.exit(1); }
