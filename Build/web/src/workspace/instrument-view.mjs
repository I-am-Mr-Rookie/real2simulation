// S15g: instrument controls markup (pure; h = React.createElement-compatible, text only). Reports { type, ... } through onAction;
// the host feeds it to reduceInstruments and answers I_MEASURE with measure(service, m).
export function renderInstruments(h, v, onAction) {
  if (!v.show) return null;
  const send = (a) => onAction?.(a), off = !onAction;
  return h('section', { className: 'ws-instruments', 'aria-label': 'Virtual instruments' },
    h('div', { className: 'ws-chips', role: 'group', 'aria-label': 'Instrument' }, ...v.instruments.map((i) => h('button', { key: i.id, type: 'button', className: 'ws-chip',
      'aria-pressed': i.selected, disabled: off || !v.canSelect, onClick: () => send({ type: 'I_SELECT', instrument: i.id }) }, i.label))),
    h('div', { className: 'ws-actions' }, h('button', { type: 'button', className: 'ws-submit', disabled: off || !v.canMeasure, onClick: () => send({ type: 'I_MEASURE' }) }, 'Take reading')),
    h('p', { className: 'ws-progress', role: 'status', 'aria-live': 'polite' }, v.status),
    v.error ? h('p', { className: 'ws-error', role: 'alert' }, v.error) : null,
    v.trials.length ? h('ol', { className: 'ws-trials', 'aria-label': 'Trial readings' }, ...v.trials.map((t) => h('li', { key: t.n, className: 'ws-trial' },
      h('strong', null, t.title),
      h('ul', null, ...t.rows.map((r) => h('li', { key: r.name },
        h('span', { className: 'ws-qname' }, r.name + ': '), h('strong', { className: 'ws-qval' }, r.text), ' ',
        h('span', { className: 'ws-tag', 'data-label': r.label }, r.label), ' ',
        h('span', { className: 'ws-src' }, 'source: ' + r.evidence))))))) : null,
    h('p', { className: 'ws-hint' }, v.notice));
}
