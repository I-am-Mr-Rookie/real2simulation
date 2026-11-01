'use client';

// N12 "Ask the agent": syncs the editor scene with the project, sends a turn, applies agent edits live, shows the report.
import { useEffect, useState } from 'react';
import { validateScene, sceneJson } from './scene.mjs';

const BASE = '/api/workspace/agent';
export const EXAMPLES = ['Drop a 5 cm ball from 1.2 m and measure g', 'Pendulum, 0.8 m, find the period'];
// The panel lives in the lab editor, so turns are framed as virtual-lab work (else the model looks for uploads).
export const CONTEXT = 'In the virtual lab editor (SIMULATED): ';

async function call(path, init = {}) {
  const r = await fetch(BASE + path, { cache: 'no-store', ...init, headers: { 'content-type': 'application/json' } });
  const body = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(body?.detail?.message ?? body?.error?.message ?? 'HTTP ' + r.status);
  return body;
}

export default function AgentPanel({ scene, onScene, load = true }) {
  const [text, setText] = useState(EXAMPLES[0]);
  const [busy, setBusy] = useState(false);
  const [log, setLog] = useState([]);
  const [history, setHistory] = useState([]);
  const [question, setQuestion] = useState(null);
  const [report, setReport] = useState(null);
  useEffect(() => {
    if (!load) return; // N22: a live room or experiment scene is open; do not replace it with the saved project scene
    call('/lab/scene').then((b) => b.scene.objects.length && onScene(validateScene(b.scene), 'Scene loaded from the project.')).catch(() => {});
    call('/lab/report').then((b) => setReport(b.markdown)).catch(() => {});
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const ask = async (msg) => {
    if (!msg.trim() || busy) return;
    setBusy(true); setQuestion(null); setLog((l) => [...l, { who: 'You', text: msg }]);
    try {
      await call('/lab/scene', { method: 'POST', body: sceneJson(scene) }); // the agent edits what the user sees
      const t = await call('/turn', { method: 'POST', body: JSON.stringify({ text: CONTEXT + msg, history }) });
      const names = (t.tool_calls ?? []).map((c) => c.name);
      setHistory((h) => [...h, { role: 'user', content: msg }, { role: 'assistant', content: t.reply }].slice(-20));
      setLog((l) => [...l, { who: 'Agent', text: t.reply, tools: names }]);
      setQuestion(t.question);
      if (names.some((n) => n.startsWith('lab_'))) onScene(validateScene((await call('/lab/scene')).scene), 'Agent edits applied. SIMULATED.');
      if (names.includes('write_report')) setReport((await call('/lab/report')).markdown);
      setText('');
    } catch (e) { setLog((l) => [...l, { who: 'Agent', text: 'Agent unavailable: ' + e.message }]); }
    setBusy(false);
  };

  return <div className="le-panel le-agent">
    <h3>Ask the agent</h3>
    <div className="le-bar" role="group" aria-label="Examples">
      {EXAMPLES.map((x) => <button key={x} type="button" onClick={() => setText(x)} disabled={busy}>{x}</button>)}
    </div>
    <form onSubmit={(e) => { e.preventDefault(); ask(text); }} className="le-bar">
      <input aria-label="Message to the agent" value={text} onChange={(e) => setText(e.target.value)} maxLength={4000} disabled={busy} />
      <button type="submit" disabled={busy || !text.trim()}>{busy ? 'Working...' : 'Ask'}</button>
      <button type="button" onClick={() => ask('Write the lab report.')} disabled={busy}>Write report</button>
    </form>
    <div className="le-log" aria-live="polite">
      {log.map((m, i) => <p key={i}><strong>{m.who}:</strong> {m.text}{m.tools?.length ? <small> (tools: {m.tools.join(', ')})</small> : null}</p>)}
    </div>
    {question && <div className="le-bar" role="group" aria-label="Agent question">
      {question.options.map((o) => <button key={o.label} type="button" onClick={() => ask(o.label)}>{o.label}{o.recommended ? ' (recommended)' : ''}</button>)}
    </div>}
    {report && <details open><summary>Lab report (SIMULATED)</summary><pre className="le-report">{report}</pre></details>}
  </div>;
}
