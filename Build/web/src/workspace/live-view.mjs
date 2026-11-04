// N09: live product workspace (agent mode screen, new project, files, agent chat + voice, GPU dot, job views).
// React is injected like workspace/react.mjs. Every number shown comes from an API response (quota, sizes, queue) or the browser upload progress.
import { API_BASE } from './controller.mjs';
import { AGENT_MODES, UPLOAD_QUESTION, LIMITS, TIPS, projectTitle, fmtBytes, quotaView, gpuDot, GPU_POLL_MS, shouldPoll, jobsState, apiErrorText,
  historyOf, questionAnswer, recommendedIndex, readAgentMode, writeAgentMode, STANDARD_MODELS, agentTier, modeLabel,
  MODEL_CHOICES, contentTitle, isDefaultTitle } from './live.mjs';
import { chartGeom, fmtPm, SIZE_UNITS, naturalPoint, experimentBody, jobView, POLL_MS, jobsFromToolCalls, shareable, scaleTag, labelsOf, gravityCheck } from './measure.mjs';
import { groupJobs, jobName, relTime, groupStatus } from './projects.mjs';
import { createUseVoice } from './voice.mjs';

const ACCEPT = 'video/mp4,video/quicktime,video/webm,.mp4,.mov,.webm';
const TRACK_KEY = 'r2s.tracked.jobs';
const LIVE_JOBS_MS = 15_000; // N55: projects refresh themselves (replaces the Refresh button)
const fileUrl = (f) => API_BASE + '/files/' + encodeURIComponent(f.id) + '/content';
async function call(path, init = {}) {
  const res = await fetch(API_BASE + path, { credentials: 'same-origin', cache: 'no-store', ...init });
  const body = await res.json().catch(() => null);
  return { status: res.status, ok: res.ok, body };
}
const errText = apiErrorText;

// XHR because fetch has no upload progress.
function uploadXhr(file, projectId, onPct) {
  return new Promise((resolve) => {
    const x = new XMLHttpRequest(), form = new FormData();
    form.append('file', file); if (projectId) form.append('project_id', projectId);
    x.open('POST', API_BASE + '/files');
    x.upload.onprogress = (e) => { if (e.lengthComputable) onPct(Math.round((e.loaded / e.total) * 100)); };
    x.onload = () => { let body = null; try { body = JSON.parse(x.responseText); } catch {} resolve({ status: x.status, ok: x.status >= 200 && x.status < 300, body }); };
    x.onerror = () => resolve({ status: 0, ok: false, body: null });
    x.send(form);
  });
}

// icon is injected by the shell (workspace must not import shell code); no icon = text only.
export const createLive = (React, icon = () => null) => {
  const { createElement: h, useState, useEffect, useRef, useCallback } = React;
  const useVoice = createUseVoice(React);

  function useLive(enabled, openAgent, userKey) {
    const [mode, setModeState] = useState(undefined); // undefined = not read yet (SSR), null = first run
    const [files, setFiles] = useState({ items: [], quota: null, error: null, loaded: false });
    const [up, setUp] = useState(null);
    const [project, setProject] = useState(null);
    const projectRequest = useRef(null);
    const [msgs, setMsgs] = useState([]);
    const [busy, setBusy] = useState(false);
    const [draft, setDraft] = useState('');
    const [gpu, setGpu] = useState({ tone: 'unknown', label: 'Checking GPU', detail: '' });
    const [jobs, setJobs] = useState(null);
    const { voice, toggleVoice } = useVoice((text) => setDraft((d) => (d ? d + ' ' : '') + text));
    const [preview, setPreview] = useState(null);
    const [tracked, setTracked] = useState({}); // N22: kind:id -> jobView, polled until terminal
    const [action, setAction] = useState(null); // { kind: 'measure', file } panel on a file
    const msgsRef = useRef(msgs); msgsRef.current = msgs;
    const trackedRef = useRef(tracked); trackedRef.current = tracked;
    const push = (m) => setMsgs((list) => [...list, { id: Date.now() + Math.random(), ...m }]);

    // N26: decided only once the user is known (the server-verified scene id of this account); the old global key is never read.
    useEffect(() => { setModeState(readAgentMode(globalThis.localStorage, userKey)); }, [userKey]);
    const setMode = (m) => { writeAgentMode(globalThis.localStorage, m, userKey); setModeState(m); };

    const loadFiles = useCallback(async () => {
      try { const r = await call('/files'); setFiles(r.ok ? { items: r.body?.files ?? [], quota: r.body?.quota ?? null, error: null, loaded: true } : (f) => ({ ...f, error: errText(r, 'Could not load files'), loaded: true })); }
      catch { setFiles((f) => ({ ...f, error: 'Could not load files (network).', loaded: true })); }
    }, []);
    const loadJobs = useCallback(async () => {
      const one = async (path, key) => { try { const r = await call(path); return jobsState(r.status, r.body, key); } catch { return jobsState(0, null, key); } };
      // Projects first: the first projects list seeds the SAMPLE project and its jobs on the server.
      const projects = await one('/projects', 'projects');
      const [experiments, rooms] = await Promise.all([one('/experiments', 'experiments'), one('/rooms', 'rooms')]);
      setJobs({ experiments, rooms, projects });
    }, []);
    useEffect(() => { if (enabled) { loadFiles(); loadJobs(); } }, [enabled, loadFiles, loadJobs]);
    useEffect(() => {
      if (!enabled) return undefined;
      const t = setInterval(() => { if (shouldPoll(globalThis.document)) loadJobs(); }, LIVE_JOBS_MS);
      return () => clearInterval(t);
    }, [enabled, loadJobs]);

    // GPU dot: poll every 10 s only while the tab is visible; refresh at once when it becomes visible again.
    useEffect(() => {
      if (!enabled) return undefined;
      const doc = globalThis.document;
      let snapshot = null, receivedAt = 0, stopped = false;
      const tick = () => { if (shouldPoll(doc) && !stopped) setGpu(gpuDot(snapshot, (Date.now() - receivedAt) / 1000)); };
      const poll = async () => {
        if (!shouldPoll(doc)) return;
        try { const r = await call('/gpu/status'); if (stopped) return; snapshot = r.ok ? r.body : null; }
        catch { if (stopped) return; snapshot = null; }
        receivedAt = Date.now(); tick();
      };
      poll();
      const t = setInterval(poll, GPU_POLL_MS);
      const clock = setInterval(tick, 1000); // Live countdown without multiplying Modal/API polls.
      doc?.addEventListener?.('visibilitychange', poll);
      return () => { stopped = true; clearInterval(t); clearInterval(clock); doc?.removeEventListener?.('visibilitychange', poll); };
    }, [enabled]);

    // N22: poll every tracked job that is not done or failed; stop polling when none is left.
    const pollOne = useCallback(async (kind, id) => {
      try { const r = await call((kind === 'experiment' ? '/experiments/' : '/rooms/') + encodeURIComponent(id));
        setTracked((t) => ({ ...t, [kind + ':' + id]: r.ok ? { kind, id, ...jobView(kind, r.body) } : { ...(t[kind + ':' + id] ?? { kind, id, state: 'unknown', step: 'Checking' }), poll: errText(r, 'Status check failed') } }));
      } catch { /* network blip: keep the last state, the next tick retries */ }
    }, []);
    const pending = Object.values(tracked).filter((j) => !j.terminal).map((j) => j.kind + ':' + j.id).join(',');
    useEffect(() => {
      if (!pending) return undefined;
      const t = setInterval(() => { for (const k of pending.split(',')) { const [kind, id] = k.split(':'); pollOne(kind, id); } }, POLL_MS);
      return () => clearInterval(t);
    }, [pending, pollOne]);
    const track = (kind, id) => { if (!trackedRef.current[kind + ':' + id]) setTracked((t) => ({ ...t, [kind + ':' + id]: { kind, id, state: 'queued', step: 'Queued', terminal: false } })); pollOne(kind, id); };
    // Keep tracked job ids across remounts and reloads in this tab (ids only; status and results are re-fetched).
    useEffect(() => { if (!enabled) return; try { for (const k of JSON.parse(globalThis.sessionStorage?.getItem(TRACK_KEY) || '[]')) { const [kind, id] = String(k).split(':'); if (/^(experiment|room)$/.test(kind) && id) track(kind, id); } } catch {} }, [enabled]); // eslint-disable-line react-hooks/exhaustive-deps
    useEffect(() => { try { const ks = Object.keys(tracked); if (ks.length) globalThis.sessionStorage?.setItem(TRACK_KEY, JSON.stringify(ks.slice(-20))); } catch {} }, [tracked]);

    const measure = async (file, form) => {
      const body = experimentBody(file.id, form, file.project_id);
      if (!body) return 'Click the moving object or type its name.';
      const r = await call('/experiments', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(body) }).catch(() => null);
      if (!r?.ok) return errText(r, 'Could not start the measurement');
      track('experiment', r.body.experiment.id); setAction(null); loadJobs(); return null;
    };
    const buildRoom = async (file) => {
      const r = await call('/rooms', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ file_id: file.id, project_id: file.project_id || undefined }) }).catch(() => null);
      if (!r?.ok) { setFiles((s) => ({ ...s, error: errText(r, 'Could not start the room build') })); return; }
      track('room', r.body.job.job_id);
      loadJobs();
    };
    // N16 share: POST returns { path }, DELETE revokes every active link of this experiment.
    const share = async (id, on) => {
      const r = await call('/experiments/' + encodeURIComponent(id) + '/share', { method: on ? 'POST' : 'DELETE' }).catch(() => null);
      return r?.ok ? { url: on ? globalThis.location.origin + r.body.path : null } : { error: errText(r, on ? 'Could not share' : 'Could not revoke') };
    };

    const send = async (text) => {
      const t = text.trim(); if (!t || busy) return;
      const history = historyOf(msgsRef.current);
      push({ role: 'user', text: t }); setDraft(''); setBusy(true);
      try {
        const r = await call('/agent/turn', { method: 'POST', headers: { 'content-type': 'application/json' },
          body: JSON.stringify({ text: t, ...agentTier(mode), history }) });
        if (r.ok) {
          const jobs = jobsFromToolCalls(r.body?.tool_calls);
          jobs.forEach((j) => track(j.kind, j.id));
          push({ role: 'assistant', text: r.body?.reply || '', question: r.body?.question ?? null, model: r.body?.model, jobs, fallback: Boolean(r.body?.answered_by), notice: r.body?.notice });
        } else push({ role: 'error', text: errText(r, 'The agent did not answer') });
      } catch { push({ role: 'error', text: 'The agent did not answer (network).' }); }
      finally { setBusy(false); }
    };

    const newProject = () => { projectRequest.current = null; setProject(null); push({ role: 'assistant', text: UPLOAD_QUESTION.question, question: UPLOAD_QUESTION, local: true }); openAgent?.(); };

    const answer = async (msg, picked, other) => {
      setMsgs((list) => list.map((m) => (m.id === msg.id ? { ...m, answered: questionAnswer(msg.question, picked, other) } : m)));
      if (!msg.local) return send(questionAnswer(msg.question, picked, other));
      const opt = UPLOAD_QUESTION.options[picked] ?? UPLOAD_QUESTION.options[0];
      push({ role: 'user', text: opt.label });
      projectRequest.current = call('/projects', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ mode: opt.mode, title: projectTitle(opt.mode) }) }).catch(() => null);
      const r = await projectRequest.current;
      if (r?.ok) { setProject(r.body.project); push({ role: 'assistant', text: 'Filming tips for ' + opt.label.toLowerCase() + ':', tips: TIPS[opt.mode] }); }
      else push({ role: 'error', text: errText(r, 'Could not create the project') });
      if (other?.trim()) send(other);
    };

    const upload = async (file) => {
      if (!file) return;
      setUp({ name: file.name, pct: 0, error: null });
      // A file picker can retain an older render's handler or finish while the project POST is still pending.
      const request = projectRequest.current, selected = request ? await request : null;
      if (request && (!selected?.ok || !selected.body?.project?.id)) { setUp({ name: file.name, pct: 0, error: 'Could not create the project. Try New project again.' }); return; }
      const r = await uploadXhr(file, selected?.body?.project?.id, (pct) => setUp((u) => (u ? { ...u, pct } : u)));
      setUp(r.ok ? null : { name: file.name, pct: 0, error: errText(r, 'Upload failed') });
      if (r.ok && r.body?.quota) setFiles((f) => ({ ...f, quota: r.body.quota }));
      const p = selected?.body?.project; // N55: a mode-only name becomes the clip name ("Apple drop", "Classroom lab")
      if (r.ok && p?.id && isDefaultTitle(p.title)) await renameProject(p.id, contentTitle(p.mode, file.name), true);
      loadFiles();
      loadJobs();
    };
    const renameProject = async (id, title, quiet) => {
      if (!title?.trim()) return;
      const r = await call('/projects/' + encodeURIComponent(id), { method: 'PATCH', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ title: title.trim() }) }).catch(() => null);
      if (r?.ok && r.body?.project) setProject((cur) => (cur?.id === id ? r.body.project : cur));
      else if (!quiet) setFiles((s) => ({ ...s, error: errText(r, 'Could not rename the project') }));
      if (!quiet) loadJobs();
      return r?.ok ? null : errText(r, 'Could not rename the project');
    };
    const deleteProject = async (g) => {
      if (!globalThis.confirm?.('Delete project ' + g.name + '? Its files stay in Files.')) return;
      const r = await call('/projects/' + encodeURIComponent(g.id), { method: 'DELETE' }).catch(() => null);
      if (!r?.ok) setFiles((s) => ({ ...s, error: errText(r, 'Could not delete the project') }));
      setProject((cur) => (cur?.id === g.id ? null : cur));
      loadJobs(); loadFiles();
    };
    // N89: server-side copy of a saved lab; the copy's bytes count against this user's 1 GB.
    const copyProject = async (g) => {
      const r = await call('/projects/' + encodeURIComponent(g.id) + '/copy', { method: 'POST', headers: { 'content-type': 'application/json' }, body: '{}' }).catch(() => null);
      if (!r?.ok) setFiles((s) => ({ ...s, error: errText(r, 'Could not copy the lab') }));
      loadJobs(); loadFiles();
    };
    const deleteRoom = async (id) => {
      const r = await call('/rooms/' + encodeURIComponent(id), { method: 'DELETE' }).catch(() => null);
      if (!r?.ok) { setFiles((s) => ({ ...s, error: errText(r, 'Could not delete the room') })); return; }
      setTracked((s) => { const next = { ...s }; delete next['room:' + id]; return next; });
      setMsgs((list) => list.map((m) => ({ ...m, jobs: m.jobs?.filter((j) => j.kind !== 'room' || j.id !== id) })));
      loadJobs(); loadFiles();
    };
    // N55 mode cards: the same first question, answered by the card the user picked.
    const startProject = (mode) => {
      projectRequest.current = null; setProject(null);
      const msg = { id: Date.now() + Math.random(), role: 'assistant', text: UPLOAD_QUESTION.question, question: UPLOAD_QUESTION, local: true };
      setMsgs((list) => [...list, msg]); openAgent?.();
      return answer(msg, Math.max(0, UPLOAD_QUESTION.options.findIndex((o) => o.mode === mode)), '');
    };
    const remove = async (f) => {
      if (!globalThis.confirm?.('Delete ' + f.name + '? This cannot be undone.')) return;
      const r = await call('/files/' + encodeURIComponent(f.id), { method: 'DELETE' }).catch(() => null);
      if (!r?.ok) setFiles((s) => ({ ...s, error: errText(r, 'Delete failed') }));
      if (preview === f.id) setPreview(null);
      loadFiles();
    };

    return { mode, setMode, files, up, upload, remove, preview, setPreview, project, newProject, msgs, busy, draft, setDraft, send, answer,
      gpu, jobs, loadJobs, voice, toggleVoice, tracked, track, action, setAction, measure, buildRoom, share,
      openAgent, startProject, renameProject, deleteProject, copyProject, deleteRoom, dismissUp: () => setUp(null) };
  }

  function ModeScreen({ L, settings = false, onDone }) {
    const [pick, setPick] = useState(L.mode ?? 'standard');
    return h('section', { className: 'lv-card lv-modes', 'aria-labelledby': 'lv-modes-h', 'data-slot': settings ? 'agent-settings' : 'first-run' },
      h('h2', { id: 'lv-modes-h' }, settings ? 'Agent mode' : 'Choose how the agent runs'),
      settings ? null : h('p', { className: 'lv-muted' }, 'You can change this later in the agent panel. Standard is the default.'),
      h('div', { className: 'lv-modegrid', role: 'radiogroup', 'aria-label': 'Agent mode' }, ...AGENT_MODES.map((m) =>
        h('label', { key: m.id, className: 'lv-mode', 'data-on': (pick === 'contributor') === (m.id === 'contributor') },
          h('input', { type: 'radio', name: 'lv-mode' + (settings ? '-s' : ''), value: m.id, checked: (pick === 'contributor') === (m.id === 'contributor'), onChange: () => setPick(m.id) }),
          h('span', { className: 'lv-mode-h' }, h('strong', null, m.title), m.id === 'standard' ? h('span', { className: 'lv-tag' }, 'Default') : null),
          h('span', { className: 'lv-muted' }, m.model),
          h('ul', { className: 'lv-pros', 'aria-label': 'Pros' }, ...m.pros.map((p) => h('li', { key: p }, p))),
          h('ul', { className: 'lv-cons', 'aria-label': 'Cons' }, ...m.cons.map((p) => h('li', { key: p }, p)))))),
      pick === 'contributor' ? null : h('div', { className: 'lv-modegrid', role: 'radiogroup', 'aria-label': 'Standard model' }, ...STANDARD_MODELS.map((m) =>
        h('label', { key: m.id, className: 'lv-mode', 'data-on': pick === m.id },
          h('input', { type: 'radio', name: 'lv-std' + (settings ? '-s' : ''), value: m.id, checked: pick === m.id, onChange: () => setPick(m.id) }),
          h('strong', null, m.label)))),
      h('button', { type: 'button', className: 'lv-btn lv-primary', onClick: () => { L.setMode(pick); onDone?.(); } }, settings ? 'Save' : 'Continue'));
  }

  function QuestionCard({ msg, onAnswer }) {
    const q = msg.question;
    const [picked, setPicked] = useState(recommendedIndex(q));
    const [other, setOther] = useState('');
    if (msg.answered) return h('p', { className: 'lv-answered' }, h('span', { className: 'lv-muted' }, q.question + ' '), h('strong', null, msg.answered));
    const submit = (e) => { e?.preventDefault?.(); onAnswer(msg, picked, other); };
    return h('form', { className: 'r2s-qcard lv-q', 'aria-label': 'Agent question', onSubmit: submit,
      onKeyDown: (e) => { if (/^[1-9]$/.test(e.key) && !/^(TEXTAREA|INPUT)$/.test(e.target.tagName) && q.options[e.key - 1]) { e.preventDefault(); setPicked(e.key - 1); }
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') submit(e); } },
      h('fieldset', null, h('legend', null, q.question),
        h('ol', { className: 'r2s-qopts' }, ...q.options.map((o, i) => h('li', { key: i },
          h('button', { type: 'button', className: 'r2s-qopt', 'aria-pressed': picked === i && !other.trim(), onClick: () => { setPicked(i); setOther(''); } },
            h('kbd', { 'aria-hidden': true }, String(i + 1)), h('span', null, o.label, o.hint ? h('small', { className: 'lv-muted lv-block' }, o.hint) : null),
            o.recommended ? h('span', { className: 'lv-tag' }, 'Recommended') : null)))),
        h('label', { className: 'r2s-qother' }, 'Other', h('textarea', { rows: 2, maxLength: 300, value: other, placeholder: 'Type your own answer', onChange: (e) => setOther(e.target.value) }))),
      h('div', { className: 'r2s-qactions' }, h('button', { type: 'submit', className: 'r2s-qsubmit' }, 'Continue', h('kbd', { 'aria-hidden': true }, 'Ctrl+Enter'))));
  }

  function Chat({ L }) {
    const [settings, setSettings] = useState(false);
    const end = useRef(null);
    useEffect(() => { end.current?.scrollIntoView?.({ block: 'nearest' }); }, [L.msgs.length, L.busy]);
    const vs = L.voice.state;
    return h('section', { className: 'lv-chat', 'aria-labelledby': 'lv-chat-h' },
      h('div', { className: 'lv-chat-head' }, h('h3', { id: 'lv-chat-h' }, 'Agent'),
        h('button', { type: 'button', className: 'lv-chip', 'aria-expanded': settings, onClick: () => setSettings(!settings), title: 'Change agent mode' },
          modeLabel(L.mode))),
      settings ? h(ModeScreen, { L, settings: true, onDone: () => setSettings(false) }) : null,
      h('ol', { className: 'lv-msgs', 'aria-live': 'polite', 'aria-label': 'Conversation' },
        L.msgs.length ? null : h('li', { className: 'lv-muted lv-empty' }, 'Ask about a physics experiment, or start a new project. Physics questions only.'),
        ...L.msgs.map((m) => h('li', { key: m.id, className: 'lv-msg', 'data-role': m.role },
          m.question ? h(QuestionCard, { msg: m, onAnswer: L.answer }) : h('p', { role: m.role === 'error' ? 'alert' : undefined }, m.text),
          m.notice ? h('small', { className: 'lv-muted lv-block', role: 'status' }, m.notice) : null,
          m.fallback ? h('small', { className: 'lv-muted lv-block' }, 'Answered by fallback model') : null,
          ...(m.jobs ?? []).map((j) => h(JobCard, { key: j.kind + j.id, L, kind: j.kind, id: j.id })),
          m.tips ? h('ul', { className: 'lv-tips' }, ...m.tips.map((t) => h('li', { key: t }, t))) : null)),
        L.busy ? h('li', { className: 'lv-msg lv-muted', 'data-role': 'assistant' }, h('span', { className: 'r2s-pulse', 'aria-hidden': true }), ' Thinking') : null,
        h('li', { ref: end, 'aria-hidden': true })),
      h('form', { className: 'lv-compose', onSubmit: (e) => { e.preventDefault(); L.send(L.draft); } },
        h('label', { className: 'r2s-sr', htmlFor: 'lv-draft' }, 'Message the agent'),
        h('textarea', { id: 'lv-draft', rows: 2, maxLength: 4000, value: L.draft, placeholder: 'Message the agent', onChange: (e) => L.setDraft(e.target.value),
          onKeyDown: (e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); L.send(L.draft); } } }),
        h('div', { className: 'lv-row' },
          h('button', { type: 'button', className: 'lv-btn', 'data-voice': vs, 'aria-pressed': vs === 'recording', disabled: vs === 'working' || vs === 'requesting', onClick: L.toggleVoice,
            title: 'Voice input, up to 60 s' }, vs === 'requesting' ? 'Waiting for microphone' : vs === 'recording' ? 'Stop recording' : vs === 'working' ? 'Transcribing' : 'Voice'),
          h('button', { type: 'submit', className: 'lv-btn lv-primary', disabled: L.busy || !L.draft.trim() }, 'Send')),
        L.voice.error ? h('p', { className: 'ws-error', role: 'alert' }, L.voice.error) : null));
  }

  function Dot({ L }) {
    const d = L.gpu;
    return h('span', { className: 'lv-gpu', 'data-tone': d.tone, role: 'status', title: d.detail ? d.label + '. ' + d.detail : d.label },
      h('span', { className: 'lv-dot', 'aria-hidden': true }), h('span', { className: 'lv-gpu-text' }, d.label, d.detail ? h('small', null, ' ' + d.detail) : null));
  }

  function MeasurePanel({ L, file }) {
    const [f, setF] = useState({ point: null, name: '', size: '', unit: 'cm', what: '' });
    const [dims, setDims] = useState(null);
    const [err, setErr] = useState(null);
    const [busy, setBusy] = useState(false);
    const set = (k) => (e) => { const v = e.target.value; setF((s) => ({ ...s, [k]: v, ...(k === 'name' && v.trim() ? { point: null } : {}) })); };
    const pick = (e) => { const el = e.currentTarget, p = naturalPoint(e.nativeEvent.offsetX, e.nativeEvent.offsetY, el.clientWidth, el.clientHeight, el.videoWidth, el.videoHeight); if (p) setF((s) => ({ ...s, point: p, name: '' })); };
    const start = async (e) => { e.preventDefault(); setBusy(true); setErr(await L.measure(file, f)); setBusy(false); };
    const ready = !!f.point || !!f.name.trim();
    return h('form', { className: 'lv-measure', onSubmit: start, 'aria-label': 'Measure this experiment' },
      h('p', null, h('strong', null, 'Step 1. '), 'Click the moving object on the first frame, or type its name.'),
      h('div', { className: 'lv-still' },
        h('video', { src: API_BASE + '/files/' + encodeURIComponent(file.id) + '/content', muted: true, playsInline: true, preload: 'auto', onClick: pick,
          'aria-label': 'First frame of ' + file.name + '. Click the moving object.',
          onLoadedMetadata: (e) => { const v = e.currentTarget; v.currentTime = 0; setDims({ w: v.videoWidth, h: v.videoHeight }); } }),
        f.point && dims ? h('span', { className: 'lv-mark', 'aria-hidden': true, style: { left: (100 * f.point.x) / dims.w + '%', top: (100 * f.point.y) / dims.h + '%' } }) : null),
      h('p', { className: 'lv-muted', role: 'status' }, f.point ? 'Picked pixel x ' + f.point.x + ', y ' + f.point.y + ' on the first frame.' : 'No point picked yet.'),
      h('label', { className: 'lv-field' }, 'Or its name', h('input', { value: f.name, maxLength: 80, placeholder: 'for example: apple', onChange: set('name') })),
      h('fieldset', { className: 'lv-size' }, h('legend', null, h('strong', null, 'Step 2. '), 'Known size (optional)'),
        h('label', { className: 'lv-field' }, 'What it is', h('input', { value: f.what, maxLength: 120, placeholder: 'ball diameter', onChange: set('what') })),
        h('label', { className: 'lv-field lv-num' }, 'Value', h('input', { type: 'number', inputMode: 'decimal', min: 0, step: 'any', value: f.size, onChange: set('size') })),
        h('label', { className: 'lv-field lv-num' }, 'Unit', h('select', { value: f.unit, onChange: set('unit') }, ...SIZE_UNITS.map((u) => h('option', { key: u, value: u }, u)))),
        h('p', { className: 'lv-muted' }, 'Without a known size the result stays in pixels, labelled scale unverified.')),
      h('div', { className: 'lv-row' }, h('button', { type: 'submit', className: 'lv-btn lv-primary', disabled: busy || !ready }, busy ? 'Starting' : 'Start measuring'),
        h('button', { type: 'button', className: 'lv-btn', onClick: () => L.setAction(null) }, 'Cancel')),
      err ? h('p', { className: 'ws-error', role: 'alert' }, err) : null);
  }

  function Chart({ result }) {
    const g = chartGeom(result);
    if (!g) return null;
    const b = g.box;
    return h('figure', { className: 'lv-chart' },
      h('svg', { viewBox: '0 0 ' + g.W + ' ' + g.H, role: 'img', 'aria-label': 'Tracked ' + g.yLabel + ' against ' + g.xLabel + ' with the fitted curve and its 1 sigma band' },
        ...g.yTicks.map((t) => h('g', { key: 'y' + t.label }, h('line', { x1: b.L, x2: b.R, y1: t.y, y2: t.y, className: 'lv-grid' }),
          h('text', { x: b.L - 6, y: t.y + 3.5, textAnchor: 'end', className: 'lv-tick' }, t.label))),
        ...g.xTicks.map((t) => h('g', { key: 'x' + t.label }, h('line', { x1: t.x, x2: t.x, y1: b.T, y2: b.B, className: 'lv-grid' }),
          h('text', { x: t.x, y: b.B + 14, textAnchor: 'middle', className: 'lv-tick' }, t.label))),
        h('path', { d: 'M' + b.L + ' ' + b.T + 'V' + b.B + 'H' + b.R, className: 'lv-axis' }),
        g.band ? h('path', { d: g.band, className: 'lv-band' }) : null, g.curve ? h('path', { d: g.curve, className: 'lv-curve' }) : null,
        ...g.points.map((p, i) => h('circle', { key: i, cx: p.cx, cy: p.cy, r: 2.6, className: 'lv-pt' })),
        h('text', { x: (b.L + b.R) / 2, y: g.H - 4, textAnchor: 'middle', className: 'lv-axis-label' }, g.xLabel),
        h('text', { x: 11, y: (b.T + b.B) / 2, textAnchor: 'middle', transform: 'rotate(-90 11 ' + (b.T + b.B) / 2 + ')', className: 'lv-axis-label' }, g.yLabel)),
      h('figcaption', { className: 'lv-muted' }, g.curve ? 'Dots: MEASURED track, ' + g.points.length + ' frames. Line: fitted curve.' + (g.band ? ' Band: 1 sigma of the fit.' : ' No 1 sigma band for this fit.')
        : 'Dots: tracked positions, ' + g.points.length + ' frames. No fitted curve.'));
  }

  function Share({ L, id }) {
    const [s, setS] = useState(null);
    const go = async (on) => { setS({ busy: true }); setS(await L.share(id, on)); };
    if (s?.url) return h('div', { className: 'lv-row lv-share' },
      h('input', { readOnly: true, value: s.url, 'aria-label': 'Challenge link', onFocus: (e) => e.target.select() }),
      h('button', { type: 'button', className: 'lv-btn', onClick: () => globalThis.navigator.clipboard?.writeText(s.url).then(() => setS({ ...s, copied: true }), () => {}) }, s.copied ? 'Copied' : 'Copy link'),
      h('button', { type: 'button', className: 'lv-btn lv-danger', onClick: () => go(false) }, 'Revoke'));
    return h('div', { className: 'lv-row' }, h('button', { type: 'button', className: 'lv-btn', disabled: s?.busy, onClick: () => go(true) }, 'Share as Guess the Gravity'),
      s?.error ? h('span', { className: 'ws-error', role: 'alert' }, s.error) : s && !s.busy ? h('span', { className: 'lv-muted' }, 'Link revoked.') : null);
  }

  function Result({ L, id, result }) {
    const q = result?.quantity, tag = scaleTag(result), gc = gravityCheck(result);
    return h('div', { className: 'lv-result' },
      q ? h('p', { className: 'lv-qty' }, h('span', { className: 'lv-muted lv-block' }, q.name), h('strong', null, fmtPm(q.value, q.uncertainty) + ' ' + q.unit), h('small', { className: 'lv-muted' }, ' 1 sigma'))
        : h('p', { role: 'status' }, 'No value reported. ' + (result?.reason ? 'No fit: ' + result.reason : result?.label || '')),
      h('div', { className: 'lv-row' }, h('span', { className: 'lv-tag', 'data-tone': tag.tone }, tag.text),
        h('span', { className: 'lv-tag', 'data-tone': 'warn' }, 'playback clock'), result?.motion ? h('span', { className: 'lv-tag' }, String(result.motion).replace(/_/g, ' ')) : null),
      gc ? h('p', { className: 'lv-muted', 'data-tone': gc.tone }, gc.text) : null,
      h('ul', { className: 'lv-labels lv-muted' }, ...labelsOf(result).map((t) => h('li', { key: t }, t))),
      h(Chart, { result }),
      h('div', { className: 'lv-row' }, h('a', { className: 'lv-btn lv-primary', href: '/lab?editor=1&experiment=' + encodeURIComponent(id) }, '3D replay, redo with changes')),
      shareable(result) ? h(Share, { L, id }) : h('p', { className: 'lv-muted' }, 'Guess the Gravity needs a known size, so the value is in m/s^2.'));
  }

  // One progress card for both modes, used in Processing and in the agent chat.
  function JobCard({ L, kind, id }) {
    const j = L.tracked[kind + ':' + id] ?? { state: 'queued', step: 'Queued' };
    const g = j.gpu ? gpuDot(j.gpu) : L.gpu;
    const sample = kind === 'experiment' ? L.jobs?.experiments?.items?.find((x) => x.id === id)?.sample : null;
    return h('div', { className: 'lv-jobcard', 'data-state': j.state },
      h('div', { className: 'lv-row lv-between' }, h('strong', { title: id }, sample ? sample.title : jobName({ id }, kind === 'experiment' ? 'experiment' : 'room').replace(/^Experiment/, 'Measurement').replace(/^Room/, 'Room lab')),
        sample ? h('span', { className: 'lv-tag', 'data-tone': 'warn' }, 'SAMPLE') : null, h('span', { className: 'lv-tag', role: 'status' }, j.step)),
      !j.terminal ? h(React.Fragment, null, h('progress', { 'aria-label': j.step }),
        h('p', { className: 'lv-muted' }, (kind === 'experiment' ? 'Hosted model, no GPU wait. Backup ' : '') + g.label + (g.detail ? '. ' + g.detail : '') + '.')) : null,
      j.error ? h('p', { className: 'ws-error', role: 'alert' }, j.error) : null,
      j.poll ? h('p', { className: 'lv-muted' }, j.poll) : null,
      j.state === 'done' && kind === 'experiment' ? h(Result, { L, id, result: j.result }) : null,
      j.state === 'done' && kind === 'room' ? h('div', { className: 'lv-row' }, h('a', { className: 'lv-btn lv-primary', href: '/lab?editor=1&room=' + encodeURIComponent(id) }, 'Open my lab'),
        ...(j.labels ?? []).map((t) => h('span', { key: t, className: 'lv-tag', 'data-tone': /unverified/.test(t) ? 'warn' : undefined }, t))) : null);
  }

  // N55: small icon-only menu; closes itself after an action.
  const closeMenu = (e) => { const d = e.currentTarget.closest('details'); if (d) d.open = false; };
  function Menu({ label, items }) {
    return h('details', { className: 'lv-menu' },
      h('summary', { className: 'lv-iconbtn', 'aria-label': label, title: label }, icon(h, 'more', 18)),
      h('div', { className: 'lv-menu-pop', role: 'menu' }, ...items.filter(Boolean).map((it) => it.href
        ? h('a', { key: it.label, role: 'menuitem', href: it.href, download: it.download, onClick: closeMenu }, it.label)
        : h('button', { key: it.label, type: 'button', role: 'menuitem', 'data-danger': it.danger || undefined, onClick: (e) => { closeMenu(e); it.onClick(); } }, it.label))));
  }
  // Preview: saved lab snapshot (N56) if the project has one, else a frame of its video, else a type icon.
  function Thumb({ f, snapshot, kind }) {
    const [bad, setBad] = useState(false);
    if (snapshot && !bad) return h('img', { className: 'lv-thumb', src: snapshot, alt: '', loading: 'lazy', onError: () => setBad(true) });
    if (f?.media_type?.startsWith('video/')) return h('video', { className: 'lv-thumb', src: fileUrl(f) + '#t=0.5', preload: 'metadata', muted: true, playsInline: true, 'aria-hidden': true, tabIndex: -1 });
    if (f?.media_type?.startsWith('image/')) return h('img', { className: 'lv-thumb', src: fileUrl(f), alt: '', loading: 'lazy' });
    return h('span', { className: 'lv-thumb lv-thumb-empty', 'data-kind': kind, 'aria-hidden': true }, icon(h, kind === 'room' ? 'cube' : 'chart', 28));
  }
  function Ring({ value }) {
    const c = 2 * Math.PI * 7, v = Number.isFinite(value) ? Math.min(1, Math.max(0, value)) : null;
    return h('svg', { className: 'lv-ring', 'data-spin': v == null || undefined, viewBox: '0 0 18 18', width: 16, height: 16, 'aria-hidden': true },
      h('circle', { cx: 9, cy: 9, r: 7, fill: 'none', strokeWidth: 2.5, className: 'lv-ring-bg' }),
      h('circle', { cx: 9, cy: 9, r: 7, fill: 'none', strokeWidth: 2.5, strokeLinecap: 'round', strokeDasharray: c, strokeDashoffset: c * (1 - (v ?? 0.3)), transform: 'rotate(-90 9 9)' }));
  }

  function ModelPicker({ L }) {
    const [open, setOpen] = useState(!!L.pickerOpen), [notice, setNotice] = useState(false); // pickerOpen: static screenshot fixture only
    const curId = MODEL_CHOICES.some((m) => m.id === L.mode) ? L.mode : 'standard';
    const [hover, setHover] = useState(curId);
    const cur = MODEL_CHOICES.find((m) => m.id === curId), shown = MODEL_CHOICES.find((m) => m.id === hover) ?? cur;
    const choose = (id) => { L.setMode(id); setOpen(false); setNotice(false); };
    return h('div', { className: 'lv-picker', onKeyDown: (e) => { if (e.key === 'Escape' && open) { e.stopPropagation(); setOpen(false); } } },
      h('button', { type: 'button', className: 'lv-pickbtn', 'aria-haspopup': 'dialog', 'aria-expanded': open, onClick: () => { setHover(curId); setNotice(false); setOpen(!open); } },
        h('span', { className: 'lv-dotmodel', 'aria-hidden': true }), h('span', { className: 'lv-model-name' }, cur.name), h('small', null, cur.sub), icon(h, 'chev', 14)),
      open ? h('div', { className: 'lv-pickpop', role: 'dialog', 'aria-label': 'Choose the agent model' },
        notice ? h('div', { className: 'lv-notice', role: 'alertdialog', 'aria-labelledby': 'lv-contrib-h' },
          h('strong', { id: 'lv-contrib-h' }, 'Contributor mode shares your prompts'),
          h('ul', null, ...AGENT_MODES[1].cons.map((c) => h('li', { key: c }, c))),
          h('div', { className: 'lv-row' }, h('button', { type: 'button', className: 'lv-btn lv-primary', onClick: () => choose('contributor') }, 'Use contributor'),
            h('button', { type: 'button', className: 'lv-btn', onClick: () => setNotice(false) }, 'Keep my current model')))
          : h(React.Fragment, null,
            h('ul', { className: 'lv-picklist' }, ...MODEL_CHOICES.map((m) => h('li', { key: m.id },
              h('button', { type: 'button', className: 'lv-pickrow', 'aria-pressed': m.id === curId, onMouseEnter: () => setHover(m.id), onFocus: () => setHover(m.id),
                onClick: () => (m.id === 'contributor' && curId !== 'contributor' ? setNotice(true) : choose(m.id)) },
                h('span', { className: 'lv-pickname' }, h('strong', null, m.name), h('small', null, m.sub)),
                h('span', { className: 'lv-pill', 'data-tag': m.tag }, m.tag), m.id === curId ? icon(h, 'check', 16) : null)))),
            h('div', { className: 'lv-pickside', 'aria-live': 'polite' },
              h('strong', null, shown.name + ' ' + shown.sub),
              ...Object.entries(shown.bars).map(([k, v]) => h('div', { key: k, className: 'lv-bar' }, h('span', null, k),
                h('span', { className: 'lv-bar-track', role: 'img', 'aria-label': k + ' ' + ['', 'low', 'medium', 'high'][v] + ', relative' }, h('span', { style: { width: (v / 3) * 100 + '%' } })))),
              h('p', { className: 'lv-pro' }, shown.pro), h('p', { className: 'lv-con' }, shown.con),
              h('small', { className: 'lv-muted' }, 'Relative only: real speed and cost depend on the task.')))) : null);
  }

  function Home({ L }) {
    const [file, setFile] = useState(null), [drag, setDrag] = useState(false);
    const vs = L.voice.state, q = quotaView(L.files.quota);
    const pickFile = (f) => { if (f) setFile(f); };
    const submit = (e) => {
      e.preventDefault();
      if (file) { L.upload(file); setFile(null); }
      if (L.draft.trim()) { L.openAgent?.(); L.send(L.draft); }
    };
    return h('section', { className: 'lv-home', 'aria-labelledby': 'lv-home-h', id: 'lv-home' },
      h('h2', { id: 'lv-home-h', className: 'lv-hero' }, 'What do you want to simulate?'),
      h('form', { className: 'lv-prompt', 'data-drag': drag || undefined, onSubmit: submit,
        onDragOver: (e) => { e.preventDefault(); setDrag(true); }, onDragLeave: () => setDrag(false),
        onDrop: (e) => { e.preventDefault(); setDrag(false); pickFile(e.dataTransfer?.files?.[0]); } },
        h('label', { className: 'r2s-sr', htmlFor: 'lv-prompt-text' }, 'Describe what you want to simulate'),
        h('textarea', { id: 'lv-prompt-text', rows: 3, maxLength: 4000, value: L.draft, placeholder: 'Describe an experiment or ask a physics question. Drop a video here to upload it.',
          onChange: (e) => L.setDraft(e.target.value), onKeyDown: (e) => { if (e.key === 'Enter' && !e.shiftKey) submit(e); } }),
        file || L.project ? h('div', { className: 'lv-chips' },
          L.project ? h('span', { className: 'lv-chip2' }, icon(h, L.project.mode === 'room' ? 'cube' : 'chart', 14), L.project.title) : null,
          file ? h('span', { className: 'lv-chip2' }, icon(h, 'film', 14), file.name, h('small', null, fmtBytes(file.size)),
            h('button', { type: 'button', className: 'lv-x', 'aria-label': 'Remove ' + file.name, onClick: () => setFile(null) }, icon(h, 'close', 12))) : null) : null,
        h('div', { className: 'lv-prompt-bar' },
          h('label', { className: 'lv-iconbtn lv-file', title: 'Attach a video (' + LIMITS + ')', 'aria-disabled': q?.full || undefined },
            icon(h, 'clip', 18), h('span', { className: 'r2s-sr' }, 'Attach a video'),
            h('input', { type: 'file', accept: ACCEPT, disabled: q?.full || (!!L.up && !L.up.error), onChange: (e) => { pickFile(e.target.files?.[0]); e.target.value = ''; } })),
          h(ModelPicker, { L }),
          h('span', { className: 'lv-grow' }),
          h('button', { type: 'button', className: 'lv-iconbtn', 'data-voice': vs, 'aria-pressed': vs === 'recording', disabled: vs === 'working' || vs === 'requesting', onClick: L.toggleVoice,
            title: vs === 'requesting' ? 'Waiting for microphone' : vs === 'recording' ? 'Stop recording' : vs === 'working' ? 'Transcribing' : 'Voice input, up to 60 s', 'aria-label': vs === 'requesting' ? 'Waiting for microphone' : vs === 'working' ? 'Transcribing' : 'Voice input' }, icon(h, 'mic', 18)),
          h('button', { type: 'submit', className: 'lv-send', 'aria-label': 'Send', title: 'Send', disabled: L.busy || (!file && !L.draft.trim()) }, icon(h, 'send', 18)))),
      L.voice.error ? h('p', { className: 'ws-error', role: 'alert' }, L.voice.error) : null,
      h('div', { className: 'lv-modecards' },
        h('button', { type: 'button', className: 'lv-modecard', onClick: () => L.startProject('room') }, h('span', { className: 'lv-mc-icon' }, icon(h, 'cube', 20)),
          h('span', null, h('strong', null, 'Turn your room into a lab'), h('small', null, 'Film a room; get an editable virtual lab with physics.'))),
        h('button', { type: 'button', className: 'lv-modecard', onClick: () => L.startProject('experiment') }, h('span', { className: 'lv-mc-icon' }, icon(h, 'chart', 20)),
          h('span', null, h('strong', null, 'Measure your experiment'), h('small', null, 'Film a motion; get a fit with uncertainty and a 3D replay.'))),
        // N89: no video needed. Templates open read-only until Make my copy saves the user's own version.
        h('a', { className: 'lv-modecard', href: '/lab?editor=1&template=physics-lab' }, h('span', { className: 'lv-mc-icon' }, icon(h, 'flask', 20)),
          h('span', null, h('strong', null, 'Physics lab template'), h('small', null, 'No video needed: a furnished lab with 14 apparatus types, ready to run.'))),
        h('a', { className: 'lv-modecard', href: '/lab?editor=1&template=blank' }, h('span', { className: 'lv-mc-icon' }, icon(h, 'plus', 20)),
          h('span', null, h('strong', null, 'Blank lab template'), h('small', null, 'No video needed: an empty grid floor to build on.')))));
  }

  function ProjectCard({ L, g, small }) {
    const [renaming, setRenaming] = useState(false), [title, setTitle] = useState(g.name), [renameError, setRenameError] = useState(null);
    const [roomDelete, setRoomDelete] = useState(null), [deletingRoom, setDeletingRoom] = useState(false);
    const cancelRoomDelete = (e) => {
      setRoomDelete(null);
      e.currentTarget.closest('.lv-pcard')?.querySelector('.lv-menu > summary')?.focus();
    };
    const saveName = async () => {
      if (!title.trim()) { setRenameError('Enter a project name.'); return; }
      const error = await L.renameProject(g.id, title);
      if (error) setRenameError(error); else { setRenaming(false); setRenameError(null); }
    };
    const st = g.status, kind = g.mode ?? (g.rooms.length ? 'room' : 'experiment');
    const pathPlot = !g.snapshot && g.trackPreview?.kind === 'plot';
    const sourceId = g.trackPreview?.file_id ?? st.job?.file_id;
    const f = sourceId ? g.files.find((x) => x.id === sourceId) : g.files.find((x) => x.media_type?.startsWith('video/')) || g.files[0];
    const room = groupStatus({ ...g, experiments: [] }, L.tracked);
    const target = room.state === 'ready' ? room : st;
    const experiment = target.kind === 'experiment' ? target : groupStatus({ ...g, rooms: [] }, L.tracked);
    const experimentId = experiment.job?.id ?? experiment.job?.job_id;
    const openExperiment = () => { L.track('experiment', experimentId); setTimeout(() => globalThis.document?.getElementById('lv-activity')?.scrollIntoView?.({ behavior: 'smooth' }), 50); };
    const id = target.job?.id ?? target.job?.job_id;
    const href = target.state === 'ready' && id ? '/lab?editor=1&' + (target.kind === 'room' ? 'room=' : 'experiment=') + encodeURIComponent(id)
      : st.state === 'saved' && g.id ? '/lab?editor=1&project=' + encodeURIComponent(g.id) : null;
    const open = () => {
      if (target.kind === 'experiment' && id) openExperiment();
      else if (href) globalThis.location.assign(href);
      else L.openAgent?.();
    };
    const when = relTime(g.created ?? st.job?.created ?? st.job?.created_at);
    return h('li', { className: 'lv-pcard', 'data-small': small || undefined, 'data-state': st.state, 'data-sample': g.sample || undefined },
      h('button', { type: 'button', className: 'lv-pcard-hit', onClick: open, 'aria-label': 'Open ' + g.name }),
      small ? null : h('div', { className: 'lv-pcard-media' }, pathPlot ? null : h(Thumb, { f, snapshot: g.snapshot, kind }),
        !g.snapshot && (pathPlot || f?.media_type?.startsWith('video/') && f.id === g.trackPreview?.file_id) ? h('svg', { className: 'lv-track-preview', 'data-plot': pathPlot || undefined, viewBox: '0 0 ' + g.trackPreview.width + ' ' + g.trackPreview.height, preserveAspectRatio: pathPlot ? 'xMidYMid meet' : 'xMidYMid slice', role: 'img', 'aria-label': g.trackPreview.label },
          h('polyline', { points: g.trackPreview.points.map((p) => p.join(',')).join(' '), fill: 'none', stroke: '#ffbe0b', strokeWidth: 3, vectorEffect: 'non-scaling-stroke' })) : null,
        pathPlot ? h('small', { className: 'lv-path-label' }, g.trackPreview.label) : null,
        g.sample ? h('span', { className: 'lv-badge' }, 'SAMPLE') : null),
      h('div', { className: 'lv-pcard-body' },
        h('span', { className: 'lv-type', title: kind === 'room' ? 'Room lab' : 'Experiment' }, icon(h, kind === 'room' ? 'cube' : 'chart', 16)),
        h('div', { className: 'lv-pcard-text' },
          renaming ? h('form', { className: 'lv-rename', onSubmit: (e) => { e.preventDefault(); saveName(); } },
            h('input', { autoFocus: true, 'aria-label': 'Project name', value: title, maxLength: 120, onChange: (e) => setTitle(e.target.value), onKeyDown: (e) => { if (e.key === 'Escape') setRenaming(false); } }),
            h('button', { type: 'submit' }, 'Save'), h('button', { type: 'button', onClick: () => setRenaming(false) }, 'Cancel'),
            renameError ? h('small', { role: 'alert' }, renameError) : null) : h('strong', { className: 'lv-pname', title: g.name }, g.name),
          h('span', { className: 'lv-pmeta' },
            st.state === 'processing' ? h('span', { className: 'lv-st', 'data-st': 'processing' }, h(Ring, { value: st.progress }), st.step || 'Processing')
              : st.state === 'ready' ? h('span', { className: 'lv-st', 'data-st': 'ready' }, 'Ready')
              : st.state === 'failed' ? h('span', { className: 'lv-st', 'data-st': 'failed', title: String(st.reason) }, 'Failed: ' + st.reason)
              : h('span', { className: 'lv-st' }, st.state === 'saved' ? 'Saved lab' : g.files.length ? g.files.length + (g.files.length === 1 ? ' file' : ' files') : 'Empty'),
            when ? h('span', null, when) : null,
            g.sample ? h('span', { className: 'lv-tagsm' }, 'RECORDED') : null)),
        h(Menu, { label: 'Project actions for ' + g.name, items: [
          { label: 'Open', onClick: open },
          target.kind === 'room' && experimentId ? { label: 'Open experiment', onClick: openExperiment } : null,
          g.sample || !g.id ? null : { label: 'Rename', onClick: () => { setTitle(g.name); setRenameError(null); setRenaming(true); } },
          g.lab && g.id ? { label: 'Make a copy', onClick: () => L.copyProject(g) } : null,
          f ? { label: 'Download video', href: fileUrl(f), download: f.name } : null,
          g.sample || !g.id ? null : { label: 'Delete', danger: true, onClick: () => L.deleteProject(g) },
          ...g.rooms.filter((r) => !r.sample).map((r) => ({ label: 'Delete room ' + (r.id ?? r.job_id).slice(0, 8), danger: true,
            onClick: () => setRoomDelete(r.id ?? r.job_id) }))] })),
      roomDelete ? h('div', { className: 'lv-room-delete', role: 'alertdialog', 'aria-label': 'Delete room ' + roomDelete.slice(0, 8),
        'aria-describedby': 'room-delete-warning-' + roomDelete,
        onKeyDown: (e) => { if (e.key === 'Escape' && !deletingRoom) cancelRoomDelete(e); } },
        h('p', { id: 'room-delete-warning-' + roomDelete }, 'Delete this room? Its 3D files and lab edits are removed. This cannot be undone.'),
        h('div', { className: 'lv-row' },
          h('button', { type: 'button', autoFocus: true, disabled: deletingRoom, onClick: cancelRoomDelete }, 'Cancel'),
          h('button', { type: 'button', 'data-danger': true, disabled: deletingRoom, onClick: async () => {
            setDeletingRoom(true);
            try { await L.deleteRoom(roomDelete); setRoomDelete(null); } finally { setDeletingRoom(false); }
          } }, deletingRoom ? 'Deleting…' : 'Delete room'))) : null);
  }

  function ProjectsGrid({ L }) {
    const [showEmpty, setShowEmpty] = useState(false);
    if (!L.jobs) return h('section', { className: 'lv-projects', 'aria-busy': true }, h('h2', null, 'Projects'), h('p', { className: 'lv-muted', role: 'status' }, 'Loading projects.'));
    const { experiments: e, rooms: r, projects: p } = L.jobs;
    const err = [e, r, p].find((j) => j?.state === 'error');
    const groups = groupJobs(p?.items ?? [], e?.items ?? [], r?.items ?? [])
      .map((g) => {
        const sources = new Set([...g.rooms, ...g.experiments].map((j) => j.file_id).filter(Boolean));
        return { ...g, files: L.files.items.filter((f) => (g.id && f.project_id === g.id) || sources.has(f.id)), status: groupStatus(g, L.tracked) };
      });
    const full = groups.filter((g) => g.sample || g.status.state !== 'empty' || g.files.length), empty = groups.filter((g) => !full.includes(g));
    return h('section', { className: 'lv-projects', 'aria-labelledby': 'lv-proj-h', id: 'lv-project' },
      h('div', { className: 'lv-head' }, h('h2', { id: 'lv-proj-h' }, 'Projects'),
        empty.length ? h('button', { type: 'button', className: 'lv-link', 'aria-pressed': showEmpty, onClick: () => setShowEmpty(!showEmpty) },
          (showEmpty ? 'Hide empty' : 'Show empty') + ' (' + empty.length + ')') : null),
      err ? h('p', { className: 'ws-error', role: 'alert' }, err.message) : null,
      L.files.error ? h('p', { className: 'ws-error', role: 'alert' }, L.files.error) : null,
      h('ul', { className: 'lv-pgrid' },
        h('li', { className: 'lv-pcard lv-new' }, h('button', { type: 'button', onClick: L.newProject }, icon(h, 'plus', 22), h('strong', null, 'New project'),
          h('small', null, 'The agent asks what you are filming'))),
        ...full.map((g) => h(ProjectCard, { key: g.id ?? 'none', L, g }))),
      showEmpty && empty.length ? h('ul', { className: 'lv-pgrid lv-pgrid-small' }, ...empty.map((g) => h(ProjectCard, { key: g.id, L, g, small: true }))) : null);
  }

  // N55: Shopify-style progress pop-up for uploads and running jobs (the cards update live too).
  function Progress({ L }) {
    const [min, setMin] = useState(false);
    const active = Object.values(L.tracked).filter((j) => !j.terminal);
    if (!L.up && !active.length) return null;
    const n = active.length + (L.up && !L.up.error ? 1 : 0);
    return h('aside', { className: 'lv-toast', 'aria-label': 'Progress', 'data-min': min || undefined },
      h('div', { className: 'lv-toast-head' }, h('strong', { role: 'status' }, n ? 'Processing ' + n + (n === 1 ? ' item' : ' items') : 'Upload stopped'),
        h('button', { type: 'button', className: 'lv-iconbtn', 'aria-expanded': !min, 'aria-label': min ? 'Show progress' : 'Hide progress', onClick: () => setMin(!min) }, icon(h, 'chev', 16))),
      min ? null : h('ul', null,
        L.up ? h('li', { key: 'up' }, icon(h, 'upload', 16), h('span', { className: 'lv-toast-text' }, h('span', null, L.up.name),
          L.up.error ? h('small', { className: 'ws-error', role: 'alert' }, L.up.error) : h('progress', { max: 100, value: L.up.pct, 'aria-label': 'Upload progress' })),
          L.up.error ? h('button', { type: 'button', className: 'lv-iconbtn', 'aria-label': 'Dismiss', onClick: L.dismissUp }, icon(h, 'close', 14)) : h('small', null, L.up.pct + '%')) : null,
        ...active.map((j) => h('li', { key: j.kind + j.id }, h(Ring, null), h('span', { className: 'lv-toast-text' },
          h('span', null, j.kind === 'room' ? 'Room lab' : 'Measurement'), h('small', { className: 'lv-muted' }, j.step + (j.kind === 'room' ? '. ' + L.gpu.label : '')))))));
  }

  function Files({ L }) {
    const q = quotaView(L.files.quota), sel = L.files.items.find((f) => f.id === L.preview);
    const modeOf = (f) => L.jobs?.projects?.items?.find((p) => p.id === f.project_id)?.mode;
    return h('section', { className: 'lv-filesview', 'aria-labelledby': 'lv-files-h', id: 'lv-files' },
      h('div', { className: 'lv-head' }, h('h2', { id: 'lv-files-h' }, 'Files'),
        h('label', { className: 'lv-btn lv-primary lv-file', 'aria-disabled': q?.full || undefined }, icon(h, 'upload', 16), 'Upload video',
          h('input', { type: 'file', accept: ACCEPT, disabled: q?.full || (!!L.up && !L.up.error), onChange: (e) => { L.upload(e.target.files?.[0]); e.target.value = ''; } }))),
      h('p', { className: 'lv-muted' }, 'Accepted: ' + LIMITS),
      L.files.error ? h('p', { className: 'ws-error', role: 'alert' }, L.files.error) : null,
      h('div', { className: 'lv-fgrid', 'data-preview': sel ? '' : undefined },
        L.files.items.length ? h('ul', { className: 'lv-flist' }, ...L.files.items.map((f) => {
          const video = f.media_type?.startsWith('video/'), room = modeOf(f) === 'room';
          return h('li', { key: f.id, 'aria-current': L.preview === f.id || undefined },
            h('div', { className: 'lv-frow' },
              h('button', { type: 'button', className: 'lv-fthumb', 'aria-label': 'Preview ' + f.name, onClick: () => L.setPreview(L.preview === f.id ? null : f.id) }, h(Thumb, { f, kind: room ? 'room' : 'experiment' })),
              h('span', { className: 'lv-fname' }, h('strong', { title: f.name }, f.name),
                h('small', { className: 'lv-muted' }, fmtBytes(f.size) + (f.duration_s != null ? ', ' + Number(f.duration_s).toFixed(1) + ' s' : '') + (f.project_id ? '' : ', no project'))),
              video ? h('button', { type: 'button', className: 'lv-btn lv-sm', 'aria-expanded': room ? undefined : L.action?.file.id === f.id,
                onClick: () => (room ? L.buildRoom(f) : L.setAction(L.action?.file.id === f.id ? null : { file: f })) }, room ? 'Build my lab' : 'Measure') : null,
              h(Menu, { label: 'File actions for ' + f.name, items: [
                video ? { label: 'Preview', onClick: () => L.setPreview(f.id) } : null,
                video && room ? { label: 'Measure this experiment', onClick: () => L.setAction({ file: f }) } : null,
                video && !room ? { label: 'Build my lab', onClick: () => L.buildRoom(f) } : null,
                { label: 'Download', href: fileUrl(f), download: f.name },
                { label: 'Delete', danger: true, onClick: () => L.remove(f) }] })),
            L.action?.file.id === f.id ? h(MeasurePanel, { L, file: f }) : null);
        })) : h('div', { className: 'lv-empty-state' }, icon(h, 'film', 28), h('p', null, L.files.loaded ? 'No files yet. Upload a video or drop one on Home.' : 'Loading files.')),
        sel ? h('aside', { className: 'lv-fpreview', 'aria-label': 'Preview' },
          h('div', { className: 'lv-head' }, h('strong', { title: sel.name }, sel.name),
            h('button', { type: 'button', className: 'lv-iconbtn', 'aria-label': 'Close preview', onClick: () => L.setPreview(null) }, icon(h, 'close', 16))),
          sel.media_type?.startsWith('video/') ? h('video', { className: 'lv-video', controls: true, preload: 'metadata', src: fileUrl(sel) }) : h('img', { className: 'lv-video', src: fileUrl(sel), alt: sel.name }),
          h('small', { className: 'lv-muted' }, fmtBytes(sel.size) + (sel.duration_s != null ? ', ' + Number(sel.duration_s).toFixed(1) + ' s' : '') + '. RECORDED, scale unverified until measured.')) : null));
  }

  // Storage meter for the bottom of the left rail.
  function Meter({ L }) {
    const q = quotaView(L.files.quota);
    if (!q) return null;
    const qq = L.files.quota;
    return h('div', { className: 'lv-meter' },
      h('div', { className: 'lv-row lv-between' }, h('strong', null, 'Storage'), h('a', { href: '#files' }, 'Files')),
      h('progress', { max: 100, value: q.pct, 'aria-label': 'Storage used' }),
      h('small', null, fmtBytes(qq.storage_bytes_used) + ' of ' + fmtBytes(qq.storage_bytes_limit) + ' used'),
      qq.storage_bytes_public > 0 ? h('small', { className: 'lv-muted' }, 'Public samples not counted') : null,
      h('small', null, qq.uploads_remaining_today + ' of ' + qq.uploads_daily_limit + ' uploads left today'));
  }

  function Centre({ L }) {
    const [firstDone, setFirstDone] = useState(false);
    const [view, setView] = useState(() => (globalThis.location?.hash === '#files' ? 'files' : 'home'));
    useEffect(() => {
      const f = () => setView(globalThis.location?.hash === '#files' ? 'files' : 'home');
      f(); globalThis.addEventListener?.('hashchange', f);
      return () => globalThis.removeEventListener?.('hashchange', f);
    }, []);
    if (L.mode === undefined) return h('div', { className: 'lv-wrap' }, h('p', { className: 'lv-muted', role: 'status' }, 'Loading your settings.'));
    if (L.mode === null && !firstDone) return h('div', { className: 'lv-wrap' }, h(ModeScreen, { L, onDone: () => setFirstDone(true) }));
    const tracked = Object.values(L.tracked);
    return h('div', { className: 'lv-wrap', 'data-view': view },
      view === 'files' ? h(Files, { L }) : h(React.Fragment, null, h(Home, { L }), h(ProjectsGrid, { L }),
        tracked.length ? h('section', { className: 'lv-activity', 'aria-labelledby': 'lv-jobs-h', id: 'lv-activity' }, h('h2', { id: 'lv-jobs-h' }, 'Recent activity'),
          h('div', { className: 'lv-actgrid' }, ...tracked.reverse().map((j) => h(JobCard, { key: j.kind + j.id, L, kind: j.kind, id: j.id })))) : null),
      h(Progress, { L }));
  }

  return { useLive, Centre, Chat, Dot, Meter, ModelPicker };
};

