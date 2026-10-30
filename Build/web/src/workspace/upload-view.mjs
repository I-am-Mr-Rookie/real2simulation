// S15n: upload control. Native labelled file input (keyboard reachable, screen-reader named); approval rule stated up front.
export const ACCEPT = 'video/mp4,video/quicktime,video/webm';
const pct = (u) => (u?.total ? Math.round((100 * u.committed) / u.total) : 0);

// snapshot = controller.snapshot(); pure view-model, no DOM.
export function uploadView(snapshot) {
  const { state, busy = false, upload = null } = snapshot;
  const show = ['upload.idle', 'upload.failed', 'upload.cancelled'].includes(state.phase);
  const status = busy ? (upload ? 'Uploading ' + upload.name + ': ' + pct(upload) + '%' : 'Preparing upload')
    : upload?.approvedClip ? 'Approved clip ' + upload.approvedClip + ' accepted' : 'No file uploaded yet.';
  return { show, disabled: busy, upload, percent: pct(upload), status, error: show && state.error ? state.error : null };
}

export function renderUpload(h, v, onFile) {
  if (!v.show) return null;
  const off = v.disabled || !onFile;
  return h('section', { className: 'ws-upload', 'aria-label': 'Upload a clip' },
    h('label', { className: 'ws-field', htmlFor: 'ws-upload-file' }, 'Video clip (MP4, MOV or WebM)',
      h('input', { id: 'ws-upload-file', type: 'file', accept: ACCEPT, disabled: off, 'aria-describedby': 'ws-upload-hint ws-upload-status',
        onChange: (e) => { const file = e.target.files?.[0]; if (file) onFile(file); } }),
      h('span', { id: 'ws-upload-hint', className: 'ws-hint' }, 'Only approved licensed clips listed in clips.csv are accepted; other files are rejected by checksum.')),
    v.upload && v.disabled ? h('progress', { className: 'ws-meter', max: 100, value: v.percent, 'aria-label': 'Upload progress' }) : null,
    h('p', { id: 'ws-upload-status', className: 'ws-progress', role: 'status', 'aria-live': 'polite' }, v.status),
    v.error ? h('p', { className: 'ws-error', role: 'alert' }, v.error.code + ': ' + v.error.message) : null);
}
