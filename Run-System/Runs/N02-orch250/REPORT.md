# N02-orch250 REPORT: DONE

- Added Build/measurement/hosted_sam.py: hosted Meta SAM 3.1 client (upload, text/box/point track, all-object parse,
  moving-object pick, cost, S07a record for inputs.validate_input and real2sim.boundary.split unchanged). Box centres; masks not decoded.
- tests/measurement/test_hosted_sam.py + fixture (6-frame excerpt of recorded N01 response, no network).
- Full ST03 hosted track: 543/543 frames, 0 missing, moving apple picked (id 2); point prompt tracks the same object (<= 2 px).
- Gate RS rerun (evidence/N02/gate.py, gate-rs.json): prefix re-track 0.00135 H (tol 0.002); committed prediction scored on
  466/466 suffix frames, RMS 111.5 H (no-floor ballistic vs apple at rest); Gate RS NOT_MET; display VIRTUAL_LAB_ONLY.
- Hosted-only fit: degree 2, 2509 +/- 189 px/s^2 playback (not g). Measurement free-fall fitter abstains (scale/clock/approval).
- Checks: test_hosted_sam 4/4; measurement inputs/free_fall + prediction/test_score 41 OK; test_tracking 14 OK
  (needs tests/measurement on PYTHONPATH, pre-existing import style).
- Paid calls (evidence/N02/ledger.jsonl): 2026-11-01T11:00:32Z sam-3.1 543 frames $0.1086; 11:01:16Z sam-3.1 543 frames $0.1086.
  Total $0.2172. One /v1/files upload (no usage reported). No Modal/GPU used.
- Skipped: mask decoding (one_bit format undocumented here), streaming responses, Modal backup (not needed).
- Risks: hosted artifact needs a controller accepted-tracking entry before it is gate-eligible; uploaded file left on
  Meta storage (not deleted); box centre vs mask centroid differs slightly from the accepted method.
