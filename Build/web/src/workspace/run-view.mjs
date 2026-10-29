// S15f: run controls markup (pure; h = React.createElement-compatible, text only). Buttons report { type } through onAction; the host
// supplies the seed for RUN_START (like the S15c retry button) and runs prepareRun / verifyReplay.
export function renderRun(h, v, onAction) {
  if (!v.show) return null;
  const send = (a) => onAction?.(a), off = !onAction;
  const btn = (cls, label, type) => h('button', { key: type, type: 'button', className: cls, disabled: off, onClick: () => send({ type }) }, label);
  return h('section', { className: 'ws-run', 'data-phase': v.phase, 'aria-label': 'Run controls' },
    h('p', { className: 'ws-progress', role: 'status', 'aria-live': 'polite' }, v.status),
    h('div', { className: 'ws-actions' },
      v.canRun ? btn('ws-submit', v.runLabel, 'RUN_START') : null,
      v.canPause ? btn('ws-back', 'Pause', 'RUN_PAUSE') : null,
      v.canResume ? btn('ws-submit', 'Resume', 'RUN_RESUME') : null,
      v.canCancel ? btn('ws-back', 'Cancel run', 'RUN_CANCEL') : null,
      v.canReplay ? btn('ws-back', 'Replay with same seed', 'R_REPLAY_START') : null),
    v.progress ? h('progress', { className: 'ws-meter', max: v.progress.total, value: v.progress.frame, 'aria-label': 'Playback position' }) : null,
    v.progress ? h('p', { className: 'ws-hint' }, 'Frame ' + v.progress.frame + ' of ' + v.progress.total + (v.frame ? ': t = ' + v.frame.time_s + ' s, position = ' + v.frame.position_m + ' m' : '')) : null,
    v.seed !== null ? h('p', { className: 'ws-hint' }, 'Seed ' + v.seed + ' (' + v.label + (v.traceHash ? '; trace ' + v.traceHash + ', replay ' + v.replayHash : '') + ')') : null,
    v.replay ? h('p', { className: 'ws-progress', role: v.replay.status === 'mismatch' ? 'alert' : 'status', 'data-status': v.replay.status }, v.replay.text) : null);
}
