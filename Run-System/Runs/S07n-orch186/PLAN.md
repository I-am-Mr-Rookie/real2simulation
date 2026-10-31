# S07n-orch186 PLAN
Objective: one deterministic script in evidence/S07/S07n/ deriving release/impact frames, t, h, g_ht = 2h/t² with u from existing owner-clip SAM 3.1 tracks, compared with stored fits; abstain where release/impact not in track.
Owns: evidence/S07/S07n/; Run-System/Runs/S07n-orch186/.
Model: anthropic/claude-opus-5-5 medium, CLAUDE lane, step S07. Coding quota OpenCodex-managed; not polled.
Rules: fixed in the script docstring before the first real run (reuse S07k v2 thresholds); one recorded post-first-run fix (scale-frame width outlier), see README.
Checks: --self-check (synthetic), in-run asserts (t = n/30, PTS span, h = ½gt², u > 0), worker_timebox check.
No tracking, GPU, Modal, Meta, video decoding, product/script edits.

