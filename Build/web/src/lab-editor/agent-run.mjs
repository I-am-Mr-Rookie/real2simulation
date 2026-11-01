// N12/N29: server-side bridge for the agent lab tools. stdin {op: 'validate' | 'run', scene, duration_s?}; stdout JSON.
// Validation is the editor's own validateScene; physics is the editor's own Rapier world (physics.mjs createPhysics,
// room collision proxy included) so agent numbers match Play. RK4 is only the fallback when Rapier cannot load.
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { validateScene } from './scene.mjs';
import { DT, MAX_SAMPLES, movingStart, createPhysics, loadRapier } from './physics.mjs';
import { integrateRK4 } from '../../../simulator/rk4.mjs';

export const ENGINE = 'Rapier (same world as the editor Play, room collision proxy included), dt 1/120 s';
export const FALLBACK_ENGINE = 'FALLBACK server RK4 (Build/simulator/rk4.mjs, Rapier failed to load), dt 1/120 s, no contacts except the floor stop';

const traced = (scene) => scene.objects.filter((o) => o.sensor && o.kind !== 'ramp' && !(o.fixed && (o.kind === 'ball' || o.kind === 'block')));

// Free-flight steps satisfy p[n+1] - 2 p[n] + p[n-1] = g dt^2; the first step that breaks it is the first contact.
export function firstContact(samples, g) {
  const tol = 0.25 * Math.hypot(...g) * DT * DT + 1e-7;
  for (let n = 1; n + 1 < samples.length; n += 1) {
    const [a, b, c] = [samples[n - 1].p, samples[n].p, samples[n + 1].p];
    if (Math.hypot(...[0, 1, 2].map((i) => c[i] - 2 * b[i] + a[i] - g[i] * DT * DT)) > tol) return n;
  }
  return -1;
}

// Same Rapier world as the editor; ball and block traces end at their first contact (the fitter measures free flight).
export function simulateRapier(R, sceneInput, durationS = 10) {
  const scene = validateScene(sceneInput);
  const steps = Math.round(Math.min(Math.max(Number(durationS) || 10, 0.1), (MAX_SAMPLES - 1) * DT) / DT);
  const sim = createPhysics(R, scene);
  try {
    sim.step(steps);
    const traces = traced(scene).map((o) => {
      const t = sim.trace(o.id);
      const hit = o.kind === 'ball' || o.kind === 'block' ? firstContact(t.samples, scene.gravity) : -1;
      // shortcut: floor test uses scene y as up (room jobs and the agent use gravity -y); tilted gravity reports surface_contact.
      // samples[hit] is the last free-flight sample; the next one is the first after the contact impulse.
      const onFloor = hit >= 0 && scene.room.kind !== 'none' && t.samples[hit + 1].p[1] - Math.max(...o.size) / 2 <= scene.room.floor_y + 0.02;
      return { ...t, engine: ENGINE, ended: hit < 0 ? 'duration' : onFloor ? 'floor_contact' : 'surface_contact', samples: hit < 0 ? t.samples : t.samples.slice(0, hit + 1) };
    });
    return { status: 'ok', label: 'SIMULATED', engine: ENGINE, scene, traces };
  } finally { sim.free(); }
}

export async function simulate(sceneInput, durationS = 10) {
  let R;
  try { R = await loadRapier(); } catch { return simulateRK4(sceneInput, durationS); }
  return simulateRapier(R, sceneInput, durationS);
}

// shortcut: pendulum swings and springs stretch along scene -y with |g|; tilted gravity or anchors need the browser Rapier run.
export function simulateRK4(sceneInput, durationS = 10) {
  const scene = validateScene(sceneInput);
  const dur = Math.min(Math.max(Number(durationS) || 10, 0.1), (MAX_SAMPLES - 1) * DT);
  const steps = Math.round(dur / DT), g = scene.gravity, gAbs = Math.hypot(...g);
  const floor = scene.room.kind === 'none' ? -Infinity : scene.room.floor_y;
  const traces = [];
  for (const o of traced(scene)) {
    let pos;
    if (o.kind === 'pendulum') {
      const L = o.params.length;
      const path = integrateRK4([(o.params.angle_deg * Math.PI) / 180, 0], DT, steps, ([th, w]) => [w, -(gAbs / L) * Math.sin(th)]);
      pos = path.map(([th]) => [o.position[0] + L * Math.sin(th), o.position[1] - L * Math.cos(th), o.position[2]]);
    } else if (o.kind === 'spring') {
      const { rest_length: r, stiffness: k, damping: c, stretch } = o.params;
      const path = integrateRK4([stretch, 0], DT, steps, ([s, v]) => [v, (-k * s - c * v) / o.mass + gAbs]);
      pos = path.map(([s]) => [o.position[0], o.position[1] - (r + s), o.position[2]]);
    } else {
      const path = integrateRK4([...movingStart(o), ...o.velocity], DT, steps, (s) => [s[3], s[4], s[5], ...g]);
      const half = o.size[1] / 2;
      const hit = path.findIndex((s) => s[1] - half <= floor);
      pos = (hit < 0 ? path : path.slice(0, Math.max(hit, 1))).map((s) => s.slice(0, 3));
    }
    const ended = (o.kind === 'ball' || o.kind === 'block') && pos.length < steps + 1 ? 'floor_contact' : 'duration';
    traces.push({ version: 'lab-trace-v1', label: 'SIMULATED', object_id: o.id, kind: o.kind, frame: 'scene', units: { t: 's', p: 'm' },
      dt: DT, gravity: g, engine: FALLBACK_ENGINE, ended, truncated: false, samples: pos.map((p, i) => ({ t: Number((i * DT).toFixed(9)), p })) });
  }
  return { status: 'ok', label: 'SIMULATED', engine: FALLBACK_ENGINE, scene, traces };
}

if (process.argv[1] && fileURLToPath(import.meta.url) === process.argv[1]) {
  try {
    const req = JSON.parse(readFileSync(0, 'utf8'));
    const out = req.op === 'validate' ? { status: 'ok', scene: validateScene(req.scene) } : req.op === 'run' ? await simulate(req.scene, req.duration_s) : null;
    process.stdout.write(JSON.stringify(out ?? { status: 'error', error: 'op must be validate or run' }));
  } catch (e) {
    process.stdout.write(JSON.stringify({ status: 'error', error: e?.name === 'SceneError' || e?.constructor?.name === 'SceneError' || e instanceof TypeError ? String(e.message).slice(0, 300) : 'simulation failed' }));
  }
}
