import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, readdirSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { getInstallGuidance, detectPlatform, orientationAdvice, ORIENTATION_POLICY, SOURCES } from '../../Build/web/src/pwa/install-guidance.mjs';
import { createInstallStore } from '../../Build/web/src/pwa/install-client.mjs';

const UA = {
  iosSafari: 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1',
  iosChrome: 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/124.0.0.0 Mobile/15E148 Safari/604.1',
  ipadDesktopUa: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15',
  androidChrome: 'Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
  androidSamsung: 'Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/24.0 Chrome/117.0.0.0 Mobile Safari/537.36',
  androidFirefox: 'Mozilla/5.0 (Android 14; Mobile; rv:125.0) Gecko/125.0 Firefox/125.0',
  winChrome: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
};
const g = (userAgent, extra = {}) => getInstallGuidance({ userAgent, ...extra });
const text = (x) => [x.headline, ...x.steps, ...x.notes].join(' ');

test('platform detection incl. iPadOS desktop-class UA', () => {
  assert.equal(detectPlatform({ userAgent: UA.iosSafari }), 'ios');
  assert.equal(detectPlatform({ userAgent: UA.ipadDesktopUa, platform: 'MacIntel', maxTouchPoints: 5 }), 'ios');
  assert.equal(detectPlatform({ userAgent: UA.ipadDesktopUa, platform: 'MacIntel', maxTouchPoints: 0 }), 'desktop');
  assert.equal(detectPlatform({ userAgent: UA.androidChrome }), 'android');
  assert.equal(detectPlatform({ userAgent: UA.winChrome }), 'desktop');
});

test('iOS: manual Add to Home Screen, never an Install button, even if a prompt were claimed', () => {
  const s = g(UA.iosSafari);
  assert.equal(s.state, 'manual');
  assert.match(s.steps.join(' '), /Share/);
  assert.match(s.steps.join(' '), /Add to Home Screen/);
  assert.match(text(s), /Edit Actions/);
  assert.equal(g(UA.iosSafari, { canPrompt: true }).state, 'prompt'); // only if the page really got the event
  const c = g(UA.iosChrome);
  assert.equal(c.browser, 'chrome');
  assert.match(c.notes.join(' '), /16\.4/);
  assert.ok(c.sources.includes('webkitIos164'));
  assert.equal(g(UA.ipadDesktopUa, { platform: 'MacIntel', maxTouchPoints: 5 }).os, 'ios');
});

test('Android: menu install, https caveat; prompt button only with a captured event', () => {
  const s = g(UA.androidChrome);
  assert.equal(s.state, 'manual');
  assert.match(text(s), /Install app/);
  assert.match(text(s), /https/);
  assert.equal(g(UA.androidChrome, { canPrompt: true }).state, 'prompt');
  assert.equal(g(UA.androidSamsung).browser, 'samsung');
  const f = g(UA.androidFirefox);
  assert.equal(f.browser, 'firefox');
  assert.doesNotMatch(text(f), /three dots/); // no browser-specific UI we cannot verify
});

test('installed standalone shows nothing to do; desktop is hedged', () => {
  const s = g(UA.androidChrome, { standalone: true });
  assert.equal(s.state, 'installed');
  assert.deepEqual(s.steps, []);
  assert.match(text(g(UA.winChrome)), /may not offer/);
});

test('every guidance states install is optional and not offline, and cites known sources', () => {
  for (const ua of Object.values(UA)) {
    const s = g(ua, { platform: 'MacIntel' });
    assert.match(text(s), /optional/);
    assert.match(text(s), /does not make simulations or videos available offline/);
    for (const k of s.sources) assert.ok(SOURCES[k], k);
  }
});

test('orientation: advice only, no lock claim anywhere', () => {
  assert.deepEqual(ORIENTATION_POLICY, { manifestOrientation: null, apiLock: false });
  assert.equal(orientationAdvice({ width: 375, height: 700 }).orientation, 'portrait');
  assert.match(orientationAdvice({ width: 375, height: 700 }).hint, /does not lock orientation/);
  assert.equal(orientationAdvice({ width: 700, height: 375 }).hint, null);
  assert.equal(orientationAdvice({ width: 900, height: 1200 }).hint, null);
  const dir = fileURLToPath(new URL('../../Build/web/src/pwa/', import.meta.url));
  for (const f of readdirSync(dir).filter((n) => /\.(mjs|jsx|js)$/.test(n) && n !== 'sw.js')) {
    const src = readFileSync(dir + f, 'utf8');
    assert.doesNotMatch(src, /orientation\s*\.\s*lock\s*\(/, f); // no ScreenOrientation.lock() call
  }
  const manifest = JSON.parse(readFileSync(fileURLToPath(new URL('../../Build/web/public/pwa/manifest.webmanifest', import.meta.url)), 'utf8'));
  assert.ok(!('orientation' in manifest));
  for (const ua of Object.values(UA)) assert.doesNotMatch(text(g(ua)) , /(locked|will lock|lock(s)? (the )?(screen|orientation))/i);
});

function fakeWindow({ ua = UA.androidChrome, standalone = false, w = 375, h = 700 } = {}) {
  const win = new EventTarget();
  Object.assign(win, { navigator: { userAgent: ua, platform: '', maxTouchPoints: 5 }, innerWidth: w, innerHeight: h,
    matchMedia: (q) => ({ matches: standalone && q.includes('standalone') }) });
  return win;
}
const evt = (type, extra = {}) => Object.assign(new Event(type, { cancelable: true }), extra);

test('store: captures beforeinstallprompt once, prompts, then drops it', async () => {
  const win = fakeWindow();
  const store = createInstallStore(win);
  assert.equal(store.getSnapshot().guidance.state, 'manual');
  assert.equal(await store.promptInstall(), 'unavailable');
  let prompted = 0;
  const e = evt('beforeinstallprompt', { prompt: async () => { prompted++; }, userChoice: Promise.resolve({ outcome: 'dismissed' }) });
  win.dispatchEvent(e);
  assert.equal(e.defaultPrevented, true);
  assert.equal(store.getSnapshot().guidance.state, 'prompt');
  assert.equal(store.getSnapshot(), store.getSnapshot()); // stable reference
  assert.equal(await store.promptInstall(), 'dismissed');
  assert.equal(prompted, 1);
  assert.equal(store.getSnapshot().guidance.state, 'manual');
  assert.equal(await store.promptInstall(), 'unavailable');
  store.dispose();
});

test('store: appinstalled, standalone, resize and unsubscribe', () => {
  const win = fakeWindow();
  const store = createInstallStore(win);
  let n = 0;
  const off = store.subscribe(() => n++);
  win.innerWidth = 700; win.innerHeight = 375;
  win.dispatchEvent(new Event('resize'));
  assert.equal(store.getSnapshot().orientation.orientation, 'landscape');
  win.dispatchEvent(new Event('appinstalled'));
  assert.equal(store.getSnapshot().guidance.state, 'installed');
  assert.equal(n, 2);
  off();
  win.dispatchEvent(new Event('resize'));
  assert.equal(n, 2);
  store.dispose();
  assert.equal(createInstallStore(fakeWindow({ standalone: true })).getSnapshot().guidance.state, 'installed');
  const ios = fakeWindow({ ua: UA.iosSafari });
  ios.navigator.standalone = true;
  assert.equal(createInstallStore(ios).getSnapshot().guidance.state, 'installed');
});
