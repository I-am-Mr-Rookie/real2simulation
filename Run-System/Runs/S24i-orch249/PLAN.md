# S24i-orch249 plan

Objective: cut demo-v1 (<= 3:00, 1080p H.264/AAC, -16 LUFS, TP <= -1.5 dBTP) from the 25 owner VO takes and the S24c/d/e/f captures, with burned captions, .srt, 720p preview and EDIT_LOG.
Owns: media/edit/S24i/; .gitignore (4 lines); Run-System/Runs/S24i-orch249/.
Approach: one script (media/edit/S24i/build.py) drives ffmpeg: per-take level/clean/trim, timeline from measured take lengths, synthesized pad bed ducked by sidechain, picture cut to voice per beat, labels via drawtext, captions via subtitles, 2-pass loudnorm.
Checks: ffprobe format, ebur128 readout, duration <= 180 s, contact sheet viewed.
Timebox: issued 2026-11-01T09:09:32Z, cutoff 09:34:32Z, deadline 09:39:32Z.
