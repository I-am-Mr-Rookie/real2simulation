'use client';
// S04o: mounts the S15n controller against the BFF (/api/workspace/*). No new state machine: workflow/interview/instrument
// reducers are reused; every number shown comes from a validated API response. Fixture banner stays until the API answers.
import React from 'react';
import { createWorkspace } from '../workspace/react.mjs';
import { createThreeViewer } from '../viewer/three-viewer.mjs';
import { createController, API_BASE, browserSimulate } from '../workspace/controller.mjs';
import { runBrowserSimulation } from '../lab/browser-simulator.mjs';
import { uploadView, renderUpload } from '../workspace/upload-view.mjs';
import { initialInterview, reduceInterview, interviewAnswers } from '../workspace/interview.mjs';
import { initialInstruments, reduceInstruments } from '../workspace/instruments.mjs';
import { initialRun } from '../workspace/runcontrol.mjs';

const Workspace = createWorkspace(React);
const adapter = createThreeViewer();
export const UNAVAILABLE_NOTICE = 'Workspace service unavailable: the private API did not answer, so no upload, job or result is shown. Nothing on this page is a measurement.';
export const LIVE_NOTICE = 'Connected to the private workspace API. Only approved licensed clips are accepted; every result is labelled RECORDED or SIMULATED by the server.';
export const INSTRUMENTS_UNAVAILABLE = 'Instruments are not available in this build; no reading is shown.';

// Reachable = the BFF forwarded and the API answered with JSON (any 2xx/4xx except auth). 401/403/5xx/network = unavailable.
export async function probeApi(f = globalThis.fetch, base = API_BASE) {
  try {
    const res = await f(base + '/jobs/s04o-probe', { credentials: 'same-origin', cache: 'no-store' });
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
    ctl.loadQuestions().then((r) => r && setLocal((l) => ({ ...l, interview: reduceInterview(l.interview, { type: 'Q_LOADED', response: r, sceneId: ctl.state.scene?.scene_id }) })));
  }, [api, phase, s.questions, ctl]);
  const live = api === 'live';
  const onAction = live ? (a) => routeAction(ctl, localRef.current, a).then(setLocal) : undefined;
  const up = uploadView(s);
  const simulated = /^(run|fit|report)\./.test(phase); // run/fit/report numbers are browser-simulated, never recorded
  return React.createElement('section', { 'data-private-content': live ? 'live' : 'fixture', 'data-api': api, 'aria-label': 'Private workspace' },
    React.createElement('h1', null, scene.title),
    React.createElement('p', { role: 'note' }, live ? LIVE_NOTICE : api === 'checking' ? 'Checking the workspace service…' : UNAVAILABLE_NOTICE),
    live ? null : React.createElement('p', { role: 'note' }, scene.notice),
    // the upload error is rendered once, by the workspace job panel (S15n limit: avoid a double alert)
    live ? renderUpload(React.createElement, { ...up, error: null }, (file) => ctl.upload(file)) : null,
    live && simulated ? React.createElement('p', { role: 'note', 'data-label': s.whatIfLabel ? 'what-if' : 'simulated' }, s.whatIfLabel
      ? s.whatIfLabel + '. Run and fit values come from the in-browser simulator on your described setup.' + (s.specLabel ? ' Spec: ' + s.specLabel + '.' : '')
      : 'SIMULATED: run and fit values come from the in-browser simulator on the validated setup.' + (s.specLabel ? ' Spec: ' + s.specLabel + '.' : '')) : null,
    live ? React.createElement('p', { role: 'note', 'data-instruments': 'unavailable' }, INSTRUMENTS_UNAVAILABLE) : null,
    React.createElement(Workspace, { state: s.state, adapter, audience: 'signed-in', onAction,
      interview: live ? local.interview : undefined, run: live ? initialRun() : undefined, instruments: live ? local.instruments : undefined,
      fit: live ? s.fitInput ?? undefined : undefined, report: live && s.report ? s.report : undefined, provenance: live ? s.provenance ?? undefined : undefined,
      whatIf: live ? s.whatIfLabel ?? undefined : undefined }));
}

