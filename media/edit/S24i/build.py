"""S24i demo-v1 build: trims/cleans VO takes, synth pad bed, cuts picture to voice, burns labels+captions.
Run from repo root: python media/edit/S24i/build.py  (writes media/edit/S24i/work/, demo-v1.mp4, preview-720p.mp4, demo-v1.srt, commands.log)
Source media is read from the canonical checkout (gitignored, private takes never leave media/)."""
import json, os, subprocess, sys
FF = r"C:/Users/HP/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-8.1.1-full_build/bin/"
SRC = os.environ.get("S24I_SRC", r"C:/Users/HP/Documents/Hackathon/2026-10-26 - Meta Global AI Developer Hackathon/media")
OUT = os.path.dirname(os.path.abspath(__file__)); W = os.path.join(OUT, "work"); os.makedirs(W, exist_ok=True)
LOG = open(os.path.join(OUT, "commands.log"), "w", encoding="utf-8")
FONT = "C\\:/Windows/Fonts/segoeui.ttf"

def ff(args, cwd=None):
    cmd = [FF + "ffmpeg.exe", "-hide_banner", "-y", "-loglevel", "error"] + args
    LOG.write(subprocess.list2cmdline(cmd).replace(SRC, "<media>").replace(OUT, "<S24i>") + "\n"); LOG.flush()
    subprocess.run(cmd, check=True, cwd=cwd)

def dur(p):
    return float(subprocess.run([FF + "ffprobe.exe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p], capture_output=True, text=True, check=True).stdout)

# beat: (label shown top, [(take, caption)], [(video, in_s, share)])
BEATS = [
 ("1", "Real video → measured track → simulation → honest error",
  [("b01-01", "Real2Simulation measures physics from real video."), ("b01-02", "And it tells you exactly what it could not measure.")],
  [("capture/S24c/beat1.webm", 2.0, 1)]),
 ("2", "SAM 3.1 · 439/439 frames tracked · Modal A10G",
  [("b02-01", "Meta's SAM 3.1 segments and tracks the object in every frame on a Modal GPU.")],
  [("capture/S24c/beat2.webm", 2.5, 1)]),
 ("3", "Metric scale: ABSTAINED (unverified)",
  [("b03-01", "MapAnything finds the floor."), ("b03-02", "When metric scale can't be sourced, the system abstains.")],
  [("capture/S24c/beat3.webm", 2.0, 1)]),
 ("4", "Image-space g fit: ±0.07367 relative (1σ, n=19) · precision, not accuracy",
  [("b04-01", "A deterministic fitter, not a language model, fits the fall and reports its uncertainty."),
   ("b04-02", "It's image-space only. The clip is probably slow motion, so this is not g in m/s².")],
  [("capture/S24c/beat4.webm", 2.0, 0.4), ("capture/S24c/beat4-fit.webm", 0.0, 0.6)]),
 ("5", "Gate RS: NOT_MET · diagnostic only · 7/466 frames scored",
  [("b05-01", "We seal a prediction before seeing the rest of the clip."),
   ("b05-02", "Today it misses. The full tracking job ran out of GPU memory, and the ballistic fit has no floor."),
   ("b05-03", "The apple lands. The prediction keeps falling.")],
  [("capture/S24c/beat5-predict.webm", 0.0, 0.6), ("capture/S24c/beat5.webm", 2.0, 0.4)]),
 ("5b", "OWN07 · SYSTEM-ESTIMATED · MEASURED (conditional)\nscale user-declared 20.28 cm · phone clock unverified · approximate, not calibrated",
  [("b05b-01", "The system finds release and impact in the phone clip, with the scale you declare."),
   ("b05b-02", "Fall time: 0.433 ± 0.027 s"), ("b05b-03", "Height: 0.923 ± 0.010 m"),
   ("b05b-04", "g: 9.84 ± 1.24 m/s²"), ("b05b-05", "Hero take: the track ends before impact, so lower bounds only."),
   ("b05b-06", "Approximate, not calibrated.")],
  [("capture/S24c/beat5b.webm", 1.5, 1)]),
 ("6", "Gate A: MET_AMENDED_Q16 · scale unverified · not setup-validated",
  [("b06-01", "Muse Spark interviews you about the setup, but every number it shows comes from a tool."),
   ("b06-02", "Our checker flagged zero invented numbers across thirty replayed turns, on recorded scenes, not validated setups.")],
  [("capture/S24e/beat6-own05.webm", 19.5, 0.45), ("capture/S24d/abc-flow.webm", 33.0, 0.55)]),
 ("7", "SIMULATED library traces · Mystery-g practice is not the blind /lab",
  [("b07-01", "The library holds simulated experiments, clearly labelled."), ("b07-02", "The Mystery-g card is practice at Earth g."),
   ("b07-03", "The lab draws a hidden g each session for a real blind test.")],
  [("capture/S24e/beat7-library-lab-home.webm", 4.2, 0.5), ("capture/S24e/beat7-lab-blind.webm", 5.0, 0.5)]),
 ("8", "Modal billed $0.599594 (BENCHMARK, read Oct 29) · $1.052013 (S13l daily billing, Oct 28 to 30)\nGate M ✗ · Gate RS ✗ · scale unverified",
  [("b08-01", "Modal bill so far: under a dollar."), ("b08-02", "Not proven: no calibrated metric source, so no physical-accuracy claim.")],
  [("capture/S24f/beat8-card.webm", 2.6, 1)]),
 ("9", "Built Oct 27 to Nov 4 · every number links to BENCHMARK.md",
  [("b09-01", "Every number you saw is a pointer into the repo's benchmark."), ("b09-02", "Try it.")],
  [("capture/S24f/beat9-close.webm", 15.9, 1)]),
]
GAP, LEAD, TAIL, END_HOLD = 0.4, 0.6, 0.7, 2.0
PAD_ORDER = None

def tc(t):
    ms = int(round(t * 1000)); return f"{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}"

def main():
    # 1 voice takes: level, clean, trim head/tail silence (0.15 s head, 0.25 s tail kept)
    takes = {}
    for _, _, lines, _ in BEATS:
        for tid, _ in lines:
            o = os.path.join(W, tid + ".wav")
            ff(["-i", os.path.join(SRC, "narration/takes", tid + ".m4a"), "-af",
                "loudnorm=I=-19:TP=-3:LRA=11,aresample=48000,highpass=f=80,deesser=i=0.3,acompressor=threshold=-20dB:ratio=3:attack=10:release=150:makeup=2,"
                "silenceremove=start_periods=1:start_threshold=-42dB:start_silence=0.15:detection=rms:stop_periods=-1:stop_duration=0.6:stop_threshold=-38dB:stop_silence=0.4,areverse,"
                "silenceremove=start_periods=1:start_threshold=-42dB:start_silence=0.25:detection=rms,areverse",
                "-ac", "1", "-ar", "48000", o])
            takes[tid] = dur(o)
    # 2 timeline
    t, rows, srt, vsegs, beat_spans = 1.0, [], [], [], []
    for bi, (beat, label, lines, shots) in enumerate(BEATS):
        b0 = t; t += LEAD
        for tid, cap in lines:
            rows.append((beat, tid, round(t, 3), round(t + takes[tid], 3))); srt.append((t, t + takes[tid], cap)); t += takes[tid] + GAP
        t += TAIL - GAP + (END_HOLD if bi == len(BEATS) - 1 else 0)
        beat_spans.append((beat, b0 if bi else 0.0, t))
    total = t
    # 3 voice track: adelay each take onto timeline
    ins, fl = [], []
    for i, (beat, tid, s, e) in enumerate(rows):
        ins += ["-i", os.path.join(W, tid + ".wav")]; fl.append(f"[{i}]adelay={int(s*1000)}:all=1[a{i}]")
    fl.append("".join(f"[a{i}]" for i in range(len(rows))) + f"amix=inputs={len(rows)}:normalize=0,apad=whole_dur={total:.3f}[v]")
    ff(ins + ["-filter_complex", ";".join(fl), "-map", "[v]", "-ac", "1", "-ar", "48000", os.path.join(W, "voice.wav")])
    # 4 music: synthesized soft pad (A major add9), slow tremolo, lowpass; fades 1 s in / 2 s out
    ff(["-f", "lavfi", "-i", f"aevalsrc=0.05*sin(2*PI*110*t)+0.04*sin(2*PI*164.81*t)+0.035*sin(2*PI*220*t)+0.03*sin(2*PI*277.18*t)+0.02*sin(2*PI*246.94*t)*(0.5+0.5*sin(2*PI*0.07*t)):s=48000:d={total:.3f}",
        "-af", f"tremolo=f=0.15:d=0.3,lowpass=f=1200,aecho=0.8:0.7:120|240:0.3|0.2,afade=t=in:d=1,afade=t=out:st={total-2:.3f}:d=2",
        "-ac", "2", os.path.join(W, "pad.wav")])
    # 5 mix: music ducked under voice by sidechain, then 2-pass loudnorm to -16 LUFS / -1.5 dBTP
    mixf = "[1]volume=-21dB[m];[0]asplit[v1][v2];[m][v1]sidechaincompress=threshold=0.02:ratio=20:attack=20:release=400:knee=4[d];[v2]pan=stereo|c0=c0|c1=c0[vs];[vs][d]amix=inputs=2:normalize=0[mx]"
    ff(["-i", os.path.join(W, "voice.wav"), "-i", os.path.join(W, "pad.wav"), "-filter_complex", mixf, "-map", "[mx]", os.path.join(W, "mix_raw.wav")])
    meas = subprocess.run([FF + "ffmpeg.exe", "-hide_banner", "-i", os.path.join(W, "mix_raw.wav"), "-af", "loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"], capture_output=True, text=True).stderr
    m = json.loads(meas[meas.rindex("{"):meas.rindex("}") + 1])
    ff(["-i", os.path.join(W, "mix_raw.wav"), "-af", f"loudnorm=I=-16:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true,aresample=48000,volume=-0.4dB", os.path.join(W, "mix.wav")])  # v1 first run measured TP -1.4 after AAC; -0.4 dB gave -1.8
    # 6 picture: per-beat segments cut to voice, shots share the beat, frozen last frame if short; label bar on top
    for bi, (beat, label, lines, shots) in enumerate(BEATS):
        b0, b1 = beat_spans[bi][1], beat_spans[bi][2]; bd = b1 - b0
        with open(os.path.join(W, f"label{beat}.txt"), "w", encoding="utf-8") as f: f.write(label)
        for si, (src, tin, share) in enumerate(shots):
            d = bd * share; o = os.path.join(W, f"seg_{bi:02}_{si}.mp4")
            # S24c 1280x720 overlays have a baked caption strip (y 612-672) that duplicates/contradicts the edit captions: cover it, keep the credit line below
            cover = "drawbox=x=0:y=912:w=iw:h=102:color=0x101418@0.92:t=fill," if "S24c" in src else ""
            ly = 700 if beat == "5b" else 22  # 5b table fills the top; its label goes in the empty middle
            vf = (f"scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=0x101418,setsar=1,fps=30,tpad=stop_mode=clone:stop_duration={d:.3f},trim=duration={d:.3f},"
                  f"{cover}drawbox=x=0:y={ly-22}:w=iw:h={130 if chr(10) in label else 84}:color=0x101418@0.82:t=fill,"
                  f"drawtext=fontfile='{FONT}':textfile=label{beat}.txt:fontcolor=white:fontsize=34:line_spacing=8:x=(w-tw)/2:y={ly}")
            ff(["-ss", f"{tin}", "-i", os.path.join(SRC, src), "-vf", vf, "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", o], cwd=W)
    segs = sorted(f for f in os.listdir(W) if f.startswith("seg_"))
    with open(os.path.join(W, "segs.txt"), "w") as f: f.writelines(f"file '{s}'\n" for s in segs)
    # 7 captions
    with open(os.path.join(OUT, "demo-v1.srt"), "w", encoding="utf-8") as f:
        for i, (s, e, c) in enumerate(srt, 1): f.write(f"{i}\n{tc(s)} --> {tc(e)}\n{c}\n\n")
    ff(["-f", "concat", "-safe", "0", "-i", "segs.txt", "-c", "copy", "picture.mp4"], cwd=W)
    style = "FontName=Segoe UI,FontSize=15,PrimaryColour=&H00FFFFFF,BackColour=&H99000000,BorderStyle=4,Outline=0,Shadow=0,MarginV=22"
    ff(["-i", "picture.mp4", "-i", "mix.wav", "-vf", f"subtitles=../demo-v1.srt:force_style='{style}',fade=t=in:d=0.6,fade=t=out:st={total-1.5:.3f}:d=1.5",
        "-c:v", "libx264", "-preset", "fast", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-t", f"{total:.3f}", "-movflags", "+faststart", "../demo-v1.mp4"], cwd=W)
    ff(["-i", "demo-v1.mp4", "-vf", "scale=1280:720", "-c:v", "libx264", "-crf", "24", "-preset", "veryfast", "-c:a", "copy", "preview-720p.mp4"], cwd=OUT)
    ff(["-i", "demo-v1.mp4", "-vf", "fps=1/10,scale=480:-1,tile=4x5", "-frames:v", "1", "work/contact.png"], cwd=OUT)
    json.dump({"takes_s": takes, "rows": rows, "beats": beat_spans, "total_s": total, "loudnorm_pass1": m}, open(os.path.join(OUT, "timeline.json"), "w"), indent=1)
    print(json.dumps({"total": total, "takes": takes}, indent=1))

if __name__ == "__main__":
    main()

