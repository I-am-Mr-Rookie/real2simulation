// S10b: deterministic fixed-step classical RK4. Dynamics own the state shape and units.
const bad = (m) => { throw new RangeError(`INVALID_RK4: ${m}`); };
const validVector = (v) => Array.isArray(v) && Number.isSafeInteger(v.length) && v.length > 0 && Array.from({ length: v.length }, (_, i) => Object.prototype.hasOwnProperty.call(v, i)).every(Boolean) && v.every((x) => typeof x === 'number' && Number.isFinite(x));
const same = (a, b) => a.length === b.length;

export function rk4Step(state, dt, dynamics) {
  if (!validVector(state)) bad('state must be a finite non-empty vector');
  if (typeof dt !== 'number' || !Number.isFinite(dt) || dt <= 0) bad('dt must be finite and positive');
  if (typeof dynamics !== 'function') bad('dynamics must be a function');
  const deriv = (s) => { if (!validVector(s)) bad('intermediate state is not finite and dense'); const d = dynamics([...s]); if (!validVector(d) || !same(d, s)) bad('dynamics returned invalid derivative'); return d; };
  const k1 = deriv(state);
  const mid = (k) => state.map((x, i) => x + dt * k[i] / 2);
  const k2 = deriv(mid(k1)); const k3 = deriv(mid(k2)); const k4 = deriv(state.map((x, i) => x + dt * k3[i]));
  const next = state.map((x, i) => x + dt * (k1[i] + 2 * k2[i] + 2 * k3[i] + k4[i]) / 6);
  if (!validVector(next)) bad('state became non-finite'); return next;
}

export function integrateRK4(state, dt, steps, dynamics) {
  if (!validVector(state)) bad('state must be a finite non-empty vector');
  if (typeof dt !== 'number' || !Number.isFinite(dt) || dt <= 0) bad('dt must be finite and positive');
  if (!Number.isSafeInteger(steps) || steps < 0 || steps > 1_000_000) bad('steps must be a safe integer in [0, 1000000]');
  if (typeof dynamics !== 'function') bad('dynamics must be a function');
  let current = [...state]; const trajectory = [Object.freeze([...current])];
  for (let i = 0; i < steps; i++) { current = rk4Step(current, dt, dynamics); trajectory.push(Object.freeze([...current])); }
  return Object.freeze(trajectory);
}
