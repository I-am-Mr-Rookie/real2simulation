'use client';

// N12 "Ask the agent": syncs the editor scene with the project, sends a turn, applies agent edits live, shows the report.
// N85: full-height chat panel: header (model picker, New chat), scrolling conversation, composer pinned at the bottom.
import * as ReactNS from 'react';
import { useEffect, useRef, useState } from 'react';
import { validateScene, sceneJson } from './scene.mjs';
import { readAgentMode, writeAgentMode, agentTier } from '../workspace/live.mjs';
import { createUseVoice } from '../workspace/voice.mjs';
import { createLive } from '../workspace/live-view.mjs';
import { icon } from '../shell/icons.mjs';
const useVoice = createUseVoice({ useState, useRef, useEffect });

const BASE = '/api/workspace/agent';
// One data list: cards in the empty state, chips above the composer later. Clicking fills the composer.
export const CARDS = [
  { id: 'drop', icon: 'drop', title: 'Measure g with a drop', text: 'Drop a 5 cm ball from 1.2 m and measure g' },
  { id: 'pendulum', icon: 'pendulum', title: 'Pendulum period', text: 'Pendulum, 0.8 m, find the period' },
  { id: 'ramp', icon: 'ramp', title: 'Add a ramp', text: 'Add a 30 degree ramp and roll a ball down it' },
  { id: 'report', icon: 'report', title: 'Write report', text: 'Write the lab report.' },
];
// The panel lives in the lab editor, so turns are framed as virtual-lab work (else the model looks for uploads).
export const CONTEXT = 'In the virtual lab editor (SIMULATED): ';
const STEPS = { lab_add_object: 'Added object', lab_update_object: 'Updated object', lab_update_objects: 'Updated objects', lab_remove_object: 'Removed object', lab_run: 'Ran simulation',
  lab_report: 'Read report', write_report: 'Wrote report', fit: 'Fitted', fit_equation: 'Fitted', fit_motion: 'Fitted' };
export const stepName = (n) => STEPS[n] ?? (n.charAt(0).toUpperCase() + n.slice(1)).replace(/_/g, ' ');
// Enter sends, Shift+Enter (or IME composition) makes a newline.
export const sendsOn = (e) => e.key === 'Enter' && !e.shiftKey && !e.isComposing;

const P = {
  drop: 'M12 3v12M7 10l5 5 5-5M5 21h14', pendulum: 'M4 3h16M12 3l5 12M17 15a2 2 0 1 0 .01 0', ramp: 'M3 20h18L3 8zM8 9a2 2 0 1 0 .01 0',
  report: 'M6 3h9l4 4v14H6zM14 3v5h5M9 13h7M9 17h5', mic: 'M12 3a3 3 0 0 0-3 3v6a3 3 0 0 0 6 0V6a3 3 0 0 0-3-3zM5 11a7 7 0 0 0 14 0M12 18v3',
  send: 'M12 19V5M5 12l7-7 7 7', stop: 'M7 7h10v10H7z', x: 'M6 6l12 12M18 6L6 18', plus: 'M12 5v14M5 12h14', step: 'M5 12l4 4 10-10',
  download: 'M12 4v11M7 10l5 5 5-5M5 20h14', open: 'M4 9V4h5M20 15v5h-5M4 4l7 7M20 20l-7-7', agent: 'M12 3l2 5 5 2-5 2-2 5-2-5-5-2 5-2z',
};
const I = ({ n, s = 16 }) => <svg className="la-ico" viewBox="0 0 24 24" width={s} height={s} aria-hidden="true" focusable="false"><path d={P[n]} fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" /></svg>;

async function call(path, init = {}) {
  const r = await fetch(BASE + path, { cache: 'no-store', ...init, headers: { 'content-type': 'application/json' } });
  const body = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(body?.detail?.message ?? body?.error?.message ?? 'HTTP ' + r.status);
  return body;
}

function Report({ md }) {
  const [open, setOpen] = useState(false);
  const save = () => { const a = document.createElement('a'); a.href = URL.createObjectURL(new Blob([md], { type: 'text/markdown' })); a.download = 'lab-report.md'; a.click(); setTimeout(() => URL.revokeObjectURL(a.href), 1000); };
  return <div className="la-report">
    <div className="la-report-head"><I n="report" s={18} /><span><strong>Lab report</strong><small>SIMULATED</small></span></div>
    {open && <pre className="le-report">{md}</pre>}
    <div className="la-report-bar">
      <button type="button" aria-expanded={open} onClick={() => setOpen(!open)}><I n="open" s={14} />{open ? 'Close' : 'Open'}</button>
      <button type="button" onClick={save}><I n="download" s={14} />Download (.md)</button>
    </div>
  </div>;
}

export default function AgentPanel({ scene, onScene, load = true }) {
  const R = ReactNS.createElement ? ReactNS : ReactNS.default;
  const live = useRef(null);
  live.current ??= createLive(R, icon); // the workspace N55 picker component, same saved setting
  const [text, setText] = useState('');
  const [busy, setBusy] = useState(false);
  const { voice, toggleVoice, cancelVoice } = useVoice((words) => setText((t) => (t ? t + ' ' : '') + words));
  const [log, setLog] = useState([]);
  const [history, setHistory] = useState([]);
  const [question, setQuestion] = useState(null);
  const [report, setReport] = useState(null);
  const [userKey, setUserKey] = useState(null);
  const [mode, setModeState] = useState(undefined);
  const logRef = useRef(null), inputRef = useRef(null);
  // N28: last answer always in view; rerun when the turn ends (busy false), after the scene/report reloads settle.
  useEffect(() => { const el = logRef.current; if (el) el.scrollTop = el.scrollHeight; }, [log, question, busy, report]);
  useEffect(() => { const el = inputRef.current; if (el) { el.style.height = 'auto'; el.style.height = Math.min(el.scrollHeight, 160) + 'px'; } }, [text]);
  useEffect(() => {
    fetch('/api/workspace/session', { cache: 'no-store' }).then((r) => (r.ok ? r.json() : {})).then((b) => { if (b.userKey) { setUserKey(b.userKey); setModeState(readAgentMode(globalThis.localStorage, b.userKey)); } }).catch(() => {});
    if (!load) return; // N22: a live room or experiment scene is open; do not replace it with the saved project scene
    call('/lab/scene').then((b) => b.scene.objects.length && onScene(validateScene(b.scene), 'Scene loaded from the project.')).catch(() => {});
    call('/lab/report').then((b) => setReport(b.markdown)).catch(() => {});
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const fill = (t) => { setText(t); inputRef.current?.focus(); };
  const newChat = () => { setLog([]); setHistory([]); setQuestion(null); };
  const ask = async (msg) => {
    if (!msg.trim() || busy) return;
    setBusy(true); setQuestion(null); setLog((l) => [...l, { who: 'You', text: msg }]);
    try {
      const session = await fetch('/api/workspace/session', { cache: 'no-store' });
      if (!session.ok) throw new Error('Sign in required.');
      const { userKey } = await session.json();
      if (!userKey) throw new Error('Sign in required.');
      const tier = agentTier(readAgentMode(globalThis.localStorage, userKey));
      await call('/lab/scene', { method: 'POST', body: sceneJson(scene) }); // the agent edits what the user sees
      const t = await call('/turn', { method: 'POST', body: JSON.stringify({ text: CONTEXT + msg, history, ...tier }) });
      const names = (t.tool_calls ?? []).map((c) => c.name);
      setHistory((h) => [...h, { role: 'user', content: msg }, { role: 'assistant', content: t.reply }].slice(-20));
      // Honesty: name the model that produced the reply; t.model is only the requested one when a fallback ran.
      setLog((l) => [...l, { who: 'Agent', text: t.reply, tools: names, model: t.answered_by || t.model, fallback: Boolean(t.answered_by) }]);
      setQuestion(t.question);
      const tidied = names.includes('lab_update_objects');
      if (names.some((n) => n.startsWith('lab_'))) onScene(validateScene((await call('/lab/scene')).scene), tidied ? 'Tidied by agent · SIMULATED. Undo or Before shows the old layout.' : 'Agent edits applied. SIMULATED.', tidied);
      if (names.includes('write_report')) setReport((await call('/lab/report')).markdown);
      setText('');
    } catch (e) { setLog((l) => [...l, { who: 'Agent', text: 'Agent unavailable: ' + e.message, error: true }]); }
    setBusy(false);
  };

  const vs = voice.state, recording = vs === 'recording';
  const Picker = live.current.ModelPicker;
  const L = { mode, setMode: (m) => { if (writeAgentMode(globalThis.localStorage, m, userKey)) setModeState(m); } };
  return <div className="le-agent">
    <div className="la-head">
      <span className="la-name"><I n="agent" s={18} />Lab agent</span>
      <button type="button" className="la-ghost" onClick={newChat} disabled={busy || (!log.length && !question)} title="New chat: clears this conversation"><I n="plus" s={14} />New chat</button>
    </div>
    <div className="le-log" aria-live="polite" ref={logRef} tabIndex={0} aria-label="Conversation">
      {!log.length && <div className="la-empty">
        <h3>What should we test?</h3>
        <p className="le-muted">Ask for an experiment, or to add, move, resize or remove objects. Results are SIMULATED.</p>
        <div className="la-cards" role="group" aria-label="Suggestions">
          {CARDS.map((c) => <button key={c.id} type="button" className="la-card" onClick={() => fill(c.text)}><I n={c.icon} s={18} />{c.title}</button>)}
        </div>
      </div>}
      {log.map((m, i) => m.who === 'You'
        ? <p key={i} className="la-user"><span className="le-sr">You: </span>{m.text}</p>
        : <div key={i} className={m.error ? 'la-reply la-error' : 'la-reply'}>
          {m.tools?.length ? <ul className="la-steps" aria-label="Agent steps">{m.tools.map((n, j) => <li key={j}><I n="step" s={13} />{stepName(n)}</li>)}</ul> : null}
          <p><span className="le-sr">Agent: </span>{m.text}</p>
          {m.model ? <small className="la-model">Answered by {m.model}{m.fallback ? <span className="la-tag">fallback model</span> : null}</small> : null}
        </div>)}
      {busy && <p className="la-working le-muted">Working...</p>}
      {question && <div className="la-question" role="group" aria-label="Agent question">
        {question.question ? <strong>{question.question}</strong> : null}
        {question.options.map((o) => <button key={o.label} type="button" className="la-qopt" onClick={() => ask(o.label)} disabled={busy}><span>{o.label}</span>{o.recommended ? <span className="la-tag">Recommended</span> : null}</button>)}
      </div>}
      {report && <Report md={report} />}
    </div>
    {log.length > 0 && <div className="la-chips" role="group" aria-label="Suggestions">
      {CARDS.map((c) => <button key={c.id} type="button" onClick={() => fill(c.text)}>{c.title}</button>)}
    </div>}
    <form className="la-composer" onSubmit={(e) => { e.preventDefault(); return ask(text); }}>
      {recording
        ? <div className="la-rec">
          <button type="button" className="la-icon" aria-label="Cancel recording" title="Cancel" onClick={cancelVoice}><I n="x" /></button>
          <span className="la-level" role="img" aria-label="Recording"><i /><i /><i /><i /><i /></span>
          <button type="button" className="la-icon la-stop" aria-label="Stop recording" title="Stop and transcribe" onClick={toggleVoice}><I n="stop" /></button>
        </div>
        : <textarea ref={inputRef} rows={1} aria-label="Message to the agent" placeholder={vs === 'working' ? 'Transcribing...' : 'Ask the agent to build or test something'} value={text} maxLength={4000} readOnly={busy}
          onChange={(e) => setText(e.target.value)} onKeyDown={(e) => { if (sendsOn(e)) { e.preventDefault(); return ask(text); } }} />}
      <div className="la-bar">
        <Picker L={L} />
        <span className="la-grow" />
        {!recording && <button type="button" className="la-icon" data-voice={vs} aria-label={vs === 'requesting' ? 'Waiting for microphone' : vs === 'working' ? 'Transcribing' : 'Voice input'}
          title={vs === 'requesting' ? 'Waiting for microphone' : vs === 'working' ? 'Transcribing' : 'Voice input, up to 60 s'} disabled={busy || vs === 'working' || vs === 'requesting'} onClick={toggleVoice}><I n="mic" /></button>}
        <button type="submit" className="la-send" aria-label={busy ? 'Working' : 'Send'} title="Send (Enter)" disabled={busy || recording || !text.trim()}><I n="send" /></button>
      </div>
    </form>
    {voice.error && <p className="la-alert" role="alert">{voice.error}</p>}
  </div>;
}

