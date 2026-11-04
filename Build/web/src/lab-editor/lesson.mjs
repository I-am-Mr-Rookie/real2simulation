// N89: one guided student question in the physics lab: predict, measure twice with one change, compare with uncertainty.
// Numbers come only from fitSimTrace (browser least squares on the SIMULATED sensor trace).
export const LESSON = {
  question: 'Does a heavier ball fall faster?',
  object: 'ball-drop',
  factor: 10,
  choices: [['heavier', 'Heavier falls faster'], ['same', 'Both fall the same'], ['lighter', 'Lighter falls faster']],
  caveat: 'SIMULATED: this engine has no air drag, so mass cannot change the fall here. In real air a feather or a paper sheet falls slower; film two real drops and measure them in your workspace to test that.',
};

// a, b: { value, uncertainty, mass } fits of run A (original mass) and run B (heavier). Same if within 2 sigma or 0.1 % (fit resolution floor).
export function lessonVerdict(a, b, prediction) {
  if (!a || !b || !Number.isFinite(a.value) || !Number.isFinite(b.value)) return null;
  const diff = Math.abs(b.value) - Math.abs(a.value), sigma = Math.hypot(a.uncertainty || 0, b.uncertainty || 0);
  const same = Math.abs(diff) <= Math.max(2 * sigma, 1e-3 * Math.abs(a.value));
  const outcome = same ? 'same' : (diff > 0) === (b.mass > a.mass) ? 'heavier' : 'lighter';
  return { diff, sigma, outcome, matched: prediction ? prediction === outcome : null,
    text: same ? 'Both runs give the same acceleration within the uncertainty: mass did not change the fall.'
      : (outcome === 'heavier' ? 'The heavier run fell faster' : 'The lighter run fell faster') + ', by ' + Math.abs(diff).toPrecision(2) + ' m/s^2.' };
}

export function lessonReport(pred, a, b, v) {
  const label = (id) => LESSON.choices.find((c) => c[0] === id)?.[1] ?? 'no prediction';
  return ['Question: ' + LESSON.question, 'Prediction: ' + label(pred),
    'Run A: ' + a.mass + ' kg, acceleration ' + a.value.toFixed(4) + ' +/- ' + a.uncertainty.toPrecision(2) + ' m/s^2 (SIMULATED)',
    'Run B: ' + b.mass + ' kg, acceleration ' + b.value.toFixed(4) + ' +/- ' + b.uncertainty.toPrecision(2) + ' m/s^2 (SIMULATED)',
    'Result: ' + v.text + (v.matched == null ? '' : v.matched ? ' The prediction matched.' : ' The prediction did not match.'), 'Note: ' + LESSON.caveat].join('\n');
}
