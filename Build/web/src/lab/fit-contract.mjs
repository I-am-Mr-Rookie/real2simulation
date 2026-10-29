const finite = (value) => typeof value === 'number' && Number.isFinite(value);

// Keep the reveal strict: this is the one trusted boundary for the known S11 response.
export function parseFitReveal(body, expectedSessionId) {
  const fit = body?.fit;
  const gravity = fit?.gravity;
  const source = gravity?.source;
  const uncertainty = fit?.uncertainty;
  if (body?.status !== 'ok' || body.sessionId !== expectedSessionId || fit?.status !== 'ok' || !gravity || !finite(gravity.value) ||
      !finite(gravity.uncertainty) || gravity.uncertainty < 0 || gravity.unit !== 'm/s^2' ||
      source?.label !== 'simulated' || typeof uncertainty?.model !== 'string' || !uncertainty.model.trim() ||
      !Array.isArray(uncertainty.assumptions) ||
      ('quantity_uncertainty' in uncertainty && uncertainty.quantity_uncertainty !== 'standard uncertainty (one sigma), not a 95% interval')) return null;
  for (let index = 0; index < uncertainty.assumptions.length; index += 1) {
    if (!Object.hasOwn(uncertainty.assumptions, index) || typeof uncertainty.assumptions[index] !== 'string') return null;
  }
  return { value: gravity.value, uncertainty: gravity.uncertainty, unit: gravity.unit,
    source: source.label, evidence: source.evidence, model: uncertainty.model,
    assumptions: uncertainty.assumptions };
}

export function sampleRows(observations) {
  const values = (Array.isArray(observations) ? observations : []).filter((row) =>
    finite(row?.time_s) && finite(row?.position_m));
  const step = Math.max(1, Math.ceil(values.length / 8));
  return values.filter((_, index) => index % step === 0 || index === values.length - 1).slice(0, 9);
}

export function plotPoints(observations, width = 592, height = 160) {
  const values = (Array.isArray(observations) ? observations : []).filter((row) =>
    finite(row?.time_s) && finite(row?.position_m));
  if (!values.length) return { points: '', time: null, position: null };
  const time = [Infinity, -Infinity], position = [Infinity, -Infinity];
  for (const row of values) {
    time[0] = Math.min(time[0], row.time_s); time[1] = Math.max(time[1], row.time_s);
    position[0] = Math.min(position[0], row.position_m); position[1] = Math.max(position[1], row.position_m);
  }
  const scale = (value, domain, size) => {
    if (domain[1] === domain[0]) return size / 2;
    const span = domain[1] - domain[0];
    // Halve only overflowing spans; ordinary and subnormal domains keep their original arithmetic.
    return (Number.isFinite(span) ? (value - domain[0]) / span
      : (value / 2 - domain[0] / 2) / (domain[1] / 2 - domain[0] / 2)) * size;
  };
  return { points: values.map((row) => `${24 + scale(row.time_s, time, width)},${190 - scale(row.position_m, position, height)}`).join(' '), time, position };
}
