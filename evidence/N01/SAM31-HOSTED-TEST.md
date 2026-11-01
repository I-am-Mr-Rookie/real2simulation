# N01: hosted Meta SAM 3.1 video tracking test (controller, Nov 1 2026)

Clip: ST03 "Woman dropping apple on ground" (Roman Odintsov, Pexels License, clips.csv), 720x1366, 30 fps.
Trimmed locally with ffmpeg to 3 s (90 frames). Uploaded via POST /v1/files (purpose user_data, 8 s), then
POST /v1/responses, model sam-3.1, content [input_text noun phrase, input_video file_id], metadata mask_encoding one_bit.

| call | window | prompt | HTTP | latency | frames returned | objects |
|---|---|---|---|---|---|---|
| 1 | 1.5-4.5 s | apple | 200 | 9.0 s | 90/90 | parser read only the first object (basket apple) |
| 2 | 1.0-4.0 s | apple | 200 | 7.6 s | 90/90 | 3 stable IDs: two basket apples + the dropped apple (ID 2) |
| 3 | 1.0-4.0 s | falling apple | 200 | 7.4 s | 90/90 | same 3 IDs; text does not single out the moving one |

Dropped apple (ID 2), box centre y in px, every 4th frame: 437 (f0-8, in hand), 451 (f24), 474, 527, 613, 784, 950,
1116 (f48, ground), then bounce and rest ~1104. Every frame has a box and a one-bit mask; IDs stay stable through the bounce.
Quick check: quadratic fit on f28-f48 (6 points): R^2 0.996, rms 15 px, vertical accel 1778 px/s^2 (pixels only; no scale,
no perspective correction; NOT a g value).

Compare: the Modal SAM 3.1 run on full ST03 ran out of memory and scored 7 of 466 frames.

Findings
- Hosted SAM 3.1 handles video directly: about 2.5 s of processing per second of 30 fps video, no GPU cold start.
- Text prompts return every matching object with stable IDs. The product must pick the moving object (largest motion
  across frames) or take a click/box prompt from the user. Picking by motion is a few lines.
- usage.video_frames_processed is reported per call (90). Price $0.20 per 1k frames: 4 calls x 90 = 360 frames, about $0.07.
- Upload via /v1/files works for a 0.5 MB mp4.

Decision: hosted SAM 3.1 is the default tracker for Mode B (owner, Nov 1). Modal SAM 3.1 stays as the backup.
Files: resp-call1.json (raw response, masks included), run4.txt (calls 2-3 summary). Key never printed or stored.

