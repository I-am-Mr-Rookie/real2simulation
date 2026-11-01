// N12: server-side bridge for the agent lab tools. stdin {op: 'validate' | 'run', scene, duration_s?}; stdout JSON.
// Validation is the editor's own validateScene; physics is the S10b RK4 integrator (no Rapier, no deps).
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { validateScene } from './scene.mjs';
import { DT, MAX_SAMPLES, movingStart } from './physics.mjs';
import { integrateRK4 } from '../../../simulator/rk4.mjs';

export const ENGINE = 'server RK4 (Build/simulator/rk4.mjs), dt 1/120 s, no contacts except the floor stop';

// shortcut: pendulum swings and springs stretch along scene -y with |g|; tilted gravity or anchors need the browser Rapier run.
export function simulate(sceneInput, durationS = 10) {
  const scene = validateScene(sceneInput);
  const dur = Math.min(Math.max(Number(durationS) || 10, 0.1), (MAX_SAMPLES - 1) * DT);
  const steps = Math.round(dur / DT), g = scene.gravity, gAbs = Math.hypot(...g);
  const floor = scene.room.kind === 'none' ? -Infinity : scene.room.floor_y;
  const traces = [];
  for (const o of scene.objects.filter((x) => x.sensor && x.kind !== 'ramp')) {
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
      if (o.fixed) continue;
      const path = integrateRK4([...movingStart(o), ...o.velocity], DT, steps, (s) => [s[3], s[4], s[5], ...g]);
      const half = o.size[1] / 2;
      const hit = path.findIndex((s) => s[1] - half <= floor);
      pos = (hit < 0 ? path : path.slice(0, Math.max(hit, 1))).map((s) => s.slice(0, 3));
    }
    const ended = (o.kind === 'ball' || o.kind === 'block') && pos.length < steps + 1 ? 'floor_contact' : 'duration';
    traces.push({ version: 'lab-trace-v1', label: 'SIMULATED', object_id: o.id, kind: o.kind, frame: 'scene', units: { t: 's', p: 'm' },
      dt: DT, gravity: g, engine: ENGINE, ended, truncated: false, samples: pos.map((p, i) => ({ t: Number((i * DT).toFixed(9)), p })) });
  }
  return { status: 'ok', label: 'SIMULATED', engine: ENGINE, scene, traces };
}

if (process.argv[1] && fileURLToPath(import.meta.url) === process.argv[1]) {
  try {
    const req = JSON.parse(readFileSync(0, 'utf8'));
    const out = req.op === 'validate' ? { status: 'ok', scene: validateScene(req.scene) } : req.op === 'run' ? simulate(req.scene, req.duration_s) : null;
    process.stdout.write(JSON.stringify(out ?? { status: 'error', error: 'op must be validate or run' }));
  } catch (e) {
    process.stdout.write(JSON.stringify({ status: 'error', error: e?.name === 'SceneError' || e?.constructor?.name === 'SceneError' || e instanceof TypeError ? String(e.message).slice(0, 300) : 'simulation failed' }));
  }
}
