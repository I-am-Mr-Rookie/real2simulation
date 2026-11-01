// N24: auto-frame the loaded room. Robust bounds (quantiles drop stray reconstruction points) and the camera distance
// that fits the bounding sphere in a perspective view. Pure, Node-testable.
export function robustBounds(positions, q = 0.02) {
  const n = Math.floor((positions?.length ?? 0) / 3);
  if (!n) return null;
  const min = [], max = [];
  for (let a = 0; a < 3; a += 1) {
    const v = new Float64Array(n);
    for (let i = 0; i < n; i += 1) v[i] = positions[i * 3 + a];
    v.sort();
    min.push(v[Math.floor(q * (n - 1))]); max.push(v[Math.ceil((1 - q) * (n - 1))]);
  }
  const center = min.map((m, a) => (m + max[a]) / 2);
  const radius = Math.max(1e-3, Math.hypot(...max.map((m, a) => m - min[a])) / 2);
  return { min, max, center, radius };
}

// Distance from the centre so a sphere of this radius fills the narrower field of view (margin > 1 leaves space).
export function fitDistance(radius, fovDeg, aspect = 1, margin = 1.05) {
  const v = (fovDeg * Math.PI) / 360, hfov = Math.atan(Math.tan(v) * Math.max(0.1, aspect));
  return (margin * radius) / Math.sin(Math.min(v, hfov));
}
