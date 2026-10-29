// Browser wiring for install guidance (S19c). Takes a window-like object so tests can fake it.
import { getInstallGuidance, orientationAdvice } from './install-guidance.mjs';

export function createInstallStore(win) {
  const nav = win.navigator || {};
  const listeners = new Set();
  let deferred = null;
  let installed = false;

  const isStandalone = () =>
    nav.standalone === true || !!win.matchMedia?.('(display-mode: standalone)').matches; // navigator.standalone is iOS-only

  const snapshot = () => ({
    guidance: getInstallGuidance({
      userAgent: nav.userAgent, platform: nav.platform, maxTouchPoints: nav.maxTouchPoints,
      standalone: installed || isStandalone(), canPrompt: !!deferred
    }),
    orientation: orientationAdvice({ width: win.innerWidth, height: win.innerHeight })
  });
  let current = snapshot();
  const emit = () => { current = snapshot(); listeners.forEach((l) => l()); };

  const onPrompt = (e) => { e.preventDefault(); deferred = e; emit(); };
  const onInstalled = () => { installed = true; deferred = null; emit(); };
  win.addEventListener('beforeinstallprompt', onPrompt);
  win.addEventListener('appinstalled', onInstalled);
  win.addEventListener('resize', emit);
  win.addEventListener('orientationchange', emit);

  return {
    getSnapshot: () => current, // stable reference between emits (useSyncExternalStore contract)
    subscribe(l) { listeners.add(l); return () => listeners.delete(l); },
    // The saved event is single-use; always drop it afterwards.
    async promptInstall() {
      if (!deferred) return 'unavailable';
      const e = deferred;
      deferred = null;
      try {
        await e.prompt();
        const { outcome } = await e.userChoice;
        return outcome;
      } finally { emit(); }
    },
    dispose() {
      win.removeEventListener('beforeinstallprompt', onPrompt);
      win.removeEventListener('appinstalled', onInstalled);
      win.removeEventListener('resize', emit);
      win.removeEventListener('orientationchange', emit);
      listeners.clear();
    }
  };
}
