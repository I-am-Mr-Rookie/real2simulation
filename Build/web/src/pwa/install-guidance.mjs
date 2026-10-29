// Install guidance + orientation advice (S19c). Pure functions: no DOM, no network.
// Every claim below is checked against MDN browser-compat-data 8.1.7 / Apple / web.dev; see README "Sources".
// Orientation: we never lock it (no manifest "orientation", no screen.orientation.lock call), see ORIENTATION_POLICY.

export const ORIENTATION_POLICY = Object.freeze({ manifestOrientation: null, apiLock: false });

// Short keys -> URLs cited in README.md.
export const SOURCES = Object.freeze({
  installCriteria: 'https://web.dev/articles/install-criteria',
  mdnInstallable: 'https://developer.mozilla.org/docs/Web/Progressive_web_apps/Guides/Making_PWAs_installable',
  mdnBeforeInstallPrompt: 'https://developer.mozilla.org/docs/Web/API/BeforeInstallPromptEvent',
  appleAddToHome: 'https://support.apple.com/guide/iphone/iph42ab2f3a7/ios',
  webkitIos164: 'https://webkit.org/blog/13878/web-push-for-web-apps-on-ios-and-ipados/',
  mdnOrientationLock: 'https://developer.mozilla.org/docs/Web/API/ScreenOrientation/lock',
  mdnManifestOrientation: 'https://developer.mozilla.org/docs/Web/Progressive_web_apps/Manifest/Reference/orientation'
});

// env = { userAgent, platform, maxTouchPoints } from navigator.
export function detectPlatform({ userAgent = '', platform = '', maxTouchPoints = 0 } = {}) {
  // iPadOS 13+ sends a Macintosh UA; touch points are the only tell.
  if (/iPhone|iPad|iPod/.test(userAgent) || (platform === 'MacIntel' && maxTouchPoints > 1)) return 'ios';
  if (/Android/.test(userAgent)) return 'android';
  return 'desktop';
}

export function detectBrowser(userAgent = '', os = detectPlatform({ userAgent })) {
  if (/SamsungBrowser/.test(userAgent)) return 'samsung';
  if (/Firefox|FxiOS/.test(userAgent)) return 'firefox';
  if (/EdgA|EdgiOS|Edg\//.test(userAgent)) return 'edge';
  if (/OPR|OPiOS|Opera/.test(userAgent)) return 'other';
  if (/CriOS/.test(userAgent)) return 'chrome';
  if (/Chrome\//.test(userAgent)) return 'chrome';
  if (/Safari/.test(userAgent) || os === 'ios') return 'safari';
  return 'other';
}

const ALWAYS = [
  'Installing is optional; the whole app also works in a normal browser tab.',
  'Installing does not make simulations or videos available offline.'
];

// state: installed | prompt | manual. steps are what the user does; notes are caveats.
export function getInstallGuidance({ userAgent = '', platform = '', maxTouchPoints = 0, standalone = false, canPrompt = false } = {}) {
  const os = detectPlatform({ userAgent, platform, maxTouchPoints });
  const browser = detectBrowser(userAgent, os);
  const out = (state, headline, steps, notes, sources) => ({ os, browser, state, headline, steps, notes: [...notes, ...ALWAYS], sources });

  if (standalone) return out('installed', 'Running as an installed app', [], [], []);

  // beforeinstallprompt exists only in Chromium-family browsers (never iOS); the page must wait for it.
  if (canPrompt) {
    return out('prompt', 'Install Real2Simulation', ['Press Install, then confirm in the browser dialog.'], [], ['mdnBeforeInstallPrompt']);
  }

  if (os === 'ios') {
    if (browser === 'safari') {
      return out('manual', 'Add to Home Screen (iPhone / iPad)', [
        'Tap the Share button.',
        'Choose Add to Home Screen.',
        'Tap Add.'
      ], ['iOS gives websites no install button or prompt, so this must be done by hand.', 'If Add to Home Screen is not in the list, scroll to the bottom, tap Edit Actions and add it.'], ['appleAddToHome']);
    }
    return out('manual', 'Add to Home Screen (iPhone / iPad)', [
      'Tap the Share button in this browser.',
      'Choose Add to Home Screen.',
      'Tap Add.'
    ], ['Browsers other than Safari can add to the Home Screen only on iOS / iPadOS 16.4 or later. If the option is missing, open this page in Safari.',
        'iOS gives websites no install button or prompt, so this must be done by hand.'], ['appleAddToHome', 'webkitIos164']);
  }

  if (os === 'android') {
    if (browser === 'firefox' || browser === 'other') {
      return out('manual', 'Install on Android', [
        'Open the browser menu.',
        'Look for Install or Add to Home screen.'
      ], ['Support and wording differ by browser. If neither entry exists, this browser is not offering install for the page; use Chrome or Samsung Internet instead.'], ['installCriteria']);
    }
    return out('manual', 'Install on Android', [
      'Open the browser menu (three dots).',
      'Choose Install app (some versions say Add to Home screen).',
      'Confirm.'
    ], ['If the entry is missing, the page may be on plain http or already installed. Install needs a secure (https) address.'], ['installCriteria', 'mdnInstallable']);
  }

  return out('manual', 'Install on desktop', [
    'In Chrome or Edge, use the install icon in the address bar, or the browser menu > Install.'
  ], ['Other desktop browsers may not offer install; use the app in a tab.'], ['mdnInstallable']);
}

// Advice only: never locks, never claims control of rotation.
export function orientationAdvice({ width, height } = {}) {
  const orientation = width > height ? 'landscape' : 'portrait';
  const narrowPortrait = orientation === 'portrait' && width < 600;
  return {
    orientation,
    hint: narrowPortrait
      ? 'Rotating your phone to landscape gives the workspace more room. The app does not lock orientation; rotation follows your device settings.'
      : null
  };
}
