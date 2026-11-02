// N49: room shell objects (block.look) drawn as simple, recognisable class shapes at the measured box size and the
// video colour. Drawing only: physics keeps the block's box (or its SF3D mesh), so a table top still holds a ball.
import * as THREE from 'three';

const shade = (hex, k) => new THREE.Color(hex).multiplyScalar(k);

// Parts as [cx, cy, cz, sx, sy, sz, colour factor] in the object's own box (size s, centred at 0).
export function lookParts(category, s) {
  const [x, y, z] = s, X = x / 2, Y = y / 2, Z = z / 2;
  const leg = Math.min(0.06, 0.12 * Math.min(x, z)), t = Math.min(0.05, 0.15 * y);
  const legs = (h) => [[-1, -1], [-1, 1], [1, -1], [1, 1]].map(([i, k]) => [i * (X - leg / 2), -Y + h / 2, k * (Z - leg / 2), leg, h, leg, 0.6]);
  switch (category) {
    case 'table': case 'desk': return [[0, Y - t / 2, 0, x, t, z, 1], ...legs(y - t)];
    case 'chair': { const seat = 0.5 * y, b = Math.min(0.06, 0.15 * z);
      return [[0, -Y + seat - t / 2, 0, x, t, z, 1], [0, -Y + seat + (y - seat) / 2, -Z + b / 2, x, y - seat, b, 0.85], ...legs(seat - t)]; }
    case 'sofa': { const base = 0.45 * y, back = 0.25 * z, arm = Math.min(0.2, 0.12 * x);
      return [[0, -Y + base / 2, 0, x, base, z, 1], [0, 0, -Z + back / 2, x, y, back, 0.85],
        [-X + arm / 2, -Y + 0.65 * y / 2, 0, arm, 0.65 * y, z, 0.9], [X - arm / 2, -Y + 0.65 * y / 2, 0, arm, 0.65 * y, z, 0.9]]; }
    case 'bed': { const frame = 0.4 * y, head = Math.min(0.08, 0.1 * x);
      return [[0, -Y + frame / 2, 0, x, frame, z, 0.7], [head / 2, -Y + frame + 0.1 * y, 0, x - head, 0.2 * y, z, 1.25],
        [-X + head / 2, 0, 0, head, y, z, 0.8]]; }
    case 'shelf': case 'cabinet': { const w = Math.min(0.03, 0.1 * Math.min(x, z)), n = Math.max(2, Math.min(5, Math.round(y / 0.35)));
      return [[-X + w / 2, 0, 0, w, y, z, 1], [X - w / 2, 0, 0, w, y, z, 1], [0, 0, -Z + w / 2, x, y, w, 0.75],
        ...Array.from({ length: n + 1 }, (_, i) => [0, -Y + w / 2 + (i * (y - w)) / n, 0, x, w, z, 1])]; }
    case 'door': return [[0, 0, 0, x, y, z, 1]];
    case 'window': { const f = Math.min(0.05, 0.1 * Math.min(x, y, z) + 0.02), thin = x < z ? 0 : 2; // thin = wall-normal axis
      const bar = (cx, cy, w, h) => (thin === 0 ? [0, cy, cx, x, h, w, 1] : [cx, cy, 0, w, h, z, 1]), span = thin === 0 ? z : x, S = span / 2;
      return [bar(0, Y - f / 2, span, f), bar(0, -Y + f / 2, span, f), bar(-S + f / 2, 0, f, y), bar(S - f / 2, 0, f, y), bar(0, 0, f, y)]; }
    default: return [[0, 0, 0, x, y, z, 1]];
  }
}

// Walls fade when the camera is outside them (dollhouse view); the room origin is inside the room (camera centre).
function dollhouse(m, part) {
  part.onBeforeRender = (r, sc, camera) => {
    const p = m.getWorldPosition(new THREE.Vector3()), n = p.clone().setY(0);
    const thin = m.scale.x < m.scale.z ? new THREE.Vector3(1, 0, 0) : new THREE.Vector3(0, 0, 1);
    thin.applyQuaternion(m.getWorldQuaternion(new THREE.Quaternion()));
    if (thin.dot(n) < 0) thin.negate();
    const outside = camera.position.clone().sub(p).dot(thin) > 0;
    part.material.opacity = outside ? 0.12 : 1; part.material.transparent = outside; part.material.depthWrite = !outside;
  };
}

export function lookMesh(o, g) {
  const { category, color } = o.look;
  const tint = category === 'door' ? '#8b5a2b' : category === 'window' ? '#e5e7eb' : color;
  for (const [cx, cy, cz, sx, sy, sz, k] of lookParts(category, o.size)) {
    const m = new THREE.Mesh(new THREE.BoxGeometry(1, 1, 1), new THREE.MeshStandardMaterial({ color: shade(tint, k), roughness: 0.8 }));
    m.position.set(cx, cy, cz); m.scale.set(Math.max(sx, 1e-3), Math.max(sy, 1e-3), Math.max(sz, 1e-3)); m.userData.id = o.id;
    if (category === 'wall') dollhouse(m, m);
    g.add(m);
  }
  if (category === 'window') { // glass pane
    const [x, y, z] = o.size, glass = new THREE.Mesh(new THREE.BoxGeometry(1, 1, 1), new THREE.MeshStandardMaterial({ color: 0x93c5fd, transparent: true, opacity: 0.35 }));
    glass.scale.set(x < z ? x / 3 : x, y, x < z ? z : z / 3); glass.userData.id = o.id; g.add(glass);
  }
  return g;
}

