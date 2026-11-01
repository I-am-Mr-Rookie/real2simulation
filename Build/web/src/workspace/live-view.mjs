// N09: live product workspace (agent mode screen, new project, files, agent chat + voice, GPU dot, job views).
// React is injected like workspace/react.mjs. Every number shown comes from an API response (quota, sizes, queue) or the browser upload progress.
import { API_BASE } from './controller.mjs';
import { AGENT_MODES, UPLOAD_QUESTION, LIMITS, TIPS, projectTitle, fmtBytes, quotaView, gpuDot, GPU_POLL_MS, shouldPoll, jobsState,
  historyOf, questionAnswer, recommendedIndex, readAgentMode, writeAgentMode, toWav16k, VOICE_MAX_S } from './live.mjs';
import { chartGeom, fmtPm, SIZE_UNITS, naturalPoint, experimentBody, jobView, POLL_MS, jobsFromToolCalls, shareable } from './measure.mjs';

const ACCEPT = 'video/mp4,video/quicktime,video/webm,.mp4,.mov,.webm';
const TRACK_KEY = 'r2s.tracked.jobs';
async function call(path, init = {}) {
  const res = await fetch(API_BASE + path, { credentials: 'same-origin', cache: 'no-store', ...init });
  const body = await res.json().catch(() => null);
  return { status: res.status, ok: res.ok, body };
}
const errText = (r, fallback) => r?.body?.error?.message || r?.body?.detail?.error?.message || fallback + ' (' + (r?.status ?? 'network') + ').';

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

export const createLive = (React) => {
  const { createElement: h, useState, useEffect, useRef, useCallback } = React;

  function useLive(enabled, openAgent) {
    const [mode, setModeState] = useState(undefined); // undefined = not read yet (SSR), null = first run
    const [files, setFiles] = useState({ items: [], quota: null, error: null, loaded: false });
    const [up, setUp] = useState(null);
    const [project, setProject] = useState(null);
    const [msgs, setMsgs] = useState([]);
    const [busy, setBusy] = useState(false);
    const [draft, setDraft] = useState('');
    const [gpu, setGpu] = useState({ tone: 'unknown', label: 'Checking GPU', detail: '' });
    const [jobs, setJobs] = useState(null);
    const [voice, setVoice] = useState({ state: 'idle', error: null });
    const [preview, setPreview] = useState(null);
    const [tracked, setTracked] = useState({}); // N22: kind:id -> jobView, polled until terminal
    const [action, setAction] = useState(null); // { kind: 'measure', file } panel on a file
    const rec = useRef(null);
    const msgsRef = useRef(msgs); msgsRef.current = msgs;
    const trackedRef = useRef(tracked); trackedRef.current = tracked;
    const push = (m) => setMsgs((list) => [...list, { id: Date.now() + Math.random(), ...m }]);

    useEffect(() => { setModeState(readAgentMode(globalThis.localStorage)); }, []);
    const setMode = (m) => { writeAgentMode(globalThis.localStorage, m); setModeState(m); };

    const loadFiles = useCallback(async () => {
      try { const r = await call('/files'); setFiles(r.ok ? { items: r.body?.files ?? [], quota: r.body?.quota ?? null, error: null, loaded: true } : (f) => ({ ...f, error: errText(r, 'Could not load files'), loaded: true })); }
      catch { setFiles((f) => ({ ...f, error: 'Could not load files (network).', loaded: true })); }
    }, []);
    const loadJobs = useCallback(async () => {
      const one = async (path, key) => { try { const r = await call(path); return jobsState(r.status, r.body, key); } catch { return jobsState(0, null, key); } };
      const [experiments, rooms] = await Promise.all([one('/experiments', 'experiments'), one('/rooms', 'rooms')]);
      setJobs({ experiments, rooms });
    }, []);
    useEffect(() => { if (enabled) { loadFiles(); loadJobs(); } }, [enabled, loadFiles, loadJobs]);

    // GPU dot: poll every 10 s only while the tab is visible; refresh at once when it becomes visible again.
    useEffect(() => {
      if (!enabled) return undefined;
      const doc = globalThis.document;
      const poll = async () => { if (!shouldPoll(doc)) return; try { const r = await call('/gpu/status'); setGpu(gpuDot(r.ok ? r.body : null)); } catch { setGpu(gpuDot(null)); } };
      poll();
      const t = setInterval(poll, GPU_POLL_MS);
      doc?.addEventListener?.('visibilitychange', poll);
      return () => { clearInterval(t); doc?.removeEventListener?.('visibilitychange', poll); };
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
          body: JSON.stringify({ text: t, contributor: mode === 'contributor', history }) });
        if (r.ok) {
          const jobs = jobsFromToolCalls(r.body?.tool_calls);
          jobs.forEach((j) => track(j.kind, j.id));
          push({ role: 'assistant', text: r.body?.reply || '', question: r.body?.question ?? null, model: r.body?.model, jobs });
        } else push({ role: 'error', text: errText(r, 'The agent did not answer') });
      } catch { push({ role: 'error', text: 'The agent did not answer (network).' }); }
      finally { setBusy(false); }
    };

    const newProject = () => { setProject(null); push({ role: 'assistant', text: UPLOAD_QUESTION.question, question: UPLOAD_QUESTION, local: true }); openAgent?.(); };

    const answer = async (msg, picked, other) => {
      setMsgs((list) => list.map((m) => (m.id === msg.id ? { ...m, answered: questionAnswer(msg.question, picked, other) } : m)));
      if (!msg.local) return send(questionAnswer(msg.question, picked, other));
      const opt = UPLOAD_QUESTION.options[picked] ?? UPLOAD_QUESTION.options[0];
      push({ role: 'user', text: opt.label });
      const r = await call('/projects', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ mode: opt.mode, title: projectTitle(opt.mode) }) }).catch(() => null);
      if (r?.ok) { setProject(r.body.project); push({ role: 'assistant', text: 'Filming tips for ' + opt.label.toLowerCase() + ':', tips: TIPS[opt.mode] }); }
      else push({ role: 'error', text: errText(r, 'Could not create the project') });
      if (other?.trim()) send(other);
    };

    const upload = async (file) => {
      if (!file) return;
      setUp({ name: file.name, pct: 0, error: null });
      const r = await uploadXhr(file, project?.id, (pct) => setUp((u) => (u ? { ...u, pct } : u)));
      setUp(r.ok ? null : { name: file.name, pct: 0, error: errText(r, 'Upload failed') });
      if (r.ok && r.body?.quota) setFiles((f) => ({ ...f, quota: r.body.quota }));
      loadFiles();
    };
    const remove = async (f) => {
      if (!globalThis.confirm?.('Delete ' + f.name + '? This cannot be undone.')) return;
      const r = await call('/files/' + encodeURIComponent(f.id), { method: 'DELETE' }).catch(() => null);
      if (!r?.ok) setFiles((s) => ({ ...s, error: errText(r, 'Delete failed') }));
      if (preview === f.id) setPreview(null);
      loadFiles();
    };

    const toggleVoice = async () => {
      if (voice.state === 'recording') { rec.current?.stop(); return; }
      if (voice.state !== 'idle') return;
      try {
        const stream = await globalThis.navigator.mediaDevices.getUserMedia({ audio: true });
        const mr = new MediaRecorder(stream), parts = [];
        const limit = setTimeout(() => mr.state === 'recording' && mr.stop(), VOICE_MAX_S * 1000);
        mr.ondataavailable = (e) => e.data.size && parts.push(e.data);
        mr.onstop = async () => {
          clearTimeout(limit); stream.getTracks().forEach((t) => t.stop());
          setVoice({ state: 'working', error: null });
          try {
            const wav = await toWav16k(await new Blob(parts).arrayBuffer());
            const r = await call('/agent/transcribe', { method: 'POST', headers: { 'content-type': 'audio/wav' }, body: wav });
            if (r.ok && r.body?.text) { setDraft((d) => (d ? d + ' ' : '') + r.body.text); setVoice({ state: 'idle', error: null }); }
            else setVoice({ state: 'idle', error: r.ok ? 'No speech heard.' : errText(r, 'Transcription failed') });
          } catch { setVoice({ state: 'idle', error: 'Could not convert the recording.' }); }
        };
        rec.current = mr; mr.start(); setVoice({ state: 'recording', error: null });
      } catch { setVoice({ state: 'idle', error: 'Microphone not available or permission denied.' }); }
    };

    return { mode, setMode, files, up, upload, remove, preview, setPreview, project, newProject, msgs, busy, draft, setDraft, send, answer,
      gpu, jobs, loadJobs, voice, toggleVoice, tracked, track, action, setAction, measure, buildRoom, share };
  }

  function ModeScreen({ L, settings = false, onDone }) {
    const [pick, setPick] = useState(L.mode ?? 'standard');
    return h('section', { className: 'lv-card lv-modes', 'aria-labelledby': 'lv-modes-h', 'data-slot': settings ? 'agent-settings' : 'first-run' },
      h('h2', { id: 'lv-modes-h' }, settings ? 'Agent mode' : 'Choose how the agent runs'),
      settings ? null : h('p', { className: 'lv-muted' }, 'You can change this later in the agent panel. Standard is the default.'),
      h('div', { className: 'lv-modegrid', role: 'radiogroup', 'aria-label': 'Agent mode' }, ...AGENT_MODES.map((m) =>
        h('label', { key: m.id, className: 'lv-mode', 'data-on': pick === m.id },
          h('input', { type: 'radio', name: 'lv-mode' + (settings ? '-s' : ''), value: m.id, checked: pick === m.id, onChange: () => setPick(m.id) }),
          h('span', { className: 'lv-mode-h' }, h('strong', null, m.title), m.id === 'standard' ? h('span', { className: 'lv-tag' }, 'Default') : null),
          h('span', { className: 'lv-muted' }, m.model),
          h('ul', { className: 'lv-pros', 'aria-label': 'Pros' }, ...m.pros.map((p) => h('li', { key: p }, p))),
          h('ul', { className: 'lv-cons', 'aria-label': 'Cons' }, ...m.cons.map((p) => h('li', { key: p }, p)))))),
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
          L.mode === 'contributor' ? 'Contributor mode' : 'Standard mode')),
      settings ? h(ModeScreen, { L, settings: true, onDone: () => setSettings(false) }) : null,
      h('ol', { className: 'lv-msgs', 'aria-live': 'polite', 'aria-label': 'Conversation' },
        L.msgs.length ? null : h('li', { className: 'lv-muted lv-empty' }, 'Ask about a physics experiment, or start a new project. Physics questions only.'),
        ...L.msgs.map((m) => h('li', { key: m.id, className: 'lv-msg', 'data-role': m.role },
          m.question ? h(QuestionCard, { msg: m, onAnswer: L.answer }) : h('p', { role: m.role === 'error' ? 'alert' : undefined }, m.text),
          ...(m.jobs ?? []).map((j) => h(JobCard, { key: j.kind + j.id, L, kind: j.kind, id: j.id })),
          m.tips ? h('ul', { className: 'lv-tips' }, ...m.tips.map((t) => h('li', { key: t }, t))) : null)),
        L.busy ? h('li', { className: 'lv-msg lv-muted', 'data-role': 'assistant' }, h('span', { className: 'r2s-pulse', 'aria-hidden': true }), ' Thinking') : null,
        h('li', { ref: end, 'aria-hidden': true })),
      h('form', { className: 'lv-compose', onSubmit: (e) => { e.preventDefault(); L.send(L.draft); } },
        h('label', { className: 'r2s-sr', htmlFor: 'lv-draft' }, 'Message the agent'),
        h('textarea', { id: 'lv-draft', rows: 2, maxLength: 4000, value: L.draft, placeholder: 'Message the agent', onChange: (e) => L.setDraft(e.target.value),
          onKeyDown: (e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); L.send(L.draft); } } }),
        h('div', { className: 'lv-row' },
          h('button', { type: 'button', className: 'lv-btn', 'data-voice': vs, 'aria-pressed': vs === 'recording', disabled: vs === 'working', onClick: L.toggleVoice,
            title: 'Voice input, up to 60 s' }, vs === 'recording' ? 'Stop recording' : vs === 'working' ? 'Transcribing' : 'Voice'),
          h('button', { type: 'submit', className: 'lv-btn lv-primary', disabled: L.busy || !L.draft.trim() }, 'Send')),
        L.voice.error ? h('p', { className: 'ws-error', role: 'alert' }, L.voice.error) : null));
  }

  function Dot({ L }) {
    const d = L.gpu;
    return h('span', { className: 'lv-gpu', 'data-tone': d.tone, role: 'status', title: d.detail ? d.label + '. ' + d.detail : d.label },
      h('span', { className: 'lv-dot', 'aria-hidden': true }), h('span', { className: 'lv-gpu-text' }, d.label, d.detail ? h('small', null, ' ' + d.detail) : null));
  }

  const JOB_TITLES = { experiments: 'Experiments', rooms: 'Rooms' };
  function Jobs({ L }) {
    if (!L.jobs) return h('p', { className: 'lv-muted' }, 'Checking job services.');
    return h('div', { className: 'lv-jobs' }, ...Object.entries(L.jobs).map(([k, j]) => h('div', { key: k, className: 'lv-job', 'data-state': j.state },
      h('h4', null, JOB_TITLES[k]),
      j.state === 'unavailable' ? h('p', { className: 'lv-muted' }, 'No saved list on this server yet. Jobs you start here show above.')
        : j.state === 'error' ? h('p', { className: 'ws-error', role: 'alert' }, j.message)
        : j.items.length ? h('ul', null, ...j.items.slice(0, 20).map((it, i) => h('li', { key: it.id ?? i },
          h('span', null, it.title || it.name || it.id || 'Job'), ' ', h('span', { className: 'lv-tag' }, String(it.status ?? it.state ?? 'unknown')),
          k === 'experiments' && it.id && !L.tracked['experiment:' + it.id] ? h('button', { type: 'button', className: 'lv-btn lv-sm', onClick: () => L.track('experiment', it.id) }, 'Open') : null,
          Number.isFinite(it.progress) ? h('progress', { max: 1, value: it.progress, 'aria-label': 'Progress' }) : null)))
        : h('p', { className: 'lv-muted' }, 'No jobs yet.'))),
      h('button', { type: 'button', className: 'lv-btn', onClick: L.loadJobs }, 'Refresh'));
  }

  // N22 Mode B: first frame still (a paused <video> seeked to 0, no server call), click the object or type its name, optional known size.
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
    return h('figure', { className: 'lv-chart' },
      h('svg', { viewBox: '0 0 ' + g.W + ' ' + g.H, role: 'img', 'aria-label': 'Tracked ' + g.axis + ' position over time with the fitted curve and its 1 sigma band' },
        g.band ? h('path', { d: g.band, className: 'lv-band' }) : null, g.curve ? h('path', { d: g.curve, className: 'lv-curve' }) : null,
        ...g.points.map((p, i) => h('circle', { key: i, cx: p.cx, cy: p.cy, r: 2.6, className: 'lv-pt' })),
        h('text', { x: g.pad, y: g.H - 8 }, g.ticks.t0 + ' s'), h('text', { x: g.W - g.pad, y: g.H - 8, textAnchor: 'end' }, g.ticks.t1 + ' s'),
        h('text', { x: 4, y: 14 }, g.axis + ' (' + g.unit + ') max ' + g.ticks.vmax), h('text', { x: g.W / 2, y: g.H - 8, textAnchor: 'middle' }, 'min ' + g.ticks.vmin)),
      h('figcaption', { className: 'lv-muted' }, 'Dots: MEASURED track, ' + g.points.length + ' frames. Line: fitted curve. Band: 1 sigma of the fit.'));
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
    const q = result?.quantity;
    const measured = /MEASURED/.test(q?.label ?? result?.label ?? '');
    return h('div', { className: 'lv-result' },
      q ? h('p', { className: 'lv-qty' }, h('span', { className: 'lv-muted lv-block' }, q.name), h('strong', null, fmtPm(q.value, q.uncertainty) + ' ' + q.unit), h('small', { className: 'lv-muted' }, ' 1 sigma'))
        : h('p', null, 'No value reported. ' + (result?.label || '')),
      h('div', { className: 'lv-row' }, h('span', { className: 'lv-tag', 'data-tone': measured ? 'ok' : 'warn' }, measured ? 'MEASURED' : 'scale unverified'),
        h('span', { className: 'lv-tag', 'data-tone': 'warn' }, 'playback clock'), result?.motion ? h('span', { className: 'lv-tag' }, String(result.motion).replace(/_/g, ' ')) : null),
      h('ul', { className: 'lv-labels lv-muted' }, ...[q?.label ?? result?.label, result?.clock, result?.track?.label].filter(Boolean).map((t) => h('li', { key: t }, t))),
      h(Chart, { result }),
      h('div', { className: 'lv-row' }, h('a', { className: 'lv-btn lv-primary', href: '/lab?editor=1&experiment=' + encodeURIComponent(id) }, '3D replay, redo with changes')),
      shareable(result) ? h(Share, { L, id }) : h('p', { className: 'lv-muted' }, 'Guess the Gravity needs a known size, so the value is in m/s^2.'));
  }

  // One progress card for both modes, used in Processing and in the agent chat.
  function JobCard({ L, kind, id }) {
    const j = L.tracked[kind + ':' + id] ?? { state: 'queued', step: 'Queued' };
    const g = j.gpu ? gpuDot(j.gpu) : L.gpu;
    return h('div', { className: 'lv-jobcard', 'data-state': j.state },
      h('div', { className: 'lv-row lv-between' }, h('strong', null, kind === 'experiment' ? 'Measurement' : 'Room lab'), h('span', { className: 'lv-tag', role: 'status' }, j.step)),
      !j.terminal ? h(React.Fragment, null, h('progress', { 'aria-label': j.step }),
        h('p', { className: 'lv-muted' }, (kind === 'experiment' ? 'Hosted model, no GPU wait. Backup ' : '') + g.label + (g.detail ? '. ' + g.detail : '') + '.')) : null,
      j.error ? h('p', { className: 'ws-error', role: 'alert' }, j.error) : null,
      j.poll ? h('p', { className: 'lv-muted' }, j.poll) : null,
      j.state === 'done' && kind === 'experiment' ? h(Result, { L, id, result: j.result }) : null,
      j.state === 'done' && kind === 'room' ? h('div', { className: 'lv-row' }, h('a', { className: 'lv-btn lv-primary', href: '/lab?editor=1&room=' + encodeURIComponent(id) }, 'Open my lab'),
        ...(j.labels ?? []).map((t) => h('span', { key: t, className: 'lv-tag', 'data-tone': /unverified/.test(t) ? 'warn' : undefined }, t))) : null);
  }

  function Centre({ L }) {
    const [firstDone, setFirstDone] = useState(false);
    const q = quotaView(L.files.quota);
    if (L.mode === null && !firstDone) return h('div', { className: 'lv-wrap' }, h(ModeScreen, { L, onDone: () => setFirstDone(true) }));
    return h('div', { className: 'lv-wrap' },
      h('section', { className: 'lv-card', 'aria-labelledby': 'lv-proj-h', id: 'lv-project' },
        h('div', { className: 'lv-row lv-between' }, h('h2', { id: 'lv-proj-h' }, L.project ? L.project.title : 'Projects'),
          h('button', { type: 'button', className: 'lv-btn lv-primary', onClick: L.newProject }, 'New project')),
        L.project ? h('div', null, h('p', { className: 'lv-muted' }, (L.project.mode === 'room' ? 'Room video: virtual lab' : 'My experiment: measurement') + '. Accepted: ' + LIMITS),
          h('ul', { className: 'lv-tips' }, ...TIPS[L.project.mode].map((t) => h('li', { key: t }, t))))
          : h('p', { className: 'lv-muted' }, 'Start a new project and the agent asks what you are uploading, then shows filming tips.')),
      h('section', { className: 'lv-card', 'aria-labelledby': 'lv-files-h', id: 'lv-files' },
        h('div', { className: 'lv-row lv-between' }, h('h2', { id: 'lv-files-h' }, 'Files'),
          h('label', { className: 'lv-btn lv-primary lv-file', 'aria-disabled': q?.full || undefined }, 'Upload video',
            h('input', { type: 'file', accept: ACCEPT, disabled: !!L.up && !L.up.error, onChange: (e) => { L.upload(e.target.files?.[0]); e.target.value = ''; } }))),
        q ? h('div', { className: 'lv-quota' }, h('progress', { max: 100, value: q.pct, 'aria-label': 'Storage used' }), h('p', { className: 'lv-muted' }, q.text)) : null,
        L.up ? h('div', { className: 'lv-up', role: 'status' }, L.up.error ? h('p', { className: 'ws-error', role: 'alert' }, L.up.name + ': ' + L.up.error)
          : h(React.Fragment, null, h('span', null, 'Uploading ' + L.up.name + ' ' + L.up.pct + '%'), h('progress', { max: 100, value: L.up.pct, 'aria-label': 'Upload progress' }))) : null,
        L.files.error ? h('p', { className: 'ws-error', role: 'alert' }, L.files.error) : null,
        L.files.items.length ? h('ul', { className: 'lv-files' }, ...L.files.items.map((f) => h('li', { key: f.id },
          h('div', { className: 'lv-row lv-between' },
            h('span', { className: 'lv-fname' }, h('strong', null, f.name), h('small', { className: 'lv-muted' }, ' ' + fmtBytes(f.size) + (f.duration_s != null ? ', ' + Number(f.duration_s).toFixed(1) + ' s' : '') + (f.project_id ? '' : ', no project'))),
            h('span', { className: 'lv-row' },
              f.media_type?.startsWith('video/') ? h('button', { type: 'button', className: 'lv-btn', 'aria-expanded': L.preview === f.id, onClick: () => L.setPreview(L.preview === f.id ? null : f.id) }, 'Preview') : null,
              f.media_type?.startsWith('video/') ? h('button', { type: 'button', className: 'lv-btn', 'aria-expanded': L.action?.file.id === f.id, onClick: () => L.setAction(L.action?.file.id === f.id ? null : { file: f }) }, 'Measure this experiment') : null,
              f.media_type?.startsWith('video/') ? h('button', { type: 'button', className: 'lv-btn', onClick: () => L.buildRoom(f) }, 'Build my lab') : null,
              h('a', { className: 'lv-btn', href: API_BASE + '/files/' + encodeURIComponent(f.id) + '/content', download: f.name }, 'Download'),
              h('button', { type: 'button', className: 'lv-btn lv-danger', onClick: () => L.remove(f) }, 'Delete'))),
          L.preview === f.id ? h('video', { className: 'lv-video', controls: true, preload: 'metadata', src: API_BASE + '/files/' + encodeURIComponent(f.id) + '/content' }) : null,
          L.action?.file.id === f.id ? h(MeasurePanel, { L, file: f }) : null)))
          : L.files.loaded ? h('p', { className: 'lv-muted' }, 'No files yet. Accepted: ' + LIMITS) : h('p', { className: 'lv-muted' }, 'Loading files.')),
      h('section', { className: 'lv-card', 'aria-labelledby': 'lv-jobs-h', id: 'lv-jobs' }, h('h2', { id: 'lv-jobs-h' }, 'Processing'),
        ...Object.values(L.tracked).reverse().map((j) => h(JobCard, { key: j.kind + j.id, L, kind: j.kind, id: j.id })), h(Jobs, { L })));
  }

  return { useLive, Centre, Chat, Dot };
};
