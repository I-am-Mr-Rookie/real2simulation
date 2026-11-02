import test from 'node:test';
import assert from 'node:assert/strict';
import { createUseVoice } from '../../Build/web/src/workspace/voice.mjs';

test('shared voice path records WAV, fills text without sending an agent turn, and releases the microphone', async () => {
  const original = Object.getOwnPropertyDescriptor(globalThis, 'navigator');
  const saved = Object.fromEntries(['MediaRecorder', 'AudioContext', 'OfflineAudioContext', 'fetch'].map((k) => [k, globalThis[k]]));
  const cells = []; let index = 0, cleanup, stopped = 0, words, sent;
  const hooks = {
    useState(v) { const i = index++; if (!(i in cells)) cells[i] = v; return [cells[i], (x) => { cells[i] = x; }]; },
    useRef(v) { const i = index++; return cells[i] ??= { current: v }; },
    useEffect(f) { cleanup ??= f(); },
  };
  const useVoice = createUseVoice(hooks), render = () => { index = 0; return useVoice((t) => { words = t; }); };
  try {
    Object.defineProperty(globalThis, 'navigator', { configurable: true, value: { mediaDevices: { getUserMedia: async () => ({ getTracks: () => [{ stop() { stopped++; } }] }) } } });
    globalThis.MediaRecorder = class {
      state = 'inactive';
      start() { this.state = 'recording'; }
      stop() { this.state = 'inactive'; this.ondataavailable({ data: new Blob(['test']) }); this.done = this.onstop(); }
    };
    globalThis.AudioContext = class { async decodeAudioData() { return { duration: .01 }; } close() {} };
    globalThis.OfflineAudioContext = class {
      destination = {};
      createBufferSource() { return { connect() {}, start() {} }; }
      async startRendering() { return { getChannelData: () => new Float32Array(160) }; }
    };
    globalThis.fetch = async (url, init) => { sent = { url, init }; return Response.json({ text: 'Drop a ball' }); };
    await render().toggleVoice();
    assert.equal(render().voice.state, 'recording');
    await render().toggleVoice();
    await new Promise((r) => setTimeout(r, 20));
    assert.equal(words, 'Drop a ball'); assert.equal(stopped, 1);
    assert.equal(sent.url, '/api/workspace/agent/transcribe');
    assert.equal(sent.init.headers['content-type'], 'audio/wav');
    assert.equal(new TextDecoder().decode(sent.init.body.slice(0, 4)), 'RIFF');
    assert.equal(render().voice.state, 'idle');
    globalThis.navigator.mediaDevices.getUserMedia = async () => { throw new Error('denied'); };
    await render().toggleVoice();
    assert.match(render().voice.error, /permission denied/);
    cleanup();
  } finally {
    cleanup?.(); Object.assign(globalThis, saved);
    if (original) Object.defineProperty(globalThis, 'navigator', original); else delete globalThis.navigator;
  }
});
