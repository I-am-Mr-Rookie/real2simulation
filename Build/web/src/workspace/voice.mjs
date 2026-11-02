import { toWav16k, VOICE_MAX_S } from './live.mjs';

// Shared by the workspace prompt and the editor drawer. Transcription fills text, never sends a turn.
export const createUseVoice = ({ useState, useRef, useEffect }) => function useVoice(onText) {
  const [voice, setVoice] = useState({ state: 'idle', error: null });
  const rec = useRef(null), text = useRef(onText), alive = useRef(true);
  text.current = onText;
  useEffect(() => { alive.current = true; return () => { alive.current = false; if (rec.current?.state === 'recording') rec.current.stop(); }; }, []);
  const update = (v) => { if (alive.current) setVoice(v); };
  const toggleVoice = async () => {
    if (rec.current) { if (rec.current.state === 'recording') rec.current.stop(); return; }
    if (voice.state !== 'idle') return;
    update({ state: 'requesting', error: null });
    let stream, limit;
    try {
      stream = await globalThis.navigator.mediaDevices.getUserMedia({ audio: true });
      if (!alive.current) { stream.getTracks().forEach((t) => t.stop()); return; }
      const mr = new MediaRecorder(stream), parts = [];
      limit = setTimeout(() => mr.state === 'recording' && mr.stop(), VOICE_MAX_S * 1000);
      mr.ondataavailable = (e) => e.data.size && parts.push(e.data);
      mr.onstop = async () => {
        clearTimeout(limit); stream.getTracks().forEach((t) => t.stop()); rec.current = null;
        if (!alive.current) return;
        update({ state: 'working', error: null });
        try {
          const wav = await toWav16k(await new Blob(parts).arrayBuffer());
          if (!alive.current) return;
          const r = await fetch('/api/workspace/agent/transcribe', { method: 'POST', headers: { 'content-type': 'audio/wav' }, body: wav });
          const body = await r.json().catch(() => ({}));
          if (!r.ok) throw new Error(body?.detail?.message ?? body?.error?.message ?? 'Transcription failed.');
          if (alive.current && body.text) text.current(body.text);
          update({ state: 'idle', error: body.text ? null : 'No speech heard.' });
        } catch (e) { update({ state: 'idle', error: e.message || 'Could not convert the recording.' }); }
      };
      rec.current = mr; mr.start(); update({ state: 'recording', error: null });
    } catch {
      clearTimeout(limit);
      stream?.getTracks().forEach((t) => t.stop()); rec.current = null;
      update({ state: 'idle', error: 'Microphone not available or permission denied.' });
    }
  };
  return { voice, toggleVoice };
};
