'use client';

import { useEffect, useRef, useState } from 'react';

// Clip-free replay: the stored x/y points only (SVG dot), no video. Shows a MEASURED-from-video challenge, never staged.
export default function GuessClient({ token }) {
  const [view, setView] = useState(null), [fail, setFail] = useState(''), [guess, setGuess] = useState('');
  const [answer, setAnswer] = useState(null), [i, setI] = useState(0), [busy, setBusy] = useState(false);
  const raf = useRef(0);
  useEffect(() => {
    fetch('/api/guess/' + encodeURIComponent(token), { cache: 'no-store' })
      .then((r) => (r.ok ? r.json() : Promise.reject()), () => Promise.reject())
      .then(setView, () => setFail('This challenge does not exist or was withdrawn.'));
  }, [token]);
  const tr = view?.trajectory, n = tr?.t_s.length ?? 0;
  useEffect(() => {
    if (!n) return;
    const t0 = performance.now(), dur = tr.t_s[n - 1] * 1000 || 1;
    const step = (now) => {
      const el = (now - t0) % (dur + 800), t = Math.min(el, dur) / 1000;
      let k = 0; while (k < n - 1 && tr.t_s[k + 1] <= t) k++;
      setI(k); raf.current = requestAnimationFrame(step);
    };
    raf.current = requestAnimationFrame(step);
    return () => cancelAnimationFrame(raf.current);
  }, [tr, n]);
  async function submit(e) {
    e.preventDefault(); setBusy(true); setFail('');
    try {
      const r = await fetch('/api/guess/' + encodeURIComponent(token) + '/reveal', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ guess: Number(guess) }) });
      if (!r.ok) throw new Error(); setAnswer(await r.json());
    } catch { setFail('Enter a number between 0 and 1000.'); }
    setBusy(false);
  }
  if (fail && !view) return <p role="alert">{fail}</p>;
  if (!view) return <p>Loading</p>;
  const xs = tr.x, ys = tr.y, pad = 20, W = 320, H = 360;
  const x0 = Math.min(...xs), y0 = Math.min(...ys), span = Math.max(Math.max(...xs) - x0, Math.max(...ys) - y0) || 1;
  const px = (x) => pad + ((x - x0) / span) * (W - 2 * pad), py = (y) => H - pad - ((y - y0) / span) * (H - 2 * pad);
  const path = xs.map((x, k) => (k ? 'L' : 'M') + px(x).toFixed(1) + ' ' + py(ys[k]).toFixed(1)).join('');
  const q = answer?.quantity;
  return <>
    <p className="lede">{view.question} Watch the replay, then guess.</p>
    <svg viewBox={'0 0 ' + W + ' ' + H} role="img" aria-label="Replay of the tracked object's path" style={{ maxWidth: 360, width: '100%', border: '1px solid currentColor' }}>
      <path d={path} fill="none" stroke="currentColor" strokeOpacity=".3" />
      <circle cx={px(xs[i])} cy={py(ys[i])} r="8" fill="currentColor" />
    </svg>
    <p className="lib-meta">Replay of tracked points only, no video. Path span {span.toFixed(2)} {tr.unit}. Scale comes from a size the sharer stated (scale unverified).</p>
    {!answer && <form onSubmit={submit}>
      <label>Your guess for g (m/s^2) <input type="number" step="any" min="0" max="1000" required value={guess} onChange={(e) => setGuess(e.target.value)} style={{ minHeight: 44 }} /></label>
      <button type="submit" disabled={busy} style={{ minHeight: 44, padding: '0 14px' }}>Reveal</button>
      {fail && <p role="alert">{fail}</p>}
    </form>}
    {answer && <div role="status">
      <p>You guessed {answer.guess} m/s^2. Measured: <strong>{q.value.toFixed(2)} ± {q.uncertainty == null ? 'unknown' : q.uncertainty.toFixed(2)} m/s^2</strong> ({q.label}).</p>
      <p className="lib-meta">{answer.label}. {answer.note} Difference: {answer.difference.toFixed(2)} m/s^2.</p>
    </div>}
  </>;
}
