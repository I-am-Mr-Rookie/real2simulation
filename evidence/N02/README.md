# N02: hosted SAM 3.1 on full ST03, fit and Gate RS rerun (N02-orch250, Nov 1 2026)

Client: Build/measurement/hosted_sam.py (upload, track with noun phrase or box/point prompt, parse every object per
frame, pick the moving object by largest centroid travel, cost from usage.video_frames_processed, S07a record).
Clip: ST03 (Pexels License), local copy, sha256 7239da80... verified before upload; video not committed.

| call | prompt | frames | missing | objects | moving id (travel px) | latency | cost |
|---|---|---|---|---|---|---|---|
| apple | "apple" | 543/543 | 0 | 3 | 2 (688; basket apples 55) | 28.5 s | $0.1086 |
| point | point on f0 at the apple box centre | 543/543 | 0 | 1 | 1 (687) | 43.7 s | $0.1086 |

Point vs text track: same object, box centres differ by at most 2.0 px (mean 0.44 px) over 543 frames.
Old Modal path on full ST03: OOM, 7 of 466 suffix frames. Hosted: all 466 sealed suffix frames observed.

Gate RS rerun (gate.py, gate-rs.json; same committed prediction/v2 sha b9c092b5..., same scorer):
- Prefix re-track (f58-76) vs accepted orch14 mask centroids: max 0.00135 image heights, within PREFIX_TOL 0.002.
- Committed ballistic prediction vs hosted suffix: coverage 466/466, RMS 111.5 image heights (first 5 frames 0.133).
  The ballistic model has no floor; the apple lands at about f78 and rests, so the 15 s extrapolation diverges.
- Gate RS: NOT_MET. Projectile above 5%, bounce and pendulum have no scored clip, and the hosted artifact is not
  in evidence/S12/accepted-tracking.json (controller custody needed). Display decision: VIRTUAL_LAB_ONLY.
- Hosted-only prefix fit (19 frames, AIC picks degree 2): rmse 0.0082 image heights, playback acceleration
  2509 +/- 189 px/s^2 (1 sigma, iid residuals). Pixels per playback second squared, NOT g: scale unverified,
  capture clock unverified (25p in 30p repeats, probable slow motion). Prediction until impact (2 frames): RMS 0.041.
- Build/measurement free-fall fitter accepts the record and abstains: metric_use_not_approved, not_earth_free_fall,
  continuous_segment_unverified, scale_unverified, capture_timebase_unverified.

Files: run.py (paid run), gate.py (offline rerun), resp-apple.json / resp-point.json (responses, mask payloads
stripped), ledger.jsonl (paid calls), gate-rs.json (result). Labels: MEASURED (image-derived tracking), scale unverified.
