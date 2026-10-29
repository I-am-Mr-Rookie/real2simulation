// S15e: experiment template controls. Pure parser, reducer and view model; no DOM/React/network.
// Typed values are only candidates: a spec is accepted solely when the injected S08/S14c validator (answers_to_spec ->
// validate_setup, run server-side) returns it AND it still matches what the user typed. No default physical numbers.
// FIELDS mirrors Build/agent/interview.py QUESTIONS/UNITS; tests/workspace/template.test.mjs + evidence/S15/template_fixtures.py catch drift.
const ANGLE = { rad: 1, deg: Math.PI / 180, '°': Math.PI / 180 };
const f = (param, label, unit, units) => ({ param, label, unit, units });
export const FIELDS = {
  free_fall: [f('drop_height', 'Drop height', 'm', { '': 1, m: 1 }), f('initial_vertical_velocity', 'Initial upward speed', 'm/s', { '': 1, 'm/s': 1 })],
  projectile: [f('launch_height', 'Launch height', 'm', { '': 1, m: 1 }), f('horizontal_speed', 'Horizontal speed', 'm/s', { '': 1, 'm/s': 1 })],
  ramp: [f('incline_angle', 'Incline angle', 'rad', ANGLE), f('friction_coefficient', 'Friction coefficient', '1', { '': 1 }), f('initial_speed', 'Initial speed', 'm/s', { '': 1, 'm/s': 1 })],
  pendulum: [f('length', 'Length', 'm', { '': 1, m: 1 }), f('release_angle', 'Release angle', 'rad', ANGLE), f('initial_angular_velocity', 'Initial angular speed', 'rad/s', { '': 1, 'rad/s': 1 })],
};
const NUMBER = /^\s*([+-]?(?:[0-9]+\.?[0-9]*|\.[0-9]+)(?:[eE][+-]?[0-9]{1,3})?)\s*(\S*)\s*$/; // ASCII digits only, as interview.py
const unitHint = (fd) => {
  const named = Object.keys(fd.units).filter(Boolean);
  return named.length ? named.join(' or ') + (fd.units[''] ? ' (blank = ' + fd.unit + ')' : ' (unit required)') : 'unitless number';
};

// text -> value in the contract unit (same grammar and factors as interview.py _parse)
export function parseQuantity(text, fd) {
  const m = typeof text === 'string' && text.length <= 64 ? NUMBER.exec(text) : null;
  const factor = m ? fd.units[m[2].toLowerCase()] : undefined;
  const value = m && factor !== undefined ? Number(m[1]) * factor : NaN;
  return Number.isFinite(value) ? { ok: true, value } : { ok: false, message: 'Enter a number with unit ' + unitHint(fd) + '.' };
}

export const initialTemplate = () => ({ status: 'empty', template: null, texts: {}, fieldErrors: {}, errors: [], pending: null, spec: null });
const own = (o, k) => Object.prototype.hasOwnProperty.call(o, k);
const clean = (t) => String(t ?? '').replace(/[\u0000-\u001f\u007f]/g, '').slice(0, 64);
const near = (a, b) => Math.abs(a - b) <= 1e-9 * Math.max(1, Math.abs(a), Math.abs(b));

// An accepted spec must be the validator's output for exactly the typed values: right template, contract units, same numbers.
function specMatches(spec, template, pending) {
  const p = spec?.parameters;
  return spec?.template === template && p && typeof p === 'object' && FIELDS[template].every((fd) => {
    const q = p[fd.param];
    return q && q.unit === fd.unit && typeof q.value === 'number' && near(q.value, pending[fd.param]);
  });
}

// Events: T_LOAD {template, spec?} | T_EDIT {param,text} | T_SUBMIT | T_VERDICT {answers, result:{ok,spec?,errors?}} | T_RESET.
// Illegal events return the same state object.
export function reduceTemplate(s, e) {
  if (e?.type === 'T_RESET') return initialTemplate();
  if (e?.type === 'T_LOAD') {
    if (s.status === 'checking' || !own(FIELDS, e.template)) return s;
    const texts = {};
    for (const fd of FIELDS[e.template]) { const q = e.spec?.parameters?.[fd.param]; texts[fd.param] = q?.unit === fd.unit && Number.isFinite(q.value) ? String(q.value) : ''; }
    return { ...initialTemplate(), status: 'editing', template: e.template, texts };
  }
  if (s.status === 'empty') return s;
  if (e.type === 'T_EDIT') {
    if (s.status === 'checking' || !own(s.texts, e.param)) return s;
    return { ...s, status: 'editing', texts: { ...s.texts, [e.param]: clean(e.text) }, fieldErrors: {}, errors: [], spec: null };
  }
  if (e.type === 'T_SUBMIT') {
    if (s.status === 'checking') return s;
    const pending = {}, fieldErrors = {};
    for (const fd of FIELDS[s.template]) { const r = parseQuantity(s.texts[fd.param], fd); r.ok ? (pending[fd.param] = r.value) : (fieldErrors[fd.param] = r.message); }
    return Object.keys(fieldErrors).length ? { ...s, status: 'editing', fieldErrors, errors: [], spec: null } : { ...s, status: 'checking', fieldErrors: {}, errors: [], pending, spec: null };
  }
  if (e.type === 'T_VERDICT') {
    if (s.status !== 'checking') return s;
    const answers = Object.fromEntries(FIELDS[s.template].map((fd) => [fd.param, { text: s.texts[fd.param] }]));
    const sent = e.answers && typeof e.answers === 'object' ? e.answers : {};
    const same = Object.keys(sent).length === Object.keys(answers).length && Object.entries(answers).every(([k, a]) => sent[k]?.text === a.text);
    if (!same) return s; // verdict for stale input
    if (e.result?.ok === true && specMatches(e.result.spec, s.template, s.pending)) return { ...s, status: 'accepted', pending: null, spec: e.result.spec };
    const errs = e.result?.ok === true ? ['Validator returned a spec that does not match the typed values; not accepted.'] : (Array.isArray(e.result?.errors) && e.result.errors.length ? e.result.errors : ['Setup rejected.']);
    return { ...s, status: 'rejected', pending: null, errors: errs.slice(0, 5).map((x) => String(x).slice(0, 240)) };
  }
  return s;
}

// What the host sends to the validator on status 'checking' ({ template, answers } -> answers_to_spec).
export const validationRequest = (s) => s.status === 'checking'
  ? { template: s.template, answers: Object.fromEntries(FIELDS[s.template].map((fd) => [fd.param, { text: s.texts[fd.param] }])) } : null;
// The only spec the workspace may pass on (as INTERVIEW_SPEC); the S15a reducer re-validates it.
export const acceptedSpec = (s) => (s.status === 'accepted' ? s.spec : null);

export function templateView(s) {
  if (s.status === 'empty') return { status: 'empty', fields: [], errors: [], canSubmit: false, accepted: [] };
  return {
    status: s.status, template: s.template, errors: s.errors, canSubmit: s.status === 'editing' || s.status === 'rejected',
    fields: FIELDS[s.template].map((fd) => ({ param: fd.param, label: fd.label, unit: fd.unit, hint: unitHint(fd), text: s.texts[fd.param], error: s.fieldErrors[fd.param] ?? null })),
    accepted: s.status === 'accepted' ? FIELDS[s.template].map((fd) => fd.label + ': ' + s.spec.parameters[fd.param].value + ' ' + fd.unit) : [],
  };
}

