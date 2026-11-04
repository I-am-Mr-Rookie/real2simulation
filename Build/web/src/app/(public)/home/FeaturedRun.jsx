import Link from 'next/link';
import run from './featured-st03.json';
import phone from './featured-own07.json';
import sweep from './featured-own-sweep.json';
import agentLog from './featured-agent.json';
import measuredTurn from './featured-agent-measured.json';
import { chartGeom, fmtPm, gravityCheck } from '../../../workspace/measure.mjs';
import './featured.css';

// N89: one real hosted-SAM run shown publicly. Every number is read from featured-st03.json, a verbatim copy of
// evidence/N07/live-st03.json (equality checked in tests/web-private/featured-run.test.mjs); the chart reuses the workspace geometry.
const r = run.result, q = r.quantity, g = chartGeom(r), check = gravityCheck(r);
// N89: the owner's own phone drop (OWN07, private clip: only the derived track is public), verbatim copy of
// evidence/N89/live-own07-book-drop.json, the live pipeline output after the impact-frame fix.
const p = phone.result, pq = p.quantity, pg = chartGeom(p), pcheck = gravityCheck(p);
// N89: all 12 owner phone drops through the same live pipeline, one run each, none dropped (verbatim copy of
// evidence/N89/own-sweep/summary.json). Stats are computed here from those rows, never typed.
const measured = sweep.rows.filter((x) => x.motion === 'free_fall' && x.unit === 'm/s^2');
const vals = measured.map((x) => x.value).sort((a, b) => a - b), mid = vals.length >> 1;
const median = vals.length % 2 ? vals[mid] : (vals[mid - 1] + vals[mid]) / 2;
const sd = Math.sqrt(vals.reduce((s, v, _, a) => s + (v - vals.reduce((x, y) => x + y, 0) / a.length) ** 2, 0) / (vals.length - 1));
const below = measured.filter((x) => x.value + 2 * x.sigma < 9.81).length;

function Sweep() {
  const W = 400, row = 22, L = 58, R = W - 14, top = 18, H = top + sweep.rows.length * row + 26, lo = 6, hi = 11;
  const X = (v) => L + ((v - lo) / (hi - lo)) * (R - L);
  return <svg viewBox={'0 0 ' + W + ' ' + H} role="img" aria-label={'Fitted g with 1 sigma bars for ' + sweep.rows.length + ' phone drops, against Earth g 9.81'}>
    {[6, 7, 8, 9, 10, 11].map((v) => <g key={v}><line x1={X(v)} x2={X(v)} y1={top - 6} y2={H - 22} className="fr-grid" /><text x={X(v)} y={H - 8} textAnchor="middle">{v}</text></g>)}
    <line x1={X(9.81)} x2={X(9.81)} y1={top - 10} y2={H - 22} className="fr-earth" /><text x={X(9.81)} y={top - 10} textAnchor="middle" className="fr-earth-t">9.81</text>
    {sweep.rows.map((x, i) => { const y = top + i * row + row / 2, ok = measured.includes(x);
      return <g key={x.clip}><text x={L - 8} y={y + 3.5} textAnchor="end">{x.clip}</text>
        {ok ? <><line x1={X(x.value - x.sigma)} x2={X(x.value + x.sigma)} y1={y} y2={y} className="fr-curve" /><circle cx={X(x.value)} cy={y} r={3.2} className="fr-pt" /></>
          : <text x={L + 4} y={y + 3.5} className="fr-miss">{x.status === 'failed' ? 'failed: ' + String(x.reason?.message ?? 'no track') : 'no g: ' + x.motion}</text>}</g>; })}
  </svg>;
}
// N89: one recorded Muse Spark turn in the lab editor (evidence/N28/run1-turns.json, verbatim copy): request, tool calls, reply.
const turn = agentLog.turns[0];

function Chart({ g, what }) {
  const b = g.box;
  return <svg viewBox={'0 0 ' + g.W + ' ' + g.H} role="img" aria-label={'Tracked ' + what + ': ' + g.yLabel + ' against ' + g.xLabel + ' with the fitted curve and its 1 sigma band'}>
    {g.yTicks.map((t) => <g key={'y' + t.label}><line x1={b.L} x2={b.R} y1={t.y} y2={t.y} className="fr-grid" /><text x={b.L - 6} y={t.y + 3.5} textAnchor="end">{t.label}</text></g>)}
    {g.xTicks.map((t) => <g key={'x' + t.label}><line x1={t.x} x2={t.x} y1={b.T} y2={b.B} className="fr-grid" /><text x={t.x} y={b.B + 14} textAnchor="middle">{t.label}</text></g>)}
    <path d={'M' + b.L + ' ' + b.T + 'V' + b.B + 'H' + b.R} className="fr-axis" />
    {g.band && <path d={g.band} className="fr-band" />}
    {g.curve && <path d={g.curve} className="fr-curve" />}
    {g.points.map((p, i) => <circle key={i} cx={p.cx} cy={p.cy} r={2.6} className="fr-pt" />)}
    <text x={(b.L + b.R) / 2} y={g.H - 4} textAnchor="middle">{g.xLabel}</text>
    <text x={11} y={(b.T + b.B) / 2} textAnchor="middle" transform={'rotate(-90 11 ' + (b.T + b.B) / 2 + ')'}>{g.yLabel}</text>
  </svg>;
}

export default function FeaturedRun() {
  const n = r.trajectory.t_s.length;
  return <section className="show featured-run" aria-labelledby="real-run">
    <h2 id="real-run">Real runs, start to finish</h2>
    <p className="show-line">Twelve phone clips and one stock clip went through the live pipeline. These are the stored outputs, not mock-ups.</p>
    <div className="card fr-phone fr-sweep">
      <div>
        <span className="chip" data-tone="ok">MEASURED</span>
        <h3>Twelve phone drops, every result shown</h3>
        <p className="fr-value"><strong>{measured.length} of {sweep.rows.length}</strong> gave a free-fall fit: median {median.toFixed(2)} m/s², spread {sd.toFixed(2)} (1 sd), range {vals[0].toFixed(2)} to {vals.at(-1).toFixed(2)}.</p>
        <p>The same book dropped onto a table, filmed by the maker on a Realme C53 phone at 30 fps, each clip run once through the live pipeline (hosted SAM 3.1 plus the fitter) with the same prompt "{sweep.target_text}" and the ruler-measured {sweep.known_size}. None was left out.</p>
        <p>Honest reading: the method is repeatable, but it reads low. {below} of {measured.length} results sit more than 2 sigma below 9.81, so the error bars miss a systematic error we have not yet explained. Treat a phone result as a classroom estimate, not a calibrated g.</p>
      </div>
      <figure className="fr-chart"><Sweep /><figcaption>Dot: fitted g. Bar: 1 sigma from the fitter and the scale. Line: Earth g.</figcaption></figure>
    </div>
    <div className="card fr-phone">
      <div>
        <span className="chip" data-tone="ok">MEASURED</span>
        <h3>One of them in detail (OWN07)</h3>
        <p className="fr-value"><strong>{fmtPm(pq.value, pq.uncertainty)} {pq.unit.replace('^2', '²')}</strong> {pq.name}, 1 sigma.</p>
        {pcheck && <p>{pcheck.text} It is one of the twelve above and reads higher than their median ({median.toFixed(2)}), so it is a worked example, not the typical result.</p>}
        <p>A book dropped onto a table, filmed by the maker on a Realme C53 phone at 30 fps, run through the live pipeline on {phone.utc.slice(0, 10)}. Hosted SAM 3.1 tracked {p.track.tracked_frames} frames; the pipeline kept {p.segment.frames} frames of free fall ({p.segment.duration_s.toFixed(2)} s) and cut the landing frames. Scale: {p.scale.object}, measured with a ruler by the maker ({p.scale.label}). {p.clock[0].toUpperCase() + p.clock.slice(1)}.</p>
        <p className="fr-meta mono">Recorded cost {'$' + p.cost_usd} · {phone.seconds} s end to end · the video is a private owner clip, so only the tracked dots are public</p>
        <p><Link className="primary-link" href="/lab?editor=1&sample=own07">Replay this drop in 3D next to a SIMULATED ball at 9.81</Link></p>
      </div>
      <figure className="fr-chart"><Chart g={pg} what="book" /><figcaption>Dots: tracked book (MEASURED). Line: fitted curve. Its 1 sigma band is thinner than the line here.</figcaption></figure>
    </div>
    <h3 className="fr-sub">A stock clip, and what the pipeline says when it cannot be right</h3>
    <p className="show-line">A public stock clip went through the same pipeline on {run.utc.slice(0, 10)}.</p>
    <ol className="fr-steps">
      <li className="card">
        <span className="chip" data-tone="ok">RECORDED</span>
        <h3>1. The clip</h3>
        <img src="/featured/st03-frames.webp" width={824} height={600} loading="lazy" alt="Four frames of an apple falling from a hand onto a cushion, frames 56, 63, 70 and 77." />
        <p>Frames {r.segment.first_frame}, 63, 70 and {r.segment.last_frame}. "Woman dropping apple on ground" by Roman Odintsov, Pexels License. Cropped.</p>
      </li>
      <li className="card">
        <span className="chip" data-tone="ok">MEASURED</span>
        <h3>2. Meta SAM 3.1 tracks it</h3>
        <p>Hosted SAM 3.1 on the Meta Model API followed the apple through all {r.track.tracked_frames} frames. The pipeline code kept the {n} frames of free fall ({r.segment.duration_s.toFixed(2)} s).</p>
        <p className="fr-meta mono">{r.track.label}<br />Recorded cost {'$' + r.cost_usd} · {run.seconds} s end to end</p>
      </li>
      <li className="card">
        <span className="chip" data-tone="sim">fitted</span>
        <h3>3. The fitter picks a model</h3>
        <figure className="fr-chart"><Chart g={g} what="apple" /><figcaption>Dots: tracked apple. Line: fitted curve. Band: 1 sigma.</figcaption></figure>
        <p className="fr-value"><strong>{fmtPm(q.value, q.uncertainty)} {q.unit.replace('^2', '²')}</strong> {q.name}, 1 sigma.</p>
        <p className="fr-meta">{r.fit.model_selection.replace(/ \(.*\)$/, '')}: constant acceleration beats constant velocity on both axes.</p>
      </li>
      <li className="card">
        <span className="chip" data-tone="warn">what-if</span>
        <h3>4. It says what it cannot know</h3>
        <p>{r.scale.label}.</p>
        <p>{r.clock}.</p>
        {check && <p>{check.text}</p>}
      </li>
    </ol>
    <p className="fr-cta"><Link className="primary-link" href="/lab?editor=1&sample=st03">Replay this run in 3D and change gravity</Link></p>
    <div className="card fr-agent">
      <span className="chip" data-tone="ok">MEASURED</span>
      <h3>Muse runs the real pipeline from one sentence</h3>
      <p>A recorded call to Meta {measuredTurn.model} on {measuredTurn.utc.slice(0, 10)} in a signed-in test workspace, on the 2.6 s crop of the clip above, unedited. Muse found the video, started hosted SAM 3.1 tracking with the size it was given, called fit too early, then fitted again once tracking finished.</p>
      <dl>
        <dt>You</dt><dd>{measuredTurn.sent}</dd>
        <dt>Tools it called</dt><dd className="mono">{measuredTurn.tools.join(' → ')}</dd>
        <dt>Muse</dt><dd>{measuredTurn.reply}</dd>
        <dt>Fit</dt><dd>{fmtPm(measuredTurn.quantity.value, measuredTurn.quantity.uncertainty)} {measuredTurn.quantity.unit}, {measuredTurn.quantity.label}, {measuredTurn.frames} frames.</dd>
      </dl>
      <p>Far below 9.81 m/s^2: the stock clip plays in slow motion, or the apple is not 7 cm. The workspace prints this as a what-if instead of hiding it.</p>
    </div>
    <div className="card fr-agent">
      <span className="chip" data-tone="sim">SIMULATED</span>
      <h3>Muse also runs the virtual lab</h3>
      <p>A recorded call to Meta {turn.model} on {turn.utc.slice(0, 10)}, unedited, on a SIMULATED drop in the lab editor, not the apple clip above. The agent turns a sentence into lab actions and reads the numbers back from the physics engine, not from its own guess.</p>
      <dl>
        <dt>You</dt><dd>{turn.sent}</dd>
        <dt>Tools it called</dt><dd className="mono">{turn.tool_calls.map((c) => c.name).join(' → ')}</dd>
        <dt>Muse</dt><dd>{turn.reply}</dd>
      </dl>
    </div>
    <p className="fr-cta"><Link href="/sign-up">Measure your own clip</Link> or <Link href="/lab?editor=1&template=physics-lab">try a physics lab lesson: does twice the height take twice as long?</Link> No video needed.</p>
  </section>;
}
