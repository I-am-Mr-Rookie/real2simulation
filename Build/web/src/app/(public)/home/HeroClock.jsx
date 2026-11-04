'use client';
import { useEffect, useRef } from 'react';
import run from './featured-st03.json';
import { chartGeom, fmtPm } from '../../../workspace/measure.mjs';

// N90 scroll-craft signature: scroll is the clip clock. The hero steps the four RECORDED stills of the ST03 apple drop,
// lights each MEASURED dot as its frame passes and moves a marker along the fitted curve. Every value is read from
// featured-st03.json (verbatim evidence), none is typed here.
const r = run.result, tr = r.trajectory, g = chartGeom(r), q = r.quantity, b = g.box;
const T1 = tr.t_s.at(-1), FPS = (r.segment.last_frame - r.segment.first_frame) / T1;
// chartGeom's browser refit samples the curve uniformly in time, so vertex i sits at t = T1 * i / (n - 1).
const CURVE = g.curve.slice(1).split('L').map((s) => s.trim().split(' ').map(Number));
const STILLS = [56, 63, 70, 77]; // frames in /featured/st03-frames.webp, left to right
const clamp = (x) => Math.min(1, Math.max(0, x));

export default function HeroClock({ children }) {
  const ref = useRef(null);
  useEffect(() => {
    const fig = ref.current, act = fig.closest('[data-sc-act]') || fig;
    const dots = [...fig.querySelectorAll('.hc-dot')], frames = [...fig.querySelectorAll('.hc-frame')];
    const rect = fig.querySelector('#hc-clip rect'), ball = fig.querySelector('.hc-ball');
    const out = Object.fromEntries([...fig.querySelectorAll('[data-hc]')].map((e) => [e.dataset.hc, e]));
    let raf = 0, lastT = -1;
    const draw = () => {
      raf = 0;
      const vh = innerHeight, a = act.getBoundingClientRect();
      // pinned (desktop): progress through the act; unpinned (phone, reduced motion): progress while the figure crosses the view
      const p = clamp(act.classList.contains('sc-act--pinned') ? -a.top / Math.max(a.height - vh, 1) : (vh * 0.95 - fig.getBoundingClientRect().top) / (vh * 0.6));
      fig.style.setProperty('--hp', p.toFixed(4));
      const t = T1 * clamp((p - 0.04) / 0.7);
      if (Math.abs(t - lastT) < 1e-4) return;
      lastT = t;
      const n = tr.t_s.filter((s) => s <= t + 1e-6).length, frame = Math.round(r.segment.first_frame + t * FPS);
      dots.forEach((d, i) => d.classList.toggle('on', i < n));
      const k = STILLS.reduce((acc, f, i) => (f <= frame ? i : acc), 0);
      frames.forEach((f, i) => f.classList.toggle('on', i === k));
      const u = (t / T1) * (CURVE.length - 1), i0 = Math.min(CURVE.length - 2, Math.floor(u)), w = u - i0;
      const [x, y] = [0, 1].map((j) => CURVE[i0][j] + (CURVE[i0 + 1][j] - CURVE[i0][j]) * w);
      rect.setAttribute('width', Math.max(0, x - b.L + 1).toFixed(1));
      ball.setAttribute('cx', x.toFixed(1)); ball.setAttribute('cy', y.toFixed(1));
      out.frame.textContent = String(STILLS[k]);
      out.t.textContent = t.toFixed(3);
      out.n.textContent = String(n);
      out.y.textContent = String(tr.y[n - 1]);
    };
    const ask = () => { if (!raf) raf = requestAnimationFrame(draw); };
    addEventListener('scroll', ask, { passive: true }); addEventListener('resize', ask);
    draw();
    return () => { removeEventListener('scroll', ask); removeEventListener('resize', ask); cancelAnimationFrame(raf); };
  }, []);
  const p0 = g.points[0];
  return <figure className="hc" ref={ref} aria-labelledby="hc-cap">
    <div className="hc-photo slab">
      {STILLS.map((f, k) => <span key={f} className={'hc-frame' + (k ? '' : ' on')} style={{ backgroundPosition: (k * 100) / 3 + '% 50%' }} role="img"
        aria-label={'Recorded frame ' + f + ' of a stock clip: an apple falling from a hand toward a cushion.'} />)}
      <span className="chip hc-tag" data-tone="ok">RECORDED</span>
    </div>
    <div className="hc-chart slab">
      <svg viewBox={'0 0 ' + g.W + ' ' + g.H} role="img" aria-label={'Tracked apple: ' + g.yLabel + ' against ' + g.xLabel + ', ' + tr.t_s.length + ' measured dots with the fitted curve'}>
        <defs><clipPath id="hc-clip"><rect x={b.L} y={0} width={1} height={g.H} /></clipPath></defs>
        {g.yTicks.map((t) => <g key={'y' + t.label}><line x1={b.L} x2={b.R} y1={t.y} y2={t.y} className="fr-grid" /><text x={b.L - 6} y={t.y + 3.5} textAnchor="end">{t.label}</text></g>)}
        {g.xTicks.map((t) => <g key={'x' + t.label}><line x1={t.x} x2={t.x} y1={b.T} y2={b.B} className="fr-grid" /><text x={t.x} y={b.B + 14} textAnchor="middle">{t.label}</text></g>)}
        <path d={'M' + b.L + ' ' + b.T + 'V' + b.B + 'H' + b.R} className="fr-axis" />
        <g clipPath="url(#hc-clip)">{g.band && <path d={g.band} className="fr-band" />}<path d={g.curve} className="fr-curve" /></g>
        {g.points.map((d, i) => <circle key={i} cx={d.cx} cy={d.cy} r={3} className={'hc-dot' + (i ? '' : ' on')} />)}
        <circle className="hc-ball" cx={p0.cx} cy={p0.cy} r={6.5} />
        <text x={(b.L + b.R) / 2} y={g.H - 4} textAnchor="middle">{g.xLabel}</text>
        <text x={11} y={(b.T + b.B) / 2} textAnchor="middle" transform={'rotate(-90 11 ' + (b.T + b.B) / 2 + ')'}>{g.yLabel}</text>
      </svg>
    </div>
    <ul className="hc-read">
      <li><span className="chip" data-tone="ok">RECORDED</span> frame <b data-hc="frame">{STILLS[0]}</b>, t = <b data-hc="t">0.000</b> s</li>
      <li><span className="chip" data-tone="ok">MEASURED</span> <b data-hc="n">1</b> of {tr.t_s.length} dots, y = <b data-hc="y">{tr.y[0]}</b> px</li>
      <li><span className="chip" data-tone="sim">fitted</span> {fmtPm(q.value, q.uncertainty)} {q.unit.replace('^2', '²')}, <span className="hc-warn">scale unverified</span></li>
    </ul>
    <figcaption id="hc-cap">{children}</figcaption>
  </figure>;
}

