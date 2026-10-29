// S15g: virtual instrument controls. Readings are Build/instruments output (contracts/fit/quantity shape), injected through a
// service; this module writes no measurement numbers. A reading is accepted only if its quantities are closed-shape, finite, carry
// the contract unit, a non-negative uncertainty and source { label: 'simulated', evidence }. The signed instrument error is dropped:
// it is the distance to the hidden true value, so a trial view must never show it.
export const INSTRUMENTS = {
  stopwatch: { label: 'Stopwatch', rows: [['Elapsed time', null, 's']] },
  light_gate: { label: 'Light gate', rows: [['Gate time', null, 's']] },
  ruler: { label: 'Ruler', rows: [['Distance', null, 'm']] },
  camera: { label: 'Camera', rows: [['Frame time', 'time', 's'], ['Image x', 'x', 'px'], ['Image y', 'y', 'px']] },
};
const CLEARS = ['RUN_START', 'RUN_CANCEL', 'EDIT_SPEC', 'RESET'];
const SHOW = ['run.done', 'fit.running', 'fit.done', 'fit.failed', 'report.open'];
const leaks = (v) => v && typeof v === 'object' && Object.entries(v).some(([k, x]) => /gravity|hidden_?g|mystery/i.test(k) || leaks(x));
const isObj = (v) => v !== null && typeof v === 'object' && !Array.isArray(v);
const closed = (o, keys) => isObj(o) && Object.keys(o).every((k) => keys.includes(k));
const finite = (x) => typeof x === 'number' && Number.isFinite(x);
const short = (s) => String(s).slice(0, 160);

function parseQuantity(name, q, unit) {
  if (!closed(q, ['value', 'unit', 'uncertainty', 'error', 'source']) || !closed(q.source, ['label', 'evidence'])) throw new Error(name + ': malformed quantity');
  if (!finite(q.value) || !finite(q.uncertainty) || q.uncertainty < 0) throw new Error(name + ': value/uncertainty must be finite, uncertainty >= 0');
  if (q.unit !== unit) throw new Error(name + ': unit must be ' + unit);
  if (q.source.label !== 'simulated') throw new Error(name + ': source label must be simulated');
  if (typeof q.source.evidence !== 'string' || !q.source.evidence.trim()) throw new Error(name + ': source evidence missing');
  return { name, value: q.value, unit, uncertainty: q.uncertainty, label: 'simulated', evidence: q.source.evidence };
}

export function parseReading(id, reading) {
  const def = INSTRUMENTS[id];
  if (!def) throw new Error('unknown instrument');
  if (leaks(reading)) throw new Error('reading reveals hidden physics');
  const multi = def.rows[0][1] !== null;
  if (multi && (!isObj(reading) || !Number.isInteger(reading.frame_index) || reading.frame_index < 0)) throw new Error('camera reading needs frame_index');
  return { frame: multi ? reading.frame_index : null,
    rows: def.rows.map(([name, key, unit]) => parseQuantity(name, multi ? reading[key] : reading, unit)) };
}

export const initialInstruments = () => ({ selected: 'stopwatch', pending: null, trials: [], error: null });

// Unchanged state returns the SAME reference. Trials belong to a run: starting/cancelling/editing/reset clears them.
export function reduceInstruments(m, event, state) {
  const t = event?.type;
  if (CLEARS.includes(t)) return m.trials.length || m.pending || m.error ? { ...initialInstruments(), selected: m.selected } : m;
  if (t === 'I_SELECT') return INSTRUMENTS[event.instrument] && !m.pending && event.instrument !== m.selected ? { ...m, selected: event.instrument, error: null } : m;
  if (t === 'I_MEASURE') return state.phase === 'run.done' && !m.pending ? { ...m, pending: { instrument: m.selected }, error: null } : m;
  if (t === 'I_FAIL') return m.pending ? { ...m, pending: null, error: short(event.message) } : m;
  if (t === 'I_READING' && m.pending?.instrument === event.instrument) {
    try { const r = parseReading(event.instrument, event.reading);
      return { ...m, pending: null, trials: [...m.trials, { n: m.trials.length + 1, instrument: event.instrument, ...r }] };
    } catch (e) { return { ...m, pending: null, error: 'Reading rejected: ' + short(e.message) }; }
  }
  return m;
}

// Host: on I_MEASURE call this and dispatch the result. service(instrumentId, nthReadingOfThatInstrument) -> reading.
export async function measure(service, m) {
  const id = m.pending.instrument;
  try { return { type: 'I_READING', instrument: id, reading: await service(id, m.trials.filter((x) => x.instrument === id).length) }; }
  catch (e) { return { type: 'I_FAIL', message: short(e?.message ?? e) }; }
}

const num = (x) => String(Number(x.toPrecision(10))); // strips binary float noise only
export function instrumentView(state, m) {
  return {
    show: SHOW.includes(state.phase),
    instruments: Object.entries(INSTRUMENTS).map(([id, d]) => ({ id, label: d.label, selected: id === m.selected })),
    canSelect: !m.pending, canMeasure: state.phase === 'run.done' && !m.pending,
    status: m.pending ? 'Reading ' + INSTRUMENTS[m.pending.instrument].label + '...' : m.trials.length ? m.trials.length + ' trial reading(s) recorded.' : 'No readings yet.',
    error: m.error,
    notice: 'Readings are simulated instrument output. The plus-minus value is the instrument\u2019s reported standard uncertainty.',
    trials: m.trials.map((t) => ({ n: t.n, title: 'Trial ' + t.n + ': ' + INSTRUMENTS[t.instrument].label + (t.frame !== null ? ', frame ' + t.frame : ''),
      rows: t.rows.map((r) => ({ name: r.name, text: num(r.value) + ' \u00b1 ' + num(r.uncertainty) + ' ' + r.unit, label: r.label, evidence: short(r.evidence) })) })),
  };
}
