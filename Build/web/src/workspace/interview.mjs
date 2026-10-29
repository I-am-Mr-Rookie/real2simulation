// S15d: interview chips + free-text panel model. Pure: no DOM/React/network/model calls.
// Input is an S14a agent-response that the host already validated (contracts/agent/validate.py); parseQuestions re-checks only what the
// panel relies on and fails closed. Prompts/labels are rendered to plain strings; numbers come only from a referenced tool output.
// Own reducer (independent of the S15a phase graph, which stays in interview.active); output is interviewAnswers(), never a spec or a number.
const ID = /^[A-Za-z0-9][A-Za-z0-9_.-]{0,63}$/;
const KINDS = ['chips', 'free_text', 'chips_and_free_text'];
const LABELS = ['measured', 'simulated'];
export const MAX_TEXT = 500;
const obj = (v) => v !== null && typeof v === 'object' && !Array.isArray(v);
const closed = (o, keys) => obj(o) && Object.keys(o).length === keys.length && keys.every((k) => k in o);
const fin = (v) => typeof v === 'number' && Number.isFinite(v);
const hasChips = (q) => q.kind !== 'free_text';
const hasText = (q) => q.kind !== 'chips';

// Mirrors Build/agent/tools.render: value ± uncertainty unit (label).
const numberText = (q) => `${Number(q.value.toPrecision(6))} ± ${Number(q.uncertainty.toPrecision(2))} ${q.unit} (${q.source.label})`;

function segmentsText(segs, outs, where, errs) {
  if (!Array.isArray(segs) || segs.length < 1 || segs.length > 64) { errs.push(where + ': 1-64 segments required'); return ''; }
  return segs.map((s, i) => {
    if (closed(s, ['type', 'text']) && s.type === 'text') {
      if (typeof s.text !== 'string' || !s.text || s.text.length > 600) errs.push(`${where}[${i}]: bad text`);
      else if (/\p{N}/u.test(s.text)) errs.push(`${where}[${i}]: untraced numeric character`);
      else return s.text;
    } else if (closed(s, ['type', 'ref']) && s.type === 'number' && closed(s.ref, ['tool_output_id', 'quantity'])) {
      const q = outs.find((o) => o?.id === s.ref.tool_output_id)?.quantities?.[s.ref.quantity];
      if (q && fin(q.value) && fin(q.uncertainty) && typeof q.unit === 'string' && LABELS.includes(q.source?.label)) return numberText(q);
      errs.push(`${where}[${i}]: number ref does not resolve to a labelled quantity`);
    } else errs.push(`${where}[${i}]: unknown segment`);
    return '';
  }).join('');
}

export function parseQuestions(response, { sceneId, toolOutputs = [] } = {}) {
  const errs = [];
  const r = response;
  if (!obj(r) || r.schema_version !== 'agent-response/1.0.0' || r.scene_id !== sceneId || !Array.isArray(r.questions) || r.questions.length > 3)
    return { ok: false, errors: ['response: not an agent-response/1.0.0 for this scene with at most 3 questions'] };
  const seen = new Set();
  const questions = r.questions.map((q, i) => {
    const where = `questions[${i}]`;
    if (!closed(q, ['id', 'kind', 'prompt', 'chips']) || !ID.test(q.id) || !KINDS.includes(q.kind) || !Array.isArray(q.chips) || q.chips.length > 6 ||
        (q.kind === 'free_text') !== (q.chips.length === 0) || seen.has(q.id)) { errs.push(where + ': malformed question'); return null; }
    seen.add(q.id);
    const ids = new Set();
    const chips = q.chips.map((c, j) => {
      if (!closed(c, ['id', 'label']) || !ID.test(c.id) || ids.has(c.id)) { errs.push(`${where}.chips[${j}]: malformed chip`); return null; }
      ids.add(c.id);
      return { id: c.id, label: segmentsText(c.label, toolOutputs, `${where}.chips[${j}].label`, errs) };
    });
    return { id: q.id, kind: q.kind, prompt: segmentsText(q.prompt, toolOutputs, where + '.prompt', errs), chips };
  });
  return errs.length ? { ok: false, errors: errs } : { ok: true, questions };
}

export const initialInterview = () => ({ status: 'idle', questions: [], index: 0, selected: null, text: '', answers: [], error: null });
const cur = (s) => (s.status === 'asking' ? s.questions[s.index] : null);
const reject = (s, message) => ({ ...s, error: { code: 'INVALID_INPUT', message: String(message).slice(0, 240) } });
export const canSubmit = (s) => { const q = cur(s); return !!q && (s.selected !== null || (hasText(q) && s.text.trim() !== '')); };

// Illegal events return the same state object (as the S15a reducer). Rejected payloads keep the position and set state.error.
export function reduceInterview(s, e) {
  const q = cur(s);
  switch (e?.type) {
    case 'Q_LOADED': { // a new round only before the first or after a finished one: the agent cannot swap a question mid-answer
      if (s.status === 'asking') return s;
      const p = parseQuestions(e.response, { sceneId: e.sceneId, toolOutputs: e.toolOutputs });
      if (!p.ok) return reject(s, p.errors.join('; '));
      return { ...s, status: p.questions.length ? 'asking' : 'complete', questions: p.questions, index: 0, selected: null, text: '', error: null };
    }
    case 'Q_CHIP': {
      if (!q || !hasChips(q) || !q.chips.some((c) => c.id === e.chipId)) return s;
      return { ...s, selected: s.selected === e.chipId ? null : e.chipId, error: null };
    }
    case 'Q_TEXT':
      if (!q || !hasText(q) || typeof e.text !== 'string') return s;
      return { ...s, text: e.text.replace(/[\u0000-\u0008\u000B-\u001F\u007F]/g, '').slice(0, MAX_TEXT), error: null };
    case 'Q_SUBMIT': {
      if (!q) return s;
      if (!canSubmit(s)) return reject(s, hasChips(q) && !hasText(q) ? 'Choose an option to continue.' : hasText(q) && !hasChips(q) ? 'Write an answer to continue.' : 'Choose an option or write an answer to continue.');
      const chip = q.chips.find((c) => c.id === s.selected);
      const answer = { questionId: q.id, prompt: q.prompt, chipId: chip?.id ?? null, chipLabel: chip?.label ?? null, text: s.text.trim() || null };
      const index = s.index + 1;
      return { ...s, answers: [...s.answers, answer], index, status: index === s.questions.length ? 'complete' : 'asking', selected: null, text: '', error: null };
    }
    case 'Q_BACK': { // reopen the previous question of this round with its answer restored
      if ((s.status !== 'asking' && s.status !== 'complete') || s.index === 0) return s;
      const last = s.answers[s.answers.length - 1];
      return { ...s, status: 'asking', index: s.index - 1, answers: s.answers.slice(0, -1), selected: last.chipId, text: last.text ?? '', error: null };
    }
    case 'Q_RESET': return initialInterview();
    default: return s;
  }
}

// What the host forwards (to the agent / experiment-template step): ids and the user's own text only.
export const interviewAnswers = (s) => (s.status === 'complete' ? s.answers.map(({ questionId, chipId, text }) => ({ questionId, chipId, text })) : null);

export function interviewView(s) {
  const q = cur(s);
  return {
    status: s.status,
    progress: q ? `Question ${s.index + 1} of ${s.questions.length}` : s.status === 'complete' ? 'All questions answered.' : 'No questions yet.',
    prompt: q?.prompt ?? null,
    chips: q && hasChips(q) ? q.chips.map((c) => ({ ...c, selected: c.id === s.selected })) : [],
    freeText: q && hasText(q) ? { value: s.text, maxLength: MAX_TEXT } : null,
    canSubmit: canSubmit(s),
    canBack: s.index > 0 && (s.status === 'asking' || s.status === 'complete'),
    last: !!q && s.index === s.questions.length - 1,
    answers: s.answers.map((a) => ({ prompt: a.prompt, answer: [a.chipLabel, a.text].filter(Boolean).join(' — ') })),
    error: s.error,
  };
}
