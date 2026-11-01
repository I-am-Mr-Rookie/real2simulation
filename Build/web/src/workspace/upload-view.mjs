// S15n: upload control. S15am: styled dropzone (B2 art + icon) wrapping the same native input #ws-upload-file (visually hidden, still focusable/labelled).
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
  const drop = (e) => { e.preventDefault(); const file = e.dataTransfer?.files?.[0]; if (file && !off) onFile(file); };
  return h('section', { className: 'ws-upload', 'aria-label': 'Upload a clip' },
    h('label', { className: 'ws-field ws-drop', htmlFor: 'ws-upload-file', 'data-disabled': off || undefined, onDragOver: (e) => e.preventDefault(), onDrop: drop },
      'Video clip (MP4, MOV or WebM)', // first child stays the label's plain-text name; art is moved above it with CSS order
      h('span', { className: 'ws-drop-art', 'aria-hidden': true }),
      h('span', { className: 'ws-drop-cta', 'aria-hidden': true }, 'Drop a clip or browse'),
      h('input', { id: 'ws-upload-file', type: 'file', accept: ACCEPT, disabled: off, 'aria-describedby': 'ws-upload-hint ws-upload-status',
        // S15bd: clear the input so re-picking the same file after an error fires change again
        onChange: (e) => { const file = e.target.files?.[0]; e.target.value = ''; if (file) onFile(file); } }),
      h('span', { id: 'ws-upload-hint', className: 'ws-hint' }, 'Only approved licensed clips listed in clips.csv are accepted; other files are rejected by checksum.')),
    v.upload && v.disabled ? h('progress', { className: 'ws-meter', max: 100, value: v.percent, 'aria-label': 'Upload progress' }) : null,
    h('p', { id: 'ws-upload-status', className: 'ws-progress', role: 'status', 'aria-live': 'polite' }, v.status),
    v.error ? h('p', { className: 'ws-error', role: 'alert' }, v.error.code + ': ' + v.error.message) : null);
}
