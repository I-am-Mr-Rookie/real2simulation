const finite = (value) => typeof value === 'number' && Number.isFinite(value);

// Keep the reveal strict: this is the one trusted boundary for the known S11 response.
export function parseFitReveal(body, expectedSessionId) {
  if (body?.status !== 'ok') return null;
  const response = body.actualS11response;
  const fit = response?.fit;
  const gravity = fit?.gravity;
  const source = gravity?.source;
  const uncertainty = fit?.uncertainty;
  if (response?.sessionId !== expectedSessionId || !gravity || !finite(gravity.value) ||
      !finite(gravity.uncertainty) || gravity.uncertainty < 0 || typeof gravity.unit !== 'string' ||
      !gravity.unit.trim() || source?.label !== 'simulated' || typeof source.evidence !== 'string' ||
      !source.evidence.trim() || typeof uncertainty?.model !== 'string' || !uncertainty.model.trim() ||
      uncertainty.assumptions == null) return null;
  return { value: gravity.value, uncertainty: gravity.uncertainty, unit: gravity.unit,
    source: source.label, evidence: source.evidence, model: uncertainty.model,
    assumptions: uncertainty.assumptions };
}

export function plotPoints(observations, width = 592, height = 160) {
  const values = (Array.isArray(observations) ? observations : []).filter((row) =>
    finite(row?.time_s) && finite(row?.position_m));
  if (!values.length) return { points: '', time: null, position: null };
  const time = [Math.min(...values.map((row) => row.time_s)), Math.max(...values.map((row) => row.time_s))];
  const position = [Math.min(...values.map((row) => row.position_m)), Math.max(...values.map((row) => row.position_m))];
  const scale = (value, domain, size) => domain[1] === domain[0] ? size / 2 : ((value - domain[0]) / (domain[1] - domain[0])) * size;
  return { points: values.map((row) => `${24 + scale(row.time_s, time, width)},${190 - scale(row.position_m, position, height)}`).join(' '), time, position };
}
