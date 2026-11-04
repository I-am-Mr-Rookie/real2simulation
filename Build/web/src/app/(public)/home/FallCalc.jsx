'use client';
import { useState } from 'react';

// N90 close: an actual input. Fall time t = sqrt(2h/g) with g = 9.81 m/s^2 and no air drag, computed here (SIMULATED).
const G = 9.81, fall = (h) => Math.sqrt((2 * h) / G);

export default function FallCalc() {
  const [h, setH] = useState('1');
  const v = Number(h), ok = h !== '' && Number.isFinite(v) && v >= 0.01 && v <= 1000;
  return <form className="fall-calc card" onSubmit={(e) => e.preventDefault()}>
    <label htmlFor="fc-h">Predict first: does twice the height take twice as long? Type a drop height in metres.</label>
    <input id="fc-h" type="number" inputMode="decimal" min="0.01" max="1000" step="any" value={h} onChange={(e) => setH(e.target.value)} />
    <output htmlFor="fc-h" aria-live="polite">{ok
      ? <><span className="chip" data-tone="sim">SIMULATED</span> From {v} m: {fall(v).toFixed(3)} s. From {2 * v} m: {fall(2 * v).toFixed(3)} s, {(fall(2 * v) / fall(v)).toFixed(2)} times as long, not 2. No air drag, g = 9.81 m/s².</>
      : 'Type a height from 0.01 to 1000 m.'}</output>
  </form>;
}
