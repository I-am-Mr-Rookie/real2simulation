# S07i batch track OWN02-OWN11 — controller operator run (2026-10-30)

Controller (chat 01a1882d…), standing Modal GPU authorization (evidence/owner/S05/GPU-AUTHORIZATION.md) + Koushik's Oct31 instruction (02-06 held-out/robustness).

- Pre-admission: Modal Usage & billing read in the ChatGPT in-app browser 23:36Z: cycle Oct 1-31 usage $0.80, spend $0.00 (OWN01 job ~ $0.02). receipt.json refreshed (Modal historical 0.80, headroom 29.20) seconds before the run.
- Command (S07i REPORT): S20_MODAL_RESERVATION_USD=0.40; uv run --python 3.12 --with modal==1.6.3 --env-file .env modal run Build/measurement/runtime/modal_track.py --batch evidence/S07/S07i/fall-windows.json --approval evidence/S07/S07g/OWNER-APPROVAL.md (PYTHONUTF8=1). This is job 2 of 2 of the standalone two-job/$1 envelope (now exhausted).
- First attempt 23:37Z died client-side (Windows charmap encode of a Modal CLI tick) before admission; no reservation row was written. Rerun started 23:37:53Z; app ap-7qnUtLNN8xQy534jpuXcQs completed and stopped ~23:43Z.
- Outcome: OWN02, OWN03, OWN04, OWN05, OWN06 tracked (track-own0N.json). OWN07-OWN11 FAILED after model_loaded with CUDA out of memory on the A10 (24 GB): the per-clip model reload accumulated memory (reserved ~22-23 GB before failure). OWN12 excluded earlier (no free fall).
- Post-run Modal read ~23:44Z: cycle usage $0.89, spend $0.00, credits header $129.11 (dashboard may still lag).
- Next: S07h fits OWN02-OWN06 with the frozen pipeline; S07j fixes the OOM (free/load-once) and proposes an explicit reviewed new standalone envelope per evidence/S20/FIX3-ADMISSION.md N4 before re-tracking OWN07-OWN11.

