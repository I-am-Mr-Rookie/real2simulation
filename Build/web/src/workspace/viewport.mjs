// S15b: viewport mount controller. Talks to the viewer ONLY through its public adapter interface
// (adapter.mount(host, request, { loadScene, signal, onState, onError }) -> { dispose }); adapter/loadScene are injected.
// One mount per distinct (scene, mode, audience) key; a change aborts and disposes the previous mount first.
export function createViewport({ adapter, loadScene, onStatus }) {
  let key = null, ctl = null, handle = null, gen = 0;
  const stop = () => { ctl?.abort(); handle?.dispose(); ctl = handle = null; };
  return {
    sync(host, request, nextKey) {
      if (nextKey === key) return;
      stop(); key = nextKey; const mine = ++gen;
      if (!request) return onStatus({ status: 'empty', error: null });
      ctl = new AbortController();
      const { signal } = ctl;
      const live = () => mine === gen && !signal.aborted; // no callbacks after replace/destroy/abort
      let status = 'loading', reported = false;
      onStatus({ status, error: null });
      adapter.mount(host, request, {
        loadScene, signal,
        onState: (s) => { if (live()) { status = s; onStatus({ status, error: null }); } },
        onError: (e) => { if (live()) { reported = true; onStatus({ status, error: { code: e?.code ?? 'UNKNOWN', message: String(e?.message ?? '').slice(0, 240) } }); } },
      }).then(
        (h) => { if (live()) handle = h; else h?.dispose(); }, // late mount of a replaced scene is cleaned up
        () => { if (live() && !reported) onStatus({ status: 'error', error: { code: 'RENDER_FAILED', message: 'Viewport failed to start' } }); },
      );
    },
    destroy() { stop(); key = null; gen++; },
  };
}
