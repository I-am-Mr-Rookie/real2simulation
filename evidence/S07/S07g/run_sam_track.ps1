# S07g: the REAL SAM 3.1 track of OWN01, ready to run once the S20 GPU admission state exists.
# Blocked 2026-10-30T22:46Z: canonical evidence/S20/runtime/receipt.json + reservations.json absent
# (Build/guardrails/ADMISSION.md: a trusted operator must supply them; agents must not fabricate).
# Run from the repo root (worktree or canonical). Never prints secrets; the env file is read by uv only.
$ErrorActionPreference = 'Stop'
$env:PYTHONUTF8 = '1'; $env:PYTHONIOENCODING = 'utf-8'
$env:S20_MODAL_RESERVATION_USD = '0.60'  # all-in bound: <=1500 s A10G/L4 + CPU/mem, inside the shared $1 envelope
$root = git rev-parse --path-format=absolute --git-common-dir | Split-Path -Parent
uv run --python 3.12 --with modal==1.6.3 --env-file "$root/.env" modal run Build/measurement/runtime/modal_track.py `
  --clip OWN01 --first 40 --last 60 --prompt "yellow book" --object-id 0 `
  --out evidence/S07/S07g/track-own01.json --approval evidence/S07/S07g/OWNER-APPROVAL.md
# Then: scale = SAM box width (px) on held pre-release frames 40-44 / 0.2028 m; fit = Build/measurement/free_fall.py
# with the fall-window / 2:1 train:held-out rule fixed in diagnostic_colour.py (same rule, SAM centroids instead).

