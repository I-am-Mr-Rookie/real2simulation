# S15ap-orch204 PLAN

Objective: replace the S15ag mark with a hand-authored pendulum logo (pivot, string, three phases), same brand filenames/sizes, plus mark.svg, mark-dark.svg, mark-16.svg and evidence in evidence/brand/logo-v2/.
Owns: Build/web/public/brand/; evidence/brand/logo-v2/; Run-System/Runs/S15ap-orch204/.
Lane/model: CLAUDE, anthropic/claude-opus-5-5 high (OpenCodex-managed; not polled).
Checks: (1) check_logo_v2.py sizes/alpha/ICO/SVG; (2) visual review at 16/32/192 and contact sheet on 6 modes; (3) worker_timebox.py check.
Approach (Ponytail): one Python primitive list drives both SVG text and Pillow supersampled raster; no new deps; no web code edits.

