# S13j evidence (RM04 geometry re-capture): NOT captured

- dispatch-start-utc.txt + reconstruct-cli.txt: the only GPU attempt. Command:
  `python -B -m Build.pipeline.gpu_stages RM04 <.worktrees/S05c-orch19/evidence/S05/S05c/input.json> evidence/S13j/reconstruct evidence/S13j/gpu-ledger.jsonl`
  (manifest sha256 b3fe96a5... == S13h reconstruct idempotency key). Result at 14:01:01Z:
  `SPEND_PAUSED retryable=False: GPU job count or all-in reservation cap reached`. Refused inside reserve_gpu before any ledger write or Modal call: $0 spent, no container, no app.
- admission-preflight.json: read-only snapshot of the canonical journal (main evidence/S20/runtime/reservations.json): 3 Modal reservations, all unsettled, $1.40 liability, vs gpu_stages MAX_JOBS=2 / CAP_USD=$1.0.
- Controller decision (14:02Z message): no GPU dispatch this run even if settled, because DEV has no path to display the bytes. No manifest written under Build/pipeline/recorded/ (no bytes exist to describe).
- Labels if/when bytes exist: scale unverified, Display only, not a measurement.
- modal-billing-report-2026-10-30_31.json: read-only Modal billing report (14:06Z) used for the settlement plan in the run REPORT; per-app sums for the 3 open reservations total $0.159332.
