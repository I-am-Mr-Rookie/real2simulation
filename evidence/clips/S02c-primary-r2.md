# S02c primary round 2 — BN01 bounce evidence and Commons search (2026-10-27 UTC)

Image-space evidence only. No calibration, no g, no owner approval, no distribution clearance.

## BN01 (Commons "Bouncy ball 240fps.webm", GolhaMedia, CC BY-SA 4.0)

- Local file test-data/public/BN01.webm, sha256 b01267b7…969b (receipt; integrity checker re-verified).
  ffprobe: 1280x720, r_frame_rate 240/1, 41.443 s. Prior rounds reviewed only 0–10 s and 20–40 s.
- New coarse sheets: [10–20 s @2 fps](S02c-r2/BN01-10-20.jpg), [12.5–16.5 s @6 fps](S02c-r2/BN01-12_5-16_5.jpg):
  at ~13 s the person throws the red ball down near a wall; it then bounces on the tiled floor while the
  person stands aside. (BN01 40 s–end sheet was generated but NOT viewed.)
- Bounded segment: `ffmpeg -ss 13.0 -t 2.6 -i BN01.webm -vf scale=640:-2 -an -c:v libx264 -crf 12` → %TEMP%/s02c-r2/BN01seg.mp4
  (624 frames, 240/1, 3,791,636 B, sha256 b90999fc7431d0a18f2a6830d6c35515e48758d2ac737f671a8b4eb19d70b633; derived, not committed).
  Segment frame n ↔ file time 13.0 + n/240 s.
- Reused tools: `s02c_opus_review.py <seg> <out> 640` (624 decoded, pts gap 1/240 s, monotonic) and
  `s02c_opus_track.py <seg> <out> 48 14 18 115 248` (manual seed from viewed sheet): min match 0.52, median 0.85,
  0 frames <0.5. Track: [S02c-r2/BN01seg-tmpl.csv](S02c-r2/BN01seg-tmpl.csv); [48 crops](S02c-r2/BN01seg-crops.jpg) viewed:
  ball inside box at f39–159 and f212–530; lost f172–208 (box on tile) and at f543/f596.
- Contacts viewed frame by frame: [f60–106](S02c-r2/BN01seg-contact60-106.jpg) first impact is OCCLUDED behind a low
  floor object near the wall (not counted as a clean contact); [f262–285 and f422–445](S02c-r2/BN01seg-contacts.jpg):
  ball descends, meets its own shadow on the floor (track y maxima f271 y=337, f433 y=333), rebounds — two
  visible unoccluded FLOOR bounces. Ball also reflects off the left wall near f344 (x reversal) mid-arc.
- Arc fits (t = n/240, quadratic in image y; [fits JSON](S02c-r2/BN01seg-fits.json)); camera correction = background
  phase correlation of top-left 400x150 region (handheld drift ≤4.1 px per arc):

| arc (seg frames) | n | a_y raw px/s² | a_y cam-corrected | RMS px | apex f |
|---|---|---|---|---|---|
| 96–166 (after occluded impact) | 71 | 1996 | 1988 | 0.39 | 137 |
| 282–340 (after floor contact f271; wall hit ~f344) | 59 | 1731 | 1800 | 0.51 | 336 |
| 438–536 (after floor contact f433) | 99 | 1920 | 1870 | 0.41 | 489 |

- Repeat check (ST03 lesson: pixel/position level, not rounded centroids): within free-flight arcs, zero-motion
  steps are 0 in f30–70, only at the occluded contact f77–88 in f30–171, and 5/98 near apex f463–480 in f438–536
  (|v_x|≈1 px/frame, integer box positions). No periodic duplicate pattern at ball level ⇒ consistent with
  distinct 240 fps frames. Whole-frame mean diff (median 0.67) is noise-dominated and not used as proof.
  Capture rate is the uploader's title claim; NOT independently verified.
- Verdict: COUNTED narrow — real Earth small-ball floor bounces with continuous full-rate post-contact
  ballistic arcs. Limits: oblique perspective (image y mixes depth; per-arc px accelerations differ 1.73–2.0k px/s²),
  scale unknown (ball diameter ≈13 px at 640 px, physical size unknown), handheld drift, first impact occluded,
  wall contact during arc 2, no restitution claim. Depicted person (possibly minor) appears elsewhere in the file;
  any future use should crop to the floor segment and remains subject to S02e depicted-rights/owner approval.

## Commons search for NEW real bounce/drop sources (no download)

API search/category listing (normal requests, UA identified). Inspected imageinfo/licence pages:
- Bounce-ball.webm (Thecd3m, CC BY-SA 4.0): description says Blender animation → REJECT (CG).
- Bouncing Ball.webm (ScienceCOLA via YouTube, CC BY 3.0): categorized Wimshurst machines → electrostatic, same family
  as rejected BN04 → REJECT.
- Time ball drop only.webm (JRennocks, CC BY-SA 4.0): Greenwich time ball descends a guided mast → not free fall, REJECT.
- Zeitsymmetrie (senkrechter wurf).webm (Rhetos, CC BY-SA 4.0): split-screen reversed-time pair like rejected FF03 → not pursued.
- Category leads not acquired: Impaktecholot (Pilotversuch).webm, DownTheWell.ogv (Videos of free fall).
- Access: Commons API returned `urllib.error.HTTPError: HTTP Error 429: Too Many Requests` on the
  'tennis ball drop filemime:video' search (~23:25 UTC). No retry; Commons cooldown ≥10 min recommended.

## FF06
Not re-reviewed this round (time spent on BN01, which had unreviewed segments already on disk).
