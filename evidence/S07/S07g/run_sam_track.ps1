# S07g: the REAL SAM 3.1 track of OWN01 (run by the controller 2026-10-30, track-own01.json exists, so a
# rerun refuses to overwrite). -Batch runs the S07i OWN02-OWN12 batch (one admission, bound 0.40 USD).
# Runs from the canonical root (the .env lives there); never prints secrets; the env file is read by uv only.
param([switch]$Batch)
$ErrorActionPreference = 'Stop'
$env:PYTHONUTF8 = '1'; $env:PYTHONIOENCODING = 'utf-8'
# Split-Path on the piped git path broke on the spaced root; GetDirectoryName + Push-Location -LiteralPath does not.
$root = [IO.Path]::GetDirectoryName((git rev-parse --path-format=absolute --git-common-dir).TrimEnd('/'))
Push-Location -LiteralPath $root
try {
  if ($Batch) {
    $env:S20_MODAL_RESERVATION_USD = '0.40'  # all-in worst case 0.397 (modal_track.BATCH_TIMEOUT_S comment)
    uv run --python 3.12 --with modal==1.6.3 --env-file .env modal run Build/measurement/runtime/modal_track.py `
      --batch evidence/S07/S07i/fall-windows.json --approval evidence/S07/S07g/OWNER-APPROVAL.md
  } else {
    $env:S20_MODAL_RESERVATION_USD = '0.60'  # all-in bound: <=1500 s A10G/L4 + CPU/mem, inside the shared $1 envelope
    uv run --python 3.12 --with modal==1.6.3 --env-file .env modal run Build/measurement/runtime/modal_track.py `
      --clip OWN01 --first 40 --last 60 --prompt "yellow book" --object-id 0 `
      --out evidence/S07/S07g/track-own01.json --approval evidence/S07/S07g/OWNER-APPROVAL.md
  }
} finally { Pop-Location }
# Then: scale = SAM box width (px) on held pre-release frames 40-44 / 0.2028 m; fit = Build/measurement/free_fall.py
# with the fall-window / 2:1 train:held-out rule fixed in diagnostic_colour.py (same rule, SAM centroids instead).

