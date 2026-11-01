// N09: live product workspace (agent mode screen, new project, files, agent chat + voice, GPU dot, job views).
// React is injected like workspace/react.mjs. Every number shown comes from an API response (quota, sizes, queue) or the browser upload progress.
import { API_BASE } from './controller.mjs';
import { AGENT_MODES, UPLOAD_QUESTION, LIMITS, TIPS, projectTitle, fmtBytes, quotaView, gpuDot, GPU_POLL_MS, shouldPoll, jobsState,
  historyOf, questionAnswer, recommendedIndex, readAgentMode, writeAgentMode, toWav16k, VOICE_MAX_S } from './live.mjs';

const ACCEPT = 'video/mp4,video/quicktime,video/webm,.mp4,.mov,.webm';
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
    const rec = useRef(null);
    const msgsRef = useRef(msgs); msgsRef.current = msgs;
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

    const send = async (text) => {
      const t = text.trim(); if (!t || busy) return;
      const history = historyOf(msgsRef.current);
      push({ role: 'user', text: t }); setDraft(''); setBusy(true);
      try {
        const r = await call('/agent/turn', { method: 'POST', headers: { 'content-type': 'application/json' },
          body: JSON.stringify({ text: t, contributor: mode === 'contributor', history }) });
        if (r.ok) push({ role: 'assistant', text: r.body?.reply || '', question: r.body?.question ?? null, model: r.body?.model });
        else push({ role: 'error', text: errText(r, 'The agent did not answer') });
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
      gpu, jobs, loadJobs, voice, toggleVoice };
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
      j.state === 'unavailable' ? h('p', { className: 'lv-muted' }, 'Not available yet: this processing service is not deployed on this server.')
        : j.state === 'error' ? h('p', { className: 'ws-error', role: 'alert' }, j.message)
        : j.items.length ? h('ul', null, ...j.items.slice(0, 20).map((it, i) => h('li', { key: it.id ?? i },
          h('span', null, it.title || it.name || it.id || 'Job'), ' ', h('span', { className: 'lv-tag' }, String(it.status ?? it.state ?? 'unknown')),
          Number.isFinite(it.progress) ? h('progress', { max: 1, value: it.progress, 'aria-label': 'Progress' }) : null)))
        : h('p', { className: 'lv-muted' }, 'No jobs yet.'))),
      h('button', { type: 'button', className: 'lv-btn', onClick: L.loadJobs }, 'Refresh'));
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
              h('a', { className: 'lv-btn', href: API_BASE + '/files/' + encodeURIComponent(f.id) + '/content', download: f.name }, 'Download'),
              h('button', { type: 'button', className: 'lv-btn lv-danger', onClick: () => L.remove(f) }, 'Delete'))),
          L.preview === f.id ? h('video', { className: 'lv-video', controls: true, preload: 'metadata', src: API_BASE + '/files/' + encodeURIComponent(f.id) + '/content' }) : null)))
          : L.files.loaded ? h('p', { className: 'lv-muted' }, 'No files yet. Accepted: ' + LIMITS) : h('p', { className: 'lv-muted' }, 'Loading files.')),
      h('section', { className: 'lv-card', 'aria-labelledby': 'lv-jobs-h', id: 'lv-jobs' }, h('h2', { id: 'lv-jobs-h' }, 'Processing'), h(Jobs, { L })));
  }

  return { useLive, Centre, Chat, Dot };
};
