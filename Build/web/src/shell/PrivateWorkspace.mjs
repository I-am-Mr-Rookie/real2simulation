'use client';
// S04o: mounts the S15n controller against the BFF (/api/workspace/*). No new state machine: workflow/interview/instrument
// reducers are reused; every number shown comes from a validated API response. Fixture banner stays until the API answers.
import React from 'react';
import { createWorkspace } from '../workspace/react.mjs';
import { createThreeViewer } from '../viewer/three-viewer.mjs';
import { createArtifactLoader } from '../viewer/artifact-loader.mjs';
import { createController, API_BASE, browserSimulate } from '../workspace/controller.mjs';
import { runBrowserSimulation } from '../lab/browser-simulator.mjs';
import { uploadView, renderUpload } from '../workspace/upload-view.mjs';
import { initialInterview, reduceInterview, interviewAnswers } from '../workspace/interview.mjs';
import { initialInstruments, reduceInstruments } from '../workspace/instruments.mjs';
import { initialRun } from '../workspace/runcontrol.mjs';
import { renderShell, toolsOf, shellKey, initialRail, railReduce, LEFT_KEY, PANE_KEY, NARROW_QUERY, HOVER_OPEN_MS, HOVER_CLOSE_MS } from './workspace-shell.mjs';
import { renderQuestionCard, renderWaiting, pendingOf, shouldAutoOpen, shouldCloseOnFinish } from './agent-card.mjs';
import { icon } from './icons.mjs';
import { createLive } from '../workspace/live-view.mjs';

const Workspace = createWorkspace(React);
const Live = createLive(React); // N09 live product: agent mode, projects, files, agent chat, GPU dot, job views
const adapter = createThreeViewer();
// S13m: scene_id is the job id; the API serves the sha-verified RM04 bundle (or 503 -> viewer shows unavailable).
export const loadScene = createArtifactLoader({
  bundleUrl: (s) => new URL(`${API_BASE}/scenes/${encodeURIComponent(s.scene_id)}/bundle/`, globalThis.location.origin) });
export const SCENE_LABEL = 'Scene geometry: Display only, scale unverified, not a measurement.';
export const UNAVAILABLE_NOTICE = 'Workspace service unavailable: the private API did not answer, so no upload, job or result is shown. Nothing on this page is a measurement.';
export const LIVE_NOTICE = 'Connected to the private workspace API. Upload your own videos in Files; the sample pipeline below accepts only approved licensed clips. Every result is labelled RECORDED or SIMULATED by the server.';
export const INSTRUMENTS_UNAVAILABLE = 'Instruments are not available in this build; no reading is shown.';
// S15an: long service notices collapse to a chip; full wording stays verbatim in the (i) detail.
const chip = (label, text, id) => React.createElement('details', { className: 'r2s-chip', 'data-chip': id },
  React.createElement('summary', { title: text }, icon(React.createElement, 'info', 14), label), React.createElement('p', { role: 'note' }, text));

// Reachable = the BFF forwarded and the API answered with JSON (any 2xx/4xx except auth). 401/403/5xx/network = unavailable.
export async function probeApi(f = globalThis.fetch, base = API_BASE) {
  try {
    const res = await f(base + '/health', { credentials: 'same-origin', cache: 'no-store' });
    const body = await res.json().catch(() => null);
    return body !== null && res.status < 500 && res.status !== 401 && res.status !== 403 ? 'live' : 'unavailable';
  } catch { return 'unavailable'; }
}

// Host side of onAction: workflow events go to the controller, Q_* to the interview reducer, I_* to the instrument reducer.
// Returns the next {interview, instruments}; side effects are controller calls only.
export async function routeAction(ctl, local, a) {
  const t = a?.type ?? '';
  if (t.startsWith('Q_')) {
    const interview = reduceInterview(local.interview, a);
    const answers = t === 'Q_SUBMIT' ? interviewAnswers(interview) : null;
    if (answers) await ctl.submitAnswers(answers);
    return { ...local, interview };
  }
  if (t === 'SPEC_RETRY') { // S15q: resend the completed answers after a visible spec/API error
    const answers = interviewAnswers(local.interview);
    if (answers) await ctl.submitAnswers(answers);
    return local;
  }
  if (t === 'UPLOAD_RETRY') { await ctl.retryUpload(); return local; }
  if (t.startsWith('I_')) {
    let instruments = reduceInstruments(local.instruments, a, ctl.state);
    // shortcut: no instrument service exists in this build; a measure request fails honestly instead of inventing a reading.
    if (t === 'I_MEASURE' && instruments.pending) instruments = reduceInstruments(instruments, { type: 'I_FAIL', message: INSTRUMENTS_UNAVAILABLE }, ctl.state);
    return { ...local, instruments };
  }
  if (t === 'RUN_START') await ctl.run(a.seed ?? 1);
  else if (t === 'FIT_START') await ctl.fit();
  else if (t === 'REPORT_OPEN') await ctl.openReport();
  else if (t) ctl.dispatch(a); // remaining graph edges (cancel, close, reset, retry) are pure reducer moves
  return local;
}

export const SESSION_KEY = 'r2s-ws-interview';
export const SESSION_RESET = 'Your earlier session was reset by the page reload. Upload the clip again to start over.';
// S15bd: sessionStorage holds only a flag (no session data). Flag set during the interview; idle with flag = reloaded mid-interview.
export function sessionNote(storage, phase) {
  try {
    if (phase === 'interview.active') storage.setItem(SESSION_KEY, '1');
    else if (phase !== 'upload.idle') storage.removeItem(SESSION_KEY);
    return phase === 'upload.idle' && storage.getItem(SESSION_KEY) === '1';
  } catch { return false; }
}

// S15bg: fixture wording only once the probe reports the service unavailable; never while checking or live (the route announcer reads the h1).
export const workspaceHeading = (api, scene) => api === 'live' ? 'Private workspace' : api === 'checking' ? 'Workspace' : scene.title;

export default function PrivateWorkspace({ scene }) {
  const { useState, useEffect, useMemo, useRef } = React;
  const [api, setApi] = useState('checking');
  const [snap, setSnap] = useState(null);
  const [local, setLocal] = useState({ interview: initialInterview(), instruments: initialInstruments() });
  const localRef = useRef(local);
  localRef.current = local;
  const ctl = useMemo(() => createController({ onChange: setSnap, simulate: browserSimulate(runBrowserSimulation) }), []);
  useEffect(() => { let on = true; probeApi().then((s) => on && setApi(s)); return () => { on = false; }; }, []);
  const s = snap ?? ctl.snapshot();
  const phase = s.state.phase;
  useEffect(() => { // fetch the agent's questions once the job hands over to the interview
    if (api !== 'live' || phase !== 'interview.active' || s.questions) return;
    ctl.loadQuestions().then((r) => r && setLocal((l) => ({ ...l, interview: reduceInterview(l.interview, { type: 'Q_LOADED', response: r, sceneId: ctl.state.scene?.scene_id ?? ctl.state.owner?.jobId }) })));
  }, [api, phase, s.questions, ctl]);
  const [resetNote, setResetNote] = useState(false);
  useEffect(() => setResetNote(sessionNote(globalThis.sessionStorage, phase)), [phase]);
  const live = api === 'live';
  const onAction = live ? (a) => routeAction(ctl, localRef.current, a).then((l) => {
    if (shouldCloseOnFinish({ action: a, interview: l.interview, narrow: narrow() })) { opened.current = false; setRight(false); }
    setLocal(l);
  }) : undefined;
  const up = uploadView(s);
  const simulated = /^(run|fit)\.|^report\.open$/.test(phase); // run/fit/report numbers are browser-simulated, never recorded (report.owner is the stored owner result)
  // S15ab shell state: left expanded/collapsed (persisted on wide screens), right panel open/closed with focus in and back.
  const [rail, setRail] = useState(null); // S15ae activity bar: { pane, open, preview } via the pure railReduce
  const [right, setRight] = useState(false);
  const L = Live.useLive(live, () => setRight(true));
  const rightToggle = useRef(null);
  const rightHead = useRef(null);
  const cardHead = useRef(null);
  const opened = useRef(false);
  // S15ac: the interview lives in the right panel; same reducer state, shown in the same phase the centre panel used.
  const iv = live && phase === 'interview.active' ? local.interview : null;
  const pending = pendingOf(iv);
  const round = useRef(null);
  const userClosed = useRef(false); // the user shut the panel while questions were pending: badge instead of forcing it open again
  const narrow = () => globalThis.matchMedia?.(NARROW_QUERY).matches ?? false;
  useEffect(() => { let o = null, p = null; try { o = localStorage.getItem(LEFT_KEY); p = localStorage.getItem(PANE_KEY); } catch {} setRail(initialRail(o, p, narrow())); }, []);
  // S15an: theme choice + System-follows-OS moved to the single global header menu (app/ThemeToggle.jsx).
  useEffect(() => { // same LEFT_KEY semantics as S15ab (wide only); the current pane is stored separately
    if (!rail) return;
    try { localStorage.setItem(PANE_KEY, rail.pane); if (!narrow()) localStorage.setItem(LEFT_KEY, rail.open ? 'expanded' : 'collapsed'); } catch {}
  }, [rail?.pane, rail?.open]); // eslint-disable-line react-hooks/exhaustive-deps
  const send = (e) => setRail((s) => railReduce(s ?? initialRail(null, null, narrow()), e));
  const timers = useRef({});
  const stop = (k) => { clearTimeout(timers.current[k]); timers.current[k] = null; };
  const later = (k, ms, f) => { stop(k); timers.current[k] = setTimeout(f, ms); };
  useEffect(() => () => { stop('open'); stop('close'); }, []); // eslint-disable-line react-hooks/exhaustive-deps
  // Hover preview: real mouse pointers on wide screens only (touch/pen taps are clicks; narrow panes are drawers).
  const hover = (id, e) => { if (e?.pointerType !== 'mouse' || narrow()) return; stop('close'); later('open', HOVER_OPEN_MS, () => send({ type: 'hoverEnter', id })); };
  const unhover = () => { stop('open'); later('close', HOVER_CLOSE_MS, () => send({ type: 'hoverLeave' })); };
  const closePreview = () => { // Escape: close the temporary pane; if focus was inside it, return focus to its icon
    const doc = globalThis.document;
    if (doc?.getElementById('r2s-pane-' + rail.preview)?.contains(doc.activeElement)) doc.querySelector('[data-pane="' + rail.preview + '"]')?.focus();
    stop('open'); stop('close'); send({ type: 'escape' });
  };
  useEffect(() => {
    if (right) { opened.current = true; (cardHead.current ?? rightHead.current)?.focus(); } else if (opened.current) rightToggle.current?.focus();
  }, [right]);
  useEffect(() => {
    const q = iv?.questions ?? null;
    if (shouldAutoOpen({ asking: pending > 0, newRound: q !== round.current, userClosed: userClosed.current, narrow: narrow() })) setRight(true);
    round.current = q;
  }, [iv?.questions, pending]); // eslint-disable-line react-hooks/exhaustive-deps -- a new round = a new questions array
  const closeRight = () => { if (pending) userClosed.current = true; setRight(false); };
  const toggleRight = () => (right ? closeRight() : setRight(true));
  const openCard = () => (right ? cardHead.current?.focus() : setRight(true));
  const toggleLeft = () => send({ type: 'toggle' });
  const tools = toolsOf({ live, phase, owner: !!s.state.owner, jobId: s.state.job?.id, uploadStatus: up.show ? up.status : null, hasReport: !!s.report || phase === 'report.owner', pending, liveFit: s.provenance?.measurement?.live_fit?.status === 'ok' });
  const openTool = (t) => {
    const el = globalThis.document?.getElementById(t.target);
    if (!el) return;
    if (narrow() && !el.closest?.('#r2s-right')) { opened.current = false; setRight(false); }
    el.scrollIntoView?.({ block: 'start', behavior: 'smooth' }); el.focus?.({ preventScroll: true });
  };
  const keysRef = useRef(null);
  keysRef.current = (e) => {
    const k = shellKey(e, tools);
    if (!k) return;
    if (k === 'escape') { if (rail?.preview) closePreview(); else if (right) closeRight(); else if (rail?.open && narrow()) toggleLeft(); else return; }
    else if (k === 'left') toggleLeft();
    else if (k === 'right') toggleRight();
    else openTool(tools.find((t) => 'tool:' + t.id === k));
    e.preventDefault();
  };
  useEffect(() => { const f = (e) => keysRef.current(e); globalThis.addEventListener('keydown', f); return () => globalThis.removeEventListener('keydown', f); }, []);
  const on = { toggleLeft, toggleRight, tool: openTool, rail: (e) => { stop('open'); stop('close'); send(e); }, hover, unhover, paneEnter: () => stop('close'),
    close: () => { if (right) closeRight(); if (narrow() && rail?.open) toggleLeft(); },
    navigated: () => { if (rail?.preview) send({ type: 'escape' }); else if (narrow() && rail?.open) toggleLeft(); } };
  return React.createElement('section', { 'data-private-content': live ? 'live' : 'fixture', 'data-api': api, 'aria-label': 'Private workspace' },
    renderShell(React.createElement, { title: workspaceHeading(api, scene), rail, right, tools, pending,
      status: live ? React.createElement(Live.Dot, { L }) : null,
      agent: React.createElement(React.Fragment, null, live ? React.createElement(Live.Chat, { L }) : null, iv ? renderQuestionCard(React.createElement, iv, onAction, { cardHead }) : null) }, on, { rightToggle, rightHead },
    live ? chip('Connected', LIVE_NOTICE, 'live') : React.createElement('p', { role: 'note' }, api === 'checking' ? 'Checking the workspace service…' : UNAVAILABLE_NOTICE),
    live ? React.createElement(Live.Centre, { L }) : null,
    live ? React.createElement('h2', { className: 'lv-sample-h' }, 'Sample pipeline') : null,
    live ? renderWaiting(React.createElement, iv, openCard) : null,
    live || api === 'checking' ? null : React.createElement('p', { role: 'note' }, scene.notice),
    // the upload error is rendered once, by the workspace job panel (S15n limit: avoid a double alert)
    live ? renderUpload(React.createElement, { ...up, error: null }, (file) => ctl.upload(file)) : null,
    live && resetNote ? React.createElement('p', { role: 'note', className: 'ws-note', 'data-slot': 'session-reset' }, SESSION_RESET) : null,
    live && simulated ? React.createElement('p', { role: 'note', 'data-label': s.whatIfLabel ? 'what-if' : 'simulated' }, s.whatIfLabel
      ? s.whatIfLabel + '. Run and fit values come from the in-browser simulator on your described setup.' + (s.specLabel ? ' Spec: ' + s.specLabel + '.' : '')
      : 'SIMULATED: run and fit values come from the in-browser simulator on the validated setup.' + (s.specLabel ? ' Spec: ' + s.specLabel + '.' : '')) : null,
    live ? chip('Instruments off', INSTRUMENTS_UNAVAILABLE, 'instruments') : null,
    live && s.state.scene ? React.createElement('p', { role: 'note', 'data-scene-label': '' }, SCENE_LABEL) : null,
    React.createElement(Workspace, { state: s.state, adapter, loadScene, audience: 'signed-in', onAction,
      run: live ? initialRun() : undefined, instruments: live ? local.instruments : undefined, // interview: rendered in the right panel (S15ac)
      fit: live ? s.fitInput ?? undefined : undefined, report: live && s.report ? s.report : undefined, provenance: live ? s.provenance ?? undefined : undefined,
      whatIf: live ? s.whatIfLabel ?? undefined : undefined })));
}

