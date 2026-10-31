// S15e: template controls markup. One labelled text input per parameter with its unit always visible; text only. Reports T_* events
// through onAction (host runs reduceTemplate, sends validationRequest to the validator, dispatches T_VERDICT, then INTERVIEW_SPEC with
// acceptedSpec). In run.ready the spec is already accepted: read-only values plus an Edit button (EDIT_SPEC discards run and fit).
export function renderTemplate(h, v, phase, onAction) {
  const send = (a) => onAction?.(a);
  if (v.status === 'empty') return null;
  const locked = phase === 'run.ready';
  return h('form', { className: 'ws-template', 'data-status': v.status, 'aria-label': 'Experiment setup', onSubmit: (e) => { e?.preventDefault?.(); send({ type: 'T_SUBMIT' }); } },
    h('fieldset', { disabled: !onAction || locked || v.status === 'checking' },
      h('legend', null, 'Experiment setup: ' + v.template.replace('_', ' ')),
      ...v.fields.map((f) => h('label', { key: f.param, className: 'ws-field' }, f.label + ' (' + f.unit + ')',
        h('input', { type: 'text', inputMode: 'decimal', value: f.text, maxLength: 64, 'aria-invalid': !!f.error, 'aria-describedby': 'hint-' + f.param + (f.error ? ' err-' + f.param : ''),
          onChange: (e) => send({ type: 'T_EDIT', param: f.param, text: e.target.value }) }),
        h('span', { id: 'hint-' + f.param, className: 'ws-hint' }, f.hint),
        f.error ? h('span', { id: 'err-' + f.param, className: 'ws-error', role: 'alert' }, f.error) : null))),
    v.errors.length ? h('ul', { className: 'ws-error', role: 'alert' }, ...v.errors.map((m, i) => h('li', { key: i }, m))) : null,
    h('p', { className: 'ws-progress', role: 'status', 'aria-live': 'polite' }, v.status === 'checking' ? 'Checking setup...' : v.status === 'accepted' ? 'Setup accepted.' : ''),
    v.accepted.length ? h('ul', { className: 'ws-accepted', 'aria-label': 'Accepted values' }, ...v.accepted.map((m, i) => h('li', { key: i }, m))) : null,
    locked ? h('button', { type: 'button', className: 'ws-back', disabled: !onAction, onClick: () => send({ type: 'EDIT_SPEC' }) }, 'Edit setup')
      : h('button', { type: 'submit', className: 'ws-submit', disabled: !onAction || !v.canSubmit }, 'Check setup'));
}
