// N89: guided student questions in the physics lab: predict, measure, change one thing, measure again, compare with uncertainty.
// Numbers come only from fitSimTrace (browser least squares on the SIMULATED sensor trace) and the scene itself.
const DT = 1 / 120; // engine step: the first-impact time is known to one step
const fmt = (v, s) => v.toFixed(4) + ' +/- ' + s.toPrecision(2);
const height = (o, floor = 0) => o.position[1] - o.size[1] / 2 - floor;

export const LESSONS = [
  { id: 'mass', question: 'Does a heavier ball fall faster?', object: 'ball-drop',
    choices: [['heavier', 'Heavier falls faster'], ['same', 'Both fall the same'], ['lighter', 'Lighter falls faster']],
    changeLabel: 'Make ball-drop 10 times heavier', change: (o) => ({ ...o, mass: +(o.mass * 10).toPrecision(3) }),
    run: (fit, o) => ({ value: fit.value, uncertainty: fit.uncertainty, mass: o.mass }), changed: (o, a) => o.mass !== a.mass,
    line: (r) => fmt(r.value, r.uncertainty) + ' m/s^2 at ' + r.mass + ' kg',
    verdict: (a, b) => {
      const diff = Math.abs(b.value) - Math.abs(a.value), sigma = Math.hypot(a.uncertainty || 0, b.uncertainty || 0);
      const same = Math.abs(diff) <= Math.max(2 * sigma, 1e-3 * Math.abs(a.value));
      return { outcome: same ? 'same' : (diff > 0) === (b.mass > a.mass) ? 'heavier' : 'lighter',
        text: same ? 'Both runs give the same acceleration within the uncertainty: mass did not change the fall.'
          : (diff > 0) === (b.mass > a.mass) ? 'The heavier run fell faster.' : 'The lighter run fell faster.' };
    },
    caveat: 'SIMULATED: this engine has no air drag, so mass cannot change the fall here. In real air a feather or a paper sheet falls slower; film two real drops and measure them in your workspace to test that.' },
  { id: 'height', question: 'Dropped from twice the height, does it take twice as long?', object: 'ball-drop',
    choices: [['double', 'Twice as long'], ['sqrt', 'About 1.4 times as long'], ['same', 'The same time']],
    changeLabel: 'Raise ball-drop to twice the height', change: (o) => ({ ...o, position: [o.position[0], +(2 * height(o) + o.size[1] / 2).toFixed(4), o.position[2]] }),
    run: (fit, o) => ({ time: fit.t1, height: +height(o).toFixed(4) }), changed: (o, a) => Math.abs(height(o) - a.height) > 1e-3,
    line: (r) => 'lands after ' + r.time.toFixed(3) + ' +/- ' + DT.toFixed(3) + ' s from ' + r.height + ' m',
    verdict: (a, b) => {
      const ratio = b.time / a.time, sigma = ratio * Math.hypot(DT / a.time, DT / b.time), k = b.height / a.height;
      const near = [['same', 1], ['sqrt', Math.sqrt(k)], ['double', k]].map(([id, v]) => [id, Math.abs(ratio - v)]).sort((x, y) => x[1] - y[1])[0][0];
      return { outcome: near, text: 'Run B took ' + ratio.toFixed(3) + ' +/- ' + sigma.toFixed(3) + ' times as long for ' + k.toFixed(2) + ' times the height. The square root of ' + k.toFixed(2) + ' is '
        + Math.sqrt(k).toFixed(3) + ': fall time grows with the square root of the height (t = sqrt(2h/g)), not in proportion.' };
    },
    caveat: 'SIMULATED, no air drag. Times are read at the first impact, to the nearest engine step (1/120 s).' },
];

// a, b: recorded runs; prediction: a choice id. Returns null until both runs exist.
export function lessonVerdict(lesson, a, b, prediction) {
  if (!a || !b) return null;
  const v = lesson.verdict(a, b);
  return { ...v, matched: prediction ? prediction === v.outcome : null };
}

export function lessonReport(lesson, pred, a, b, v) {
  const label = lesson.choices.find((c) => c[0] === pred)?.[1] ?? 'no prediction';
  return ['Question: ' + lesson.question, 'Prediction: ' + label, 'Run A: ' + lesson.line(a) + ' (SIMULATED)', 'Run B: ' + lesson.line(b) + ' (SIMULATED)',
    'Result: ' + v.text + (v.matched == null ? '' : v.matched ? ' The prediction matched.' : ' The prediction did not match.'), 'Note: ' + lesson.caveat].join('\n');
}
