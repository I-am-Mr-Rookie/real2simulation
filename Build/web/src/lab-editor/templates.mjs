// N89: starter labs for visitors without a video. Plain lab-scene-v1 JSON; copying one saves it as the user's own lab
// (POST /api/workspace/projects with a scene), so the template itself never changes and counts against no quota.
import { defaultScene, validateScene } from './scene.mjs';

const WALL = '#d6d3d1', WOOD = '#a16207', BENCH = '#57534e';
const fixed = (id, position, size, category, color) => ({ id, kind: 'block', position, size, fixed: true, sensor: false, friction: 0.6, restitution: 0.2, look: { category, color } });
const vertical = [0, 0, 0.7071067812, 0.7071067812]; // ruler turned upright about z

// Room: 10 m wide (x), 7.5 m deep (z -5 to 2.5), 3.2 m high, open on the +z side so the lab is visible from the front.
// Furniture is fixed and records no trace, so the live graph starts on the apparatus.
function physicsLab() {
  const masses = [10, 20, 50, 100, 200, 500, 1000].map((g, i) => ({ id: 'mass-' + g + 'g', kind: 'mass', position: [0.29 + i * 0.17, 0.86, 1.6], params: { grams: g } }));
  return {
    ...defaultScene(),
    objects: [
      fixed('wall-back', [0, 1.6, -5], [10, 3.2, 0.15], 'wall', WALL),
      fixed('wall-left', [-5, 1.6, -1.25], [0.15, 3.2, 7.5], 'wall', WALL),
      fixed('wall-right', [5, 1.6, -1.25], [0.15, 3.2, 7.5], 'wall', WALL),
      fixed('window-left', [-2.8, 1.9, -4.9], [1.6, 1.1, 0.2], 'window', WALL),
      fixed('window-right', [2.8, 1.9, -4.9], [1.6, 1.1, 0.2], 'window', WALL),
      fixed('door', [-4.9, 1.05, 1], [0.14, 2.1, 1], 'door', WOOD),
      fixed('board', [0, 1.7, -4.88], [2.6, 1.1, 0.05], 'board', '#1f3a2e'),
      fixed('cabinet', [4.2, 0.9, -4.6], [1.2, 1.8, 0.5], 'cabinet', '#78716c'),
      fixed('bench-mechanics', [-3, 0.45, -3.2], [2.4, 0.9, 1.1], 'table', BENCH),
      fixed('bench-motion', [0, 0.45, -3.2], [2.4, 0.9, 1.1], 'table', BENCH),
      fixed('bench-rotation', [3, 0.45, -3.2], [2.4, 0.9, 1.1], 'table', BENCH),
      fixed('bench-cradle', [3.4, 0.45, -1.2], [1.4, 0.9, 0.8], 'table', BENCH),
      fixed('mass-table', [0.8, 0.4, 1.6], [1.6, 0.8, 0.7], 'table', WOOD),
      fixed('stool-1', [-3, 0.3, -2.3], [0.45, 0.6, 0.45], 'chair', '#44403c'),
      fixed('stool-2', [0, 0.3, -2.3], [0.45, 0.6, 0.45], 'chair', '#44403c'),
      // Free fall first: the live graph shows the first sensor, so the first Play draws a clean drop curve.
      { id: 'ball-drop', kind: 'ball', position: [-1, 2, -0.6], size: [0.06, 0.06, 0.06], mass: 0.05 },
      { id: 'photogate-1', kind: 'photogate', position: [-1, 1, -0.6] },
      { id: 'ruler-drop', kind: 'ruler', position: [-0.92, 1.01, -0.6], rotation: vertical, params: { length: 2 } },
      // Mechanics bench: simple pendulum with a protractor, and a spring with a hanging mass.
      { id: 'pendulum-1', kind: 'pendulum', position: [-3.7, 1.9, -3.2], size: [0.06, 0.06, 0.06], mass: 0.2, params: { length: 0.8, angle_deg: 20 } },
      { id: 'protractor-1', kind: 'protractor', position: [-3.7, 1.9, -3.12] },
      { id: 'spring-1', kind: 'spring', position: [-2.3, 1.8, -3.2], mass: 0.5, params: { rest_length: 0.4, stiffness: 40, damping: 0.2, stretch: 0.15 } },
      // Motion bench: dynamics cart on a 10 degree track.
      { id: 'cart-1', kind: 'cart', position: [0, 1.06, -3.2], mass: 0.5, params: { length: 1.5, angle_deg: 10 } },
      // Rotation bench: flywheel with a falling mass, Atwood machine; Newton cradle on its own bench.
      { id: 'flywheel-1', kind: 'flywheel', position: [2.4, 1.75, -3.2], mass: 1, params: { radius: 0.15, inertia: 0, hang_mass: 0.05, hang_length: 0.4 } },
      { id: 'atwood-1', kind: 'atwood', position: [3.7, 1.95, -3.2], params: { radius: 0.05, m1: 0.2, m2: 0.15, hang_length: 0.5 } },
      { id: 'cradle-1', kind: 'cradle', position: [3.4, 1.55, -1.2], params: { count: 5, length: 0.5, angle_deg: 30 } },
      // Floor stations: incline with a ball, projectile launcher, sliding blocks.
      { id: 'ramp-1', kind: 'ramp', position: [-3, 0.35, -0.6], friction: 0.3 },
      { id: 'ball-ramp', kind: 'ball', position: [-2.55, 0.72, -0.6], size: [0.08, 0.08, 0.08], mass: 0.1, friction: 0.4 },
      { id: 'launcher-1', kind: 'launcher', position: [1, 0.1, 0.6], mass: 0.05, params: { angle_deg: 45, speed: 4 } },
      { id: 'ruler-range', kind: 'ruler', position: [2, 0.01, 0.75], params: { length: 2 } },
      { id: 'block-a', kind: 'block', position: [-3, 0.1, 1.5], velocity: [1.5, 0, 0], mass: 1, friction: 0.2 },
      { id: 'block-b', kind: 'block', position: [-1.5, 0.1, 1.5], mass: 2, friction: 0.2 },
      ...masses,
    ],
  };
}

export const TEMPLATES = [
  { id: 'blank', title: 'Blank lab', blurb: 'An empty grid floor. Add any apparatus and press Play.', scene: defaultScene },
  { id: 'physics-lab', title: 'Physics lab', blurb: 'A 10 m by 7.5 m lab, open at the front: pendulum, spring, cart track, flywheel, Atwood machine, Newton cradle, incline, free fall with a photogate, launcher, collision blocks and a 10 g to 1 kg mass set.', scene: physicsLab },
];

export function templateScene(id) {
  const t = TEMPLATES.find((x) => x.id === id);
  return t ? validateScene(t.scene()) : null;
}

// Agent suggestions that use the physics lab's own apparatus (shown while its stations are in the scene, copies included).
export const PHYSICS_LAB_CARDS = [
  { id: 'period', icon: 'pendulum', title: 'Pendulum period vs length', text: 'Run pendulum-1 at lengths 0.4, 0.6, 0.8 and 1.0 m, measure each period and fit period against length.' },
  { id: 'gate', icon: 'drop', title: 'Free fall through the photogate', text: 'Run the lab and read photogate-1 for ball-drop. What g does the gate time give for the 1 m drop?' },
  { id: 'atwood', icon: 'ramp', title: 'Atwood machine', text: 'Run atwood-1 with masses 0.2 and 0.15 kg, then 0.25 and 0.15 kg. Compare each acceleration with (m1 - m2) g / (m1 + m2).' },
  { id: 'report', icon: 'report', title: 'Write report', text: 'Write the lab report.' },
];
export const hasPhysicsStations = (scene) => ['pendulum-1', 'photogate-1', 'atwood-1'].every((id) => scene.objects.some((o) => o.id === id));

