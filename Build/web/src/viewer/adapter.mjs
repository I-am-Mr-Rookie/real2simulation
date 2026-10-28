// Viewer adapter implementing the S04a contract (Build/web/src/shell/README.md -> Viewer adapter).
// Framework-free. Renderer (canvas/GPU) is injected; S09b supplies the real one.
import { ViewerError, abortError } from './common.mjs';
import { buildSceneModel } from './scene-model.mjs';

export { ViewerError } from './common.mjs';

const ID = /^[a-zA-Z0-9][a-zA-Z0-9_-]{0,95}$/;
const exactKeys = (o, keys) => o && typeof o === 'object' && !Array.isArray(o) &&
  Object.keys(o).length === keys.length && keys.every((k) => Object.hasOwn(o, k));

/** Mirrors integration.schema.json $defs.viewer (contract 1.0.0). Returns an error string or null. */
export function checkViewerRequest(r) {
  if (!exactKeys(r, ['contract_version', 'kind', 'audience', 'scene', 'mode'])) return 'viewer request fields invalid';
  if (r.contract_version !== '1.0.0') return 'unsupported contract version';
  if (r.kind !== 'viewer') return 'not a viewer request';
  if (!['guest', 'signed-in'].includes(r.audience)) return 'invalid audience';
  if (!['inspect', 'lab', 'mystery'].includes(r.mode)) return 'invalid mode';
  const s = r.scene;
  if (!exactKeys(s, ['scene_id', 'scene_version', 'access', 'evidence'])) return 'scene reference fields invalid';
  if (typeof s.scene_id !== 'string' || !ID.test(s.scene_id)) return 'invalid scene id';
  if (s.scene_version !== '1.0.0') return 'unsupported scene version';
  if (!['public-library', 'private'].includes(s.access)) return 'invalid access';
  if (!['synthetic', 'reconstructed'].includes(s.evidence)) return 'invalid evidence label';
  if (r.audience === 'guest' && s.access !== 'public-library') return 'guest may only view public-library scenes';
  return null;
}

/**
 * @param {{ createRenderer(host: unknown, model: object, signal: AbortSignal): Promise<{dispose(): void}> | {dispose(): void} }} deps
 */
export function createViewerAdapter({ createRenderer }) {
  if (typeof createRenderer !== 'function') throw new TypeError('createRenderer is required');
  return Object.freeze({
    async mount(host, request, { loadScene, signal, onState, onError }) {
      let live = true; // false after failure/dispose: no callbacks afterwards
      const emit = (state) => { if (live && !signal.aborted) onState(state); };
      const fail = (state, err) => {
        if (live && !signal.aborted) { onState(state); onError({ code: err.code, message: err.message }); }
        live = false;
        throw err;
      };
      const guard = () => { if (signal.aborted) { live = false; throw abortError(); } };

      guard();
      const why = checkViewerRequest(request);
      if (why) fail('error', new ViewerError('INVALID_REQUEST', why));
      if (request.mode === 'mystery') {
        fail('unavailable', new ViewerError('UNAVAILABLE', 'Mystery mode needs the S10 redacted payload, which does not exist yet'));
      }
      emit('loading');

      let bundle, model, renderer;
      try { bundle = await loadScene(request.scene, signal); } catch (e) {
        // Viewer-authored codes from the S09c artifact loader pass through; anything else is LOAD_FAILED.
        guard();
        const pass = e instanceof ViewerError && ['LOAD_FAILED', 'INVALID_ARTIFACT', 'UNSUPPORTED'].includes(e.code);
        fail('error', pass ? e : new ViewerError('LOAD_FAILED', 'Scene could not be loaded'));
      }
      guard();
      try { model = await buildSceneModel(bundle, request.scene); } catch (e) {
        guard(); fail('error', e instanceof ViewerError ? e : new ViewerError('INVALID_ARTIFACT', 'Scene artifact is invalid'));
      }
      guard();
      try { renderer = await createRenderer(host, model, signal); } catch {
        guard(); fail('error', new ViewerError('RENDER_FAILED', 'Renderer could not start'));
      }
      if (!renderer || typeof renderer.dispose !== 'function') fail('error', new ViewerError('RENDER_FAILED', 'Renderer returned no disposer'));

      let disposed = false;
      const dispose = () => {
        if (disposed) return;
        disposed = true; live = false;
        signal.removeEventListener('abort', dispose);
        try { renderer.dispose(); } catch { /* disposal must not throw into the shell */ }
      };
      if (signal.aborted) { dispose(); throw abortError(); } // partial renderer cleaned up
      signal.addEventListener('abort', dispose, { once: true });
      emit('ready');
      return Object.freeze({ dispose });
    },
  });
}
