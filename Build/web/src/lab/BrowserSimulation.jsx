'use client';

import { useId, useState } from 'react';
import { runBrowserSimulation } from './browser-simulator.mjs';
import { plotPoints, sampleRows } from './fit-contract.mjs';

const display = (value) => Number(value.toPrecision(6)).toString();

export default function BrowserSimulation({ payload }) {
  const titleId = useId();
  const [result, setResult] = useState(null);
  const current = result?.payload === payload ? result : null;
  const trajectory = current?.trajectory;
  const observations = trajectory?.samples.map((sample) => ({ time_s: sample.time_s, position_m: sample.position_m[1] }));
  const plot = plotPoints(observations);
  const firstPoint = plot.points.split(' ')[0].split(',');

  function run() {
    try {
      setResult({ payload, trajectory: runBrowserSimulation(payload) });
    } catch {
      // Never render raw input or engine errors: this component is not a Mystery reveal surface.
      setResult({ payload, error: 'Browser simulation unavailable. Supply a validated NORMAL synthetic setup with at most 2000 samples.' });
    }
  }

  return <section className="lab-browser-sim" aria-label="In-browser simulation">
    <h2>In-browser trajectory</h2>
    <p className="eyebrow">Simulated · synthetic · RK4-only. No contact response or free drag.</p>
    <button type="button" className="secondary" onClick={run}>Compute in browser</button>
    <p role="status">{current?.error || (trajectory
      ? `Computed ${trajectory.samples.length} actual ${trajectory.kind} trajectory points in this browser.`
      : 'NORMAL mode only. Compute to show the actual engine trace.')}</p>
    {trajectory && <>
      <p>Static trace: all {trajectory.samples.length} engine points; no animation. Time (s) vs world Y position (m).</p>
      <svg viewBox="0 0 640 220" width="100%" role="img" aria-labelledby={titleId}>
        <title id={titleId}>Simulated world Y position against time, computed in browser with fixed-step RK4</title>
        <polyline points={plot.points} fill="none" stroke="currentColor" strokeWidth="2" />
        <circle cx={firstPoint[0]} cy={firstPoint[1]} r="3" fill="currentColor" />
        <text x="24" y="212">Time (s)</text>
        <text x="24" y="20">World Y (m)</text>
      </svg>
      <p>Time: {display(plot.time[0])}–{display(plot.time[1])} s. World Y: {display(plot.position[0])}–{display(plot.position[1])} m.</p>
      <table>
        <caption>Selected actual engine samples (6 significant digits; not the full trace)</caption>
        <thead><tr><th scope="col">Time (s)</th><th scope="col">World Y (m)</th></tr></thead>
        <tbody>{sampleRows(observations).map((sample) => <tr key={sample.time_s}>
          <td>{display(sample.time_s)}</td><td>{display(sample.position_m)}</td>
        </tr>)}</tbody>
      </table>
    </>}
  </section>;
}
