// Original, procedurally drawn icon (pendulum glyph). No third-party artwork,
// logos or fonts; pure Node (zlib only), deterministic pixels.
import { deflateSync } from 'node:zlib';

export const COLORS = { bg: [21, 90, 146], fg: [255, 255, 255] }; // #155a92 / white
const PIVOT = [0.5, 0.22], LEN = 0.42, SWING = (28 * Math.PI) / 180, BOB_R = 0.08;
const BOB = [PIVOT[0] + LEN * Math.sin(SWING), PIVOT[1] + LEN * Math.cos(SWING)];
const HW = { string: 0.012, bar: 0.014, arc: 0.008 };

const segDist = (p, a, b) => {
  const dx = b[0] - a[0], dy = b[1] - a[1];
  const t = Math.max(0, Math.min(1, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / (dx * dx + dy * dy)));
  return Math.hypot(p[0] - a[0] - t * dx, p[1] - a[1] - t * dy);
};
const arcDist = (p) => {
  const dx = p[0] - PIVOT[0], dy = p[1] - PIVOT[1];
  if (Math.abs(Math.atan2(dx, dy)) <= SWING) return Math.abs(Math.hypot(dx, dy) - LEN);
  const ends = [-1, 1].map((s) => [PIVOT[0] + s * LEN * Math.sin(SWING), PIVOT[1] + LEN * Math.cos(SWING)]);
  return Math.min(...ends.map((c) => Math.hypot(p[0] - c[0], p[1] - c[1])));
};
const inRoundRect = (x, y, r) => {
  const qx = Math.abs(x - 0.5) - (0.5 - r), qy = Math.abs(y - 0.5) - (0.5 - r);
  return Math.hypot(Math.max(qx, 0), Math.max(qy, 0)) + Math.min(Math.max(qx, qy), 0) <= r;
};

// variant 'any': rounded corners on transparent, larger glyph.
// variant 'maskable': full-bleed background, glyph inside the central safe zone.
export function render(size, variant) {
  const any = variant === 'any', scale = any ? 1.2 : 1, SS = 4;
  const out = Buffer.alloc(size * size * 4);
  for (let py = 0; py < size; py++) for (let px = 0; px < size; px++) {
    let r = 0, g = 0, b = 0, a = 0;
    for (let sy = 0; sy < SS; sy++) for (let sx = 0; sx < SS; sx++) {
      const x = (px + (sx + 0.5) / SS) / size, y = (py + (sy + 0.5) / SS) / size;
      if (any && !inRoundRect(x, y, 0.2)) continue;
      const q = [0.5 + (x - 0.5) / scale, 0.5 + (y - 0.5) / scale];
      let c = COLORS.bg;
      if (arcDist(q) <= HW.arc) c = c.map((v, i) => Math.round((v + COLORS.fg[i]) / 2));
      if (segDist(q, PIVOT, BOB) <= HW.string || segDist(q, [0.38, PIVOT[1]], [0.62, PIVOT[1]]) <= HW.bar ||
          Math.hypot(q[0] - BOB[0], q[1] - BOB[1]) <= BOB_R) c = COLORS.fg;
      r += c[0]; g += c[1]; b += c[2]; a++;
    }
    const o = (py * size + px) * 4, n = SS * SS;
    if (a) { out[o] = Math.round(r / a); out[o + 1] = Math.round(g / a); out[o + 2] = Math.round(b / a); }
    out[o + 3] = Math.round((255 * a) / n);
  }
  return out;
}

const CRC = Array.from({ length: 256 }, (_, n) => { let c = n; for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1; return c >>> 0; });
const crc32 = (buf) => { let c = 0xffffffff; for (const v of buf) c = CRC[(c ^ v) & 255] ^ (c >>> 8); return (c ^ 0xffffffff) >>> 0; };
const chunk = (type, data) => {
  const t = Buffer.from(type, 'ascii'), len = Buffer.alloc(4), crc = Buffer.alloc(4);
  len.writeUInt32BE(data.length); crc.writeUInt32BE(crc32(Buffer.concat([t, data])));
  return Buffer.concat([len, t, data, crc]);
};

export function encodePng(size, rgba) {
  const ihdr = Buffer.alloc(13);
  ihdr.writeUInt32BE(size, 0); ihdr.writeUInt32BE(size, 4); ihdr[8] = 8; ihdr[9] = 6; // 8-bit RGBA
  const raw = Buffer.alloc((size * 4 + 1) * size);
  for (let y = 0; y < size; y++) rgba.copy(raw, y * (size * 4 + 1) + 1, y * size * 4, (y + 1) * size * 4);
  return Buffer.concat([Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]), chunk('IHDR', ihdr),
    chunk('IDAT', deflateSync(raw, { level: 9 })), chunk('IEND', Buffer.alloc(0))]);
}

// Vector source of the same glyph (any-variant geometry), 512 viewBox.
export function svg() {
  const S = 512, k = 1.2, t = (v) => ((0.5 + (v - 0.5) * k) * S).toFixed(1), d = (v) => (v * k * S).toFixed(1);
  const [bx, by] = BOB, a0 = [PIVOT[0] - LEN * Math.sin(SWING), by], a1 = [bx, by];
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" role="img" aria-label="Real2Simulation pendulum icon">
  <rect width="512" height="512" rx="102" fill="#155a92"/>
  <path d="M${t(a0[0])} ${t(a0[1])}A${d(LEN)} ${d(LEN)} 0 0 0 ${t(a1[0])} ${t(a1[1])}" fill="none" stroke="#fff" stroke-opacity=".5" stroke-width="${d(HW.arc * 2)}"/>
  <path d="M${t(0.38)} ${t(PIVOT[1])}H${t(0.62)}M${t(PIVOT[0])} ${t(PIVOT[1])}L${t(bx)} ${t(by)}" fill="none" stroke="#fff" stroke-linecap="round" stroke-width="${d(HW.string * 2)}"/>
  <circle cx="${t(bx)}" cy="${t(by)}" r="${d(BOB_R)}" fill="#fff"/>
</svg>
`;
}
