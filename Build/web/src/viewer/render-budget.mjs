// S09e: deterministic device render budget. Same device facts -> same frozen budget; computed once per mount.
// Reduced tier: viewport < 768 CSS px, < 4 GiB device memory or < 4 cores (unknown/invalid facts are ignored).
const TIERS = {
  full: { maxPixelRatio: 2, maxPoints: 2_000_000, antialias: true }, // maxPoints = artifact-loader default point limit
  reduced: { maxPixelRatio: 1.5, maxPoints: 250_000, antialias: false },
};
const known = (v) => typeof v === 'number' && Number.isFinite(v) && v > 0;

/** { devicePixelRatio, viewportWidthPx, deviceMemoryGiB?, cores? } -> frozen { tier, pixelRatio, maxPoints, antialias }. */
export function renderBudget({ devicePixelRatio, viewportWidthPx, deviceMemoryGiB, cores } = {}) {
  const small = known(viewportWidthPx) && viewportWidthPx < 768;
  const weak = (known(deviceMemoryGiB) && deviceMemoryGiB < 4) || (known(cores) && cores < 4);
  const tier = small || weak ? 'reduced' : 'full';
  const t = TIERS[tier];
  return Object.freeze({ tier, pixelRatio: Math.min(known(devicePixelRatio) ? devicePixelRatio : 1, t.maxPixelRatio), maxPoints: t.maxPoints, antialias: t.antialias });
}

/** Browser device facts for renderBudget (read once at mount). Width = narrower of layout viewport and screen,
 * because a phone page without a viewport meta tag reports a ~980 px layout viewport. */
export function probeDevice(g = globalThis) {
  const widths = [g.innerWidth, g.screen?.width].filter(known);
  return { devicePixelRatio: g.devicePixelRatio, viewportWidthPx: widths.length ? Math.min(...widths) : undefined, deviceMemoryGiB: g.navigator?.deviceMemory, cores: g.navigator?.hardwareConcurrency };
}

/** Keep every ceil(n/maxPoints)-th xyz/rgb point (deterministic); original arrays when already within budget. */
export function decimatePoints(positions, colors, maxPoints) {
  if (!Number.isSafeInteger(maxPoints) || maxPoints < 1) throw new RangeError('maxPoints must be a positive integer');
  if (positions.length % 3 || colors.length !== positions.length) throw new RangeError('positions/colors must be matching xyz/rgb arrays');
  const n = positions.length / 3;
  if (n <= maxPoints) return { positions, colors, count: n };
  const stride = Math.ceil(n / maxPoints), count = Math.ceil(n / stride);
  const p = new Float32Array(count * 3), c = new Uint8Array(count * 3);
  for (let k = 0; k < count; k++) {
    const s = k * stride * 3;
    p.set(positions.subarray(s, s + 3), k * 3); c.set(colors.subarray(s, s + 3), k * 3);
  }
  return { positions: p, colors: c, count };
}
