# S07g controller operator admission + real SAM 3.1 track of OWN01 (2026-10-30)

Controller (trusted operator, chat 01a1882d…) initialized the canonical S20 GPU admission state that the S07g worker correctly refused to fabricate. Authority: standing Modal GPU authorization (evidence/owner/S05/GPU-AUTHORIZATION.md, <= $30 monthly, verify headroom/no overage) + Koushik's Oct31 instruction to run SAM 3.1 on 01_demo_hero.

- Verified at 2026-10-30T23:15:02Z in the ChatGPT in-app browser (Modal Usage & billing, workspace koushiksadhakjeet): cycle Oct 1-31 total usage $0.78, credits applied -$0.78, spend $0.00; Starter plan $30 included monthly credits; $100 grant active (not counted). Screenshot: modal-usage-preadmission.png.
- evidence/S20/runtime/reservations.json initialized (did not exist; schema gpu-reservations/1, empty) — first initialization, not a reset. receipt.json (schema reconstruction-admission/1, as_of 23:15:35Z): Modal historical 0.78, credit_headroom 29.22 (monthly only); Meta historical 0.08 (owner-reported balance 149.92/150), Meta credit_headroom 0 (conservative; no Meta call). Repo ledgers are projected by the guard on top (conservative double count). Runtime files stay local (gitignored).
- Reservation: S20_MODAL_RESERVATION_USD 0.60, request modal-track:OWN01:24e8a049… (1 of the 2-job/$1 standalone envelope; $0.40 and 1 job remain).
- Run: uv + modal 1.6.3, modal run Build/measurement/runtime/modal_track.py --clip OWN01 --first 40 --last 60 --prompt "yellow book" --object-id 0 --approval evidence/S07/S07g/OWNER-APPROVAL.md. GPU NVIDIA A10; checkpoint facebook/sam3.1 sam3.1_multiplex.pt sha256 0567debe…; load 19.2 s, track 7.6 s, remote elapsed 45.1 s; app ap-9SEBfxKkipzckSWGcQRGvt completed and stopped. Output: track-own01.json (21 frames). Expected cost well under the $0.60 bound; final billing to reconcile from the Modal dashboard.
- run_sam_track.ps1 bug: $root via Split-Path breaks on the space-containing path ("Hackathon/.env"); run from repo root with --env-file .env instead.
- No fit yet: scale + deterministic fit on these SAM masks is the next row (S07i).

