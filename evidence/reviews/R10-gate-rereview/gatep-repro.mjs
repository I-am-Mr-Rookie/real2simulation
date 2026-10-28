// R10-gate-rereview: fresh Gate P P2 repros against pinned source.
import { freeFallTrajectory } from '../../../Build/simulator/trajectories.mjs';
import { contactAwareTrajectory } from '../../../Build/simulator/contacts.mjs';
const physics = { friction: 0.4, restitution: 0, density: 1 };
const geometry = { floorY: 0, floorHalfExtents: [5, 0.1, 5], sphereRadius: 0.1 };
const traj = (y, dt = 0.005, steps = 0) => freeFallTrajectory({ initialPosition: [0, y, 0], initialVelocity: [0, 0, 0], gravity: 9.81, dt, steps, source: 'simulated', inputProvenance: 'synthetic' });
const run = async (name, input) => { try { const o = await contactAwareTrajectory({ physics, gravity: 9.81, ...input }); const s = o.samples.find((x) => x.contact); console.log(JSON.stringify({ name, ok: true, n: o.samples.length, firstContact: s ? { t: s.time_s, bracket: s.contactBracket_s } : null })); } catch (e) { console.log(JSON.stringify({ name, ok: false, error: e.message })); } };
await run('P2-1 audit repro double overflow', { trajectory: traj(2), geometry: { ...geometry, floorY: -1e308, floorHalfExtents: [5, 1e308, 5] } });
await run('P2-1 float32-only overflow (center -3.5e38)', { trajectory: traj(2), geometry: { ...geometry, floorY: -3e38, floorHalfExtents: [5, 5e37, 5] } });
await run('P2-2 audit repro penetration y=0.05', { trajectory: traj(0.05), geometry });
await run('P2-2 penetration by 1 ulp', { trajectory: traj(0.1 - Number.EPSILON), geometry });
await run('exact touch y=r', { trajectory: traj(0.1), geometry });
await run('just above by EPSILON', { trajectory: traj(0.1 + Number.EPSILON), geometry });
await run('far-from-origin above by 1e-5 at floorY=1000 (float32 ulp ~6e-5)', { trajectory: traj(1000.1 + 1e-5), geometry: { ...geometry, floorY: 1000 } });
for (const dt of [0.005, 0.0025, 0.001]) {
  const o = await contactAwareTrajectory({ trajectory: traj(2, dt, Math.round(2 / dt)), geometry, physics, gravity: 9.81 });
  const s = o.samples.find((x) => x.contact); const a = Math.sqrt(1.9 * 2 / 9.81);
  console.log(JSON.stringify({ name: 'analytic', dt, t: s.time_s, analytic: a, err: Math.abs(s.time_s - a), within: Math.abs(s.time_s - a) <= 0.005 && s.contactBracket_s[0] <= a && a <= s.contactBracket_s[1] }));
}
