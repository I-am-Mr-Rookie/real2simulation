'use client';

import { useEffect, useRef, useState } from 'react';

const TEMPLATES = [
  ['free_fall', 'Free fall', 'Ballistic drop'],
  ['projectile', 'Projectile', 'Ballistic launch'],
  ['ramp', 'Ramp', 'Rolling motion'],
  ['pendulum', 'Pendulum', 'Oscillation'],
];
const BALLISTIC = new Set(['free_fall', 'projectile']);

function errorMessage(body, fallback) {
  return body?.error?.message || body?.error?.code || fallback;
}

function sampleRows(observations) {
  if (!Array.isArray(observations)) return [];
  const step = Math.max(1, Math.ceil(observations.length / 8));
  return observations.filter((_, index) => index % step === 0 || index === observations.length - 1).slice(0, 9);
}

function displayFit(fit) {
  const gravity = fit?.gravity && typeof fit.gravity === 'object' ? fit.gravity : null;
  const quantity = fit?.quantity && typeof fit.quantity === 'object' ? fit.quantity : null;
  const value = typeof fit?.gravity === 'number' ? fit.gravity : (gravity?.value ?? quantity?.value ?? fit?.value ?? fit?.magnitude);
  const uncertainty = typeof fit?.uncertainty === 'object' ? fit.uncertainty.value : fit?.uncertainty;
  if (typeof value !== 'number') return null;
  return { value, uncertainty, unit: gravity?.unit || quantity?.unit || fit?.unit || 'm/s²', source: fit?.source || gravity?.source || 'simulated' };
}

export default function LabClient() {
  const [template, setTemplate] = useState('free_fall');
  const [mystery, setMystery] = useState(false);
  const [session, setSession] = useState(null);
  const [fit, setFit] = useState(null);
  const [status, setStatus] = useState('idle');
  const [message, setMessage] = useState('Choose a template, then run a synthetic trial.');
  const request = useRef(null);
  const requestVersion = useRef(0);

  const reset = () => { request.current?.abort(); requestVersion.current += 1; setSession(null); setFit(null); setStatus('idle'); setMessage('Choose a template, then run a synthetic trial.'); };
  const chooseTemplate = (event) => { setTemplate(event.target.value); reset(); };
  const chooseMystery = (event) => { setMystery(event.target.checked); reset(); };

  useEffect(() => () => request.current?.abort(), []);

  async function run(event) {
    event.preventDefault();
    request.current?.abort();
    const version = ++requestVersion.current;
    const controller = new AbortController();
    request.current = controller;
    setSession(null); setFit(null); setStatus('running'); setMessage('Generating simulated observations…');
    try {
      const response = await fetch('/api/lab', { method: 'POST', headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ action: 'start', template, mystery }), signal: controller.signal });
      const body = await response.json().catch(() => null);
      if (controller.signal.aborted || version !== requestVersion.current) return;
      if (!response.ok || body?.status !== 'ok') throw new Error(errorMessage(body, 'The synthetic trial could not start.'));
      setSession(body); setStatus('ready'); setMessage('Trial ready. Fit the ballistic model or run another trial.');
    } catch (error) {
      if (error.name === 'AbortError') return;
      setStatus('error'); setMessage(error.message || 'The synthetic trial could not start.');
    }
  }

  async function fitTrial() {
    if (!session?.sessionId || !BALLISTIC.has(template)) return;
    request.current?.abort();
    const version = ++requestVersion.current;
    const controller = new AbortController();
    request.current = controller;
    setStatus('fitting'); setFit(null); setMessage('Fitting the ballistic model…');
    try {
      const response = await fetch('/api/lab', { method: 'POST', headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ action: 'fit', sessionId: session.sessionId }), signal: controller.signal });
      const body = await response.json().catch(() => null);
      if (controller.signal.aborted || version !== requestVersion.current) return;
      if (!response.ok || body?.status !== 'ok') throw new Error(errorMessage(body, 'The fit could not be completed.'));
      if (body.sessionId && body.sessionId !== session.sessionId) throw new Error('The fit belongs to a different trial. Run the trial again.');
      const revealed = displayFit(body.fit || body.actualS11response || body.reveal || body.gravity);
      if (!revealed) throw new Error('The fit response did not include a readable reveal.');
      setFit(revealed); setStatus('fitted'); setMessage('Fit complete. This is simulated evidence, not a calibrated measurement.');
    } catch (error) {
      if (error.name === 'AbortError') return;
      setStatus('error'); setMessage(error.message || 'The fit could not be completed.');
    }
  }

  const rows = sampleRows(session?.observations);
  const ballistic = BALLISTIC.has(template);
  return <section className="lab" aria-labelledby="lab-title">
    <div className="lab-intro"><p className="eyebrow">Synthetic lab · Mystery-g</p><h1 id="lab-title">Test a motion model</h1>
      <p className="lede">Explore a deterministic, simulated trajectory before connecting a measured video.</p></div>
    <form className="lab-controls" onSubmit={run}>
      <fieldset><legend>Template</legend><div className="template-grid">
        {TEMPLATES.map(([value, label, hint]) => <label className="template-choice" key={value}><input type="radio" name="template" value={value} checked={template === value} onChange={chooseTemplate} /><span><strong>{label}</strong><small>{hint}</small></span></label>)}
      </div></fieldset>
      <label className="mystery-toggle"><input type="checkbox" checked={mystery} onChange={chooseMystery} disabled={!ballistic} /> <span><strong>Mystery-g mode</strong><small>Hide the simulated gravity until reveal</small></span></label>
      <div className="lab-actions"><button type="submit" disabled={status === 'running' || status === 'fitting'}>{status === 'running' ? 'Running…' : 'Run trial'}</button>
        <button type="button" className="secondary" onClick={fitTrial} disabled={!session || !ballistic || status === 'running' || status === 'fitting'}>Fit &amp; reveal</button></div>
      {!ballistic && <p className="field-note">Fit is available only for ballistic templates.</p>}
    </form>
    <p className={`lab-status status-${status}`} role="status" aria-live="polite">{message}</p>
    {session && <div className="lab-results" aria-label="Synthetic trial results">
      <div className="result-heading"><div><p className="eyebrow">Observed trajectory</p><h2>{session.template === 'free_fall' ? 'Free fall' : 'Projectile'} samples</h2></div><span className="badge">Simulated · {session.units?.position || 'm'}</span></div>
      <div className="plot-wrap"><svg className="trajectory-plot" viewBox="0 0 640 220" role="img" aria-label="Sampled simulated position over time"><polyline points={rows.map((row, i) => `${24 + (i * 592 / Math.max(1, rows.length - 1))},${190 - Math.min(160, Math.max(0, Number(row.position_m) || 0) * 22)}`).join(' ')} /><line x1="24" y1="190" x2="616" y2="190" /><text x="24" y="213">time (s)</text><text x="28" y="18">position (m)</text></svg></div>
      <div className="table-wrap"><table><caption>Sampled observations</caption><thead><tr><th scope="col">Time (s)</th><th scope="col">Position (m)</th></tr></thead><tbody>{rows.map((row, index) => <tr key={`${row.time_s}-${index}`}><td>{Number(row.time_s).toFixed(2)}</td><td>{Number(row.position_m).toFixed(3)}</td></tr>)}</tbody></table></div>
      {fit && <div className="reveal"><p className="eyebrow">Reveal</p><h2>{fit.value.toFixed(3)} ± {typeof fit.uncertainty === 'number' ? fit.uncertainty.toFixed(3) : '—'} {fit.unit}</h2><p>Gravity · source: {fit.source}</p></div>}
      <p className="limitations"><strong>Limits:</strong> {session.limitations?.join(' ') || 'Synthetic observations only; no camera calibration or physical uncertainty.'}</p>
    </div>}
  </section>;
}

export { BALLISTIC, displayFit, sampleRows };
